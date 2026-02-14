# CivicQ Technical Architecture

**Status:** FOUNDATIONAL - System Design
**Owner:** Engineering Team
**Last Updated:** 2026-02-14

---

## Overview

CivicQ is designed as a **multi-tenant civic infrastructure platform** that enables cities to deploy transparent, verifiable candidate Q&A systems for local elections. The architecture prioritizes security, transparency, scalability, and anti-manipulation design.

**Core Design Thesis:**
CivicQ succeeds by being a **boring, auditable, trustworthy** piece of civic infrastructure—not a viral social media platform. Every architectural decision is evaluated against three criteria:
1. Does it prevent manipulation?
2. Is it transparent and auditable?
3. Can election officials trust it?

This document defines the complete technical architecture from data models to deployment infrastructure.

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│  Voter Web App  │  Candidate Portal  │  Admin Console          │
│  (React + TS)   │  (React + TS)      │  (React + TS)           │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│  • Authentication & Authorization (JWT)                         │
│  • Rate Limiting & DDoS Protection                              │
│  • Request Validation & Sanitization                            │
│  • CORS & Security Headers                                      │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│                    FastAPI Backend (Python)                     │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐ │
│  │ Ballot API   │ Question API │ Answer API   │ User API     │ │
│  ├──────────────┼──────────────┼──────────────┼──────────────┤ │
│  │ Ranking      │ Verification │ Moderation   │ Analytics    │ │
│  │ Engine       │ Service      │ Service      │ Service      │ │
│  └──────────────┴──────────────┴──────────────┴──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌───────────────┐  ┌──────────────┐  ┌──────────────────┐
│  PostgreSQL   │  │    Redis     │  │  Media Storage   │
│  (+ pgvector) │  │   (Cache)    │  │   (S3/Blob)      │
│  Primary DB   │  │  Session Mgmt│  │  Video/Images    │
└───────────────┘  └──────────────┘  └──────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKGROUND JOBS                             │
├─────────────────────────────────────────────────────────────────┤
│  Celery Workers (Python)                                        │
│  • Video Transcoding                                            │
│  • Speech-to-Text (Whisper / Deepgram)                          │
│  • Question Clustering (Embeddings)                             │
│  • Anomaly Detection (Voting Patterns)                          │
│  • Email/SMS Notifications                                      │
└─────────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. Voter Web Application
**Technology:** React 18 + TypeScript + React Router
**Purpose:** Public-facing interface for voters to view ballots, watch videos, submit/rank questions

**Key Screens:**
- Home: Personalized ballot based on address
- Contest: Race or ballot measure details with candidates
- Question: Individual question with all candidate answers
- Compare: Side-by-side candidate comparison
- Submit: Question submission with duplicate detection
- Profile: User verification status and preferences

**State Management:** React Context + React Query for server state
**Styling:** Tailwind CSS for utility-first styling
**Accessibility:** WCAG 2.1 AA compliant from day one

#### 2. Candidate Portal
**Technology:** React 18 + TypeScript
**Purpose:** Candidate-facing interface for identity verification, video recording, answer management

**Key Features:**
- Identity verification flow (multi-step)
- In-app video recording (MediaRecorder API)
- Question queue with priorities
- Answer review and transcript correction
- Source attachment for claims
- Performance analytics (views, engagement)

**Security:**
- Separate authentication context from voter app
- Additional verification layers (candidate filing ID)
- Video signing and provenance tracking
- Audit logs for all actions

#### 3. Admin Console
**Technology:** React 18 + TypeScript
**Purpose:** City staff dashboard for moderation, reporting, configuration

**Key Features:**
- Moderation queue for questions and answers
- Anomaly detection alerts
- User verification management
- Question merging and editing
- Reporting and analytics
- System configuration (verification methods, ranking weights)
- Audit log viewer

**Access Control:** Role-based (admin, moderator, read-only)

#### 4. API Backend
**Technology:** FastAPI (Python 3.11+) + SQLAlchemy + Pydantic
**Purpose:** Core business logic, data persistence, authentication

**API Design Principles:**
- RESTful where appropriate, RPC for complex operations
- OpenAPI documentation auto-generated
- Versioned API (v1, v2, etc.)
- Consistent error responses
- Pagination for all list endpoints
- Field filtering and sparse responses

**Key Services:**

**Ballot Service:**
- CRUD for cities, districts, contests, candidates
- Geocoding and district lookup
- Ballot generation for voter address

