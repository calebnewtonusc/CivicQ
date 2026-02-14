"""
Comprehensive unit tests for all database models.
"""

import pytest
from datetime import datetime, date, timedelta
from sqlalchemy.exc import IntegrityError

from app.models.user import User, UserRole, VerificationStatus, VerificationRecord, VerificationMethod
from app.models.question import Question, QuestionStatus, QuestionVersion, Vote
from app.models.ballot import Ballot, Contest, ContestType, Candidate, CandidateStatus, Measure
from app.models.answer import VideoAnswer, AnswerStatus, Rebuttal
from app.models.follow import Follow
from app.models.moderation import Report, ReportType, ReportStatus
from app.models.city import City, CityStatus


class TestUserModel:
    """Test User model functionality."""

    def test_create_user(self, db_session):
        """Test creating a basic user."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
            full_name="Test User",
            role=UserRole.VOTER,
        )
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.role == UserRole.VOTER
        assert user.is_active is True
        assert user.email_verified is False
        assert user.verification_status == VerificationStatus.PENDING

    def test_user_unique_email(self, db_session):
        """Test that email must be unique."""
        user1 = User(email="test@example.com", hashed_password="hash1")
        db_session.add(user1)
        db_session.commit()

        user2 = User(email="test@example.com", hashed_password="hash2")
        db_session.add(user2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_roles(self, db_session):
        """Test different user roles."""
        roles = [UserRole.VOTER, UserRole.CANDIDATE, UserRole.ADMIN, UserRole.MODERATOR]

        for role in roles:
            user = User(
                email=f"{role.value}@example.com",
                hashed_password="hash",
                role=role,
            )
            db_session.add(user)

        db_session.commit()

        assert db_session.query(User).count() == len(roles)

    def test_user_verification_fields(self, db_session):
        """Test user verification fields."""
        user = User(
            email="verify@example.com",
            hashed_password="hash",
            email_verified=True,
            verification_status=VerificationStatus.VERIFIED,
            verification_token="token123",
        )
        db_session.add(user)
        db_session.commit()

        assert user.email_verified is True
        assert user.verification_status == VerificationStatus.VERIFIED
        assert user.verification_token == "token123"

    def test_user_two_factor(self, db_session):
        """Test two-factor authentication fields."""
        user = User(
            email="2fa@example.com",
            hashed_password="hash",
            two_factor_enabled=True,
            two_factor_secret="secret123",
            backup_codes=["code1", "code2", "code3"],
        )
        db_session.add(user)
        db_session.commit()

        assert user.two_factor_enabled is True
        assert user.two_factor_secret == "secret123"
        assert len(user.backup_codes) == 3

    def test_user_oauth(self, db_session):
        """Test OAuth fields."""
        user = User(
            email="oauth@example.com",
            hashed_password="hash",
            oauth_provider="google",
            oauth_id="google_user_123",
        )
        db_session.add(user)
        db_session.commit()

        assert user.oauth_provider == "google"
        assert user.oauth_id == "google_user_123"

    def test_user_city_scope(self, db_session):
        """Test city scoping fields."""
        user = User(
            email="city@example.com",
            hashed_password="hash",
            city_id="SF",
            city_name="San Francisco",
        )
        db_session.add(user)
        db_session.commit()

        assert user.city_id == "SF"
        assert user.city_name == "San Francisco"


class TestVerificationRecordModel:
    """Test VerificationRecord model functionality."""

    def test_create_verification_record(self, db_session):
        """Test creating a verification record."""
        user = User(email="verify@example.com", hashed_password="hash")
        db_session.add(user)
        db_session.commit()

        record = VerificationRecord(
            user_id=user.id,
            method=VerificationMethod.EMAIL,
            city_scope="SF",
            status=VerificationStatus.VERIFIED,
            verified_at=datetime.utcnow(),
        )
        db_session.add(record)
        db_session.commit()

        assert record.id is not None
        assert record.user_id == user.id
        assert record.method == VerificationMethod.EMAIL
        assert record.status == VerificationStatus.VERIFIED

    def test_verification_methods(self, db_session):
        """Test different verification methods."""
        user = User(email="user@example.com", hashed_password="hash")
        db_session.add(user)
        db_session.commit()

        methods = [
            VerificationMethod.SMS,
            VerificationMethod.EMAIL,
            VerificationMethod.VOTER_ROLL,
            VerificationMethod.ID_PROOFING,
        ]

        for method in methods:
            record = VerificationRecord(
                user_id=user.id,
                method=method,
                city_scope="TEST",
                status=VerificationStatus.PENDING,
            )
            db_session.add(record)

        db_session.commit()
        assert len(user.verification_records) == len(methods)

    def test_verification_cascade_delete(self, db_session):
        """Test that verification records are deleted when user is deleted."""
        user = User(email="delete@example.com", hashed_password="hash")
        db_session.add(user)
        db_session.commit()

        record = VerificationRecord(
            user_id=user.id,
            method=VerificationMethod.EMAIL,
            city_scope="TEST",
        )
        db_session.add(record)
        db_session.commit()

        record_id = record.id
        db_session.delete(user)
        db_session.commit()

        assert db_session.query(VerificationRecord).filter_by(id=record_id).first() is None


class TestQuestionModel:
    """Test Question model functionality."""

    def test_create_question(self, db_session):
        """Test creating a basic question."""
        # Create necessary prerequisites
        ballot = Ballot(city_id="SF", city_name="San Francisco", election_date=date(2024, 11, 5))
        db_session.add(ballot)
        db_session.commit()

        contest = Contest(ballot_id=ballot.id, type=ContestType.RACE, title="Mayor")
        db_session.add(contest)
        db_session.commit()

        user = User(email="author@example.com", hashed_password="hash")
        db_session.add(user)
        db_session.commit()

        question = Question(
            contest_id=contest.id,
            author_id=user.id,
            question_text="What is your plan for affordable housing?",
            issue_tags=["housing", "economy"],
            status=QuestionStatus.APPROVED,
        )
        db_session.add(question)
        db_session.commit()

        assert question.id is not None
        assert question.question_text == "What is your plan for affordable housing?"
        assert question.status == QuestionStatus.APPROVED
        assert "housing" in question.issue_tags

    def test_question_voting_counts(self, db_session):
        """Test question upvote/downvote counts."""
        ballot = Ballot(city_id="SF", city_name="San Francisco", election_date=date(2024, 11, 5))
        contest = Contest(ballot_id=ballot.id, type=ContestType.RACE, title="Mayor")
        question = Question(
            contest_id=contest.id,
            question_text="Test question?",
            upvotes=10,
            downvotes=2,
            rank_score=8.5,
        )
        db_session.add_all([ballot, contest, question])
        db_session.commit()

        assert question.upvotes == 10
        assert question.downvotes == 2
        assert question.rank_score == 8.5

    def test_question_clustering(self, db_session):
        """Test question clustering fields."""
        ballot = Ballot(city_id="SF", city_name="San Francisco", election_date=date(2024, 11, 5))
        contest = Contest(ballot_id=ballot.id, type=ContestType.RACE, title="Mayor")
        question = Question(
            contest_id=contest.id,
            question_text="Test question?",
            cluster_id=123,
        )
        db_session.add_all([ballot, contest, question])
        db_session.commit()

        assert question.cluster_id == 123

    def test_question_moderation(self, db_session):
        """Test question moderation fields."""
        ballot = Ballot(city_id="SF", city_name="San Francisco", election_date=date(2024, 11, 5))
        contest = Contest(ballot_id=ballot.id, type=ContestType.RACE, title="Mayor")
        question = Question(
            contest_id=contest.id,
            question_text="Test question?",
            is_flagged=3,
            moderation_notes="Reviewed and approved",
        )
        db_session.add_all([ballot, contest, question])
        db_session.commit()

        assert question.is_flagged == 3
        assert question.moderation_notes == "Reviewed and approved"


class TestVoteModel:
    """Test Vote model functionality."""

    def test_create_vote(self, db_session):
        """Test creating a vote."""
        # Setup
        ballot = Ballot(city_id="SF", city_name="San Francisco", election_date=date(2024, 11, 5))
        contest = Contest(ballot_id=ballot.id, type=ContestType.RACE, title="Mayor")
        question = Question(contest_id=contest.id, question_text="Test?")
        user = User(email="voter@example.com", hashed_password="hash")
        db_session.add_all([ballot, contest, question, user])
        db_session.commit()

        vote = Vote(
            user_id=user.id,
            question_id=question.id,
            value=1,
            weight=1.0,
        )
        db_session.add(vote)
        db_session.commit()

        assert vote.id is not None
        assert vote.value == 1
        assert vote.weight == 1.0

    def test_vote_unique_constraint(self, db_session):
        """Test that a user can only vote once per question."""
        ballot = Ballot(city_id="SF", city_name="San Francisco", election_date=date(2024, 11, 5))
        contest = Contest(ballot_id=ballot.id, type=ContestType.RACE, title="Mayor")
        question = Question(contest_id=contest.id, question_text="Test?")
        user = User(email="voter@example.com", hashed_password="hash")
        db_session.add_all([ballot, contest, question, user])
        db_session.commit()

        vote1 = Vote(user_id=user.id, question_id=question.id, value=1)
        db_session.add(vote1)
        db_session.commit()

        vote2 = Vote(user_id=user.id, question_id=question.id, value=-1)
        db_session.add(vote2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_vote_anomaly_detection(self, db_session):
        """Test vote anomaly detection fields."""
        ballot = Ballot(city_id="SF", city_name="San Francisco", election_date=date(2024, 11, 5))
        contest = Contest(ballot_id=ballot.id, type=ContestType.RACE, title="Mayor")
        question = Question(contest_id=contest.id, question_text="Test?")
        user = User(email="voter@example.com", hashed_password="hash")
        db_session.add_all([ballot, contest, question, user])
        db_session.commit()

        vote = Vote(
            user_id=user.id,
            question_id=question.id,
            value=1,
            device_risk_score=0.3,
            weight=0.7,
            metadata={"ip_hash": "abc123"},
        )
        db_session.add(vote)
        db_session.commit()

        assert vote.device_risk_score == 0.3
        assert vote.weight == 0.7
        assert vote.metadata["ip_hash"] == "abc123"


class TestBallotModel:
    """Test Ballot model functionality."""

    def test_create_ballot(self, db_session):
        """Test creating a ballot."""
        ballot = Ballot(
            city_id="SF",
            city_name="San Francisco",
            election_date=date(2024, 11, 5),
            version=1,
            is_published=True,
        )
        db_session.add(ballot)
        db_session.commit()

        assert ballot.id is not None
        assert ballot.city_id == "SF"
        assert ballot.election_date == date(2024, 11, 5)
        assert ballot.is_published is True

    def test_ballot_source_metadata(self, db_session):
        """Test ballot source metadata."""
        ballot = Ballot(
            city_id="LA",
            city_name="Los Angeles",
            election_date=date(2024, 11, 5),
            source_metadata={
                "provider": "BallotReady",
                "imported_at": "2024-01-15T10:00:00Z",
            },
        )
        db_session.add(ballot)
        db_session.commit()

        assert ballot.source_metadata["provider"] == "BallotReady"


class TestContestModel:
    """Test Contest model functionality."""

    def test_create_race_contest(self, db_session):
        """Test creating a race contest."""
        ballot = Ballot(city_id="SF", city_name="San Francisco", election_date=date(2024, 11, 5))
        db_session.add(ballot)
        db_session.commit()

        contest = Contest(
            ballot_id=ballot.id,
            type=ContestType.RACE,
            title="Mayor",
            jurisdiction="City of San Francisco",
            office="Mayor",
            seat_count=1,
        )
        db_session.add(contest)
        db_session.commit()

        assert contest.id is not None
        assert contest.type == ContestType.RACE
        assert contest.office == "Mayor"

    def test_create_measure_contest(self, db_session):
        """Test creating a measure contest."""
        ballot = Ballot(city_id="SF", city_name="San Francisco", election_date=date(2024, 11, 5))
        db_session.add(ballot)
        db_session.commit()

        contest = Contest(
            ballot_id=ballot.id,
            type=ContestType.MEASURE,
            title="Proposition A",
            description="Housing bond measure",
        )
        db_session.add(contest)
        db_session.commit()

        assert contest.type == ContestType.MEASURE
        assert contest.title == "Proposition A"

    def test_contest_cascade_delete(self, db_session):
        """Test that contests are deleted when ballot is deleted."""
        ballot = Ballot(city_id="SF", city_name="San Francisco", election_date=date(2024, 11, 5))
        contest = Contest(ballot_id=ballot.id, type=ContestType.RACE, title="Mayor")
        db_session.add_all([ballot, contest])
        db_session.commit()

        contest_id = contest.id
        db_session.delete(ballot)
        db_session.commit()

        assert db_session.query(Contest).filter_by(id=contest_id).first() is None


class TestCandidateModel:
    """Test Candidate model functionality."""

    def test_create_candidate(self, db_session):
        """Test creating a candidate."""
        ballot = Ballot(city_id="SF", city_name="San Francisco", election_date=date(2024, 11, 5))
        contest = Contest(ballot_id=ballot.id, type=ContestType.RACE, title="Mayor")
        db_session.add_all([ballot, contest])
        db_session.commit()

        candidate = Candidate(
            contest_id=contest.id,
            name="Jane Doe",
            filing_id="CAND-2024-001",
            email="jane@example.com",
            status=CandidateStatus.VERIFIED,
        )
        db_session.add(candidate)
        db_session.commit()

        assert candidate.id is not None
        assert candidate.name == "Jane Doe"
        assert candidate.status == CandidateStatus.VERIFIED

    def test_candidate_profile(self, db_session):
        """Test candidate profile fields."""
        ballot = Ballot(city_id="SF", city_name="San Francisco", election_date=date(2024, 11, 5))
        contest = Contest(ballot_id=ballot.id, type=ContestType.RACE, title="Mayor")
        db_session.add_all([ballot, contest])
        db_session.commit()

        candidate = Candidate(
            contest_id=contest.id,
            name="John Smith",
            profile_fields={
                "party": "Independent",
                "occupation": "City Council Member",
                "education": "Stanford University",
            },
            photo_url="https://example.com/photo.jpg",
            website="https://johnformayor.com",
        )
        db_session.add(candidate)
        db_session.commit()

        assert candidate.profile_fields["party"] == "Independent"
        assert candidate.photo_url is not None
        assert candidate.website is not None

    def test_candidate_identity_verification(self, db_session):
        """Test candidate identity verification."""
        ballot = Ballot(city_id="SF", city_name="San Francisco", election_date=date(2024, 11, 5))
        contest = Contest(ballot_id=ballot.id, type=ContestType.RACE, title="Mayor")
        db_session.add_all([ballot, contest])
        db_session.commit()

        candidate = Candidate(
            contest_id=contest.id,
            name="Verified Candidate",
            identity_verified=True,
            identity_verified_at=date.today(),
        )
        db_session.add(candidate)
        db_session.commit()

        assert candidate.identity_verified is True
        assert candidate.identity_verified_at == date.today()


class TestMeasureModel:
    """Test Measure model functionality."""

    def test_create_measure(self, db_session):
        """Test creating a measure."""
        ballot = Ballot(city_id="SF", city_name="San Francisco", election_date=date(2024, 11, 5))
        contest = Contest(ballot_id=ballot.id, type=ContestType.MEASURE, title="Prop A")
        db_session.add_all([ballot, contest])
        db_session.commit()

        measure = Measure(
            contest_id=contest.id,
            measure_number="Prop A",
            measure_text="Shall the city issue bonds for housing?",
            summary="Housing bond measure",
            fiscal_notes="Estimated cost: $500M",
        )
        db_session.add(measure)
        db_session.commit()

        assert measure.id is not None
        assert measure.measure_number == "Prop A"
        assert measure.fiscal_notes == "Estimated cost: $500M"

    def test_measure_pro_con(self, db_session):
        """Test measure pro/con statements."""
        ballot = Ballot(city_id="SF", city_name="San Francisco", election_date=date(2024, 11, 5))
        contest = Contest(ballot_id=ballot.id, type=ContestType.MEASURE, title="Prop A")
        db_session.add_all([ballot, contest])
        db_session.commit()

        measure = Measure(
            contest_id=contest.id,
            measure_number="Prop A",
            measure_text="Bond measure",
            pro_statement="This will help housing",
            con_statement="This will increase taxes",
            pro_contacts={"name": "Housing Alliance", "email": "info@housing.org"},
            con_contacts={"name": "Taxpayers Union", "email": "info@taxpayers.org"},
        )
        db_session.add(measure)
        db_session.commit()

        assert measure.pro_statement is not None
        assert measure.con_statement is not None
        assert measure.pro_contacts["name"] == "Housing Alliance"


class TestRelationships:
    """Test model relationships."""

    def test_user_questions_relationship(self, db_session):
        """Test user to questions relationship."""
        ballot = Ballot(city_id="SF", city_name="San Francisco", election_date=date(2024, 11, 5))
        contest = Contest(ballot_id=ballot.id, type=ContestType.RACE, title="Mayor")
        user = User(email="author@example.com", hashed_password="hash")
        db_session.add_all([ballot, contest, user])
        db_session.commit()

        q1 = Question(contest_id=contest.id, author_id=user.id, question_text="Question 1")
        q2 = Question(contest_id=contest.id, author_id=user.id, question_text="Question 2")
        db_session.add_all([q1, q2])
        db_session.commit()

        assert len(user.questions) == 2

    def test_ballot_contests_relationship(self, db_session):
        """Test ballot to contests relationship."""
        ballot = Ballot(city_id="SF", city_name="San Francisco", election_date=date(2024, 11, 5))
        db_session.add(ballot)
        db_session.commit()

        c1 = Contest(ballot_id=ballot.id, type=ContestType.RACE, title="Mayor")
        c2 = Contest(ballot_id=ballot.id, type=ContestType.MEASURE, title="Prop A")
        db_session.add_all([c1, c2])
        db_session.commit()

        assert len(ballot.contests) == 2

    def test_contest_questions_relationship(self, db_session):
        """Test contest to questions relationship."""
        ballot = Ballot(city_id="SF", city_name="San Francisco", election_date=date(2024, 11, 5))
        contest = Contest(ballot_id=ballot.id, type=ContestType.RACE, title="Mayor")
        db_session.add_all([ballot, contest])
        db_session.commit()

        q1 = Question(contest_id=contest.id, question_text="Question 1")
        q2 = Question(contest_id=contest.id, question_text="Question 2")
        q3 = Question(contest_id=contest.id, question_text="Question 3")
        db_session.add_all([q1, q2, q3])
        db_session.commit()

        assert len(contest.questions) == 3
