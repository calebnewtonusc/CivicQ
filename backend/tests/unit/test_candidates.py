"""
Unit tests for candidate functionality.
"""

import pytest
from fastapi import status


class TestCandidateAnswers:
    """Tests for candidate answer recording."""

    def test_record_answer(self, client, authenticated_candidate, sample_question_data):
        """Test candidate recording an answer."""
        # Create question first (as voter)
        # ... (simplified for example)

        answer_data = {
            "question_id": 1,
            "video_url": "https://example.com/video.mp4",
            "transcript": "My answer to the question...",
        }

        response = client.post(
            "/api/v1/answers",
            json=answer_data,
            headers=authenticated_candidate["headers"],
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["transcript"] == answer_data["transcript"]
        assert "id" in data

    def test_record_answer_non_candidate(self, client, authenticated_user):
        """Test that non-candidates cannot record answers."""
        answer_data = {
            "question_id": 1,
            "video_url": "https://example.com/video.mp4",
            "transcript": "My answer...",
        }

        response = client.post(
            "/api/v1/answers", json=answer_data, headers=authenticated_user["headers"]
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_candidate_answers(self, client, authenticated_candidate):
        """Test retrieving candidate's answers."""
        candidate_id = authenticated_candidate["candidate"]["id"]
        response = client.get(f"/api/v1/candidates/{candidate_id}/answers")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_update_answer_transcript(self, client, authenticated_candidate):
        """Test updating answer transcript (corrections only)."""
        # Create answer first
        answer_data = {
            "question_id": 1,
            "video_url": "https://example.com/video.mp4",
            "transcript": "Original transcript",
        }
        create_response = client.post(
            "/api/v1/answers",
            json=answer_data,
            headers=authenticated_candidate["headers"],
        )
        answer_id = create_response.json()["id"]

        # Update transcript
        updated_data = {"transcript": "Corrected transcript"}
        response = client.patch(
            f"/api/v1/answers/{answer_id}",
            json=updated_data,
            headers=authenticated_candidate["headers"],
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["transcript"] == updated_data["transcript"]


class TestCandidateRebuttals:
    """Tests for candidate rebuttals."""

    def test_submit_rebuttal(self, client, authenticated_candidate):
        """Test submitting a rebuttal to another candidate's answer."""
        rebuttal_data = {
            "target_answer_id": 1,
            "claim_reference": "opponent stated X",
            "video_url": "https://example.com/rebuttal.mp4",
            "transcript": "That claim is incorrect because...",
        }

        response = client.post(
            "/api/v1/rebuttals",
            json=rebuttal_data,
            headers=authenticated_candidate["headers"],
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["transcript"] == rebuttal_data["transcript"]

    def test_rebuttal_without_claim_reference(self, client, authenticated_candidate):
        """Test that rebuttals require specific claim reference."""
        rebuttal_data = {
            "target_answer_id": 1,
            "video_url": "https://example.com/rebuttal.mp4",
            "transcript": "General attack without specific claim",
        }

        response = client.post(
            "/api/v1/rebuttals",
            json=rebuttal_data,
            headers=authenticated_candidate["headers"],
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestCandidateProfile:
    """Tests for candidate profile management."""

    def test_get_candidate_profile(self, client, authenticated_candidate):
        """Test retrieving candidate profile."""
        candidate_id = authenticated_candidate["candidate"]["id"]
        response = client.get(f"/api/v1/candidates/{candidate_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == candidate_id

    def test_update_candidate_profile(self, client, authenticated_candidate):
        """Test updating candidate profile."""
        updated_data = {"bio": "Updated candidate bio"}
        response = client.patch(
            "/api/v1/candidates/me",
            json=updated_data,
            headers=authenticated_candidate["headers"],
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["bio"] == updated_data["bio"]
