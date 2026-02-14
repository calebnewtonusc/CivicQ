"""
Unit tests for question submission and ranking.
"""

import pytest
from fastapi import status


class TestQuestionSubmission:
    """Tests for question submission."""

    def test_submit_question(self, client, authenticated_user, sample_question_data):
        """Test successful question submission."""
        response = client.post(
            "/api/v1/questions",
            json=sample_question_data,
            headers=authenticated_user["headers"],
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["text"] == sample_question_data["text"]
        assert data["issue_tags"] == sample_question_data["issue_tags"]
        assert "id" in data
        assert "created_at" in data

    def test_submit_question_unauthorized(self, client, sample_question_data):
        """Test question submission without authentication."""
        response = client.post("/api/v1/questions", json=sample_question_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_submit_duplicate_question(
        self, client, authenticated_user, sample_question_data
    ):
        """Test submitting duplicate question."""
        # Submit first question
        client.post(
            "/api/v1/questions",
            json=sample_question_data,
            headers=authenticated_user["headers"],
        )

        # Try to submit same question again
        response = client.post(
            "/api/v1/questions",
            json=sample_question_data,
            headers=authenticated_user["headers"],
        )

        # Should suggest existing question
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_409_CONFLICT,
        ]

    def test_submit_question_with_invalid_tags(
        self, client, authenticated_user, sample_question_data
    ):
        """Test submitting question with invalid issue tags."""
        sample_question_data["issue_tags"] = ["invalid-tag-123"]
        response = client.post(
            "/api/v1/questions",
            json=sample_question_data,
            headers=authenticated_user["headers"],
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestQuestionRanking:
    """Tests for question ranking."""

    def test_upvote_question(self, client, authenticated_user, sample_question_data):
        """Test upvoting a question."""
        # Submit question first
        question_response = client.post(
            "/api/v1/questions",
            json=sample_question_data,
            headers=authenticated_user["headers"],
        )
        question_id = question_response.json()["id"]

        # Upvote question
        response = client.post(
            f"/api/v1/questions/{question_id}/vote",
            json={"vote": 1},
            headers=authenticated_user["headers"],
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["vote_count"] > 0

    def test_downvote_question(self, client, authenticated_user, sample_question_data):
        """Test downvoting a question."""
        # Submit question first
        question_response = client.post(
            "/api/v1/questions",
            json=sample_question_data,
            headers=authenticated_user["headers"],
        )
        question_id = question_response.json()["id"]

        # Downvote question
        response = client.post(
            f"/api/v1/questions/{question_id}/vote",
            json={"vote": -1},
            headers=authenticated_user["headers"],
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["vote_count"] <= 0

    def test_vote_twice_same_user(self, client, authenticated_user, sample_question_data):
        """Test that user cannot vote twice on same question."""
        # Submit question first
        question_response = client.post(
            "/api/v1/questions",
            json=sample_question_data,
            headers=authenticated_user["headers"],
        )
        question_id = question_response.json()["id"]

        # First vote
        client.post(
            f"/api/v1/questions/{question_id}/vote",
            json={"vote": 1},
            headers=authenticated_user["headers"],
        )

        # Second vote (should replace first vote)
        response = client.post(
            f"/api/v1/questions/{question_id}/vote",
            json={"vote": -1},
            headers=authenticated_user["headers"],
        )

        assert response.status_code == status.HTTP_200_OK

    def test_get_top_questions(self, client, sample_question_data):
        """Test retrieving top-ranked questions."""
        response = client.get("/api/v1/questions/top")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)


class TestQuestionModeration:
    """Tests for question moderation."""

    def test_report_question(self, client, authenticated_user, sample_question_data):
        """Test reporting a question."""
        # Submit question first
        question_response = client.post(
            "/api/v1/questions",
            json=sample_question_data,
            headers=authenticated_user["headers"],
        )
        question_id = question_response.json()["id"]

        # Report question
        response = client.post(
            f"/api/v1/questions/{question_id}/report",
            json={"reason": "inappropriate", "details": "Contains spam"},
            headers=authenticated_user["headers"],
        )

        assert response.status_code == status.HTTP_201_CREATED

    def test_edit_own_question(self, client, authenticated_user, sample_question_data):
        """Test editing own question."""
        # Submit question first
        question_response = client.post(
            "/api/v1/questions",
            json=sample_question_data,
            headers=authenticated_user["headers"],
        )
        question_id = question_response.json()["id"]

        # Edit question
        updated_data = {"text": "Updated question text?"}
        response = client.patch(
            f"/api/v1/questions/{question_id}",
            json=updated_data,
            headers=authenticated_user["headers"],
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["text"] == updated_data["text"]

    def test_delete_own_question(self, client, authenticated_user, sample_question_data):
        """Test deleting own question."""
        # Submit question first
        question_response = client.post(
            "/api/v1/questions",
            json=sample_question_data,
            headers=authenticated_user["headers"],
        )
        question_id = question_response.json()["id"]

        # Delete question
        response = client.delete(
            f"/api/v1/questions/{question_id}",
            headers=authenticated_user["headers"],
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
