"""
Contest API Routes

Handles contest information, candidate lookup, and question retrieval.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from app.models.base import get_db
from app.models.ballot import Contest, Candidate
from app.models.question import Question
from app.models.answer import VideoAnswer
from app.schemas.ballot import ContestResponse, CandidateResponse

router = APIRouter()


@router.get("/", response_model=List[ContestResponse])
async def get_contests(
    ballot_id: int = Query(..., description="Ballot ID to get contests for"),
    db: Session = Depends(get_db)
):
    """
    Get contests for a ballot

    Returns all contests (races and measures) for a specific ballot.
    Public endpoint - no authentication required.

    Args:
        ballot_id: Ballot ID
        db: Database session

    Returns:
        List of contests with candidates

    Raises:
        HTTPException 404: If no contests found
    """
    contests = db.query(Contest).filter(
        Contest.ballot_id == ballot_id
    ).order_by(
        Contest.display_order,
        Contest.id
    ).all()

    if not contests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No contests found for ballot {ballot_id}"
        )

    # Build response with question and answer counts
    result = []
    for contest in contests:
        # Get question count
        question_count = db.query(func.count(Question.id)).filter(
            Question.contest_id == contest.id
        ).scalar() or 0

        # Get answered question count
        answered_count = db.query(func.count(distinct(Question.id))).join(
            VideoAnswer, VideoAnswer.question_id == Question.id
        ).filter(
            Question.contest_id == contest.id
        ).scalar() or 0

        contest_response = ContestResponse(
            id=contest.id,
            ballot_id=contest.ballot_id,
            contest_type=contest.type,
            title=contest.title,
            office=contest.office,
            jurisdiction=contest.jurisdiction,
            candidates=[CandidateResponse.model_validate(c) for c in contest.candidates],
            question_count=question_count,
            answered_count=answered_count
        )
        result.append(contest_response)

    return result


@router.get("/{contest_id}", response_model=ContestResponse)
async def get_contest(
    contest_id: int,
    db: Session = Depends(get_db)
):
    """
    Get contest details

    Returns detailed information about a specific contest including
    all candidates and question statistics.
    Public endpoint - no authentication required.

    Args:
        contest_id: Contest ID
        db: Database session

    Returns:
        Contest details with candidates

    Raises:
        HTTPException 404: If contest not found
    """
    contest = db.query(Contest).filter(Contest.id == contest_id).first()

    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contest not found"
        )

    # Get question count
    question_count = db.query(func.count(Question.id)).filter(
        Question.contest_id == contest.id
    ).scalar() or 0

    # Get answered question count
    answered_count = db.query(func.count(distinct(Question.id))).join(
        VideoAnswer, VideoAnswer.question_id == Question.id
    ).filter(
        Question.contest_id == contest.id
    ).scalar() or 0

    # Build candidate responses with answer counts
    candidates_data = []
    for candidate in contest.candidates:
        # Get answer count for this candidate
        answer_count = db.query(func.count(VideoAnswer.id)).filter(
            VideoAnswer.candidate_id == candidate.id
        ).scalar() or 0

        candidate_response = CandidateResponse(
            id=candidate.id,
            contest_id=candidate.contest_id,
            name=candidate.name,
            filing_id=candidate.filing_id,
            email=candidate.email,
            is_verified=candidate.identity_verified,
            answer_count=answer_count
        )
        candidates_data.append(candidate_response)

    return ContestResponse(
        id=contest.id,
        ballot_id=contest.ballot_id,
        contest_type=contest.type,
        title=contest.title,
        office=contest.office,
        jurisdiction=contest.jurisdiction,
        candidates=candidates_data,
        question_count=question_count,
        answered_count=answered_count
    )


@router.get("/{contest_id}/candidates", response_model=List[CandidateResponse])
async def get_contest_candidates(
    contest_id: int,
    db: Session = Depends(get_db)
):
    """
    Get candidates for a contest

    Returns all candidates running in a specific contest.
    Public endpoint - no authentication required.

    Args:
        contest_id: Contest ID
        db: Database session

    Returns:
        List of candidates

    Raises:
        HTTPException 404: If contest not found
    """
    # Verify contest exists
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contest not found"
        )

    # Get candidates
    candidates = db.query(Candidate).filter(
        Candidate.contest_id == contest_id
    ).order_by(
        Candidate.display_order,
        Candidate.name
    ).all()

    # Build response with answer counts
    result = []
    for candidate in candidates:
        answer_count = db.query(func.count(VideoAnswer.id)).filter(
            VideoAnswer.candidate_id == candidate.id
        ).scalar() or 0

        candidate_response = CandidateResponse(
            id=candidate.id,
            contest_id=candidate.contest_id,
            name=candidate.name,
            filing_id=candidate.filing_id,
            email=candidate.email,
            is_verified=candidate.identity_verified,
            answer_count=answer_count
        )
        result.append(candidate_response)

    return result
