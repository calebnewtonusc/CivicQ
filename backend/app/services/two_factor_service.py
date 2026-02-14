"""
Two-Factor Authentication Service

Handles TOTP-based 2FA setup, verification, and backup codes.
"""

import pyotp
import qrcode
import io
import base64
import secrets
import hashlib
from typing import List, Tuple
from sqlalchemy.orm import Session
import logging

from app.models.user import User
from app.core.security import get_password_hash

logger = logging.getLogger(__name__)


class TwoFactorService:
    """Service for two-factor authentication operations"""

    @staticmethod
    def generate_secret() -> str:
        """
        Generate a random base32 secret for TOTP

        Returns:
            Base32 encoded secret
        """
        return pyotp.random_base32()

    @staticmethod
    def generate_qr_code(user_email: str, secret: str, issuer: str = "CivicQ") -> str:
        """
        Generate QR code for TOTP setup

        Args:
            user_email: User's email address
            secret: TOTP secret
            issuer: Application name

        Returns:
            Base64 encoded QR code image
        """
        # Generate provisioning URI
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user_email,
            issuer_name=issuer
        )

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{qr_base64}"

    @staticmethod
    def generate_backup_codes(count: int = 10) -> List[str]:
        """
        Generate backup codes for 2FA recovery

        Args:
            count: Number of backup codes to generate

        Returns:
            List of backup codes
        """
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = secrets.token_hex(4).upper()
            # Format as XXXX-XXXX for readability
            formatted = f"{code[:4]}-{code[4:]}"
            codes.append(formatted)

        return codes

    @staticmethod
    def hash_backup_codes(codes: List[str]) -> List[str]:
        """
        Hash backup codes for secure storage

        Args:
            codes: List of backup codes

        Returns:
            List of hashed backup codes
        """
        return [get_password_hash(code) for code in codes]

    @staticmethod
    def verify_totp_code(secret: str, code: str, window: int = 1) -> bool:
        """
        Verify TOTP code

        Args:
            secret: TOTP secret
            code: 6-digit code from authenticator app
            window: Number of time windows to check (allows for clock drift)

        Returns:
            True if code is valid
        """
        try:
            totp = pyotp.TOTP(secret)
            # Verify with small window for clock drift
            return totp.verify(code, valid_window=window)
        except Exception as e:
            logger.error(f"Error verifying TOTP code: {str(e)}")
            return False

    @staticmethod
    def setup_2fa(user: User, db: Session) -> Tuple[str, str, List[str]]:
        """
        Setup 2FA for a user

        Args:
            user: User object
            db: Database session

        Returns:
            Tuple of (secret, qr_code, backup_codes)
        """
        # Generate secret
        secret = TwoFactorService.generate_secret()

        # Generate QR code
        qr_code = TwoFactorService.generate_qr_code(user.email, secret)

        # Generate backup codes
        backup_codes = TwoFactorService.generate_backup_codes()

        # Store hashed backup codes (don't enable 2FA yet)
        user.two_factor_secret = secret
        user.backup_codes = TwoFactorService.hash_backup_codes(backup_codes)

        db.commit()

        return secret, qr_code, backup_codes

    @staticmethod
    def enable_2fa(user: User, code: str, secret: str, db: Session) -> bool:
        """
        Enable 2FA after verifying initial code

        Args:
            user: User object
            code: TOTP code to verify
            secret: TOTP secret
            db: Database session

        Returns:
            True if 2FA enabled successfully
        """
        # Verify code
        if not TwoFactorService.verify_totp_code(secret, code):
            return False

        # Enable 2FA
        user.two_factor_enabled = True
        db.commit()

        logger.info(f"2FA enabled for user {user.id}")
        return True

    @staticmethod
    def disable_2fa(user: User, db: Session) -> bool:
        """
        Disable 2FA for a user

        Args:
            user: User object
            db: Database session

        Returns:
            True if 2FA disabled successfully
        """
        user.two_factor_enabled = False
        user.two_factor_secret = None
        user.backup_codes = None

        db.commit()

        logger.info(f"2FA disabled for user {user.id}")
        return True

    @staticmethod
    def verify_2fa(user: User, code: str, db: Session) -> bool:
        """
        Verify 2FA code (either TOTP or backup code)

        Args:
            user: User object
            code: TOTP or backup code
            db: Database session

        Returns:
            True if code is valid
        """
        if not user.two_factor_enabled or not user.two_factor_secret:
            return False

        # Try TOTP code first
        if TwoFactorService.verify_totp_code(user.two_factor_secret, code):
            return True

        # Try backup codes
        if user.backup_codes:
            from app.core.security import verify_password

            for i, hashed_code in enumerate(user.backup_codes):
                if verify_password(code, hashed_code):
                    # Remove used backup code
                    user.backup_codes.pop(i)
                    db.commit()
                    logger.info(f"Backup code used for user {user.id}")
                    return True

        return False

    @staticmethod
    def regenerate_backup_codes(user: User, db: Session) -> List[str]:
        """
        Regenerate backup codes for a user

        Args:
            user: User object
            db: Database session

        Returns:
            New list of backup codes
        """
        backup_codes = TwoFactorService.generate_backup_codes()
        user.backup_codes = TwoFactorService.hash_backup_codes(backup_codes)

        db.commit()

        logger.info(f"Backup codes regenerated for user {user.id}")
        return backup_codes
