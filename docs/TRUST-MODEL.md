# CivicQ Trust Model

**Status:** FOUNDATIONAL - Product Identity
**Owner:** Product + Engineering + Legal
**Last Updated:** 2026-02-14

---

## Overview

Trust is not a marketing message. Trust is a product feature.

Voters don't trust political platforms. They don't trust social media. They don't trust anything that looks like it could be manipulated by money, algorithms, or faction warfare. CivicQ's survival depends on building a system that is auditable, boringly transparent, and demonstrably fair.

**Core Thesis:**
CivicQ wins if and only if it becomes the first civic Q&A platform that voters, candidates, and election officials can actually trust—not because we say so, but because the system makes trust verifiable.

This document defines the CivicQ trust model: the commitments we make, how we make them visible, and how we measure whether we're keeping them.

---

## The Trust Problem

### Why Voters Don't Trust Platforms

**Psychological Factors:**
1. **Manipulation fear:** Algorithms optimized for engagement, not truth
2. **Loss of control:** Uncertainty about what's real vs. AI-generated or edited
3. **Pay-to-win anxiety:** Suspicion that money buys visibility
4. **Faction warfare:** Platforms that reward outrage and mob dominance
5. **Data misuse fear:** Personal information used for targeting or manipulation
6. **Deepfake paranoia:** Videos that can't be trusted

**CivicQ's Unique Vulnerabilities:**
- Handles election information (high-stakes, high-scrutiny)
- Involves candidates who have incentive to game the system
- Relies on user-generated content (questions) that could be astroturfed
- Uses video (deepfakes are an existential threat)
- Implements ranking algorithms (vulnerable to "it's rigged" claims)
- Serves diverse political viewpoints (any perceived bias is fatal)

**The Stakes:**
If we get trust wrong, we don't just lose users. We undermine democracy, enable misinformation, and poison civic discourse.

---

## The CivicQ Trust Model: Core Commitments

### Commitment 1: No Pay-to-Win, Ever

**What It Means:**
Every candidate gets equal visibility. There are no ads, no boosting, no sponsored placements, no premium tiers. A candidate with $10 gets the same opportunity to answer questions as a candidate with $1 million.

**Why It Matters:**
The moment candidates can buy visibility, the platform becomes just another campaign spending channel. Voters will (correctly) assume that what they see is determined by money, not merit.

**How We Deliver It:**

**Technical Implementation:**
- All candidates appear in the same list for each contest
- Candidate order is randomized on each page load (no fixed "top" candidate)
- No featured or promoted answers
- No advertising of any kind on the platform
- No monetization based on visibility or engagement

**Business Model Constraint:**
- Revenue comes from cities (B2G subscription), not candidates or voters
- Cities pay a flat fee based on population, not per-candidate or per-engagement
- No pay-per-question, pay-per-video, or performance-based pricing
- Open-source algorithm ensures no hidden preferencing

**Visibility:**
- Public pricing page shows exactly what cities pay
- Transparency report shows revenue sources
- Algorithm code is open-source and auditable
- No private deals or special arrangements

**Measurement:**
- Regular audits of candidate exposure (should be statistically equal)
- Public reports on candidate participation rates
- Zero tolerance for pay-to-win features (board/governance decision required)

---

### Commitment 2: Verified Video Provenance (No Editing, No Deepfakes)

**What It Means:**
All candidate videos are recorded in-app with cryptographic signing. Candidates cannot upload pre-recorded or edited videos. Every video is verifiably authentic from the moment it's recorded.

**Why It Matters:**
In the deepfake era, "here's a video of the candidate saying X" is not enough. Voters need proof that the video is authentic, unedited, and recorded by the candidate (not AI or an impersonator).

**How We Deliver It:**

**Technical Implementation:**
- **In-app recording only:**
  - Candidates record directly in the browser or app
  - MediaRecorder API captures video stream
  - No upload of external files (exception: accessibility accommodations)

- **Cryptographic signing:**
  - SHA-256 hash generated at recording time
  - Hash stored in database and displayed with video
  - Re-hash on every playback; if hash doesn't match, video is flagged

- **Metadata capture:**
  - Recording timestamp (server-verified)
  - Device fingerprint (not stored, but used for anomaly detection)
  - IP address (hashed for fraud detection, not stored raw)
  - Candidate account ID linked to verified identity

