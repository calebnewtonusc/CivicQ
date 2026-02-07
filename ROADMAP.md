# CivicQ Development Roadmap

**Status**: MVP Deployed (Frontend on Vercel)
**Created**: February 2026
**Last Updated**: February 7, 2026

---

## Current State

- ✅ Frontend deployed to Vercel (static build working)
- ✅ Backend structure created (FastAPI + PostgreSQL + Redis)
- ✅ Database models defined (10+ SQLAlchemy models)
- ✅ Docker Compose configuration ready
- ⏳ Backend deployment pending (Railway recommended)
- ⏳ Full functionality pending (see roadmap below)

---

## Phase 1: Core Infrastructure (CRITICAL)

### 1.1 Database Setup
**Priority**: 🔴 CRITICAL
**Status**: Not Started

- [ ] Create initial Alembic migration
  ```bash
  cd backend
  alembic revision --autogenerate -m "Initial database schema"
  alembic upgrade head
  ```
- [ ] Test migration creates all tables correctly
- [ ] Add seed data script for development
- [ ] Verify pgvector extension is enabled in PostgreSQL

**Files to create**:
- `backend/database/migrations/versions/001_initial_schema.py`
- `backend/scripts/seed_data.py`

---

### 1.2 Celery Task Queue
**Priority**: 🔴 CRITICAL
**Status**: Not Started

- [ ] Create `backend/app/tasks.py` with Celery app configuration
- [ ] Implement video transcription task
- [ ] Implement embedding generation task
- [ ] Implement email notification task
- [ ] Configure Celery worker in Docker Compose
- [ ] Add Flower for task monitoring (optional)

**Files to create**:
- `backend/app/tasks.py`
- `backend/app/celery_app.py`

**Example structure**:
```python
# app/celery_app.py
from celery import Celery

celery_app = Celery(
    "civicq",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

# app/tasks.py
from app.celery_app import celery_app

@celery_app.task
def transcribe_video(video_id: int):
    # Implement transcription logic
    pass
```

---

### 1.3 Environment Configuration
**Priority**: 🟡 HIGH
**Status**: Partial

- [ ] Set up Railway database (PostgreSQL + Redis)
- [ ] Configure all required environment variables
  - `DATABASE_URL`
  - `REDIS_URL`
  - `JWT_SECRET_KEY`
  - `ALLOWED_ORIGINS` (Vercel URL)
- [ ] Add optional API keys for full functionality:
  - `OPENAI_API_KEY` (for Whisper transcription)
  - `DEEPGRAM_API_KEY` or `ASSEMBLYAI_API_KEY` (alternative transcription)
  - `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` (for S3 video storage)
  - `SMTP_*` variables (for email notifications)
  - `TWILIO_*` variables (for SMS verification)
- [ ] Connect Vercel frontend to Railway backend
  - Add `REACT_APP_API_URL` environment variable in Vercel

---

## Phase 2: Backend API Implementation (HIGH PRIORITY)

### 2.1 Authentication & User Management
**Priority**: 🟡 HIGH
**Status**: Stub endpoints exist

**Files**: `backend/app/api/auth.py`

- [ ] Implement `/signup` endpoint
  - Email validation
  - Password hashing (bcrypt)
  - Create user record
  - Send verification email
- [ ] Implement `/login` endpoint
  - Verify credentials
  - Generate JWT token
  - Return user data
- [ ] Implement `/verify/start` endpoint
  - Send verification code via email/SMS
  - Store verification token in Redis
- [ ] Implement `/verify/complete` endpoint
  - Validate verification code
  - Update user verification status
- [ ] Implement `/me` endpoint
  - Get current user from JWT
  - Return user profile

**Dependencies**:
- `passlib[bcrypt]` for password hashing
- `python-jose[cryptography]` for JWT
- Email service integration

---

### 2.2 Question System
**Priority**: 🟡 HIGH
**Status**: Stub endpoints exist

**Files**: `backend/app/api/questions.py`

- [ ] Implement question submission
  - Text validation
  - Duplicate detection (vector similarity)
  - Initial ranking score calculation
- [ ] Implement question clustering
  - Generate embeddings using sentence-transformers
  - Group similar questions
  - Merge duplicates with version tracking
- [ ] Implement question ranking algorithm
  - Anti-polarization scoring
  - Voter upvote integration
  - Demographic weighting
