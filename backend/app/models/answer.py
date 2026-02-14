"""
Video Answer, Rebuttal, and Claim Models

VideoAnswers: candidate id, question version id, video asset id, transcript id, duration, published status
Rebuttals: candidate id, target answer id, target claim reference, video asset id, transcript id
Claims: answer id, extracted claim snippet, candidate-provided sources, reviewer notes
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum, Float, Boolean, JSON
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base


class AnswerStatus(str, enum.Enum):
    """Video answer status"""
    DRAFT = "draft"
    PROCESSING = "processing"
    PUBLISHED = "published"
    WITHDRAWN = "withdrawn"


class VideoAnswer(Base):
    """
    Video Answer model

    Represents a candidate's video answer to a question.
    Videos are recorded in-app (no editing), time-boxed, and include transcripts.
    """
    __tablename__ = "video_answers"

    # Candidate reference
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)

    # Question reference (binds to specific version)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_version_id = Column(Integer, ForeignKey("question_versions.id", ondelete="SET NULL"), nullable=True)

    # Video metadata
    video_asset_id = Column(String, nullable=False)  # S3 key or storage ID
    video_url = Column(String, nullable=True)  # CDN URL
    duration = Column(Float, nullable=False)  # Seconds

    # Transcript
    transcript_id = Column(String, nullable=True)
    transcript_text = Column(Text, nullable=True)
    transcript_url = Column(String, nullable=True)  # VTT or SRT file URL

    # Captions
    captions_url = Column(String, nullable=True)

    # Provenance (authenticity metadata)
    provenance_hash = Column(String, nullable=True)  # Hash of raw video
    authenticity_metadata = Column(JSON, nullable=True)  # Chain of custody

    # Status
    status = Column(Enum(AnswerStatus), default=AnswerStatus.DRAFT, nullable=False)

    # Structured answer components (optional extraction)
    position_summary = Column(Text, nullable=True)
    rationale = Column(Text, nullable=True)
    tradeoff_acknowledged = Column(Text, nullable=True)
    implementation_plan = Column(Text, nullable=True)
    measurement_criteria = Column(Text, nullable=True)
    values_statement = Column(Text, nullable=True)

    # "I don't know yet" flag
    is_open_question = Column(Boolean, default=False, nullable=False)

    # Correction (if candidate corrects a misstatement)
    has_correction = Column(Boolean, default=False, nullable=False)
    correction_text = Column(Text, nullable=True)

    # Relationships
    candidate = relationship("Candidate", back_populates="video_answers")
    question = relationship("Question", back_populates="video_answers")
    question_version = relationship("QuestionVersion")
    claims = relationship("Claim", back_populates="answer", cascade="all, delete-orphan")
    rebuttals_received = relationship("Rebuttal", foreign_keys="Rebuttal.target_answer_id", back_populates="target_answer")
    video = relationship("Video", back_populates="answer")

    def __repr__(self):
        return f"<VideoAnswer candidate={self.candidate_id} question={self.question_id}>"


class Rebuttal(Base):
    """
    Rebuttal model

    Represents a candidate's rebuttal to another candidate's answer.
    Rebuttals must attach to a specific quoted claim (no free-floating attacks).
    """
    __tablename__ = "rebuttals"

    # Candidate giving the rebuttal
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)

    # Target answer
    target_answer_id = Column(Integer, ForeignKey("video_answers.id", ondelete="CASCADE"), nullable=False, index=True)

    # Target claim reference (quoted text from transcript)
    target_claim_text = Column(Text, nullable=False)
    target_claim_timestamp = Column(Float, nullable=True)  # Timestamp in target video

    # Rebuttal video
    video_asset_id = Column(String, nullable=False)
    video_url = Column(String, nullable=True)
    duration = Column(Float, nullable=False)

    # Transcript
    transcript_id = Column(String, nullable=True)
    transcript_text = Column(Text, nullable=True)
    transcript_url = Column(String, nullable=True)

    # Status
    status = Column(Enum(AnswerStatus), default=AnswerStatus.DRAFT, nullable=False)

    # Relationships
    candidate = relationship("Candidate", back_populates="rebuttals")
    target_answer = relationship("VideoAnswer", foreign_keys=[target_answer_id], back_populates="rebuttals_received")

    def __repr__(self):
        return f"<Rebuttal candidate={self.candidate_id} target_answer={self.target_answer_id}>"


class Claim(Base):
    """
    Claim model

    Represents an extracted claim from a video answer with optional sources.
    Candidates can attach sources (official docs, budgets, audits, etc.)
    """
    __tablename__ = "claims"

    # Answer reference
    answer_id = Column(Integer, ForeignKey("video_answers.id", ondelete="CASCADE"), nullable=False, index=True)

    # Claim content
    claim_snippet = Column(Text, nullable=False)
    claim_timestamp = Column(Float, nullable=True)  # Timestamp in video

    # Sources (candidate-provided)
    sources = Column(JSON, nullable=True)  # Array of {url, title, description}

    # Verification/review
    is_verified = Column(Boolean, default=False, nullable=False)
    reviewer_notes = Column(Text, nullable=True)

    # Relationships
    answer = relationship("VideoAnswer", back_populates="claims")

    def __repr__(self):
        return f"<Claim answer={self.answer_id}: {self.claim_snippet[:50]}...>"
