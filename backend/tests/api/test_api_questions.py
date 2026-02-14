"""
API tests for question endpoints.
"""

import pytest
from tests.fixtures.factories import UserFactory, QuestionFactory, ContestFactory, CityFactory


class TestQuestionsCreate:
    """Test question creation endpoint."""

    def test_create_question(self, client, auth_headers, test_contest):
        """Test creating a new question."""
        response = client.post(
            "/api/v1/questions",
            headers=auth_headers,
            json={
                "contest_id": test_contest.id,
                "question_text": "What is your plan for affordable housing?",
                "issue_tags": ["housing", "economy"],
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["question_text"] == "What is your plan for affordable housing?"
        assert "housing" in data["issue_tags"]

    def test_create_question_unauthorized(self, client, test_contest):
        """Test creating question without authentication."""
        response = client.post(
            "/api/v1/questions",
            json={
                "contest_id": test_contest.id,
                "question_text": "Test question?",
            },
        )

        assert response.status_code == 401

    def test_create_question_invalid_contest(self, client, auth_headers):
        """Test creating question for non-existent contest."""
        response = client.post(
            "/api/v1/questions",
            headers=auth_headers,
            json={
                "contest_id": 99999,
                "question_text": "Test question?",
            },
        )

        assert response.status_code == 404

    def test_create_question_with_context(self, client, auth_headers, test_contest):
        """Test creating question with additional context."""
        response = client.post(
            "/api/v1/questions",
            headers=auth_headers,
            json={
                "contest_id": test_contest.id,
                "question_text": "How will you address traffic congestion?",
                "context": "I spend 2 hours commuting each day.",
                "issue_tags": ["transportation"],
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["context"] == "I spend 2 hours commuting each day."


class TestQuestionsGet:
    """Test getting questions endpoint."""

    def test_get_questions_list(self, client, db_session, test_contest, test_user):
        """Test getting list of questions."""
        # Create multiple questions
        for i in range(5):
            QuestionFactory.create_approved(
                db_session,
                contest_id=test_contest.id,
                author_id=test_user.id,
                question_text=f"Question {i}?",
            )

        response = client.get(f"/api/v1/questions?contest_id={test_contest.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5

    def test_get_question_by_id(self, client, db_session, test_contest, test_user):
        """Test getting a specific question."""
        question = QuestionFactory.create_approved(
            db_session,
            contest_id=test_contest.id,
            author_id=test_user.id,
        )

        response = client.get(f"/api/v1/questions/{question.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == question.id

    def test_get_nonexistent_question(self, client):
        """Test getting non-existent question."""
        response = client.get("/api/v1/questions/99999")

        assert response.status_code == 404

    def test_filter_questions_by_status(self, client, db_session, test_contest, test_user):
        """Test filtering questions by status."""
        from app.models.question import QuestionStatus

        # Create approved and pending questions
        QuestionFactory.create(
            db_session,
            contest_id=test_contest.id,
            author_id=test_user.id,
            status=QuestionStatus.APPROVED,
        )
        QuestionFactory.create(
            db_session,
            contest_id=test_contest.id,
            author_id=test_user.id,
            status=QuestionStatus.PENDING,
        )

        response = client.get(
            f"/api/v1/questions?contest_id={test_contest.id}&status=approved"
        )

        assert response.status_code == 200
        data = response.json()
        assert all(q["status"] == "approved" for q in data["items"])

    def test_filter_questions_by_tags(self, client, db_session, test_contest, test_user):
        """Test filtering questions by issue tags."""
        QuestionFactory.create_approved(
            db_session,
            contest_id=test_contest.id,
            author_id=test_user.id,
            issue_tags=["housing", "economy"],
        )
        QuestionFactory.create_approved(
            db_session,
            contest_id=test_contest.id,
            author_id=test_user.id,
            issue_tags=["education"],
        )

        response = client.get(
            f"/api/v1/questions?contest_id={test_contest.id}&tags=housing"
        )

        assert response.status_code == 200
        data = response.json()
        assert all("housing" in q.get("issue_tags", []) for q in data["items"])


class TestQuestionsPagination:
    """Test question pagination."""

    def test_paginate_questions(self, client, db_session, test_contest, test_user):
        """Test paginating questions."""
        # Create 25 questions
        for i in range(25):
            QuestionFactory.create_approved(
                db_session,
                contest_id=test_contest.id,
                author_id=test_user.id,
            )

        # Get first page
        response = client.get(
            f"/api/v1/questions?contest_id={test_contest.id}&page=1&per_page=10"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] == 25
        assert data["pages"] == 3


class TestQuestionsVoting:
    """Test question voting endpoints."""

    def test_upvote_question(self, client, db_session, auth_headers, test_contest, test_user):
        """Test upvoting a question."""
        question = QuestionFactory.create_approved(
            db_session,
            contest_id=test_contest.id,
            author_id=test_user.id,
        )

        response = client.post(
            f"/api/v1/questions/{question.id}/vote",
            headers=auth_headers,
            json={"value": 1},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["upvotes"] == 1

    def test_downvote_question(self, client, db_session, auth_headers, test_contest, test_user):
        """Test downvoting a question."""
        question = QuestionFactory.create_approved(
            db_session,
            contest_id=test_contest.id,
            author_id=test_user.id,
        )

        response = client.post(
            f"/api/v1/questions/{question.id}/vote",
            headers=auth_headers,
            json={"value": -1},
        )

        assert response.status_code == 200

    def test_change_vote(self, client, db_session, auth_headers, test_contest, test_user):
        """Test changing a vote."""
        from tests.fixtures.factories import VoteFactory

        question = QuestionFactory.create_approved(
            db_session,
            contest_id=test_contest.id,
            author_id=test_user.id,
        )

        # Create initial upvote
        response = client.post(
            f"/api/v1/questions/{question.id}/vote",
            headers=auth_headers,
            json={"value": 1},
        )
        assert response.status_code == 200

        # Change to downvote
        response = client.post(
            f"/api/v1/questions/{question.id}/vote",
            headers=auth_headers,
            json={"value": -1},
        )
        assert response.status_code == 200

    def test_vote_unauthorized(self, client, db_session, test_contest, test_user):
        """Test voting without authentication."""
        question = QuestionFactory.create_approved(
            db_session,
            contest_id=test_contest.id,
            author_id=test_user.id,
        )

        response = client.post(
            f"/api/v1/questions/{question.id}/vote",
            json={"value": 1},
        )

        assert response.status_code == 401


class TestQuestionsModeration:
    """Test question moderation endpoints."""

    def test_approve_question(self, client, db_session, admin_headers, test_contest, test_user):
        """Test approving a question."""
        from app.models.question import QuestionStatus

        question = QuestionFactory.create(
            db_session,
            contest_id=test_contest.id,
            author_id=test_user.id,
            status=QuestionStatus.PENDING,
        )

        response = client.post(
            f"/api/v1/admin/questions/{question.id}/approve",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"

    def test_reject_question(self, client, db_session, admin_headers, test_contest, test_user):
        """Test rejecting a question."""
        question = QuestionFactory.create_approved(
            db_session,
            contest_id=test_contest.id,
            author_id=test_user.id,
        )

        response = client.post(
            f"/api/v1/admin/questions/{question.id}/remove",
            headers=admin_headers,
            json={"reason": "Inappropriate content"},
        )

        assert response.status_code == 200

    def test_moderate_question_unauthorized(self, client, db_session, auth_headers, test_contest, test_user):
        """Test that non-admin cannot moderate questions."""
        question = QuestionFactory.create_approved(
            db_session,
            contest_id=test_contest.id,
            author_id=test_user.id,
        )

        response = client.post(
            f"/api/v1/admin/questions/{question.id}/approve",
            headers=auth_headers,
        )

        assert response.status_code == 403


class TestQuestionsSearch:
    """Test question search functionality."""

    def test_search_questions(self, client, db_session, test_contest, test_user):
        """Test searching questions."""
        QuestionFactory.create_approved(
            db_session,
            contest_id=test_contest.id,
            author_id=test_user.id,
            question_text="What is your plan for affordable housing?",
        )
        QuestionFactory.create_approved(
            db_session,
            contest_id=test_contest.id,
            author_id=test_user.id,
            question_text="How will you improve public transportation?",
        )

        response = client.get(
            f"/api/v1/questions/search?q=housing&contest_id={test_contest.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert "housing" in data["items"][0]["question_text"].lower()


class TestQuestionsValidation:
    """Test input validation for questions."""

    def test_create_question_empty_text(self, client, auth_headers, test_contest):
        """Test creating question with empty text."""
        response = client.post(
            "/api/v1/questions",
            headers=auth_headers,
            json={
                "contest_id": test_contest.id,
                "question_text": "",
            },
        )

        assert response.status_code == 422

    def test_create_question_too_long(self, client, auth_headers, test_contest):
        """Test creating question that's too long."""
        response = client.post(
            "/api/v1/questions",
            headers=auth_headers,
            json={
                "contest_id": test_contest.id,
                "question_text": "x" * 10000,  # Extremely long
            },
        )

        assert response.status_code == 422 or response.status_code == 400

    def test_invalid_vote_value(self, client, db_session, auth_headers, test_contest, test_user):
        """Test voting with invalid value."""
        question = QuestionFactory.create_approved(
            db_session,
            contest_id=test_contest.id,
            author_id=test_user.id,
        )

        response = client.post(
            f"/api/v1/questions/{question.id}/vote",
            headers=auth_headers,
            json={"value": 5},  # Invalid, should be 1 or -1
        )

        assert response.status_code == 422 or response.status_code == 400