- [ ] Implement question search and filtering
- [ ] Add moderation queue integration

**Key algorithms to implement**:
```python
# Ranking formula from PRD
rank_score = (
    (upvotes * 0.4) +
    (demographic_diversity * 0.3) +
    (time_decay_factor * 0.2) +
    (question_quality_score * 0.1)
)
```

---

### 2.3 Ballot & Contest Management
**Priority**: 🟡 HIGH
**Status**: Stub endpoints exist

**Files**:
- `backend/app/api/ballots.py`
- `backend/app/api/contests.py`

- [ ] Implement ballot creation (admin only)
- [ ] Implement contest creation
- [ ] Link questions to contests
- [ ] Implement voter ballot retrieval by location
- [ ] Add ballot versioning system

---

### 2.4 Candidate Management
**Priority**: 🟡 HIGH
**Status**: Stub endpoints exist

**Files**: `backend/app/api/candidates.py`

- [ ] Implement candidate profile creation
- [ ] Implement video answer upload
  - S3/storage integration
  - Queue transcription task
  - Extract video metadata
- [ ] Implement video answer retrieval
- [ ] Implement candidate comparison endpoint
  - Side-by-side answer display
  - Provenance tracking

---

### 2.5 Moderation System
**Priority**: 🟠 MEDIUM
**Status**: Stub endpoints exist

**Files**: `backend/app/api/moderation.py`

- [ ] Implement moderation queue
- [ ] Implement approve/reject actions
- [ ] Add moderation analytics
- [ ] Implement flagging system for inappropriate content
- [ ] Add moderator assignment logic

---

### 2.6 Admin Dashboard API
**Priority**: 🟠 MEDIUM
**Status**: Stub endpoints exist

**Files**: `backend/app/api/admin.py`

- [ ] Implement analytics endpoints
- [ ] Implement user management
- [ ] Implement system health checks
- [ ] Add bulk operations for ballots/contests

---

## Phase 3: Frontend Implementation (HIGH PRIORITY)

### 3.1 API Service Layer
**Priority**: 🟡 HIGH
**Status**: Empty directory

**Files to create**:
- `frontend/src/services/api.ts` - Axios client setup
- `frontend/src/services/auth.ts` - Authentication API calls
- `frontend/src/services/questions.ts` - Question API calls
- `frontend/src/services/ballots.ts` - Ballot API calls
- `frontend/src/services/candidates.ts` - Candidate API calls

**Example structure**:
```typescript
// services/api.ts
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

---

### 3.2 TypeScript Type Definitions
**Priority**: 🟡 HIGH
**Status**: Empty directory

**Files to create**:
- `frontend/src/types/user.ts`
- `frontend/src/types/question.ts`
- `frontend/src/types/ballot.ts`
- `frontend/src/types/candidate.ts`
- `frontend/src/types/api.ts`

**Example**:
```typescript
// types/user.ts
export interface User {
  id: number;
  email: string;
  role: 'voter' | 'candidate' | 'moderator' | 'admin';
  verification_status: 'unverified' | 'pending' | 'verified';
  created_at: string;
}