- **Tamper detection:**
  - If video file is modified, hash will change
  - Automatic flag if hash mismatch detected
  - Human review for flagged videos

- **Content Authenticity:**
  - Future: C2PA (Coalition for Content Provenance and Authenticity) integration
  - Embeds provenance metadata directly in video file
  - Verifiable by third-party tools

**User Visibility:**
- Every video displays "Recorded in CivicQ on [date]"
- "Verify authenticity" button shows hash and metadata
- Public API endpoint to verify any video hash
- Transparency log of all videos with hashes

**Accessibility Accommodation:**
- Candidates with disabilities may request alternative recording methods
- All accommodations are documented and disclosed
- Videos recorded externally are clearly labeled as such

**Measurement:**
- 100% of videos recorded in-app (with disclosed exceptions)
- Zero successful deepfakes or manipulated videos
- Public audit log of all video verifications

---

### Commitment 3: Transparent and Auditable Ranking

**What It Means:**
The algorithm that determines "top questions" is open-source, auditable, and explained in plain language. Anyone can see exactly how rankings are calculated, and city admins can verify that the algorithm is running as documented.

**Why It Matters:**
If voters think the ranking is rigged by bots, faction dominance, or platform manipulation, they won't trust the questions—and they'll assume candidates are only answering softballs.

**How We Deliver It:**

**Technical Implementation:**

**Open-Source Algorithm:**
- Ranking code is in public GitHub repository
- Cities can inspect, audit, or run the code themselves
- Algorithm versioning: any changes are documented in changelog
- No hidden factors or proprietary "secret sauce"

**Portfolio-Based Ranking:**
- Questions are not ranked purely by upvotes (prevents mob dominance)
- Issue buckets ensure diversity (e.g., 30% housing, 20% education, etc.)
- Viewpoint clustering prevents one faction from flooding top 100
- Minority concern slots ensure smaller groups are heard

**Anomaly Detection:**
- Coordinated voting is automatically flagged
- Suspicious patterns (same IP, rapid voting, lockstep behavior) are downweighted
- Human review for edge cases

**Transparency Dashboard:**
- Shows how top 100 is distributed across issues
- Shows viewpoint clusters and how questions are grouped
- Displays anomaly flags and moderation actions
- Available to voters, candidates, and city admins

**User Visibility:**
- Every question shows "Why this ranking?" tooltip
  - Example: "Ranked #3. High support across multiple neighborhoods. Flagged by 12 voters as important. Part of housing issue bucket (25% of top 100)."
- Public FAQ explains algorithm in plain language
- City admins can export ranking data for independent analysis

**Measurement:**
- Issue diversity score (top 100 should reflect community priorities, not one issue)
- Viewpoint balance score (no single cluster dominates)
- Anomaly detection accuracy (% of flagged votes correctly identified)
- Voter trust in ranking fairness (quarterly survey)

---

### Commitment 4: Political Neutrality (Non-Partisan Infrastructure)

**What It Means:**
CivicQ is civic infrastructure, not a political actor. We do not endorse candidates, parties, or policies. We do not design features to favor any political viewpoint.

**Why It Matters:**
If the platform is perceived as biased toward one party or ideology, it loses credibility with half the electorate—and election officials won't adopt it.

**How We Deliver It:**

**Governance:**
- Board includes representatives from across political spectrum
- No partisan donations or endorsements
- Open governance model (decisions documented publicly)
- Independent audit of neutrality (annual)

**Product Design:**
- Features are designed for fairness, not outcomes
- No "nudges" or defaults that favor specific viewpoints
- Issue tags are neutral (e.g., "housing policy" not "affordable housing crisis")
- Moderation policy is viewpoint-neutral (enforce civility, not ideology)

**Moderation:**
- Content moderation is rules-based, not viewpoint-based
- Rules: no harassment, threats, spam, off-topic content
- No censorship of political viewpoints (unless they violate rules)
- Appeals process for moderation decisions
- Transparency report on moderation actions

**Data and Analytics:**
- No profiling voters by political affiliation
- No targeted messaging based on ideology
- No predictive models for "likely Trump voter" or "likely progressive"
- Analytics are aggregate and anonymized

**User Visibility:**
- Public neutrality commitment on homepage
- Transparency report shows moderation by rule type (not ideology)
- Board composition and governance documents are public
- Open invitation for neutral third-party audits

**Measurement:**
- Candidate participation rate (should be equal across parties)
- Voter trust in neutrality (quarterly survey)
- Moderation actions distribution (should not favor one viewpoint)
- Third-party audit score (annual)

