# Video Infrastructure - Production Ready

## Overview

CivicQ now includes a **production-grade video infrastructure** that rivals YouTube in terms of quality and features. The system handles everything from upload to playback with professional-grade transcoding, adaptive streaming, and analytics.

## Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       │ 1. Request Upload URL
       ▼
┌─────────────────┐
│  FastAPI API    │
└────────┬────────┘
         │
         │ 2. Generate Presigned URL
         ▼
┌─────────────────┐      3. Direct Upload
│   S3/R2 CDN     │◄─────────────────────┐
└────────┬────────┘                      │
         │                               │
         │ 4. Upload Complete      ┌──────────┐
         ▼                         │ Browser  │
┌─────────────────┐               └──────────┘
│  Celery Queue   │
└────────┬────────┘
         │
         │ 5. Process Video
         ▼
┌─────────────────────────────────┐
│   Video Processing Pipeline     │
│                                 │
│  • Extract Metadata             │
│  • Transcode (1080p→240p)       │
│  • Generate HLS Streams         │
│  • Create Thumbnails            │
│  • Generate Sprite Sheets       │
│  • Extract Audio                │
│  • Transcribe with Whisper      │
│  • Generate Captions (VTT)      │
└────────┬────────────────────────┘
         │
         │ 6. Upload Processed Assets
         ▼
┌─────────────────┐
│   S3/R2 CDN     │
└────────┬────────┘
         │
         │ 7. Deliver via CDN
         ▼
┌─────────────────┐
│  Video Player   │
│  (Adaptive HLS) │
└─────────────────┘
```

## Features

### 1. Video Upload
- **Direct-to-S3 Upload**: No server bandwidth usage
- **Presigned URLs**: Secure, temporary upload URLs
- **Multipart Upload**: Support for files up to 5GB
- **Chunked Transfer**: Progress tracking and resume capability
- **Client Validation**: File type, size, and duration checks
- **Drag & Drop**: Modern upload interface

### 2. Video Processing
- **Automatic Transcoding**: Multiple quality levels (1080p, 720p, 480p, 360p, 240p)
- **HLS Streaming**: Adaptive bitrate streaming
- **Web Optimization**: Fast-start encoding for progressive download
- **Thumbnail Generation**: Main thumbnail + sprite sheets for scrubbing
- **Audio Extraction**: For transcription processing
- **Metadata Extraction**: Duration, resolution, codec, bitrate

### 3. Video Streaming
- **Adaptive Bitrate**: Automatic quality switching based on bandwidth
- **HLS Support**: Industry-standard HTTP Live Streaming
- **Quality Selection**: Manual quality override
- **Fallback Support**: Original video if HLS unavailable
- **CDN Delivery**: CloudFront or Cloudflare for global distribution

### 4. Transcription & Captions
- **Multiple Providers**:
  - OpenAI Whisper (API or local)
  - AWS Transcribe
  - Deepgram
  - AssemblyAI
- **WebVTT Format**: Standard caption format
- **Multi-language**: Automatic language detection
- **Time-synced**: Frame-accurate timestamps

### 5. Analytics
- **View Tracking**: Total views and watch time
- **Quality Metrics**: Quality distribution and buffering events
- **Completion Rate**: Average completion percentage
- **Session Tracking**: Individual viewing sessions
- **Engagement Metrics**: Pauses, seeks, quality changes

### 6. Video Player
- **Custom Controls**: Professional UI with modern design
- **Keyboard Shortcuts**: Space (play/pause), arrows (seek), M (mute), F (fullscreen)
- **Speed Control**: 0.5x to 2x playback speed
- **Picture-in-Picture**: PiP support
- **Closed Captions**: Toggle subtitles
- **Responsive**: Works on all screen sizes

## Setup Instructions

### Prerequisites

1. **FFmpeg**: Required for video processing
   ```bash
   # macOS
   brew install ffmpeg

   # Ubuntu/Debian
   sudo apt-get install ffmpeg

   # Verify installation
   ffmpeg -version
   ```

2. **Redis**: Required for Celery task queue
   ```bash
   # macOS
   brew install redis
   brew services start redis

   # Ubuntu/Debian
   sudo apt-get install redis-server
   sudo systemctl start redis
   ```

3. **S3-Compatible Storage**: AWS S3 or Cloudflare R2
   - Create a bucket for video storage
   - Generate access keys (Access Key ID and Secret Access Key)
   - Note the region and bucket name

### Environment Configuration

Add these variables to `/Users/joelnewton/Desktop/2026-Code/projects/CivicQ/backend/.env`:

```bash
# S3/Storage Configuration
S3_BUCKET=your-bucket-name
S3_REGION=us-east-1
S3_ACCESS_KEY=your-access-key-id
S3_SECRET_KEY=your-secret-access-key
S3_ENDPOINT=  # Optional: For Cloudflare R2 or other S3-compatible services

