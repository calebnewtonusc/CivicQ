"""
Transcription Service

Handles video/audio transcription using multiple providers:
- OpenAI Whisper (local or API)
- AWS Transcribe
- Deepgram
- AssemblyAI
"""

import os
import json
import logging
import tempfile
from typing import Dict, List, Optional
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Service for transcribing video/audio content"""

    def __init__(self):
        """Initialize transcription service"""
        self.service = settings.TRANSCRIPTION_SERVICE
        logger.info(f"Transcription service initialized: provider={self.service}")

    async def transcribe_audio(
        self,
        audio_path: str,
        language: str = "en",
        format: str = "vtt"
    ) -> Dict:
        """
        Transcribe audio file

        Args:
            audio_path: Path to audio file
            language: Language code
            format: Output format (vtt, srt, json)

        Returns:
            Transcription result dict
        """
        if self.service == "whisper":
            return await self._transcribe_whisper(audio_path, language, format)
        elif self.service == "aws":
            return await self._transcribe_aws(audio_path, language, format)
        elif self.service == "deepgram":
            return await self._transcribe_deepgram(audio_path, language, format)
        elif self.service == "assemblyai":
            return await self._transcribe_assemblyai(audio_path, language, format)
        else:
            raise ValueError(f"Unknown transcription service: {self.service}")

    async def _transcribe_whisper(
        self,
        audio_path: str,
        language: str,
        format: str
    ) -> Dict:
        """
        Transcribe using OpenAI Whisper

        Args:
            audio_path: Path to audio file
            language: Language code
            format: Output format

        Returns:
            Transcription result
        """
        try:
            import openai

            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

            with open(audio_path, 'rb') as audio_file:
                # Use Whisper API
                if format == "vtt":
                    response = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="vtt",
                        language=language
                    )
                    transcript_text = response
                    captions = response
                else:
                    response = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="verbose_json",
                        language=language
                    )
                    transcript_text = response.text
                    captions = self._convert_to_vtt(response.segments) if format == "vtt" else None

            logger.info(f"Whisper transcription complete: {len(transcript_text)} chars")

            return {
                'text': transcript_text,
                'captions': captions,
                'language': language,
                'provider': 'whisper',
                'confidence': 0.95  # Whisper doesn't provide confidence scores
            }

        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            raise

    async def _transcribe_whisper_local(
        self,
        audio_path: str,
        language: str
    ) -> Dict:
        """
        Transcribe using local Whisper model (requires whisper package)

        Args:
            audio_path: Path to audio file
            language: Language code

        Returns:
            Transcription result
        """
        try:
            import whisper

            # Load model (can be tiny, base, small, medium, large)
            model = whisper.load_model("base")

            # Transcribe
            result = model.transcribe(audio_path, language=language)

            logger.info(f"Local Whisper transcription complete: {len(result['text'])} chars")

            return {
                'text': result['text'],
                'segments': result['segments'],
                'language': result['language'],
                'provider': 'whisper-local',
                'confidence': 0.9
            }

        except Exception as e:
            logger.error(f"Local Whisper transcription failed: {e}")
            raise

    async def _transcribe_deepgram(
        self,
        audio_path: str,
        language: str,
        format: str
    ) -> Dict:
        """
        Transcribe using Deepgram

        Args:
            audio_path: Path to audio file
            language: Language code
            format: Output format

        Returns:
            Transcription result
        """
        try:
            url = "https://api.deepgram.com/v1/listen"

            headers = {
                "Authorization": f"Token {settings.DEEPGRAM_API_KEY}",
                "Content-Type": "audio/mpeg"
            }

            params = {
                "language": language,
                "punctuate": "true",
                "diarize": "true",
                "utterances": "true",
                "smart_format": "true"
            }

            async with httpx.AsyncClient() as client:
                with open(audio_path, 'rb') as audio_file:
                    response = await client.post(
                        url,
                        headers=headers,
                        params=params,
                        content=audio_file.read(),
                        timeout=300.0
                    )

                response.raise_for_status()
                result = response.json()

            # Extract transcript
            transcript = result['results']['channels'][0]['alternatives'][0]['transcript']
            words = result['results']['channels'][0]['alternatives'][0]['words']
            confidence = result['results']['channels'][0]['alternatives'][0]['confidence']

            # Convert to VTT if needed
            captions = None
            if format == "vtt":
                captions = self._convert_deepgram_to_vtt(words)

            logger.info(f"Deepgram transcription complete: {len(transcript)} chars")

            return {
                'text': transcript,
                'captions': captions,
                'language': language,
                'provider': 'deepgram',
                'confidence': confidence,
                'words': words
            }

        except Exception as e:
            logger.error(f"Deepgram transcription failed: {e}")
            raise

    async def _transcribe_assemblyai(
        self,
        audio_path: str,
        language: str,
        format: str
    ) -> Dict:
        """
        Transcribe using AssemblyAI

        Args:
            audio_path: Path to audio file
            language: Language code
            format: Output format

        Returns:
            Transcription result
        """
        try:
            headers = {"authorization": settings.ASSEMBLYAI_API_KEY}

            # Upload audio file
            async with httpx.AsyncClient() as client:
                with open(audio_path, 'rb') as f:
                    upload_response = await client.post(
                        "https://api.assemblyai.com/v2/upload",
                        headers=headers,
                        content=f.read()
                    )
                    upload_response.raise_for_status()
                    audio_url = upload_response.json()['upload_url']

                # Request transcription
                transcript_request = {
                    "audio_url": audio_url,
                    "language_code": language
                }

                transcript_response = await client.post(
                    "https://api.assemblyai.com/v2/transcript",
                    headers=headers,
                    json=transcript_request
                )
                transcript_response.raise_for_status()
                transcript_id = transcript_response.json()['id']

                # Poll for completion
                while True:
                    status_response = await client.get(
                        f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                        headers=headers
                    )
                    status_response.raise_for_status()
                    result = status_response.json()

                    if result['status'] == 'completed':
                        break
                    elif result['status'] == 'error':
                        raise Exception(f"Transcription failed: {result['error']}")

                    # Wait before polling again
                    import asyncio
                    await asyncio.sleep(3)

            # Get VTT captions if needed
            captions = None
            if format == "vtt":
                async with httpx.AsyncClient() as client:
                    vtt_response = await client.get(
                        f"https://api.assemblyai.com/v2/transcript/{transcript_id}/vtt",
                        headers=headers
                    )
                    vtt_response.raise_for_status()
                    captions = vtt_response.text

            logger.info(f"AssemblyAI transcription complete: {len(result['text'])} chars")

            return {
                'text': result['text'],
                'captions': captions,
                'language': language,
                'provider': 'assemblyai',
                'confidence': result['confidence'],
                'words': result.get('words', [])
            }

        except Exception as e:
            logger.error(f"AssemblyAI transcription failed: {e}")
            raise

    async def _transcribe_aws(
        self,
        audio_path: str,
        language: str,
        format: str
    ) -> Dict:
        """
        Transcribe using AWS Transcribe

        Args:
            audio_path: Path to audio file
            language: Language code
            format: Output format

        Returns:
            Transcription result
        """
        try:
            import boto3
            import time

            # Upload to S3 first
            from app.services.storage_service import storage_service

            s3_key = f"transcription/temp/{os.path.basename(audio_path)}"
            # Upload would happen here using storage_service

            # Start transcription job
            transcribe = boto3.client('transcribe')

            job_name = f"transcription_{int(time.time())}"
            job_uri = storage_service.get_public_url(s3_key)

            transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': job_uri},
                MediaFormat='mp3',
                LanguageCode=language,
                Subtitles={'Formats': ['vtt']} if format == 'vtt' else {}
            )

            # Poll for completion
            while True:
                status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
                if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
                    break
                elif status['TranscriptionJob']['TranscriptionJobStatus'] == 'FAILED':
                    raise Exception("AWS Transcribe job failed")

                time.sleep(5)

            # Get results
            result_url = status['TranscriptionJob']['Transcript']['TranscriptFileUri']

            async with httpx.AsyncClient() as client:
                result_response = await client.get(result_url)
                result_response.raise_for_status()
                result = result_response.json()

            transcript = result['results']['transcripts'][0]['transcript']

            # Get VTT captions if requested
            captions = None
            if format == 'vtt' and 'SubtitleFileUris' in status['TranscriptionJob']['Subtitles']:
                vtt_url = status['TranscriptionJob']['Subtitles']['SubtitleFileUris'][0]
                async with httpx.AsyncClient() as client:
                    vtt_response = await client.get(vtt_url)
                    captions = vtt_response.text

            logger.info(f"AWS Transcribe complete: {len(transcript)} chars")

            return {
                'text': transcript,
                'captions': captions,
                'language': language,
                'provider': 'aws-transcribe',
                'confidence': 0.9
            }

        except Exception as e:
            logger.error(f"AWS Transcribe failed: {e}")
            raise

    def _convert_to_vtt(self, segments: List[Dict]) -> str:
        """
        Convert Whisper segments to WebVTT format

        Args:
            segments: List of segment dicts with start, end, text

        Returns:
            VTT formatted string
        """
        vtt = "WEBVTT\n\n"

        for i, segment in enumerate(segments):
            start = self._format_timestamp(segment['start'])
            end = self._format_timestamp(segment['end'])
            text = segment['text'].strip()

            vtt += f"{i + 1}\n{start} --> {end}\n{text}\n\n"

        return vtt

    def _convert_deepgram_to_vtt(self, words: List[Dict]) -> str:
        """
        Convert Deepgram word timestamps to WebVTT

        Args:
            words: List of word dicts with start, end, word

        Returns:
            VTT formatted string
        """
        vtt = "WEBVTT\n\n"

        # Group words into captions (max 10 words or 5 seconds)
        captions = []
        current_caption = []
        current_start = None

        for word in words:
            if not current_start:
                current_start = word['start']

            current_caption.append(word['word'])

            # Create new caption after 10 words or 5 seconds
            if len(current_caption) >= 10 or (word['end'] - current_start) >= 5:
                captions.append({
                    'start': current_start,
                    'end': word['end'],
                    'text': ' '.join(current_caption)
                })
                current_caption = []
                current_start = None

        # Add remaining words
        if current_caption:
            captions.append({
                'start': current_start,
                'end': words[-1]['end'],
                'text': ' '.join(current_caption)
            })

        # Format as VTT
        for i, caption in enumerate(captions):
            start = self._format_timestamp(caption['start'])
            end = self._format_timestamp(caption['end'])
            vtt += f"{i + 1}\n{start} --> {end}\n{caption['text']}\n\n"

        return vtt

    def _format_timestamp(self, seconds: float) -> str:
        """
        Format timestamp for VTT (HH:MM:SS.mmm)

        Args:
            seconds: Timestamp in seconds

        Returns:
            Formatted timestamp string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60

        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"


# Singleton instance
transcription_service = TranscriptionService()
