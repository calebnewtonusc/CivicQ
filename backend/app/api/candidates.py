"""
Candidate API Routes

Handles candidate profiles, video answers, and rebuttals.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.models.base import get_db
from app.models.ballot import Candidate
from app.models.answer import VideoAnswer, Rebuttal, AnswerStatus
from app.models.question import Question, QuestionStatus
from app.models.user import User
from app.schemas.ballot import CandidateResponse
from app.schemas.answer import AnswerCreate, AnswerResponse, RebuttalCreate, RebuttalResponse
from app.core.security import get_current_user
from pydantic import BaseModel

router = APIRouter()


class CandidateProfileUpdate(BaseModel):
    """Schema for updating candidate profile"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    photo_url: Optional[str] = None
    profile_fields: Optional[Dict[str, Any]] = None


class DashboardStatsResponse(BaseModel):
    """Schema for candidate dashboard statistics"""
    total_questions: int
    answered_questions: int
    pending_questions: int
    total_views: int
    total_upvotes: int
    answer_rate: float
    recent_activity: List[Dict[str, Any]]


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """
    Get candidate details

    Returns candidate profile with answer count.
    Public endpoint - no authentication required.

    Args:
        candidate_id: Candidate ID
        db: Database session

    Returns:
        Candidate details

    Raises:
        HTTPException 404: If candidate not found
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Get answer count
    answer_count = db.query(func.count(VideoAnswer.id)).filter(
        VideoAnswer.candidate_id == candidate_id,
        VideoAnswer.status == AnswerStatus.PUBLISHED
    ).scalar() or 0

    return CandidateResponse(
        id=candidate.id,
        contest_id=candidate.contest_id,
        name=candidate.name,
        filing_id=candidate.filing_id,
        email=candidate.email,
        is_verified=candidate.identity_verified,
        answer_count=answer_count
    )


@router.get("/{candidate_id}/answers", response_model=List[AnswerResponse])
async def get_candidate_answers(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all answers from a candidate

    Returns all published video answers from a specific candidate.
    Public endpoint - no authentication required.

    Args:
        candidate_id: Candidate ID
        db: Database session

    Returns:
        List of video answers

    Raises:
        HTTPException 404: If candidate not found
    """
    # Verify candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Get published answers
    answers = db.query(VideoAnswer).filter(
        VideoAnswer.candidate_id == candidate_id,
        VideoAnswer.status == AnswerStatus.PUBLISHED
    ).order_by(
        VideoAnswer.created_at.desc()
    ).all()

    return [AnswerResponse.model_validate(a) for a in answers]


