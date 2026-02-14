#!/usr/bin/env python3
"""
Development Seed Data

Creates realistic development data for local testing.
Includes cities, users, ballots, questions, and votes.
"""

import os
import sys
import logging
import random
from datetime import datetime, timedelta, date
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from app.models.base import SessionLocal, engine, Base
from app.models.user import User, UserRole, VerificationStatus, VerificationRecord, VerificationMethod
from app.models.city import City, CityStatus, CityStaff, CityStaffRole
from app.models.ballot import Ballot, Contest, Candidate, Measure, ContestType, CandidateStatus
from app.models.question import Question, QuestionStatus, Vote
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DevDataSeeder:
    """Development data seeder"""

    def __init__(self, db: Session):
        self.db = db
        self.users = []
        self.cities = []
        self.ballots = []
        self.contests = []
        self.candidates = []
        self.questions = []

    def seed_all(self):
        """Seed all development data"""
        logger.info("Starting development data seeding...")

        self.seed_cities()
        self.seed_users()
        self.seed_city_staff()
        self.seed_ballots()
        self.seed_contests()
        self.seed_candidates()
        self.seed_questions()
        self.seed_votes()

        logger.info("Development data seeding completed!")

    def seed_cities(self):
        """Seed cities"""
        logger.info("Seeding cities...")

        cities_data = [
            {
                "name": "San Francisco",
                "slug": "san-francisco",
                "state": "CA",
                "county": "San Francisco",
                "population": 873965,
                "primary_contact_name": "Jane Smith",
                "primary_contact_email": "jane.smith@sfgov.org",
                "primary_contact_title": "City Clerk",
                "status": CityStatus.ACTIVE,
                "verified_at": datetime.utcnow(),
                "timezone": "America/Los_Angeles",
                "primary_color": "#004E8A",
                "secondary_color": "#FF6B35",
                "next_election_date": date(2026, 11, 3),
                "onboarding_completed": True,
            },
            {
                "name": "Oakland",
                "slug": "oakland",
                "state": "CA",
                "county": "Alameda",
                "population": 433031,
                "primary_contact_name": "John Davis",
                "primary_contact_email": "john.davis@oaklandca.gov",
                "primary_contact_title": "City Clerk",
                "status": CityStatus.ACTIVE,
                "verified_at": datetime.utcnow(),
                "timezone": "America/Los_Angeles",
                "primary_color": "#0066CC",
                "secondary_color": "#FFD700",
                "next_election_date": date(2026, 11, 3),
                "onboarding_completed": True,
            },
            {
                "name": "Berkeley",
                "slug": "berkeley",
                "state": "CA",
                "county": "Alameda",
                "population": 124321,
                "primary_contact_name": "Sarah Johnson",
                "primary_contact_email": "sjohnson@cityofberkeley.info",
                "primary_contact_title": "City Clerk",
                "status": CityStatus.ACTIVE,
                "verified_at": datetime.utcnow(),
                "timezone": "America/Los_Angeles",
                "primary_color": "#003262",
                "secondary_color": "#FDB515",
                "next_election_date": date(2026, 11, 3),
                "onboarding_completed": True,
            },
        ]

        for city_data in cities_data:
            city = City(**city_data)
            self.db.add(city)
            self.cities.append(city)

        self.db.commit()
        logger.info(f"Created {len(self.cities)} cities")

    def seed_users(self):
        """Seed users"""
        logger.info("Seeding users...")

        # Admin user
        admin = User(
            email="admin@civicq.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            role=UserRole.ADMIN,
            is_active=True,
            is_superuser=True,
            email_verified=True,
            verification_status=VerificationStatus.VERIFIED,
        )
        self.db.add(admin)
        self.users.append(admin)

        # City staff users
        for city in self.cities:
            staff_user = User(
                email=f"clerk@{city.slug}.gov",
                hashed_password=get_password_hash("password123"),
                full_name=city.primary_contact_name,
                role=UserRole.CITY_STAFF,
                is_active=True,
                email_verified=True,
                verification_status=VerificationStatus.VERIFIED,
                city_id=city.slug,
                city_name=city.name,
            )
            self.db.add(staff_user)
            self.users.append(staff_user)

        # Voters
        voter_names = [
            "Alice Johnson", "Bob Smith", "Carol Williams", "David Brown",
            "Emma Davis", "Frank Miller", "Grace Wilson", "Henry Moore",
            "Isabel Taylor", "Jack Anderson", "Kate Thomas", "Liam Jackson",
            "Mia White", "Noah Harris", "Olivia Martin", "Peter Thompson",
            "Quinn Garcia", "Ruby Martinez", "Sam Robinson", "Tara Clark",
        ]

        for i, name in enumerate(voter_names):
            city = random.choice(self.cities)
            voter = User(
                email=f"voter{i+1}@example.com",
                hashed_password=get_password_hash("password123"),
                full_name=name,
                role=UserRole.VOTER,
                is_active=True,
                email_verified=True,
                verification_status=VerificationStatus.VERIFIED,
                city_id=city.slug,
                city_name=city.name,
            )
            self.db.add(voter)
            self.users.append(voter)

        # Candidates
        candidate_names = [
            "Maria Rodriguez", "James Lee", "Sarah Chen", "Michael Johnson",
            "Jennifer Kim", "Robert Taylor", "Lisa Nguyen", "William Garcia",
        ]

        for i, name in enumerate(candidate_names):
            city = random.choice(self.cities)
            candidate = User(
                email=f"candidate{i+1}@example.com",
                hashed_password=get_password_hash("password123"),
                full_name=name,
                role=UserRole.CANDIDATE,
                is_active=True,
                email_verified=True,
                verification_status=VerificationStatus.VERIFIED,
                city_id=city.slug,
                city_name=city.name,
            )
            self.db.add(candidate)
            self.users.append(candidate)

        self.db.commit()
        logger.info(f"Created {len(self.users)} users")

    def seed_city_staff(self):
        """Link city staff to cities"""
        logger.info("Seeding city staff relationships...")

        for city in self.cities:
            # Find city staff user
            staff_user = next(
                (u for u in self.users if u.email == f"clerk@{city.slug}.gov"),
                None
            )

            if staff_user:
                city_staff = CityStaff(
                    city_id=city.id,
                    user_id=staff_user.id,
                    role=CityStaffRole.OWNER,
                    is_active=True,
                )
                self.db.add(city_staff)

        self.db.commit()
        logger.info("City staff relationships created")

    def seed_ballots(self):
        """Seed ballots"""
        logger.info("Seeding ballots...")

        for city in self.cities:
            ballot = Ballot(
                city_id=city.slug,
                city_name=city.name,
                election_date=date(2026, 11, 3),
                version=1,
                is_published=True,
            )
            self.db.add(ballot)
            self.ballots.append(ballot)

        self.db.commit()
        logger.info(f"Created {len(self.ballots)} ballots")

    def seed_contests(self):
        """Seed contests"""
        logger.info("Seeding contests...")

        contest_templates = [
            {"type": ContestType.RACE, "title": "Mayor", "office": "Mayor", "seat_count": 1},
            {"type": ContestType.RACE, "title": "City Council District 1", "office": "City Council", "seat_count": 1},
            {"type": ContestType.RACE, "title": "City Council District 2", "office": "City Council", "seat_count": 1},
            {"type": ContestType.RACE, "title": "City Council At-Large", "office": "City Council", "seat_count": 2},
            {"type": ContestType.MEASURE, "title": "Measure A: Parks Funding", "office": None, "seat_count": None},
            {"type": ContestType.MEASURE, "title": "Measure B: Housing Bond", "office": None, "seat_count": None},
        ]

        for ballot in self.ballots:
            for i, template in enumerate(contest_templates):
                contest = Contest(
                    ballot_id=ballot.id,
                    type=template["type"],
                    title=template["title"],
                    office=template["office"],
                    seat_count=template["seat_count"],
                    display_order=i,
                )
                self.db.add(contest)
                self.contests.append(contest)

        self.db.commit()
        logger.info(f"Created {len(self.contests)} contests")

    def seed_candidates(self):
        """Seed candidates"""
        logger.info("Seeding candidates...")

        # Get candidate users
        candidate_users = [u for u in self.users if u.role == UserRole.CANDIDATE]

        # Only seed for race contests
        race_contests = [c for c in self.contests if c.type == ContestType.RACE]

        candidate_idx = 0
        for contest in race_contests:
            # Add 2-4 candidates per race
            num_candidates = random.randint(2, 4)

            for i in range(num_candidates):
                if candidate_idx >= len(candidate_users):
                    candidate_idx = 0

                user = candidate_users[candidate_idx]
                candidate_idx += 1

                candidate = Candidate(
                    contest_id=contest.id,
                    user_id=user.id,
                    name=user.full_name,
                    email=user.email,
                    status=CandidateStatus.ACTIVE,
                    identity_verified=True,
                    identity_verified_at=date.today(),
                    display_order=i,
                )
                self.db.add(candidate)
                self.candidates.append(candidate)

        # Seed measures
        measure_contests = [c for c in self.contests if c.type == ContestType.MEASURE]
        for contest in measure_contests:
            measure = Measure(
                contest_id=contest.id,
                measure_number=contest.title.split(":")[0].replace("Measure ", ""),
                measure_text=f"This measure would {contest.title.split(':')[1].strip().lower()}.",
                summary=f"A comprehensive measure to address {contest.title.split(':')[1].strip().lower()}.",
                fiscal_notes="Estimated cost: $10-20 million annually.",
                pro_statement="This measure will benefit our community.",
                con_statement="This measure is too expensive.",
            )
            self.db.add(measure)

        self.db.commit()
        logger.info(f"Created {len(self.candidates)} candidates")

    def seed_questions(self):
        """Seed questions"""
        logger.info("Seeding questions...")

        question_templates = [
            "What is your plan to address affordable housing in our city?",
            "How will you improve public transportation?",
            "What are your priorities for public safety?",
            "How do you plan to support small businesses?",
            "What is your stance on climate change and sustainability?",
            "How will you address homelessness?",
            "What are your plans for education funding?",
            "How will you improve infrastructure?",
            "What is your approach to economic development?",
            "How will you ensure transparency in government?",
        ]

        issue_tags_options = [
            ["housing", "affordability"],
            ["transportation", "infrastructure"],
            ["public-safety", "police"],
            ["economy", "small-business"],
            ["environment", "climate"],
            ["homelessness", "social-services"],
            ["education", "schools"],
            ["infrastructure", "roads"],
            ["economy", "jobs"],
            ["transparency", "accountability"],
        ]

        # Get verified voters
        voters = [u for u in self.users if u.role == UserRole.VOTER and u.verification_status == VerificationStatus.VERIFIED]

        # Create questions for race contests
        race_contests = [c for c in self.contests if c.type == ContestType.RACE]

        for contest in race_contests:
            # 3-5 questions per contest
            num_questions = random.randint(3, 5)

            for i in range(num_questions):
                author = random.choice(voters)
                template_idx = random.randint(0, len(question_templates) - 1)

                question = Question(
                    contest_id=contest.id,
                    author_id=author.id,
                    question_text=question_templates[template_idx],
                    issue_tags=issue_tags_options[template_idx],
                    status=QuestionStatus.APPROVED,
                    upvotes=random.randint(5, 50),
                    downvotes=random.randint(0, 10),
                    rank_score=random.uniform(0.5, 1.0),
                )
                self.db.add(question)
                self.questions.append(question)

        self.db.commit()
        logger.info(f"Created {len(self.questions)} questions")

    def seed_votes(self):
        """Seed votes on questions"""
        logger.info("Seeding votes...")

        voters = [u for u in self.users if u.role == UserRole.VOTER]

        vote_count = 0
        for question in self.questions:
            # Random number of voters vote on each question
            num_voters = random.randint(3, len(voters) // 2)
            voting_users = random.sample(voters, num_voters)

            for user in voting_users:
                # 80% upvote, 20% downvote
                value = 1 if random.random() < 0.8 else -1

                vote = Vote(
                    user_id=user.id,
                    question_id=question.id,
                    value=value,
                    weight=1.0,
                )
                self.db.add(vote)
                vote_count += 1

        self.db.commit()
        logger.info(f"Created {vote_count} votes")


def main():
    """Main entry point"""
    logger.info("Initializing database...")

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    db = SessionLocal()

    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            response = input(f"Database already contains {existing_users} users. Clear and reseed? (yes/no): ")
            if response.lower() != "yes":
                logger.info("Seeding cancelled")
                return

            # Clear existing data
            logger.info("Clearing existing data...")
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)

        # Seed data
        seeder = DevDataSeeder(db)
        seeder.seed_all()

        logger.info("\nDevelopment data seeded successfully!")
        logger.info(f"  - Cities: {len(seeder.cities)}")
        logger.info(f"  - Users: {len(seeder.users)}")
        logger.info(f"  - Ballots: {len(seeder.ballots)}")
        logger.info(f"  - Contests: {len(seeder.contests)}")
        logger.info(f"  - Candidates: {len(seeder.candidates)}")
        logger.info(f"  - Questions: {len(seeder.questions)}")

        logger.info("\nTest Credentials:")
        logger.info("  Admin: admin@civicq.com / admin123")
        logger.info("  Voter: voter1@example.com / password123")
        logger.info("  Candidate: candidate1@example.com / password123")
        logger.info("  City Staff: clerk@san-francisco.gov / password123")

    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
