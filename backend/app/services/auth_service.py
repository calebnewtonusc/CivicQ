"""
Authentication Service

Handles user signup, login, verification, and token management.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
import secrets
import string
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User, VerificationRecord, VerificationStatus, VerificationMethod, UserRole
from app.schemas.user import (
    UserCreate, UserLogin, Token, VerificationStart, VerificationComplete, UserResponse,
    PasswordResetRequest, PasswordResetConfirm, PasswordChange
)
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.services.email_service import email_service
from app.services.session_service import session_service


class AuthService:
    """Service for authentication operations"""

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """
        Create a new user account

        Args:
            db: Database session
            user_data: User registration data

        Returns:
            Created user object

        Raises:
            HTTPException: If email already exists
        """
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create user
        user = User(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            city_name=user_data.city,
            role=UserRole.VOTER,
            verification_status=VerificationStatus.PENDING,
            email_verified=False
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # Auto-send email verification
        try:
            AuthService.request_email_verification(db, user)
        except Exception as e:
            # Don't fail user creation if email fails
            from app.core.logging_config import logger
            logger.error(f"Failed to send verification email to {user.email}: {str(e)}")

        return user

    @staticmethod
    def authenticate_user(db: Session, login_data: UserLogin) -> Tuple[User, str]:
        """
        Authenticate a user and generate access token

        Args:
            db: Database session
            login_data: User login credentials

        Returns:
            Tuple of (user, access_token)

        Raises:
            HTTPException: If credentials are invalid
        """
        user = db.query(User).filter(User.email == login_data.email).first()

        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )

        # Update last active
        user.last_active = datetime.utcnow()
        db.commit()

        # Generate access token
        access_token = create_access_token(data={"sub": user.id})

        return user, access_token

    @staticmethod
    def generate_verification_code() -> str:
        """
        Generate a random verification code

        Returns:
            6-digit verification code
        """
        return ''.join(secrets.choice(string.digits) for _ in range(6))

    @staticmethod
    def start_verification(
        db: Session,
        user: User,
        verification_data: VerificationStart
    ) -> VerificationRecord:
        """
        Start the verification process for a user

        Args:
            db: Database session
            user: User to verify
            verification_data: Verification method and contact info

        Returns:
            Created verification record

        Raises:
            HTTPException: If user is already verified or invalid method
        """
        if user.verification_status == VerificationStatus.VERIFIED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already verified"
            )

        # Map verification method string to enum
        method_map = {
            "sms": VerificationMethod.SMS,
            "email": VerificationMethod.EMAIL,
            "mail": VerificationMethod.MAIL_CODE,
            "id_vendor": VerificationMethod.ID_PROOFING
        }

        method = method_map.get(verification_data.method)
        if not method:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid verification method: {verification_data.method}"
            )

        # Generate verification code
        code = AuthService.generate_verification_code()

        # Create verification record
        verification = VerificationRecord(
            user_id=user.id,
            method=method,
            city_scope=user.city_name or "unknown",
            status=VerificationStatus.PENDING,
            metadata={
                "code": code,  # In production, this should be hashed
                "phone": verification_data.phone,
                "address": verification_data.address
            },
            expires_at=datetime.utcnow() + timedelta(minutes=settings.VERIFICATION_CODE_EXPIRE_MINUTES)
        )

        db.add(verification)

        # Update user verification token
        user.verification_token = code
        user.verification_status = VerificationStatus.PENDING

        db.commit()
        db.refresh(verification)

        # In production, send SMS/Email with code here
        # For now, we'll just return the record (code will be in metadata)

        return verification

    @staticmethod
    def complete_verification(
        db: Session,
        user: User,
        verification_data: VerificationComplete
    ) -> User:
        """
        Complete the verification process

        Args:
            db: Database session
            user: User being verified
            verification_data: Verification code and ID

        Returns:
            Updated user object

        Raises:
            HTTPException: If verification code is invalid or expired
        """
        # Find verification record
        verification = db.query(VerificationRecord).filter(
            VerificationRecord.id == int(verification_data.verification_id),
            VerificationRecord.user_id == user.id,
            VerificationRecord.status == VerificationStatus.PENDING
        ).first()

        if not verification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Verification record not found"
            )

        # Check if expired
        if verification.expires_at and verification.expires_at < datetime.utcnow():
            verification.status = VerificationStatus.REJECTED
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code has expired"
            )

        # Verify code
        stored_code = verification.metadata.get("code") if verification.metadata else None
        if stored_code != verification_data.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )

        # Update verification record
        verification.status = VerificationStatus.VERIFIED
        verification.verified_at = datetime.utcnow()

        # Update user
        user.verification_status = VerificationStatus.VERIFIED
        user.verification_token = None

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Get a user by ID

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User object or None if not found
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def request_password_reset(db: Session, email: str) -> bool:
        """
        Request password reset

        Args:
            db: Database session
            email: User's email address

        Returns:
            True if reset email sent (always returns True to prevent email enumeration)
        """
        user = db.query(User).filter(User.email == email).first()

        if not user:
            # Return True anyway to prevent email enumeration
            return True

        # Generate reset token
        reset_token = secrets.token_urlsafe(32)

        # Store token and expiration
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)

        db.commit()

        # Send password reset email
        email_service.send_password_reset_email(
            to_email=user.email,
            reset_token=reset_token,
            user_name=user.full_name
        )

        return True

    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> bool:
        """
        Reset password using token

        Args:
            db: Database session
            token: Password reset token
            new_password: New password

        Returns:
            True if password reset successfully

        Raises:
            HTTPException: If token is invalid or expired
        """
        user = db.query(User).filter(
            User.password_reset_token == token
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )

        # Check if token expired
        if user.password_reset_expires and user.password_reset_expires < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired"
            )

        # Update password
        user.hashed_password = get_password_hash(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None

        db.commit()

        # Invalidate all existing sessions
        session_service.delete_all_user_sessions(user.id)

        # Send confirmation email
        email_service.send_password_changed_email(
            to_email=user.email,
            user_name=user.full_name
        )

        return True

    @staticmethod
    def change_password(
        db: Session,
        user: User,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Change password for authenticated user

        Args:
            db: Database session
            user: User object
            current_password: Current password
            new_password: New password

        Returns:
            True if password changed successfully

        Raises:
            HTTPException: If current password is incorrect
        """
        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Update password
        user.hashed_password = get_password_hash(new_password)
        db.commit()

        # Invalidate all existing sessions
        session_service.delete_all_user_sessions(user.id)

        # Send confirmation email
        email_service.send_password_changed_email(
            to_email=user.email,
            user_name=user.full_name
        )

        return True

    @staticmethod
    def request_email_verification(db: Session, user: User) -> bool:
        """
        Request email verification

        Args:
            db: Database session
            user: User object

        Returns:
            True if verification email sent
        """
        if user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )

        # Generate verification token
        verification_token = secrets.token_urlsafe(32)

        # Store token and expiration
        user.email_verification_token = verification_token
        user.email_verification_expires = datetime.utcnow() + timedelta(hours=24)

        db.commit()

        # Send verification email
        email_service.send_verification_email(
            to_email=user.email,
            verification_token=verification_token,
            user_name=user.full_name
        )

        return True

    @staticmethod
    def verify_email(db: Session, token: str) -> User:
        """
        Verify email using token

        Args:
            db: Database session
            token: Email verification token

        Returns:
            User object

        Raises:
            HTTPException: If token is invalid or expired
        """
        user = db.query(User).filter(
            User.email_verification_token == token
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )

        # Check if token expired
        if user.email_verification_expires and user.email_verification_expires < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token has expired"
            )

        # Mark email as verified
        user.email_verified = True
        user.email_verification_token = None
        user.email_verification_expires = None

        db.commit()

        # Send welcome email
        email_service.send_welcome_email(
            to_email=user.email,
            user_name=user.full_name
        )

        return user
