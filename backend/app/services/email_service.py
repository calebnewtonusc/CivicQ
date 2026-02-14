"""
Email Service

Handles email sending with SendGrid integration and email templates.
Supports verification emails, password reset, 2FA codes, and notifications.
"""

import os
from typing import Optional, Dict, Any
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails using SendGrid"""

    def __init__(self):
        """Initialize email service with SendGrid client and Jinja2 templates"""
        self.sendgrid_client = None
        self.is_configured = False

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
        plain_content: Optional[str] = None
    ) -> bool:
        """
        Send an email using SendGrid

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            plain_content: Plain text email content (optional)

        Returns:
            True if email sent successfully, False otherwise
        """
        # Validate inputs
        if not to_email:
            logger.error("Cannot send email: recipient email is empty")
            return False

        if not subject:
            logger.warning("Email subject is empty")

        try:
            if not self.is_configured or not self.sendgrid_client:
                # Fallback for development - log email instead of sending
                logger.info(f"[DEV MODE] Email to {to_email}: {subject}")
                logger.info(f"Content: {plain_content or html_content[:200]}...")
                return True

            message = Mail(
                from_email=Email(settings.EMAIL_FROM, "CivicQ"),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )

            if plain_content:
                message.plain_text_content = Content("text/plain", plain_content)

            response = self.sendgrid_client.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email to {to_email}: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False

    def send_verification_email(
        self,
        to_email: str,
        verification_token: str,
        user_name: Optional[str] = None
    ) -> bool:
        """
        Send email verification link

        Args:
            to_email: Recipient email address
            verification_token: Verification token
            user_name: User's name (optional)

        Returns:
            True if email sent successfully
        """
        verification_url = f"{settings.FRONTEND_URL}/auth/verify-email?token={verification_token}"

        context = {
            'user_name': user_name or 'there',
            'verification_url': verification_url,
            'app_name': 'CivicQ',
            'support_email': settings.EMAIL_FROM
        }

        html_content = self._render_template('verification_email.html', context)
        plain_content = f"""
        Hi {context['user_name']},

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
            plain_content=plain_content
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
