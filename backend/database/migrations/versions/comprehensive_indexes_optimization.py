"""
Comprehensive Database Indexes and Optimization

This migration creates all necessary indexes for optimal query performance:
- B-tree indexes on foreign keys
- Composite indexes for common query patterns
- Partial indexes for filtered queries
- Full-text search indexes
- GIN indexes for JSON and array fields

Revision ID: comprehensive_indexes
Revises: city_onboarding_migration
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'comprehensive_indexes'
down_revision = 'city_onboarding_migration'
branch_labels = None
depends_on = None


def upgrade():
    """Apply comprehensive indexing strategy"""

    # ========================================================================
    # Users Table Indexes
    # ========================================================================

    # Composite index for city + role queries
    op.create_index(
        'idx_users_city_role',
        'users',
        ['city_id', 'role'],
        unique=False
    )

    # Composite index for city + verification status
    op.create_index(
        'idx_users_city_verification',
        'users',
        ['city_id', 'verification_status'],
        unique=False
    )

    # Partial index for active users only
    op.create_index(
        'idx_users_active',
        'users',
        ['id'],
        unique=False,
        postgresql_where=sa.text('is_active = true')
    )

    # Index for email verification lookups
    op.create_index(
        'idx_users_email_verification_token',
        'users',
        ['email_verification_token'],
        unique=False,
        postgresql_where=sa.text('email_verification_token IS NOT NULL')
    )

    # Index for password reset lookups
    op.create_index(
        'idx_users_password_reset_token',
        'users',
        ['password_reset_token'],
        unique=False,
        postgresql_where=sa.text('password_reset_token IS NOT NULL')
    )

    # Composite index for OAuth lookups
    op.create_index(
        'idx_users_oauth',
        'users',
        ['oauth_provider', 'oauth_id'],
        unique=False,
        postgresql_where=sa.text('oauth_provider IS NOT NULL')
    )

    # Index for locked accounts
    op.create_index(
        'idx_users_locked',
        'users',
        ['account_locked_until'],
        unique=False,
        postgresql_where=sa.text('account_locked_until IS NOT NULL')
    )

    # ========================================================================
    # Cities Table Indexes
    # ========================================================================

    # Index for active cities
    op.create_index(
        'idx_cities_active',
        'cities',
        ['id', 'status'],
        unique=False,
        postgresql_where=sa.text("status = 'active'")
    )

    # Composite index for state + status
    op.create_index(
        'idx_cities_state_status',
        'cities',
        ['state', 'status'],
        unique=False
    )

    # Index for next election date
    op.create_index(
        'idx_cities_next_election',
        'cities',
        ['next_election_date'],
        unique=False,
        postgresql_where=sa.text('next_election_date IS NOT NULL')
    )

    # ========================================================================
    # Ballots Table Indexes
    # ========================================================================

    # Composite index for city + election date
    op.create_index(
        'idx_ballots_city_election',
        'ballots',
        ['city_id', 'election_date'],
        unique=False
    )

    # Partial index for published ballots
    op.create_index(
        'idx_ballots_published',
        'ballots',
        ['city_id', 'election_date'],
        unique=False,
        postgresql_where=sa.text('is_published = true')
    )

    # ========================================================================
    # Contests Table Indexes
    # ========================================================================

    # Composite index for ballot + type
    op.create_index(
        'idx_contests_ballot_type',
        'contests',
        ['ballot_id', 'type'],
        unique=False
    )

    # Index for display order
    op.create_index(
        'idx_contests_ballot_order',
        'contests',
        ['ballot_id', 'display_order'],
        unique=False
    )

    # ========================================================================
    # Candidates Table Indexes
    # ========================================================================

    # Index on user_id for candidate lookups
    op.create_index(
        'idx_candidates_user_id',
        'candidates',
        ['user_id'],
        unique=False,
        postgresql_where=sa.text('user_id IS NOT NULL')
    )

    # Composite index for contest + status
    op.create_index(
        'idx_candidates_contest_status',
        'candidates',
        ['contest_id', 'status'],
        unique=False
    )

    # Partial index for active candidates
    op.create_index(
        'idx_candidates_active',
        'candidates',
        ['contest_id', 'display_order'],
        unique=False,
        postgresql_where=sa.text("status = 'active'")
    )

    # Index on filing_id
    op.create_index(
        'idx_candidates_filing_id',
        'candidates',
        ['filing_id'],
        unique=False,
        postgresql_where=sa.text('filing_id IS NOT NULL')
    )

    # ========================================================================
    # Questions Table Indexes
    # ========================================================================

    # Composite index for contest + status
    op.create_index(
        'idx_questions_contest_status',
        'questions',
        ['contest_id', 'status'],
        unique=False
    )

    # Composite index for contest + rank (for sorting)
    op.create_index(
        'idx_questions_contest_rank',
        'questions',
        ['contest_id', 'rank_score'],
        unique=False,
        postgresql_where=sa.text("status = 'approved'")
    )

    # Index on author
    op.create_index(
        'idx_questions_author',
        'questions',
        ['author_id'],
        unique=False,
        postgresql_where=sa.text('author_id IS NOT NULL')
    )

    # GIN index for issue tags array
    op.create_index(
        'idx_questions_issue_tags',
        'questions',
        ['issue_tags'],
        unique=False,
        postgresql_using='gin'
    )

    # Index on cluster_id for deduplication
    op.create_index(
        'idx_questions_cluster',
        'questions',
        ['cluster_id'],
        unique=False,
        postgresql_where=sa.text('cluster_id IS NOT NULL')
    )

    # Partial index for flagged questions
    op.create_index(
        'idx_questions_flagged',
        'questions',
        ['contest_id', 'is_flagged'],
        unique=False,
        postgresql_where=sa.text('is_flagged > 0')
    )

    # Full-text search index on question text
    op.execute("""
        CREATE INDEX idx_questions_text_search
        ON questions
        USING gin(to_tsvector('english', question_text))
    """)

    # ========================================================================
    # Question Versions Table Indexes
    # ========================================================================

    # Composite index for question + version
    op.create_index(
        'idx_question_versions_question_version',
        'question_versions',
        ['question_id', 'version_number'],
        unique=True
    )

    # ========================================================================
    # Votes Table Indexes
    # ========================================================================

    # Index on user_id for user's votes
    op.create_index(
        'idx_votes_user',
        'votes',
        ['user_id'],
        unique=False
    )

    # Index on question_id for question's votes
    op.create_index(
        'idx_votes_question',
        'votes',
        ['question_id'],
        unique=False
    )

    # Composite index for vote aggregation
    op.create_index(
        'idx_votes_question_value',
        'votes',
        ['question_id', 'value'],
        unique=False
    )

    # Index for weighted votes
    op.create_index(
        'idx_votes_weight',
        'votes',
        ['question_id', 'weight'],
        unique=False,
        postgresql_where=sa.text('weight < 1.0')
    )

    # ========================================================================
    # Video Answers Table Indexes
    # ========================================================================

    # Composite index for candidate + question
    op.create_index(
        'idx_video_answers_candidate_question',
        'video_answers',
        ['candidate_id', 'question_id'],
        unique=False
    )

    # Partial index for published answers
    op.create_index(
        'idx_video_answers_published',
        'video_answers',
        ['question_id', 'status'],
        unique=False,
        postgresql_where=sa.text("status = 'published'")
    )

    # Index on question_version_id
    op.create_index(
        'idx_video_answers_version',
        'video_answers',
        ['question_version_id'],
        unique=False,
        postgresql_where=sa.text('question_version_id IS NOT NULL')
    )

    # Full-text search on transcript
    op.execute("""
        CREATE INDEX idx_video_answers_transcript_search
        ON video_answers
        USING gin(to_tsvector('english', transcript_text))
        WHERE transcript_text IS NOT NULL
    """)

    # ========================================================================
    # Rebuttals Table Indexes
    # ========================================================================

    # Composite index for candidate + target answer
    op.create_index(
        'idx_rebuttals_candidate_target',
        'rebuttals',
        ['candidate_id', 'target_answer_id'],
        unique=False
    )

    # Index on target answer
    op.create_index(
        'idx_rebuttals_target',
        'rebuttals',
        ['target_answer_id'],
        unique=False
    )

    # Partial index for published rebuttals
    op.create_index(
        'idx_rebuttals_published',
        'rebuttals',
        ['target_answer_id'],
        unique=False,
        postgresql_where=sa.text("status = 'published'")
    )

    # ========================================================================
    # Claims Table Indexes
    # ========================================================================

    # Index on answer_id
    op.create_index(
        'idx_claims_answer',
        'claims',
        ['answer_id'],
        unique=False
    )

    # Partial index for verified claims
    op.create_index(
        'idx_claims_verified',
        'claims',
        ['answer_id'],
        unique=False,
        postgresql_where=sa.text('is_verified = true')
    )

    # GIN index for sources JSON
    op.create_index(
        'idx_claims_sources',
        'claims',
        ['sources'],
        unique=False,
        postgresql_using='gin',
        postgresql_where=sa.text('sources IS NOT NULL')
    )

    # ========================================================================
    # Reports Table Indexes
    # ========================================================================

    # Composite index for target lookup
    op.create_index(
        'idx_reports_target',
        'reports',
        ['target_type', 'target_id'],
        unique=False
    )

    # Index on reporter
    op.create_index(
        'idx_reports_reporter',
        'reports',
        ['reporter_id'],
        unique=False,
        postgresql_where=sa.text('reporter_id IS NOT NULL')
    )

    # Partial index for pending reports
    op.create_index(
        'idx_reports_pending',
        'reports',
        ['status', 'created_at'],
        unique=False,
        postgresql_where=sa.text("status = 'pending'")
    )

    # ========================================================================
    # Moderation Actions Table Indexes
    # ========================================================================

    # Composite index for target
    op.create_index(
        'idx_moderation_actions_target',
        'moderation_actions',
        ['target_type', 'target_id'],
        unique=False
    )

    # Index on moderator
    op.create_index(
        'idx_moderation_actions_moderator',
        'moderation_actions',
        ['moderator_id'],
        unique=False,
        postgresql_where=sa.text('moderator_id IS NOT NULL')
    )

    # Index for public actions
    op.create_index(
        'idx_moderation_actions_public',
        'moderation_actions',
        ['created_at'],
        unique=False,
        postgresql_where=sa.text('is_public = true')
    )

    # ========================================================================
    # Audit Logs Table Indexes
    # ========================================================================

    # Composite index for event type + timestamp
    op.create_index(
        'idx_audit_logs_event_time',
        'audit_logs',
        ['event_type', 'created_at'],
        unique=False
    )

    # Index on actor
    op.create_index(
        'idx_audit_logs_actor',
        'audit_logs',
        ['actor_id'],
        unique=False,
        postgresql_where=sa.text('actor_id IS NOT NULL')
    )

    # Composite index for target
    op.create_index(
        'idx_audit_logs_target',
        'audit_logs',
        ['target_type', 'target_id'],
        unique=False,
        postgresql_where=sa.text('target_type IS NOT NULL')
    )

    # Index for city scope
    op.create_index(
        'idx_audit_logs_city',
        'audit_logs',
        ['city_scope', 'created_at'],
        unique=False,
        postgresql_where=sa.text('city_scope IS NOT NULL')
    )

    # Index for severity
    op.create_index(
        'idx_audit_logs_severity',
        'audit_logs',
        ['severity', 'created_at'],
        unique=False
    )

    # GIN index for event_data JSON
    op.create_index(
        'idx_audit_logs_event_data',
        'audit_logs',
        ['event_data'],
        unique=False,
        postgresql_using='gin',
        postgresql_where=sa.text('event_data IS NOT NULL')
    )

    # ========================================================================
    # Follows Table Indexes
    # ========================================================================

    # Index on user
    op.create_index(
        'idx_follows_user',
        'follows',
        ['user_id'],
        unique=False
    )

    # Composite index for target lookup
    op.create_index(
        'idx_follows_target',
        'follows',
        ['target_type', 'target_id'],
        unique=False,
        postgresql_where=sa.text('target_id IS NOT NULL')
    )

    # Index for issue tag follows
    op.create_index(
        'idx_follows_tag',
        'follows',
        ['target_value'],
        unique=False,
        postgresql_where=sa.text('target_value IS NOT NULL')
    )

    # Partial index for active follows
    op.create_index(
        'idx_follows_active',
        'follows',
        ['user_id', 'target_type'],
        unique=False,
        postgresql_where=sa.text('is_active = true')
    )

    # ========================================================================
    # Videos Table Indexes
    # ========================================================================

    # Index on user
    op.create_index(
        'idx_videos_user',
        'videos',
        ['user_id'],
        unique=False
    )

    # Index on answer
    op.create_index(
        'idx_videos_answer',
        'videos',
        ['answer_id'],
        unique=False,
        postgresql_where=sa.text('answer_id IS NOT NULL')
    )

    # Partial index for ready videos
    op.create_index(
        'idx_videos_ready',
        'videos',
        ['created_at'],
        unique=False,
        postgresql_where=sa.text("status = 'ready'")
    )

    # Partial index for processing videos
    op.create_index(
        'idx_videos_processing',
        'videos',
        ['processing_started_at'],
        unique=False,
        postgresql_where=sa.text("status = 'processing'")
    )

    # ========================================================================
    # Video Analytics Table Indexes
    # ========================================================================

    # Index on video
    op.create_index(
        'idx_video_analytics_video',
        'video_analytics',
        ['video_id', 'created_at'],
        unique=False
    )

    # Index on user
    op.create_index(
        'idx_video_analytics_user',
        'video_analytics',
        ['user_id', 'created_at'],
        unique=False,
        postgresql_where=sa.text('user_id IS NOT NULL')
    )

    # Index on session
    op.create_index(
        'idx_video_analytics_session',
        'video_analytics',
        ['session_id'],
        unique=False
    )

    # ========================================================================
    # City Staff Table Indexes
    # ========================================================================

    # Composite index for city + user
    op.create_index(
        'idx_city_staff_city_user',
        'city_staff',
        ['city_id', 'user_id'],
        unique=True
    )

    # Index on user
    op.create_index(
        'idx_city_staff_user',
        'city_staff',
        ['user_id'],
        unique=False
    )

    # Partial index for active staff
    op.create_index(
        'idx_city_staff_active',
        'city_staff',
        ['city_id', 'role'],
        unique=False,
        postgresql_where=sa.text('is_active = true')
    )

    # ========================================================================
    # City Invitations Table Indexes
    # ========================================================================

    # Index on email
    op.create_index(
        'idx_city_invitations_email',
        'city_invitations',
        ['email'],
        unique=False
    )

    # Partial index for pending invitations
    op.create_index(
        'idx_city_invitations_pending',
        'city_invitations',
        ['city_id', 'email'],
        unique=False,
        postgresql_where=sa.text('accepted = false')
    )

    # ========================================================================
    # Verification Records Table Indexes
    # ========================================================================

    # Index on user
    op.create_index(
        'idx_verification_records_user',
        'verification_records',
        ['user_id'],
        unique=False
    )

    # Composite index for city + status
    op.create_index(
        'idx_verification_records_city_status',
        'verification_records',
        ['city_scope', 'status'],
        unique=False
    )

    # Partial index for verified records
    op.create_index(
        'idx_verification_records_verified',
        'verification_records',
        ['user_id', 'city_scope'],
        unique=False,
        postgresql_where=sa.text("status = 'verified'")
    )


def downgrade():
    """Remove all indexes created in upgrade"""

    # Drop all indexes in reverse order
    index_names = [
        # Verification Records
        'idx_verification_records_verified',
        'idx_verification_records_city_status',
        'idx_verification_records_user',

        # City Invitations
        'idx_city_invitations_pending',
        'idx_city_invitations_email',

        # City Staff
        'idx_city_staff_active',
        'idx_city_staff_user',
        'idx_city_staff_city_user',

        # Video Analytics
        'idx_video_analytics_session',
        'idx_video_analytics_user',
        'idx_video_analytics_video',

        # Videos
        'idx_videos_processing',
        'idx_videos_ready',
        'idx_videos_answer',
        'idx_videos_user',

        # Follows
        'idx_follows_active',
        'idx_follows_tag',
        'idx_follows_target',
        'idx_follows_user',

        # Audit Logs
        'idx_audit_logs_event_data',
        'idx_audit_logs_severity',
        'idx_audit_logs_city',
        'idx_audit_logs_target',
        'idx_audit_logs_actor',
        'idx_audit_logs_event_time',

        # Moderation Actions
        'idx_moderation_actions_public',
        'idx_moderation_actions_moderator',
        'idx_moderation_actions_target',

        # Reports
        'idx_reports_pending',
        'idx_reports_reporter',
        'idx_reports_target',

        # Claims
        'idx_claims_sources',
        'idx_claims_verified',
        'idx_claims_answer',

        # Rebuttals
        'idx_rebuttals_published',
        'idx_rebuttals_target',
        'idx_rebuttals_candidate_target',

        # Video Answers
        'idx_video_answers_transcript_search',
        'idx_video_answers_version',
        'idx_video_answers_published',
        'idx_video_answers_candidate_question',

        # Votes
        'idx_votes_weight',
        'idx_votes_question_value',
        'idx_votes_question',
        'idx_votes_user',

        # Question Versions
        'idx_question_versions_question_version',

        # Questions
        'idx_questions_text_search',
        'idx_questions_flagged',
        'idx_questions_cluster',
        'idx_questions_issue_tags',
        'idx_questions_author',
        'idx_questions_contest_rank',
        'idx_questions_contest_status',

        # Candidates
        'idx_candidates_filing_id',
        'idx_candidates_active',
        'idx_candidates_contest_status',
        'idx_candidates_user_id',

        # Contests
        'idx_contests_ballot_order',
        'idx_contests_ballot_type',

        # Ballots
        'idx_ballots_published',
        'idx_ballots_city_election',

        # Cities
        'idx_cities_next_election',
        'idx_cities_state_status',
        'idx_cities_active',

        # Users
        'idx_users_locked',
        'idx_users_oauth',
        'idx_users_password_reset_token',
        'idx_users_email_verification_token',
        'idx_users_active',
        'idx_users_city_verification',
        'idx_users_city_role',
    ]

    for index_name in index_names:
        op.drop_index(index_name)
