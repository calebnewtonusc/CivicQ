# MVP Scope - CivicQ V1

**Version:** 1.0
**Last Updated:** 2026-02-14
**Status:** Planning

---

## Executive Summary

The V1 ruthless feature set is designed to deliver a complete civic Q&A loop for one pilot city without attempting to be "everything at once." The goal is to prove the core value proposition: **voters get clear answers, candidates get fair exposure, election officials get trustworthy infrastructure**—while building trust through transparent, anti-manipulation design.

If you try to ship everything, you ship nothing. CivicQ V1 succeeds by being narrow, effective, and trusted.

---

## Core V1 Feature Set

### 1. Voter Web Application

**What it includes:**

**Home Screen:**
- Personalized ballot based on voter address
- List of all contests (races + ballot measures)
- Progress indicators (X questions answered out of Y)

**Contest View:**
- Candidate list with photos, bios, party affiliation
- Top 10 questions ranked by community
- Answer status (which candidates answered which questions)
- "Compare candidates" button

**Question View:**
- Question text, context, issue tags
- All candidate video answers
- Transcript with captions
- Source citations (if candidate provided)
- Vote up/down (verified users only)
- "Why this ranking?" explanation

**Question Submission:**
- Submit new question with issue tags
- Duplicate detection ("Similar questions already exist")
- Moderation status tracking

**Verification Flow:**
- Email or SMS verification
- City-configurable verification methods
- Clear explanation of why verification matters

**What it excludes from V1:**
- Native mobile apps (responsive web only)
- Social sharing to Twitter/Facebook (simple link sharing only)
- "Recommended questions for you" (no personalization algorithms)
- Video annotations or timestamping
- Multi-language support (English + Spanish only)

**Success Criteria:**
- Voter can find their ballot in < 30 seconds
- Voter can watch top 3 candidate answers in < 5 minutes
- 80%+ of voters "understand candidate positions better" (survey)

---

### 2. Candidate Portal

**What it includes:**

**Identity Verification:**
- Upload candidate filing ID
- Upload government-issued photo ID
- Manual review by city admin (1-2 business days)

**Question Queue:**
- List of top 100 questions for their contest
- Sorting by ranking, date, issue tag
- Answer status (not answered, draft, published)

**Video Recording:**
- In-browser video recording (MediaRecorder API)
- 1-3 minute time limit per question
- Preview before submitting
- Cannot re-record (encourages authenticity)

**Transcript Review:**
- Auto-generated transcript
- Candidate can correct transcription errors (not content)
- Original transcript preserved for audit

**Source Attachment:**
- Add citations for factual claims
- Link to budget docs, audit reports, official data
- Max 3 sources per answer

**Analytics Dashboard:**
- Video views (aggregate count)
- Answer completion rate
- Top viewed answers
- Coverage metrics (% of top 10 answered)

**What it excludes from V1:**
- Video editing or splicing
- Pre-recorded video upload (all in-app recording)
- Live Q&A or debate features
- Direct messaging with voters
- Campaign website integration

**Success Criteria:**
- Candidate can verify identity in < 10 minutes (excluding review time)
- Candidate can record answer in < 5 minutes (first try)
- 80%+ of candidates "feel process is fair" (survey)

---

### 3. Admin Moderation Console

**What it includes:**

**Moderation Queue:**
- Pending questions flagged by automated moderation
- User-reported content
- Voting anomalies flagged by algorithm

**Question Management:**
- Approve/reject questions
- Edit for clarity (preserves original version)
- Merge duplicate questions
- Add/edit issue tags

**User Management:**
- Verify user accounts (manual review if automated fails)
- Ban users for violations
- Review verification appeals

**Analytics Dashboard:**
- Engagement metrics (questions, votes, views)
- Coverage metrics (% candidates participating)
- Trust metrics (voter confidence survey results)

**Anomaly Alerts:**
- Coordinated voting patterns
- Suspicious account activity
- Unusual submission patterns

**What it excludes from V1:**
- AI-powered content moderation (human review only)
- Real-time chat support for users
- Advanced user segmentation or targeting
- A/B testing infrastructure

**Success Criteria:**
- Moderation queue < 24 hour turnaround
- < 5% questions inappropriately rejected (audit)
- City admin rates console 4/5 or higher (usability)