@router.post("/{candidate_id}/answers", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED)
async def submit_answer(
    candidate_id: int,
    answer_data: AnswerCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a video answer

    Allows a candidate to submit a video answer to a question.
    Only the candidate associated with the user account can submit.

    Args:
        candidate_id: Candidate ID
        answer_data: Answer data with video URL and metadata
        current_user: Authenticated user
        db: Database session

    Returns:
        Created answer object

    Raises:
        HTTPException 403: If user is not the candidate
        HTTPException 404: If candidate or question not found
        HTTPException 400: If answer already exists
    """
    # Get candidate
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Verify user is the candidate or has candidate role
    if candidate.user_id != current_user.id and current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the candidate can submit answers"
        )

    # Verify question exists
    question = db.query(Question).filter(Question.id == answer_data.question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    # Check if answer already exists for this candidate/question
    existing_answer = db.query(VideoAnswer).filter(
        VideoAnswer.candidate_id == candidate_id,
        VideoAnswer.question_id == answer_data.question_id
    ).first()

    if existing_answer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Answer already exists for this question. Use update endpoint to modify."
        )

    # Create answer
    answer = VideoAnswer(
        candidate_id=candidate_id,
        question_id=answer_data.question_id,
        question_version_id=question.current_version_id,
        video_asset_id=answer_data.video_url,  # In production, this would be S3 key
        video_url=answer_data.video_url,
        duration=answer_data.duration,
        transcript_text=answer_data.transcript,
        status=AnswerStatus.PUBLISHED,  # Auto-publish for now
        views=0
    )

    # Store sources if provided
    if answer_data.sources:
        answer.authenticity_metadata = {"sources": answer_data.sources}

    db.add(answer)
    db.commit()
    db.refresh(answer)

    return AnswerResponse.model_validate(answer)


@router.get("/{candidate_id}/rebuttals", response_model=List[RebuttalResponse])
async def get_candidate_rebuttals(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all rebuttals from a candidate

    Returns all published rebuttals from a specific candidate.
    Public endpoint - no authentication required.

    Args:
        candidate_id: Candidate ID
        db: Database session

    Returns:
        List of rebuttals

    Raises:
        HTTPException 404: If candidate not found
    """
    # Verify candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Get published rebuttals
    rebuttals = db.query(Rebuttal).filter(
        Rebuttal.candidate_id == candidate_id,
        Rebuttal.status == AnswerStatus.PUBLISHED
    ).order_by(
        Rebuttal.created_at.desc()
    ).all()

    return [RebuttalResponse.model_validate(r) for r in rebuttals]


@router.post("/{candidate_id}/rebuttals", response_model=RebuttalResponse, status_code=status.HTTP_201_CREATED)
async def submit_rebuttal(
    candidate_id: int,
    rebuttal_data: RebuttalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a rebuttal

    Allows a candidate to submit a rebuttal to another candidate's answer.
    Rebuttals must reference a specific claim from the target answer.

    Args:
        candidate_id: Candidate ID
        rebuttal_data: Rebuttal data with target answer and video
        current_user: Authenticated user
        db: Database session

    Returns:
        Created rebuttal object

    Raises:
        HTTPException 403: If user is not the candidate
        HTTPException 404: If candidate or target answer not found
        HTTPException 400: If rebutting own answer
    """
    # Get candidate
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Verify user is the candidate
    if candidate.user_id != current_user.id and current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the candidate can submit rebuttals"
        )

    # Verify target answer exists
    target_answer = db.query(VideoAnswer).filter(
        VideoAnswer.id == rebuttal_data.answer_id
    ).first()

    if not target_answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target answer not found"
        )

    # Prevent rebutting own answer
    if target_answer.candidate_id == candidate_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot rebut your own answer"
        )

    # Create rebuttal
    rebuttal = Rebuttal(
        candidate_id=candidate_id,
        target_answer_id=rebuttal_data.answer_id,
        target_claim_text=rebuttal_data.claim_reference,
        video_asset_id=rebuttal_data.video_url,  # In production, this would be S3 key
        video_url=rebuttal_data.video_url,
        duration=rebuttal_data.duration,
        transcript_text=rebuttal_data.transcript,
        status=AnswerStatus.PUBLISHED  # Auto-publish for now
    )

    db.add(rebuttal)
    db.commit()
    db.refresh(rebuttal)

    return RebuttalResponse.model_validate(rebuttal)


@router.get("/{candidate_id}/dashboard", response_model=DashboardStatsResponse)
async def get_candidate_dashboard(
    candidate_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get candidate dashboard statistics

    Returns comprehensive statistics for the candidate including:
    - Questions awaiting answers
    - Answered questions count
    - Total views and engagement
    - Recent activity

    Args:
        candidate_id: Candidate ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Dashboard statistics and metrics

    Raises:
        HTTPException 403: If user is not the candidate
        HTTPException 404: If candidate not found
    """
    # Get candidate
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Verify user is the candidate
    if candidate.user_id != current_user.id and current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the candidate can access their dashboard"
        )

    # Get all questions for this candidate's contest
    total_questions = db.query(func.count(Question.id)).filter(
        Question.contest_id == candidate.contest_id,
        Question.status == QuestionStatus.APPROVED
    ).scalar() or 0

    # Get answered questions count
    answered_questions = db.query(func.count(VideoAnswer.id.distinct())).filter(
        VideoAnswer.candidate_id == candidate_id,
        VideoAnswer.status == AnswerStatus.PUBLISHED
    ).scalar() or 0

    # Get total views across all answers
    total_views = db.query(func.coalesce(func.sum(VideoAnswer.views), 0)).filter(
        VideoAnswer.candidate_id == candidate_id,
        VideoAnswer.status == AnswerStatus.PUBLISHED
    ).scalar() or 0

    # Get total upvotes for questions they've answered
    answered_question_ids = db.query(VideoAnswer.question_id).filter(
        VideoAnswer.candidate_id == candidate_id,
        VideoAnswer.status == AnswerStatus.PUBLISHED
    ).subquery()

    total_upvotes = db.query(func.coalesce(func.sum(Question.upvotes), 0)).filter(
        Question.id.in_(answered_question_ids)
    ).scalar() or 0

    # Calculate answer rate
    answer_rate = (answered_questions / total_questions * 100) if total_questions > 0 else 0

    # Get recent activity (last 5 answers)
    recent_answers = db.query(VideoAnswer).filter(
        VideoAnswer.candidate_id == candidate_id
    ).order_by(
        VideoAnswer.created_at.desc()
    ).limit(5).all()

    recent_activity = []
    for answer in recent_answers:
        question = db.query(Question).filter(Question.id == answer.question_id).first()
        recent_activity.append({
            "type": "answer",
            "question_text": question.question_text if question else "Unknown question",
            "question_id": answer.question_id,
            "status": answer.status.value,
            "created_at": answer.created_at.isoformat(),
            "views": answer.views or 0
        })

    return DashboardStatsResponse(
        total_questions=total_questions,
        answered_questions=answered_questions,
        pending_questions=total_questions - answered_questions,
        total_views=total_views,
        total_upvotes=total_upvotes,
        answer_rate=round(answer_rate, 1),
        recent_activity=recent_activity
    )


@router.get("/{candidate_id}/questions/pending")
async def get_pending_questions(
    candidate_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get questions awaiting candidate's answer

    Returns all approved questions for this candidate's contest
    that they haven't answered yet, sorted by rank score.

    Args:
        candidate_id: Candidate ID
        current_user: Authenticated user
        db: Database session

    Returns:
        List of questions awaiting answers

    Raises:
        HTTPException 403: If user is not the candidate
        HTTPException 404: If candidate not found
    """
    # Get candidate
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Verify user is the candidate
    if candidate.user_id != current_user.id and current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the candidate can view pending questions"
        )

    # Get question IDs this candidate has already answered
    answered_question_ids = db.query(VideoAnswer.question_id).filter(
        VideoAnswer.candidate_id == candidate_id
    ).subquery()

    # Get unanswered questions
    pending_questions = db.query(Question).filter(
        Question.contest_id == candidate.contest_id,
        Question.status == QuestionStatus.APPROVED,
        ~Question.id.in_(answered_question_ids)
    ).order_by(
        Question.rank_score.desc(),
        Question.upvotes.desc()
    ).all()

    return [{
        "id": q.id,
        "question_text": q.question_text,
        "issue_tags": q.issue_tags or [],
        "upvotes": q.upvotes,
        "downvotes": q.downvotes,
        "rank_score": q.rank_score,
        "created_at": q.created_at.isoformat(),
        "context": q.context
    } for q in pending_questions]


@router.put("/{candidate_id}/profile", response_model=CandidateResponse)
async def update_candidate_profile(
    candidate_id: int,
    profile_data: CandidateProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update candidate profile information

    Allows a candidate to update their profile including name,
    contact info, website, photo, and custom profile fields.

    Args:
        candidate_id: Candidate ID
        profile_data: Profile update data
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated candidate profile

    Raises:
        HTTPException 403: If user is not the candidate
        HTTPException 404: If candidate not found
    """
    # Get candidate
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    # Verify user is the candidate
    if candidate.user_id != current_user.id and current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the candidate can update their profile"
        )

    # Update fields
    if profile_data.name is not None:
        candidate.name = profile_data.name
    if profile_data.email is not None:
        candidate.email = profile_data.email
    if profile_data.phone is not None:
        candidate.phone = profile_data.phone
    if profile_data.website is not None:
        candidate.website = profile_data.website
    if profile_data.photo_url is not None:
        candidate.photo_url = profile_data.photo_url
    if profile_data.profile_fields is not None:
        # Merge with existing profile fields
        current_fields = candidate.profile_fields or {}
        current_fields.update(profile_data.profile_fields)
        candidate.profile_fields = current_fields

    db.commit()
    db.refresh(candidate)

    # Get answer count
    answer_count = db.query(func.count(VideoAnswer.id)).filter(
        VideoAnswer.candidate_id == candidate_id,
        VideoAnswer.status == AnswerStatus.PUBLISHED
    ).scalar() or 0

    return CandidateResponse(
        id=candidate.id,
        contest_id=candidate.contest_id,
        name=candidate.name,
        filing_id=candidate.filing_id,
        email=candidate.email,
        is_verified=candidate.identity_verified,
        answer_count=answer_count
    )
