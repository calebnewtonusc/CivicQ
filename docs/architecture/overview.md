# CivicQ Architecture Overview

## System Architecture

CivicQ is a **location-anchored, high-integrity content system** for civic engagement in local elections. The architecture prioritizes:

1. **Integrity** - Verified identities, tamper-evident content, audit logging
2. **Transparency** - Open records, versioning, moderation accountability
3. **Anti-Manipulation** - Anomaly detection, representative ranking, rate limiting
4. **Accessibility** - Mobile-responsive, fast performance, WCAG compliance

## High-Level Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Voters    │◄───────►│   Web App    │◄───────►│   API       │
│  (Mobile/   │         │  (React)     │         │  (FastAPI)  │
│   Desktop)  │         └──────────────┘         └─────────────┘
└─────────────┘                                         │
                                                        │
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│ Candidates  │◄───────►│  Candidate   │◄───────►│  Database   │
│  (Portal)   │         │   Portal     │         │ (Postgres)  │
└─────────────┘         └──────────────┘         └─────────────┘
                                                        │
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│ City Staff  │◄───────►│    Admin     │◄───────►│   Media     │
│  (Admin)    │         │   Console    │         │  Pipeline   │
└─────────────┘         └──────────────┘         └─────────────┘
```

## Core Components

### 1. Frontend Applications

#### Voter Web App (React + TypeScript)
- **Purpose:** Public-facing application for voters
- **Key Features:**
  - Ballot home screen (contest cards with progress)
  - Question submission and ranking
  - Video answer watching
  - Side-by-side candidate comparison
  - Issue following and filtering
- **Tech Stack:**
  - React 18 with TypeScript
  - React Router for navigation
  - TanStack Query for data fetching
  - Zustand for state management
  - Tailwind CSS for styling
- **Design Principles:**
  - Mobile-first, responsive design
  - Accessibility (WCAG 2.1 AA)
  - No infinite scroll (intentional endpoint)
  - Calm, library-like UX (not social media)

#### Candidate Portal (React + TypeScript)
- **Purpose:** Secure portal for candidates to record answers
- **Key Features:**
  - Identity verification
  - Top questions queue with deadlines
  - In-app video recording
  - Transcript review and correction
  - Source attachment for claims
  - Progress tracking relative to other candidates
- **Security:**
  - Multi-factor authentication
  - City-issued candidate verification
  - Audit logging of all actions

#### Admin Console (React + TypeScript)
- **Purpose:** City staff and moderator dashboard
- **Key Features:**
  - Moderation queue
  - Metrics and reporting
  - Candidate onboarding management
  - Transparency reports
  - Coverage statistics
- **Access Control:**
  - Role-based permissions
  - City-scoped data access
  - Action audit logging

### 2. Backend API (FastAPI)

#### Core Responsibilities
- RESTful API for all client applications
- Authentication and authorization
- Business logic and validation
- Database operations
- Integration with external services

#### API Structure
```
/api/auth              - Authentication & verification
/api/cities            - City and election discovery
/api/ballot            - Personalized ballot retrieval
/api/contests          - Contest details and candidates
/api/questions         - Question CRUD and ranking
/api/candidates        - Candidate profiles and answers
/api/reports           - Content reporting
/api/admin             - Admin operations
```

#### Security Features
- JWT-based authentication
- Rate limiting (per-user and per-IP)
- CORS protection
- Input validation and sanitization
- SQL injection prevention (ORM)
- XSS protection
- CSRF tokens
- Secure headers (HSTS, CSP, etc.)

### 3. Database (PostgreSQL)

#### Why PostgreSQL?
- **ACID compliance** for integrity
- **pgvector extension** for semantic search
- **Row-level security** for multi-tenancy
- **JSON support** for flexible metadata
- **Mature ecosystem** and tooling

#### Key Features
- City-scoped data isolation
- Vector embeddings for question deduplication
- Comprehensive audit logging
- Question versioning
- Optimized indexes for ranking queries

### 4. Media Pipeline

#### Video Recording Flow
```
1. In-app recording (browser MediaRecorder or native)
2. Upload to object storage (S3-compatible)
3. Transcoding (multiple formats/resolutions)
4. Transcript generation (Whisper/Deepgram/AssemblyAI)
5. Caption generation (WebVTT/SRT)
6. Provenance hash calculation
7. CDN distribution
```

#### Authenticity & Provenance
- Videos recorded in-app (no uploads)
- Cryptographic hashing of raw files
- Tamper-evident metadata
- Chain of custody logging
- Timestamped authenticity stamps

#### Storage Strategy
- **Hot storage:** Active election videos (CDN)
- **Warm storage:** Recent past elections (S3 Standard)
- **Cold storage:** Archive (S3 Glacier)

### 5. Verification System

#### Modular Design
The verification system is **city-configurable** with multiple adapters:

##### Light Verification (SMS + Mail Code)
- SMS verification code
- Physical mail confirmation code
- Minimal PII stored
- Hard to scale for bots

##### Medium Verification (Voter Roll Match)
- Name + DOB + address match
- City-provided voter roll
- No external vendor
- Privacy-friendly

##### Strong Verification (ID Proofing)
- Third-party identity verification
- Liveness detection
- Document verification
- City opt-in only (due to privacy sensitivity)

#### Privacy Principles
- **Minimal data retention:** Only store verification token
- **Modular providers:** City chooses verification method
- **Transparency:** Clear privacy policy per method
- **No selling data:** Never share or monetize user data

### 6. Ranking Algorithm

#### Goals
- Represent the **whole community**, not just loud factions
- Prevent brigading and manipulation
- Surface diverse viewpoints
- Ensure minority concerns are heard

#### Components

##### 1. Verified-Only Voting
Only verified residents can vote on questions.

##### 2. Anomaly Detection
- Rate limiting (votes per hour)
- Device fingerprinting (non-invasive)
- Voting pattern analysis
- Lockstep voting detection
- Downweighting of suspicious votes

##### 3. Issue Portfolio Allocation
Questions are allocated across issue buckets:
- Housing: 20%
- Public Safety: 15%
- Education: 15%
- Budget/Taxes: 10%
- Environment: 10%
- Other: 30%

Prevents one issue from dominating.

##### 4. Viewpoint Clustering
- Semantic clustering of similar questions
- Cluster cap (max 5 questions per cluster)
- Prevents "ten versions of same talking point"

##### 5. Minority Concern Slots
- 10% of top questions reserved for minority concerns
- Questions intensely important to smaller segments
- Reduces polarization by acknowledging all voices

##### 6. Geographic Balancing (Optional)
If city provides district mapping, ensure representation across areas.

#### Ranking Score Formula
```
score = base_score × anomaly_weight × recency_factor
+ minority_boost + geographic_boost

