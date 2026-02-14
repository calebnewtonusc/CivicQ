# CivicQ Database Schema

Complete schema documentation for the CivicQ database.

## Overview

The CivicQ database contains 16 tables organized into 6 main functional areas:

1. **Users & Verification** (2 tables)
2. **Ballots & Contests** (4 tables)
3. **Questions & Voting** (3 tables)
4. **Answers & Rebuttals** (3 tables)
5. **Moderation** (3 tables)
6. **Social Features** (1 table)

## Table Relationships

```
users
├── verification_records (user_id -> users.id)
├── questions (author_id -> users.id)
├── votes (user_id -> users.id)
├── reports (reporter_id, resolved_by_id -> users.id)
├── follows (user_id -> users.id)
└── candidates (user_id -> users.id)

ballots
└── contests (ballot_id -> ballots.id)
    ├── candidates (contest_id -> contests.id)
    │   ├── video_answers (candidate_id -> candidates.id)
    │   │   ├── claims (answer_id -> video_answers.id)
    │   │   └── rebuttals (target_answer_id -> video_answers.id)
    │   └── rebuttals (candidate_id -> candidates.id)
    ├── measures (contest_id -> contests.id)
    └── questions (contest_id -> contests.id)
        ├── question_versions (question_id -> questions.id)
        ├── votes (question_id -> questions.id)
        └── video_answers (question_id -> questions.id)
```

## Tables

### 1. Users & Verification

#### users
User accounts for voters, candidates, admins, and moderators.

**Columns:**
- `id` (PK) - Integer, auto-increment
- `created_at` - Timestamp
- `updated_at` - Timestamp
- `email` - String, unique, indexed
- `hashed_password` - String
- `full_name` - String, nullable
- `phone_number` - String, nullable
- `role` - Enum (voter, candidate, admin, moderator, city_staff)
- `is_active` - Boolean, default true
- `is_superuser` - Boolean, default false
- `city_id` - String, indexed, nullable
- `city_name` - String, nullable
- `verification_status` - Enum (pending, verified, rejected, expired)
- `verification_token` - String, nullable
- `last_active` - DateTime, nullable

**Indexes:**
- Primary key on `id`
- Unique index on `email`
- Index on `city_id`

#### verification_records
Identity verification records for users.

**Columns:**
- `id` (PK) - Integer
- `created_at` - Timestamp
- `updated_at` - Timestamp
- `user_id` (FK -> users.id, CASCADE) - Integer
- `method` - Enum (sms, email, mail_code, voter_roll, id_proofing)
- `provider` - String, nullable
- `city_scope` - String, indexed
- `status` - Enum (pending, verified, rejected, expired)
- `metadata` - JSON, nullable
- `verified_at` - DateTime, nullable
- `expires_at` - DateTime, nullable

**Indexes:**
- Primary key on `id`
- Index on `city_scope`

### 2. Ballots & Contests

#### ballots
Election ballots for specific cities and dates.

**Columns:**
- `id` (PK) - Integer
- `created_at` - Timestamp
- `updated_at` - Timestamp
- `city_id` - String, indexed
- `city_name` - String
- `election_date` - Date, indexed
- `version` - Integer, default 1
- `source_metadata` - JSON, nullable
- `is_published` - Boolean, default false

**Indexes:**
- Primary key on `id`
- Index on `city_id`
- Index on `election_date`

#### contests
Races or ballot measures within an election.

**Columns:**
- `id` (PK) - Integer
- `created_at` - Timestamp
- `updated_at` - Timestamp
- `ballot_id` (FK -> ballots.id, CASCADE) - Integer
- `type` - Enum (race, measure)
- `title` - String
- `jurisdiction` - String, nullable
- `office` - String, nullable (for races)
- `seat_count` - Integer, default 1, nullable
- `description` - Text, nullable
- `display_order` - Integer, default 0

**Indexes:**
- Primary key on `id`

#### candidates
Candidates running in races.

