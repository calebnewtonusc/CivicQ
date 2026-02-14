# Video Infrastructure - Quick Start Guide

Get the video infrastructure running in 15 minutes!

## Prerequisites

Install these tools first:

```bash
# 1. FFmpeg (for video processing)
brew install ffmpeg  # macOS
# OR
sudo apt-get install ffmpeg  # Ubuntu/Debian

# 2. Redis (for task queue)
brew install redis  # macOS
brew services start redis
# OR
sudo apt-get install redis-server  # Ubuntu/Debian
sudo systemctl start redis

# Verify installations
ffmpeg -version
redis-cli ping  # Should return "PONG"
```

## Step 1: Configure Storage (Cloudflare R2 - Recommended)

### Why Cloudflare R2?
- **Zero egress fees** (no bandwidth charges)
- **$0.015/GB/month** storage (cheaper than S3)
- **S3-compatible API** (works with boto3)

### Setup Instructions:

1. **Create R2 Bucket**:
   - Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
   - Navigate to R2 Storage
   - Create new bucket (e.g., "civicq-videos")

2. **Get API Credentials**:
   - In R2, go to "Manage R2 API Tokens"
   - Create API token with "Object Read & Write" permissions
   - Copy: Access Key ID, Secret Access Key, and Endpoint URL

3. **Update Backend .env**:
   ```bash
   cd /Users/joelnewton/Desktop/2026-Code/projects/CivicQ/backend
   nano .env
   ```

   Add these lines:
   ```bash
   # Cloudflare R2 Configuration
   S3_BUCKET=civicq-videos
   S3_REGION=auto
   S3_ACCESS_KEY=your-r2-access-key-id
   S3_SECRET_KEY=your-r2-secret-access-key
   S3_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com

   # Optional: Use custom domain for CDN
   CDN_URL=https://videos.yourdomain.com

   # Transcription (use Whisper API)
   TRANSCRIPTION_SERVICE=whisper
   OPENAI_API_KEY=your-openai-api-key

   # Redis for Celery
   CELERY_BROKER_URL=redis://localhost:6379/1
   CELERY_RESULT_BACKEND=redis://localhost:6379/1
   ```

## Step 2: Install Backend Dependencies

```bash
cd /Users/joelnewton/Desktop/2026-Code/projects/CivicQ/backend
pip install -r requirements.txt
```

## Step 3: Run Database Migration

```bash
cd /Users/joelnewton/Desktop/2026-Code/projects/CivicQ/backend

# Run migration to add video tables
alembic upgrade head
```

## Step 4: Start Services

Open **3 terminal windows**:

### Terminal 1: Redis (if not running as service)
```bash
redis-server
```

### Terminal 2: Celery Worker
```bash
cd /Users/joelnewton/Desktop/2026-Code/projects/CivicQ/backend
celery -A app.tasks.video_tasks worker --loglevel=info
```

You should see:
```
[tasks]
  . app.tasks.video_tasks.process_video
  . app.tasks.video_tasks.transcode_video
  . app.tasks.video_tasks.create_hls_stream
  . app.tasks.video_tasks.generate_thumbnails
  . app.tasks.video_tasks.transcribe_video

[2026-02-14 12:00:00,000: INFO/MainProcess] Connected to redis://localhost:6379/1
[2026-02-14 12:00:00,000: INFO/MainProcess] celery@hostname ready.
```

### Terminal 3: FastAPI Server
```bash
cd /Users/joelnewton/Desktop/2026-Code/projects/CivicQ/backend
uvicorn app.main:app --reload
```

Visit: http://localhost:8000/api/docs

## Step 5: Install Frontend Dependencies

```bash
cd /Users/joelnewton/Desktop/2026-Code/projects/CivicQ/frontend
npm install hls.js axios
npm start
```

## Step 6: Test Video Upload

### Option A: Use the UI

1. Navigate to your app in browser
2. Use the `VideoUploader` component
3. Drag & drop a video file
4. Click "Upload Video"
5. Watch the progress bar
6. Video processing will start automatically

### Option B: Test with cURL