**Question Service:**
- Question submission with validation
- Duplicate detection using embeddings
- Question versioning
- Merging and moderation

**Ranking Service:**
- Portfolio-based ranking algorithm
- Viewpoint clustering
- Anomaly detection
- Rate limiting and fraud prevention

**Answer Service:**
- Video upload and metadata storage
- Transcoding job initiation
- Transcript generation and correction
- Source attachment management

**Verification Service:**
- Modular verification adapters (email, SMS, ID.me, civic ID)
- Verification status tracking
- Audit logging

**Moderation Service:**
- Automated content screening
- Human moderation queue
- Escalation workflows
- Appeal handling

**Analytics Service:**
- Engagement metrics (views, votes, completions)
- Coverage metrics (questions answered per candidate)
- Trust metrics (platform trust score)
- Exportable reports for election officials

#### 5. Database Layer
**Technology:** PostgreSQL 15+ with pgvector extension

**Key Tables:**
- `cities`: City configurations
- `districts`: Geographic boundaries (JSON/GeoJSON)
- `contests`: Races and ballot measures
- `candidates`: Candidate profiles
- `questions`: Submitted questions with versioning
- `answers`: Video answers with metadata
- `votes`: Question rankings (encrypted voter ID)
- `users`: Voter accounts
- `candidate_users`: Candidate accounts
- `admin_users`: Admin accounts
- `verification_records`: Verification audit trail
- `moderation_queue`: Pending moderation items
- `audit_logs`: All critical operations

**Indexes:**
- Full-text search on questions (PostgreSQL FTS)
- Vector similarity search on question embeddings (pgvector)
- Geographic indexes on district boundaries
- Composite indexes on foreign keys and frequent queries

**Data Retention:**
- Questions: Permanent (versioned)
- Answers: Permanent (election public record)
- Votes: Permanent (anonymized after ranking stabilizes)
- User PII: Deleted after election + 90 days (configurable)
- Audit logs: 7 years (compliance requirement)

#### 6. Caching Layer
**Technology:** Redis

**Use Cases:**
- Session storage (JWT tokens, CSRF tokens)
- Rate limiting counters
- Ranking algorithm cache (top 100 questions)
- Frequently accessed data (ballot info, candidate profiles)
- Celery task queue and results backend

**TTL Policies:**
- Sessions: 7 days
- Rate limits: 1 hour rolling window
- Rankings: 15 minutes (updates every 15 min during active periods)
- Static data: 1 hour

#### 7. Media Pipeline
**Technology:** Celery + FFmpeg + Whisper/Deepgram + S3/CloudStorage

**Video Processing Flow:**
```
1. Candidate records video in browser (MediaRecorder API)
2. Upload to presigned S3 URL (direct to storage, not through backend)
3. S3 event triggers Celery task
4. Celery worker:
   a. Validates video (duration, format, resolution)
   b. Generates cryptographic signature
   c. Transcodes to multiple formats (HLS, MP4 480p/720p/1080p)
   d. Extracts audio for transcription
   e. Generates captions (Whisper or Deepgram)
   f. Creates thumbnail and preview clips
   g. Stores all outputs in CDN-backed storage
5. Updates database with video metadata and status
6. Notifies candidate of completion
```

**Provenance Tracking:**
- Every video has SHA-256 hash stored at upload
- Metadata includes: recording timestamp, device info, IP (hashed), candidate ID
- Tampering detection: re-hash on every access, compare to original
- Audit trail: who accessed, when, what action

**Storage:**
- Original videos: Glacier Deep Archive (long-term retention, low cost)
- Transcoded videos: S3 Standard + CloudFront CDN
- Captions: Database (VTT format)

#### 8. Background Job System
**Technology:** Celery with Redis broker/backend

**Job Types:**

**Video Processing Jobs:**
- `transcode_video(video_id)`: Transcode to multiple formats
- `generate_captions(video_id)`: Speech-to-text transcription
- `extract_thumbnail(video_id)`: Generate video thumbnail

**Ranking Jobs:**
- `update_question_rankings(city_id)`: Recalculate top questions
- `detect_voting_anomalies(city_id)`: Check for coordinated voting
- `cluster_questions(city_id)`: Group similar questions

**Notification Jobs:**
- `send_verification_email(user_id)`: Email verification
- `send_answer_notification(candidate_id, question_id)`: Notify of new questions
- `send_moderation_alert(admin_id, item_id)`: Alert moderators