**Columns:**
- `id` (PK) - Integer
- `created_at` - Timestamp
- `updated_at` - Timestamp
- `contest_id` (FK -> contests.id, CASCADE) - Integer
- `user_id` (FK -> users.id, SET NULL) - Integer, nullable
- `name` - String
- `filing_id` - String, indexed, nullable
- `email` - String, nullable
- `phone` - String, nullable
- `status` - Enum (pending, verified, active, withdrawn, disqualified)
- `profile_fields` - JSON, nullable
- `photo_url` - String, nullable
- `website` - String, nullable
- `identity_verified` - Boolean, default false
- `identity_verified_at` - Date, nullable
- `display_order` - Integer, default 0

**Indexes:**
- Primary key on `id`
- Index on `filing_id`

#### measures
Ballot measures (propositions, referendums).

**Columns:**
- `id` (PK) - Integer
- `created_at` - Timestamp
- `updated_at` - Timestamp
- `contest_id` (FK -> contests.id, CASCADE) - Integer
- `measure_number` - String, nullable
- `measure_text` - Text
- `summary` - Text, nullable
- `fiscal_notes` - Text, nullable
- `pro_statement` - Text, nullable
- `con_statement` - Text, nullable
- `pro_contacts` - JSON, nullable
- `con_contacts` - JSON, nullable

**Indexes:**
- Primary key on `id`

### 3. Questions & Voting

#### questions
Voter-submitted questions for candidates.

**Columns:**
- `id` (PK) - Integer
- `created_at` - Timestamp
- `updated_at` - Timestamp
- `contest_id` (FK -> contests.id, CASCADE) - Integer, indexed
- `author_id` (FK -> users.id, SET NULL) - Integer, nullable
- `current_version_id` - Integer, nullable
- `question_text` - Text
- `issue_tags` - Array of Strings, indexed (GIN)
- `status` - Enum (pending, approved, merged, removed), indexed
- `cluster_id` - Integer, indexed, nullable
- `embedding` - Vector(384), indexed (IVFFlat), nullable
- `context` - Text, nullable
- `upvotes` - Integer, default 0
- `downvotes` - Integer, default 0
- `rank_score` - Float, default 0.0, indexed
- `representation_metadata` - JSON, nullable
- `is_flagged` - Integer, default 0
- `moderation_notes` - Text, nullable

**Indexes:**
- Primary key on `id`
- Index on `contest_id`
- Index on `status`
- Index on `cluster_id`
- Index on `rank_score`
- GIN index on `issue_tags`
- IVFFlat vector index on `embedding` (for similarity search)

**Special Features:**
- Uses pgvector for semantic similarity search
- Supports question clustering and deduplication

#### question_versions
Edit history for questions.

**Columns:**
- `id` (PK) - Integer
- `created_at` - Timestamp
- `updated_at` - Timestamp
- `question_id` (FK -> questions.id, CASCADE) - Integer, indexed
- `version_number` - Integer
- `question_text` - Text
- `edit_author_id` (FK -> users.id, SET NULL) - Integer, nullable
- `edit_reason` - Text, nullable
- `diff_metadata` - JSON, nullable

**Indexes:**
- Primary key on `id`
- Index on `question_id`

#### votes
Upvotes/downvotes on questions by verified users.

**Columns:**
- `id` (PK) - Integer
- `created_at` - Timestamp
- `updated_at` - Timestamp
- `user_id` (FK -> users.id, CASCADE) - Integer, indexed
- `question_id` (FK -> questions.id, CASCADE) - Integer, indexed
- `value` - Integer (+1 for upvote, -1 for downvote)
- `device_risk_score` - Float, default 0.0, nullable
- `weight` - Float, default 1.0 (can be downweighted if suspicious)
- `metadata` - JSON, nullable (device info, IP hash, etc.)

**Indexes:**
- Primary key on `id`
- Index on `user_id`
- Index on `question_id`
- Unique composite index on `(user_id, question_id)` - prevents duplicate votes

### 4. Answers & Rebuttals

#### video_answers
Candidate video answers to questions.

