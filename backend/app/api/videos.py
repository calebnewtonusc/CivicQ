"""
Video API Endpoints

Handles video upload, processing, streaming, and analytics.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.security import get_current_user
from app.models.user import User
from app.models.video import Video, VideoStatus, VideoAnalytics
from app.models.answer import VideoAnswer
from app.schemas.video import (
    VideoUploadRequest,
    VideoUploadResponse,
    MultipartUploadInitRequest,
    MultipartUploadInitResponse,
    MultipartUploadCompleteRequest,
    VideoResponse,
    VideoListResponse,
    VideoProcessingStatus,
    VideoAnalyticsRequest,
    VideoAnalyticsResponse,
    VideoUpdateRequest,
    VideoDeleteResponse,
    VideoMetadata,
    VideoStreamingInfo,
    VideoTranscription,
)
from app.services.storage_service import storage_service
from app.tasks.video_tasks import process_video
from app.models.base import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload/initiate", response_model=VideoUploadResponse)
async def initiate_video_upload(
    request: VideoUploadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate video upload and get presigned upload URL

    Returns:
        Upload URL and video ID
    """
    try:
        # Validate file size (max 500MB)
        max_size = 500 * 1024 * 1024
        if request.file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum of {max_size} bytes"
            )

        # Validate content type
        allowed_types = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/webm']
        if request.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Content type {request.content_type} not allowed"
            )

        # Validate answer ownership if provided
        if request.answer_id:
            answer = db.query(VideoAnswer).filter(
                VideoAnswer.id == request.answer_id,
                VideoAnswer.candidate_id == current_user.id
            ).first()
            if not answer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Answer not found or access denied"
                )

        # Generate upload key
        key = storage_service.generate_upload_key(
            current_user.id,
            request.filename,
            prefix="videos"
        )

        # Create video record
        video = Video(
            user_id=current_user.id,
            answer_id=request.answer_id,
            original_filename=request.filename,
            file_size_bytes=request.file_size,
            mime_type=request.content_type,
            status=VideoStatus.UPLOADING,
            storage_provider="s3",
            bucket_name=storage_service.bucket,
            storage_region=storage_service.region,
            original_key=key
        )

        db.add(video)
        db.commit()
        db.refresh(video)

        logger.info(f"Video upload initiated: video_id={video.id}, user_id={current_user.id}")

        # Generate presigned upload URL
        upload_info = storage_service.generate_presigned_upload_url(
            key=key,
            content_type=request.content_type,
            expires_in=3600,  # 1 hour
            max_size=request.file_size * 2  # Allow some buffer
        )

        return VideoUploadResponse(
            video_id=video.id,
            upload_url=upload_info['url'],
            upload_fields=upload_info['fields'],
            key=upload_info['key'],
            expires_in=upload_info['expires_in']
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to initiate upload: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate upload"
        )


@router.post("/upload/multipart/initiate", response_model=MultipartUploadInitResponse)
async def initiate_multipart_upload(
    request: MultipartUploadInitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate multipart upload for large videos

    Returns:
        Upload ID and presigned URLs for each part
    """
    try:
        # Validate file size
        max_size = 5 * 1024 * 1024 * 1024  # 5GB max for multipart
        if request.file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum of {max_size} bytes"
            )

        # Generate upload key
        key = storage_service.generate_upload_key(
            current_user.id,
            request.filename,
            prefix="videos"
        )

        # Create video record
        video = Video(
            user_id=current_user.id,
            answer_id=request.answer_id,
            original_filename=request.filename,
            file_size_bytes=request.file_size,
            mime_type=request.content_type,
            status=VideoStatus.UPLOADING,
            storage_provider="s3",
            bucket_name=storage_service.bucket,
            storage_region=storage_service.region,
            original_key=key
        )

        db.add(video)
        db.commit()
        db.refresh(video)

        # Initiate multipart upload
        upload_id = storage_service.initiate_multipart_upload(
            key=key,
            content_type=request.content_type,
            metadata={'video_id': str(video.id)}
        )

        # Calculate number of parts
        total_parts = (request.file_size + request.part_size - 1) // request.part_size

        # Generate presigned URLs for each part
        part_urls = []
        for part_number in range(1, total_parts + 1):
            part_url = storage_service.generate_presigned_upload_part_url(
                key=key,
                upload_id=upload_id,
                part_number=part_number,
                expires_in=3600
            )
            part_urls.append(part_url)

        logger.info(f"Multipart upload initiated: video_id={video.id}, parts={total_parts}")

        return MultipartUploadInitResponse(
            video_id=video.id,
            upload_id=upload_id,
            key=key,
            total_parts=total_parts,
            part_urls=part_urls
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to initiate multipart upload: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate multipart upload"
        )


@router.post("/upload/{video_id}/complete")
async def complete_video_upload(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark video upload as complete and trigger processing

    Returns:
        Processing status
    """
    try:
        # Get video
        video = db.query(Video).filter(
            Video.id == video_id,
            Video.user_id == current_user.id
        ).first()

        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )

        # Update status
        video.status = VideoStatus.UPLOADED
        video.original_url = storage_service.get_public_url(video.original_key)
        db.commit()

        # Trigger processing task
        process_video.delay(video_id)

        logger.info(f"Video upload completed: video_id={video_id}")

        return {
            "video_id": video_id,
            "status": "uploaded",
            "message": "Video processing started"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to complete upload: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete upload"
        )


