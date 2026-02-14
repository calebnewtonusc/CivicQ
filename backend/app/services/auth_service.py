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
from app.schemas.user import UserCreate, UserLogin, Token, VerificationStart, VerificationComplete, UserResponse
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings


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
            verification_status=VerificationStatus.PENDING
        )

        db.add(user)
        db.commit()
        db.refresh(user)

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
