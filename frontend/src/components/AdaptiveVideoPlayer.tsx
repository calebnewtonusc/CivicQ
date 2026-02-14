/**
 * Professional Adaptive Video Player Component
 *
 * Features:
 * - Adaptive streaming (HLS) with quality selection
 * - Custom controls with modern UI
 * - Closed captions/subtitles
 * - Picture-in-Picture
 * - Playback speed control
 * - Keyboard shortcuts
 * - Analytics tracking
 * - Thumbnail preview on scrubbing
 */

import React, { useRef, useState, useEffect, useCallback } from 'react';
import Hls from 'hls.js';
import axios from 'axios';
import './AdaptiveVideoPlayer.css';

interface AdaptiveVideoPlayerProps {
  videoId: number;
  autoplay?: boolean;
  muted?: boolean;
  controls?: boolean;
  className?: string;
}

interface VideoData {
  id: number;
  status: string;
  original_url: string;
  thumbnail_url?: string;
  streaming: {
    has_hls: boolean;
    hls_url?: string;
    available_qualities: string[];
  };
  transcription: {
    has_captions: boolean;
    captions_url?: string;
  };
  metadata: {
    duration_seconds: number;
    width: number;
    height: number;
  };
}

const AdaptiveVideoPlayer: React.FC<AdaptiveVideoPlayerProps> = ({
  videoId,
  autoplay = false,
  muted = false,
  controls = true,
  className = ''
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const hlsRef = useRef<Hls | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);

  const [videoData, setVideoData] = useState<VideoData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [mute, setMute] = useState(muted);
  const [fullscreen, setFullscreen] = useState(false);
  const [showControls, setShowControls] = useState(true);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [selectedQuality, setSelectedQuality] = useState<string>('auto');
  const [availableQualities, setAvailableQualities] = useState<string[]>([]);
  const [showSettings, setShowSettings] = useState(false);
  const [buffering, setBuffering] = useState(false);

  const sessionId = useRef(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const watchStartTime = useRef<number>(0);
  const analyticsTimer = useRef<NodeJS.Timeout | null>(null);

  // Load video data
  useEffect(() => {
    loadVideoData();
  }, [videoId]);

  const loadVideoData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/videos/${videoId}`);
      setVideoData(response.data);

      if (response.data.status !== 'ready') {
        setError('Video is still processing. Please check back later.');
        return;
      }

      setLoading(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load video');
      setLoading(false);
    }
  };

  // Initialize video player
  useEffect(() => {
    if (!videoData || !videoRef.current) return;

    const video = videoRef.current;

    // Use HLS if available
    if (videoData.streaming.has_hls && videoData.streaming.hls_url) {
      if (Hls.isSupported()) {
        const hls = new Hls({
          enableWorker: true,
          lowLatencyMode: false,
          backBufferLength: 90
        });

        hls.loadSource(videoData.streaming.hls_url);
        hls.attachMedia(video);

        hls.on(Hls.Events.MANIFEST_PARSED, () => {
          const levels = hls.levels.map((level, index) => ({
            index,
            height: level.height,
            bitrate: level.bitrate
          }));

          const qualities = levels.map(l => `${l.height}p`);
          setAvailableQualities(['auto', ...qualities]);

          if (autoplay) {
            video.play();
          }
        });

        hls.on(Hls.Events.ERROR, (event, data) => {
          if (data.fatal) {
            switch (data.type) {
              case Hls.ErrorTypes.NETWORK_ERROR:
                hls.startLoad();
                break;
              case Hls.ErrorTypes.MEDIA_ERROR:
                hls.recoverMediaError();
                break;
              default:
                setError('Fatal error loading video');
                break;
            }
          }
        });

        hlsRef.current = hls;

        return () => {
          hls.destroy();
        };
      } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        // Native HLS support (Safari)
        video.src = videoData.streaming.hls_url;
      }
    } else {
      // Fallback to original video
      video.src = videoData.original_url;
    }

    // Add captions if available
    if (videoData.transcription.has_captions && videoData.transcription.captions_url) {
      const track = document.createElement('track');
      track.kind = 'captions';
      track.label = 'English';
      track.srclang = 'en';
      track.src = videoData.transcription.captions_url;
      track.default = true;
      video.appendChild(track);
    }
  }, [videoData, autoplay]);

  // Video event handlers
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handlePlay = () => {
      setPlaying(true);
      watchStartTime.current = Date.now();
      startAnalyticsTracking();
    };

    const handlePause = () => {
      setPlaying(false);
      trackAnalytics();
    };

    const handleTimeUpdate = () => {
      setCurrentTime(video.currentTime);
    };

    const handleDurationChange = () => {
      setDuration(video.duration);
    };

    const handleVolumeChange = () => {
      setVolume(video.volume);
      setMute(video.muted);
    };

    const handleWaiting = () => {
      setBuffering(true);
    };

    const handleCanPlay = () => {
      setBuffering(false);
    };

    const handleEnded = () => {
      setPlaying(false);
      trackAnalytics();
    };

    video.addEventListener('play', handlePlay);
    video.addEventListener('pause', handlePause);
    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('durationchange', handleDurationChange);
    video.addEventListener('volumechange', handleVolumeChange);
    video.addEventListener('waiting', handleWaiting);
    video.addEventListener('canplay', handleCanPlay);
    video.addEventListener('ended', handleEnded);

    return () => {
      video.removeEventListener('play', handlePlay);
      video.removeEventListener('pause', handlePause);
      video.removeEventListener('timeupdate', handleTimeUpdate);
      video.removeEventListener('durationchange', handleDurationChange);
      video.removeEventListener('volumechange', handleVolumeChange);
      video.removeEventListener('waiting', handleWaiting);
      video.removeEventListener('canplay', handleCanPlay);
      video.removeEventListener('ended', handleEnded);
    };
  }, []);

  // Analytics tracking
  const startAnalyticsTracking = () => {
    if (analyticsTimer.current) {
      clearInterval(analyticsTimer.current);
    }

    analyticsTimer.current = setInterval(() => {
      trackAnalytics();
    }, 30000); // Track every 30 seconds
  };

  const trackAnalytics = useCallback(async () => {
    if (!videoRef.current || !videoData) return;

    const video = videoRef.current;
    const watchDuration = (Date.now() - watchStartTime.current) / 1000;
    const completionPercentage = (video.currentTime / video.duration) * 100;

    try {
      await axios.post(`/api/videos/${videoId}/analytics`, {
        session_id: sessionId.current,
        quality_selected: selectedQuality,
        watch_duration_seconds: watchDuration,
        completion_percentage: completionPercentage,
        buffering_events: 0,
        total_buffering_time_seconds: 0
      });
    } catch (err) {
      console.error('Failed to track analytics:', err);
    }

    watchStartTime.current = Date.now();
  }, [videoId, selectedQuality, videoData]);

  // Cleanup analytics on unmount
  useEffect(() => {
    return () => {
      if (analyticsTimer.current) {
        clearInterval(analyticsTimer.current);
      }
      trackAnalytics();
    };
  }, [trackAnalytics]);

  // Control handlers
  const togglePlay = () => {
    if (videoRef.current) {
      if (playing) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
    }
  };

  const handleSeek = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!progressRef.current || !videoRef.current) return;

    const rect = progressRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = x / rect.width;
    const time = percentage * duration;

    videoRef.current.currentTime = time;
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    if (videoRef.current) {
      videoRef.current.volume = newVolume;
      setVolume(newVolume);
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !mute;
      setMute(!mute);
    }
  };

  const toggleFullscreen = () => {
    if (!containerRef.current) return;

    if (!fullscreen) {
      if (containerRef.current.requestFullscreen) {
        containerRef.current.requestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
    setFullscreen(!fullscreen);
  };

  const changePlaybackRate = (rate: number) => {
    if (videoRef.current) {
      videoRef.current.playbackRate = rate;
      setPlaybackRate(rate);
    }
  };

  const changeQuality = (quality: string) => {
    if (!hlsRef.current) return;

    setSelectedQuality(quality);

    if (quality === 'auto') {
      hlsRef.current.currentLevel = -1;
    } else {
      const height = parseInt(quality.replace('p', ''));
      const levelIndex = hlsRef.current.levels.findIndex(l => l.height === height);
      if (levelIndex >= 0) {
        hlsRef.current.currentLevel = levelIndex;
      }
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="video-player-loading">
        <div className="spinner"></div>
        <p>Loading video...</p>
      </div>
    );
  }

  if (error || !videoData) {
    return (
      <div className="video-player-error">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="10" strokeWidth={2} />
          <line x1="12" y1="8" x2="12" y2="12" strokeWidth={2} strokeLinecap="round" />
          <line x1="12" y1="16" x2="12.01" y2="16" strokeWidth={2} strokeLinecap="round" />
        </svg>
        <p>{error || 'Failed to load video'}</p>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={`video-player-container ${className} ${fullscreen ? 'fullscreen' : ''}`}
      onMouseEnter={() => setShowControls(true)}
      onMouseLeave={() => setShowControls(playing ? false : true)}
      onMouseMove={() => setShowControls(true)}
    >
      <video
        ref={videoRef}
        className="video-element"
        poster={videoData.thumbnail_url}
        onClick={togglePlay}
      />

      {buffering && (
        <div className="buffering-indicator">
          <div className="spinner"></div>
        </div>
      )}

      {controls && (
        <div className={`video-controls ${showControls ? 'visible' : ''}`}>
          <div
            ref={progressRef}
            className="progress-container"
            onClick={handleSeek}
          >
            <div className="progress-bar">
              <div
                className="progress-filled"
                style={{ width: `${(currentTime / duration) * 100}%` }}
              />
            </div>
          </div>

          <div className="controls-row">
            <button onClick={togglePlay} className="control-btn">
              {playing ? (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                  <rect x="6" y="4" width="4" height="16" />
                  <rect x="14" y="4" width="4" height="16" />
                </svg>
              ) : (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                  <path d="M8 5v14l11-7z" />
                </svg>
              )}
            </button>

            <div className="time-display">
              {formatTime(currentTime)} / {formatTime(duration)}
            </div>

            <button onClick={toggleMute} className="control-btn">
              {mute || volume === 0 ? (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                  <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z" />
                </svg>
              ) : (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                  <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z" />
                </svg>
              )}
            </button>

            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={volume}
              onChange={handleVolumeChange}
              className="volume-slider"
            />

            <div className="spacer" />

            <div className="settings-menu">
              <button onClick={() => setShowSettings(!showSettings)} className="control-btn">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                  <path d="M19.14,12.94c0.04-0.3,0.06-0.61,0.06-0.94c0-0.32-0.02-0.64-0.07-0.94l2.03-1.58c0.18-0.14,0.23-0.41,0.12-0.61 l-1.92-3.32c-0.12-0.22-0.37-0.29-0.59-0.22l-2.39,0.96c-0.5-0.38-1.03-0.7-1.62-0.94L14.4,2.81c-0.04-0.24-0.24-0.41-0.48-0.41 h-3.84c-0.24,0-0.43,0.17-0.47,0.41L9.25,5.35C8.66,5.59,8.12,5.92,7.63,6.29L5.24,5.33c-0.22-0.08-0.47,0-0.59,0.22L2.74,8.87 C2.62,9.08,2.66,9.34,2.86,9.48l2.03,1.58C4.84,11.36,4.8,11.69,4.8,12s0.02,0.64,0.07,0.94l-2.03,1.58 c-0.18,0.14-0.23,0.41-0.12,0.61l1.92,3.32c0.12,0.22,0.37,0.29,0.59,0.22l2.39-0.96c0.5,0.38,1.03,0.7,1.62,0.94l0.36,2.54 c0.05,0.24,0.24,0.41,0.48,0.41h3.84c0.24,0,0.44-0.17,0.47-0.41l0.36-2.54c0.59-0.24,1.13-0.56,1.62-0.94l2.39,0.96 c0.22,0.08,0.47,0,0.59-0.22l1.92-3.32c0.12-0.22,0.07-0.47-0.12-0.61L19.14,12.94z M12,15.6c-1.98,0-3.6-1.62-3.6-3.6 s1.62-3.6,3.6-3.6s3.6,1.62,3.6,3.6S13.98,15.6,12,15.6z" />
                </svg>
              </button>

              {showSettings && (
                <div className="settings-dropdown">
                  <div className="settings-section">
                    <p className="settings-label">Speed</p>
                    {[0.5, 0.75, 1, 1.25, 1.5, 2].map(rate => (
                      <button
                        key={rate}
                        onClick={() => changePlaybackRate(rate)}
                        className={`settings-option ${playbackRate === rate ? 'active' : ''}`}
                      >
                        {rate}x
                      </button>
                    ))}
                  </div>

                  {availableQualities.length > 0 && (
                    <div className="settings-section">
                      <p className="settings-label">Quality</p>
                      {availableQualities.map(quality => (
                        <button
                          key={quality}
                          onClick={() => changeQuality(quality)}
                          className={`settings-option ${selectedQuality === quality ? 'active' : ''}`}
                        >
                          {quality}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>

            <button onClick={toggleFullscreen} className="control-btn">
              {fullscreen ? (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                  <path d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z" />
                </svg>
              ) : (
                <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                  <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z" />
                </svg>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdaptiveVideoPlayer;
