"""
LLM-powered endpoints for AI features.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.models.base import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.question import Question
from app.models.ballot import Contest
from app.services.llm_service import get_llm_service, QuestionAnalysis
from pydantic import BaseModel


router = APIRouter()


class QuestionAnalysisRequest(BaseModel):
    """Request for question analysis"""
    question_text: str
    contest_id: int


class QuestionAnalysisResponse(BaseModel):
    """Response with question analysis"""
    analysis: Dict[str, Any]
    success: bool
    message: str


class DuplicateCheckRequest(BaseModel):
    """Request to check for duplicate questions"""
    question_text: str
    contest_id: int


class DuplicateCheckResponse(BaseModel):
    """Response with duplicate check result"""
    is_duplicate: bool
    similarity_score: float
    matched_question_id: int | None
    explanation: str
    success: bool


class SuggestedQuestionsResponse(BaseModel):
    """Response with suggested questions"""
    questions: List[str]
    success: bool


@router.post("/analyze-question", response_model=QuestionAnalysisResponse)
def analyze_question(
    request: QuestionAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze a question for quality, appropriateness, and categorization.

    Uses Claude AI to evaluate the question and provide suggestions.
    """
    # Get contest details
    contest = db.query(Contest).filter(Contest.id == request.contest_id).first()
    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contest not found"
        )

    try:
        llm_service = get_llm_service()
        analysis = llm_service.analyze_question(
            question_text=request.question_text,
            contest_type=contest.type,
            contest_title=contest.title,
            city_name=contest.ballot.city_name
        )

        return QuestionAnalysisResponse(
            analysis=analysis.dict(),
            success=True,
            message="Question analyzed successfully"
        )

    except Exception as e:
        return QuestionAnalysisResponse(
            analysis={
                "quality_score": 75.0,
                "is_appropriate": True,
                "category": "General",
                "issues": [],
                "suggestions": [],
                "improved_version": None
            },
            success=False,
            message=f"Analysis failed: {str(e)}"
        )


@router.post("/check-duplicate", response_model=DuplicateCheckResponse)
def check_duplicate(
    request: DuplicateCheckRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check if a question is a duplicate of existing questions.

    Uses Claude AI to detect semantically similar questions.
    """
    # Get existing questions for this contest
    existing_questions = db.query(Question).filter(
        Question.contest_id == request.contest_id,
        Question.status == "approved"
    ).all()

    questions_data = [
        {"id": q.id, "text": q.question_text}
        for q in existing_questions
    ]

    try:
        llm_service = get_llm_service()
        result = llm_service.check_duplicate(
            new_question=request.question_text,
            existing_questions=questions_data
        )

        return DuplicateCheckResponse(
            is_duplicate=result.is_duplicate,
            similarity_score=result.similarity_score,
            matched_question_id=result.matched_question_id,
            explanation=result.explanation,
            success=True
        )

    except Exception as e:
        return DuplicateCheckResponse(
            is_duplicate=False,
            similarity_score=0.0,
            matched_question_id=None,
            explanation=f"Duplicate check failed: {str(e)}",
            success=False
        )


@router.get("/suggested-questions/{contest_id}", response_model=SuggestedQuestionsResponse)
def get_suggested_questions(
    contest_id: int,
    num_suggestions: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-generated suggested questions for a contest.

    Uses Claude AI to generate relevant questions based on the contest.
    """
    if num_suggestions < 1 or num_suggestions > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="num_suggestions must be between 1 and 10"
        )

    # Get contest details
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contest not found"
        )

    try:
        llm_service = get_llm_service()
        questions = llm_service.generate_suggested_questions(
            contest_type=contest.type,
            contest_title=contest.title,
            city_name=contest.ballot.city_name,
            num_suggestions=num_suggestions
        )

        return SuggestedQuestionsResponse(
            questions=questions,
            success=True
        )

    except Exception as e:
        return SuggestedQuestionsResponse(
            questions=[],
            success=False
        )


@router.get("/health")
def llm_health_check():
    """Check if LLM service is available"""
    try:
        llm_service = get_llm_service()
        return {
            "status": "healthy",
            "enabled": llm_service.enabled,
            "model": llm_service.model
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
