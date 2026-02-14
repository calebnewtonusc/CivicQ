"""
User and Verification Models

Users: account id, role (voter/candidate/admin/mod), city scope, verification status
VerificationRecords: user id, method, provider, city scope, status, timestamps
"""

from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.base import Base


class UserRole(str, enum.Enum):
    """User role types"""
    VOTER = "voter"
    CANDIDATE = "candidate"
    ADMIN = "admin"
    MODERATOR = "moderator"
    CITY_STAFF = "city_staff"


class VerificationStatus(str, enum.Enum):
    """Verification status types"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"


class VerificationMethod(str, enum.Enum):
    """Verification method types"""
    SMS = "sms"
    EMAIL = "email"
    MAIL_CODE = "mail_code"
    VOTER_ROLL = "voter_roll"
    ID_PROOFING = "id_proofing"


class User(Base):
    """
    User model

    Represents all users in the system (voters, candidates, admins, moderators).
    """
    __tablename__ = "users"

    # Authentication
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Profile
    full_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)

    # Role and permissions
    role = Column(Enum(UserRole), default=UserRole.VOTER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # City scope
    city_id = Column(String, nullable=True, index=True)  # City identifier
    city_name = Column(String, nullable=True)

    # Verification
    verification_status = Column(
        Enum(VerificationStatus),
        default=VerificationStatus.PENDING,
        nullable=False
    )
    verification_token = Column(String, nullable=True)  # Minimal verification token
    email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(String, nullable=True)
    email_verification_expires = Column(DateTime, nullable=True)

    # Password Reset
    password_reset_token = Column(String, nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)

    # Two-Factor Authentication
    two_factor_enabled = Column(Boolean, default=False, nullable=False)
    two_factor_secret = Column(String, nullable=True)  # TOTP secret
    backup_codes = Column(JSON, nullable=True)  # Encrypted backup codes

    # OAuth
    oauth_provider = Column(String, nullable=True)  # 'google', 'facebook', etc.
    oauth_id = Column(String, nullable=True)  # Provider's user ID

    # Activity tracking
    last_active = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    verification_records = relationship("VerificationRecord", back_populates="user")
    questions = relationship("Question", back_populates="author")
    votes = relationship("Vote", back_populates="user")
    reports = relationship("Report", back_populates="reporter")
    follows = relationship("Follow", back_populates="user")

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class VerificationRecord(Base):
    """
    Verification Record model

    Stores minimal verification data for user identity proofing.
    Supports multiple city-configurable verification methods.
    """
    __tablename__ = "verification_records"

    # User reference
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Verification details
    method = Column(Enum(VerificationMethod), nullable=False)
    provider = Column(String, nullable=True)  # e.g., "twilio", "id.me"
    city_scope = Column(String, nullable=False, index=True)

    # Status
    status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING)

    # Minimal metadata (no sensitive PII stored)
    metadata = Column(JSON, nullable=True)  # Non-sensitive verification metadata only

    # Timestamps
    verified_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="verification_records")

    def __repr__(self):
        return f"<VerificationRecord user={self.user_id} method={self.method} status={self.status}>"
