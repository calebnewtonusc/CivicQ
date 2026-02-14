# CivicQ Development Roadmap

**Version:** 1.0
**Last Updated:** 2026-02-14
**Timeline:** 24 months (Q1 2026 - Q4 2027)

---

## Overview

This roadmap is **ambitious and realistic**. It balances speed (prove value fast) with responsibility (don't manufacture scandals). Each phase has specific deliverables, success criteria, and decision gates.

**Key Principle:** We do not advance to the next phase until success criteria for the current phase are met. No "move fast and break things" when dealing with democratic infrastructure.

---

## Phase 0: Foundation (Q1 2026) - CURRENT

**Timeline:** Months 0-3 (Feb 2026 - Apr 2026)
**Goal:** Establish architecture, documentation, and development infrastructure

### Key Deliverables

#### 1. Documentation Suite ✅
- [x] Comprehensive README with mission and principles
- [x] CODE_OF_CONDUCT with civic engagement focus
- [x] SECURITY policy with election security emphasis
- [x] CHANGELOG following semantic versioning
- [x] ARCHITECTURE documentation
- [x] API documentation
- [x] TRUST-MODEL explaining transparency commitments
- [x] PRIVACY framework
- [x] MVP-SCOPE defining V1 features
- [x] DEPLOYMENT guide

#### 2. Repository Structure ✅
- [x] Backend: FastAPI + SQLAlchemy + Pydantic
- [x] Frontend: React + TypeScript
- [x] Database: PostgreSQL + pgvector
- [x] Infrastructure: Docker Compose for local development
- [x] Documentation: Comprehensive docs/ directory

#### 3. Core Architecture Decisions
- [ ] Database schema finalized (10+ models)
- [ ] API design patterns established
- [ ] Authentication strategy defined (JWT)
- [ ] Video pipeline architecture (FFmpeg + Whisper)
- [ ] Ranking algorithm specification

#### 4. Development Environment
- [ ] Docker Compose working (backend + frontend + db + redis)
- [ ] Local development guide tested
- [ ] VS Code recommended extensions documented
- [ ] Pre-commit hooks configured (linting, formatting)

**Milestone Gate:** Architecture reviewed and approved; team can begin implementation.

---

## Phase 1: Core Infrastructure (Q2 2026)

**Timeline:** Months 3-6 (Apr 2026 - Jul 2026)
**Goal:** Build foundational platform features

### Key Deliverables

#### 1. Database and Migrations
- [ ] Alembic migrations for all core models
- [ ] Seed data scripts for development
- [ ] pgvector extension enabled and tested
- [ ] Database indexes optimized

**Success Criteria:**
- All migrations run cleanly on fresh database
- Seed data creates realistic test scenarios
- Query performance < 100ms for common operations

#### 2. Authentication System
- [ ] User registration and login (email/password)
- [ ] JWT token generation and validation
- [ ] Password reset flow
- [ ] Session management with Redis
- [ ] Rate limiting on auth endpoints

**Success Criteria:**
- Auth endpoints functional and secure
- Rate limiting prevents brute force attacks
- Password reset flow tested end-to-end

#### 3. Ballot Management
- [ ] City, district, contest CRUD APIs
- [ ] Candidate profile management
- [ ] Geocoding and ballot lookup by address
- [ ] Admin interface for ballot creation

**Success Criteria:**
- Admin can create full ballot for test city
- Voter can look up ballot by address
- Data model supports complex district boundaries

#### 4. Question System
- [ ] Question submission API
- [ ] Question listing with pagination
- [ ] Issue tagging system
- [ ] Basic duplicate detection (embedding search)

**Success Criteria:**
- Voter can submit question
- Questions display with issue tags
- Duplicate detection identifies 80%+ duplicates

#### 5. Voting and Ranking (V1)
- [ ] Vote up/down on questions (verified users only)
- [ ] Portfolio-based ranking algorithm
- [ ] Anomaly detection for coordinated voting
- [ ] Ranking transparency tooltips

**Success Criteria:**
- Ranking reflects issue diversity (3+ categories in top 10)
- Anomaly detection flags coordinated voting
- "Why this ranking?" explanations are clear

---

## Phase 2: Video Pipeline (Q2-Q3 2026)

**Timeline:** Months 6-9 (Jul 2026 - Oct 2026)
**Goal:** Implement video recording, processing, and delivery

### Key Deliverables

#### 1. Video Recording
- [ ] In-browser video recording (MediaRecorder API)
- [ ] Upload to presigned S3 URL
- [ ] Recording metadata capture
- [ ] Time limits and visual countdown

**Success Criteria:**
- Candidate can record 1-3 minute video
- Video uploads reliably on WiFi and cellular
- Metadata includes timestamp, candidate ID, device info

#### 2. Video Processing (Celery)
- [ ] Celery workers set up with Redis broker
- [ ] FFmpeg transcoding pipeline (HLS + MP4)
- [ ] Caption generation (Whisper or Deepgram)
- [ ] Thumbnail extraction
- [ ] Provenance tracking (SHA-256 hash)

**Success Criteria:**
- Video processing completes within 5 minutes
- Captions accuracy ≥ 90%
- All videos have verifiable hash

#### 3. Video Delivery
- [ ] S3 + CloudFront CDN setup
- [ ] Adaptive bitrate streaming (HLS)
- [ ] Caption file (VTT) delivery
- [ ] Video playback UI with controls

**Success Criteria:**
- Videos play on desktop and mobile
- Streaming works on 3G connections (480p)
- Captions display correctly

#### 4. Answer Management
- [ ] Candidate can review and publish answers
- [ ] Transcript correction (preserves original)
- [ ] Source citation attachment
- [ ] Answer analytics (views, completion rate)

**Success Criteria:**
- Candidate can correct transcript errors
- Sources display with answers
- Analytics update in real-time

---

## Phase 3: User Verification (Q3 2026)

**Timeline:** Months 9-12 (Oct 2026 - Jan 2027)
**Goal:** Implement modular verification system

### Key Deliverables

#### 1. Email Verification
- [ ] Email verification code flow
- [ ] SendGrid integration
- [ ] Verification status tracking
- [ ] Expiration and retry logic

**Success Criteria:**
- 95%+ delivery rate for verification emails
- Code expires after 15 minutes
- Rate limiting prevents abuse

#### 2. SMS Verification (Optional)
- [ ] Twilio integration
- [ ] SMS code delivery
- [ ] Phone number hashing (not stored)

**Success Criteria:**
- 90%+ delivery rate for SMS codes
- No phone numbers stored in database

#### 3. Candidate Verification
- [ ] Filing ID verification flow
- [ ] Photo ID upload and review
- [ ] Manual review by city admin
- [ ] Verification badge on profile

**Success Criteria:**
- Manual review turnaround < 2 business days
- < 5% false positives (legitimate candidates rejected)

#### 4. City-Configurable Verification
- [ ] Verification method adapter pattern
- [ ] City admin can enable/disable methods
- [ ] Custom verification workflows

**Success Criteria:**
- City can choose email, SMS, or both
- Custom verification adapters can be added

---

## Phase 4: Admin Console (Q3-Q4 2026)

**Timeline:** Months 12-15 (Jan 2027 - Apr 2027)
**Goal:** Build moderation and administration tools

### Key Deliverables

#### 1. Moderation Queue
- [ ] Pending questions view
- [ ] Approve/reject/edit actions
- [ ] Merge duplicate questions
- [ ] Flag content for review

**Success Criteria:**
- Admin can process queue in < 24 hours
- Merge preserves vote counts
- Actions are audit logged

#### 2. User Management
- [ ] User list with search and filters
- [ ] Manual verification approval
- [ ] Ban/suspend users
- [ ] Review appeals

**Success Criteria:**
- Admin can find and manage users
- Bans prevent further submissions
- Appeals process is documented

#### 3. Analytics Dashboard
- [ ] Engagement metrics (questions, votes, views)
- [ ] Coverage metrics (% candidates participating)
- [ ] Trust metrics (survey integration)
- [ ] Exportable reports

**Success Criteria:**
- Dashboard loads in < 2 seconds
- Reports export to CSV/PDF
- Metrics update every 15 minutes

#### 4. Anomaly Detection Alerts
- [ ] Coordinated voting alerts
- [ ] Unusual submission patterns
- [ ] Suspicious account activity
- [ ] Admin email notifications

**Success Criteria:**
- Alerts fire within 15 minutes of detection
- < 10% false positives
- Admin can review and take action

---

## Phase 5: Pilot Preparation (Q2 2027)

**Timeline:** Months 15-18 (Apr 2027 - Jul 2027)
**Goal:** Polish, test, and prepare for pilot city launch

### Key Deliverables

#### 1. Frontend Polish
- [ ] Mobile-responsive design refinement
- [ ] Accessibility audit and fixes (WCAG 2.1 AA)
- [ ] Performance optimization (< 3s load time)
- [ ] UX testing with real users

**Success Criteria:**
- Lighthouse score ≥ 90 (all categories)
- WCAG 2.1 AA compliant
- Usability testing: 90%+ task completion

#### 2. Security Audit
- [ ] Third-party security audit
- [ ] Penetration testing
- [ ] Fix all critical and high-severity issues
- [ ] Publish security audit report

**Success Criteria:**
- Zero critical vulnerabilities
- < 5 high-severity vulnerabilities
- Public security audit summary published

#### 3. Performance Testing
- [ ] Load testing (100 concurrent users)
- [ ] Stress testing (500 concurrent users)
- [ ] Video pipeline capacity testing
- [ ] Database performance tuning

**Success Criteria:**
- API p95 response time < 500ms at 100 concurrent users
- Video processing keeps up with 10 uploads/minute
- Database handles 10K questions + 100K votes

#### 4. Pilot City Recruitment
- [ ] Pilot city selection criteria defined
- [ ] Outreach to 10 potential cities
- [ ] Pilot agreement template
- [ ] City admin training materials

**Success Criteria:**
- Pilot city signed and committed
- City admin trained on platform
- Launch date set (6 months before election)

---

## Phase 6: Pilot Launch (Q3 2027)

**Timeline:** Months 18-21 (Jul 2027 - Oct 2027)
**Goal:** Launch with pilot city and learn

### Key Deliverables

#### 1. Deployment
- [ ] Production infrastructure deployed
- [ ] Monitoring and alerts configured
- [ ] Backup and disaster recovery tested
- [ ] On-call rotation established

**Success Criteria:**
- 99% uptime during election period
- All services monitored
- Disaster recovery drill passed

#### 2. Candidate Onboarding
- [ ] Onboard all candidates in pilot city
- [ ] Verify candidate identities
- [ ] Train candidates on video recording
- [ ] Provide candidate support helpline

**Success Criteria:**
- 80%+ candidates onboarded
- 50%+ candidates answer ≥ 1 question
- < 5% candidates report technical issues

#### 3. Voter Outreach
- [ ] Launch announcement (press, social media)
- [ ] Voter outreach campaign
- [ ] Partnerships with civic organizations
- [ ] Help center and FAQs published

**Success Criteria:**
- 50%+ eligible voters aware of CivicQ
- 25%+ eligible voters create account
- Positive press coverage (3+ articles)

#### 4. Election Day Operations
- [ ] On-call team staffed
- [ ] Real-time monitoring
- [ ] Incident response ready
- [ ] Election official coordination

**Success Criteria:**
- Zero election-critical incidents
- < 5 minutes to respond to P0 incidents
- Smooth election day operations

---

## Phase 7: Post-Pilot Iteration (Q4 2027)

**Timeline:** Months 21-24 (Oct 2027 - Jan 2028)
**Goal:** Learn from pilot, iterate, and prepare for scale

### Key Deliverables

#### 1. Pilot Retrospective
- [ ] Voter survey (trust, clarity, usability)
- [ ] Candidate survey (fairness, ease of use)
- [ ] City admin feedback
- [ ] Analytics review (engagement, coverage)

**Success Criteria:**
- 75%+ voter trust score
- 85%+ candidate fairness score
- City admin recommends to other cities (NPS ≥ 50)

#### 2. Bug Fixes and Improvements
- [ ] Fix all critical bugs
- [ ] Address usability pain points
- [ ] Performance optimizations
- [ ] Feature requests prioritized

**Success Criteria:**
- Zero critical bugs
- < 10 high-priority bugs
- Performance improvements: 20% faster

#### 3. Scale Preparation
- [ ] Multi-city architecture
- [ ] Automated deployment (CI/CD)
- [ ] Self-service city onboarding
- [ ] Pricing and business model finalized

**Success Criteria:**
- Can onboard new city in < 1 week
- Automated deployment tested
- Pricing model validated with 3+ cities

#### 4. V2 Planning
- [ ] Roadmap for V2 features
- [ ] Community feedback incorporated
- [ ] Technical debt prioritized
- [ ] Funding strategy (grants, city contracts)

**Success Criteria:**
- V2 roadmap published
- Funding secured for 6+ months
- Team ready to scale

---

## Beyond 2027: V2 and Scale

### V2 Features (2028)

**Rebuttal Videos:**
- Candidates can respond to other candidates' answers
- Time-limited, must cite specific claims
- Prevents "he said, she said" loops

**Issue Pages:**
- Dedicated landing pages for each issue
- All answers on housing, education, safety, etc.
- Cross-contest comparison

**Multi-City Support:**
- Shared platform for 10+ cities
- City-specific configurations
- Centralized admin for civic organizations

**Advanced Analytics:**
- Sentiment analysis on transcripts
- Topic modeling and clustering
- Predictive modeling for candidate participation

**Open API:**
- Public API for researchers and civic groups
- Anonymized dataset for academic research
- Third-party integrations

**Mobile Apps:**
- Native iOS and Android apps
- Push notifications
- Offline support for ballots

---

## Success Metrics (24-Month Goals)

### Product Success
- **Pilot City:** 75%+ voter trust score
- **Scale:** 10 cities using CivicQ
- **Engagement:** 30%+ eligible voters create account
- **Coverage:** 80%+ candidates participate

### Platform Success
- **Reliability:** 99.9% uptime
- **Performance:** < 500ms API p95
- **Security:** Zero trust violations
- **Accessibility:** WCAG 2.1 AA compliant

### Business Success
- **Revenue:** $100K ARR from city contracts
- **Sustainability:** Break-even within 24 months
- **Partnerships:** 5+ civic organizations promoting CivicQ
- **Recognition:** Featured in civic tech publications

---

## Risk Mitigation

### Technical Risks

**Database Performance:**
- Mitigation: Read replicas, caching, query optimization
- Fallback: Vertical scaling, sharding by city

**Video Processing Bottleneck:**
- Mitigation: Separate worker pools, spot instances
- Fallback: Queue prioritization, async processing

**Security Breach:**
- Mitigation: Security audits, penetration testing, bug bounty
- Fallback: Incident response plan, breach notification

### Product Risks

**Low Candidate Participation:**
- Mitigation: Outreach, training, value proposition clarity
- Fallback: Highlight participating candidates, public pressure

**Voter Distrust:**
- Mitigation: Transparency, open-source code, third-party audits
- Fallback: Education campaign, trust-building initiatives

**Manipulation Attempts:**
- Mitigation: Anomaly detection, rate limiting, manual review
- Fallback: Temporarily disable submissions, increase human review

### Business Risks

**No Pilot City:**
- Mitigation: Broaden outreach, flexible pilot terms
- Fallback: Launch as open-source tool, community-driven

**Funding Gap:**
- Mitigation: Grants, city contracts, civic org partnerships
- Fallback: Reduce scope, volunteer-driven development

---

## Decision Gates

**Gate 1 (End of Phase 0):** Architecture approved, funding secured for Phase 1
**Gate 2 (End of Phase 1):** Core features functional, pilot city committed
**Gate 3 (End of Phase 3):** Security audit passed, deployment ready
**Gate 4 (End of Phase 6):** Pilot success criteria met, ready to scale
**Gate 5 (End of Phase 7):** Business model validated, V2 roadmap funded

---

## Resource Requirements

**Phase 0-1 (Months 0-6):**
- 2 full-time engineers
- 1 part-time product manager
- 1 part-time designer

**Phase 2-4 (Months 6-15):**
- 3 full-time engineers
- 1 full-time product manager
- 1 full-time designer
- 1 part-time DevOps engineer

**Phase 5-7 (Months 15-24):**
- 4 full-time engineers
- 1 full-time product manager
- 1 full-time designer
- 1 full-time DevOps engineer
- 1 part-time security engineer

---

**For detailed feature scope, see [MVP-SCOPE.md](MVP-SCOPE.md)**

**For deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)**

---

**Last Updated:** 2026-02-14
**Next Review:** Quarterly or after major milestones