---

### 4. Ranking Algorithm

**What it includes:**

**Portfolio-Based Ranking:**
- Issue buckets (housing, education, safety, etc.)
- Viewpoint clustering (prevents one faction dominance)
- Minority concern slots (10% reserved)
- Recency bonus (newer questions get slight boost)

**Anomaly Detection:**
- Flag coordinated voting (same IP, rapid votes, lockstep patterns)
- Downweight suspicious votes
- Human review for borderline cases

**Transparency:**
- "Why this ranking?" tooltip for every question
- Public algorithm documentation (GitHub)
- City admin can export ranking data for audit

**What it excludes from V1:**
- Machine learning for clustering (rule-based clustering only)
- User personalization (same ranking for everyone)
- Real-time ranking updates (updates every 15 minutes)

**Success Criteria:**
- Top 10 represents ≥ 3 different issue categories
- No single viewpoint cluster occupies > 40% of top 100
- Voter trust in ranking fairness: 75%+ (survey)

---

### 5. Video Pipeline

**What it includes:**

**Recording:**
- In-browser recording (MediaRecorder API)
- 1-3 minute time limit
- Visual countdown timer
- Question text displayed during recording

**Processing (Celery Background Jobs):**
- Transcode to HLS + MP4 (480p, 720p, 1080p)
- Generate captions (Whisper or Deepgram)
- Create thumbnail from first frame
- Compute SHA-256 hash for provenance

**Provenance Tracking:**
- Recording timestamp
- Candidate account ID
- Device fingerprint (hashed)
- IP address (hashed)

**Delivery:**
- CDN-backed video delivery (S3 + CloudFront)
- Adaptive bitrate streaming (HLS)
- Caption file (VTT) for accessibility

**What it excludes from V1:**
- Live streaming
- Video editing tools
- Rebuttal videos (text rebuttals only)
- User-uploaded videos (candidates record in-app only)

**Success Criteria:**
- Video processing completes within 5 minutes
- Captions accuracy ≥ 90%
- Video playback on 3G connections (480p)

---

### 6. Verification System

**What it includes:**

**Email Verification:**
- Send verification code via email
- Code expires in 15 minutes
- Rate limiting (3 attempts per email)

**SMS Verification (Optional):**
- Send verification code via Twilio
- Code expires in 10 minutes
- Phone number not stored (hashed for fraud detection)

**City-Configurable:**
- Cities choose which methods to enable
- Can add custom verification (e.g., city voter registration lookup)

**What it excludes from V1:**
- ID.me integration (planned for V2)
- Facial recognition verification
- Social media account linking
- Credit card verification

**Success Criteria:**
- 90%+ verification success rate (automated)
- < 10% false positives (legitimate users blocked)
- < 5% false negatives (bots/duplicates verified)

---

## Non-Goals for V1

CivicQ V1 is **not:**

1. **A voting system:** We do not collect votes for elected office
2. **A debate platform:** No live video, no real-time responses
3. **A social network:** No profiles, followers, comments, or feeds
4. **A news aggregator:** No third-party content or curated news
5. **A fundraising tool:** No donation buttons or ActBlue integration
6. **A nationwide platform:** One pilot city only in V1
7. **A mobile app:** Responsive web only (no native iOS/Android)
8. **Multi-language:** English + Spanish only in V1

---

## Success Metrics

### Voter Success

**Primary:**
- 75%+ voters "understand candidates better after using CivicQ"
- 70%+ voters "trust information on CivicQ"
- 50%+ eligible voters create account (awareness)

**Secondary:**
- 10+ videos watched per voter (engagement)
- 30%+ voters submit or vote on questions (participation)

### Candidate Success

**Primary:**
- 80%+ candidates participate (answer ≥ 1 question)
- 50%+ candidates answer top 10 questions
- 85%+ candidates "feel process is fair"

**Secondary:**
- Avg 12 answers per candidate
- 75%+ answers include source citations

### Platform Success

**Primary:**
- Zero trust violations (manipulation, bias, security breaches)
- 95%+ uptime during election period
- <500ms API response time (p95)

