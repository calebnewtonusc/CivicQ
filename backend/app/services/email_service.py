"""
Email Service

Production-grade email service with SendGrid integration, retry logic,
rate limiting, delivery tracking, and comprehensive error handling.

Features:
- SendGrid integration with retry logic
- Email template rendering with Jinja2
- Rate limiting and bounce management
- Email delivery tracking and analytics
- Async email sending via Celery tasks
- Development mode with email logging
"""

import os
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
import logging
import redis
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailRateLimiter:
    """Rate limiter for email sending to prevent abuse"""

    def __init__(self):
        """Initialize rate limiter with Redis"""
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        except Exception as e:
            logger.warning(f"Redis not available for rate limiting: {e}")
            self.redis_client = None

    def check_rate_limit(self, email: str, limit: int = 10, window: int = 3600) -> bool:
        """
        Check if email sending is within rate limits

        Args:
            email: Email address to check
            limit: Maximum emails per window (default: 10)
            window: Time window in seconds (default: 1 hour)

        Returns:
            True if within limits, False if rate limit exceeded
        """
        if not self.redis_client:
            return True  # Allow if Redis not available

        try:
            key = f"email_rate:{email}"
            count = self.redis_client.get(key)

            if count is None:
                # First email in window
                self.redis_client.setex(key, window, 1)
                return True

            if int(count) >= limit:
                logger.warning(f"Rate limit exceeded for email: {email}")
                return False

            # Increment counter
            self.redis_client.incr(key)
            return True

        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True  # Allow on error

    def reset_rate_limit(self, email: str):
        """Reset rate limit for an email address"""
        if self.redis_client:
            try:
                self.redis_client.delete(f"email_rate:{email}")
            except Exception as e:
                logger.error(f"Failed to reset rate limit: {e}")


