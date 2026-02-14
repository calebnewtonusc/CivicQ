"""
City Model for Multi-City Support

Cities: registration, configuration, verification, branding
CityStaff: city user relationships, roles, permissions
"""

from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, DateTime, JSON, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.base import Base


class CityStatus(str, enum.Enum):
    """City status types"""
    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


class CityStaffRole(str, enum.Enum):
    """City staff role types"""
    OWNER = "owner"  # City clerk or primary admin
    ADMIN = "admin"  # Full administrative access
    EDITOR = "editor"  # Can edit ballots and content
    MODERATOR = "moderator"  # Can moderate questions
    VIEWER = "viewer"  # Read-only access


class City(Base):
    """
    City model

    Represents a city/jurisdiction using CivicQ.
    Supports multi-tenancy with full data isolation.
    """
    __tablename__ = "cities"

    # Basic Information
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)  # URL-friendly identifier

    # Location
    state = Column(String(2), nullable=False)  # Two-letter state code
    county = Column(String, nullable=True)
    population = Column(Integer, nullable=True)

    # Contact Information
    primary_contact_name = Column(String, nullable=False)
    primary_contact_email = Column(String, nullable=False)
    primary_contact_phone = Column(String, nullable=True)
    primary_contact_title = Column(String, nullable=True)  # e.g., "City Clerk"

    # Verification
    status = Column(Enum(CityStatus), default=CityStatus.PENDING_VERIFICATION, nullable=False)
    verification_method = Column(String, nullable=True)  # How they were verified
    verification_notes = Column(Text, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    verified_by = Column(String, nullable=True)  # Admin who verified

    # Official Documentation (for verification)
    documentation_urls = Column(JSON, nullable=True)  # Links to official documents
    official_email_domain = Column(String, nullable=True)  # e.g., "cityofboston.gov"

    # Branding
    logo_url = Column(String, nullable=True)
    primary_color = Column(String(7), nullable=True)  # Hex color code
    secondary_color = Column(String(7), nullable=True)

    # Configuration
    timezone = Column(String, default="America/Los_Angeles", nullable=False)
    settings = Column(JSON, nullable=True)  # City-specific settings

    # Features enabled
    features = Column(JSON, nullable=True, default=dict)  # Feature flags per city

    # Election Information
    next_election_date = Column(Date, nullable=True)
    election_info_url = Column(String, nullable=True)  # Link to city's election info page

    # Subscription/Billing (for future)
    subscription_tier = Column(String, default="free", nullable=False)
    subscription_expires = Column(DateTime, nullable=True)

    # Usage tracking
    total_voters = Column(Integer, default=0, nullable=False)
    total_questions = Column(Integer, default=0, nullable=False)
    total_ballots = Column(Integer, default=0, nullable=False)

    # Onboarding
    onboarding_completed = Column(Boolean, default=False, nullable=False)
    onboarding_step = Column(Integer, default=0, nullable=False)
    onboarding_data = Column(JSON, nullable=True)  # Temporary onboarding state

    # Relationships
    staff = relationship("CityStaff", back_populates="city", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<City {self.name} ({self.state})>"


class CityStaff(Base):
    """
    City Staff model

    Links users to cities with specific roles.
    A user can be staff for multiple cities.
    """
    __tablename__ = "city_staff"

    # References
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Role and permissions
    role = Column(Enum(CityStaffRole), default=CityStaffRole.VIEWER, nullable=False)

    # Invitation tracking
    invited_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    invited_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Access control
    is_active = Column(Boolean, default=True, nullable=False)
    last_access = Column(DateTime, nullable=True)

    # Relationships
    city = relationship("City", back_populates="staff")
    user = relationship("User", foreign_keys=[user_id])
    invited_by = relationship("User", foreign_keys=[invited_by_id])

    def __repr__(self):
        return f"<CityStaff city={self.city_id} user={self.user_id} role={self.role}>"


class CityInvitation(Base):
    """
    City Staff Invitation model

    Tracks pending invitations to join city staff.
    """
    __tablename__ = "city_invitations"

    # References
    city_id = Column(Integer, ForeignKey("cities.id", ondelete="CASCADE"), nullable=False)

    # Invitation details
    email = Column(String, nullable=False, index=True)
    role = Column(Enum(CityStaffRole), default=CityStaffRole.VIEWER, nullable=False)

    # Token for accepting invitation
    token = Column(String, unique=True, nullable=False, index=True)

    # Tracking
    invited_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    invited_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    # Status
    accepted = Column(Boolean, default=False, nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    accepted_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    city = relationship("City")
    invited_by = relationship("User", foreign_keys=[invited_by_id])
    accepted_by = relationship("User", foreign_keys=[accepted_by_id])

    def __repr__(self):
        return f"<CityInvitation {self.email} to city={self.city_id}>"