# CDN Configuration
CDN_URL=https://cdn.yourdomain.com  # CloudFront or Cloudflare CDN URL

# Video Processing
MAX_VIDEO_DURATION_SECONDS=180
VIDEO_TIME_LIMIT_COUNCIL=90
VIDEO_TIME_LIMIT_MAYOR=120
VIDEO_TIME_LIMIT_MEASURE=180

# Transcription Service (whisper, aws, deepgram, assemblyai)
TRANSCRIPTION_SERVICE=whisper
OPENAI_API_KEY=your-openai-api-key  # For Whisper API
DEEPGRAM_API_KEY=  # Optional: For Deepgram
ASSEMBLYAI_API_KEY=  # Optional: For AssemblyAI

# Celery (Task Queue)
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

### Backend Setup

1. **Install Dependencies**:
   ```bash
   cd /Users/joelnewton/Desktop/2026-Code/projects/CivicQ/backend
   pip install -r requirements.txt
   ```

2. **Run Database Migrations**:
   ```bash
   alembic upgrade head
   ```

3. **Start Celery Worker**:
   ```bash
   celery -A app.tasks.video_tasks worker --loglevel=info
   ```

4. **Start FastAPI Server**:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. **Install HLS.js**:
   ```bash
   cd /Users/joelnewton/Desktop/2026-Code/projects/CivicQ/frontend
   npm install hls.js
   ```

2. **Start Development Server**:
   ```bash
   npm start
   ```

## API Endpoints

### Upload Video

**POST** `/api/videos/upload/initiate`
```json
{
  "filename": "video.mp4",
  "content_type": "video/mp4",
  "file_size": 52428800,
  "answer_id": 123
}
```

Response:
```json
{
  "video_id": 456,
  "upload_url": "https://...",
  "upload_fields": {...},
  "key": "videos/1/20260214_abc123.mp4",
  "expires_in": 3600
}
```

### Complete Upload

**POST** `/api/videos/upload/{video_id}/complete`

Response:
```json
{
  "video_id": 456,
  "status": "uploaded",
  "message": "Video processing started"
}
```

### Get Video

**GET** `/api/videos/{video_id}`

Response:
```json
{
  "id": 456,
  "status": "ready",
  "metadata": {
    "duration_seconds": 120,
    "width": 1920,
    "height": 1080,
    "fps": 30
  },
  "streaming": {
    "has_hls": true,
    "hls_url": "https://cdn.yourdomain.com/videos/1/456/hls/master.m3u8",
    "available_qualities": ["720p", "480p", "360p"]
  },
  "transcription": {
    "has_captions": true,
    "captions_url": "https://cdn.yourdomain.com/videos/1/456/captions.vtt"
  },
  "thumbnail_url": "https://cdn.yourdomain.com/videos/1/456/thumbnail.jpg"
}
```

### Track Analytics

**POST** `/api/videos/{video_id}/analytics`
```json
{
  "session_id": "session_abc123",
  "quality_selected": "720p",
  "watch_duration_seconds": 45.5,
  "completion_percentage": 37.9,
  "buffering_events": 2,
  "total_buffering_time_seconds": 1.5
}
```

## Usage Examples

### Frontend: Upload Video

```tsx
import VideoUploader from './components/VideoUploader';

function MyComponent() {
  const handleUploadComplete = (videoId: number) => {
    console.log('Video uploaded:', videoId);
    // Redirect or show success message
  };

  return (
    <VideoUploader
      answerId={123}
      onUploadComplete={handleUploadComplete}
      maxSizeMB={500}
      maxDurationSeconds={180}
    />
  );
}
```

### Frontend: Play Video

```tsx
import AdaptiveVideoPlayer from './components/AdaptiveVideoPlayer';

function VideoPage() {
  return (
    <AdaptiveVideoPlayer
      videoId={456}
      autoplay={false}
      controls={true}
    />
  );
}
```

## CDN Configuration

### CloudFront (AWS)

1. **Create Distribution**:
   - Origin: Your S3 bucket
   - Origin Access Identity: Create new OAI
   - Cache Policy: CachingOptimized
   - Price Class: Use all edge locations

