/**
 * Video Uploader Component
 *
 * Professional video upload with:
 * - Drag & drop support
 * - Chunked/multipart upload for large files
 * - Progress tracking
 * - Preview and validation
 * - Automatic processing initiation
 */

import React, { useState, useRef, useCallback } from 'react';
import axios from 'axios';
import './VideoUploader.css';

interface VideoUploaderProps {
  answerId?: number;
  onUploadComplete?: (videoId: number) => void;
  onError?: (error: string) => void;
  maxSizeMB?: number;
  maxDurationSeconds?: number;
}

interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

const VideoUploader: React.FC<VideoUploaderProps> = ({
  answerId,
  onUploadComplete,
  onError,
  maxSizeMB = 500,
  maxDurationSeconds = 180
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState<UploadProgress>({ loaded: 0, total: 0, percentage: 0 });
  const [videoId, setVideoId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoPreviewRef = useRef<HTMLVideoElement>(null);

  const validateVideo = useCallback(async (file: File): Promise<boolean> => {
    // Check file size
    const maxBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxBytes) {
      const errorMsg = `File size exceeds ${maxSizeMB}MB limit`;
      setError(errorMsg);
      onError?.(errorMsg);
      return false;
    }

    // Check file type
    const allowedTypes = ['video/mp4', 'video/quicktime', 'video/webm', 'video/x-msvideo'];
    if (!allowedTypes.includes(file.type)) {
      const errorMsg = 'Invalid file type. Please upload MP4, MOV, or WebM';
      setError(errorMsg);
      onError?.(errorMsg);
      return false;
    }

    // Check video duration
    return new Promise((resolve) => {
      const video = document.createElement('video');
      video.preload = 'metadata';

      video.onloadedmetadata = () => {
        window.URL.revokeObjectURL(video.src);

        if (video.duration > maxDurationSeconds) {
          const errorMsg = `Video duration exceeds ${maxDurationSeconds} seconds limit`;
          setError(errorMsg);
          onError?.(errorMsg);
          resolve(false);
        } else {
          resolve(true);
        }
      };

      video.onerror = () => {
        const errorMsg = 'Failed to load video metadata';
        setError(errorMsg);
        onError?.(errorMsg);
        resolve(false);
      };

      video.src = URL.createObjectURL(file);
    });
  }, [maxSizeMB, maxDurationSeconds, onError]);

  const handleFileSelect = useCallback(async (file: File) => {
    setError(null);

    const isValid = await validateVideo(file);
    if (!isValid) {
      return;
    }

    setSelectedFile(file);

    // Create preview
    const previewUrl = URL.createObjectURL(file);
    setPreview(previewUrl);
  }, [validateVideo]);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const file = e.dataTransfer.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const uploadSmallFile = async (file: File, uploadUrl: string, fields: Record<string, string>) => {
    const formData = new FormData();

    // Add all fields from presigned URL
    Object.entries(fields).forEach(([key, value]) => {
      formData.append(key, value);
    });

    // Add file last
    formData.append('file', file);

    await axios.post(uploadUrl, formData, {
      onUploadProgress: (progressEvent) => {
        const loaded = progressEvent.loaded || 0;
        const total = progressEvent.total || file.size;
        const percentage = Math.round((loaded * 100) / total);

        setProgress({ loaded, total, percentage });
      }
    });
  };

  const uploadLargeFile = async (file: File) => {
    const chunkSize = 5 * 1024 * 1024; // 5MB chunks

    // Initiate multipart upload
    const initResponse = await axios.post('/api/videos/upload/multipart/initiate', {
      filename: file.name,
      content_type: file.type,
      file_size: file.size,
      part_size: chunkSize,
      answer_id: answerId
    });

    const { video_id, upload_id, part_urls } = initResponse.data;
    setVideoId(video_id);

    // Upload parts
    const parts = [];
    const totalParts = part_urls.length;

    for (let i = 0; i < totalParts; i++) {
      const start = i * chunkSize;
      const end = Math.min(start + chunkSize, file.size);
      const chunk = file.slice(start, end);

      const partResponse = await axios.put(part_urls[i], chunk, {
        headers: {
          'Content-Type': file.type
        },
        onUploadProgress: (progressEvent) => {
          const partLoaded = progressEvent.loaded || 0;
          const overallLoaded = start + partLoaded;
          const percentage = Math.round((overallLoaded * 100) / file.size);

          setProgress({
            loaded: overallLoaded,
            total: file.size,
            percentage
          });
        }
      });

      parts.push({
        PartNumber: i + 1,
        ETag: partResponse.headers.etag
      });
    }

    // Complete multipart upload
    await axios.post(`/api/videos/upload/multipart/${video_id}/complete`, {
      upload_id,
      parts
    });

    return video_id;
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setError(null);
    setProgress({ loaded: 0, total: selectedFile.size, percentage: 0 });

    try {
      const isLargeFile = selectedFile.size > 100 * 1024 * 1024; // 100MB threshold

      if (isLargeFile) {
        // Use multipart upload for large files
        const uploadedVideoId = await uploadLargeFile(selectedFile);
        setVideoId(uploadedVideoId);
      } else {
        // Use simple presigned upload for smaller files
        const initResponse = await axios.post('/api/videos/upload/initiate', {
          filename: selectedFile.name,
          content_type: selectedFile.type,
          file_size: selectedFile.size,
          answer_id: answerId
        });

        const { video_id, upload_url, upload_fields } = initResponse.data;
        setVideoId(video_id);

        await uploadSmallFile(selectedFile, upload_url, upload_fields);

        // Mark upload as complete
        await axios.post(`/api/videos/upload/${video_id}/complete`);
      }

      // Upload complete
      if (videoId && onUploadComplete) {
        onUploadComplete(videoId);
      }

      // Reset
      setSelectedFile(null);
      setPreview(null);
      setProgress({ loaded: 0, total: 0, percentage: 0 });

    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Upload failed';
      setError(errorMsg);
      onError?.(errorMsg);
    } finally {
      setUploading(false);
    }
  };

  const handleCancel = () => {
    setSelectedFile(null);
    setPreview(null);
    setProgress({ loaded: 0, total: 0, percentage: 0 });
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="video-uploader">
      {!selectedFile ? (
        <div
          className={`upload-area ${dragActive ? 'drag-active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="video/mp4,video/quicktime,video/webm"
            onChange={handleFileInput}
            style={{ display: 'none' }}
          />

          <div className="upload-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>

          <p className="upload-title">Drop your video here or click to browse</p>
          <p className="upload-subtitle">
            MP4, MOV, or WebM • Max {maxSizeMB}MB • Max {maxDurationSeconds}s
          </p>
        </div>
      ) : (
        <div className="preview-area">
          {preview && (
            <video
              ref={videoPreviewRef}
              src={preview}
              controls
              className="video-preview"
            />
          )}

          <div className="file-info">
            <p className="file-name">{selectedFile.name}</p>
            <p className="file-size">{formatFileSize(selectedFile.size)}</p>
          </div>

          {uploading ? (
            <div className="progress-area">
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${progress.percentage}%` }}
                />
              </div>
              <p className="progress-text">
                Uploading... {progress.percentage}%
                ({formatFileSize(progress.loaded)} / {formatFileSize(progress.total)})
              </p>
            </div>
          ) : (
            <div className="action-buttons">
              <button
                onClick={handleUpload}
                className="btn btn-primary"
                disabled={uploading}
              >
                Upload Video
              </button>
              <button
                onClick={handleCancel}
                className="btn btn-secondary"
                disabled={uploading}
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="error-message">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" strokeWidth={2} />
            <line x1="12" y1="8" x2="12" y2="12" strokeWidth={2} strokeLinecap="round" />
            <line x1="12" y1="16" x2="12.01" y2="16" strokeWidth={2} strokeLinecap="round" />
          </svg>
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};

export default VideoUploader;
