# CivicQ Privacy Framework

**Status:** FOUNDATIONAL - Privacy Policy
**Owner:** Legal + Engineering + Product
**Last Updated:** 2026-02-14

---

## Overview

CivicQ is committed to protecting user privacy while enabling transparent civic engagement. This document outlines our privacy framework, data handling practices, and user rights.

**Core Privacy Principle:** Collect only what's necessary, protect what we collect, delete what we don't need.

---

## Data We Collect

### Voter Accounts

**Required Data:**
- Email address (for account creation and verification)
- Password (hashed with bcrypt, never stored in plain text)
- Address (for ballot matching, can be geocoded and hashed)

**Optional Data:**
- Phone number (if SMS verification chosen)
- Name (optional, for personalization)

**Generated Data:**
- Account ID (UUID)
- Verification status (boolean)
- Created/updated timestamps

### Question Submission

**Stored:**
- Question text
- Issue tags
- Context (optional)
- Submission timestamp

**Anonymized:**
- After submission approved, link to user ID is removed
- Questions become part of public record, attribution removed

### Question Voting

**Stored:**
- Vote (up/down)
- IP address hash (fraud detection, not reversible)
- User agent hash
- Timestamp

**Anonymized:**
- After 30 days or ranking stabilization, user ID removed
- Only aggregate vote counts remain public

### Video Viewing

**Not Tracked Per-User:**
- We track aggregate view counts (total views per video)
- We do NOT track which specific users watched which videos
- No behavioral profiling or "recommended for you" based on viewing history

---

## Data We DON'T Collect

- Political affiliation or party preference
- Social media profiles
- Third-party tracking pixels
- Browsing history outside CivicQ
- Location data beyond city/district (no GPS tracking)
- Device fingerprinting (except for fraud detection, then hashed)
- Facial recognition data
- Biometric data

---

## How We Use Data

### Account Management
- Email: Login, password reset, verification
- Password: Authentication only
- Address: Ballot matching (determine contests on your ballot)

### Platform Operation
- Questions: Public display, ranking algorithm
- Votes: Ranking calculation, anomaly detection
- Video views: Aggregate analytics (total views, completion rate)

### Security and Fraud Prevention
- IP hash: Detect coordinated voting, bot attacks
- User agent hash: Identify automated submissions
- Verification records: Ensure only verified users vote/submit

### Analytics (Aggregate Only)
- Engagement metrics (total questions, total votes, total views)
- Coverage metrics (% candidates answering top questions)
- Trust metrics (voter confidence surveys)

**We Never:**
- Sell or rent user data
- Share with third parties (except legal requirements)
- Use for political profiling or targeting
- Create individual behavioral profiles

---

## Data Retention

| Data Type | Retention Period | Rationale |
|-----------|------------------|-----------|
| Account info (email, address) | Until account deleted + 30 days | Operational necessity |
| Passwords | Until changed or account deleted | Security |
| Questions | Permanent (public record) | Election archive |
| Answers (videos) | Permanent (public record) | Election archive |
| Votes (user ID link) | 30 days, then anonymized | Fraud detection window |
| Votes (aggregate) | Permanent | Public ranking record |
| IP/UA hashes | 30 days | Fraud detection |
| Audit logs | 7 years | Legal compliance |
| Session data | 7 days | Active session management |

### Post-Election Cleanup

After election + 90 days (configurable by city):
- User PII deleted (email, address, phone)
- Accounts converted to anonymous IDs
- Users can opt to keep account for future elections

---

## User Rights

### Right to Access
- View all data we have about you via privacy dashboard
- Export data in machine-readable format (JSON)

### Right to Deletion
- Delete account and associated data at any time
- Questions/votes remain (anonymized), account info deleted
- Request processed within 30 days

### Right to Correction
- Update email, address, name at any time
- Cannot edit submitted questions (prevents manipulation)

### Right to Portability
- Export your data (questions submitted, votes cast)
- Download in JSON or CSV format

### Right to Object
- Opt out of aggregate analytics
- Request removal from any non-essential processing

### Right to Know
- Transparency dashboard shows what data we collect
- Privacy policy in plain language
- Regular transparency reports

---

## Data Security

### Encryption

**At Rest:**
- Database encryption (PostgreSQL TDE or disk encryption)
- Sensitive fields (email, address) encrypted with AES-256
- Passwords hashed with bcrypt (cost factor 12)

**In Transit:**
- TLS 1.3 for all connections
- HTTPS only (HSTS enabled)
- Certificate pinning (planned)

### Access Controls

**Who Can Access Data:**
- Engineers: Encrypted production access, audit logged
- City admins: Aggregate data only, no PII
- Candidates: Only their own performance data
- Voters: Only their own account data

