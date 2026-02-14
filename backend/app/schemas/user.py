"""
User-related Pydantic Schemas
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enum"""
    VOTER = "voter"
    CANDIDATE = "candidate"
    ADMIN = "admin"
    MODERATOR = "moderator"


class VerificationStatus(str, Enum):
    """Verification status enum"""
    UNVERIFIED = "unverified"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=100)
    city: str = Field(..., min_length=2, max_length=100)
    address: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    email: str
    full_name: str
    role: UserRole
    city: str
    verification_status: VerificationStatus
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class VerificationStart(BaseModel):
    """Schema for starting verification process"""
    method: str = Field(..., description="Verification method: sms, mail, or id_vendor")
    phone: Optional[str] = None
    address: Optional[str] = None


class VerificationComplete(BaseModel):
    """Schema for completing verification"""
    code: str = Field(..., min_length=4, max_length=10)
    verification_id: str


class PasswordResetRequest(BaseModel):
    """Schema for requesting password reset"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for confirming password reset"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class PasswordChange(BaseModel):
    """Schema for changing password (authenticated users)"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class EmailVerificationRequest(BaseModel):
    """Schema for requesting email verification"""
    email: EmailStr


class EmailVerificationConfirm(BaseModel):
    """Schema for confirming email verification"""
    token: str


class TwoFactorSetup(BaseModel):
    """Schema for 2FA setup response"""
    secret: str
    qr_code: str
    backup_codes: list[str]


class TwoFactorVerify(BaseModel):
    """Schema for 2FA verification"""
    code: str = Field(..., min_length=6, max_length=6)


class TwoFactorEnable(BaseModel):
    """Schema for enabling 2FA"""
    code: str = Field(..., min_length=6, max_length=6)
    secret: str
