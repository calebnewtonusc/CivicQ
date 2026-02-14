"""
Question and Ranking API Routes

Handles question submission, voting, editing, and retrieval.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.models.base import get_db
from app.models.user import User
from app.schemas.question import (
    QuestionCreate,
    QuestionResponse,
    QuestionList,
    QuestionVote,
    QuestionEdit,
    QuestionVersionResponse
)
from app.services.question_service import QuestionService
from app.services.vote_service import VoteService
from app.core.security import get_current_user

router = APIRouter()


@router.post("/contest/{contest_id}/questions", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def submit_question(
    contest_id: int,
    question_data: QuestionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a new question for a contest

    Creates a new question that voters want candidates to answer.
    Questions are auto-approved and can be voted on by other users.

    Args:
        contest_id: Contest ID (must match question_data.contest_id)
        question_data: Question content and metadata
        current_user: Authenticated user
        db: Database session

    Returns:
        Created question object

    Raises:
        HTTPException 400: If contest_id mismatch
        HTTPException 404: If contest doesn't exist
    """
    # Validate contest_id match
    if contest_id != question_data.contest_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contest ID in path must match contest ID in request body"
        )

    question = QuestionService.create_question(db, question_data, current_user)
    return QuestionResponse.model_validate(question)


@router.get("/contest/{contest_id}/questions", response_model=QuestionList)
async def get_questions(
    contest_id: int,
    sort: str = Query("top", description="Sort method: top, new, or controversial"),
    issue: Optional[str] = Query(None, description="Filter by issue tag"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Questions per page"),
    db: Session = Depends(get_db)
):
    """
    Get questions for a contest

    Retrieves questions with filtering and sorting options.
    Public endpoint - no authentication required.

    Args:
        contest_id: Contest ID to get questions for
        sort: Sort method (top, new, controversial)
        issue: Optional issue tag filter
        page: Page number (1-indexed)
        page_size: Number of questions per page (max 100)
        db: Database session

    Returns:
        QuestionList with questions and pagination info
    """
    questions = QuestionService.get_questions_by_contest(
        db,
        contest_id=contest_id,
        sort=sort,
        issue=issue,
        page=page,
        page_size=page_size
    )

    return questions


@router.post("/questions/{question_id}/vote")
async def vote_on_question(
    question_id: int,
    vote_data: QuestionVote,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Vote on a question

    Cast an upvote (+1), downvote (-1), or remove vote (0).
    Only verified users can vote.

    Args:
        question_id: Question ID to vote on
        vote_data: Vote value (+1, -1, or 0)
        current_user: Authenticated user
        db: Database session

    Returns:
        Success message and updated vote counts

    Raises:
        HTTPException 403: If user is not verified
        HTTPException 404: If question doesn't exist
    """
    vote = VoteService.vote_on_question(db, question_id, vote_data, current_user)

    # Get updated question
    question = QuestionService.get_question(db, question_id)

    if vote_data.value == 0:
        return {
            "message": "Vote removed",
            "upvotes": question.upvotes,
            "downvotes": question.downvotes,
            "rank_score": question.rank_score
        }
    else:
        return {
            "message": "Vote recorded",
            "vote_value": vote.value,
            "upvotes": question.upvotes,
            "downvotes": question.downvotes,
            "rank_score": question.rank_score
        }


@router.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int,
    db: Session = Depends(get_db)
):
    """
    Get question details

    Retrieves a single question by ID.
    Public endpoint - no authentication required.

    Args:
        question_id: Question ID
        db: Database session

    Returns:
        Question details

    Raises:
        HTTPException 404: If question doesn't exist
    """
    question = QuestionService.get_question(db, question_id)

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )

    return QuestionResponse.model_validate(question)


@router.get("/questions/{question_id}/versions", response_model=List[QuestionVersionResponse])
async def get_question_versions(
    question_id: int,
    db: Session = Depends(get_db)
):
    """
    Get version history for a question

    Retrieves all versions of a question, showing edit history.
    Public endpoint - no authentication required.

    Args:
        question_id: Question ID
        db: Database session

    Returns:
        List of question versions

    Raises:
        HTTPException 404: If question doesn't exist
    """
    versions = QuestionService.get_question_versions(db, question_id)
    return versions


@router.post("/questions/{question_id}/edit", response_model=QuestionResponse)
async def edit_question(
    question_id: int,
    edit_data: QuestionEdit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Edit a question

    Creates a new version of the question with the updated text.
    All edits are tracked in version history.

    Args:
        question_id: Question ID to edit
        edit_data: New question text and edit reason
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated question object

    Raises:
        HTTPException 404: If question doesn't exist
    """
    question = QuestionService.edit_question(db, question_id, edit_data, current_user)
    return QuestionResponse.model_validate(question)


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a question

    Soft deletes a question by changing its status to removed.
    Only the author or moderators can delete.

    Args:
        question_id: Question ID to delete
        current_user: Authenticated user
        db: Database session

    Raises:
        HTTPException 403: If user lacks permission
        HTTPException 404: If question doesn't exist
    """
    QuestionService.delete_question(db, question_id, current_user)
    return None
