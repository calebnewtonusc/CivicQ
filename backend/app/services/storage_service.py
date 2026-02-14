"""
Storage Service

Handles file uploads to S3-compatible storage (AWS S3, Cloudflare R2, etc.)
with signed URL generation, CDN integration, and multipart upload support.
"""

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import hashlib
import mimetypes
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """Service for managing file storage with S3-compatible services"""

    def __init__(self):
        """Initialize S3 client with validation"""
        self.bucket = settings.S3_BUCKET
        self.region = settings.S3_REGION or "us-east-1"
        self.cdn_url = settings.CDN_URL
        self.is_available = False

        # Validate required settings
        if not settings.S3_BUCKET:
            logger.warning("S3_BUCKET not configured. Storage service will not be available.")
            return

        if not settings.S3_ACCESS_KEY or not settings.S3_SECRET_KEY:
            logger.warning("S3 credentials not configured. Storage service will not be available.")
            return

        try:
            # Configure S3 client
            config = Config(
                region_name=self.region,
                signature_version='s3v4',
                retries={
                    'max_attempts': 3,
                    'mode': 'standard'
                }
            )

            # Support both AWS S3 and S3-compatible services (like Cloudflare R2)
            client_kwargs = {
                'aws_access_key_id': settings.S3_ACCESS_KEY,
                'aws_secret_access_key': settings.S3_SECRET_KEY,
                'config': config
            }

            # Use custom endpoint for S3-compatible services (e.g., Cloudflare R2)
            if settings.S3_ENDPOINT:
                client_kwargs['endpoint_url'] = settings.S3_ENDPOINT

            self.s3_client = boto3.client('s3', **client_kwargs)

            # Validate bucket access
            self._validate_bucket_access()

            self.is_available = True
            logger.info(f"Storage service initialized: bucket={self.bucket}, region={self.region}")

        except Exception as e:
            logger.error(f"Failed to initialize storage service: {e}")
            self.is_available = False

    def _validate_bucket_access(self):
        """
        Validate that the bucket exists and is accessible

        Raises:
            ClientError: If bucket is not accessible
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket)
            logger.info(f"Successfully validated access to bucket: {self.bucket}")
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == '404':
                logger.error(f"Bucket does not exist: {self.bucket}")
            elif error_code == '403':
                logger.error(f"Access denied to bucket: {self.bucket}")
            else:
                logger.error(f"Error accessing bucket {self.bucket}: {e}")
            raise

    def _ensure_storage_available(self):
        """
        Ensure storage service is available before operations

        Raises:
            RuntimeError: If storage service is not available
        """
        if not self.is_available:
            raise RuntimeError(
                "Storage service is not available. Please check S3 configuration: "
                "S3_BUCKET, S3_ACCESS_KEY, S3_SECRET_KEY must be set."
            )

    def generate_upload_key(self, user_id: int, filename: str, prefix: str = "videos") -> str:
        """
        Generate unique S3 key for upload

        Args:
            user_id: User ID
            filename: Original filename
            prefix: Storage prefix (videos, thumbnails, etc.)

        Returns:
            S3 key path
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_hash = hashlib.md5(f"{user_id}_{filename}_{timestamp}".encode()).hexdigest()[:8]
        extension = filename.rsplit('.', 1)[1] if '.' in filename else 'mp4'

        return f"{prefix}/{user_id}/{timestamp}_{file_hash}.{extension}"

    def generate_presigned_upload_url(
        self,
        key: str,
        content_type: str,
        expires_in: int = 3600,
        max_size: int = 500 * 1024 * 1024  # 500MB default
    ) -> Dict[str, str]:
        """
        Generate presigned URL for direct upload to S3

        Args:
            key: S3 object key
            content_type: MIME type
            expires_in: URL expiration in seconds
            max_size: Maximum file size in bytes

        Returns:
            Dict with upload URL and fields
        """
        self._ensure_storage_available()

        if not key:
            raise ValueError("Object key cannot be empty")

        if not content_type:
            raise ValueError("Content type must be specified")

        try:
            # Generate presigned POST for better upload control
            presigned_post = self.s3_client.generate_presigned_post(
                Bucket=self.bucket,
                Key=key,
                Fields={
                    'Content-Type': content_type,
                    'x-amz-meta-uploaded-by': 'civicq-platform'
                },
                Conditions=[
                    {'Content-Type': content_type},
                    ['content-length-range', 0, max_size]
                ],
                ExpiresIn=expires_in
            )

            logger.info(f"Generated presigned upload URL: key={key}")

            return {
                'url': presigned_post['url'],
                'fields': presigned_post['fields'],
                'key': key,
                'expires_in': expires_in
            }

        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise

    def generate_presigned_download_url(
        self,
        key: str,
        expires_in: int = 3600,
        response_content_type: Optional[str] = None,
        response_content_disposition: Optional[str] = None
    ) -> str:
        """
        Generate presigned URL for downloading file

        Args:
            key: S3 object key
            expires_in: URL expiration in seconds
            response_content_type: Override content type
            response_content_disposition: Set content disposition

        Returns:
            Presigned download URL
        """
        try:
            params = {
                'Bucket': self.bucket,
                'Key': key
            }

            if response_content_type:
                params['ResponseContentType'] = response_content_type

            if response_content_disposition:
                params['ResponseContentDisposition'] = response_content_disposition

            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params=params,
                ExpiresIn=expires_in
            )

            return url

        except ClientError as e:
            logger.error(f"Failed to generate presigned download URL: {e}")
            raise

    def get_public_url(self, key: str) -> str:
        """
        Get public URL for object (CDN or S3)

        Args:
            key: S3 object key

        Returns:
            Public URL
        """
        if self.cdn_url:
            return f"{self.cdn_url}/{key}"

        # For S3-compatible services with custom endpoint
        if settings.S3_ENDPOINT:
            return f"{settings.S3_ENDPOINT}/{self.bucket}/{key}"

        # Standard AWS S3 URL
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"

    def initiate_multipart_upload(
        self,
        key: str,
        content_type: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Initiate multipart upload for large files

        Args:
            key: S3 object key
            content_type: MIME type
            metadata: Custom metadata

        Returns:
            Upload ID
        """
        try:
            upload_params = {
                'Bucket': self.bucket,
                'Key': key,
                'ContentType': content_type
            }

            if metadata:
                upload_params['Metadata'] = metadata

            response = self.s3_client.create_multipart_upload(**upload_params)
            upload_id = response['UploadId']

            logger.info(f"Initiated multipart upload: key={key}, upload_id={upload_id}")

            return upload_id

        except ClientError as e:
            logger.error(f"Failed to initiate multipart upload: {e}")
            raise

    def generate_presigned_upload_part_url(
        self,
        key: str,
        upload_id: str,
        part_number: int,
        expires_in: int = 3600
    ) -> str:
        """
        Generate presigned URL for uploading a part in multipart upload

        Args:
            key: S3 object key
            upload_id: Multipart upload ID
            part_number: Part number (1-indexed)
            expires_in: URL expiration in seconds

        Returns:
            Presigned URL for part upload
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'upload_part',
                Params={
                    'Bucket': self.bucket,
                    'Key': key,
                    'UploadId': upload_id,
                    'PartNumber': part_number
                },
                ExpiresIn=expires_in
            )

            return url

        except ClientError as e:
            logger.error(f"Failed to generate presigned part URL: {e}")
            raise

    def complete_multipart_upload(
        self,
        key: str,
        upload_id: str,
        parts: list
    ) -> Dict:
        """
        Complete multipart upload

        Args:
            key: S3 object key
            upload_id: Multipart upload ID
            parts: List of {PartNumber, ETag} dicts

        Returns:
            Upload result
        """
        try:
            response = self.s3_client.complete_multipart_upload(
                Bucket=self.bucket,
                Key=key,
                UploadId=upload_id,
                MultipartUpload={'Parts': parts}
            )

            logger.info(f"Completed multipart upload: key={key}")

            return response

        except ClientError as e:
            logger.error(f"Failed to complete multipart upload: {e}")
            raise

    def abort_multipart_upload(self, key: str, upload_id: str):
        """
        Abort multipart upload and clean up parts

        Args:
            key: S3 object key
            upload_id: Multipart upload ID
        """
        try:
            self.s3_client.abort_multipart_upload(
                Bucket=self.bucket,
                Key=key,
                UploadId=upload_id
            )

            logger.info(f"Aborted multipart upload: key={key}")

        except ClientError as e:
            logger.error(f"Failed to abort multipart upload: {e}")
            raise

    def delete_object(self, key: str):
        """
        Delete object from storage

        Args:
            key: S3 object key
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=key)
            logger.info(f"Deleted object: key={key}")

        except ClientError as e:
            logger.error(f"Failed to delete object: {e}")
            raise

    def delete_objects(self, keys: list):
        """
        Delete multiple objects from storage

        Args:
            keys: List of S3 object keys
        """
        if not keys:
            return

        try:
            objects = [{'Key': key} for key in keys]
            self.s3_client.delete_objects(
                Bucket=self.bucket,
                Delete={'Objects': objects}
            )

            logger.info(f"Deleted {len(keys)} objects")

        except ClientError as e:
            logger.error(f"Failed to delete objects: {e}")
            raise

    def get_object_metadata(self, key: str) -> Dict:
        """
        Get object metadata

        Args:
            key: S3 object key

        Returns:
            Object metadata
        """
        try:
            response = self.s3_client.head_object(Bucket=self.bucket, Key=key)

            return {
                'size': response['ContentLength'],
                'content_type': response['ContentType'],
                'etag': response['ETag'],
                'last_modified': response['LastModified'],
                'metadata': response.get('Metadata', {})
            }

        except ClientError as e:
            logger.error(f"Failed to get object metadata: {e}")
            raise

    def copy_object(self, source_key: str, dest_key: str) -> Dict:
        """
        Copy object within bucket

        Args:
            source_key: Source S3 key
            dest_key: Destination S3 key

        Returns:
            Copy result
        """
        try:
            response = self.s3_client.copy_object(
                Bucket=self.bucket,
                CopySource={'Bucket': self.bucket, 'Key': source_key},
                Key=dest_key
            )

            logger.info(f"Copied object: {source_key} -> {dest_key}")

            return response

        except ClientError as e:
            logger.error(f"Failed to copy object: {e}")
            raise


# Singleton instance
storage_service = StorageService()
