"""
Video Schemas

Pydantic models for video API requests and responses.
"""

from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, Field, validator


class VideoUploadRequest(BaseModel):
    """Request schema for initiating video upload"""
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type (e.g., video/mp4)")
    file_size: int = Field(..., description="File size in bytes", gt=0)
    answer_id: Optional[int] = Field(None, description="Associated answer ID")


class VideoUploadResponse(BaseModel):
    """Response schema for video upload initiation"""
    video_id: int
    upload_url: str
    upload_fields: Dict[str, str]
    key: str
    expires_in: int


class MultipartUploadInitRequest(BaseModel):
    """Request schema for multipart upload initiation"""
    filename: str
    content_type: str
    file_size: int
    part_size: int = Field(default=5 * 1024 * 1024, description="Size of each part in bytes")
    answer_id: Optional[int] = None


class MultipartUploadInitResponse(BaseModel):
    """Response schema for multipart upload initiation"""
    video_id: int
    upload_id: str
    key: str
    total_parts: int
    part_urls: List[str]


class MultipartUploadCompleteRequest(BaseModel):
    """Request schema for completing multipart upload"""
    upload_id: str
    parts: List[Dict[str, any]]  # List of {PartNumber, ETag}


class VideoMetadata(BaseModel):
    """Video metadata"""
    duration_seconds: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    codec: Optional[str] = None
    bitrate: Optional[int] = None
    file_size_bytes: int


class VideoQuality(BaseModel):
    """Video quality information"""
    quality: str
    url: str
    width: int
    height: int
    bitrate: str


class VideoStreamingInfo(BaseModel):
    """Streaming information"""
    has_hls: bool
    has_dash: bool
    hls_url: Optional[str] = None
    dash_url: Optional[str] = None
    available_qualities: List[str]


class VideoTranscription(BaseModel):
    """Video transcription information"""
    has_transcription: bool
    text: Optional[str] = None
    language: Optional[str] = None
    has_captions: bool
    captions_url: Optional[str] = None


class VideoResponse(BaseModel):
    """Complete video response"""
    id: int
    user_id: int
    answer_id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None

    # Status
    status: str
    processing_progress: int

    # Metadata
    metadata: VideoMetadata

    # Playback
    original_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    sprite_sheet_url: Optional[str] = None

    # Streaming
    streaming: VideoStreamingInfo

    # Transcription
    transcription: VideoTranscription

    # Analytics
    view_count: int
    watch_time_seconds: int

    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VideoListResponse(BaseModel):
    """List of videos with pagination"""
    videos: List[VideoResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class VideoProcessingStatus(BaseModel):
    """Video processing status"""
    video_id: int
    status: str
    progress: int
    error: Optional[str] = None
    estimated_completion: Optional[datetime] = None


class VideoAnalyticsRequest(BaseModel):
    """Video analytics tracking request"""
    session_id: str
    quality_selected: Optional[str] = None
    watch_duration_seconds: float
    completion_percentage: float
    paused_count: int = 0
    seeked_count: int = 0
    quality_changes: int = 0
    buffering_events: int = 0
    total_buffering_time_seconds: float = 0


class VideoAnalyticsResponse(BaseModel):
    """Video analytics response"""
    video_id: int
    total_views: int
    total_watch_time: int
    average_completion: float
    quality_distribution: Dict[str, int]
    average_buffering_time: float


class VideoUpdateRequest(BaseModel):
    """Video update request"""
    title: Optional[str] = None
    description: Optional[str] = None


class VideoDeleteResponse(BaseModel):
    """Video deletion response"""
    video_id: int
    deleted: bool
    message: str