**Columns:**
- `id` (PK) - Integer
- `created_at` - Timestamp
- `updated_at` - Timestamp
- `candidate_id` (FK -> candidates.id, CASCADE) - Integer, indexed
- `question_id` (FK -> questions.id, CASCADE) - Integer, indexed
- `question_version_id` (FK -> question_versions.id, SET NULL) - Integer, nullable
- `video_asset_id` - String
- `video_url` - String, nullable
- `duration` - Float (seconds)
- `transcript_id` - String, nullable
- `transcript_text` - Text, nullable
- `transcript_url` - String, nullable
- `captions_url` - String, nullable
- `provenance_hash` - String, nullable
- `authenticity_metadata` - JSON, nullable
- `status` - Enum (draft, processing, published, withdrawn)
- `position_summary` - Text, nullable
- `rationale` - Text, nullable
- `tradeoff_acknowledged` - Text, nullable
- `implementation_plan` - Text, nullable
- `measurement_criteria` - Text, nullable
- `values_statement` - Text, nullable
- `is_open_question` - Boolean, default false
- `has_correction` - Boolean, default false
- `correction_text` - Text, nullable

**Indexes:**
- Primary key on `id`
- Index on `candidate_id`
- Index on `question_id`

#### rebuttals
Candidate rebuttals to other candidates' answers.

**Columns:**
- `id` (PK) - Integer
- `created_at` - Timestamp
- `updated_at` - Timestamp
- `candidate_id` (FK -> candidates.id, CASCADE) - Integer, indexed
- `target_answer_id` (FK -> video_answers.id, CASCADE) - Integer, indexed
- `target_claim_text` - Text (quoted text from transcript)
- `target_claim_timestamp` - Float, nullable
- `video_asset_id` - String
- `video_url` - String, nullable
- `duration` - Float (seconds)
- `transcript_id` - String, nullable
- `transcript_text` - Text, nullable
- `transcript_url` - String, nullable
- `status` - Enum (draft, processing, published, withdrawn)

**Indexes:**
- Primary key on `id`
- Index on `candidate_id`
- Index on `target_answer_id`

#### claims
Extracted claims from video answers with optional sources.

**Columns:**
- `id` (PK) - Integer
- `created_at` - Timestamp
- `updated_at` - Timestamp
- `answer_id` (FK -> video_answers.id, CASCADE) - Integer, indexed
- `claim_snippet` - Text
- `claim_timestamp` - Float, nullable
- `sources` - JSON, nullable (array of {url, title, description})
- `is_verified` - Boolean, default false
- `reviewer_notes` - Text, nullable

**Indexes:**
- Primary key on `id`
- Index on `answer_id`

### 5. Moderation

#### reports
User reports for moderation review.

**Columns:**
- `id` (PK) - Integer
- `created_at` - Timestamp
- `updated_at` - Timestamp
- `reporter_id` (FK -> users.id, SET NULL) - Integer, indexed, nullable
- `target_type` - String (question, answer, rebuttal)
- `target_id` - Integer
- `reason` - Enum (spam, doxxing, threats, harassment, off_topic, misinformation, other)
- `description` - Text, nullable
- `status` - Enum (pending, under_review, resolved, dismissed), indexed
- `resolved_by_id` (FK -> users.id, SET NULL) - Integer, nullable
- `resolution_notes` - Text, nullable

**Indexes:**
- Primary key on `id`
- Index on `reporter_id`
- Index on `status`

#### moderation_actions
Record of all moderation actions.

**Columns:**
- `id` (PK) - Integer
- `created_at` - Timestamp
- `updated_at` - Timestamp
- `target_type` - String
- `target_id` - Integer, indexed
- `action_type` - Enum (approve, remove, merge, flag, warn_user, suspend_user)
- `moderator_id` (FK -> users.id, SET NULL) - Integer, indexed, nullable
- `rationale_code` - String, nullable
- `rationale_text` - Text, nullable
- `report_id` (FK -> reports.id, SET NULL) - Integer, nullable
- `is_public` - Boolean, default true

**Indexes:**
- Primary key on `id`
- Index on `target_id`
- Index on `moderator_id`

#### audit_logs
Immutable audit trail for integrity-sensitive operations.

**Columns:**
- `id` (PK) - Integer
- `created_at` - Timestamp
- `updated_at` - Timestamp
- `event_type` - Enum (user_created, user_verified, question_submitted, etc.), indexed
- `actor_id` (FK -> users.id, SET NULL) - Integer, indexed, nullable
- `target_type` - String, nullable
- `target_id` - Integer, nullable
- `event_data` - JSON, nullable
- `ip_address_hash` - String, nullable (hashed, not raw IP)
- `user_agent` - String, nullable
- `city_scope` - String, indexed, nullable
- `severity` - String, default 'info' (info, warning, critical)

