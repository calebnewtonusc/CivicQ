"""
Follow Model

Follows: user id, follow target (contest/candidate/issue tag), notification prefs
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Enum, JSON, Boolean, Index
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base


class FollowTargetType(str, enum.Enum):
    """Follow target types"""
    CONTEST = "contest"
    CANDIDATE = "candidate"
    ISSUE_TAG = "issue_tag"


class Follow(Base):
    """
    Follow model

    Allows users to follow contests, candidates, or issue tags
    to receive updates and curated content.
    """
    __tablename__ = "follows"

    # User reference
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Follow target (polymorphic)
    target_type = Column(Enum(FollowTargetType), nullable=False)
    target_id = Column(Integer, nullable=True)  # Null for issue tags
    target_value = Column(String, nullable=True)  # For issue tags (string value)

    # Notification preferences
    notification_prefs = Column(JSON, nullable=True)  # e.g., {email: true, push: false}

    # Active status
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="follows")

    # Unique constraint: one follow per user per target
    __table_args__ = (
        Index('idx_user_follow_target', 'user_id', 'target_type', 'target_id', 'target_value', unique=True),
    )

    def __repr__(self):
        return f"<Follow user={self.user_id} target={self.target_type}:{self.target_id or self.target_value}>"
