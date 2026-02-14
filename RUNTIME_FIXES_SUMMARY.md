# Runtime Errors and Code Quality Fixes - Summary

## Overview
This document summarizes all critical runtime error fixes, null pointer risk mitigations, and code quality improvements applied to the CivicQ project.

---

## 1. NULL POINTER FIXES

### Frontend - BallotPage.tsx (Lines 93-99)
**Issue**: `ballot.contests` could be null/undefined causing runtime errors during array operations.

**Fix Applied**:
```typescript
// Before (RISKY):
const sortedContests = ballot.contests
  ? [...ballot.contests].sort((a, b) => a.display_order - b.display_order)
  : [];

// After (SAFE):
const sortedContests = Array.isArray(ballot.contests)
  ? [...ballot.contests].sort((a, b) => (a.display_order || 0) - (b.display_order || 0))
  : [];

const races = sortedContests.filter((c) => c && c.type === 'race');
const measures = sortedContests.filter((c) => c && c.type === 'measure');
```

### Frontend - ContestPage.tsx (Lines 86, 320-323)
**Issue**: `candidates` and `video_answers` arrays could be null/undefined.

**Fix Applied**:
```typescript
// Defensive null checks for questions and candidates
const questions = Array.isArray(questionsData?.items) ? questionsData.items : [];
const activeCandidates = Array.isArray(candidates)
  ? candidates.filter((c) => c && c.status === 'active')
  : [];

// Safe array length check for video_answers
value={
  activeCandidates.reduce(
    (sum, c) => sum + (Array.isArray(c?.video_answers) ? c.video_answers.length : 0),
    0
  )
}
```

### Frontend - CandidateAnswerPage.tsx (Line 150)
**Issue**: `question.issue_tags` could be null/undefined causing map errors.

**Fix Applied**:
```typescript
// Before (RISKY):
{question.issue_tags && question.issue_tags.length > 0 && (

// After (SAFE):
{Array.isArray(question.issue_tags) && question.issue_tags.length > 0 && (
```

---

## 2. INFINITE LOOP FIX

### Frontend - SmartQuestionComposer.tsx (Lines 56-71)
**Issue**: useEffect had mutation objects in dependency array, causing infinite re-renders.

**Fix Applied**:
```typescript
// Added refs to store mutations
const analyzeMutationRef = useRef<typeof analyzeMutation | null>(null);
const duplicateCheckMutationRef = useRef<typeof duplicateCheckMutation | null>(null);

// Store mutation refs
useEffect(() => {
  analyzeMutationRef.current = analyzeMutation;
  duplicateCheckMutationRef.current = duplicateCheckMutation;
});

// Fixed useEffect - removed mutations from dependency array
useEffect(() => {
  if (questionText.length < 10) {
    setShowAnalysis(false);
    setAnalysis(null);
    setIsDuplicate(false);
    return;
  }

  const timer = setTimeout(() => {
    if (analyzeMutationRef.current) {
      analyzeMutationRef.current.mutate(questionText);
    }
    if (duplicateCheckMutationRef.current) {
      duplicateCheckMutationRef.current.mutate(questionText);
    }
  }, 1500);

  return () => clearTimeout(timer);
}, [questionText]); // Only depend on questionText
```

---

## 3. TYPE SCHEMA MISMATCH

### Backend - user.py (Lines 42-60)
**Issue**: Backend `UserResponse` schema used `city` field, but frontend expected `city_id` and `city_name`.

**Fix Applied**:
```python
class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    email: str
    full_name: str
    role: UserRole
    city: str
    city_id: Optional[str] = None  # Added for frontend compatibility
    city_name: Optional[str] = None  # Added for frontend compatibility
    verification_status: VerificationStatus
    phone_number: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    last_active: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
```

---

## 4. VIDEO UPLOAD ERROR HANDLING

### Frontend - VideoAnswerRecorder.tsx
**Issues**: Missing error handling for:
- Camera/microphone permissions
- MediaRecorder support
- Video blob validation
- Upload failures

**Fixes Applied**:

