"""
Question, QuestionVersion, and Vote Models

Questions: contest id, canonical question id, current version id, issue tags, status, cluster id
QuestionVersions: question id, version number, text, edit author, created timestamp, diff metadata
Votes: user id, question id, value (+1/-1), timestamp, device risk score, weight
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum, Float, ARRAY, JSON, DateTime, Index
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import enum

from app.models.base import Base


class QuestionStatus(str, enum.Enum):
    """Question status"""
    PENDING = "pending"
    APPROVED = "approved"
    MERGED = "merged"
    REMOVED = "removed"


class Question(Base):
    """
    Question model

    Represents a question asked by voters for candidates to answer.
    Questions can be versioned and clustered for deduplication.
    """
    __tablename__ = "questions"

    # Contest reference
    contest_id = Column(Integer, ForeignKey("contests.id", ondelete="CASCADE"), nullable=False, index=True)

    # Author (verified voter)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Question content (current version)
    current_version_id = Column(Integer, nullable=True)
    question_text = Column(Text, nullable=False)

    # Issue tags
    issue_tags = Column(ARRAY(String), nullable=True, index=True)

    # Status
    status = Column(Enum(QuestionStatus), default=QuestionStatus.PENDING, nullable=False, index=True)

    # Clustering for deduplication
    cluster_id = Column(Integer, nullable=True, index=True)
    embedding = Column(Vector(384), nullable=True)  # Sentence embedding for similarity

    # Context (optional - "why this matters to me")
    context = Column(Text, nullable=True)

    # Ranking metadata
    upvotes = Column(Integer, default=0, nullable=False)
    downvotes = Column(Integer, default=0, nullable=False)
    rank_score = Column(Float, default=0.0, nullable=False, index=True)
    representation_metadata = Column(JSON, nullable=True)  # e.g., neighborhood distribution

    # Moderation
    is_flagged = Column(Integer, default=0, nullable=False)
    moderation_notes = Column(Text, nullable=True)

    # Relationships
    contest = relationship("Contest", back_populates="questions")
    author = relationship("User", back_populates="questions")
    versions = relationship("QuestionVersion", back_populates="question", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="question", cascade="all, delete-orphan")
    video_answers = relationship("VideoAnswer", back_populates="question", cascade="all, delete-orphan")

    # Index for vector similarity search
    __table_args__ = (
        Index('idx_question_embedding', 'embedding', postgresql_using='ivfflat'),
    )

    def __repr__(self):
        return f"<Question {self.id}: {self.question_text[:50]}...>"


class QuestionVersion(Base):
    """
    Question Version model

    Tracks edit history of questions.
    Transparent versioning ensures answers bind to specific question versions.
    """
    __tablename__ = "question_versions"

    # Question reference
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)

    # Version info
    version_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)

    # Edit metadata
    edit_author_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    edit_reason = Column(Text, nullable=True)
    diff_metadata = Column(JSON, nullable=True)  # What changed

    # Relationships
    question = relationship("Question", back_populates="versions")
    edit_author = relationship("User")

    def __repr__(self):
        return f"<QuestionVersion {self.question_id} v{self.version_number}>"


class Vote(Base):
    """
    Vote model

    Represents upvote/downvote on questions.
    Only verified users can vote. Includes anomaly detection metadata.
    """
    __tablename__ = "votes"

    # User reference (verified voters only)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Question reference
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)

    # Vote value
    value = Column(Integer, nullable=False)  # +1 for upvote, -1 for downvote

    # Anomaly detection
    device_risk_score = Column(Float, default=0.0, nullable=True)
    weight = Column(Float, default=1.0, nullable=False)  # Can be downweighted if suspicious

    # Metadata
    metadata = Column(JSON, nullable=True)  # Device info, IP hash, etc. (non-PII)

    # Relationships
    user = relationship("User", back_populates="votes")
    question = relationship("Question", back_populates="votes")

    # Unique constraint: one vote per user per question
    __table_args__ = (
        Index('idx_user_question_vote', 'user_id', 'question_id', unique=True),
    )

    def __repr__(self):
        return f"<Vote user={self.user_id} question={self.question_id} value={self.value}>"
