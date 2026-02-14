"""
Pydantic Schemas for Request/Response Validation
"""

from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    VerificationStart,
    VerificationComplete,
)
from app.schemas.question import (
    QuestionCreate,
    QuestionResponse,
    QuestionList,
    QuestionVote,
    QuestionEdit,
    QuestionVersionResponse,
)
from app.schemas.ballot import (
    BallotResponse,
    ContestResponse,
    CandidateResponse,
)
from app.schemas.answer import (
    AnswerCreate,
    AnswerResponse,
    RebuttalCreate,
    RebuttalResponse,
)

__all__ = [
    # User schemas
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "Token",
    "VerificationStart",
    "VerificationComplete",
    # Question schemas
    "QuestionCreate",
    "QuestionResponse",
    "QuestionList",
    "QuestionVote",
    "QuestionEdit",
    "QuestionVersionResponse",
    # Ballot schemas
    "BallotResponse",
    "ContestResponse",
    "CandidateResponse",
    # Answer schemas
    "AnswerCreate",
    "AnswerResponse",
    "RebuttalCreate",
    "RebuttalResponse",
]