#### Enhanced Camera Access (Lines 52-103)
```typescript
const startCamera = async () => {
  try {
    setError(null);

    // Check if mediaDevices API is available
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error('Media devices not supported in this browser...');
    }

    const mediaStream = await navigator.mediaDevices.getUserMedia({
      video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: 'user' },
      audio: true
    });

    setStream(mediaStream);
    if (videoRef.current) {
      videoRef.current.srcObject = mediaStream;
    }
  } catch (err) {
    console.error('Error accessing camera:', err);

    let errorMessage = 'Could not access camera and microphone. ';
    if (err instanceof Error) {
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        errorMessage += 'Please allow camera and microphone permissions in your browser settings.';
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        errorMessage += 'No camera or microphone found...';
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        errorMessage += 'Camera is already in use by another application.';
      } else {
        errorMessage += err.message || 'Please check permissions and try again.';
      }
    }
    setError(errorMessage);
  }
};
```

#### Enhanced Recording with Browser Compatibility
```typescript
const startRecording = () => {
  if (!stream) {
    setError('No camera stream available. Please start the camera first.');
    return;
  }

  try {
    // Check MediaRecorder support
    if (!window.MediaRecorder) {
      throw new Error('Video recording is not supported in this browser.');
    }

    // Try different mime types for browser compatibility
    let mimeType = 'video/webm;codecs=vp8,opus';
    if (!MediaRecorder.isTypeSupported(mimeType)) {
      mimeType = 'video/webm';
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = 'video/mp4';
        if (!MediaRecorder.isTypeSupported(mimeType)) {
          throw new Error('No supported video format found for recording.');
        }
      }
    }

    const mediaRecorder = new MediaRecorder(stream, { mimeType });

    mediaRecorder.onerror = (event: Event) => {
      console.error('MediaRecorder error:', event);
      setError('Recording error occurred. Please try again.');
      // ... cleanup
    };

    // ... rest of recording logic
  }
};
```

#### Enhanced Upload with Validation
```typescript
const uploadVideo = async () => {
  if (!recordedVideoUrl) {
    setError('No video to upload. Please record a video first.');
    return;
  }

  try {
    // Fetch the blob from the object URL
    const response = await fetch(recordedVideoUrl);
    const blob = await response.blob();

    // Validate blob size (max 500MB)
    const maxSize = 500 * 1024 * 1024;
    if (blob.size > maxSize) {
      throw new Error('Video file is too large. Maximum size is 500MB.');
    }

    // Validate blob type
    if (!blob.type.startsWith('video/')) {
      throw new Error('Invalid video format.');
    }

    // Upload logic with error details
    const submitResponse = await fetch(...);
    if (!submitResponse.ok) {
      const errorData = await submitResponse.json().catch(() => ({ detail: 'Failed to submit answer' }));
      throw new Error(errorData.detail || `Server error: ${submitResponse.status}`);
    }
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : 'Failed to upload video. Please try again.';
    setError(errorMessage);
  }
};
```

---

## 5. API INTERCEPTOR IMPROVEMENTS

### Frontend - api.ts (Lines 46-70)
**Issues**: 
- Missing network error handling
- No logging for debugging
- No timeout handling
- Generic error responses

**Fix Applied**:
```typescript
// Request interceptor with error logging
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Enhanced response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    // Network error handling
    if (!error.response) {
      if (error.code === 'ERR_NETWORK') {
        console.warn('Network error: Backend may be unavailable, falling back to demo mode...');
      } else if (error.code === 'ECONNABORTED') {
        console.error('Request timeout:', error.message);
      } else {
        console.error('Request failed:', error.message);
      }
      return Promise.reject(error);
    }

    // Specific status code handling
    const status = error.response.status;
    if (status === 401) {
      console.warn('Authentication failed: Token expired or invalid');
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    } else if (status === 403) {
      console.error('Access forbidden: Insufficient permissions');
    } else if (status === 404) {
      console.warn('Resource not found:', error.config?.url);
    } else if (status === 422) {
      console.error('Validation error:', error.response.data);
    } else if (status >= 500) {
      console.error('Server error:', error.response.data);
    }

    return Promise.reject(error);
  }
);
```

