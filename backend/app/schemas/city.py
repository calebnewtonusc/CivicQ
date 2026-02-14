"""
City Pydantic Schemas

Request/response models for city onboarding and management.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import re


# City Registration


class CityRegistrationRequest(BaseModel):
    """Initial city registration request"""

    # Basic info
    name: str = Field(..., min_length=2, max_length=200, description="City name")
    state: str = Field(..., min_length=2, max_length=2, description="Two-letter state code")
    county: Optional[str] = Field(None, max_length=100)
    population: Optional[int] = Field(None, ge=1)

    # Primary contact (usually city clerk)
    primary_contact_name: str = Field(..., min_length=2, max_length=200)
    primary_contact_email: EmailStr
    primary_contact_phone: Optional[str] = None
    primary_contact_title: Optional[str] = Field(None, max_length=100)

    # Verification
    official_email_domain: Optional[str] = Field(None, description="Official city email domain (e.g., cityofboston.gov)")
    documentation_urls: Optional[List[str]] = Field(default_factory=list, description="Links to official documents proving identity")

    # Account for primary contact
    password: str = Field(..., min_length=8)

    @validator('state')
    def validate_state(cls, v):
        """Ensure state is uppercase two-letter code"""
        v = v.upper()
        # Basic validation - could be more comprehensive
        if not re.match(r'^[A-Z]{2}$', v):
            raise ValueError('State must be a two-letter code')
        return v

    @validator('password')
    def validate_password(cls, v):
        """Basic password validation"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class CityVerificationRequest(BaseModel):
    """Request to verify a city (admin only)"""
    city_id: int
    verification_method: str
    verification_notes: Optional[str] = None
    approved: bool


# City Setup Wizard


class CityBrandingUpdate(BaseModel):
    """Update city branding"""
    logo_url: Optional[str] = None
    primary_color: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')
    secondary_color: Optional[str] = Field(None, regex=r'^#[0-9A-Fa-f]{6}$')


class CityElectionUpdate(BaseModel):
    """Update election information"""
    next_election_date: Optional[date] = None
    election_info_url: Optional[str] = None


class CitySettingsUpdate(BaseModel):
    """Update city settings"""
    timezone: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    features: Optional[Dict[str, bool]] = None


class CityOnboardingComplete(BaseModel):
    """Mark onboarding as complete"""
    completed: bool = True


# Staff Management


class CityStaffInviteRequest(BaseModel):
    """Invite a user to join city staff"""
    email: EmailStr
    role: str = Field(..., description="staff role: owner, admin, editor, moderator, viewer")

    @validator('role')
    def validate_role(cls, v):
        """Validate role"""
        valid_roles = ['owner', 'admin', 'editor', 'moderator', 'viewer']
        if v.lower() not in valid_roles:
            raise ValueError(f'Role must be one of: {", ".join(valid_roles)}')
        return v.lower()


class CityStaffUpdateRequest(BaseModel):
    """Update city staff member"""
    role: Optional[str] = None
    is_active: Optional[bool] = None


class CityStaffInvitationAcceptRequest(BaseModel):
    """Accept city staff invitation"""
    token: str
    password: Optional[str] = Field(None, min_length=8, description="Password if creating new account")


# City Responses


class CityStaffResponse(BaseModel):
    """City staff member response"""
    id: int
    user_id: int
    role: str
    is_active: bool
    invited_at: datetime
    last_access: Optional[datetime]

    # User details
    user_email: Optional[str] = None
    user_full_name: Optional[str] = None

    class Config:
        from_attributes = True


class CityResponse(BaseModel):
    """City response"""
    id: int
    name: str
    slug: str
    state: str
    county: Optional[str]
    population: Optional[int]

    # Contact
    primary_contact_name: str
    primary_contact_email: str
    primary_contact_phone: Optional[str]
    primary_contact_title: Optional[str]

    # Status
    status: str
    verified_at: Optional[datetime]

    # Branding
    logo_url: Optional[str]
    primary_color: Optional[str]
    secondary_color: Optional[str]

    # Configuration
    timezone: str
    settings: Optional[Dict[str, Any]]
    features: Optional[Dict[str, Any]]

    # Election
    next_election_date: Optional[date]
    election_info_url: Optional[str]

    # Onboarding
    onboarding_completed: bool
    onboarding_step: int

    # Metadata
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CityDetailResponse(CityResponse):
    """Detailed city response with staff"""
    staff: List[CityStaffResponse] = []
    total_voters: int
    total_questions: int
    total_ballots: int


class CityListResponse(BaseModel):
    """List of cities"""
    cities: List[CityResponse]
    total: int


# Dashboard Stats


class CityDashboardStats(BaseModel):
    """City dashboard statistics"""
    total_voters: int
    total_questions: int
    total_candidates: int
    total_ballots: int
    total_contests: int

    # Recent activity
    questions_this_week: int
    voters_this_week: int

    # Engagement
    avg_questions_per_contest: float
    avg_votes_per_question: float

    # Upcoming
    next_election_date: Optional[date]
    days_until_election: Optional[int]


# Ballot Import


class BallotImportCandidate(BaseModel):
    """Candidate for import"""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    filing_id: Optional[str] = None
    website: Optional[str] = None


class BallotImportContest(BaseModel):
    """Contest for import"""
    title: str
    type: str  # "race" or "measure"
    office: Optional[str] = None
    jurisdiction: Optional[str] = None
    seat_count: int = 1
    description: Optional[str] = None
    candidates: List[BallotImportCandidate] = []

    # For measures
    measure_number: Optional[str] = None
    measure_text: Optional[str] = None
    summary: Optional[str] = None


class BallotImportRequest(BaseModel):
    """Import ballot data"""
    election_date: date
    contests: List[BallotImportContest]
    source_metadata: Optional[Dict[str, Any]] = None


class BallotImportResponse(BaseModel):
    """Ballot import response"""
    ballot_id: int
    contests_created: int
    candidates_created: int
    measures_created: int
    message: str