// types/question.ts
export interface Question {
  id: number;
  question_text: string;
  submitter_id: number;
  contest_id: number;
  rank_score: number;
  upvote_count: number;
  created_at: string;
}
```

---

### 3.3 Shared UI Components
**Priority**: 🟠 MEDIUM
**Status**: Empty directory

**Files to create**:
- `frontend/src/components/ui/Button.tsx`
- `frontend/src/components/ui/Card.tsx`
- `frontend/src/components/ui/Input.tsx`
- `frontend/src/components/ui/Modal.tsx`
- `frontend/src/components/ui/Loading.tsx`
- `frontend/src/components/layout/Header.tsx`
- `frontend/src/components/layout/Navigation.tsx`
- `frontend/src/components/layout/Footer.tsx`

All components should use Tailwind CSS for styling.

---

### 3.4 Feature-Specific Components
**Priority**: 🟠 MEDIUM
**Status**: Empty directory

**Files to create**:
- `frontend/src/components/QuestionCard.tsx`
- `frontend/src/components/QuestionList.tsx`
- `frontend/src/components/QuestionSubmitForm.tsx`
- `frontend/src/components/CandidateCard.tsx`
- `frontend/src/components/VideoPlayer.tsx`
- `frontend/src/components/BallotView.tsx`
- `frontend/src/components/ContestOverview.tsx`
- `frontend/src/components/SideBySideComparison.tsx`

---

### 3.5 Page Implementation
**Priority**: 🟡 HIGH
**Status**: Placeholders exist

**Files to update**:
- `frontend/src/pages/HomePage.tsx` - Landing page (partially done)
- `frontend/src/pages/BallotPage.tsx` - User's ballot view
- `frontend/src/pages/ContestPage.tsx` - Contest details with questions
- `frontend/src/pages/QuestionPage.tsx` - Individual question view
- `frontend/src/pages/CandidatePage.tsx` - Candidate profile

**New files to create**:
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/pages/SignupPage.tsx`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/pages/SubmitQuestionPage.tsx`
- `frontend/src/pages/CompareCandidatesPage.tsx`

---

### 3.6 State Management & Utilities
**Priority**: 🟠 MEDIUM
**Status**: Empty directory

**Files to create**:
- `frontend/src/utils/auth.ts` - Token management, auth helpers
- `frontend/src/utils/formatters.ts` - Date formatting, text utils
- `frontend/src/utils/validators.ts` - Form validation
- `frontend/src/store/authStore.ts` - Zustand auth store
- `frontend/src/store/questionStore.ts` - Zustand question store

**Example**:
```typescript
// store/authStore.ts
import create from 'zustand';
import { User } from '@types/user';