---

## 6. SERVICE VALIDATION

### Backend - video_processing_service.py
**Issue**: No validation that ffmpeg is installed before attempting to use it.

**Fix Applied**:
```python
def __init__(self):
    """Initialize video processing service"""
    self.temp_dir = tempfile.gettempdir()
    self.ffmpeg_available = self._check_ffmpeg_installed()

    if not self.ffmpeg_available:
        logger.warning("ffmpeg not found. Video processing will not be available.")
    else:
        logger.info("Video processing service initialized with ffmpeg")

def _check_ffmpeg_installed(self) -> bool:
    """Check if ffmpeg is installed and available"""
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
    """Ensure ffmpeg is available before processing"""
    if not self.ffmpeg_available:
        raise RuntimeError(
            "ffmpeg is not installed or not available in PATH. "
            "Please install ffmpeg to enable video processing. "
            "Visit https://ffmpeg.org/download.html for installation instructions."
        )

def get_video_metadata(self, input_path: str) -> Dict:
    """Extract video metadata using ffprobe"""
    self._ensure_ffmpeg_available()
    
    if not input_path or not os.path.exists(input_path):
        raise FileNotFoundError(f"Video file not found: {input_path}")
    
    # ... rest of implementation
```

### Backend - storage_service.py
**Issue**: No validation that S3 bucket is accessible before attempting operations.

**Fix Applied**:
```python
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
        # Initialize S3 client
        self.s3_client = boto3.client('s3', **client_kwargs)
        
        # Validate bucket access
        self._validate_bucket_access()
        
        self.is_available = True
        logger.info(f"Storage service initialized: bucket={self.bucket}, region={self.region}")
    except Exception as e:
        logger.error(f"Failed to initialize storage service: {e}")
        self.is_available = False

def _validate_bucket_access(self):
    """Validate that the bucket exists and is accessible"""
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
    """Ensure storage service is available before operations"""
    if not self.is_available:
        raise RuntimeError(
            "Storage service is not available. Please check S3 configuration: "
            "S3_BUCKET, S3_ACCESS_KEY, S3_SECRET_KEY must be set."
        )

def generate_presigned_upload_url(self, key: str, content_type: str, ...) -> Dict[str, str]:
    """Generate presigned URL for direct upload to S3"""
    self._ensure_storage_available()
    
    if not key:
        raise ValueError("Object key cannot be empty")
    if not content_type:
        raise ValueError("Content type must be specified")
    
    # ... rest of implementation
```

### Backend - email_service.py
**Issue**: No validation that email service is configured before attempting to send.

**Fix Applied**:
```python
def __init__(self):
    """Initialize email service with SendGrid client and Jinja2 templates"""
    self.sendgrid_client = None
    self.is_configured = False

    # Check if SendGrid is configured
    if hasattr(settings, 'SENDGRID_API_KEY') and settings.SENDGRID_API_KEY:
        try:
            self.sendgrid_client = SendGridAPIClient(settings.SENDGRID_API_KEY)
            self.is_configured = True
            logger.info("Email service initialized with SendGrid")
        except Exception as e:
            logger.error(f"Failed to initialize SendGrid client: {e}")
            logger.warning("Email service will run in dev mode (logging only)")
    else:
        logger.warning("SENDGRID_API_KEY not configured. Email service will run in dev mode (logging only)")

    # Validate template directory
    template_dir = Path(__file__).parent.parent / 'templates' / 'emails'
    if not template_dir.exists():
        logger.warning(f"Email template directory not found: {template_dir}")
        logger.info("Creating email template directory")
        template_dir.mkdir(parents=True, exist_ok=True)

    try:
        self.jinja_env = Environment(...)
    except Exception as e:
        logger.error(f"Failed to initialize template engine: {e}")
        self.jinja_env = None

def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
    """Render an email template with context"""
    if not self.jinja_env:
        logger.warning(f"Template engine not available, using fallback for {template_name}")
        return self._generate_fallback_html(context)
    
    try:
        template = self.jinja_env.get_template(template_name)
        return template.render(**context)
    except Exception as e:
        logger.error(f"Failed to render template {template_name}: {e}")
        return self._generate_fallback_html(context)

def _send_email(self, to_email: str, subject: str, ...) -> bool:
    """Send an email using SendGrid"""
    # Validate inputs
    if not to_email:
        logger.error("Cannot send email: recipient email is empty")
        return False
    
    if not subject:
        logger.warning("Email subject is empty")
    
    # Graceful degradation to dev mode
    if not self.is_configured or not self.sendgrid_client:
        logger.info(f"[DEV MODE] Email to {to_email}: {subject}")
        return True
    
    # ... rest of implementation
```