---

### Commitment 5: Privacy and Data Minimization

**What It Means:**
We collect the minimum data necessary to operate the platform. User data is not sold, shared, or used for purposes other than running CivicQ. Voters can participate anonymously where appropriate.

**Why It Matters:**
Voters fear that their political engagement data will be used against them—for targeting, profiling, or doxxing. Trust requires strict privacy protections.

**How We Deliver It:**

**Data Collection:**
- **What we collect:**
  - Email (for account creation and verification)
  - Address (for ballot matching, can be hashed)
  - Verification status (boolean, not verification details)
  - Questions submitted (anonymized after submission)
  - Votes (anonymized after ranking stabilizes)
  - Videos watched (aggregate analytics only, not per-user tracking)

- **What we don't collect:**
  - Political affiliation
  - Browsing history
  - Social media profiles
  - Third-party tracking data
  - Detailed behavioral analytics

**Data Retention:**
- Account data: Retained until user deletes account
- Questions and answers: Permanent public record (election archive)
- Votes: Anonymized after 30 days or when ranking stabilizes
- PII: Deleted 90 days after election (configurable by city)
- Logs: 30 days for debugging, then deleted (audit logs: 7 years)

**Data Usage:**
- Only used to operate CivicQ (not for marketing, profiling, or third-party purposes)
- Aggregate analytics only (no individual-level data)
- No selling of data, ever
- No sharing with third parties (except legal requirements or city partners)

**Privacy Controls:**
- Users can delete their account and data at any time
- Users can export their data (GDPR/CCPA compliance)
- Users can participate anonymously (watch videos without account)
- Verified users: voting is anonymous (we track that you voted, not how)

**User Visibility:**
- Clear privacy policy in plain language
- Privacy dashboard shows what data we have
- Transparency report on data requests and breaches
- No dark patterns or hidden data collection

**Measurement:**
- Data minimization score (bytes of PII per user)
- Privacy compliance audit (annual)
- User trust in privacy (quarterly survey)
- Zero data breaches or unauthorized access

---

### Commitment 6: Accessibility and Inclusion

**What It Means:**
CivicQ is designed for all voters, including those with disabilities, limited internet access, or low digital literacy. Accessibility is not an add-on; it's a requirement.

**Why It Matters:**
If the platform is only usable by tech-savvy voters, it reinforces existing inequalities and excludes marginalized communities. Trust requires serving everyone.

**How We Deliver It:**

**Technical Accessibility:**
- WCAG 2.1 AA compliance (minimum)
- Screen reader support
- Keyboard navigation
- Captions for all videos (auto-generated + human review)
- High contrast mode
- Adjustable font sizes
- Mobile-responsive design

**Language Access:**
- English by default
- Spanish translation (priority for pilot cities)
- Additional languages based on city demographics
- Plain language (no jargon or legalese)

**Low-Bandwidth Support:**
- Works on 3G connections
- Lightweight pages (< 500 KB)
- Low-res video options
- Offline-friendly (cache ballots for later viewing)

**Digital Literacy:**
- Simple, intuitive UI
- Onboarding guide and tooltips
- Help center with FAQs
- Phone support for cities with dedicated helpline

**User Visibility:**
- Accessibility statement on homepage
- Feedback mechanism for accessibility issues
- Regular usability testing with diverse users
- Accessibility champion on every release

**Measurement:**
- WCAG compliance score (100% AA, target AAA)
- Accessibility issue resolution time (< 48 hours for critical)
- User satisfaction across demographics (no disparities)
- Third-party accessibility audit (annual)

---

## Trust as a Measurable Feature

### Trust Metrics Dashboard

We track trust as a first-class product metric:

**Voter Trust Score:**
- % of voters who "trust information on CivicQ" (quarterly survey)
- Target: 80%+ by end of pilot
- Benchmarked against local news, social media, official election websites

**Candidate Trust Score:**
- % of candidates who "believe CivicQ is fair" (end-of-election survey)
- Target: 90%+ (higher than voter score, since candidates scrutinize fairness closely)

**Election Official Trust Score:**
- % of election officials who "would recommend CivicQ to other cities" (NPS)
- Target: 80%+ NPS score

**Transparency Index:**
- Weighted score across: open-source code, public pricing, transparency reports, audit availability
- Target: 100% (all commitments met)