**Indexes:**
- Primary key on `id`
- Index on `event_type`
- Index on `actor_id`
- Index on `city_scope`

### 6. Social Features

#### follows
User follows for contests, candidates, and issue tags.

**Columns:**
- `id` (PK) - Integer
- `created_at` - Timestamp
- `updated_at` - Timestamp
- `user_id` (FK -> users.id, CASCADE) - Integer, indexed
- `target_type` - Enum (contest, candidate, issue_tag)
- `target_id` - Integer, nullable (null for issue tags)
- `target_value` - String, nullable (for issue tags)
- `notification_prefs` - JSON, nullable
- `is_active` - Boolean, default true

**Indexes:**
- Primary key on `id`
- Index on `user_id`
- Unique composite index on `(user_id, target_type, target_id, target_value)`

## PostgreSQL Extensions

### pgvector
Used for vector similarity search on question embeddings.

**Configuration:**
- Extension: `vector`
- Vector dimension: 384 (for sentence-transformers/all-MiniLM-L6-v2)
- Index type: IVFFlat with 100 lists
- Distance metric: Cosine similarity

**Usage:**
- Question clustering and deduplication
- Semantic search for similar questions

## Enum Types

All enum types are created as PostgreSQL native enums:

1. `userrole` - voter, candidate, admin, moderator, city_staff
2. `verificationstatus` - pending, verified, rejected, expired
3. `verificationmethod` - sms, email, mail_code, voter_roll, id_proofing
4. `contesttype` - race, measure
5. `candidatestatus` - pending, verified, active, withdrawn, disqualified
6. `questionstatus` - pending, approved, merged, removed
7. `answerstatus` - draft, processing, published, withdrawn
8. `reportstatus` - pending, under_review, resolved, dismissed
9. `reportreason` - spam, doxxing, threats, harassment, off_topic, misinformation, other
10. `moderationactiontype` - approve, remove, merge, flag, warn_user, suspend_user
11. `auditeventtype` - user_created, user_verified, question_submitted, etc.
12. `followtargettype` - contest, candidate, issue_tag

## Constraints

### Foreign Key Constraints

All foreign keys specify `ondelete` behavior:

- **CASCADE** - Child records are deleted when parent is deleted
  - Used for: verification_records, contests, candidates, measures, question_versions, votes, video_answers, rebuttals, claims, follows

- **SET NULL** - Foreign key is set to NULL when parent is deleted
  - Used for: questions.author_id, candidates.user_id, question_versions.edit_author_id, video_answers.question_version_id, reports.reporter_id, reports.resolved_by_id, moderation_actions.moderator_id, moderation_actions.report_id, audit_logs.actor_id

### Unique Constraints

- `users.email` - One email per user
- `votes(user_id, question_id)` - One vote per user per question
- `follows(user_id, target_type, target_id, target_value)` - One follow per user per target

## Performance Considerations

### Indexes

The schema includes indexes on:
- All primary keys (automatic)
- All foreign keys for join performance
- Frequently filtered columns (status, city_id, etc.)
- Array columns using GIN indexes
- Vector columns using IVFFlat indexes

### Vector Search

For optimal performance with vector similarity search:
- Database < 100k questions: Use IVFFlat with 100 lists (current setup)
- Database > 100k questions: Consider increasing lists to sqrt(rows)
- Database > 1M questions: Consider HNSW indexing (requires pgvector 0.5.0+)

### Query Optimization

- Use indexes on contest_id, status, and rank_score for question filtering
- Use composite index on (user_id, question_id) for vote lookups
- Use GIN index on issue_tags for array searches
- Use vector index for semantic similarity searches

## Security Features

### Audit Trail
- All integrity-sensitive operations logged in `audit_logs`
- Immutable event stream for compliance and security

### Data Privacy
- IP addresses are hashed, not stored raw
- Minimal PII in verification_records
- Verification metadata is non-sensitive only

### Moderation
- Comprehensive reporting system
- Transparent moderation actions
- User warnings and suspensions tracked

## Migration Files

- **Initial migration**: `d49625079456_initial_migration.py`
- Creates all tables, indexes, and constraints
- Enables pgvector extension
- Sets up all enum types
