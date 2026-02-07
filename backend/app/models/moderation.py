"""
Moderation and Audit Models

Reports: reporter id, target type (question/answer/rebuttal), reason codes, status
ModerationActions: target, action type, moderator id, rationale code, timestamps
AuditLog: immutable event stream for anything integrity-sensitive
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum, JSON, Boolean
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base


class ReportStatus(str, enum.Enum):
    """Report status"""
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class ReportReason(str, enum.Enum):
    """Report reason codes"""
    SPAM = "spam"
    DOXXING = "doxxing"
    THREATS = "threats"
    HARASSMENT = "harassment"
    OFF_TOPIC = "off_topic"
    MISINFORMATION = "misinformation"
    OTHER = "other"


class ModerationActionType(str, enum.Enum):
    """Moderation action types"""
    APPROVE = "approve"
    REMOVE = "remove"
    MERGE = "merge"
    FLAG = "flag"
    WARN_USER = "warn_user"
    SUSPEND_USER = "suspend_user"


class AuditEventType(str, enum.Enum):
    """Audit event types"""
    USER_CREATED = "user_created"
    USER_VERIFIED = "user_verified"
    QUESTION_SUBMITTED = "question_submitted"
    QUESTION_VOTED = "question_voted"
    ANSWER_PUBLISHED = "answer_published"
    REBUTTAL_PUBLISHED = "rebuttal_published"
    MODERATION_ACTION = "moderation_action"
    CANDIDATE_VERIFIED = "candidate_verified"
    BALLOT_CREATED = "ballot_created"
    CONTEST_CREATED = "contest_created"
    SECURITY_ALERT = "security_alert"


class Report(Base):
    """
    Report model

    Allows users to report questions, answers, or rebuttals for moderation review.
    """
    __tablename__ = "reports"

    # Reporter
    reporter_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Target (polymorphic - can be question, answer, or rebuttal)
    target_type = Column(String, nullable=False)  # "question", "answer", "rebuttal"
    target_id = Column(Integer, nullable=False)

    # Report details
    reason = Column(Enum(ReportReason), nullable=False)
    description = Column(Text, nullable=True)

    # Status
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING, nullable=False, index=True)

    # Resolution
    resolved_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolution_notes = Column(Text, nullable=True)

    # Relationships
    reporter = relationship("User", foreign_keys=[reporter_id])
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])

    def __repr__(self):
        return f"<Report {self.target_type}:{self.target_id} - {self.reason}>"


class ModerationAction(Base):
    """
    Moderation Action model

    Records all moderation actions for transparency and accountability.
    """
    __tablename__ = "moderation_actions"

    # Target (polymorphic)
    target_type = Column(String, nullable=False)
    target_id = Column(Integer, nullable=False, index=True)

    # Action
    action_type = Column(Enum(ModerationActionType), nullable=False)

    # Moderator
    moderator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Rationale
    rationale_code = Column(String, nullable=True)  # Published moderation standard code
    rationale_text = Column(Text, nullable=True)

    # Related report (if applicable)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="SET NULL"), nullable=True)

    # Public visibility (for transparency reports)
    is_public = Column(Boolean, default=True, nullable=False)

    # Relationships
    moderator = relationship("User")
    report = relationship("Report")

    def __repr__(self):
        return f"<ModerationAction {self.action_type} on {self.target_type}:{self.target_id}>"


class AuditLog(Base):
    """
    Audit Log model

    Immutable event stream for integrity-sensitive operations.
    Used for security, compliance, and transparency.
    """
    __tablename__ = "audit_logs"

    # Event type
    event_type = Column(Enum(AuditEventType), nullable=False, index=True)

    # Actor (user who performed the action)
    actor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Target (what was acted upon)
    target_type = Column(String, nullable=True)
    target_id = Column(Integer, nullable=True)

    # Event details
    event_data = Column(JSON, nullable=True)

    # Metadata
    ip_address_hash = Column(String, nullable=True)  # Hashed, not raw IP
    user_agent = Column(String, nullable=True)
    city_scope = Column(String, nullable=True, index=True)

    # Severity (for filtering)
    severity = Column(String, default="info", nullable=False)  # info, warning, critical

    # Relationships
    actor = relationship("User")

    def __repr__(self):
        return f"<AuditLog {self.event_type} by user={self.actor_id}>"