interface AuthState {
  user: User | null;
  token: string | null;
  setUser: (user: User) => void;
  setToken: (token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  setUser: (user) => set({ user }),
  setToken: (token) => {
    localStorage.setItem('token', token);
    set({ token });
  },
  logout: () => {
    localStorage.removeItem('token');
    set({ user: null, token: null });
  },
}));
```

---

## Phase 4: Video & AI Features (MEDIUM PRIORITY)

### 4.1 Video Upload & Storage
**Priority**: 🟠 MEDIUM
**Status**: Not Started

- [ ] Set up S3 bucket (or alternative storage)
- [ ] Implement multipart upload endpoint
- [ ] Add video validation (format, size, duration)
- [ ] Generate video thumbnails
- [ ] Implement CDN integration for video delivery

**Files to create**:
- `backend/app/services/storage.py`

---

### 4.2 Video Transcription
**Priority**: 🟠 MEDIUM
**Status**: Not Started

- [ ] Implement OpenAI Whisper integration
- [ ] Add alternative providers (Deepgram/AssemblyAI)
- [ ] Create transcription task queue
- [ ] Store transcripts with timestamps
- [ ] Implement transcript search

**Files to create**:
- `backend/app/services/transcription.py`

---

### 4.3 Question Embeddings & Similarity
**Priority**: 🟠 MEDIUM
**Status**: Models support it, not implemented

- [ ] Set up sentence-transformers model
- [ ] Generate embeddings for new questions
- [ ] Implement vector similarity search (pgvector)
- [ ] Create clustering algorithm
- [ ] Add duplicate detection threshold

**Files to create**:
- `backend/app/services/embeddings.py`

---

## Phase 5: Production Readiness (MEDIUM PRIORITY)

### 5.1 Security Enhancements
**Priority**: 🟠 MEDIUM
**Status**: Basic setup done

- [ ] Add rate limiting to all endpoints (currently in main.py)
- [ ] Implement CSRF protection
- [ ] Add request validation with Pydantic
- [ ] Set up HTTPS (handled by Vercel/Railway)
- [ ] Implement input sanitization
- [ ] Add security headers (CORS, CSP, etc.)
- [ ] Set up API key rotation
- [ ] Add audit logging for sensitive operations

---

### 5.2 Testing
**Priority**: 🟠 MEDIUM
**Status**: Empty test directory

- [ ] Write backend unit tests (pytest)
  - Test all API endpoints
  - Test authentication flow
  - Test ranking algorithm
  - Test database models
- [ ] Write frontend unit tests (Jest/React Testing Library)
  - Test components
  - Test API services
  - Test state management
- [ ] Add integration tests
- [ ] Set up CI/CD pipeline (GitHub Actions)

**Files to create**:
- `backend/tests/test_auth.py`
- `backend/tests/test_questions.py`
- `backend/tests/test_ranking.py`
- `frontend/src/__tests__/components/`
- `.github/workflows/test.yml`

---

### 5.3 Monitoring & Logging
**Priority**: 🟢 LOW-MEDIUM
**Status**: Not Started

- [ ] Set up structured logging
- [ ] Add application monitoring (Sentry recommended)
- [ ] Implement performance tracking
- [ ] Set up database query monitoring
- [ ] Add error tracking and alerting
- [ ] Create health check endpoints

**Optional integrations**:
- Sentry for error tracking
- LogRocket for session replay
- DataDog or New Relic for APM

---

### 5.4 Performance Optimization
**Priority**: 🟢 LOW-MEDIUM
**Status**: Not Started

- [ ] Add database indexes
- [ ] Implement caching strategy (Redis)
- [ ] Optimize API responses (pagination, field selection)
- [ ] Add lazy loading for frontend
- [ ] Implement code splitting
- [ ] Optimize bundle size
- [ ] Add service worker for PWA

---

### 5.5 Documentation
**Priority**: 🟢 LOW-MEDIUM
**Status**: Deployment docs done

- [ ] Complete API documentation (OpenAPI/Swagger)
- [ ] Write developer setup guide
- [ ] Create user documentation
- [ ] Document deployment procedures
- [ ] Add architecture diagrams
- [ ] Create contribution guidelines

**Files to create**:
- `docs/API.md`
- `docs/ARCHITECTURE.md`
- `docs/DEVELOPMENT.md`
- `CONTRIBUTING.md`

---

## Phase 6: Advanced Features (LOW PRIORITY)

### 6.1 Email Notifications
**Priority**: 🟢 LOW
**Status**: Not Started

- [ ] Set up SMTP configuration
- [ ] Create email templates
- [ ] Implement verification emails
- [ ] Add new answer notifications
- [ ] Send weekly digest emails

---

### 6.2 SMS Verification (Optional)
**Priority**: 🟢 LOW
**Status**: Not Started

- [ ] Integrate Twilio
- [ ] Implement SMS verification flow
- [ ] Add phone number validation

---

### 6.3 Analytics Dashboard
**Priority**: 🟢 LOW
**Status**: Not Started

- [ ] Create admin analytics page
- [ ] Show question statistics
- [ ] Track user engagement
- [ ] Visualize demographic data
- [ ] Export reports

---

### 6.4 Mobile App (Future)
**Priority**: 🟢 LOW
**Status**: Not Started

- Consider React Native
- Share types/services with web app
- Push notifications for new answers

---

## Quick Start Checklist

To get CivicQ fully functional, complete these tasks in order:

1. ✅ Frontend deployed to Vercel (DONE)
2. [ ] Deploy backend to Railway
3. [ ] Create database migrations (`alembic revision --autogenerate`)
4. [ ] Implement Celery tasks
5. [ ] Implement authentication API (`/signup`, `/login`)
6. [ ] Create frontend API service layer
7. [ ] Implement question submission & ranking
8. [ ] Build ballot/contest pages
9. [ ] Add candidate video upload
10. [ ] Test end-to-end flow

---

## Priority Legend

- 🔴 **CRITICAL**: Must be done before MVP works
- 🟡 **HIGH**: Core functionality, needed for launch
- 🟠 **MEDIUM**: Important features, can be added after launch
- 🟢 **LOW**: Nice to have, future enhancements

---

## Notes

- All backend endpoints currently return stub responses
- Database schema is defined but migrations not created
- Frontend structure is complete but components/services empty
- Deployment infrastructure is ready but needs configuration

**Estimated effort**:
- Phase 1 (Critical): 2-3 days
- Phase 2 (Backend API): 1-2 weeks
- Phase 3 (Frontend): 1-2 weeks
- Phase 4 (AI Features): 3-5 days
- Phase 5 (Production): 1 week
- Phase 6 (Advanced): 2-4 weeks

**Total MVP (Phases 1-3)**: 3-4 weeks of development

---

For deployment instructions, see:
- [DEPLOYMENT_READY.md](DEPLOYMENT_READY.md) - Quick deploy guide
- [DEPLOY_MANUAL.md](DEPLOY_MANUAL.md) - Detailed deployment instructions