base_score = upvotes - downvotes
anomaly_weight = 0.0 to 1.0 (suspicious votes downweighted)
recency_factor = slight decay to prevent early capture
minority_boost = +N if intense support in smaller segment
geographic_boost = +N if underrepresented district
```

### 7. Moderation System

#### Three-Layer Approach

##### Layer 1: Automated Filters
- Profanity and slurs
- Personal information (doxxing)
- Threats and violence
- Spam detection
- Duplicate detection

##### Layer 2: Civic Integrity Rules
- Off-jurisdiction questions
- Pure harassment
- Propaganda phrased as questions
- Misinformation (flagged for review, not auto-removed)

##### Layer 3: Human Review Board
- City moderation board
- Process-based (not opinion-based)
- Published standards
- Appeal mechanism
- Transparent action logging

#### Transparency Requirements
- All moderation actions logged
- Aggregate statistics published
- Quarterly transparency reports
- Rationale codes for all removals

## Data Flow Examples

### Example 1: Voter Asks a Question

```
1. Voter opens contest page
2. Clicks "Ask a Question"
3. Enters question text + issue tags + context
4. Frontend checks character limits
5. API receives submission
6. Generate embedding (sentence-transformers)
7. Check for duplicates (vector similarity search)
8. If similar question exists, prompt to upvote instead
9. If user proceeds, save question (status: pending)
10. Run automated moderation filters
11. If passes, approve (status: approved)
12. If flagged, send to moderation queue
13. Return question ID to frontend
14. Frontend shows success + encourages sharing
```

### Example 2: Candidate Records an Answer

```
1. Candidate logs into portal
2. Views "Top Questions" queue
3. Selects question to answer
4. Clicks "Record Answer"
5. Portal shows structured prompts
6. Browser captures video (MediaRecorder API)
7. Time limit enforced client-side and server-side
8. Video uploaded to S3 (multipart upload)
9. Backend triggers processing:
   - Transcoding (FFmpeg)
   - Transcript generation (Whisper)
   - Caption generation
   - Hash calculation
10. Candidate reviews transcript
11. Can correct transcription errors (not change video)
12. Can attach sources to claims
13. Submit for publication
14. Video answer published (status: published)
15. CDN caches video for fast delivery
```

### Example 3: Voter Ranks Questions

```
1. Voter opens contest page
2. Sees "Top Questions" list
3. Clicks upvote on question
4. Frontend checks verification status
5. If not verified, prompt to verify
6. If verified, submit vote (value: +1)
7. Backend checks:
   - User is verified
   - User hasn't voted on this question before
   - Rate limit not exceeded
