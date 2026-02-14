"""
Video Processing Tasks

Celery tasks for asynchronous video processing, transcoding, and transcription.
"""

import os
import tempfile
import logging
from typing import Dict, List
from celery import Celery, Task
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.video import Video, VideoStatus
from app.services.storage_service import storage_service
from app.services.video_processing_service import video_processing_service
from app.services.transcription_service import transcription_service

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    'video_tasks',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # 55 minutes soft limit
)


class VideoProcessingTask(Task):
    """Base task with database session management"""

    def __call__(self, *args, **kwargs):
        from app.models.base import SessionLocal
        db = SessionLocal()
        try:
            return self.run(*args, db=db, **kwargs)
        finally:
            db.close()


@celery_app.task(base=VideoProcessingTask, bind=True, name='process_video')
def process_video(self, video_id: int, db: Session = None):
    """
    Main video processing task

    Args:
        video_id: Video ID to process
        db: Database session

    Returns:
        Processing result dict
    """
    try:
        # Get video record
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            logger.error(f"Video not found: {video_id}")
            return {'error': 'Video not found'}

        # Update status
        video.status = VideoStatus.PROCESSING
        db.commit()

        logger.info(f"Starting video processing: video_id={video_id}")

        # Download original video from storage
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = os.path.join(temp_dir, 'input.mp4')
            download_url = storage_service.generate_presigned_download_url(video.original_key)

            # Download file
            import httpx
            with httpx.stream('GET', download_url) as response:
                with open(input_path, 'wb') as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)

            logger.info(f"Downloaded video: {input_path}")

            # Extract metadata
            metadata = video_processing_service.get_video_metadata(input_path)
            video.duration_seconds = metadata['duration']
            video.width = metadata['width']
            video.height = metadata['height']
            video.fps = metadata['fps']
            video.codec = metadata['codec']
            video.bitrate = metadata['bitrate']
            db.commit()

            # Validate video
            is_valid, error_msg = video_processing_service.validate_video(
                input_path,
                max_duration=settings.MAX_VIDEO_DURATION_SECONDS
            )

            if not is_valid:
                video.status = VideoStatus.FAILED
                video.processing_error = error_msg
                db.commit()
                logger.error(f"Video validation failed: {error_msg}")
                return {'error': error_msg}

            # Update progress
            self.update_state(state='PROGRESS', meta={'progress': 10})
            video.processing_progress = 10
            db.commit()

            # Process video tasks in parallel using Celery groups
            from celery import group

            tasks = []

            # 1. Transcode to multiple qualities
            tasks.append(transcode_video.s(video_id))

            # 2. Generate thumbnails
            tasks.append(generate_thumbnails.s(video_id))

            # 3. Extract audio and transcribe
            tasks.append(transcribe_video.s(video_id))

            # Execute tasks in parallel
            job = group(tasks)
            result = job.apply_async()
            result.get()  # Wait for all tasks to complete

            # Update progress
            self.update_state(state='PROGRESS', meta={'progress': 90})
            video.processing_progress = 90
            db.commit()

            # Mark as ready
            video.status = VideoStatus.READY
            video.processing_progress = 100
            db.commit()

            logger.info(f"Video processing complete: video_id={video_id}")

            return {
                'video_id': video_id,
                'status': 'completed',
                'duration': video.duration_seconds,
                'qualities': video.available_qualities
            }

    except Exception as e:
        logger.error(f"Video processing failed: {e}", exc_info=True)

        if video:
            video.status = VideoStatus.FAILED
            video.processing_error = str(e)
            db.commit()

        raise