**Access Logging:**
- All database access logged
- Admin actions audit logged
- Logs reviewed weekly for anomalies

---

## Third-Party Services

### Services We Use

| Service | Purpose | Data Shared | Privacy Policy |
|---------|---------|-------------|----------------|
| Vercel/Netlify | Frontend hosting | None (static files) | [Link] |
| Railway/Render | Backend hosting | All data (encrypted) | [Link] |
| Neon/RDS | Database | All data (encrypted) | [Link] |
| Upstash | Redis cache | Session tokens (encrypted) | [Link] |
| S3/Cloudflare | Video storage/CDN | Videos, metadata | [Link] |
| Whisper/Deepgram | Transcription | Audio only (temporary) | [Link] |
| Sentry | Error tracking | Error messages (no PII) | [Link] |

**All third-party services:**
- Sign Data Processing Agreements (DPA)
- GDPR/CCPA compliant
- No secondary use of data
- Encrypted data transmission

### Services We DON'T Use

- Google Analytics (privacy invasion)
- Facebook Pixel (tracking)
- Third-party ad networks
- Social media login (creates tracking vectors)
- Credit card processing (cities pay directly)

---

## Legal Basis for Processing (GDPR)

- **Account creation:** Contractual necessity
- **Verification:** Legal obligation (election integrity)
- **Question/vote processing:** Legitimate interest (civic engagement)
- **Analytics:** Legitimate interest (platform improvement)
- **Security:** Legal obligation (fraud prevention)

---

## Children's Privacy (COPPA)

CivicQ is not intended for users under 13.

- Account creation requires 18+ age confirmation
- No collection of data from children under 13
- If we discover a child's account, we delete immediately

For 13-17 year olds:
- Parental consent required for account creation
- Limited data collection (email, address only)
- No video viewing tracking

---

## International Users

### GDPR (European Users)

- Full GDPR compliance for EU voters
- Data processing based on consent or legal obligation
- Right to be forgotten, right to portability
- Data Protection Officer contact: [TBD]

### CCPA (California Users)

- Full CCPA compliance for California residents
- Right to know, delete, opt-out
- No sale of personal information
- No discrimination for exercising rights

### Other Jurisdictions

- Privacy practices apply globally
- Comply with local data protection laws
- Data residency requirements (if applicable)

---

## Data Breaches

### Notification

If data breach occurs:
- Notify affected users within 72 hours
- Notify city election officials immediately
- Notify relevant data protection authorities (GDPR/CCPA)
- Public disclosure on website and social media

### Information Provided

- What data was breached
- When breach occurred
- How breach occurred
- Steps we're taking to remediate
- Steps users should take (password reset, etc.)

### Prevention

- Regular security audits
- Penetration testing
- Employee security training
- Incident response plan

---

## Privacy by Design

### Design Principles

1. **Proactive not reactive:** Build privacy in from the start
2. **Privacy as default:** Most privacy-protective settings by default
3. **Privacy embedded:** Into system design, not add-on
4. **Positive-sum:** Privacy doesn't come at cost of functionality
5. **End-to-end security:** Lifecycle protection
6. **Visibility and transparency:** Open about data practices
7. **User-centric:** Respect for user privacy

### Implementation Examples

- Anonymous question submission (no user ID attached)
- Anonymous voting (no "who voted for what" tracking)
- Aggregate-only analytics (no individual tracking)
- Local storage where possible (minimize server data)
- Auto-deletion of unnecessary data (sessions, IP hashes)

---

## Privacy Governance

### Privacy Review Board

- Reviews privacy policy changes
- Approves new data collection
- Investigates privacy complaints
- Conducts privacy audits

### Privacy Impact Assessments

- Required for new features that collect/process data
- Assess risks, mitigations, necessity
- Approved by Privacy Review Board

---

## Contact and Complaints

### Privacy Questions

- Email: privacy@civicq.org (TBD)
- Web form: civicq.org/privacy-contact

### Data Subject Requests

- Access, deletion, correction, portability
- Submit via privacy dashboard or email
- Response within 30 days

### Complaints

- Contact Privacy Review Board
- File complaint with data protection authority (GDPR)
- Contact California Attorney General (CCPA)

---

## Changes to Privacy Policy

We will:
- Notify users of material changes via email
- Post changes on website with effective date
- Maintain version history of privacy policy
- Give users option to delete account if they disagree

---

**For related policies, see:**
- [Trust Model](TRUST-MODEL.md)
- [Security Policy](../SECURITY.md)
- [Terms of Service](../TERMS.md) (TBD)

---

**Last Updated:** 2026-02-14
**Effective Date:** [TBD - upon pilot launch]
**Next Review:** Annually or upon material changes
