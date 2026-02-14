"""
Unit tests for Question, QuestionVersion, and Vote models.
"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.question import Question, QuestionVersion, Vote, QuestionStatus
from app.models.user import User, UserRole
from app.models.ballot import Contest


class TestQuestionModel:
    """Test Question model functionality."""

    def test_create_question(self, db_session):
        """Test creating a new question."""
        # Create dependencies
        user = User(email="voter@example.com", hashed_password="hashed", role=UserRole.VOTER)
        db_session.add(user)

        contest = Contest(
            title="Mayor",
            contest_type="race",
            city_id="test-city",
        )
        db_session.add(contest)
        db_session.commit()

        question = Question(
            contest_id=contest.id,
            author_id=user.id,
            question_text="What is your plan for affordable housing?",
            issue_tags=["housing", "economy"],
            status=QuestionStatus.PENDING,
        )
        db_session.add(question)
        db_session.commit()

        assert question.id is not None
        assert question.question_text == "What is your plan for affordable housing?"
        assert "housing" in question.issue_tags
        assert question.status == QuestionStatus.PENDING
        assert question.upvotes == 0
        assert question.downvotes == 0

    def test_question_status_transitions(self, db_session):
        """Test question status transitions."""
        user = User(email="voter@example.com", hashed_password="hashed")
        db_session.add(user)

        contest = Contest(title="Mayor", contest_type="race", city_id="test-city")
        db_session.add(contest)
        db_session.commit()

        question = Question(
            contest_id=contest.id,
            author_id=user.id,
            question_text="Test question",
            status=QuestionStatus.PENDING,
        )
        db_session.add(question)
        db_session.commit()

        # Approve question
        question.status = QuestionStatus.APPROVED
        db_session.commit()
        assert question.status == QuestionStatus.APPROVED

        # Merge question
        question.status = QuestionStatus.MERGED
        db_session.commit()
        assert question.status == QuestionStatus.MERGED

    def test_question_with_context(self, db_session):
        """Test question with additional context."""
        user = User(email="voter@example.com", hashed_password="hashed")
        db_session.add(user)

        contest = Contest(title="Mayor", contest_type="race", city_id="test-city")
        db_session.add(contest)
        db_session.commit()

        context_text = "I'm asking this because my rent has doubled in the last 3 years."
        question = Question(
            contest_id=contest.id,
            author_id=user.id,
            question_text="What will you do about rising housing costs?",
            context=context_text,
        )
        db_session.add(question)
        db_session.commit()

        assert question.context == context_text

    def test_question_clustering(self, db_session):
        """Test question clustering for deduplication."""
        user = User(email="voter@example.com", hashed_password="hashed")
        db_session.add(user)

        contest = Contest(title="Mayor", contest_type="race", city_id="test-city")
        db_session.add(contest)
        db_session.commit()

        q1 = Question(
            contest_id=contest.id,
            author_id=user.id,
            question_text="What will you do about housing?",
            cluster_id=1,
        )
        q2 = Question(
            contest_id=contest.id,
            author_id=user.id,
            question_text="What's your plan for affordable housing?",
            cluster_id=1,
        )
        db_session.add_all([q1, q2])
        db_session.commit()

        assert q1.cluster_id == q2.cluster_id

    def test_question_ranking(self, db_session):
        """Test question ranking and score."""
        user = User(email="voter@example.com", hashed_password="hashed")
        db_session.add(user)

        contest = Contest(title="Mayor", contest_type="race", city_id="test-city")
        db_session.add(contest)
        db_session.commit()

        question = Question(
            contest_id=contest.id,
            author_id=user.id,
            question_text="Test question",
            upvotes=10,
            downvotes=2,
            rank_score=8.5,
        )
        db_session.add(question)
        db_session.commit()

        assert question.upvotes == 10
        assert question.downvotes == 2
        assert question.rank_score == 8.5

    def test_question_moderation(self, db_session):
        """Test question moderation features."""
        user = User(email="voter@example.com", hashed_password="hashed")
        db_session.add(user)

        contest = Contest(title="Mayor", contest_type="race", city_id="test-city")
        db_session.add(contest)
        db_session.commit()

        question = Question(
            contest_id=contest.id,
            author_id=user.id,
            question_text="Test question",
            is_flagged=3,
            moderation_notes="Contains offensive language",
        )
        db_session.add(question)
        db_session.commit()

        assert question.is_flagged == 3
        assert question.moderation_notes is not None

    def test_question_contest_relationship(self, db_session):
        """Test relationship between questions and contests."""
        user = User(email="voter@example.com", hashed_password="hashed")
        db_session.add(user)

        contest = Contest(title="Mayor", contest_type="race", city_id="test-city")
        db_session.add(contest)
        db_session.commit()

        for i in range(5):
            question = Question(
                contest_id=contest.id,
                author_id=user.id,
                question_text=f"Question {i}",
            )
            db_session.add(question)
        db_session.commit()

        db_session.refresh(contest)
        assert len(contest.questions) == 5

    def test_question_cascade_delete_with_contest(self, db_session):
        """Test that questions are deleted when contest is deleted."""
        user = User(email="voter@example.com", hashed_password="hashed")
        db_session.add(user)

        contest = Contest(title="Mayor", contest_type="race", city_id="test-city")
        db_session.add(contest)
        db_session.commit()

        question = Question(
            contest_id=contest.id,
            author_id=user.id,
            question_text="Test question",
        )
        db_session.add(question)
        db_session.commit()

        contest_id = contest.id
        db_session.delete(contest)
        db_session.commit()

        # Question should be deleted
        result = db_session.query(Question).filter_by(contest_id=contest_id).first()
        assert result is None


class TestQuestionVersionModel:
    """Test QuestionVersion model functionality."""

    def test_create_question_version(self, db_session):
        """Test creating a question version."""
        user = User(email="voter@example.com", hashed_password="hashed")
        db_session.add(user)

        contest = Contest(title="Mayor", contest_type="race", city_id="test-city")
        db_session.add(contest)
        db_session.commit()

        question = Question(
            contest_id=contest.id,
            author_id=user.id,
            question_text="Original question",
        )
        db_session.add(question)
        db_session.commit()

        version = QuestionVersion(
            question_id=question.id,
            version_number=1,
            question_text="Original question",
            edit_author_id=user.id,
        )
        db_session.add(version)
        db_session.commit()

        assert version.id is not None
        assert version.question_id == question.id
        assert version.version_number == 1

    def test_question_version_history(self, db_session):
        """Test tracking multiple versions of a question."""
        user = User(email="voter@example.com", hashed_password="hashed")
        db_session.add(user)

        contest = Contest(title="Mayor", contest_type="race", city_id="test-city")
        db_session.add(contest)
        db_session.commit()

        question = Question(
            contest_id=contest.id,
            author_id=user.id,
            question_text="Version 3 text",
        )
        db_session.add(question)
        db_session.commit()

        # Create version history
        versions = [
            QuestionVersion(
                question_id=question.id,
                version_number=1,
                question_text="Version 1 text",
                edit_author_id=user.id,
            ),
            QuestionVersion(
                question_id=question.id,
                version_number=2,
                question_text="Version 2 text",
                edit_author_id=user.id,
                edit_reason="Clarified wording",
            ),
            QuestionVersion(
                question_id=question.id,
                version_number=3,
                question_text="Version 3 text",
                edit_author_id=user.id,
                edit_reason="Fixed typo",
            ),
        ]
        db_session.add_all(versions)
        db_session.commit()

        db_session.refresh(question)
        assert len(question.versions) == 3

    def test_question_version_with_diff(self, db_session):
        """Test version with diff metadata."""
        user = User(email="voter@example.com", hashed_password="hashed")
        db_session.add(user)

        contest = Contest(title="Mayor", contest_type="race", city_id="test-city")
        db_session.add(contest)
        db_session.commit()

        question = Question(
            contest_id=contest.id,
            author_id=user.id,
            question_text="Updated text",
        )
        db_session.add(question)
        db_session.commit()

        version = QuestionVersion(
            question_id=question.id,
            version_number=2,
            question_text="Updated text",
            edit_author_id=user.id,
            diff_metadata={
                "added": ["Updated"],
                "removed": ["Original"],
            },
        )
        db_session.add(version)
        db_session.commit()

        assert version.diff_metadata["added"] == ["Updated"]
        assert version.diff_metadata["removed"] == ["Original"]


class TestVoteModel:
    """Test Vote model functionality."""

    def test_create_vote(self, db_session):
        """Test creating a vote."""
        user = User(email="voter@example.com", hashed_password="hashed")
        db_session.add(user)

        contest = Contest(title="Mayor", contest_type="race", city_id="test-city")
        db_session.add(contest)
        db_session.commit()

        question = Question(
            contest_id=contest.id,
            author_id=user.id,
            question_text="Test question",
        )
        db_session.add(question)
        db_session.commit()

        vote = Vote(
            user_id=user.id,
            question_id=question.id,
            value=1,  # Upvote
        )
        db_session.add(vote)
        db_session.commit()

        assert vote.id is not None
        assert vote.value == 1
        assert vote.weight == 1.0

    def test_vote_upvote_downvote(self, db_session):
        """Test upvote and downvote values."""
        user = User(email="voter@example.com", hashed_password="hashed")
        db_session.add(user)

        contest = Contest(title="Mayor", contest_type="race", city_id="test-city")
        db_session.add(contest)
        db_session.commit()

        question = Question(
            contest_id=contest.id,
            author_id=user.id,
            question_text="Test question",
        )
        db_session.add(question)
        db_session.commit()

        upvote = Vote(user_id=user.id, question_id=question.id, value=1)
        db_session.add(upvote)
        db_session.commit()

        assert upvote.value == 1

        # Change to downvote
        upvote.value = -1
        db_session.commit()

        assert upvote.value == -1

    def test_vote_unique_constraint(self, db_session):
        """Test that a user can only vote once per question."""
        user = User(email="voter@example.com", hashed_password="hashed")
        db_session.add(user)

        contest = Contest(title="Mayor", contest_type="race", city_id="test-city")
        db_session.add(contest)
        db_session.commit()

        question = Question(
            contest_id=contest.id,
            author_id=user.id,
            question_text="Test question",
        )
        db_session.add(question)
        db_session.commit()

        vote1 = Vote(user_id=user.id, question_id=question.id, value=1)
        db_session.add(vote1)
        db_session.commit()

        vote2 = Vote(user_id=user.id, question_id=question.id, value=-1)
        db_session.add(vote2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_vote_with_risk_score(self, db_session):
        """Test vote with device risk score."""
        user = User(email="voter@example.com", hashed_password="hashed")
        db_session.add(user)

        contest = Contest(title="Mayor", contest_type="race", city_id="test-city")
        db_session.add(contest)
        db_session.commit()

        question = Question(
            contest_id=contest.id,
            author_id=user.id,
            question_text="Test question",
        )
        db_session.add(question)
        db_session.commit()

        vote = Vote(
            user_id=user.id,
            question_id=question.id,
            value=1,
            device_risk_score=0.3,
            weight=0.7,  # Downweighted due to risk
        )
        db_session.add(vote)
        db_session.commit()

        assert vote.device_risk_score == 0.3
        assert vote.weight == 0.7

    def test_vote_with_metadata(self, db_session):
        """Test vote with metadata."""
        user = User(email="voter@example.com", hashed_password="hashed")
        db_session.add(user)

        contest = Contest(title="Mayor", contest_type="race", city_id="test-city")
        db_session.add(contest)
        db_session.commit()

        question = Question(
            contest_id=contest.id,
            author_id=user.id,
            question_text="Test question",
        )
        db_session.add(question)
        db_session.commit()

        vote = Vote(
            user_id=user.id,
            question_id=question.id,
            value=1,
            metadata={
                "user_agent": "Mozilla/5.0",
                "ip_hash": "hashed_ip",
            },
        )
        db_session.add(vote)
        db_session.commit()

        assert vote.metadata["user_agent"] == "Mozilla/5.0"

    def test_vote_cascade_delete(self, db_session):
        """Test that votes are deleted when question is deleted."""
        user = User(email="voter@example.com", hashed_password="hashed")
        db_session.add(user)

        contest = Contest(title="Mayor", contest_type="race", city_id="test-city")
        db_session.add(contest)
        db_session.commit()

        question = Question(
            contest_id=contest.id,
            author_id=user.id,
            question_text="Test question",
        )
        db_session.add(question)
        db_session.commit()

        vote = Vote(user_id=user.id, question_id=question.id, value=1)
        db_session.add(vote)
        db_session.commit()

        question_id = question.id
        db_session.delete(question)
        db_session.commit()

        # Vote should be deleted
        result = db_session.query(Vote).filter_by(question_id=question_id).first()
        assert result is None