@celery_app.task(base=VideoProcessingTask, bind=True, name='transcode_video')
def transcode_video(self, video_id: int, db: Session = None):
    """
    Transcode video to multiple quality levels

    Args:
        video_id: Video ID
        db: Database session

    Returns:
        Transcoding result
    """
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            return {'error': 'Video not found'}

        logger.info(f"Transcoding video: video_id={video_id}")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Download original
            input_path = os.path.join(temp_dir, 'input.mp4')
            download_url = storage_service.generate_presigned_download_url(video.original_key)

            import httpx
            with httpx.stream('GET', download_url) as response:
                with open(input_path, 'wb') as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)

            # Determine qualities to generate based on input resolution
            input_height = video.height
            qualities = []

            if input_height >= 1080:
                qualities = ["1080p", "720p", "480p", "360p"]
            elif input_height >= 720:
                qualities = ["720p", "480p", "360p"]
            elif input_height >= 480:
                qualities = ["480p", "360p"]
            else:
                qualities = ["360p"]

            transcoded_versions = {}

            for quality in qualities:
                output_filename = f"{quality}.mp4"
                output_path = os.path.join(temp_dir, output_filename)

                # Transcode
                result = video_processing_service.transcode_video(
                    input_path,
                    output_path,
                    quality=quality
                )

                if result:
                    # Upload to storage
                    key = f"videos/{video.user_id}/{video.id}/{output_filename}"

                    # Upload file
                    with open(output_path, 'rb') as f:
                        upload_url = storage_service.generate_presigned_upload_url(
                            key,
                            'video/mp4',
                            max_size=result['size'] * 2
                        )

                        # Upload using presigned URL
                        import httpx
                        httpx.post(
                            upload_url['url'],
                            data=upload_url['fields'],
                            files={'file': f}
                        )

                    transcoded_versions[quality] = key
                    logger.info(f"Transcoded and uploaded {quality}: {key}")

            # Update video record
            video.transcoded_versions = transcoded_versions
            db.commit()

            # Create HLS streaming
            create_hls_stream.delay(video_id)

            logger.info(f"Transcoding complete: {len(transcoded_versions)} qualities")

            return {
                'video_id': video_id,
                'qualities': list(transcoded_versions.keys())
            }

    except Exception as e:
        logger.error(f"Transcoding failed: {e}", exc_info=True)
        raise


@celery_app.task(base=VideoProcessingTask, name='create_hls_stream')
def create_hls_stream(video_id: int, db: Session = None):
    """
    Create HLS adaptive streaming files

    Args:
        video_id: Video ID
        db: Database session

    Returns:
        HLS creation result
    """
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            return {'error': 'Video not found'}

        logger.info(f"Creating HLS stream: video_id={video_id}")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Download original
            input_path = os.path.join(temp_dir, 'input.mp4')
            download_url = storage_service.generate_presigned_download_url(video.original_key)

            import httpx
            with httpx.stream('GET', download_url) as response:
                with open(input_path, 'wb') as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)

            # Create HLS output directory
            hls_dir = os.path.join(temp_dir, 'hls')

            # Generate HLS stream
            result = video_processing_service.create_hls_stream(
                input_path,
                hls_dir,
                qualities=["720p", "480p", "360p"]
            )

            # Upload HLS files to storage
            hls_prefix = f"videos/{video.user_id}/{video.id}/hls"

            for root, dirs, files in os.walk(hls_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, hls_dir)
                    s3_key = f"{hls_prefix}/{relative_path}"

                    # Determine content type
                    if file.endswith('.m3u8'):
                        content_type = 'application/vnd.apple.mpegurl'
                    elif file.endswith('.ts'):
                        content_type = 'video/mp2t'
                    else:
                        content_type = 'application/octet-stream'

                    # Upload file
                    with open(file_path, 'rb') as f:
                        upload_url = storage_service.generate_presigned_upload_url(
                            s3_key,
                            content_type
                        )

                        httpx.post(
                            upload_url['url'],
                            data=upload_url['fields'],
                            files={'file': f}
                        )

            # Update video record
            master_playlist_key = f"{hls_prefix}/master.m3u8"
            video.hls_master_playlist_key = master_playlist_key
            video.hls_master_playlist_url = storage_service.get_public_url(master_playlist_key)
            db.commit()

            logger.info(f"HLS stream created: {master_playlist_key}")

            return {
                'video_id': video_id,
                'hls_url': video.hls_master_playlist_url
            }

    except Exception as e:
        logger.error(f"HLS creation failed: {e}", exc_info=True)
        raise