```bash
# 1. Get upload URL
curl -X POST http://localhost:8000/api/videos/upload/initiate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "filename": "test.mp4",
    "content_type": "video/mp4",
    "file_size": 10485760
  }'

# Response will include upload_url and video_id

# 2. Upload file to S3 using presigned URL
# (Use the upload_url from response)

# 3. Complete upload
curl -X POST http://localhost:8000/api/videos/upload/{video_id}/complete \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 4. Check processing status
curl http://localhost:8000/api/videos/{video_id}/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Step 7: Monitor Processing

### Check Celery Logs
In Terminal 2, you'll see processing logs:
```
[2026-02-14 12:05:00] INFO: Starting video processing: video_id=123
[2026-02-14 12:05:05] INFO: Transcoding to 720p: /tmp/video.mp4
[2026-02-14 12:05:45] INFO: Generating thumbnails: video_id=123
[2026-02-14 12:06:00] INFO: Transcribing video: video_id=123
[2026-02-14 12:06:30] INFO: Video processing complete: video_id=123
```

### Check Video Status
```bash
curl http://localhost:8000/api/videos/123 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Response when ready:
```json
{
  "id": 123,
  "status": "ready",
  "streaming": {
    "has_hls": true,
    "hls_url": "https://your-r2-bucket.r2.cloudflarestorage.com/videos/1/123/hls/master.m3u8",
    "available_qualities": ["720p", "480p", "360p"]
  },
  "thumbnail_url": "https://your-r2-bucket.r2.cloudflarestorage.com/videos/1/123/thumbnail.jpg",
  "transcription": {
    "has_captions": true,
    "captions_url": "https://your-r2-bucket.r2.cloudflarestorage.com/videos/1/123/captions.vtt"
  }
}
```

## Step 8: Play Video

Use the `AdaptiveVideoPlayer` component:

```tsx
import AdaptiveVideoPlayer from './components/AdaptiveVideoPlayer';

function MyPage() {
  return (
    <div>
      <h1>Watch Video</h1>
      <AdaptiveVideoPlayer videoId={123} />
    </div>
  );
}
```

Features:
- Adaptive quality switching
- Playback speed control (0.5x - 2x)
- Closed captions
- Fullscreen
- Keyboard shortcuts
- Analytics tracking

## Troubleshooting

### Video Upload Fails

**Error**: "Access Denied"
- Check S3 credentials in `.env`
- Verify bucket permissions
- Ensure CORS is configured on bucket

**Error**: "File too large"
- Check `MAX_VIDEO_DURATION_SECONDS` in config
- For files > 100MB, multipart upload is used automatically

### Processing Fails

**Check Celery Worker**:
```bash
# In Terminal 2, look for errors
# Common issues:

# FFmpeg not found
ERROR: ffmpeg: command not found
# Solution: Install ffmpeg (see Prerequisites)

# Redis not running
ERROR: [Errno 111] Connection refused
# Solution: Start Redis (redis-server)

# Missing OpenAI API key
ERROR: No API key provided
# Solution: Add OPENAI_API_KEY to .env
```

**Check Video Processing Error**:
```bash
curl http://localhost:8000/api/videos/123 | jq '.processing_error'
```

### Player Not Working

**HLS Not Loading**:
- Check browser console for errors
- Verify HLS URL is accessible
- Test HLS URL directly in browser
- Safari has native HLS support
- Chrome/Firefox need hls.js

**No Captions**:
- Check if transcription completed
- Verify OPENAI_API_KEY is set
- Check Celery logs for transcription errors

## Performance Tips

### Optimize Processing Speed

1. **Use Multiple Workers**:
   ```bash
   celery -A app.tasks.video_tasks worker --concurrency=4
   ```

2. **Hardware Acceleration** (if available):
   Update `video_processing_service.py` to use GPU:
   ```python
   # Add to transcode_video()
   '-hwaccel', 'videotoolbox',  # macOS
   # OR
   '-hwaccel', 'cuda',  # NVIDIA GPU
   ```

3. **Skip High Resolutions**:
   Reduce qualities in `transcode_video()` for faster processing

### Reduce Costs

1. **Use Cloudflare R2** instead of S3 (saves $40-50/month per 500GB)

2. **Delete Original After Processing**:
   ```python
   # In video_tasks.py, after transcoding
   storage_service.delete_object(video.original_key)
   ```

3. **Use Local Whisper** instead of API:
   ```bash
   # Install whisper locally
   pip install openai-whisper

   # Update .env
   TRANSCRIPTION_SERVICE=whisper-local
   ```

## Next Steps

1. **Set up CDN** for faster delivery (see VIDEO_INFRASTRUCTURE.md)
2. **Configure monitoring** with Sentry
3. **Add content moderation** with AWS Rekognition
4. **Optimize quality ladder** based on your audience
5. **Set up backup** and disaster recovery

## Support

- **Logs**: `tail -f backend/logs/video.log`
- **Celery Status**: `celery -A app.tasks.video_tasks inspect stats`
- **Redis Status**: `redis-cli info`
- **Full Docs**: See [VIDEO_INFRASTRUCTURE.md](/Users/joelnewton/Desktop/2026-Code/projects/CivicQ/VIDEO_INFRASTRUCTURE.md)

---

That's it! You now have a production-ready video infrastructure. Upload a video and watch it get automatically transcoded, captioned, and delivered with adaptive streaming.
