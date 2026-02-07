# CivicQ Database Schema

## Overview

The CivicQ database schema is designed around the core principle of **integrity-first civic engagement**. Every table supports one of these goals:

1. **Verified participation** - Users, verification, voting
2. **Structured content** - Ballots, contests, questions, answers
3. **Anti-manipulation** - Anomaly detection, moderation, audit logging
4. **Transparency** - Public records, versioning, chain of custody

## Core Entities

### Users & Verification

#### `users`
Represents all users in the system (voters, candidates, admins, moderators).

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| email | STRING | Unique email address |
| hashed_password | STRING | Bcrypt hashed password |
| full_name | STRING | User's full name (optional) |
| phone_number | STRING | Phone number (optional) |
| role | ENUM | voter/candidate/admin/moderator/city_staff |
| is_active | BOOLEAN | Account status |
| is_superuser | BOOLEAN | Superuser flag |
| city_id | STRING | City identifier for scoping |
| city_name | STRING | City name |
| verification_status | ENUM | pending/verified/rejected/expired |
| verification_token | STRING | Minimal verification token |
| last_active | DATETIME | Last activity timestamp |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Update timestamp |

**Indexes:** email, city_id

#### `verification_records`
Stores minimal verification data for user identity proofing.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| user_id | INTEGER | Foreign key to users |
| method | ENUM | sms/email/mail_code/voter_roll/id_proofing |
| provider | STRING | Verification provider (e.g., "twilio") |
| city_scope | STRING | City scope |
| status | ENUM | pending/verified/rejected/expired |
| metadata | JSON | Non-sensitive verification metadata |
| verified_at | DATETIME | Verification timestamp |
| expires_at | DATETIME | Expiration timestamp |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Update timestamp |

**Indexes:** user_id, city_scope

### Ballots & Contests

#### `ballots`
Represents an election ballot for a specific city.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| city_id | STRING | City identifier |
| city_name | STRING | City name |
| election_date | DATE | Election date |
| version | INTEGER | Ballot version |
| source_metadata | JSON | Source of ballot data |
| is_published | BOOLEAN | Publication status |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Update timestamp |

**Indexes:** city_id, election_date

#### `contests`
Represents a race or ballot measure within an election.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| ballot_id | INTEGER | Foreign key to ballots |
| type | ENUM | race/measure |
| title | STRING | Contest title |
| jurisdiction | STRING | Jurisdiction |
| office | STRING | Office name (for races) |
| seat_count | INTEGER | Number of seats (for multi-seat races) |
| description | TEXT | Contest description |
| display_order | INTEGER | Display order |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Update timestamp |

**Indexes:** ballot_id

#### `candidates`
Represents a candidate in a race.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| contest_id | INTEGER | Foreign key to contests |
| user_id | INTEGER | Foreign key to users (optional) |
| name | STRING | Candidate name |
| filing_id | STRING | Official filing ID |
| email | STRING | Contact email |
| phone | STRING | Contact phone |
| status | ENUM | pending/verified/active/withdrawn/disqualified |
| profile_fields | JSON | Flexible profile data |
| photo_url | STRING | Profile photo URL |
| website | STRING | Website URL |
| identity_verified | BOOLEAN | Identity verification status |
| identity_verified_at | DATE | Identity verification date |
| display_order | INTEGER | Display order |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Update timestamp |

**Indexes:** contest_id, user_id, filing_id

#### `measures`
Represents a ballot measure.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| contest_id | INTEGER | Foreign key to contests |
| measure_number | STRING | Measure number (e.g., "Prop 1") |
| measure_text | TEXT | Full measure text |
| summary | TEXT | Summary |
| fiscal_notes | TEXT | Fiscal impact notes |
| pro_statement | TEXT | Pro argument |
| con_statement | TEXT | Con argument |
| pro_contacts | JSON | Pro side contacts |
| con_contacts | JSON | Con side contacts |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Update timestamp |

**Indexes:** contest_id