**Maintenance Jobs:**
- `cleanup_expired_sessions()`: Remove old sessions
- `archive_old_videos()`: Move to cold storage
- `generate_daily_reports()`: Analytics emails

**Job Priorities:**
- Critical (election day operations): Highest priority
- User-facing (video processing): High priority
- Background analytics: Normal priority
- Maintenance: Low priority

---

## Data Models

### Core Entities

#### City
```python
class City(Base):
    id: UUID
    name: str
    state: str
    timezone: str
    election_date: date
    verification_methods: List[str]  # ['email', 'sms', 'id_me']
    ranking_config: dict  # Portfolio weights, clustering params
    moderation_config: dict
    created_at: datetime
    updated_at: datetime
```

#### Contest
```python
class Contest(Base):
    id: UUID
    city_id: UUID (FK)
    type: Enum['race', 'ballot_measure']
    title: str
    description: str
    election_date: date
    district_id: UUID (FK, nullable)
    filing_deadline: datetime
    active: bool
    created_at: datetime
```

#### Candidate
```python
class Candidate(Base):
    id: UUID
    contest_id: UUID (FK)
    user_id: UUID (FK to candidate_users)
    name: str
    party: str (nullable)
    website: str (nullable)
    bio: str
    photo_url: str
    verified: bool
    verification_method: str
    filed_date: date
    created_at: datetime
```

#### Question
```python
class Question(Base):
    id: UUID
    contest_id: UUID (FK)
    user_id: UUID (FK, nullable after anonymization)
    version: int  # Question can be edited, creates new version
    parent_id: UUID (FK, nullable - for merged questions)

    question_text: str
    context: str (nullable)
    issue_tags: List[str]

    status: Enum['pending', 'active', 'merged', 'rejected']

    # Ranking metadata
    upvotes: int
    downvotes: int
    ranking_score: float  # Computed by ranking algorithm
    viewpoint_cluster: int (nullable)

    # Embeddings for duplicate detection
    embedding: Vector(1536)  # OpenAI ada-002 or similar

    created_at: datetime
    updated_at: datetime
```

#### Answer
```python
class Answer(Base):
    id: UUID
    question_id: UUID (FK)
    candidate_id: UUID (FK)

    # Video metadata
    video_url: str
    video_hash: str  # SHA-256 of original video
    duration_seconds: int
    recorded_at: datetime

    # Transcript
    transcript: str
    transcript_corrected: str (nullable)
    caption_url: str  # VTT file

    # Sources (candidate can attach supporting evidence)
    sources: JSON  # [{ "claim": "...", "url": "...", "description": "..." }]

    # Status
    status: Enum['processing', 'published', 'flagged', 'removed']

    # Analytics
    view_count: int
    completion_rate: float

    created_at: datetime
    published_at: datetime (nullable)
```

#### QuestionVote
```python
class QuestionVote(Base):
    id: UUID
    question_id: UUID (FK)
    user_id: UUID (FK, anonymized after ranking stabilizes)
    user_hash: str  # Hash of user_id for fraud detection

    vote: Enum['up', 'down']

    # Fraud detection metadata
    ip_hash: str
    user_agent_hash: str
    voted_at: datetime

    # For anomaly detection
    flagged: bool
    flag_reason: str (nullable)
```

#### VerificationRecord
```python
class VerificationRecord(Base):
    id: UUID
    user_id: UUID (FK)
    city_id: UUID (FK)

    method: Enum['email', 'sms', 'id_me', 'manual']
    status: Enum['pending', 'verified', 'rejected']

    # Evidence (encrypted)
    verification_data: JSON (encrypted)

    verified_at: datetime (nullable)
    expires_at: datetime
    created_at: datetime
```

### Relationships

```
City 1:N Contest
Contest 1:N Candidate
Contest 1:N Question
Question 1:N Answer (one per candidate)
Question 1:N QuestionVote
User 1:N Question (submitted)
User 1:N QuestionVote
User 1:1 VerificationRecord
Candidate 1:1 User (candidate_users table)
```

---

## Ranking Algorithm

### Portfolio-Based Ranking

**Problem:** Pure upvote ranking allows one faction to dominate the top 100 questions.

**Solution:** Portfolio ranking that ensures diverse representation.

**Algorithm:**

1. **Issue Bucketing:**
   - Tag all questions with issues (housing, education, public safety, etc.)
   - Define portfolio weights: e.g., 30% housing, 20% education, 15% safety, 35% other
   - Weights learned from voting patterns + city configuration