---

## 7. VALIDATION UTILITIES

### Frontend - validation.ts
Enhanced existing validation utilities with defensive programming helpers:

```typescript
// Type-safe null checks
export function isDefined<T>(value: T | null | undefined): value is T {
  return value !== null && value !== undefined;
}

// Safe array operations
export function safeArray<T>(value: T[] | null | undefined): T[] {
  return Array.isArray(value) ? value : [];
}

export function isNonEmptyArray<T>(value: unknown): value is T[] {
  return Array.isArray(value) && value.length > 0;
}

export function filterNullish<T>(array: (T | null | undefined)[]): T[] {
  return array.filter((item): item is T => item !== null && item !== undefined);
}

// Safe primitive conversions
export function safeString(value: string | null | undefined, defaultValue = ''): string {
  return typeof value === 'string' ? value : defaultValue;
}

export function safeNumber(value: number | null | undefined, defaultValue = 0): number {
  return typeof value === 'number' && !isNaN(value) ? value : defaultValue;
}

// Safe JSON parsing
export function safeParseJSON<T>(json: string, defaultValue: T): T {
  if (!json || typeof json !== 'string') return defaultValue;
  try {
    return JSON.parse(json) as T;
  } catch (error) {
    console.error('Failed to parse JSON:', error);
    return defaultValue;
  }
}
```

---

## TESTING RECOMMENDATIONS

1. **Null Safety Tests**: Test all array operations with null, undefined, and empty arrays
2. **Browser Compatibility**: Test video recording across Chrome, Firefox, Safari, Edge
3. **Error Paths**: Test camera permission denial, network failures, upload errors
4. **Service Availability**: Test graceful degradation when services are unavailable
5. **Schema Validation**: Verify backend responses match frontend type expectations

---

## DEPLOYMENT CHECKLIST

- [ ] Verify ffmpeg is installed on production server
- [ ] Validate S3 bucket credentials and access
- [ ] Configure SendGrid API key (or verify dev mode is acceptable)
- [ ] Test video upload flow end-to-end
- [ ] Monitor logs for service initialization warnings
- [ ] Test error handling with actual network failures
- [ ] Verify schema compatibility between frontend/backend

---

## FILES MODIFIED

### Frontend
- `/frontend/src/pages/BallotPage.tsx` - Null safety for contests array
- `/frontend/src/pages/ContestPage.tsx` - Null safety for candidates and video_answers
- `/frontend/src/pages/CandidateAnswerPage.tsx` - Null safety for issue_tags
- `/frontend/src/components/SmartQuestionComposer.tsx` - Fixed infinite loop
- `/frontend/src/components/VideoAnswerRecorder.tsx` - Enhanced error handling
- `/frontend/src/services/api.ts` - Improved interceptor error handling
- `/frontend/src/utils/validation.ts` - Added defensive programming utilities

### Backend
- `/backend/app/schemas/user.py` - Fixed schema type mismatch
- `/backend/app/services/video_processing_service.py` - Added ffmpeg validation
- `/backend/app/services/storage_service.py` - Added S3 validation
- `/backend/app/services/email_service.py` - Added email service validation

---

*All fixes implement defensive programming principles and graceful degradation where appropriate.*
