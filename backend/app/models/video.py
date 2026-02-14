"""
Video Model

Represents uploaded videos with processing state, transcoding status,
and metadata for adaptive streaming.
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Integer, DateTime, Float, JSON, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base


class VideoStatus(str, Enum):
    """Video processing status"""
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"
    DELETED = "deleted"


class TranscodingQuality(str, Enum):
    """Video quality levels for adaptive streaming"""
    SOURCE = "source"
    HD_1080P = "1080p"
    HD_720P = "720p"
    SD_480P = "480p"
    SD_360P = "360p"
    SD_240P = "240p"


class Video(Base):
    """Video model with transcoding and streaming support"""
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)

    # Ownership
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    answer_id = Column(Integer, ForeignKey("answers.id"), nullable=True, index=True)

    # Basic Info
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    # Upload Info
    original_filename = Column(String(255), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)

    # Video Properties
    duration_seconds = Column(Float, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    fps = Column(Float, nullable=True)
    codec = Column(String(50), nullable=True)
    bitrate = Column(Integer, nullable=True)

    # Processing Status
    status = Column(String(20), nullable=False, default=VideoStatus.UPLOADING, index=True)
    processing_started_at = Column(DateTime, nullable=True)
    processing_completed_at = Column(DateTime, nullable=True)
    processing_error = Column(Text, nullable=True)
    processing_progress = Column(Integer, default=0)  # 0-100

    # Storage
    storage_provider = Column(String(50), nullable=False)  # s3, r2, cloudflare
    bucket_name = Column(String(255), nullable=False)
    storage_region = Column(String(100), nullable=True)

    # Original file
    original_key = Column(String(500), nullable=False)  # S3 key
    original_url = Column(String(1000), nullable=True)  # Direct URL or CDN URL

    # Transcoded versions (JSON map of quality -> S3 key)
    transcoded_versions = Column(JSON, nullable=True, default={})
    # Example: {"1080p": "videos/abc123/1080p.mp4", "720p": "videos/abc123/720p.mp4"}

    # HLS/DASH Streaming
    hls_master_playlist_key = Column(String(500), nullable=True)
    hls_master_playlist_url = Column(String(1000), nullable=True)
    dash_manifest_key = Column(String(500), nullable=True)
    dash_manifest_url = Column(String(1000), nullable=True)

    # Thumbnails
    thumbnail_key = Column(String(500), nullable=True)
    thumbnail_url = Column(String(1000), nullable=True)
    sprite_sheet_key = Column(String(500), nullable=True)  # For video scrubbing
    sprite_sheet_url = Column(String(1000), nullable=True)
    thumbnail_timestamps = Column(JSON, nullable=True)  # Array of timestamps

    # Transcription
    transcription_key = Column(String(500), nullable=True)
    transcription_url = Column(String(1000), nullable=True)
    transcription_text = Column(Text, nullable=True)
    transcription_language = Column(String(10), nullable=True)
    has_captions = Column(Boolean, default=False)
    captions_vtt_key = Column(String(500), nullable=True)
    captions_vtt_url = Column(String(1000), nullable=True)

    # CDN
    cdn_enabled = Column(Boolean, default=True)
    cdn_distribution_id = Column(String(255), nullable=True)

    # Analytics
    view_count = Column(Integer, default=0)
    watch_time_seconds = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="videos")
    answer = relationship("Answer", back_populates="video")

    def __repr__(self):
        return f"<Video(id={self.id}, status={self.status}, duration={self.duration_seconds}s)>"

    @property
    def is_ready(self) -> bool:
        """Check if video is ready for playback"""
        return self.status == VideoStatus.READY

    @property
    def is_processing(self) -> bool:
        """Check if video is currently processing"""
        return self.status == VideoStatus.PROCESSING

    @property
    def has_hls(self) -> bool:
        """Check if HLS streaming is available"""
        return self.hls_master_playlist_url is not None

    @property
    def has_dash(self) -> bool:
        """Check if DASH streaming is available"""
        return self.dash_manifest_url is not None

    @property
    def available_qualities(self) -> list:
        """Get list of available quality levels"""
        if not self.transcoded_versions:
            return []
        return list(self.transcoded_versions.keys())

    def get_url_for_quality(self, quality: str) -> str:
        """Get playback URL for specific quality"""
        if quality == "source":
            return self.original_url

        if not self.transcoded_versions or quality not in self.transcoded_versions:
            return self.original_url

        # Build CDN URL from transcoded key
        key = self.transcoded_versions[quality]
        if self.cdn_enabled and hasattr(self, 'cdn_base_url'):
            return f"{self.cdn_base_url}/{key}"
        return f"https://{self.bucket_name}.s3.{self.storage_region}.amazonaws.com/{key}"


class VideoAnalytics(Base):
    """Track video viewing analytics"""
    __tablename__ = "video_analytics"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # Session info
    session_id = Column(String(100), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Playback info
    quality_selected = Column(String(20), nullable=True)
    watch_duration_seconds = Column(Float, nullable=False)
    completion_percentage = Column(Float, nullable=False)

    # Engagement
    paused_count = Column(Integer, default=0)
    seeked_count = Column(Integer, default=0)
    quality_changes = Column(Integer, default=0)

    # Buffering
    buffering_events = Column(Integer, default=0)
    total_buffering_time_seconds = Column(Float, default=0)

    # Timestamps
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<VideoAnalytics(video_id={self.video_id}, watch_duration={self.watch_duration_seconds}s)>"
