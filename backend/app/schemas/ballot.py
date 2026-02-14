"""
Ballot and Contest-related Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class ContestType(str, Enum):
    """Contest type enum"""
    RACE = "race"
    MEASURE = "measure"


class BallotResponse(BaseModel):
    """Schema for ballot response"""
    id: int
    city: str
    election_date: date
    contests: List["ContestResponse"]
    created_at: datetime

    class Config:
        from_attributes = True


class ContestResponse(BaseModel):
    """Schema for contest response"""
    id: int
    ballot_id: int
    contest_type: ContestType
    title: str
    office: Optional[str]
    jurisdiction: str
    candidates: List["CandidateResponse"] = []
    question_count: int = 0
    answered_count: int = 0

    class Config:
        from_attributes = True


class CandidateResponse(BaseModel):
    """Schema for candidate response"""
    id: int
    contest_id: int
    name: str
    filing_id: Optional[str]
    email: Optional[str]
    is_verified: bool = False
    answer_count: int = 0

    class Config:
        from_attributes = True


# Update forward refs
BallotResponse.model_rebuild()
ContestResponse.model_rebuild()