2. **Update Bucket Policy**:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "AWS": "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity YOUR_OAI_ID"
         },
         "Action": "s3:GetObject",
         "Resource": "arn:aws:s3:::your-bucket/*"
       }
     ]
   }
   ```

3. **Update `.env`**:
   ```bash
   CDN_URL=https://d1234abcd.cloudfront.net
   ```

### Cloudflare R2

1. **Create R2 Bucket**:
   - Go to Cloudflare Dashboard
   - Create R2 bucket
   - Enable public access or use custom domain

2. **Get Credentials**:
   - Create API token for R2
   - Get endpoint URL

3. **Update `.env`**:
   ```bash
   S3_BUCKET=your-r2-bucket
   S3_ENDPOINT=https://abc123.r2.cloudflarestorage.com
   S3_ACCESS_KEY=your-r2-access-key
   S3_SECRET_KEY=your-r2-secret-key
   CDN_URL=https://r2.yourdomain.com
   ```

## Storage Cost Optimization

### Tips for Cost Reduction

1. **Use Cloudflare R2**:
   - Zero egress fees (no bandwidth charges)
   - $0.015/GB/month storage
   - Significantly cheaper than S3

2. **Lifecycle Policies**:
   - Delete original videos after transcoding
   - Archive old videos to Glacier/Deep Archive
   - Set expiration for temporary uploads

3. **Smart Transcoding**:
   - Don't transcode to qualities higher than source
   - Skip similar quality levels (e.g., if source is 480p, don't create 720p)
   - Use efficient codecs (H.264 with CRF)

4. **CDN Caching**:
   - Long cache TTL for video files (1 year)
   - Enable compression for text files (VTT, M3U8)
   - Use edge caching for popular videos

## Performance Optimization

### Video Processing

1. **Parallel Processing**:
   - Celery processes transcoding, thumbnails, and transcription in parallel
   - Use multiple worker processes for faster processing

2. **Optimize FFmpeg**:
   - Use hardware acceleration if available
   - Tune preset (fast, medium, slow) based on needs
   - Use appropriate CRF value (23 is good balance)

3. **Queue Management**:
   - Priority queue for urgent processing
   - Separate queues for different video types
   - Retry failed jobs with exponential backoff

### Streaming Performance

1. **HLS Segment Size**:
   - 4-second segments for good balance
   - Shorter segments = faster quality switching
   - Longer segments = less overhead

2. **Quality Ladder**:
   - Provide enough quality levels (typically 3-4)
   - Don't create unnecessary qualities
   - Consider mobile-optimized streams (240p, 360p)

3. **Adaptive Bitrate**:
   - HLS.js handles automatic quality switching
   - Fallback to lower quality on slow connections
   - Preload buffer to prevent buffering

## Monitoring & Debugging

### Check Processing Status

```bash
# Check Celery workers
celery -A app.tasks.video_tasks inspect active

# Check Redis queue
redis-cli
> LLEN celery

# Check video processing logs
tail -f logs/video_processing.log
```

### Common Issues

1. **Upload Fails**:
   - Check S3 credentials and permissions
   - Verify bucket CORS configuration
   - Check file size limits

2. **Processing Fails**:
   - Verify FFmpeg is installed
   - Check Celery worker is running
   - Review error logs in video.processing_error

3. **Streaming Issues**:
   - Verify HLS files were created
   - Check CDN is serving files
   - Test with different browsers

## Security Considerations

1. **Presigned URLs**: Expire after 1 hour
2. **Upload Validation**: File type, size, and duration limits
3. **Access Control**: Only owners can view processing videos
4. **Content Moderation**: Can integrate with AWS Rekognition
5. **Rate Limiting**: Prevent upload spam

## Future Enhancements

- [ ] Live streaming support
- [ ] WebRTC for ultra-low latency
- [ ] 4K video support
- [ ] Multi-language audio tracks
- [ ] Chapter markers
- [ ] Video editing capabilities
- [ ] AI-powered highlights
- [ ] Social sharing with preview cards

## Cost Estimates

### Monthly Costs (1000 videos, 100 hours)

**Cloudflare R2**:
- Storage: 100 GB × $0.015 = $1.50
- Operations: ~$0.50
- **Total: ~$2/month**

**AWS S3 + CloudFront**:
- Storage: 100 GB × $0.023 = $2.30
- Data transfer: 500 GB × $0.085 = $42.50
- Requests: ~$0.50
- **Total: ~$45/month**

**OpenAI Whisper API**:
- 100 hours × $0.006/min = $36/month

**Recommendation**: Use Cloudflare R2 for storage and local Whisper for transcription to minimize costs.

## Support

For issues or questions:
- Check logs: `tail -f backend/logs/video.log`
- Review Celery status: `celery -A app.tasks.video_tasks inspect stats`
- Test upload: Use Postman or cURL to test API endpoints

---

**Built with**: FastAPI, Celery, FFmpeg, HLS.js, S3/R2, Redis
**License**: MIT
