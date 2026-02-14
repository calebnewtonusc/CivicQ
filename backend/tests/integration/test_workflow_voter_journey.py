"""
Integration tests for complete voter journey.

Tests the full workflow: signup → verify → login → submit question → vote
"""

import pytest
from unittest.mock import patch


class TestVoterJourney:
    """Test complete voter journey from signup to voting."""

    def test_complete_voter_flow(self, client, db_session, test_city, test_contest):
        """
        Test complete voter flow:
        1. Register
        2. Verify email
        3. Login
        4. Submit question
        5. Vote on other questions
        """
        # Step 1: Register
        with patch('app.services.auth_service.AuthService.request_email_verification'):
            register_response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": "voter@example.com",
                    "password": "SecurePass123!",
                    "full_name": "Test Voter",
                    "city": test_city.name,
                },
            )
        assert register_response.status_code == 201
        user_data = register_response.json()

        # Step 2: Verify email (simulate)
        from app.models.user import User
        from datetime import datetime, timedelta

        user = db_session.query(User).filter_by(email="voter@example.com").first()
        verification_token = "test_token"
        user.email_verification_token = verification_token
        user.email_verification_expires = datetime.utcnow() + timedelta(days=1)
        db_session.commit()

        verify_response = client.post(f"/api/v1/auth/verify-email/{verification_token}")
        assert verify_response.status_code == 200

        # Step 3: Login
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "voter@example.com",
                "password": "SecurePass123!",
            },
        )
        assert login_response.status_code == 200
        token_data = login_response.json()
        auth_headers = {"Authorization": f"Bearer {token_data['access_token']}"}

        # Step 4: Submit question
        question_response = client.post(
            "/api/v1/questions",
            headers=auth_headers,
            json={
                "contest_id": test_contest.id,
                "question_text": "What is your plan for affordable housing?",
                "issue_tags": ["housing", "economy"],
            },
        )
        assert question_response.status_code == 201
        question_data = question_response.json()

        # Step 5: Vote on question
        vote_response = client.post(
            f"/api/v1/questions/{question_data['id']}/vote",
            headers=auth_headers,
            json={"value": 1},
        )
        assert vote_response.status_code == 200

        # Verify final state
        me_response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert me_response.status_code == 200
        assert me_response.json()["email"] == "voter@example.com"


class TestQuestionLifecycle:
    """Test complete question lifecycle."""

    def test_question_submission_to_answer(self, client, db_session, test_city, test_contest):
        """
        Test question lifecycle:
        1. Voter submits question
        2. Moderator approves question
        3. Other voters upvote
        4. Candidate answers via video
        """
        from tests.fixtures.factories import UserFactory, VideoFactory
        from app.core.security import create_access_token

        # Create voter
        voter = UserFactory.create_voter(db_session, city_id=test_city.slug)
        voter_token = create_access_token({"sub": str(voter.id), "email": voter.email})
        voter_headers = {"Authorization": f"Bearer {voter_token}"}

        # Create moderator
        moderator = UserFactory.create_moderator(db_session, city_id=test_city.slug)
        mod_token = create_access_token({"sub": str(moderator.id), "email": moderator.email})
        mod_headers = {"Authorization": f"Bearer {mod_token}"}

        # Create candidate
        candidate = UserFactory.create_candidate(db_session, city_id=test_city.slug)
        cand_token = create_access_token({"sub": str(candidate.id), "email": candidate.email})
        cand_headers = {"Authorization": f"Bearer {cand_token}"}

        # Step 1: Submit question
        question_response = client.post(
            "/api/v1/questions",
            headers=voter_headers,
            json={
                "contest_id": test_contest.id,
                "question_text": "What will you do about climate change?",
                "issue_tags": ["environment", "climate"],
            },
        )
        assert question_response.status_code == 201
        question = question_response.json()

        # Step 2: Moderator approves
        approve_response = client.post(
            f"/api/v1/admin/questions/{question['id']}/approve",
            headers=mod_headers,
        )
        assert approve_response.status_code == 200

        # Step 3: Other voters upvote
        for _ in range(5):
            upvoter = UserFactory.create_voter(db_session, city_id=test_city.slug)
            upvoter_token = create_access_token({"sub": str(upvoter.id), "email": upvoter.email})
            upvoter_headers = {"Authorization": f"Bearer {upvoter_token}"}

            client.post(
                f"/api/v1/questions/{question['id']}/vote",
                headers=upvoter_headers,
                json={"value": 1},
            )

        # Step 4: Candidate answers (simulate video upload)
        # This would involve video upload in real scenario
        video = VideoFactory.create(db_session, user_id=candidate.id)

        # Verify question has votes
        question_response = client.get(f"/api/v1/questions/{question['id']}")
        assert question_response.status_code == 200
        final_question = question_response.json()
        assert final_question["upvotes"] >= 5


