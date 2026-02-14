"""
Answer and Rebuttal-related Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AnswerCreate(BaseModel):
    """Schema for creating a video answer"""
    question_id: int
    video_url: str
    duration: int = Field(..., gt=0, le=300, description="Duration in seconds")
    transcript: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None


class AnswerResponse(BaseModel):
    """Schema for answer response"""
    id: int
    question_id: int
    candidate_id: int
    video_url: str
    transcript: Optional[str]
    duration: int
    sources: Optional[List[Dict[str, Any]]]
    created_at: datetime
    views: int = 0

    class Config:
        from_attributes = True


class RebuttalCreate(BaseModel):
    """Schema for creating a rebuttal"""
    answer_id: int
    claim_reference: str = Field(..., max_length=500)
    video_url: str
    duration: int = Field(..., gt=0, le=180, description="Duration in seconds")
    transcript: Optional[str] = None


class RebuttalResponse(BaseModel):
    """Schema for rebuttal response"""
    id: int
    answer_id: int
    candidate_id: int
    claim_reference: str
    video_url: str
    transcript: Optional[str]
    duration: int
    created_at: datetime

    class Config:
        from_attributes = True