### Questions & Voting

#### `questions`
Represents a question asked by voters for candidates to answer.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| contest_id | INTEGER | Foreign key to contests |
| author_id | INTEGER | Foreign key to users |
| current_version_id | INTEGER | Current version ID |
| question_text | TEXT | Question content |
| issue_tags | ARRAY(STRING) | Issue tags |
| status | ENUM | pending/approved/merged/removed |
| cluster_id | INTEGER | Cluster ID for deduplication |
| embedding | VECTOR(384) | Sentence embedding |
| context | TEXT | Optional context ("why this matters") |
| upvotes | INTEGER | Upvote count |
| downvotes | INTEGER | Downvote count |
| rank_score | FLOAT | Composite ranking score |
| representation_metadata | JSON | Geographic/demographic distribution |
| is_flagged | INTEGER | Flag count |
| moderation_notes | TEXT | Moderation notes |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Update timestamp |

**Indexes:** contest_id, author_id, status, cluster_id, rank_score, issue_tags, embedding (ivfflat)

#### `question_versions`
Tracks edit history of questions.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| question_id | INTEGER | Foreign key to questions |
| version_number | INTEGER | Version number |
| question_text | TEXT | Question text for this version |
| edit_author_id | INTEGER | Foreign key to users |
| edit_reason | TEXT | Reason for edit |
| diff_metadata | JSON | What changed |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Update timestamp |

**Indexes:** question_id

#### `votes`
Represents upvote/downvote on questions.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| user_id | INTEGER | Foreign key to users |
| question_id | INTEGER | Foreign key to questions |
| value | INTEGER | +1 for upvote, -1 for downvote |
| device_risk_score | FLOAT | Anomaly detection score |
| weight | FLOAT | Vote weight (can be downweighted) |
| metadata | JSON | Device info, IP hash (non-PII) |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Update timestamp |

**Indexes:** user_id, question_id
**Unique Constraint:** (user_id, question_id)

### Video Answers & Rebuttals

#### `video_answers`
Represents a candidate's video answer to a question.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| candidate_id | INTEGER | Foreign key to candidates |
| question_id | INTEGER | Foreign key to questions |
| question_version_id | INTEGER | Foreign key to question_versions |
| video_asset_id | STRING | S3 key or storage ID |
| video_url | STRING | CDN URL |
| duration | FLOAT | Duration in seconds |
| transcript_id | STRING | Transcript ID |
| transcript_text | TEXT | Full transcript |
| transcript_url | STRING | VTT/SRT file URL |
| captions_url | STRING | Captions URL |
| provenance_hash | STRING | Hash of raw video |
| authenticity_metadata | JSON | Chain of custody |
| status | ENUM | draft/processing/published/withdrawn |
| position_summary | TEXT | Extracted position |
| rationale | TEXT | Extracted rationale |
| tradeoff_acknowledged | TEXT | Extracted tradeoff |
| implementation_plan | TEXT | Extracted implementation |
| measurement_criteria | TEXT | Extracted measurement |
| values_statement | TEXT | Extracted values |
| is_open_question | BOOLEAN | "I don't know yet" flag |
| has_correction | BOOLEAN | Correction flag |
| correction_text | TEXT | Correction text |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Update timestamp |

**Indexes:** candidate_id, question_id

#### `rebuttals`
Represents a candidate's rebuttal to another candidate's answer.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| candidate_id | INTEGER | Foreign key to candidates |
| target_answer_id | INTEGER | Foreign key to video_answers |
| target_claim_text | TEXT | Quoted claim being rebutted |
| target_claim_timestamp | FLOAT | Timestamp in target video |
| video_asset_id | STRING | S3 key or storage ID |
| video_url | STRING | CDN URL |
| duration | FLOAT | Duration in seconds |
| transcript_id | STRING | Transcript ID |
| transcript_text | TEXT | Full transcript |
| transcript_url | STRING | VTT/SRT file URL |
| status | ENUM | draft/processing/published/withdrawn |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Update timestamp |

