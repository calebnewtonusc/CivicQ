# CivicQ Database Schema Reference

Complete reference for all tables, columns, relationships, and constraints in the CivicQ database.

## Table of Contents

- [Overview](#overview)
- [User Management](#user-management)
- [City Multi-tenancy](#city-multi-tenancy)
- [Electoral Data](#electoral-data)
- [Questions and Voting](#questions-and-voting)
- [Video Answers](#video-answers)
- [Moderation](#moderation)
- [Social Features](#social-features)
- [Relationships Diagram](#relationships-diagram)

## Overview

### Database Information

- **Database**: PostgreSQL 14+
- **Extensions**: pgvector (for vector similarity search)
- **Schema Version**: Managed by Alembic migrations
- **Character Set**: UTF-8

### Naming Conventions

- **Tables**: Lowercase, plural (e.g., `users`, `questions`)
- **Columns**: Snake_case (e.g., `created_at`, `user_id`)
- **Indexes**: `idx_table_column(s)` (e.g., `idx_users_email`)
- **Foreign Keys**: `fk_table_column` (implicit via SQLAlchemy)

## User Management

### users

Primary user table for all user types (voters, candidates, city staff, admins).

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | INTEGER | NO | AUTO | Primary key |
| email | VARCHAR | NO | - | Unique email address |
| hashed_password | VARCHAR | NO | - | Bcrypt hashed password |
| full_name | VARCHAR | YES | - | User's full name |
| phone_number | VARCHAR | YES | - | Phone number |
| role | ENUM | NO | 'voter' | User role (voter, candidate, admin, moderator, city_staff) |
| is_active | BOOLEAN | NO | TRUE | Account active status |
| is_superuser | BOOLEAN | NO | FALSE | Superuser flag |
| city_id | VARCHAR | YES | - | City identifier |
| city_name | VARCHAR | YES | - | City name |
| verification_status | ENUM | NO | 'pending' | Verification status (pending, verified, rejected, expired) |
| verification_token | VARCHAR | YES | - | Minimal verification token |
| email_verified | BOOLEAN | NO | FALSE | Email verification status |
| email_verification_token | VARCHAR | YES | - | Email verification token |
| email_verification_expires | DATETIME | YES | - | Token expiration |
| password_reset_token | VARCHAR | YES | - | Password reset token |
| password_reset_expires | DATETIME | YES | - | Token expiration |
| two_factor_enabled | BOOLEAN | NO | FALSE | 2FA enabled flag |
| two_factor_secret | VARCHAR | YES | - | TOTP secret |
| backup_codes | JSON | YES | - | Encrypted backup codes |
| oauth_provider | VARCHAR | YES | - | OAuth provider name |
| oauth_id | VARCHAR | YES | - | Provider's user ID |
| last_active | DATETIME | YES | NOW() | Last activity timestamp |
| last_login | DATETIME | YES | - | Last login timestamp |
| last_login_ip | VARCHAR | YES | - | Last login IP |
| last_login_user_agent | VARCHAR | YES | - | Last login user agent |
| failed_login_attempts | INTEGER | NO | 0 | Failed login counter |
| account_locked_until | DATETIME | YES | - | Account lock expiration |
| locked_reason | VARCHAR | YES | - | Lock reason |
| created_at | DATETIME | NO | NOW() | Record creation time |
| updated_at | DATETIME | NO | NOW() | Record update time |

**Indexes:**
- PRIMARY KEY: `id`
- UNIQUE: `email`
- INDEX: `city_id`, `role`, `verification_status`
- COMPOSITE: `(city_id, role)`, `(city_id, verification_status)`
- PARTIAL: `email_verification_token WHERE NOT NULL`

**Relationships:**
- verification_records → verification_records.user_id
- questions → questions.author_id
- votes → votes.user_id
- reports → reports.reporter_id
- follows → follows.user_id
- videos → videos.user_id

---

### verification_records

Tracks user verification attempts and status.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | INTEGER | NO | AUTO | Primary key |
| user_id | INTEGER | NO | - | Foreign key to users |
| method | ENUM | NO | - | Verification method (sms, email, mail_code, voter_roll, id_proofing) |
| provider | VARCHAR | YES | - | Verification provider |
| city_scope | VARCHAR | NO | - | City for verification |
| status | ENUM | NO | 'pending' | Status (pending, verified, rejected, expired) |
| metadata | JSON | YES | - | Non-sensitive metadata |
| verified_at | DATETIME | YES | - | Verification timestamp |
| expires_at | DATETIME | YES | - | Expiration timestamp |
| created_at | DATETIME | NO | NOW() | Record creation time |
| updated_at | DATETIME | NO | NOW() | Record update time |

**Indexes:**
- PRIMARY KEY: `id`
- INDEX: `user_id`, `city_scope`
- COMPOSITE: `(city_scope, status)`

**Foreign Keys:**
- user_id → users.id (CASCADE DELETE)

---

## City Multi-tenancy

### cities

Represents cities/jurisdictions using CivicQ.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | INTEGER | NO | AUTO | Primary key |
| name | VARCHAR | NO | - | City name |
| slug | VARCHAR | NO | - | URL-friendly identifier |
| state | VARCHAR(2) | NO | - | Two-letter state code |
| county | VARCHAR | YES | - | County name |
| population | INTEGER | YES | - | Population |
| primary_contact_name | VARCHAR | NO | - | Primary contact name |
| primary_contact_email | VARCHAR | NO | - | Primary contact email |
| primary_contact_phone | VARCHAR | YES | - | Primary contact phone |
| primary_contact_title | VARCHAR | YES | - | Primary contact title |
| status | ENUM | NO | 'pending_verification' | Status (pending_verification, active, suspended, inactive) |
| verification_method | VARCHAR | YES | - | How verified |
| verification_notes | TEXT | YES | - | Verification notes |
| verified_at | DATETIME | YES | - | Verification timestamp |
| verified_by | VARCHAR | YES | - | Admin who verified |
| documentation_urls | JSON | YES | - | Links to docs |
| official_email_domain | VARCHAR | YES | - | Official domain |
| logo_url | VARCHAR | YES | - | Logo URL |
| primary_color | VARCHAR(7) | YES | - | Hex color |
| secondary_color | VARCHAR(7) | YES | - | Hex color |
| timezone | VARCHAR | NO | 'America/Los_Angeles' | Timezone |
| settings | JSON | YES | - | City settings |
| features | JSON | YES | {} | Feature flags |
| next_election_date | DATE | YES | - | Next election |
| election_info_url | VARCHAR | YES | - | Election info URL |
| subscription_tier | VARCHAR | NO | 'free' | Subscription tier |
| subscription_expires | DATETIME | YES | - | Subscription expiration |
| total_voters | INTEGER | NO | 0 | Voter count |
| total_questions | INTEGER | NO | 0 | Question count |
| total_ballots | INTEGER | NO | 0 | Ballot count |
| onboarding_completed | BOOLEAN | NO | FALSE | Onboarding status |
| onboarding_step | INTEGER | NO | 0 | Current step |
| onboarding_data | JSON | YES | - | Onboarding state |
| created_at | DATETIME | NO | NOW() | Record creation time |
| updated_at | DATETIME | NO | NOW() | Record update time |

**Indexes:**
- PRIMARY KEY: `id`
- UNIQUE: `slug`
- INDEX: `state`, `status`
- COMPOSITE: `(state, status)`

**Relationships:**
- staff → city_staff.city_id

---

### city_staff

Links users to cities with specific roles.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | INTEGER | NO | AUTO | Primary key |
| city_id | INTEGER | NO | - | Foreign key to cities |
| user_id | INTEGER | NO | - | Foreign key to users |
| role | ENUM | NO | 'viewer' | Role (owner, admin, editor, moderator, viewer) |
| invited_by_id | INTEGER | YES | - | Who invited |
| invited_at | DATETIME | NO | NOW() | Invitation time |
| is_active | BOOLEAN | NO | TRUE | Active status |
| last_access | DATETIME | YES | - | Last access time |
| created_at | DATETIME | NO | NOW() | Record creation time |
| updated_at | DATETIME | NO | NOW() | Record update time |

**Indexes:**
- PRIMARY KEY: `id`
- UNIQUE: `(city_id, user_id)`
- INDEX: `user_id`

**Foreign Keys:**
- city_id → cities.id (CASCADE DELETE)
- user_id → users.id (CASCADE DELETE)
- invited_by_id → users.id (SET NULL)

---

### city_invitations

Tracks pending city staff invitations.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | INTEGER | NO | AUTO | Primary key |
| city_id | INTEGER | NO | - | Foreign key to cities |
| email | VARCHAR | NO | - | Invitee email |
| role | ENUM | NO | 'viewer' | Role to grant |
| token | VARCHAR | NO | - | Invitation token |
| invited_by_id | INTEGER | YES | - | Who invited |
| invited_at | DATETIME | NO | NOW() | Invitation time |
| expires_at | DATETIME | NO | - | Expiration time |
| accepted | BOOLEAN | NO | FALSE | Accepted flag |
| accepted_at | DATETIME | YES | - | Acceptance time |
| accepted_by_id | INTEGER | YES | - | Who accepted |
| created_at | DATETIME | NO | NOW() | Record creation time |
| updated_at | DATETIME | NO | NOW() | Record update time |

**Indexes:**
- PRIMARY KEY: `id`
- UNIQUE: `token`
- INDEX: `email`, `city_id`

**Foreign Keys:**
- city_id → cities.id (CASCADE DELETE)
- invited_by_id → users.id (SET NULL)
- accepted_by_id → users.id (SET NULL)

---

## Electoral Data

### ballots

Election ballots for specific cities.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | INTEGER | NO | AUTO | Primary key |
| city_id | VARCHAR | NO | - | City identifier |
| city_name | VARCHAR | NO | - | City name |
| election_date | DATE | NO | - | Election date |
| version | INTEGER | NO | 1 | Ballot version |
| source_metadata | JSON | YES | - | Source data info |
| is_published | BOOLEAN | NO | FALSE | Published status |
| created_at | DATETIME | NO | NOW() | Record creation time |
| updated_at | DATETIME | NO | NOW() | Record update time |

**Indexes:**
- PRIMARY KEY: `id`
- INDEX: `city_id`, `election_date`
- COMPOSITE: `(city_id, election_date)`

**Relationships:**
- contests → contests.ballot_id

---

### contests

Races or measures within a ballot.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | INTEGER | NO | AUTO | Primary key |
| ballot_id | INTEGER | NO | - | Foreign key to ballots |
| type | ENUM | NO | - | Type (race, measure) |
| title | VARCHAR | NO | - | Contest title |
| jurisdiction | VARCHAR | YES | - | Jurisdiction |
| office | VARCHAR | YES | - | Office (for races) |
| seat_count | INTEGER | YES | 1 | Number of seats |
| description | TEXT | YES | - | Description |
| display_order | INTEGER | NO | 0 | Display order |
| created_at | DATETIME | NO | NOW() | Record creation time |
| updated_at | DATETIME | NO | NOW() | Record update time |

**Indexes:**
- PRIMARY KEY: `id`
- INDEX: `ballot_id`
- COMPOSITE: `(ballot_id, type)`, `(ballot_id, display_order)`

**Foreign Keys:**
- ballot_id → ballots.id (CASCADE DELETE)

**Relationships:**
- candidates → candidates.contest_id
- measures → measures.contest_id
- questions → questions.contest_id

---

### candidates

Candidates in races.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | INTEGER | NO | AUTO | Primary key |
| contest_id | INTEGER | NO | - | Foreign key to contests |
| user_id | INTEGER | YES | - | Foreign key to users |
| name | VARCHAR | NO | - | Candidate name |
| filing_id | VARCHAR | YES | - | Official filing ID |
| email | VARCHAR | YES | - | Contact email |
| phone | VARCHAR | YES | - | Contact phone |
| status | ENUM | NO | 'pending' | Status (pending, verified, active, withdrawn, disqualified) |
| profile_fields | JSON | YES | - | Profile data |
| photo_url | VARCHAR | YES | - | Photo URL |
| website | VARCHAR | YES | - | Website URL |
| identity_verified | BOOLEAN | NO | FALSE | Verified flag |
| identity_verified_at | DATE | YES | - | Verification date |
| display_order | INTEGER | NO | 0 | Display order |
| created_at | DATETIME | NO | NOW() | Record creation time |
| updated_at | DATETIME | NO | NOW() | Record update time |

**Indexes:**
- PRIMARY KEY: `id`
- INDEX: `contest_id`, `user_id`, `filing_id`, `status`

**Foreign Keys:**
- contest_id → contests.id (CASCADE DELETE)
- user_id → users.id (SET NULL)

**Relationships:**
- video_answers → video_answers.candidate_id
- rebuttals → rebuttals.candidate_id

---

### measures

Ballot measures/propositions.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | INTEGER | NO | AUTO | Primary key |
| contest_id | INTEGER | NO | - | Foreign key to contests |
| measure_number | VARCHAR | YES | - | Measure number |
| measure_text | TEXT | NO | - | Full text |
| summary | TEXT | YES | - | Summary |
| fiscal_notes | TEXT | YES | - | Fiscal impact |
| pro_statement | TEXT | YES | - | Pro argument |
| con_statement | TEXT | YES | - | Con argument |
| pro_contacts | JSON | YES | - | Pro contacts |
| con_contacts | JSON | YES | - | Con contacts |
| created_at | DATETIME | NO | NOW() | Record creation time |
| updated_at | DATETIME | NO | NOW() | Record update time |

**Indexes:**
- PRIMARY KEY: `id`
- INDEX: `contest_id`

**Foreign Keys:**
- contest_id → contests.id (CASCADE DELETE)

---

## Questions and Voting

### questions

Voter-submitted questions for candidates.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | INTEGER | NO | AUTO | Primary key |
| contest_id | INTEGER | NO | - | Foreign key to contests |
| author_id | INTEGER | YES | - | Foreign key to users |
| current_version_id | INTEGER | YES | - | Current version |
| question_text | TEXT | NO | - | Question text |
| issue_tags | ARRAY | YES | - | Issue tags |
| status | ENUM | NO | 'pending' | Status (pending, approved, merged, removed) |
| cluster_id | INTEGER | YES | - | Dedup cluster |
| embedding | VECTOR(384) | YES | - | Sentence embedding |
| context | TEXT | YES | - | Optional context |
| upvotes | INTEGER | NO | 0 | Upvote count |
| downvotes | INTEGER | NO | 0 | Downvote count |
| rank_score | FLOAT | NO | 0.0 | Ranking score |
| representation_metadata | JSON | YES | - | Rep metadata |
| is_flagged | INTEGER | NO | 0 | Flag count |
| moderation_notes | TEXT | YES | - | Mod notes |
| created_at | DATETIME | NO | NOW() | Record creation time |
| updated_at | DATETIME | NO | NOW() | Record update time |

**Indexes:**
- PRIMARY KEY: `id`
- INDEX: `contest_id`, `author_id`, `status`, `cluster_id`, `rank_score`
- COMPOSITE: `(contest_id, status)`, `(contest_id, rank_score)`
- GIN: `issue_tags`
- VECTOR: `embedding` (ivfflat)
- FULL-TEXT: `question_text`

**Foreign Keys:**
- contest_id → contests.id (CASCADE DELETE)
- author_id → users.id (SET NULL)

**Relationships:**
- versions → question_versions.question_id
- votes → votes.question_id
- video_answers → video_answers.question_id

---

### question_versions

Question edit history.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | INTEGER | NO | AUTO | Primary key |
| question_id | INTEGER | NO | - | Foreign key to questions |
| version_number | INTEGER | NO | - | Version number |
| question_text | TEXT | NO | - | Question text |
| edit_author_id | INTEGER | YES | - | Editor user ID |
| edit_reason | TEXT | YES | - | Edit reason |
| diff_metadata | JSON | YES | - | What changed |
| created_at | DATETIME | NO | NOW() | Record creation time |
| updated_at | DATETIME | NO | NOW() | Record update time |

**Indexes:**
- PRIMARY KEY: `id`
- UNIQUE: `(question_id, version_number)`
- INDEX: `question_id`

**Foreign Keys:**
- question_id → questions.id (CASCADE DELETE)
- edit_author_id → users.id (SET NULL)

---

### votes

Upvotes/downvotes on questions.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | INTEGER | NO | AUTO | Primary key |
| user_id | INTEGER | NO | - | Foreign key to users |
| question_id | INTEGER | NO | - | Foreign key to questions |
| value | INTEGER | NO | - | +1 or -1 |
| device_risk_score | FLOAT | YES | 0.0 | Risk score |
| weight | FLOAT | NO | 1.0 | Vote weight |
| metadata | JSON | YES | - | Device metadata |
| created_at | DATETIME | NO | NOW() | Record creation time |
| updated_at | DATETIME | NO | NOW() | Record update time |

**Indexes:**
- PRIMARY KEY: `id`
- UNIQUE: `(user_id, question_id)`
- INDEX: `user_id`, `question_id`

**Foreign Keys:**
- user_id → users.id (CASCADE DELETE)
- question_id → questions.id (CASCADE DELETE)

---

## Video Answers

For complete video models, see the Video section of the schema. Key tables:

- **video_answers** - Candidate video responses
- **rebuttals** - Candidate rebuttals to other answers
- **claims** - Extracted claims with sources
- **videos** - Video processing and storage
- **video_analytics** - Video playback analytics

## Moderation

### reports

User reports of content.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| id | INTEGER | NO | AUTO | Primary key |
| reporter_id | INTEGER | YES | - | Reporter user |
| target_type | VARCHAR | NO | - | Type (question, answer, rebuttal) |
| target_id | INTEGER | NO | - | Target ID |
| reason | ENUM | NO | - | Reason code |
| description | TEXT | YES | - | Description |
| status | ENUM | NO | 'pending' | Status |
| resolved_by_id | INTEGER | YES | - | Resolver user |
| resolution_notes | TEXT | YES | - | Resolution notes |
| created_at | DATETIME | NO | NOW() | Record creation time |
| updated_at | DATETIME | NO | NOW() | Record update time |

**Foreign Keys:**
- reporter_id → users.id (SET NULL)
- resolved_by_id → users.id (SET NULL)

---

### moderation_actions

Record of moderation actions.

### audit_logs

Immutable audit trail for critical events.

---

## Social Features

### follows

User follows for contests, candidates, or issues.

---

## Relationships Diagram

```
users
├── verification_records
├── questions (as author)
├── votes
├── reports (as reporter)
├── follows
├── videos
└── city_staff

cities
├── city_staff
├── city_invitations
└── ballots (via city_id)

ballots
└── contests
    ├── candidates
    │   ├── video_answers
    │   └── rebuttals
    ├── measures
    └── questions
        ├── question_versions
        ├── votes
        └── video_answers
```

---

For more details on database operations, see [DATABASE_GUIDE.md](DATABASE_GUIDE.md).
