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
from fractions import Fraction
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
        self.ffmpeg_available = self._check_ffmpeg_installed()

        if not self.ffmpeg_available:
            logger.warning("ffmpeg not found. Video processing will not be available.")
        else:
            logger.info("Video processing service initialized with ffmpeg")

    def _check_ffmpeg_installed(self) -> bool:
        """
        Check if ffmpeg is installed and available

        Returns:
            True if ffmpeg is available, False otherwise
        """
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
        except Exception as e:
            logger.error(f"Error checking ffmpeg availability: {e}")
            return False

    def _ensure_ffmpeg_available(self):
        """
        Ensure ffmpeg is available before processing

        Raises:
            RuntimeError: If ffmpeg is not available
        """
        if not self.ffmpeg_available:
            raise RuntimeError(
                "ffmpeg is not installed or not available in PATH. "
                "Please install ffmpeg to enable video processing. "
                "Visit https://ffmpeg.org/download.html for installation instructions."
            )

    def get_video_metadata(self, input_path: str) -> Dict:
        """
        Extract video metadata using ffprobe

        Args:
            input_path: Path to video file

        Returns:
            Video metadata dict
        """
        self._ensure_ffmpeg_available()

        if not input_path or not os.path.exists(input_path):
            raise FileNotFoundError(f"Video file not found: {input_path}")

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
                    'fps': float(Fraction(video_stream['r_frame_rate'])),  # Safely parse fraction like "30/1"
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
        qualities: List[str] = None,
        segment_duration: int = 4,
        encryption_key: Optional[str] = None
    ) -> Dict:
        """
        Create HLS adaptive streaming files with advanced features

        Args:
            input_path: Input video path
            output_dir: Output directory for HLS files
            qualities: List of quality levels to generate
            segment_duration: Segment duration in seconds
            encryption_key: Optional AES-128 encryption key

        Returns:
            HLS streaming result dict with segment information
        """
        self._ensure_ffmpeg_available()

        try:
            os.makedirs(output_dir, exist_ok=True)

            if qualities is None:
                qualities = ["1080p", "720p", "480p", "360p"]

            input_metadata = self.get_video_metadata(input_path)
            input_height = input_metadata.get('height', 0)
            input_width = input_metadata.get('width', 0)

            # Filter qualities based on input resolution
            available_qualities = [
                q for q in qualities
                if self.QUALITY_PRESETS[q]['height'] <= input_height
            ]

            if not available_qualities:
                # Use lowest quality if input is very low resolution
                available_qualities = [min(qualities, key=lambda q: self.QUALITY_PRESETS[q]['height'])]

            logger.info(f"Creating HLS stream with {len(available_qualities)} quality levels: {available_qualities}")

            # Build ffmpeg command for multi-variant HLS
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-y',  # Overwrite output files
                '-loglevel', 'info',
                '-hide_banner'
            ]

            # Map streams for each quality variant
            for idx, quality in enumerate(available_qualities):
                preset = self.QUALITY_PRESETS[quality]

                # Video stream
                cmd.extend([
                    '-map', '0:v:0',
                    '-map', '0:a:0',
                ])

            # Global encoding options
            cmd.extend([
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-ar', '48000',  # Audio sample rate
                '-ac', '2',  # Stereo audio
                '-profile:v', 'high',
                '-level', '4.0',
                '-pix_fmt', 'yuv420p',
                '-sc_threshold', '0',  # Disable scene change detection for consistent segments
                '-g', '48',  # GOP size (keyframe interval)
                '-keyint_min', '48',
                '-force_key_frames', f'expr:gte(t,n_forced*{segment_duration})',  # Force keyframes
            ])

            # Per-variant encoding settings
            for idx, quality in enumerate(available_qualities):
                preset = self.QUALITY_PRESETS[quality]

                # Calculate scale maintaining aspect ratio
                scale_filter = f"scale=-2:{preset['height']}"

                cmd.extend([
                    f'-filter:v:{idx}', scale_filter,
                    f'-maxrate:v:{idx}', preset['video_bitrate'],
                    f'-bufsize:v:{idx}', str(int(preset['video_bitrate'].replace('k', '')) * 2) + 'k',
                    f'-b:v:{idx}', preset['video_bitrate'],
                    f'-b:a:{idx}', preset['audio_bitrate'],
                    f'-preset:v:{idx}', preset['preset'],
                ])

            # HLS output options
            cmd.extend([
                '-f', 'hls',
                '-hls_time', str(segment_duration),
                '-hls_playlist_type', 'vod',
                '-hls_flags', 'independent_segments+program_date_time',
                '-hls_segment_type', 'mpegts',
                '-hls_segment_filename', os.path.join(output_dir, 'v%v/seg_%03d.ts'),
            ])

            # Add encryption if key provided
            if encryption_key:
                key_info_file = os.path.join(output_dir, 'key_info.txt')
                key_file = os.path.join(output_dir, 'enc.key')

                # Write encryption key
                with open(key_file, 'wb') as f:
                    f.write(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)

                # Write key info file
                with open(key_info_file, 'w') as f:
                    f.write(f"{key_file}\n{key_file}\n")

                cmd.extend([
                    '-hls_key_info_file', key_info_file,
                ])

            # Build variant stream map
            var_stream_map = []
            for idx, quality in enumerate(available_qualities):
                preset = self.QUALITY_PRESETS[quality]
                var_stream_map.append(f"v:{idx},a:{idx},name:{quality}")

            cmd.extend([
                '-var_stream_map', ' '.join(var_stream_map),
                '-master_pl_name', 'master.m3u8',
                os.path.join(output_dir, 'v%v/playlist.m3u8')
            ])

            logger.info(f"Running HLS generation command...")
            logger.debug(f"Command: {' '.join(cmd)}")

            # Run ffmpeg with progress monitoring
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            stderr_output = []
            for line in process.stderr:
                stderr_output.append(line)
                if 'time=' in line:
                    logger.debug(f"HLS progress: {line.strip()}")

            process.wait()

            if process.returncode != 0:
                error_msg = ''.join(stderr_output[-50:])  # Last 50 lines
                logger.error(f"HLS generation failed: {error_msg}")
                raise RuntimeError(f"HLS generation failed: {error_msg}")

            # Verify output files
            master_playlist = os.path.join(output_dir, 'master.m3u8')
            if not os.path.exists(master_playlist):
                raise RuntimeError("Master playlist not generated")

            # Count segments for each quality
            segment_info = {}
            total_segments = 0
            for idx, quality in enumerate(available_qualities):
                variant_dir = os.path.join(output_dir, f'v{idx}')
                segments = len([f for f in os.listdir(variant_dir) if f.endswith('.ts')])
                segment_info[quality] = segments
                total_segments += segments

            logger.info(f"HLS stream created successfully: {total_segments} total segments across {len(available_qualities)} qualities")

            return {
                'master_playlist': master_playlist,
                'qualities': available_qualities,
                'output_dir': output_dir,
                'segment_duration': segment_duration,
                'total_segments': total_segments,
                'segments_per_quality': segment_info,
                'encrypted': encryption_key is not None
            }

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"HLS creation failed: {error_msg}")
            raise RuntimeError(f"HLS creation failed: {error_msg}")
        except Exception as e:
            logger.error(f"Unexpected error during HLS creation: {e}", exc_info=True)
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

    def generate_multiple_thumbnails(
        self,
        input_path: str,
        output_dir: str,
        count: int = 5,
        width: int = 1280
    ) -> List[Dict]:
        """
        Generate multiple thumbnails at different timestamps

        Args:
            input_path: Input video path
            output_dir: Output directory for thumbnails
            count: Number of thumbnails to generate
            width: Thumbnail width

        Returns:
            List of thumbnail metadata dicts
        """
        self._ensure_ffmpeg_available()

        try:
            os.makedirs(output_dir, exist_ok=True)
            metadata = self.get_video_metadata(input_path)
            duration = metadata['duration']

            thumbnails = []

            for i in range(count):
                # Distribute thumbnails evenly across video duration
                timestamp = (duration / (count + 1)) * (i + 1)
                output_path = os.path.join(output_dir, f'thumb_{i:02d}.jpg')

                self.generate_thumbnail(input_path, output_path, timestamp, width)

                thumbnails.append({
                    'index': i,
                    'path': output_path,
                    'timestamp': timestamp,
                    'width': width
                })

            logger.info(f"Generated {count} thumbnails")

            return thumbnails

        except Exception as e:
            logger.error(f"Multiple thumbnail generation failed: {e}")
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
        Generate sprite sheet for video scrubbing with VTT metadata

        Args:
            input_path: Input video path
            output_path: Output sprite sheet path
            interval: Interval between frames in seconds
            tile_width: Width of each thumbnail
            tile_height: Height of each thumbnail
            columns: Number of columns in sprite

        Returns:
            Sprite sheet metadata with VTT data
        """
        self._ensure_ffmpeg_available()

        try:
            metadata = self.get_video_metadata(input_path)
            duration = metadata['duration']
            num_frames = int(duration / interval)

            # Limit to reasonable number of frames
            if num_frames > 100:
                logger.warning(f"Too many frames ({num_frames}), adjusting interval")
                interval = int(duration / 100)
                num_frames = 100

            rows = (num_frames + columns - 1) // columns

            logger.info(f"Generating sprite sheet: {num_frames} frames, {columns}x{rows} grid")

            # Generate sprite sheet using ffmpeg
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.filter(stream, 'fps', f'1/{interval}')
            stream = ffmpeg.filter(stream, 'scale', tile_width, tile_height)
            stream = ffmpeg.filter(stream, 'tile', f'{columns}x{rows}')
            stream = ffmpeg.output(stream, output_path, vcodec='mjpeg', q=2)  # High quality JPEG

            ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

            # Generate WebVTT metadata for sprite sheet
            vtt_path = output_path.replace('.jpg', '.vtt').replace('.png', '.vtt')
            self._generate_sprite_vtt(
                vtt_path,
                output_path,
                num_frames,
                columns,
                rows,
                tile_width,
                tile_height,
                interval
            )

            logger.info(f"Generated sprite sheet: {output_path} with {num_frames} frames")

            return {
                'path': output_path,
                'vtt_path': vtt_path,
                'tile_width': tile_width,
                'tile_height': tile_height,
                'columns': columns,
                'rows': rows,
                'interval': interval,
                'total_frames': num_frames
            }

        except ffmpeg.Error as e:
            logger.error(f"Sprite sheet generation failed: {e.stderr.decode()}")
            raise
        except Exception as e:
            logger.error(f"Sprite sheet generation failed: {e}")
            raise

    def _generate_sprite_vtt(
        self,
        vtt_path: str,
        sprite_url: str,
        num_frames: int,
        columns: int,
        rows: int,
        tile_width: int,
        tile_height: int,
        interval: int
    ):
        """
        Generate WebVTT file for sprite sheet thumbnails

        Args:
            vtt_path: Output VTT file path
            sprite_url: URL or path to sprite sheet
            num_frames: Total number of frames
            columns: Number of columns
            rows: Number of rows
            tile_width: Width of each tile
            tile_height: Height of each tile
            interval: Interval between frames
        """
        try:
            with open(vtt_path, 'w') as f:
                f.write("WEBVTT\n\n")

                for i in range(num_frames):
                    row = i // columns
                    col = i % columns

                    # Calculate coordinates
                    x = col * tile_width
                    y = row * tile_height

                    # Calculate time range
                    start_time = i * interval
                    end_time = (i + 1) * interval

                    # Format timestamps
                    start = self._format_vtt_timestamp(start_time)
                    end = self._format_vtt_timestamp(end_time)

                    # Write VTT cue
                    f.write(f"{start} --> {end}\n")
                    f.write(f"{os.path.basename(sprite_url)}#xywh={x},{y},{tile_width},{tile_height}\n\n")

            logger.info(f"Generated sprite VTT: {vtt_path}")

        except Exception as e:
            logger.error(f"VTT generation failed: {e}")
            raise

    def _format_vtt_timestamp(self, seconds: float) -> str:
        """
        Format timestamp for WebVTT (HH:MM:SS.mmm)

        Args:
            seconds: Timestamp in seconds

        Returns:
            Formatted timestamp
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60

        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

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
