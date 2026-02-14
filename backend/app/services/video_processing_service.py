"""
Video Processing Service

Handles video transcoding, adaptive streaming (HLS/DASH), thumbnail generation,
and video optimization using ffmpeg.
"""

import ffmpeg
import subprocess
import os
import json
import tempfile
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import shutil

from app.core.config import settings

logger = logging.getLogger(__name__)


class VideoProcessingService:
    """Service for video processing and transcoding"""

    # Transcoding presets for different quality levels
    QUALITY_PRESETS = {
        "1080p": {
            "height": 1080,
            "video_bitrate": "5000k",
            "audio_bitrate": "192k",
            "preset": "medium"
        },
        "720p": {
            "height": 720,
            "video_bitrate": "2800k",
            "audio_bitrate": "128k",
            "preset": "medium"
        },
        "480p": {
            "height": 480,
            "video_bitrate": "1400k",
            "audio_bitrate": "128k",
            "preset": "medium"
        },
        "360p": {
            "height": 360,
            "video_bitrate": "800k",
            "audio_bitrate": "96k",
            "preset": "fast"
        },
        "240p": {
            "height": 240,
            "video_bitrate": "400k",
            "audio_bitrate": "64k",
            "preset": "fast"
        }
    }

    def __init__(self):
        """Initialize video processing service"""
        self.temp_dir = tempfile.gettempdir()
        logger.info("Video processing service initialized")

    def get_video_metadata(self, input_path: str) -> Dict:
        """
        Extract video metadata using ffprobe

        Args:
            input_path: Path to video file

        Returns:
            Video metadata dict
        """
        try:
            probe = ffmpeg.probe(input_path)

            video_stream = next(
                (stream for stream in probe['streams'] if stream['codec_type'] == 'video'),
                None
            )
            audio_stream = next(
                (stream for stream in probe['streams'] if stream['codec_type'] == 'audio'),
                None
            )

            metadata = {
                'duration': float(probe['format']['duration']),
                'size': int(probe['format']['size']),
                'bitrate': int(probe['format']['bit_rate']),
                'format': probe['format']['format_name'],
            }

            if video_stream:
                metadata.update({
                    'width': int(video_stream['width']),
                    'height': int(video_stream['height']),
                    'codec': video_stream['codec_name'],
                    'fps': eval(video_stream['r_frame_rate']),  # Fraction like "30/1"
                    'video_bitrate': int(video_stream.get('bit_rate', 0))
                })

            if audio_stream:
                metadata.update({
                    'audio_codec': audio_stream['codec_name'],
                    'audio_bitrate': int(audio_stream.get('bit_rate', 0)),
                    'sample_rate': int(audio_stream.get('sample_rate', 0))
                })

            logger.info(f"Extracted video metadata: duration={metadata['duration']}s, "
                       f"resolution={metadata.get('width')}x{metadata.get('height')}")

            return metadata

        except ffmpeg.Error as e:
            logger.error(f"Failed to probe video: {e.stderr.decode()}")
            raise

    def validate_video(self, input_path: str, max_duration: Optional[int] = None) -> Tuple[bool, str]:
        """
        Validate video file

        Args:
            input_path: Path to video file
            max_duration: Maximum allowed duration in seconds

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            metadata = self.get_video_metadata(input_path)

            # Check duration
            if max_duration and metadata['duration'] > max_duration:
                return False, f"Video duration exceeds maximum of {max_duration} seconds"

            # Check if video stream exists
            if 'width' not in metadata:
                return False, "No video stream found in file"

            # Check minimum resolution
            if metadata.get('width', 0) < 320 or metadata.get('height', 0) < 240:
                return False, "Video resolution too low (minimum 320x240)"

            return True, ""

        except Exception as e:
            return False, f"Invalid video file: {str(e)}"

    def transcode_video(
        self,
        input_path: str,
        output_path: str,
        quality: str = "720p",
        progress_callback: Optional[callable] = None
    ) -> Dict:
        """
        Transcode video to specific quality

        Args:
            input_path: Input video path
            output_path: Output video path
            quality: Quality preset (1080p, 720p, 480p, 360p, 240p)
            progress_callback: Optional callback for progress updates

        Returns:
            Transcoding result dict
        """
        try:
            preset = self.QUALITY_PRESETS[quality]

            # Get input metadata
            input_metadata = self.get_video_metadata(input_path)
            input_height = input_metadata.get('height', 0)

            # Skip if input resolution is lower than target
            if input_height < preset['height']:
                logger.info(f"Skipping {quality} transcode: input resolution too low")
                return None

            # Build ffmpeg command
            stream = ffmpeg.input(input_path)

            # Scale video maintaining aspect ratio
            video = stream.video.filter('scale', -2, preset['height'])

            # Audio stream
            audio = stream.audio

            # Output with codec settings
            output = ffmpeg.output(
                video,
                audio,
                output_path,
                vcodec='libx264',
                video_bitrate=preset['video_bitrate'],
                acodec='aac',
                audio_bitrate=preset['audio_bitrate'],
                preset=preset['preset'],
                movflags='faststart',  # Enable progressive download
                pix_fmt='yuv420p'  # Compatibility
            )

            # Run transcoding
            logger.info(f"Transcoding to {quality}: {input_path} -> {output_path}")

            ffmpeg.run(output, overwrite_output=True, capture_stdout=True, capture_stderr=True)

            # Get output metadata
            output_metadata = self.get_video_metadata(output_path)

            logger.info(f"Transcoding complete: {quality}, size={output_metadata['size']} bytes")

            return {
                'quality': quality,
                'path': output_path,
                'size': output_metadata['size'],
                'bitrate': output_metadata['bitrate'],
                'duration': output_metadata['duration']
            }

        except ffmpeg.Error as e:
            logger.error(f"Transcoding failed for {quality}: {e.stderr.decode()}")
            raise

    def create_hls_stream(
        self,
        input_path: str,
        output_dir: str,
        qualities: List[str] = None
    ) -> Dict:
        """
        Create HLS adaptive streaming files

        Args:
            input_path: Input video path
            output_dir: Output directory for HLS files
            qualities: List of quality levels to generate

        Returns:
            HLS streaming result dict
        """
        try:
            os.makedirs(output_dir, exist_ok=True)

            if qualities is None:
                qualities = ["720p", "480p", "360p"]

            input_metadata = self.get_video_metadata(input_path)
            input_height = input_metadata.get('height', 0)

            # Filter qualities based on input resolution
            available_qualities = [
                q for q in qualities
                if self.QUALITY_PRESETS[q]['height'] <= input_height
            ]

            if not available_qualities:
                available_qualities = [min(qualities, key=lambda q: self.QUALITY_PRESETS[q]['height'])]

            variant_streams = []
            stream_map = []

            for idx, quality in enumerate(available_qualities):
                preset = self.QUALITY_PRESETS[quality]
                variant_streams.append(f"v:{idx},a:{idx}")
                stream_map.append(
                    f"v:{idx}:height={preset['height']},v_b={preset['video_bitrate']},"
                    f"a:{idx}:a_b={preset['audio_bitrate']}"
                )

            # Build HLS command
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'medium',
            ]

            # Add streams for each quality
            for idx, quality in enumerate(available_qualities):
                preset = self.QUALITY_PRESETS[quality]
                cmd.extend([
                    '-map', '0:v',
                    '-map', '0:a',
                    '-filter:v:{}'.format(idx), f'scale=-2:{preset["height"]}',
                    '-b:v:{}'.format(idx), preset['video_bitrate'],
                    '-b:a:{}'.format(idx), preset['audio_bitrate'],
                ])

            # HLS options
            master_playlist = os.path.join(output_dir, 'master.m3u8')
            cmd.extend([
                '-f', 'hls',
                '-hls_time', '4',
                '-hls_playlist_type', 'vod',
                '-hls_segment_filename', os.path.join(output_dir, 'segment_%v_%03d.ts'),
                '-master_pl_name', 'master.m3u8',
                '-var_stream_map', ' '.join(variant_streams),
                os.path.join(output_dir, 'stream_%v.m3u8')
            ])

            logger.info(f"Creating HLS stream with qualities: {available_qualities}")

            subprocess.run(cmd, check=True, capture_output=True)

            logger.info(f"HLS stream created: {master_playlist}")

            return {
                'master_playlist': master_playlist,
                'qualities': available_qualities,
                'output_dir': output_dir
            }

        except subprocess.CalledProcessError as e:
            logger.error(f"HLS creation failed: {e.stderr.decode()}")
            raise

    def generate_thumbnail(
        self,
        input_path: str,
        output_path: str,
        timestamp: float = None,
        width: int = 1280
    ) -> str:
        """
        Generate video thumbnail

        Args:
            input_path: Input video path
            output_path: Output image path
            timestamp: Timestamp in seconds (defaults to 10% of duration)
            width: Thumbnail width

        Returns:
            Output thumbnail path
        """
        try:
            metadata = self.get_video_metadata(input_path)

            if timestamp is None:
                timestamp = metadata['duration'] * 0.1  # 10% into video

            # Ensure timestamp is within video duration
            timestamp = min(timestamp, metadata['duration'] - 1)

            # Generate thumbnail
            stream = ffmpeg.input(input_path, ss=timestamp)
            stream = ffmpeg.filter(stream, 'scale', width, -1)
            stream = ffmpeg.output(stream, output_path, vframes=1, format='image2', vcodec='mjpeg')

            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

            logger.info(f"Generated thumbnail at {timestamp}s: {output_path}")

            return output_path

        except ffmpeg.Error as e:
            logger.error(f"Thumbnail generation failed: {e.stderr.decode()}")
            raise

    def generate_sprite_sheet(
        self,
        input_path: str,
        output_path: str,
        interval: int = 10,
        tile_width: int = 160,
        tile_height: int = 90,
        columns: int = 10
    ) -> Dict:
        """
        Generate sprite sheet for video scrubbing

        Args:
            input_path: Input video path
            output_path: Output sprite sheet path
            interval: Interval between frames in seconds
            tile_width: Width of each thumbnail
            tile_height: Height of each thumbnail
            columns: Number of columns in sprite

        Returns:
            Sprite sheet metadata
        """
        try:
            metadata = self.get_video_metadata(input_path)
            duration = metadata['duration']
            num_frames = int(duration / interval)

            # Generate sprite sheet using ffmpeg
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.filter(stream, 'fps', f'1/{interval}')
            stream = ffmpeg.filter(stream, 'scale', tile_width, tile_height)
            stream = ffmpeg.filter(stream, 'tile', f'{columns}x{(num_frames + columns - 1) // columns}')
            stream = ffmpeg.output(stream, output_path)

            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

            logger.info(f"Generated sprite sheet: {num_frames} frames, {output_path}")

            return {
                'path': output_path,
                'tile_width': tile_width,
                'tile_height': tile_height,
                'columns': columns,
                'interval': interval,
                'total_frames': num_frames
            }

        except ffmpeg.Error as e:
            logger.error(f"Sprite sheet generation failed: {e.stderr.decode()}")
            raise

    def extract_audio(self, input_path: str, output_path: str) -> str:
        """
        Extract audio from video for transcription

        Args:
            input_path: Input video path
            output_path: Output audio path (e.g., .mp3 or .wav)

        Returns:
            Output audio path
        """
        try:
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.output(stream, output_path, acodec='libmp3lame', audio_bitrate='128k')

            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

            logger.info(f"Extracted audio: {output_path}")

            return output_path

        except ffmpeg.Error as e:
            logger.error(f"Audio extraction failed: {e.stderr.decode()}")
            raise

    def optimize_for_web(self, input_path: str, output_path: str) -> str:
        """
        Optimize video for web playback

        Args:
            input_path: Input video path
            output_path: Output video path

        Returns:
            Output video path
        """
        try:
            # Web-optimized settings
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.output(
                stream,
                output_path,
                vcodec='libx264',
                acodec='aac',
                preset='medium',
                crf=23,
                movflags='faststart',  # Enable progressive download
                pix_fmt='yuv420p',
                vf='scale=trunc(iw/2)*2:trunc(ih/2)*2'  # Ensure even dimensions
            )

            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

            logger.info(f"Optimized video for web: {output_path}")

            return output_path

        except ffmpeg.Error as e:
            logger.error(f"Web optimization failed: {e.stderr.decode()}")
            raise


# Singleton instance
video_processing_service = VideoProcessingService()