@celery_app.task(base=VideoProcessingTask, name='generate_thumbnails')
def generate_thumbnails(video_id: int, db: Session = None):
    """
    Generate video thumbnails

    Args:
        video_id: Video ID
        db: Database session

    Returns:
        Thumbnail generation result
    """
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            return {'error': 'Video not found'}

        logger.info(f"Generating thumbnails: video_id={video_id}")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Download original
            input_path = os.path.join(temp_dir, 'input.mp4')
            download_url = storage_service.generate_presigned_download_url(video.original_key)

            import httpx
            with httpx.stream('GET', download_url) as response:
                with open(input_path, 'wb') as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)

            # Generate main thumbnail
            thumbnail_path = os.path.join(temp_dir, 'thumbnail.jpg')
            video_processing_service.generate_thumbnail(
                input_path,
                thumbnail_path,
                timestamp=video.duration_seconds * 0.1  # 10% into video
            )

            # Upload thumbnail
            thumbnail_key = f"videos/{video.user_id}/{video.id}/thumbnail.jpg"
            with open(thumbnail_path, 'rb') as f:
                upload_url = storage_service.generate_presigned_upload_url(
                    thumbnail_key,
                    'image/jpeg'
                )
                httpx.post(
                    upload_url['url'],
                    data=upload_url['fields'],
                    files={'file': f}
                )

            video.thumbnail_key = thumbnail_key
            video.thumbnail_url = storage_service.get_public_url(thumbnail_key)

            # Generate sprite sheet for scrubbing
            sprite_path = os.path.join(temp_dir, 'sprite.jpg')
            sprite_result = video_processing_service.generate_sprite_sheet(
                input_path,
                sprite_path,
                interval=10  # Every 10 seconds
            )

            # Upload sprite sheet
            sprite_key = f"videos/{video.user_id}/{video.id}/sprite.jpg"
            with open(sprite_path, 'rb') as f:
                upload_url = storage_service.generate_presigned_upload_url(
                    sprite_key,
                    'image/jpeg'
                )
                httpx.post(
                    upload_url['url'],
                    data=upload_url['fields'],
                    files={'file': f}
                )

            video.sprite_sheet_key = sprite_key
            video.sprite_sheet_url = storage_service.get_public_url(sprite_key)
            db.commit()

            logger.info(f"Thumbnails generated: video_id={video_id}")

            return {
                'video_id': video_id,
                'thumbnail_url': video.thumbnail_url,
                'sprite_url': video.sprite_sheet_url
            }

    except Exception as e:
        logger.error(f"Thumbnail generation failed: {e}", exc_info=True)
        raise


@celery_app.task(base=VideoProcessingTask, name='transcribe_video')
def transcribe_video(video_id: int, db: Session = None):
    """
    Transcribe video audio

    Args:
        video_id: Video ID
        db: Database session

    Returns:
        Transcription result
    """
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            return {'error': 'Video not found'}

        logger.info(f"Transcribing video: video_id={video_id}")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Download original
            input_path = os.path.join(temp_dir, 'input.mp4')
            download_url = storage_service.generate_presigned_download_url(video.original_key)

            import httpx
            with httpx.stream('GET', download_url) as response:
                with open(input_path, 'wb') as f:
                    for chunk in response.iter_bytes():
                        f.write(chunk)

            # Extract audio
            audio_path = os.path.join(temp_dir, 'audio.mp3')
            video_processing_service.extract_audio(input_path, audio_path)

            # Transcribe
            import asyncio
            result = asyncio.run(
                transcription_service.transcribe_audio(
                    audio_path,
                    language='en',
                    format='vtt'
                )
            )

            # Save transcription text
            video.transcription_text = result['text']
            video.transcription_language = result['language']
            video.has_captions = True

            # Upload VTT captions
            if result.get('captions'):
                captions_key = f"videos/{video.user_id}/{video.id}/captions.vtt"
                captions_path = os.path.join(temp_dir, 'captions.vtt')

                with open(captions_path, 'w') as f:
                    f.write(result['captions'])

                with open(captions_path, 'rb') as f:
                    upload_url = storage_service.generate_presigned_upload_url(
                        captions_key,
                        'text/vtt'
                    )
                    httpx.post(
                        upload_url['url'],
                        data=upload_url['fields'],
                        files={'file': f}
                    )

                video.captions_vtt_key = captions_key
                video.captions_vtt_url = storage_service.get_public_url(captions_key)

            db.commit()

            logger.info(f"Transcription complete: video_id={video_id}")

            return {
                'video_id': video_id,
                'text_length': len(result['text']),
                'language': result['language'],
                'has_captions': video.has_captions
            }

    except Exception as e:
        logger.error(f"Transcription failed: {e}", exc_info=True)
        raise
