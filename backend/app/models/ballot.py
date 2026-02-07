"""
Ballot, Contest, Candidate, and Measure Models

Ballots: city, election date, version, source metadata
Contests: ballot id, type (race/measure), title, jurisdiction, office, seat count
Candidates: contest id, name, filing id, status, contact, profile fields
Measures: contest id, measure text, summary, fiscal notes, pro/con roles
"""

from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base


class ContestType(str, enum.Enum):
    """Contest type"""
    RACE = "race"
    MEASURE = "measure"


class CandidateStatus(str, enum.Enum):
    """Candidate status"""
    PENDING = "pending"
    VERIFIED = "verified"
    ACTIVE = "active"
    WITHDRAWN = "withdrawn"
    DISQUALIFIED = "disqualified"


class Ballot(Base):
    """
    Ballot model

    Represents an election ballot for a specific city.
    """
    __tablename__ = "ballots"

    # City and election info
    city_id = Column(String, nullable=False, index=True)
    city_name = Column(String, nullable=False)
    election_date = Column(Date, nullable=False, index=True)

    # Ballot metadata
    version = Column(Integer, default=1, nullable=False)
    source_metadata = Column(JSON, nullable=True)  # Source of ballot data

    # Status
    is_published = Column(Boolean, default=False, nullable=False)

    # Relationships
    contests = relationship("Contest", back_populates="ballot", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Ballot {self.city_name} - {self.election_date}>"


class Contest(Base):
    """
    Contest model

    Represents a race or ballot measure within an election.
    """
    __tablename__ = "contests"

    # Ballot reference
    ballot_id = Column(Integer, ForeignKey("ballots.id", ondelete="CASCADE"), nullable=False)

    # Contest details
    type = Column(Enum(ContestType), nullable=False)
    title = Column(String, nullable=False)
    jurisdiction = Column(String, nullable=True)
    office = Column(String, nullable=True)  # For races
    seat_count = Column(Integer, default=1, nullable=True)  # For multi-seat races

    # Description
    description = Column(Text, nullable=True)

    # Metadata
    display_order = Column(Integer, default=0)

    # Relationships
    ballot = relationship("Ballot", back_populates="contests")
    candidates = relationship("Candidate", back_populates="contest", cascade="all, delete-orphan")
    measures = relationship("Measure", back_populates="contest", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="contest", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Contest {self.title} ({self.type})>"


class Candidate(Base):
    """
    Candidate model

    Represents a candidate in a race.
    """
    __tablename__ = "candidates"

    # Contest reference
    contest_id = Column(Integer, ForeignKey("contests.id", ondelete="CASCADE"), nullable=False)

    # User reference (if they have an account)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Candidate info
    name = Column(String, nullable=False)
    filing_id = Column(String, nullable=True, index=True)  # Official candidate filing ID

    # Contact (for onboarding)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    # Status
    status = Column(Enum(CandidateStatus), default=CandidateStatus.PENDING, nullable=False)

    # Profile
    profile_fields = Column(JSON, nullable=True)  # Flexible profile data
    photo_url = Column(String, nullable=True)
    website = Column(String, nullable=True)

    # Identity verification
    identity_verified = Column(Boolean, default=False, nullable=False)
    identity_verified_at = Column(Date, nullable=True)

    # Display order
    display_order = Column(Integer, default=0)

    # Relationships
    contest = relationship("Contest", back_populates="candidates")
    user = relationship("User")
    video_answers = relationship("VideoAnswer", back_populates="candidate", cascade="all, delete-orphan")
    rebuttals = relationship("Rebuttal", back_populates="candidate", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Candidate {self.name}>"


class Measure(Base):
    """
    Measure model

    Represents a ballot measure (proposition, referendum, etc.)
    """
    __tablename__ = "measures"

    # Contest reference
    contest_id = Column(Integer, ForeignKey("contests.id", ondelete="CASCADE"), nullable=False)

    # Measure details
    measure_number = Column(String, nullable=True)  # e.g., "Prop 1", "Measure A"
    measure_text = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    fiscal_notes = Column(Text, nullable=True)

    # Pro/Con information
    pro_statement = Column(Text, nullable=True)
    con_statement = Column(Text, nullable=True)

    # Verified proponents/opponents (optional)
    pro_contacts = Column(JSON, nullable=True)
    con_contacts = Column(JSON, nullable=True)

    # Relationships
    contest = relationship("Contest", back_populates="measures")

    def __repr__(self):
        return f"<Measure {self.measure_number}>"
