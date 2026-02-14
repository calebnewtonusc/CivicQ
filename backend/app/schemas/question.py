"""
Question-related Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class QuestionStatus(str, Enum):
    """Question status enum"""
    PENDING = "pending"
    APPROVED = "approved"
    MERGED = "merged"
    REMOVED = "removed"


class QuestionCreate(BaseModel):
    """Schema for creating a question"""
    contest_id: int
    question_text: str = Field(..., min_length=10, max_length=500)
    context: Optional[str] = Field(None, max_length=200)
    issue_tags: List[str] = Field(default_factory=list, max_items=5)


class QuestionResponse(BaseModel):
    """Schema for question response"""
    id: int
    contest_id: int
    author_id: Optional[int]
    question_text: str
    context: Optional[str]
    issue_tags: List[str]
    status: QuestionStatus
    upvotes: int
    downvotes: int
    rank_score: float
    created_at: datetime
    updated_at: datetime
    cluster_id: Optional[int] = None
    current_version: int = 1

    class Config:
        from_attributes = True


class QuestionList(BaseModel):
    """Schema for list of questions"""
    questions: List[QuestionResponse]
    total: int
    page: int
    page_size: int


class QuestionVote(BaseModel):
    """Schema for voting on a question"""
    value: int = Field(..., ge=-1, le=1, description="Vote value: +1 for upvote, -1 for downvote, 0 to remove vote")


class QuestionEdit(BaseModel):
    """Schema for editing a question"""
    question_text: str = Field(..., min_length=10, max_length=500)
    edit_reason: str = Field(..., min_length=5, max_length=200)


class QuestionVersionResponse(BaseModel):
    """Schema for question version response"""
    id: int
    question_id: int
    version_number: int
    question_text: str
    edit_author_id: Optional[int]
    edit_reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
