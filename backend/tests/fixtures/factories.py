"""
Test data factories for creating model instances.
"""

from datetime import datetime, timedelta, date
from typing import Optional
import secrets

from app.models.user import User, UserRole, VerificationRecord, VerificationStatus, VerificationMethod
from app.models.city import City, CityStaff, CityInvitation, CityStatus, CityStaffRole
from app.models.question import Question, QuestionVersion, Vote, QuestionStatus
from app.models.ballot import Contest, Candidate
from app.models.video import Video, VideoAnswer, VideoStatus


class UserFactory:
    """Factory for creating test users."""

    @staticmethod
    def create(
        db_session,
        email: Optional[str] = None,
        role: UserRole = UserRole.VOTER,
        city_id: Optional[str] = None,
        email_verified: bool = False,
        **kwargs
    ) -> User:
        """Create a test user."""
        if email is None:
            email = f"user{secrets.token_hex(4)}@example.com"

        user = User(
            email=email,
            hashed_password="$2b$12$hashed_password_here",
            role=role,
            city_id=city_id,
            email_verified=email_verified,
            **kwargs
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @staticmethod
    def create_voter(db_session, city_id: str = "test-city", **kwargs) -> User:
        """Create a verified voter."""
        return UserFactory.create(
            db_session,
            role=UserRole.VOTER,
            city_id=city_id,
            email_verified=True,
            verification_status=VerificationStatus.VERIFIED,
            **kwargs
        )

    @staticmethod
    def create_candidate(db_session, city_id: str = "test-city", **kwargs) -> User:
        """Create a verified candidate."""
        return UserFactory.create(
            db_session,
            role=UserRole.CANDIDATE,
            city_id=city_id,
            email_verified=True,
            verification_status=VerificationStatus.VERIFIED,
            **kwargs
        )

    @staticmethod
    def create_admin(db_session, **kwargs) -> User:
        """Create an admin user."""
        return UserFactory.create(
            db_session,
            role=UserRole.ADMIN,
            is_superuser=True,
            email_verified=True,
            **kwargs
        )

    @staticmethod
    def create_moderator(db_session, city_id: str = "test-city", **kwargs) -> User:
        """Create a moderator."""
        return UserFactory.create(
            db_session,
            role=UserRole.MODERATOR,
            city_id=city_id,
            email_verified=True,
            **kwargs
        )


class CityFactory:
    """Factory for creating test cities."""

    @staticmethod
    def create(
        db_session,
        name: Optional[str] = None,
        slug: Optional[str] = None,
        state: str = "CA",
        status: CityStatus = CityStatus.ACTIVE,
        **kwargs
    ) -> City:
        """Create a test city."""
        if name is None:
            rand = secrets.token_hex(4)
            name = f"Test City {rand}"
            slug = f"test-city-{rand}"
        elif slug is None:
            slug = name.lower().replace(" ", "-")

        city = City(
            name=name,
            slug=slug,
            state=state,
            status=status,
            primary_contact_name="City Clerk",
            primary_contact_email=f"clerk@{slug}.gov",
            **kwargs
        )
        db_session.add(city)
        db_session.commit()
        db_session.refresh(city)
        return city

    @staticmethod
    def create_with_staff(db_session, **kwargs) -> tuple[City, User]:
        """Create a city with an owner."""
        city = CityFactory.create(db_session, **kwargs)
        owner = UserFactory.create(
            db_session,
            role=UserRole.CITY_STAFF,
            city_id=city.slug,
        )

        staff = CityStaff(
            city_id=city.id,
            user_id=owner.id,
            role=CityStaffRole.OWNER,
        )
        db_session.add(staff)
        db_session.commit()

        return city, owner


class QuestionFactory:
    """Factory for creating test questions."""

    @staticmethod
    def create(
        db_session,
        contest_id: int,
        author_id: int,
        question_text: Optional[str] = None,
        status: QuestionStatus = QuestionStatus.PENDING,
        **kwargs
    ) -> Question:
        """Create a test question."""
        if question_text is None:
            question_text = f"Test question {secrets.token_hex(4)}?"

        question = Question(
            contest_id=contest_id,
            author_id=author_id,
            question_text=question_text,
            status=status,
            **kwargs
        )
        db_session.add(question)
        db_session.commit()
        db_session.refresh(question)
        return question

    @staticmethod
    def create_approved(db_session, contest_id: int, author_id: int, **kwargs) -> Question:
        """Create an approved question."""
        return QuestionFactory.create(
            db_session,
            contest_id=contest_id,
            author_id=author_id,
            status=QuestionStatus.APPROVED,
            **kwargs
        )


class ContestFactory:
    """Factory for creating test contests."""

    @staticmethod
    def create(
        db_session,
        city_id: str = "test-city",
        title: Optional[str] = None,
        contest_type: str = "race",
        **kwargs
    ) -> Contest:
        """Create a test contest."""
        if title is None:
            title = f"Test Contest {secrets.token_hex(4)}"

        contest = Contest(
            city_id=city_id,
            title=title,
            contest_type=contest_type,
            **kwargs
        )
        db_session.add(contest)
        db_session.commit()
        db_session.refresh(contest)
        return contest


class CandidateFactory:
    """Factory for creating test candidates."""

    @staticmethod
    def create(
        db_session,
        contest_id: int,
        name: Optional[str] = None,
        **kwargs
    ) -> Candidate:
        """Create a test candidate."""
        if name is None:
            name = f"Test Candidate {secrets.token_hex(4)}"

        candidate = Candidate(
            contest_id=contest_id,
            name=name,
            **kwargs
        )
        db_session.add(candidate)
        db_session.commit()
        db_session.refresh(candidate)
        return candidate


class VoteFactory:
    """Factory for creating test votes."""

    @staticmethod
    def create(
        db_session,
        user_id: int,
        question_id: int,
        value: int = 1,
        **kwargs
    ) -> Vote:
        """Create a test vote."""
        vote = Vote(
            user_id=user_id,
            question_id=question_id,
            value=value,
            **kwargs
        )
        db_session.add(vote)
        db_session.commit()
        db_session.refresh(vote)
        return vote


class VideoFactory:
    """Factory for creating test videos."""

    @staticmethod
    def create(
        db_session,
        user_id: int,
        title: Optional[str] = None,
        status: VideoStatus = VideoStatus.PROCESSING,
        **kwargs
    ) -> Video:
        """Create a test video."""
        if title is None:
            title = f"Test Video {secrets.token_hex(4)}"

        video = Video(
            user_id=user_id,
            title=title,
            status=status,
            original_filename=f"{title}.mp4",
            storage_path=f"/videos/{secrets.token_hex(16)}.mp4",
            **kwargs
        )
        db_session.add(video)
        db_session.commit()
        db_session.refresh(video)
        return video


class VideoAnswerFactory:
    """Factory for creating test video answers."""

    @staticmethod
    def create(
        db_session,
        question_id: int,
        candidate_id: int,
        video_id: int,
        **kwargs
    ) -> VideoAnswer:
        """Create a test video answer."""
        answer = VideoAnswer(
            question_id=question_id,
            candidate_id=candidate_id,
            video_id=video_id,
            **kwargs
        )
        db_session.add(answer)
        db_session.commit()
        db_session.refresh(answer)
        return answer


class VerificationRecordFactory:
    """Factory for creating test verification records."""

    @staticmethod
    def create(
        db_session,
        user_id: int,
        method: VerificationMethod = VerificationMethod.EMAIL,
        city_scope: str = "test-city",
        status: VerificationStatus = VerificationStatus.VERIFIED,
        **kwargs
    ) -> VerificationRecord:
        """Create a test verification record."""
        record = VerificationRecord(
            user_id=user_id,
            method=method,
            city_scope=city_scope,
            status=status,
            verified_at=datetime.utcnow() if status == VerificationStatus.VERIFIED else None,
            **kwargs
        )
        db_session.add(record)
        db_session.commit()
        db_session.refresh(record)
        return record


class ScenarioBuilder:
    """Build complex test scenarios with multiple related objects."""

    @staticmethod
    def build_city_with_election(db_session) -> dict:
        """
        Build a complete city with contests, candidates, and questions.

        Returns dict with:
        - city
        - contests (list)
        - candidates (list)
        - voters (list)
        - questions (list)
        """
        # Create city
        city = CityFactory.create(db_session, name="Test City")

        # Create contests
        mayor_contest = ContestFactory.create(
            db_session,
            city_id=city.slug,
            title="Mayor",
            contest_type="race"
        )
        council_contest = ContestFactory.create(
            db_session,
            city_id=city.slug,
            title="City Council",
            contest_type="race"
        )

        # Create candidates
        candidates = [
            CandidateFactory.create(db_session, contest_id=mayor_contest.id, name="Jane Smith"),
            CandidateFactory.create(db_session, contest_id=mayor_contest.id, name="John Doe"),
            CandidateFactory.create(db_session, contest_id=council_contest.id, name="Alice Johnson"),
        ]

        # Create voters
        voters = [
            UserFactory.create_voter(db_session, city_id=city.slug)
            for _ in range(5)
        ]

        # Create questions
        questions = [
            QuestionFactory.create_approved(
                db_session,
                contest_id=mayor_contest.id,
                author_id=voters[0].id,
                question_text="What is your plan for affordable housing?",
                issue_tags=["housing", "economy"]
            ),
            QuestionFactory.create_approved(
                db_session,
                contest_id=mayor_contest.id,
                author_id=voters[1].id,
                question_text="How will you address climate change?",
                issue_tags=["environment", "climate"]
            ),
        ]

        return {
            "city": city,
            "contests": [mayor_contest, council_contest],
            "candidates": candidates,
            "voters": voters,
            "questions": questions,
        }

    @staticmethod
    def build_question_with_votes(db_session, num_upvotes: int = 10, num_downvotes: int = 2) -> dict:
        """
        Build a question with votes.

        Returns dict with:
        - question
        - voters (list)
        - votes (list)
        """
        # Setup
        city = CityFactory.create(db_session)
        contest = ContestFactory.create(db_session, city_id=city.slug)
        author = UserFactory.create_voter(db_session, city_id=city.slug)

        # Create question
        question = QuestionFactory.create_approved(
            db_session,
            contest_id=contest.id,
            author_id=author.id
        )

        # Create voters and votes
        voters = []
        votes = []

        # Upvotes
        for _ in range(num_upvotes):
            voter = UserFactory.create_voter(db_session, city_id=city.slug)
            vote = VoteFactory.create(db_session, user_id=voter.id, question_id=question.id, value=1)
            voters.append(voter)
            votes.append(vote)

        # Downvotes
        for _ in range(num_downvotes):
            voter = UserFactory.create_voter(db_session, city_id=city.slug)
            vote = VoteFactory.create(db_session, user_id=voter.id, question_id=question.id, value=-1)
            voters.append(voter)
            votes.append(vote)

        # Update question counts
        question.upvotes = num_upvotes
        question.downvotes = num_downvotes
        db_session.commit()

        return {
            "question": question,
            "voters": voters,
            "votes": votes,
        }