**Indexes:** candidate_id, target_answer_id

#### `claims`
Represents extracted claims with optional sources.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| answer_id | INTEGER | Foreign key to video_answers |
| claim_snippet | TEXT | Extracted claim text |
| claim_timestamp | FLOAT | Timestamp in video |
| sources | JSON | Array of source objects |
| is_verified | BOOLEAN | Verification status |
| reviewer_notes | TEXT | Reviewer notes |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Update timestamp |

**Indexes:** answer_id

### Moderation & Audit

#### `reports`
Allows users to report content for moderation review.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| reporter_id | INTEGER | Foreign key to users |
| target_type | STRING | question/answer/rebuttal |
| target_id | INTEGER | ID of target content |
| reason | ENUM | spam/doxxing/threats/harassment/off_topic/misinformation/other |
| description | TEXT | Report description |
| status | ENUM | pending/under_review/resolved/dismissed |
| resolved_by_id | INTEGER | Foreign key to users |
| resolution_notes | TEXT | Resolution notes |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Update timestamp |

**Indexes:** reporter_id, status

#### `moderation_actions`
Records all moderation actions for transparency.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| target_type | STRING | Type of content acted upon |
| target_id | INTEGER | ID of target content |
| action_type | ENUM | approve/remove/merge/flag/warn_user/suspend_user |
| moderator_id | INTEGER | Foreign key to users |
| rationale_code | STRING | Published moderation standard code |
| rationale_text | TEXT | Rationale text |
| report_id | INTEGER | Foreign key to reports |
| is_public | BOOLEAN | Public visibility flag |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Update timestamp |

**Indexes:** moderator_id, target_id

#### `audit_logs`
Immutable event stream for integrity-sensitive operations.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| event_type | ENUM | Various event types |
| actor_id | INTEGER | Foreign key to users |
| target_type | STRING | Type of target |
| target_id | INTEGER | ID of target |
| event_data | JSON | Event details |
| ip_address_hash | STRING | Hashed IP address |
| user_agent | STRING | User agent |
| city_scope | STRING | City scope |
| severity | STRING | info/warning/critical |
| created_at | DATETIME | Creation timestamp |

**Indexes:** event_type, actor_id, city_scope

### User Engagement

#### `follows`
Allows users to follow contests, candidates, or issue tags.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| user_id | INTEGER | Foreign key to users |
| target_type | ENUM | contest/candidate/issue_tag |
| target_id | INTEGER | ID of target (null for issue tags) |
| target_value | STRING | Value for issue tags |
| notification_prefs | JSON | Notification preferences |
| is_active | BOOLEAN | Active status |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Update timestamp |

**Indexes:** user_id
**Unique Constraint:** (user_id, target_type, target_id, target_value)

## Key Design Decisions

### 1. Vector Search for Question Deduplication
Uses pgvector extension for semantic similarity search to detect duplicate questions.

### 2. Question Versioning
Transparent edit history ensures answers bind to specific question versions, preventing "bait-and-switch."

### 3. Minimal PII Storage
Verification records store minimal metadata. Sensitive documents are processed by providers and never stored.

### 4. Anomaly Detection Metadata
Votes include device risk scores and weights to enable downweighting of suspicious activity.

### 5. Immutable Audit Log
All integrity-sensitive events are logged immutably for transparency and compliance.

### 6. Polymorphic Target References
Reports, moderation actions, and follows use polymorphic references (target_type + target_id) for flexibility.

## Migration Strategy

1. Create core tables (users, ballots, contests)
2. Add verification and voting tables
3. Add question and answer tables
4. Add moderation and audit tables
5. Add vector search indexes
6. Add follows and engagement tables

## Backup and Retention

- **Full backups:** Daily
- **Point-in-time recovery:** 30 days
- **Audit logs:** Retained indefinitely
- **Video content:** Retained per city policy (typically post-election + 2 years)