class EmailService:
    """Production-grade email service with SendGrid integration"""

    def __init__(self):
        """Initialize email service with SendGrid client and Jinja2 templates"""
        self.sendgrid_client = None
        self.is_configured = False
        self.rate_limiter = EmailRateLimiter()

        # Check if SendGrid is configured
        if hasattr(settings, 'SENDGRID_API_KEY') and settings.SENDGRID_API_KEY:
            try:
                self.sendgrid_client = SendGridAPIClient(settings.SENDGRID_API_KEY)
                self.is_configured = True
                logger.info("Email service initialized with SendGrid")
            except Exception as e:
                logger.error(f"Failed to initialize SendGrid client: {e}")
                logger.warning("Email service will run in dev mode (logging only)")
        else:
            logger.warning("SENDGRID_API_KEY not configured. Email service will run in dev mode (logging only)")

        # Setup Jinja2 for email templates
        template_dir = Path(__file__).parent.parent / 'templates' / 'emails'

        # Validate template directory exists
        if not template_dir.exists():
            logger.warning(f"Email template directory not found: {template_dir}")
            logger.info("Creating email template directory")
            template_dir.mkdir(parents=True, exist_ok=True)

        try:
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(template_dir)),
                autoescape=select_autoescape(['html', 'xml'])
            )
        except Exception as e:
            logger.error(f"Failed to initialize template engine: {e}")
            self.jinja_env = None

    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render an email template with context

        Args:
            template_name: Name of the template file
            context: Template context variables

        Returns:
            Rendered HTML string
        """
        if not self.jinja_env:
            logger.warning(f"Template engine not available, using fallback for {template_name}")
            return self._generate_fallback_html(context)

        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {e}")
            return self._generate_fallback_html(context)

    def _render_plain_text_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render plain text email template

        Args:
            template_name: Name of the template file (will look for .txt version)
            context: Template context variables

        Returns:
            Rendered plain text string
        """
        # Try to load .txt version of template
        txt_template_name = template_name.replace('.html', '.txt')

        if not self.jinja_env:
            return self._generate_fallback_plain_text(context)

        try:
            template = self.jinja_env.get_template(txt_template_name)
            return template.render(**context)
        except Exception as e:
            # If .txt template doesn't exist, generate from context
            logger.debug(f"Plain text template {txt_template_name} not found, using fallback")
            return self._generate_fallback_plain_text(context)

    def _generate_fallback_plain_text(self, context: Dict[str, Any]) -> str:
        """
        Generate simple plain text from context when template is not available

        Args:
            context: Template context variables

        Returns:
            Simple plain text string
        """
        lines = ["CivicQ\n" + "=" * 40 + "\n"]
        for key, value in context.items():
            if isinstance(value, str) and key not in ['support_email', 'app_name']:
                lines.append(f"{key.replace('_', ' ').title()}: {value}\n")
        lines.append("\n" + "=" * 40)
        lines.append(f"\nQuestions? Contact us at {context.get('support_email', 'support@civicq.org')}")
        return "\n".join(lines)

    def _generate_fallback_html(self, context: Dict[str, Any]) -> str:
        """
        Generate simple fallback HTML when templates are not available

        Args:
            context: Template context variables

        Returns:
            Simple HTML string
        """
        content = "<html><body>"
        for key, value in context.items():
            if isinstance(value, str):
                content += f"<p><strong>{key}:</strong> {value}</p>"
        content += "</body></html>"
        return content

    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        category: Optional[str] = None,
        custom_args: Optional[Dict[str, str]] = None,
        retry_count: int = 3,
        retry_delay: int = 2
    ) -> Dict[str, Any]:
        """
        Send an email using SendGrid with retry logic

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            plain_content: Plain text email content (optional)
            attachments: List of attachment dictionaries (optional)
            category: Email category for tracking (optional)
            custom_args: Custom arguments for analytics (optional)
            retry_count: Number of retries on failure (default: 3)
            retry_delay: Delay between retries in seconds (default: 2)

        Returns:
            Dictionary with status, message_id, and error information
        """
        # Validate inputs
        if not to_email:
            logger.error("Cannot send email: recipient email is empty")
            return {"success": False, "error": "Empty recipient email"}

        if not subject:
            logger.warning("Email subject is empty")

        # Check rate limits
        if not self.rate_limiter.check_rate_limit(to_email):
            logger.error(f"Rate limit exceeded for {to_email}")
            return {"success": False, "error": "Rate limit exceeded"}

        # Try sending with retries
        last_exception = None
        for attempt in range(retry_count):
            try:
                if not self.is_configured or not self.sendgrid_client:
                    # Fallback for development - log email instead of sending
                    logger.info(f"[DEV MODE] Email to {to_email}: {subject}")
                    logger.info(f"Content preview: {plain_content[:200] if plain_content else html_content[:200]}...")
                    return {
                        "success": True,
                        "dev_mode": True,
                        "message_id": f"dev_{int(time.time())}"
                    }

                # Create SendGrid message
                message = Mail(
                    from_email=Email(settings.EMAIL_FROM, "CivicQ"),
                    to_emails=To(to_email),
                    subject=subject,
                    html_content=Content("text/html", html_content)
                )

                # Add plain text content
                if plain_content:
                    message.plain_text_content = Content("text/plain", plain_content)

                # Add attachments
                if attachments:
                    for attachment_data in attachments:
                        attachment = Attachment()
                        attachment.file_content = FileContent(attachment_data['content'])
                        attachment.file_name = FileName(attachment_data['filename'])
                        attachment.file_type = FileType(attachment_data.get('type', 'application/octet-stream'))
                        attachment.disposition = Disposition('attachment')
                        message.add_attachment(attachment)

                # Add tracking categories
                if category:
                    message.category = category

                # Add custom arguments for analytics
                if custom_args:
                    for key, value in custom_args.items():
                        message.custom_arg = {key: value}

                # Send email
                response = self.sendgrid_client.send(message)

                if response.status_code in [200, 201, 202]:
                    message_id = response.headers.get('X-Message-Id', '')
                    logger.info(f"Email sent successfully to {to_email} (message_id: {message_id})")

                    return {
                        "success": True,
                        "message_id": message_id,
                        "status_code": response.status_code
                    }
                else:
                    logger.error(f"Failed to send email to {to_email}: {response.status_code}")
                    last_exception = f"HTTP {response.status_code}: {response.body}"

            except Exception as e:
                logger.error(f"Error sending email to {to_email} (attempt {attempt + 1}/{retry_count}): {str(e)}")
                last_exception = str(e)

                # Wait before retry (exponential backoff)
                if attempt < retry_count - 1:
                    time.sleep(retry_delay * (2 ** attempt))

        # All retries failed
        logger.error(f"Failed to send email to {to_email} after {retry_count} attempts")
        return {
            "success": False,
            "error": last_exception or "Unknown error",
            "attempts": retry_count
        }

    def send_verification_email(
        self,
        to_email: str,
        verification_token: str,
        user_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send email verification link

        Args:
            to_email: Recipient email address
            verification_token: Verification token
            user_name: User's name (optional)

        Returns:
            Dictionary with send result and message_id
        """
        verification_url = f"{settings.FRONTEND_URL}/auth/verify-email?token={verification_token}"

        context = {
            'user_name': user_name or 'there',
            'verification_url': verification_url,
            'app_name': 'CivicQ',
            'support_email': settings.EMAIL_FROM
        }

        html_content = self._render_template('verification_email.html', context)
        plain_content = self._render_plain_text_template('verification_email.html', context)

        if not plain_content or len(plain_content) < 50:
            # Fallback plain text
            plain_content = f"""Hi {context['user_name']},

Thank you for signing up for CivicQ! Please verify your email address by clicking the link below:

{verification_url}

This link will expire in 24 hours.

If you didn't create an account, you can safely ignore this email.

Best regards,
The CivicQ Team
"""

        return self._send_email(
            to_email=to_email,
            subject="Verify Your CivicQ Email Address",
            html_content=html_content,
            plain_content=plain_content,
            category="email_verification",
            custom_args={
                "email_type": "verification",
                "user_name": user_name or "unknown"
            }
        )

    def send_password_reset_email(
        self,
        to_email: str,
        reset_token: str,
        user_name: Optional[str] = None
    ) -> bool:
        """
        Send password reset link

        Args:
            to_email: Recipient email address
            reset_token: Password reset token
            user_name: User's name (optional)

        Returns:
            True if email sent successfully
        """
        reset_url = f"{settings.FRONTEND_URL}/auth/reset-password?token={reset_token}"

        context = {
            'user_name': user_name or 'there',
            'reset_url': reset_url,
            'app_name': 'CivicQ',
            'support_email': settings.EMAIL_FROM
        }

        html_content = self._render_template('password_reset.html', context)
        plain_content = f"""
        Hi {context['user_name']},

        We received a request to reset your password for your CivicQ account. Click the link below to reset it:

        {reset_url}

        This link will expire in 1 hour for security reasons.

        If you didn't request a password reset, please ignore this email or contact support if you have concerns.

        Best regards,
        The CivicQ Team
        """

        return self._send_email(
            to_email=to_email,
            subject="Reset Your CivicQ Password",
            html_content=html_content,
            plain_content=plain_content
        )

    def send_2fa_code_email(
        self,
        to_email: str,
        code: str,
        user_name: Optional[str] = None
    ) -> bool:
        """
        Send 2FA verification code

        Args:
            to_email: Recipient email address
            code: 6-digit verification code
            user_name: User's name (optional)

        Returns:
            True if email sent successfully
        """
        context = {
            'user_name': user_name or 'there',
            'code': code,
            'app_name': 'CivicQ',
            'support_email': settings.EMAIL_FROM
        }

        html_content = self._render_template('2fa_code.html', context)
        plain_content = f"""
        Hi {context['user_name']},

        Your CivicQ verification code is:

        {code}

        This code will expire in 10 minutes.

        If you didn't request this code, please secure your account immediately.

        Best regards,
        The CivicQ Team
        """

        return self._send_email(
            to_email=to_email,
            subject="Your CivicQ Verification Code",
            html_content=html_content,
            plain_content=plain_content
        )

    def send_welcome_email(
        self,
        to_email: str,
        user_name: Optional[str] = None
    ) -> bool:
        """
        Send welcome email after successful registration

        Args:
            to_email: Recipient email address
            user_name: User's name (optional)

        Returns:
            True if email sent successfully
        """
        context = {
            'user_name': user_name or 'there',
            'app_name': 'CivicQ',
            'app_url': settings.FRONTEND_URL,
            'support_email': settings.EMAIL_FROM
        }

        html_content = self._render_template('welcome_email.html', context)
        plain_content = f"""
        Hi {context['user_name']},

        Welcome to CivicQ! Your account has been successfully created.

        CivicQ empowers citizens to engage with local government through transparent, organized Q&A with candidates and elected officials.

        Get started: {settings.FRONTEND_URL}

        If you have any questions, feel free to reach out to our support team.

        Best regards,
        The CivicQ Team
        """

        return self._send_email(
            to_email=to_email,
            subject="Welcome to CivicQ!",
            html_content=html_content,
            plain_content=plain_content
        )

    def send_password_changed_email(
        self,
        to_email: str,
        user_name: Optional[str] = None
    ) -> bool:
        """
        Send notification that password was changed

        Args:
            to_email: Recipient email address
            user_name: User's name (optional)

        Returns:
            True if email sent successfully
        """
        context = {
            'user_name': user_name or 'there',
            'app_name': 'CivicQ',
            'support_email': settings.EMAIL_FROM
        }

        html_content = self._render_template('password_changed.html', context)
        plain_content = f"""
        Hi {context['user_name']},

        Your CivicQ password was recently changed.

        If you made this change, you can safely ignore this email.

        If you didn't change your password, please contact our support team immediately at {settings.EMAIL_FROM}

        Best regards,
        The CivicQ Team
        """

        return self._send_email(
            to_email=to_email,
            subject="Your CivicQ Password Was Changed",
            html_content=html_content,
            plain_content=plain_content
        )


# Global email service instance
email_service = EmailService()