**Incident Response:**
- Time to detect and fix trust violations (deepfakes, manipulation, bias)
- Target: < 24 hours for critical incidents

---

## What Breaks Trust

### Red Lines (Zero Tolerance)

These actions would be fatal to trust and are **never acceptable:**

1. **Selling user data or candidate data** to third parties
2. **Secret deals with candidates** for preferential treatment
3. **Hidden algorithm changes** without public documentation
4. **Accepting political donations** from candidates or parties
5. **Introducing pay-to-win features** (ads, boosting, sponsored content)
6. **Manipulating rankings** to favor specific viewpoints
7. **Allowing edited videos** without clear disclosure
8. **Collecting unnecessary personal data** without consent
9. **Sharing data with law enforcement** without legal requirement and disclosure
10. **Ignoring accessibility** or excluding marginalized groups

### How We Enforce Red Lines

- Governance: Board must approve any changes to trust commitments
- Legal: Contracts prohibit trust violations (city agreements include trust guarantees)
- Technical: Code reviews and automated checks for trust violations
- Public: Any trust violation is disclosed immediately with remediation plan

---

## Earning Trust Over Time

### Phase 1: Pilot City (Months 0-6)
**Goal:** Prove trustworthiness in controlled environment

**Actions:**
- Publish all source code (backend, frontend, ranking algorithm)
- Run transparency reports (monthly)
- Conduct third-party security audit
- Invite independent monitoring of ranking algorithm
- Survey voters and candidates on trust

**Success Criteria:**
- 70%+ voter trust score
- 85%+ candidate trust score
- Zero trust violations
- Positive press coverage on transparency

---

### Phase 2: Expansion (Months 6-18)
**Goal:** Scale trust model to multiple cities

**Actions:**
- Annual third-party neutrality audit
- Publish annual transparency report
- Open governance model (public board meetings)
- Community feedback mechanism
- Bug bounty program for trust violations

**Success Criteria:**
- 80%+ voter trust score
- 90%+ candidate trust score
- Trusted by election officials in 10+ cities
- Featured as case study in civic tech community

---

### Phase 3: Institutionalization (Months 18+)
**Goal:** CivicQ becomes default civic infrastructure

**Actions:**
- Legal protections (nonprofit status or public benefit corp)
- Independent oversight board
- Open data initiative (anonymized dataset for researchers)
- Standards body for civic Q&A platforms

**Success Criteria:**
- 85%+ voter trust score (higher than local news)
- Adoption by 100+ cities
- Cited as model for trustworthy civic tech
- Sustained zero trust violations

---

## Transparency Reporting

### Quarterly Transparency Report

Published every quarter, includes:

**Usage Stats:**
- Cities served
- Voters registered
- Questions submitted
- Answers published
- Videos watched

**Trust Metrics:**
- Voter trust score
- Candidate trust score
- Election official NPS

**Moderation:**
- Questions flagged / approved / rejected
- Voting anomalies detected / resolved
- User appeals / resolutions

**Security:**
- Security incidents (if any)
- Deepfake attempts (if any)
- Data breach attempts (if any)

**Financial:**
- Revenue sources (by city, anonymized)
- Operating costs
- Donations (if any)
- Third-party funding (if any)

---

## Accountability and Recourse

### If We Break Trust

**Disclosure:**
- Immediate public disclosure of trust violation
- Clear explanation of what happened and why
- Timeline of events

**Remediation:**
- Immediate fix if possible
- Long-term systemic changes to prevent recurrence
- Independent review of root cause

**Accountability:**
- Responsible parties identified (if internal failure)
- Governance changes if structural issue
- Legal recourse if contractual violation (for cities)

**User Recourse:**
- Users can delete accounts and data
- Cities can terminate contracts
- Public apology and commitment to improvement

---

## Living Commitment

This trust model is a living document. We will:
- Review annually
- Update based on lessons learned
- Solicit feedback from voters, candidates, and election officials
- Adapt to new threats (AI, deepfakes, manipulation techniques)

**Trust is earned daily. It can be lost in an instant. We treat it as our most important product feature.**

---

**For related policies, see:**
- [Privacy Policy](PRIVACY.md)
- [Security Policy](../SECURITY.md)
- [Code of Conduct](../CODE_OF_CONDUCT.md)

---

**Last Updated:** 2026-02-14
**Next Review:** 2026-08-14 (6 months) or after first pilot election
