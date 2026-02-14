import React, { useState, useRef, useEffect } from 'react';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';
import SuccessMessage from './SuccessMessage';

interface VideoAnswerRecorderProps {
  questionId: number;
  questionText: string;
  candidateId: number;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export const VideoAnswerRecorder: React.FC<VideoAnswerRecorderProps> = ({
  questionId,
  questionText,
  candidateId,
  onSuccess,
  onCancel,
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPreviewing, setIsPreviewing] = useState(false);
  const [recordedVideoUrl, setRecordedVideoUrl] = useState<string | null>(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const MAX_RECORDING_TIME = 120; // 2 minutes in seconds

  useEffect(() => {
    return () => {
      // Cleanup on unmount
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      if (recordedVideoUrl) {
        URL.revokeObjectURL(recordedVideoUrl);
      }
    };
  }, [stream, recordedVideoUrl]);

  const startCamera = async () => {
    try {
      setError(null);
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user'
        },
        audio: true
      });

      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err) {
      console.error('Error accessing camera:', err);
      setError('Could not access camera and microphone. Please check permissions.');
    }
  };

  const startRecording = () => {
    if (!stream) return;

    try {
      chunksRef.current = [];
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'video/webm;codecs=vp8,opus'
      });

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'video/webm' });
        const url = URL.createObjectURL(blob);
        setRecordedVideoUrl(url);
        setIsPreviewing(true);

        // Stop the camera stream
        if (stream) {
          stream.getTracks().forEach(track => track.stop());
          setStream(null);
        }
      };

      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;
      setIsRecording(true);
      setRecordingTime(0);

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => {
          const newTime = prev + 1;
          if (newTime >= MAX_RECORDING_TIME) {
            stopRecording();
          }
          return newTime;
        });
      }, 1000);
    } catch (err) {
      console.error('Error starting recording:', err);
      setError('Could not start recording. Please try again.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);

      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  const retakeVideo = async () => {
    if (recordedVideoUrl) {
      URL.revokeObjectURL(recordedVideoUrl);
      setRecordedVideoUrl(null);
    }
    setIsPreviewing(false);
    setRecordingTime(0);
    await startCamera();
  };

  const uploadVideo = async () => {
    if (!recordedVideoUrl) return;

    try {
      setIsUploading(true);
      setError(null);

      // In a real implementation, you would:
      // 1. Convert the blob to a file
      // 2. Upload to your backend/S3
      // 3. Submit the answer with the video URL

      // For demo purposes, we'll simulate an upload
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Mock submission
      const response = await fetch(`http://localhost:8000/api/candidates/${candidateId}/answers`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          question_id: questionId,
          video_url: 'https://demo-video-url.com/placeholder.mp4', // In production, this would be the actual uploaded URL
          duration: recordingTime,
          transcript: 'Video transcript will be generated automatically'
        })
      });

      if (!response.ok) {
        throw new Error('Failed to submit answer');
      }

      setSuccess('Answer submitted successfully!');
      setTimeout(() => {
        if (onSuccess) onSuccess();
      }, 1500);
    } catch (err) {
      console.error('Error uploading video:', err);
      setError('Failed to upload video. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Question Display */}
      <div className="mb-6 p-4 bg-blue-50 rounded-lg">
        <h3 className="text-sm font-medium text-gray-700 mb-2">Question:</h3>
        <p className="text-lg font-semibold text-gray-900">{questionText}</p>
      </div>

      {error && <ErrorMessage message={error} className="mb-4" />}
      {success && <SuccessMessage message={success} className="mb-4" />}

      {/* Video Display */}
      <div className="relative bg-gray-900 rounded-lg overflow-hidden mb-6" style={{ aspectRatio: '16/9' }}>
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted={!isPreviewing}
          src={isPreviewing ? recordedVideoUrl || undefined : undefined}
          className="w-full h-full object-cover"
        />

        {/* Recording Indicator */}
        {isRecording && (
          <div className="absolute top-4 left-4 flex items-center space-x-2 bg-red-600 text-white px-3 py-1.5 rounded-full">
            <div className="h-3 w-3 bg-white rounded-full animate-pulse" />
            <span className="text-sm font-medium">REC {formatTime(recordingTime)}</span>
          </div>
        )}

        {/* Time Limit Warning */}
        {isRecording && recordingTime >= MAX_RECORDING_TIME - 10 && (
          <div className="absolute top-4 right-4 bg-yellow-500 text-white px-3 py-1.5 rounded-full">
            <span className="text-sm font-medium">{MAX_RECORDING_TIME - recordingTime}s remaining</span>
          </div>
        )}

        {/* No Camera Placeholder */}
        {!stream && !isPreviewing && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center text-white">
              <svg className="mx-auto h-16 w-16 mb-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <p className="text-lg font-medium">Camera not started</p>
            </div>
          </div>
        )}
      </div>

      {/* Recording Guidelines */}
      {!isRecording && !isPreviewing && (
        <div className="mb-6 p-4 bg-yellow-50 rounded-lg">
          <h4 className="text-sm font-medium text-yellow-800 mb-2">Recording Guidelines:</h4>
          <ul className="text-sm text-yellow-700 space-y-1">
            <li>Maximum recording time: {formatTime(MAX_RECORDING_TIME)}</li>
            <li>Ensure good lighting and minimal background noise</li>
            <li>Answer the question directly and concisely</li>
            <li>Videos cannot be edited after recording (authenticity guarantee)</li>
          </ul>
        </div>
      )}

      {/* Controls */}
      <div className="flex items-center justify-center space-x-4">
        {!stream && !isPreviewing && (
          <button
            onClick={startCamera}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 font-medium"
          >
            Start Camera
          </button>
        )}

        {stream && !isRecording && !isPreviewing && (
          <button
            onClick={startRecording}
            className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 font-medium flex items-center"
          >
            <div className="h-3 w-3 bg-white rounded-full mr-2" />
            Start Recording
          </button>
        )}

        {isRecording && (
          <button
            onClick={stopRecording}
            className="px-6 py-3 bg-gray-800 text-white rounded-lg hover:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 font-medium"
          >
            Stop Recording
          </button>
        )}

        {isPreviewing && (
          <>
            <button
              onClick={retakeVideo}
              className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 font-medium"
            >
              Retake
            </button>
            <button
              onClick={uploadVideo}
              disabled={isUploading}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {isUploading ? (
                <>
                  <LoadingSpinner size="sm" className="mr-2" />
                  Uploading...
                </>
              ) : (
                'Submit Answer'
              )}
            </button>
          </>
        )}

        {onCancel && (
          <button
            onClick={onCancel}
            className="px-6 py-3 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 font-medium"
          >
            Cancel
          </button>
        )}
      </div>

      {/* Preview Info */}
      {isPreviewing && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-600">
            <strong>Recording Duration:</strong> {formatTime(recordingTime)}
          </p>
          <p className="text-sm text-gray-600 mt-2">
            Please review your answer before submitting. Once submitted, this video will be publicly visible and cannot be edited.
          </p>
        </div>
      )}
    </div>
  );
};