**Secondary:**
- 1000+ questions submitted
- 10,000+ votes cast
- 50,000+ video views

### City Success

**Primary:**
- City admin rates platform 4/5 or higher
- City recommends to other cities (NPS ≥ 50)
- Zero election-critical incidents

**Secondary:**
- Local press coverage (≥ 3 positive articles)
- Candidates mention CivicQ in campaigns
- Voter turnout increase (measured against historical data)

---

## Out of Scope (Planned for V2)

**Features explicitly excluded from V1:**

1. **Rebuttal Videos:** Candidates can rebut in text only (V1), video rebuttals in V2
2. **Issue Pages:** Dedicated issue landing pages (e.g., "All answers on housing")
3. **Voter Endorsements:** Users cannot endorse candidates
4. **Campaign Integration:** No API for campaigns to embed on their websites
5. **Advanced Analytics:** Sentiment analysis, topic modeling, trend detection
6. **Multi-City Management:** Each city is standalone instance in V1
7. **Open API:** Public API for researchers and civic groups
8. **Real-Time Notifications:** Email/SMS alerts for new answers or questions

---

## Technical Debt Acceptable for V1

To ship on time, we accept these technical shortcuts:

**Database:**
- Single PostgreSQL instance (no sharding)
- No read replicas (vertical scaling only)
- Basic indexes (can optimize later)

**Backend:**
- Monolithic API (no microservices)
- Synchronous processing where acceptable
- Basic error handling (not comprehensive retry logic)

**Frontend:**
- No state management library (Context API sufficient)
- No advanced caching (React Query default behavior)
- Basic responsive design (can polish later)

**Infrastructure:**
- Manual deployments acceptable (CI/CD nice-to-have)
- Single region deployment
- No blue-green deployments

**Monitoring:**
- Sentry for errors (no full observability stack)
- Manual log review (no aggregation/alerts)
- Basic uptime monitoring (no distributed tracing)

**These will be addressed in V1.1 and V2 based on pilot learnings.**

---

## Launch Criteria

CivicQ V1 is ready to launch when:

**Functional:**
- ✅ All V1 features implemented and tested
- ✅ Voter can complete full flow (find ballot → watch videos → submit question)
- ✅ Candidate can complete full flow (verify → record → publish)
- ✅ Admin can moderate queue in < 24 hours

**Quality:**
- ✅ No critical bugs
- ✅ < 10 high-priority bugs
- ✅ Accessibility: WCAG 2.1 AA compliant
- ✅ Performance: p95 response time < 500ms

**Security:**
- ✅ Security audit completed with no critical findings
- ✅ Penetration testing passed
- ✅ HTTPS enabled with valid cert
- ✅ Data encryption at rest and in transit

**Trust:**
- ✅ All code open-sourced
- ✅ Transparency report template ready
- ✅ Privacy policy and ToS finalized
- ✅ Ranking algorithm documented and auditable

**Operational:**
- ✅ City admin trained on console
- ✅ Help center and FAQs published
- ✅ Incident response plan documented
- ✅ Backup and recovery tested

---

## Pilot City Selection Criteria

**Ideal Pilot City:**
- Population: 10,000 - 100,000 (manageable scale)
- Election: City council or mayor race (3-5 candidates)
- Timing: 6 months to election day (enough time for adoption)
- Tech-savvy: City has election website and social media presence
- Supportive: City clerk/manager enthusiastic about transparency
- Diverse: Mix of demographics, neighborhoods, viewpoints

**Red Flags:**
- Highly partisan city (CivicQ may be politicized)
- No internet access for significant population
- Contentious election with litigation risk
- City staff resistant to technology change

---

## Post-V1 Roadmap

**V1.1 (Bug Fixes + Polish):**
- Fix bugs discovered in pilot
- Performance optimizations
- UX improvements based on feedback

**V1.2 (Scale Improvements):**
- Read replicas for database
- CDN optimization
- Admin bulk operations

**V2 (Feature Expansion):**
- Rebuttal videos
- Issue pages
- Multi-city support
- Advanced analytics
- Open API

---

**For detailed roadmap, see [ROADMAP.md](ROADMAP.md)**

---

**Last Updated:** 2026-02-14
**Next Review:** After pilot city confirmed