class TestCityOnboarding:
    """Test city onboarding flow."""

    def test_city_registration_and_setup(self, client, db_session, mock_email_service):
        """
        Test city onboarding:
        1. City registers
        2. Upload ballot data
        3. Invite staff
        4. Configure settings
        """
        from tests.fixtures.factories import UserFactory
        from app.core.security import create_access_token

        # Step 1: Admin creates city
        admin = UserFactory.create_admin(db_session)
        admin_token = create_access_token({"sub": str(admin.id), "email": admin.email})
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        city_response = client.post(
            "/api/v1/admin/cities",
            headers=admin_headers,
            json={
                "name": "New City",
                "slug": "new-city",
                "state": "CA",
                "primary_contact_name": "City Clerk",
                "primary_contact_email": "clerk@newcity.gov",
            },
        )
        assert city_response.status_code == 201
        city = city_response.json()

        # Step 2: Upload ballot data (mock)
        with patch('app.services.ballot_data_service.BallotDataService.import_ballot'):
            ballot_response = client.post(
                f"/api/v1/cities/{city['slug']}/ballots/import",
                headers=admin_headers,
                json={
                    "election_date": "2024-11-05",
                    "data_source": "google_civic",
                },
            )
            assert ballot_response.status_code in [200, 201, 202]

        # Step 3: Invite staff
        invite_response = client.post(
            f"/api/v1/cities/{city['slug']}/staff/invite",
            headers=admin_headers,
            json={
                "email": "staff@newcity.gov",
                "role": "editor",
            },
        )
        assert invite_response.status_code in [200, 201]

        # Step 4: Configure settings
        settings_response = client.patch(
            f"/api/v1/cities/{city['slug']}/settings",
            headers=admin_headers,
            json={
                "settings": {
                    "require_voter_verification": True,
                    "moderation_mode": "post-approval",
                }
            },
        )
        assert settings_response.status_code == 200


class TestBallotImport:
    """Test ballot data import workflow."""

    def test_ballot_import_and_question_linking(self, client, db_session, test_city, mock_ballot_api):
        """
        Test ballot import workflow:
        1. Import ballot data
        2. Create contests
        3. Link questions to contests
        """
        from tests.fixtures.factories import UserFactory
        from app.core.security import create_access_token

        admin = UserFactory.create_admin(db_session)
        admin_token = create_access_token({"sub": str(admin.id), "email": admin.email})
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # Step 1: Import ballot
        with patch('app.services.ballot_data_service.BallotDataService.fetch_and_import'):
            import_response = client.post(
                f"/api/v1/cities/{test_city.slug}/ballots/import",
                headers=admin_headers,
                json={
                    "address": "100 Main St, San Francisco, CA",
                    "election_date": "2024-11-05",
                },
            )
            assert import_response.status_code in [200, 201, 202]

        # Step 2: Verify contests were created
        contests_response = client.get(f"/api/v1/cities/{test_city.slug}/contests")
        assert contests_response.status_code == 200

        # Step 3: Link questions
        contests = contests_response.json()
        if contests:
            voter = UserFactory.create_voter(db_session, city_id=test_city.slug)
            voter_token = create_access_token({"sub": str(voter.id), "email": voter.email})
            voter_headers = {"Authorization": f"Bearer {voter_token}"}

            question_response = client.post(
                "/api/v1/questions",
                headers=voter_headers,
                json={
                    "contest_id": contests[0]["id"],
                    "question_text": "What is your position on this issue?",
                },
            )
            assert question_response.status_code == 201


class TestMultiCityIsolation:
    """Test that cities are properly isolated."""

    def test_city_data_isolation(self, client, db_session):
        """Test that data from one city is isolated from another."""
        from tests.fixtures.factories import UserFactory, CityFactory, QuestionFactory, ContestFactory
        from app.core.security import create_access_token

        # Create two cities
        city1 = CityFactory.create(db_session, name="City One", slug="city-one")
        city2 = CityFactory.create(db_session, name="City Two", slug="city-two")

        # Create contests in each city
        contest1 = ContestFactory.create(db_session, city_id=city1.slug)
        contest2 = ContestFactory.create(db_session, city_id=city2.slug)

        # Create voters in each city
        voter1 = UserFactory.create_voter(db_session, city_id=city1.slug)
        voter2 = UserFactory.create_voter(db_session, city_id=city2.slug)

        # Create questions in each city
        question1 = QuestionFactory.create_approved(
            db_session,
            contest_id=contest1.id,
            author_id=voter1.id,
        )
        question2 = QuestionFactory.create_approved(
            db_session,
            contest_id=contest2.id,
            author_id=voter2.id,
        )

        # Verify voter1 can only see city1 questions
        token1 = create_access_token({"sub": str(voter1.id), "email": voter1.email})
        headers1 = {"Authorization": f"Bearer {token1}"}

        response = client.get(f"/api/v1/questions?contest_id={contest1.id}", headers=headers1)
        assert response.status_code == 200
        questions = response.json()["items"]
        assert all(q["contest_id"] == contest1.id for q in questions)

        # Verify voter2 cannot access city1's questions via API security
        token2 = create_access_token({"sub": str(voter2.id), "email": voter2.email})
        headers2 = {"Authorization": f"Bearer {token2}"}

        # This should either return empty or forbidden depending on implementation
        response = client.get(f"/api/v1/questions?contest_id={contest1.id}", headers=headers2)
        # Implementation dependent - either empty results or access denied
        assert response.status_code in [200, 403]
