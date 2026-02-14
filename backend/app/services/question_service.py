"""
Question Service

Handles question CRUD operations, ranking, versioning, and clustering.
"""

from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func
from fastapi import HTTPException, status

from app.models.question import Question, QuestionVersion, QuestionStatus
from app.models.ballot import Contest
from app.models.user import User
from app.schemas.question import (
    QuestionCreate,
    QuestionResponse,
    QuestionList,
    QuestionEdit,
    QuestionVersionResponse
)
from app.core.config import settings


class QuestionService:
    """Service for question operations"""

    @staticmethod
    def create_question(
        db: Session,
        question_data: QuestionCreate,
        author: User
    ) -> Question:
        """
        Create a new question

        Args:
            db: Database session
            question_data: Question data
            author: User creating the question

        Returns:
            Created question object

        Raises:
            HTTPException: If contest doesn't exist or user not verified
        """
        # Verify contest exists
        contest = db.query(Contest).filter(Contest.id == question_data.contest_id).first()
        if not contest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contest not found"
            )

        # Check user verification (optional - can be relaxed based on requirements)
        # For now allowing unverified users to ask questions

        # Create question
        question = Question(
            contest_id=question_data.contest_id,
            author_id=author.id,
            question_text=question_data.question_text,
            context=question_data.context,
            issue_tags=question_data.issue_tags or [],
            status=QuestionStatus.APPROVED,  # Auto-approve for now; can add moderation later
            upvotes=0,
            downvotes=0,
            rank_score=0.0
        )

        db.add(question)
        db.commit()
        db.refresh(question)

        # Create initial version
        version = QuestionVersion(
            question_id=question.id,
            version_number=1,
            question_text=question_data.question_text,
            edit_author_id=author.id,
            edit_reason="Initial version"
        )

        db.add(version)
        db.commit()
        db.refresh(version)

        # Update question with current version
        question.current_version_id = version.id
        db.commit()
        db.refresh(question)

        return question

    @staticmethod
    def get_question(db: Session, question_id: int) -> Optional[Question]:
        """
        Get a question by ID

        Args:
            db: Database session
            question_id: Question ID

        Returns:
            Question object or None if not found
        """
        return db.query(Question).filter(Question.id == question_id).first()

    @staticmethod
    def get_questions_by_contest(
        db: Session,
        contest_id: int,
        sort: str = "top",
        issue: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> QuestionList:
        """
        Get questions for a contest with filtering and sorting

        Args:
            db: Database session
            contest_id: Contest ID to filter by
            sort: Sort method ("top", "new", "controversial")
            issue: Issue tag to filter by (optional)
            page: Page number (1-indexed)
            page_size: Number of questions per page

        Returns:
            QuestionList with questions and pagination info
        """
        # Base query
        query = db.query(Question).filter(
            Question.contest_id == contest_id,
            Question.status == QuestionStatus.APPROVED
        )

        # Filter by issue tag if provided
        if issue:
            query = query.filter(Question.issue_tags.contains([issue]))

        # Apply sorting
        if sort == "top":
            query = query.order_by(desc(Question.rank_score))
        elif sort == "new":
            query = query.order_by(desc(Question.created_at))
        elif sort == "controversial":
            # Controversial = high engagement but mixed votes
            query = query.order_by(desc(Question.upvotes + Question.downvotes))
        else:
            query = query.order_by(desc(Question.rank_score))

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        questions = query.offset(offset).limit(page_size).all()

        return QuestionList(
            questions=[QuestionResponse.model_validate(q) for q in questions],
            total=total,
            page=page,
            page_size=page_size
        )

    @staticmethod
    def edit_question(
        db: Session,
        question_id: int,
        edit_data: QuestionEdit,
        editor: User
    ) -> Question:
        """
        Edit a question (creates new version)

        Args:
            db: Database session
            question_id: Question ID to edit
            edit_data: Edit data with new text and reason
            editor: User making the edit

        Returns:
            Updated question object

        Raises:
            HTTPException: If question doesn't exist
        """
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )

        # Check if editor is author or has edit permissions
        # For now, allow anyone to edit (community editing)
        # Can be restricted to author or verified users later

        # Get current version number
        latest_version = db.query(QuestionVersion).filter(
            QuestionVersion.question_id == question_id
        ).order_by(desc(QuestionVersion.version_number)).first()

        new_version_number = (latest_version.version_number + 1) if latest_version else 1

        # Create new version
        new_version = QuestionVersion(
            question_id=question_id,
            version_number=new_version_number,
            question_text=edit_data.question_text,
            edit_author_id=editor.id,
            edit_reason=edit_data.edit_reason
        )

        db.add(new_version)
        db.commit()
        db.refresh(new_version)

        # Update question
        question.question_text = edit_data.question_text
        question.current_version_id = new_version.id
        question.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(question)

        return question

    @staticmethod
    def get_question_versions(
        db: Session,
        question_id: int
    ) -> List[QuestionVersionResponse]:
        """
        Get version history for a question

        Args:
            db: Database session
            question_id: Question ID

        Returns:
            List of question versions

        Raises:
            HTTPException: If question doesn't exist
        """
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )

        versions = db.query(QuestionVersion).filter(
            QuestionVersion.question_id == question_id
        ).order_by(desc(QuestionVersion.version_number)).all()

        return [QuestionVersionResponse.model_validate(v) for v in versions]

    @staticmethod
    def calculate_rank_score(question: Question) -> float:
        """
        Calculate rank score for a question using a modified Wilson score

        This gives a confidence-based ranking that:
        - Rewards questions with more upvotes
        - Penalizes questions with many downvotes
        - Accounts for total vote count (confidence)

        Args:
            question: Question object

        Returns:
            Calculated rank score
        """
        total_votes = question.upvotes + question.downvotes

        if total_votes == 0:
            return 0.0

        # Simple upvote ratio for now
        # Can be enhanced with time decay, diversity bonuses, etc.
        upvote_ratio = question.upvotes / total_votes

        # Apply confidence factor (more votes = more confidence)
        # Using a simple logarithmic scale
        import math
        confidence = min(1.0, math.log(total_votes + 1) / math.log(100))

        # Final score: weighted upvote ratio
        score = upvote_ratio * confidence

        return score

    @staticmethod
    def update_question_rank(db: Session, question: Question) -> Question:
        """
        Update the rank score for a question

        Args:
            db: Database session
            question: Question to update

        Returns:
            Updated question object
        """
        question.rank_score = QuestionService.calculate_rank_score(question)
        db.commit()
        db.refresh(question)
        return question

    @staticmethod
    def delete_question(db: Session, question_id: int, user: User) -> bool:
        """
        Delete a question (soft delete by changing status)

        Args:
            db: Database session
            question_id: Question ID to delete
            user: User requesting deletion

        Returns:
            True if deleted successfully

        Raises:
            HTTPException: If question doesn't exist or user lacks permission
        """
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )

        # Check permissions: author or admin/moderator
        if question.author_id != user.id and user.role not in ["admin", "moderator"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this question"
            )

        # Soft delete
        question.status = QuestionStatus.REMOVED
        db.commit()

        return True