@router.post("/upload/multipart/{video_id}/complete")
async def complete_multipart_upload(
    video_id: int,
    request: MultipartUploadCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete multipart upload

    Returns:
        Upload completion status
    """
    try:
        # Get video
        video = db.query(Video).filter(
            Video.id == video_id,
            Video.user_id == current_user.id
        ).first()

        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )

        # Complete multipart upload
        storage_service.complete_multipart_upload(
            key=video.original_key,
            upload_id=request.upload_id,
            parts=request.parts
        )

        # Update status
        video.status = VideoStatus.UPLOADED
        video.original_url = storage_service.get_public_url(video.original_key)
        db.commit()

        # Trigger processing
        process_video.delay(video_id)

        logger.info(f"Multipart upload completed: video_id={video_id}")

        return {
            "video_id": video_id,
            "status": "uploaded",
            "message": "Video processing started"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to complete multipart upload: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete multipart upload"
        )


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get video details

    Returns:
        Video information with streaming URLs
    """
    try:
        video = db.query(Video).filter(Video.id == video_id).first()

        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )

        # Build response
        return VideoResponse(
            id=video.id,
            user_id=video.user_id,
            answer_id=video.answer_id,
            title=video.title,
            description=video.description,
            status=video.status,
            processing_progress=video.processing_progress,
            metadata=VideoMetadata(
                duration_seconds=video.duration_seconds,
                width=video.width,
                height=video.height,
                fps=video.fps,
                codec=video.codec,
                bitrate=video.bitrate,
                file_size_bytes=video.file_size_bytes
            ),
            original_url=video.original_url,
            thumbnail_url=video.thumbnail_url,
            sprite_sheet_url=video.sprite_sheet_url,
            streaming=VideoStreamingInfo(
                has_hls=video.has_hls,
                has_dash=video.has_dash,
                hls_url=video.hls_master_playlist_url,
                dash_url=video.dash_manifest_url,
                available_qualities=video.available_qualities
            ),
            transcription=VideoTranscription(
                has_transcription=video.transcription_text is not None,
                text=video.transcription_text,
                language=video.transcription_language,
                has_captions=video.has_captions,
                captions_url=video.captions_vtt_url
            ),
            view_count=video.view_count,
            watch_time_seconds=video.watch_time_seconds,
            created_at=video.created_at,
            updated_at=video.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get video: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get video"
        )