8. Calculate anomaly score:
   - Check voting patterns
   - Check device fingerprint
   - Check for coordinated behavior
9. If suspicious, downweight vote (weight: 0.5)
10. Update question upvote count
11. Recalculate rank scores (async job)
12. Return updated vote status to frontend
13. Frontend updates UI optimistically
```

## Deployment Architecture

### Development
```
Local Machine:
- Backend: uvicorn (localhost:8000)
- Frontend: React dev server (localhost:3000)
- Database: PostgreSQL (localhost:5432)
- Redis: localhost:6379
```

### Production
```
Cloud Infrastructure:
- Frontend: Static hosting (Vercel/Netlify) + CDN
- Backend: Container (Docker) on cloud VM or PaaS
- Database: Managed PostgreSQL (AWS RDS / GCP Cloud SQL)
- Redis: Managed Redis (AWS ElastiCache / GCP Memorystore)
- Object Storage: S3 or S3-compatible
- CDN: CloudFlare or CloudFront
- Video Processing: Serverless functions or dedicated workers
```

### Scaling Strategy

#### Phase 1 (Pilot City - <10k users)
- Single backend server
- Single database instance
- Shared Redis
- Basic CDN

#### Phase 2 (Multiple Cities - <100k users)
- Horizontal backend scaling (load balancer)
- Database read replicas
- Dedicated Redis for caching
- Advanced CDN with edge caching

#### Phase 3 (Regional Scale - >100k users)
- Auto-scaling backend
- Database sharding (by city)
- Redis cluster
- Multi-region CDN
- Dedicated video processing cluster

## Security Architecture

### Defense in Depth

1. **Network Layer**
   - WAF (Web Application Firewall)
   - DDoS protection
   - Rate limiting

2. **Application Layer**
   - Input validation
   - Output encoding
   - CSRF protection
   - XSS prevention

3. **Data Layer**
   - Encryption at rest
   - Encryption in transit (TLS)
   - Database row-level security
   - Secrets management (Vault)

4. **Identity Layer**
   - Multi-factor authentication
   - Password hashing (bcrypt)
   - JWT with short expiration
   - Refresh token rotation

5. **Monitoring Layer**
   - Real-time anomaly detection
   - Audit logging
   - Security event alerting
   - Regular penetration testing

## Privacy Architecture

### Principles
1. **Minimal Data Collection:** Only collect what's necessary
2. **Purpose Limitation:** Use data only for stated purpose
3. **Transparency:** Clear privacy policy and data usage
4. **User Control:** Allow users to export and delete data
5. **Security:** Protect all user data with strong encryption

### PII Handling
- **Never store:** Raw IP addresses, precise geolocation
- **Hashed storage:** IP address hashes for fraud detection
- **Encrypted storage:** Phone numbers, email (if required)
- **Minimal retention:** Delete after verification complete
- **City-scoped:** Data isolated by city

## Monitoring & Observability

### Key Metrics

#### Application Health
- Request latency (p50, p95, p99)
- Error rates (4xx, 5xx)
- Uptime percentage

#### Business Metrics
- Verified user count
- Questions submitted
- Questions ranked
- Answers published
- Contest coverage
- Watch time

#### Integrity Metrics
- Suspicious votes detected
- Moderation actions taken
- Appeal outcomes
- Anomaly detection triggers

#### Performance Metrics
- Page load time
- Video streaming performance
- Database query time
- API response time

### Logging Strategy
- **Structured logging** (JSON format)
- **Log levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Correlation IDs:** Track requests across services
- **Retention:** 30 days hot, 1 year cold

## Technology Choices Summary

| Component | Technology | Why |
|-----------|-----------|-----|
| Frontend | React + TypeScript | Type safety, component reuse, ecosystem |
| Backend | FastAPI | Fast, modern, async, auto docs |
| Database | PostgreSQL | ACID, pgvector, mature |
| Object Storage | S3-compatible | Industry standard, scalable |
| CDN | CloudFlare | Performance, DDoS protection |
| Transcription | Whisper (local) | Open-source, no vendor lock-in |
| Embeddings | sentence-transformers | Local, no API costs |
| Video | FFmpeg | Open-source, comprehensive |
| Cache | Redis | Fast, versatile |
| Task Queue | Celery | Mature, Python ecosystem |

## Future Enhancements

### Phase 2
- Mobile native apps (iOS/Android)
- Push notifications
- Real-time updates (WebSockets)
- Advanced analytics dashboard

### Phase 3
- Multi-language support
- Accessibility enhancements (screen reader optimization)
- Offline mode (PWA)
- Integration with official election systems

### Phase 4
- Open API for third-party integrations
- Embeddable widgets
- Data export API
- Research partnerships
