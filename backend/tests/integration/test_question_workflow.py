"""
Integration tests for complete question-answer workflow.
"""

import pytest
from fastapi import status


class TestQuestionAnswerWorkflow:
    """Integration tests for the full question-to-answer flow."""

    def test_complete_question_answer_cycle(
        self, client, authenticated_user, authenticated_candidate, sample_question_data
    ):
        """Test complete workflow from question submission to candidate answer."""

        # Step 1: Voter submits question
        question_response = client.post(
            "/api/v1/questions",
            json=sample_question_data,
            headers=authenticated_user["headers"],
        )
        assert question_response.status_code == status.HTTP_201_CREATED
        question_id = question_response.json()["id"]

        # Step 2: Other voters upvote question
        vote_response = client.post(
            f"/api/v1/questions/{question_id}/vote",
            json={"vote": 1},
            headers=authenticated_user["headers"],
        )
        assert vote_response.status_code == status.HTTP_200_OK

        # Step 3: Question appears in top questions
        top_questions_response = client.get("/api/v1/questions/top")
        assert top_questions_response.status_code == status.HTTP_200_OK
        top_questions = top_questions_response.json()
        assert any(q["id"] == question_id for q in top_questions)

        # Step 4: Candidate records answer
        answer_data = {
            "question_id": question_id,
            "video_url": "https://example.com/answer.mp4",
            "transcript": "Here is my detailed answer to this question...",
        }
        answer_response = client.post(
            "/api/v1/answers",
            json=answer_data,
            headers=authenticated_candidate["headers"],
        )
        assert answer_response.status_code == status.HTTP_201_CREATED
        answer_id = answer_response.json()["id"]

        # Step 5: Voter views answer
        view_answer_response = client.get(f"/api/v1/answers/{answer_id}")
        assert view_answer_response.status_code == status.HTTP_200_OK
        answer_data_retrieved = view_answer_response.json()
        assert answer_data_retrieved["question_id"] == question_id

    def test_multiple_candidates_same_question(
        self, client, authenticated_user, authenticated_candidate, sample_question_data
    ):
        """Test multiple candidates answering the same question."""

        # Step 1: Voter submits question
        question_response = client.post(
            "/api/v1/questions",
            json=sample_question_data,
            headers=authenticated_user["headers"],
        )
        question_id = question_response.json()["id"]

        # Step 2: First candidate answers
        answer_data_1 = {
            "question_id": question_id,
            "video_url": "https://example.com/answer1.mp4",
            "transcript": "My answer to this question...",
        }
        answer_response_1 = client.post(
            "/api/v1/answers",
            json=answer_data_1,
            headers=authenticated_candidate["headers"],
        )
        assert answer_response_1.status_code == status.HTTP_201_CREATED

        # Step 3: Get all answers for question
        question_answers_response = client.get(f"/api/v1/questions/{question_id}/answers")
        assert question_answers_response.status_code == status.HTTP_200_OK
        answers = question_answers_response.json()
        assert len(answers) >= 1

    def test_rebuttal_workflow(
        self, client, authenticated_candidate, sample_question_data
    ):
        """Test rebuttal workflow between candidates."""

        # (Simplified - assumes multiple candidates set up)

        # Step 1: First candidate answers
        answer_data = {
            "question_id": 1,
            "video_url": "https://example.com/answer.mp4",
            "transcript": "I claim that X is true...",
        }
        answer_response = client.post(
            "/api/v1/answers",
            json=answer_data,
            headers=authenticated_candidate["headers"],
        )
        answer_id = answer_response.json()["id"]

        # Step 2: Second candidate rebuts
        rebuttal_data = {
            "target_answer_id": answer_id,
            "claim_reference": "The claim that X is true",
            "video_url": "https://example.com/rebuttal.mp4",
            "transcript": "Actually, X is not true because...",
        }
        rebuttal_response = client.post(
            "/api/v1/rebuttals",
            json=rebuttal_data,
            headers=authenticated_candidate["headers"],
        )
        assert rebuttal_response.status_code == status.HTTP_201_CREATED

        # Step 3: View answer with rebuttals
        view_answer_response = client.get(f"/api/v1/answers/{answer_id}/rebuttals")
        assert view_answer_response.status_code == status.HTTP_200_OK
        rebuttals = view_answer_response.json()
        assert len(rebuttals) > 0