2. **Viewpoint Clustering:**
   - Embed questions using sentence transformers
   - Cluster similar questions (HDBSCAN or K-means)
   - Limit how many questions from one cluster can be in top 100
   - Ensures "10 variations of defund police" doesn't dominate

3. **Ranking Score:**
   ```python
   score = (upvotes - downvotes)
           * viewpoint_diversity_multiplier
           * recency_bonus
           * minority_concern_boost
   ```

4. **Minority Concern Slot:**
   - Reserve 10% of slots for questions with high intensity but low breadth
   - Example: "What's your plan for the community garden?" may not be top 100 citywide
     but is critical to a specific neighborhood

5. **Anomaly Detection:**
   - Flag coordinated voting (same IP, same timeframe, lockstep votes)
   - Downweight votes from flagged accounts
   - Human review for borderline cases

**Transparency:** All ranking logic is open-source and auditable. City admins can see exactly how top 100 is computed.

---

## Security Architecture

### Authentication & Authorization

**Voter Auth:**
- Email/password with bcrypt hashing
- JWT tokens (access token: 15 min, refresh token: 7 days)
- Optional 2FA (TOTP or SMS)

**Candidate Auth:**
- Same as voter auth + additional verification layer
- Candidate must prove identity (filing ID + supporting docs)
- Separate JWT claims for candidate role

**Admin Auth:**
- Same as voter auth + invite-only registration
- Role-based access control (admin, moderator, viewer)
- Audit logging for all admin actions

**API Security:**
- HTTPS only (TLS 1.3)
- CORS restricted to known origins
- Rate limiting (1000 req/hour per IP for anonymous, 5000 for authenticated)
- CSRF protection for state-changing operations
- Content Security Policy (CSP) headers

### Data Security

**Encryption:**
- At rest: PostgreSQL TDE or encrypted disks
- In transit: TLS 1.3 for all connections
- Sensitive fields: AES-256 encryption for PII (email, phone)

