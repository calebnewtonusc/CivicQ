#!/usr/bin/env python3
"""
Create a demo politician/candidate account for CivicQ

This script creates:
1. A demo user account with candidate role
2. A demo ballot and contest
3. A candidate profile linked to the user
4. Some sample questions for the candidate to answer
"""

import sys
import os
from datetime import date, datetime, timedelta

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.models.base import SessionLocal, engine, Base
from app.models.user import User, UserRole, VerificationStatus
from app.models.ballot import Ballot, Contest, Candidate, CandidateStatus, ContestType
from app.models.question import Question, QuestionStatus
from app.core.security import get_password_hash


def create_demo_data(db: Session):
    """Create demo candidate account and related data"""

    print("\n🚀 Creating CivicQ Demo Candidate Account...\n")

    # 1. Create demo user account
    print("1️⃣  Creating user account...")

    # Check if demo user already exists
    existing_user = db.query(User).filter(User.email == "demo.candidate@civicq.com").first()
    if existing_user:
        print("   ⚠️  Demo user already exists. Deleting old account...")
        db.delete(existing_user)
        db.commit()

    demo_user = User(
        email="demo.candidate@civicq.com",
        hashed_password=get_password_hash("DemoCandidate2024!"),
        full_name="Sarah Johnson",
        phone_number="(555) 123-4567",
        role=UserRole.CANDIDATE,
        is_active=True,
        is_superuser=False,
        city_id="santa-monica-ca",
        city_name="Santa Monica",
        verification_status=VerificationStatus.VERIFIED,
        last_active=datetime.utcnow()
    )
    db.add(demo_user)
    db.commit()
    db.refresh(demo_user)
    print(f"   ✅ User created: {demo_user.email}")
    print(f"   🔑 Password: DemoCandidate2024!")

    # 2. Create demo ballot
    print("\n2️⃣  Creating demo ballot...")

    existing_ballot = db.query(Ballot).filter(
        Ballot.city_id == "santa-monica-ca",
        Ballot.election_date == date(2024, 11, 5)
    ).first()

    if existing_ballot:
        demo_ballot = existing_ballot
        print(f"   ℹ️  Using existing ballot: {demo_ballot.city_name}")
    else:
        demo_ballot = Ballot(
            city_id="santa-monica-ca",
            city_name="Santa Monica",
            election_date=date(2024, 11, 5),
            version=1,
            is_published=True,
            source_metadata={
                "source": "demo_data",
                "created_by": "create_demo_candidate.py"
            }
        )
        db.add(demo_ballot)
        db.commit()
        db.refresh(demo_ballot)
        print(f"   ✅ Ballot created: {demo_ballot.city_name} - {demo_ballot.election_date}")

    # 3. Create demo contest
    print("\n3️⃣  Creating demo contest...")

    existing_contest = db.query(Contest).filter(
        Contest.ballot_id == demo_ballot.id,
        Contest.title == "City Council - District 3"
    ).first()

    if existing_contest:
        demo_contest = existing_contest
        print(f"   ℹ️  Using existing contest: {demo_contest.title}")
    else:
        demo_contest = Contest(
            ballot_id=demo_ballot.id,
            type=ContestType.RACE,
            title="City Council - District 3",
            jurisdiction="Santa Monica",
            office="City Council",
            seat_count=1,
            description="City Council represents residents in city governance, " +
                       "including budget decisions, housing policy, and local services.",
            display_order=1
        )
        db.add(demo_contest)
        db.commit()
        db.refresh(demo_contest)
        print(f"   ✅ Contest created: {demo_contest.title}")

    # 4. Create candidate profile
    print("\n4️⃣  Creating candidate profile...")

    existing_candidate = db.query(Candidate).filter(
        Candidate.user_id == demo_user.id
    ).first()

    if existing_candidate:
        print("   ⚠️  Candidate profile already exists. Updating...")
        demo_candidate = existing_candidate
    else:
        demo_candidate = Candidate(
            contest_id=demo_contest.id,
            user_id=demo_user.id,
            name="Sarah Johnson",
            filing_id="CC-D3-2024-001",
            email="demo.candidate@civicq.com",
            phone="(555) 123-4567",
            status=CandidateStatus.ACTIVE,
            identity_verified=True,
            identity_verified_at=date.today(),
            website="https://sarahjohnson.com",
            photo_url="https://randomuser.me/api/portraits/women/44.jpg",
            display_order=1
        )
        db.add(demo_candidate)
        db.commit()
        db.refresh(demo_candidate)

    # Update profile fields
    demo_candidate.profile_fields = {
        "bio": "Small business owner and community advocate with 15 years in Santa Monica. "
              "Committed to affordable housing, sustainable development, and transparent governance.",
        "education": "MBA from UCLA Anderson School of Management\nBA in Political Science from UC Berkeley",
        "experience": "• Owner, Local Coffee House (2010-present)\n"
                     "• Chair, Santa Monica Planning Commission (2020-2023)\n"
                     "• Member, Affordable Housing Task Force (2019-2022)",
        "priorities": "1. Increase affordable housing supply\n"
                     "2. Support local small businesses\n"
                     "3. Improve public transit and bike infrastructure\n"
                     "4. Enhance public safety through community programs\n"
                     "5. Promote environmental sustainability",
        "endorsements": "• Santa Monica Democratic Club\n"
                       "• Sierra Club - Santa Monica Bay Chapter\n"
                       "• Local Business Alliance\n"
                       "• Housing Rights Coalition"
    }
    db.commit()
    db.refresh(demo_candidate)
    print(f"   ✅ Candidate profile created: {demo_candidate.name}")

    # 5. Create sample questions
    print("\n5️⃣  Creating sample questions...")

    sample_questions = [
        {
            "text": "What is your plan to address the housing affordability crisis in Santa Monica?",
            "tags": ["housing", "affordability", "development"],
            "context": "Median rent in Santa Monica has increased 45% over the past 5 years.",
            "upvotes": 127,
            "rank_score": 8.5
        },
        {
            "text": "How will you support local small businesses while promoting sustainable development?",
            "tags": ["economy", "small business", "sustainability"],
            "context": "Many small businesses struggle with high commercial rents and competition from chains.",
            "upvotes": 89,
            "rank_score": 7.2
        },
        {
            "text": "What are your priorities for improving public transportation in our city?",
            "tags": ["transportation", "public transit", "infrastructure"],
            "context": "Many residents rely on the Big Blue Bus for daily commuting.",
            "upvotes": 76,
            "rank_score": 6.8
        },
        {
            "text": "How do you plan to address homelessness in Santa Monica?",
            "tags": ["homelessness", "social services", "housing"],
            "context": "The homeless population has increased significantly in recent years.",
            "upvotes": 143,
            "rank_score": 9.1
        },
        {
            "text": "What is your stance on new development projects near the beach?",
            "tags": ["development", "environment", "beaches"],
            "context": "Several major development projects have been proposed for the coastal area.",
            "upvotes": 92,
            "rank_score": 7.5
        },
        {
            "text": "How will you ensure transparency and accountability in city government?",
            "tags": ["governance", "transparency", "accountability"],
            "context": "Voters want more access to city council decisions and budget information.",
            "upvotes": 68,
            "rank_score": 6.4
        },
        {
            "text": "What is your plan for improving public safety while maintaining community trust?",
            "tags": ["public safety", "police", "community"],
            "context": "Finding the right balance between safety and community-oriented policing.",
            "upvotes": 105,
            "rank_score": 8.0
        }
    ]

    created_questions = []
    for q_data in sample_questions:
        # Check if question already exists
        existing_q = db.query(Question).filter(
            Question.contest_id == demo_contest.id,
            Question.question_text == q_data["text"]
        ).first()

        if not existing_q:
            question = Question(
                contest_id=demo_contest.id,
                author_id=None,  # Anonymous voter question
                question_text=q_data["text"],
                issue_tags=q_data["tags"],
                context=q_data.get("context"),
                status=QuestionStatus.APPROVED,
                upvotes=q_data["upvotes"],
                downvotes=5,
                rank_score=q_data["rank_score"],
                is_flagged=False
            )
            db.add(question)
            created_questions.append(question)

    if created_questions:
        db.commit()
        print(f"   ✅ Created {len(created_questions)} sample questions")
    else:
        print(f"   ℹ️  Sample questions already exist")

    # 6. Create additional demo candidates for comparison
    print("\n6️⃣  Creating additional candidates for the contest...")

    other_candidates = [
        {
            "name": "Michael Chen",
            "filing_id": "CC-D3-2024-002",
            "status": CandidateStatus.ACTIVE,
            "photo_url": "https://randomuser.me/api/portraits/men/32.jpg",
            "website": "https://michaelchen.com"
        },
        {
            "name": "Patricia Rodriguez",
            "filing_id": "CC-D3-2024-003",
            "status": CandidateStatus.ACTIVE,
            "photo_url": "https://randomuser.me/api/portraits/women/65.jpg",
            "website": "https://patriciarodriguez.com"
        }
    ]

    for idx, cand_data in enumerate(other_candidates, start=2):
        existing = db.query(Candidate).filter(
            Candidate.contest_id == demo_contest.id,
            Candidate.filing_id == cand_data["filing_id"]
        ).first()

        if not existing:
            candidate = Candidate(
                contest_id=demo_contest.id,
                user_id=None,
                name=cand_data["name"],
                filing_id=cand_data["filing_id"],
                status=cand_data["status"],
                photo_url=cand_data["photo_url"],
                website=cand_data["website"],
                identity_verified=True,
                identity_verified_at=date.today(),
                display_order=idx + 1
            )
            db.add(candidate)

    db.commit()
    print(f"   ✅ Created {len(other_candidates)} additional candidates")

    # Summary
    print("\n" + "="*60)
    print("✨ DEMO ACCOUNT CREATED SUCCESSFULLY! ✨")
    print("="*60)
    print(f"\n📧 Email:    demo.candidate@civicq.com")
    print(f"🔑 Password: DemoCandidate2024!")
    print(f"\n👤 Candidate: {demo_candidate.name}")
    print(f"🏛️  Contest:   {demo_contest.title}")
    print(f"📍 City:      {demo_ballot.city_name}")
    print(f"📅 Election:  {demo_ballot.election_date}")
    print(f"\n❓ Questions awaiting answers: {len(created_questions) if created_questions else len(sample_questions)}")
    print("\n" + "="*60)
    print("\n🎯 Next steps:")
    print("   1. Log in at http://localhost:3000/login")
    print("   2. Navigate to the Candidate Dashboard")
    print("   3. Start answering voter questions!")
    print("\n" + "="*60 + "\n")


def main():
    """Main entry point"""
    # Create database tables if they don't exist
    print("📋 Ensuring database tables exist...")
    Base.metadata.create_all(bind=engine)

    # Create session
    db = SessionLocal()

    try:
        create_demo_data(db)
    except Exception as e:
        print(f"\n❌ Error creating demo data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
