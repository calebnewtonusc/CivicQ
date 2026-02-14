"""
Vote Service

Handles voting operations on questions with fraud detection.
"""

from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status

from app.models.question import Question, Vote
from app.models.user import User, VerificationStatus
from app.schemas.question import QuestionVote
from app.services.question_service import QuestionService


class VoteService:
    """Service for voting operations"""

    @staticmethod
    def vote_on_question(
        db: Session,
        question_id: int,
        vote_data: QuestionVote,
        user: User
    ) -> Vote:
        """
        Vote on a question (upvote, downvote, or remove vote)

        Args:
            db: Database session
            question_id: Question ID to vote on
            vote_data: Vote data with value (+1, -1, or 0)
            user: User casting the vote

        Returns:
            Vote object

        Raises:
            HTTPException: If question doesn't exist or user not verified
        """
        # Get question
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )

        # Check if user is verified (required for voting)
        if user.verification_status != VerificationStatus.VERIFIED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only verified users can vote"
            )

        # Check if user already voted
        existing_vote = db.query(Vote).filter(
            and_(
                Vote.user_id == user.id,
                Vote.question_id == question_id
            )
        ).first()

        # Handle vote value
        if vote_data.value == 0:
            # Remove vote
            if existing_vote:
                VoteService._remove_vote(db, existing_vote, question)
            return None
        elif vote_data.value in [-1, 1]:
            if existing_vote:
                # Update existing vote
                return VoteService._update_vote(db, existing_vote, vote_data.value, question)
            else:
                # Create new vote
                return VoteService._create_vote(db, question_id, vote_data.value, user, question)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vote value must be -1, 0, or 1"
            )

    @staticmethod
    def _create_vote(
        db: Session,
        question_id: int,
        value: int,
        user: User,
        question: Question
    ) -> Vote:
        """
        Create a new vote

        Args:
            db: Database session
            question_id: Question ID
            value: Vote value (+1 or -1)
            user: User casting vote
            question: Question object

        Returns:
            Created vote object
        """
        vote = Vote(
            user_id=user.id,
            question_id=question_id,
            value=value,
            weight=1.0,  # Can be adjusted based on fraud detection
            device_risk_score=0.0  # Can be populated with device fingerprinting
        )

        db.add(vote)

        # Update question vote counts
        if value == 1:
            question.upvotes += 1
        else:
            question.downvotes += 1

        db.commit()
        db.refresh(vote)

        # Update question rank
        QuestionService.update_question_rank(db, question)

        return vote

    @staticmethod
    def _update_vote(
        db: Session,
        existing_vote: Vote,
        new_value: int,
        question: Question
    ) -> Vote:
        """
        Update an existing vote

        Args:
            db: Database session
            existing_vote: Existing vote object
            new_value: New vote value
            question: Question object

        Returns:
            Updated vote object
        """
        old_value = existing_vote.value

        # Don't update if value is the same
        if old_value == new_value:
            return existing_vote

        # Update question vote counts
        if old_value == 1:
            question.upvotes -= 1
        else:
            question.downvotes -= 1

        if new_value == 1:
            question.upvotes += 1
        else:
            question.downvotes += 1

        # Update vote
        existing_vote.value = new_value
        existing_vote.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(existing_vote)

        # Update question rank
        QuestionService.update_question_rank(db, question)

        return existing_vote

    @staticmethod
    def _remove_vote(
        db: Session,
        vote: Vote,
        question: Question
    ) -> None:
        """
        Remove a vote

        Args:
            db: Database session
            vote: Vote object to remove
            question: Question object
        """
        # Update question vote counts
        if vote.value == 1:
            question.upvotes -= 1
        else:
            question.downvotes -= 1

        # Delete vote
        db.delete(vote)
        db.commit()

        # Update question rank
        QuestionService.update_question_rank(db, question)

    @staticmethod
    def get_user_vote(
        db: Session,
        question_id: int,
        user_id: int
    ) -> Optional[Vote]:
        """
        Get a user's vote on a question

        Args:
            db: Database session
            question_id: Question ID
            user_id: User ID

        Returns:
            Vote object or None if user hasn't voted
        """
        return db.query(Vote).filter(
            and_(
                Vote.user_id == user_id,
                Vote.question_id == question_id
            )
        ).first()

    @staticmethod
    def detect_vote_fraud(vote: Vote, user: User) -> float:
        """
        Detect potential vote fraud and return risk score

        This is a placeholder for future fraud detection logic.
        Could include:
        - Device fingerprinting
        - IP analysis
        - Voting pattern analysis
        - Time-based anomaly detection

        Args:
            vote: Vote object
            user: User who cast the vote

        Returns:
            Risk score (0.0 to 1.0, higher = more suspicious)
        """
        # Placeholder implementation
        # In production, this would analyze:
        # - Multiple votes from same device/IP
        # - Rapid voting patterns
        # - Coordinated voting behavior
        # - User account age and activity
        return 0.0