**PII Handling:**
- Minimize collection (only what's needed)
- Hash IPs and user agents for fraud detection
- Anonymize votes after ranking stabilizes
- Delete user PII after election + 90 days (configurable)

**Video Security:**
- Cryptographic signing on upload
- Tamper detection on every access
- Provenance metadata (recording timestamp, device)
- No editing allowed (all videos recorded in-app)

### Fraud Prevention

**Question Submission:**
- Verified users only
- Rate limit: 5 questions per day
- Duplicate detection using embeddings
- Human review for borderline cases

**Question Voting:**
- Verified users only
- Rate limit: 100 votes per hour
- Anomaly detection for coordinated voting
- Honeypot questions to catch bots

**Video Answers:**
- Candidates only
- In-app recording only (no uploads)
- Time limits (1-3 minutes per question)
- Cryptographic signing

---

## Deployment Architecture

### Production Infrastructure

**Frontend:**
- Deployed to Vercel or Netlify (CDN-backed)
- Environment-specific builds (staging, production)
- Automatic preview deployments for PRs

**Backend:**
- Deployed to Railway, Render, or AWS ECS
- Auto-scaling based on load
- Load balancer with health checks
- Separate instances for API and Celery workers

**Database:**
- Managed PostgreSQL (Neon, RDS, Cloud SQL)
- Automated backups (daily, retained for 30 days)
- Point-in-time recovery enabled
- Read replicas for analytics queries

**Redis:**
- Managed Redis (Upstash, ElastiCache, Cloud Memorystore)
- Persistence enabled for session data
- Separate instances for cache vs. Celery

**Media Storage:**
- S3 or Azure Blob Storage
- CloudFront or Azure CDN for delivery
- Lifecycle policies for archival

**Monitoring:**
- Application: Sentry for error tracking
- Infrastructure: Datadog or Grafana + Prometheus
- Uptime: UptimeRobot or Pingdom
- Logs: CloudWatch, Papertrail, or Datadog

**CI/CD:**
- GitHub Actions or GitLab CI
- Automated tests on every PR
- Deployment on merge to main (staging) or release tags (production)
- Rollback capability

### Disaster Recovery

**Backup Strategy:**
- Database: Daily automated backups, retained 30 days
- Media: Replicated across regions
- Configuration: Infrastructure as Code (Terraform or Pulumi)

**Recovery Objectives:**
- RTO (Recovery Time Objective): 4 hours
- RPO (Recovery Point Objective): 24 hours (1 day of data loss acceptable)

**Incident Response:**
1. Detect (monitoring alerts)
2. Assess (on-call engineer evaluates)
3. Communicate (status page, email to admins)
4. Mitigate (rollback, scale up, patch)
5. Resolve (root cause fix)
6. Post-mortem (document and improve)

---

## Scalability Considerations

### Current Scale (MVP)
- 1 city, 10,000 voters, 50 candidates, 500 questions
- Easily handled by single backend instance + small DB

### Future Scale (10 cities)
- 100,000 voters, 500 candidates, 5,000 questions
- Backend: 2-3 instances with load balancer
- DB: Vertical scaling + read replicas
- Redis: Cluster mode for high availability

### Future Scale (100 cities)
- 1M voters, 5,000 candidates, 50,000 questions
- Backend: Horizontal scaling with auto-scaling
- DB: Sharding by city (multi-tenant architecture)
- CDN: Critical for video delivery
- Celery: Dedicated worker pools per job type

### Bottlenecks and Mitigations

**Database:**
- Problem: Large JOINs for complex queries
- Solution: Materialized views, read replicas, caching

**Video Processing:**
- Problem: FFmpeg is CPU-intensive
- Solution: Separate worker pool, spot instances, queue prioritization

**Ranking Algorithm:**
- Problem: Recomputing top 100 for every vote is expensive
- Solution: Compute every 15 minutes, cache results, incremental updates

---

## Observability and Monitoring

### Key Metrics

**Application Metrics:**
- Request latency (p50, p95, p99)
- Error rate by endpoint
- Database query performance
- Celery queue depth and processing time

**Business Metrics:**
- Questions submitted per day
- Answers published per day
- Voter engagement (votes cast, videos watched)
- Coverage (% candidates answering top 10 questions)

**Security Metrics:**
- Failed login attempts
- Rate limit violations
- Anomaly detection flags
- Admin actions (audit log volume)

### Alerting

**Critical Alerts (Page On-Call):**
- API downtime > 5 minutes
- Database connection failures
- Celery queue backed up > 1000 jobs
- Security anomaly detected (voting fraud)

**Warning Alerts (Notify Slack):**
- API latency p95 > 500ms
- Error rate > 1%
- Disk space < 20%
- SSL certificate expiring in < 7 days

### Logging

**Log Levels:**
- ERROR: Application errors, exceptions
- WARN: Potential issues, rate limits hit
- INFO: Requests, business events (question submitted, answer published)
- DEBUG: Development only

**Structured Logging:**
```json
{
  "timestamp": "2026-02-14T12:00:00Z",
  "level": "INFO",
  "service": "api",
  "user_id": "uuid",
  "action": "question_submitted",
  "question_id": "uuid",
  "city_id": "uuid",
  "ip_hash": "sha256"
}
```

---

## Technology Choices and Rationale

### Why FastAPI?
- Fast, modern Python framework
- Automatic OpenAPI documentation
- Type safety with Pydantic
- Async support for high concurrency
- Easy to test and maintain

### Why PostgreSQL?
- Mature, reliable, open-source
- pgvector extension for embeddings
- Full-text search built-in
- JSON support for flexible fields
- Strong ACID guarantees

### Why React?
- Component-based architecture
- Large ecosystem and community
- TypeScript support for type safety
- Excellent tooling and dev experience
- Easy to hire for

### Why Celery?
- Mature task queue for Python
- Supports multiple brokers (Redis, RabbitMQ)
- Task retries, scheduling, and monitoring
- Integrates well with FastAPI

### Why Redis?
- Fast in-memory data store
- Perfect for caching and sessions
- Celery broker/backend
- Rate limiting and leaderboards

---

## Future Architecture Improvements

### Planned Enhancements

**Real-Time Features (Q3 2026):**
- WebSocket support for live ranking updates
- Live moderation queue for admins
- Real-time notifications for candidates

**Multi-Region Deployment (2027):**
- Regional data residency for compliance
- Lower latency for geographically distributed cities
- Active-active failover

**Advanced Analytics (2027):**
- Machine learning for question clustering
- Sentiment analysis on transcripts
- Predictive modeling for candidate participation

**Mobile Apps (2027):**
- Native iOS and Android apps
- Push notifications
- Offline support for viewing ballots

---

**For implementation details, see:**
- [API Documentation](API.md)
- [Database Schema](architecture/database-schema.md)
- [Deployment Guide](DEPLOYMENT.md)

---

**Last Updated:** 2026-02-14
**Next Review:** After MVP deployment