@router.get("/", response_model=VideoListResponse)
async def list_videos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List user's videos with pagination

    Returns:
        List of videos
    """
    try:
        query = db.query(Video).filter(Video.user_id == current_user.id)

        if status_filter:
            query = query.filter(Video.status == status_filter)

        total = query.count()
        videos = query.order_by(Video.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

        video_responses = []
        for video in videos:
            video_responses.append(VideoResponse(
                id=video.id,
                user_id=video.user_id,
                answer_id=video.answer_id,
                title=video.title,
                description=video.description,
                status=video.status,
                processing_progress=video.processing_progress,
                metadata=VideoMetadata(
                    duration_seconds=video.duration_seconds,
                    width=video.width,
                    height=video.height,
                    fps=video.fps,
                    codec=video.codec,
                    bitrate=video.bitrate,
                    file_size_bytes=video.file_size_bytes
                ),
                original_url=video.original_url,
                thumbnail_url=video.thumbnail_url,
                sprite_sheet_url=video.sprite_sheet_url,
                streaming=VideoStreamingInfo(
                    has_hls=video.has_hls,
                    has_dash=video.has_dash,
                    hls_url=video.hls_master_playlist_url,
                    dash_url=video.dash_manifest_url,
                    available_qualities=video.available_qualities
                ),
                transcription=VideoTranscription(
                    has_transcription=video.transcription_text is not None,
                    text=video.transcription_text,
                    language=video.transcription_language,
                    has_captions=video.has_captions,
                    captions_url=video.captions_vtt_url
                ),
                view_count=video.view_count,
                watch_time_seconds=video.watch_time_seconds,
                created_at=video.created_at,
                updated_at=video.updated_at
            ))

        return VideoListResponse(
            videos=video_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )

    except Exception as e:
        logger.error(f"Failed to list videos: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list videos"
        )


@router.get("/{video_id}/status", response_model=VideoProcessingStatus)
async def get_processing_status(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get video processing status

    Returns:
        Processing status and progress
    """
    try:
        video = db.query(Video).filter(
            Video.id == video_id,
            Video.user_id == current_user.id
        ).first()

        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )

        return VideoProcessingStatus(
            video_id=video.id,
            status=video.status,
            progress=video.processing_progress,
            error=video.processing_error,
            estimated_completion=None  # Could calculate based on processing time
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get status"
        )


@router.post("/{video_id}/analytics")
async def track_video_analytics(
    video_id: int,
    request: VideoAnalyticsRequest,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Track video viewing analytics

    Returns:
        Success message
    """
    try:
        video = db.query(Video).filter(Video.id == video_id).first()

        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )

        # Create analytics record
        analytics = VideoAnalytics(
            video_id=video_id,
            user_id=current_user.id if current_user else None,
            session_id=request.session_id,
            quality_selected=request.quality_selected,
            watch_duration_seconds=request.watch_duration_seconds,
            completion_percentage=request.completion_percentage,
            paused_count=request.paused_count,
            seeked_count=request.seeked_count,
            quality_changes=request.quality_changes,
            buffering_events=request.buffering_events,
            total_buffering_time_seconds=request.total_buffering_time_seconds
        )

        db.add(analytics)

        # Update video stats
        video.view_count += 1
        video.watch_time_seconds += int(request.watch_duration_seconds)

        db.commit()

        return {"message": "Analytics tracked successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to track analytics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to track analytics"
        )


@router.put("/{video_id}")
async def update_video(
    video_id: int,
    request: VideoUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update video metadata

    Returns:
        Updated video
    """
    try:
        video = db.query(Video).filter(
            Video.id == video_id,
            Video.user_id == current_user.id
        ).first()

        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )

        if request.title is not None:
            video.title = request.title

        if request.description is not None:
            video.description = request.description

        db.commit()

        return {"message": "Video updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update video: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update video"
        )


@router.delete("/{video_id}", response_model=VideoDeleteResponse)
async def delete_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete video and all associated files

    Returns:
        Deletion confirmation
    """
    try:
        video = db.query(Video).filter(
            Video.id == video_id,
            Video.user_id == current_user.id
        ).first()

        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Video not found"
            )

        # Collect all S3 keys to delete
        keys_to_delete = [video.original_key]

        if video.thumbnail_key:
            keys_to_delete.append(video.thumbnail_key)

        if video.sprite_sheet_key:
            keys_to_delete.append(video.sprite_sheet_key)

        if video.captions_vtt_key:
            keys_to_delete.append(video.captions_vtt_key)

        if video.transcoded_versions:
            keys_to_delete.extend(video.transcoded_versions.values())

        # Delete from storage
        storage_service.delete_objects(keys_to_delete)

        # Mark as deleted in database (soft delete)
        from datetime import datetime
        video.status = VideoStatus.DELETED
        video.deleted_at = datetime.utcnow()

        db.commit()

        logger.info(f"Video deleted: video_id={video_id}")

        return VideoDeleteResponse(
            video_id=video_id,
            deleted=True,
            message="Video deleted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete video: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete video"
        )
