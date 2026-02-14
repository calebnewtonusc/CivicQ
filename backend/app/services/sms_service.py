"""
SMS Service

Handles SMS sending with Twilio integration.
Supports verification codes, 2FA codes, and security notifications.
"""

import logging
from typing import Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from app.core.config import settings

logger = logging.getLogger(__name__)


class SMSService:
    """Service for sending SMS messages using Twilio"""

    def __init__(self):
        """Initialize SMS service with Twilio client"""
        self.twilio_client = None
        self.is_configured = False
        self.from_number = None

        # Check if Twilio is configured
        if all([
            hasattr(settings, 'TWILIO_ACCOUNT_SID') and settings.TWILIO_ACCOUNT_SID,
            hasattr(settings, 'TWILIO_AUTH_TOKEN') and settings.TWILIO_AUTH_TOKEN,
            hasattr(settings, 'TWILIO_PHONE_NUMBER') and settings.TWILIO_PHONE_NUMBER
        ]):
            try:
                self.twilio_client = Client(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
                self.from_number = settings.TWILIO_PHONE_NUMBER
                self.is_configured = True
                logger.info("SMS service initialized with Twilio")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
                logger.warning("SMS service will run in dev mode (logging only)")
        else:
            logger.warning("Twilio credentials not configured. SMS service will run in dev mode (logging only)")

    def _send_sms(self, to_phone: str, message: str) -> bool:
        """
        Send an SMS message using Twilio

        Args:
            to_phone: Recipient phone number (E.164 format: +1234567890)
            message: SMS message content

        Returns:
            True if SMS sent successfully, False otherwise
        """
        # Validate inputs
        if not to_phone:
            logger.error("Cannot send SMS: recipient phone number is empty")
            return False

        if not message:
            logger.warning("SMS message is empty")
            return False

        # Normalize phone number (basic validation)
        if not to_phone.startswith('+'):
            # Assume US number if no country code
            to_phone = f'+1{to_phone.replace("-", "").replace("(", "").replace(")", "").replace(" ", "")}'

        try:
            if not self.is_configured or not self.twilio_client:
                # Fallback for development - log SMS instead of sending
                logger.info(f"[DEV MODE] SMS to {to_phone}: {message}")
                return True

            message_obj = self.twilio_client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_phone
            )

            if message_obj.sid:
                logger.info(f"SMS sent successfully to {to_phone} (SID: {message_obj.sid})")
                return True
            else:
                logger.error(f"Failed to send SMS to {to_phone}")
                return False

        except TwilioRestException as e:
            logger.error(f"Twilio error sending SMS to {to_phone}: {e.msg}")
            return False
        except Exception as e:
            logger.error(f"Error sending SMS to {to_phone}: {str(e)}")
            return False

    def send_verification_code(
        self,
        to_phone: str,
        code: str,
        user_name: Optional[str] = None
    ) -> bool:
        """
        Send verification code via SMS

        Args:
            to_phone: Recipient phone number
            code: 6-digit verification code
            user_name: User's name (optional)

        Returns:
            True if SMS sent successfully
        """
        greeting = f"Hi {user_name}, " if user_name else ""
        message = (
            f"{greeting}Your CivicQ verification code is: {code}\n\n"
            f"This code will expire in 15 minutes.\n\n"
            f"If you didn't request this code, please ignore this message."
        )

        return self._send_sms(to_phone, message)

    def send_2fa_code(
        self,
        to_phone: str,
        code: str,
        user_name: Optional[str] = None
    ) -> bool:
        """
        Send 2FA authentication code via SMS

        Args:
            to_phone: Recipient phone number
            code: 6-digit 2FA code
            user_name: User's name (optional)

        Returns:
            True if SMS sent successfully
        """
        greeting = f"Hi {user_name}, " if user_name else ""
        message = (
            f"{greeting}Your CivicQ 2FA code is: {code}\n\n"
            f"This code will expire in 10 minutes.\n\n"
            f"If you didn't request this code, please secure your account immediately."
        )

        return self._send_sms(to_phone, message)

    def send_login_alert(
        self,
        to_phone: str,
        location: str = "Unknown location",
        device: str = "Unknown device",
        user_name: Optional[str] = None
    ) -> bool:
        """
        Send login alert notification via SMS

        Args:
            to_phone: Recipient phone number
            location: Login location (city/country)
            device: Device information
            user_name: User's name (optional)

        Returns:
            True if SMS sent successfully
        """
        greeting = f"Hi {user_name}, " if user_name else "Hi, "
        message = (
            f"{greeting}New login to your CivicQ account:\n\n"
            f"Location: {location}\n"
            f"Device: {device}\n\n"
            f"If this wasn't you, please secure your account immediately."
        )

        return self._send_sms(to_phone, message)

    def send_password_changed_alert(
        self,
        to_phone: str,
        user_name: Optional[str] = None
    ) -> bool:
        """
        Send password changed alert via SMS

        Args:
            to_phone: Recipient phone number
            user_name: User's name (optional)

        Returns:
            True if SMS sent successfully
        """
        greeting = f"Hi {user_name}, " if user_name else "Hi, "
        message = (
            f"{greeting}Your CivicQ password was recently changed.\n\n"
            f"If you didn't make this change, please contact support immediately."
        )

        return self._send_sms(to_phone, message)

    def send_account_locked_alert(
        self,
        to_phone: str,
        reason: str = "multiple failed login attempts",
        user_name: Optional[str] = None
    ) -> bool:
        """
        Send account locked notification via SMS

        Args:
            to_phone: Recipient phone number
            reason: Reason for account lock
            user_name: User's name (optional)

        Returns:
            True if SMS sent successfully
        """
        greeting = f"Hi {user_name}, " if user_name else "Hi, "
        message = (
            f"{greeting}Your CivicQ account has been locked due to {reason}.\n\n"
            f"Please reset your password or contact support to unlock your account."
        )

        return self._send_sms(to_phone, message)


# Global SMS service instance
sms_service = SMSService()
