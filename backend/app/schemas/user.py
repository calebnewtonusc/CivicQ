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
