"""
Ballot Import Schemas

Pydantic models for normalizing ballot data from external APIs
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date
from enum import Enum

from app.models.ballot import ContestType


class ImportSource(str, Enum):
    """Source of imported ballot data"""
    GOOGLE_CIVIC = "google_civic"
    VOTE_AMERICA = "vote_america"
    BALLOTPEDIA = "ballotpedia"
    MANUAL = "manual"


class ImportedCandidate(BaseModel):
    """Normalized candidate data from external source"""
    name: str
    filing_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    photo_url: Optional[str] = None
    party: Optional[str] = None
    profile_fields: Optional[Dict[str, Any]] = None

    @validator("name")
    def normalize_name(cls, v):
        """Normalize candidate name"""
        return v.strip()

    @validator("email")
    def normalize_email(cls, v):
        """Normalize email address"""
        if v:
            return v.strip().lower()
        return v


class ImportedMeasure(BaseModel):
    """Normalized ballot measure data from external source"""
    measure_number: str = Field(..., description="e.g., 'Prop 1', 'Measure A'")
    measure_text: str = Field(..., description="Full text of the measure")
    summary: Optional[str] = None
    fiscal_notes: Optional[str] = None
    pro_statement: Optional[str] = None
    con_statement: Optional[str] = None


class ImportedContest(BaseModel):
    """Normalized contest data from external source"""
    title: str
    jurisdiction: str
    office: Optional[str] = None  # For races
    seat_count: Optional[int] = 1  # For multi-seat races
    description: Optional[str] = None
    contest_type: ContestType
    candidates: List[ImportedCandidate] = []
    measure: Optional[ImportedMeasure] = None

    @validator("candidates")
    def validate_race_has_candidates(cls, v, values):
        """Ensure races have candidates"""
        if values.get("contest_type") == ContestType.RACE and len(v) == 0:
            raise ValueError("Races must have at least one candidate")
        return v

    @validator("measure")
    def validate_measure_has_data(cls, v, values):
        """Ensure measures have measure data"""
        if values.get("contest_type") == ContestType.MEASURE and v is None:
            raise ValueError("Ballot measures must have measure data")
        return v


class ImportedBallot(BaseModel):
    """Normalized ballot data from external source"""
    city_id: str = Field(..., description="Unique city identifier (e.g., 'los-angeles-ca')")
    city_name: str
    state: str = Field(..., description="State abbreviation (e.g., 'CA', 'NY')")
    election_date: date
    election_name: str = Field(..., description="e.g., 'November 2024 General Election'")
    source: ImportSource
    sources: List[ImportSource] = Field(default_factory=list)
    contests: List[ImportedContest] = []
    source_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Raw metadata from source API"
    )

    @validator("city_id")
    def normalize_city_id(cls, v):
        """Normalize city ID to lowercase with hyphens"""
        return v.lower().replace(" ", "-")

    @validator("state")
    def validate_state(cls, v):
        """Validate state abbreviation"""
        if len(v) != 2:
            raise ValueError("State must be 2-letter abbreviation")
        return v.upper()


class BallotImportRequest(BaseModel):
    """Request to import ballot data"""
    address: Optional[str] = None
    city_name: Optional[str] = None
    state: Optional[str] = None
    election_date: Optional[date] = None
    sources: List[ImportSource] = [
        ImportSource.GOOGLE_CIVIC,
        ImportSource.VOTE_AMERICA,
        ImportSource.BALLOTPEDIA,
    ]

    @validator("sources")
    def validate_sources(cls, v):
        """Ensure at least one source is specified"""
        if len(v) == 0:
            raise ValueError("At least one source must be specified")
        return v

    def validate_request(self):
        """Validate that either address OR city+state is provided"""
        has_address = bool(self.address)
        has_city = bool(self.city_name and self.state)

        if not has_address and not has_city:
            raise ValueError("Either 'address' or 'city_name' + 'state' must be provided")

        if has_address and has_city:
            raise ValueError("Provide either 'address' OR 'city_name' + 'state', not both")


class BallotImportResponse(BaseModel):
    """Response from ballot import"""
    success: bool
    ballot_id: Optional[int] = None
    city_name: str
    election_date: date
    contests_imported: int
    candidates_imported: int
    measures_imported: int
    sources_used: List[ImportSource]
    warnings: List[str] = []
    errors: List[str] = []


class BallotRefreshRequest(BaseModel):
    """Request to refresh ballot data"""
    ballot_id: int
    sources: List[ImportSource] = [
        ImportSource.GOOGLE_CIVIC,
        ImportSource.VOTE_AMERICA,
        ImportSource.BALLOTPEDIA,
    ]


class BallotImportStatus(BaseModel):
    """Status of ballot import/data quality"""
    ballot_id: int
    city_name: str
    election_date: str
    version: int
    is_published: bool
    last_updated: str
    sources: List[str]
    statistics: Dict[str, Any] = Field(
        description="Data quality statistics"
    )


class CandidateContactUpdate(BaseModel):
    """Update contact information for a candidate"""
    candidate_id: int
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None


class BulkContactImport(BaseModel):
    """Bulk import contact information for candidates"""
    ballot_id: int
    candidates: List[CandidateContactUpdate]
