"""Initial migration

Revision ID: d49625079456
Revises:
Create Date: 2026-02-14 11:40:21.600000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd49625079456'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Create enum types
    op.execute("""
        CREATE TYPE userrole AS ENUM (
            'voter', 'candidate', 'admin', 'moderator', 'city_staff'
        )
    """)

    op.execute("""
        CREATE TYPE verificationstatus AS ENUM (
            'pending', 'verified', 'rejected', 'expired'
        )
    """)

    op.execute("""
        CREATE TYPE verificationmethod AS ENUM (
            'sms', 'email', 'mail_code', 'voter_roll', 'id_proofing'
        )
    """)

    op.execute("""
        CREATE TYPE contesttype AS ENUM (
            'race', 'measure'
        )
    """)

    op.execute("""
        CREATE TYPE candidatestatus AS ENUM (
            'pending', 'verified', 'active', 'withdrawn', 'disqualified'
        )
    """)

    op.execute("""
        CREATE TYPE questionstatus AS ENUM (
            'pending', 'approved', 'merged', 'removed'
        )
    """)

    op.execute("""
        CREATE TYPE answerstatus AS ENUM (
            'draft', 'processing', 'published', 'withdrawn'
        )
    """)

    op.execute("""
        CREATE TYPE reportstatus AS ENUM (
            'pending', 'under_review', 'resolved', 'dismissed'
        )
    """)

    op.execute("""
        CREATE TYPE reportreason AS ENUM (
            'spam', 'doxxing', 'threats', 'harassment', 'off_topic',
            'misinformation', 'other'
        )
    """)

    op.execute("""
        CREATE TYPE moderationactiontype AS ENUM (
            'approve', 'remove', 'merge', 'flag', 'warn_user', 'suspend_user'
        )
    """)

    op.execute("""
        CREATE TYPE auditeventtype AS ENUM (
            'user_created', 'user_verified', 'question_submitted',
            'question_voted', 'answer_published', 'rebuttal_published',
            'moderation_action', 'candidate_verified', 'ballot_created',
            'contest_created', 'security_alert'
        )
    """)

    op.execute("""
        CREATE TYPE followtargettype AS ENUM (
            'contest', 'candidate', 'issue_tag'
        )
    """)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('phone_number', sa.String(), nullable=True),
        sa.Column('role', postgresql.ENUM('voter', 'candidate', 'admin', 'moderator', 'city_staff',
                  name='userrole', create_type=False), nullable=False, server_default='voter'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('city_id', sa.String(), nullable=True),
        sa.Column('city_name', sa.String(), nullable=True),
        sa.Column('verification_status', postgresql.ENUM('pending', 'verified', 'rejected', 'expired',
                  name='verificationstatus', create_type=False), nullable=False, server_default='pending'),
        sa.Column('verification_token', sa.String(), nullable=True),
        sa.Column('last_active', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_city_id'), 'users', ['city_id'], unique=False)

    # Create verification_records table
    op.create_table(
        'verification_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('method', postgresql.ENUM('sms', 'email', 'mail_code', 'voter_roll', 'id_proofing',
                  name='verificationmethod', create_type=False), nullable=False),
        sa.Column('provider', sa.String(), nullable=True),
        sa.Column('city_scope', sa.String(), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'verified', 'rejected', 'expired',
                  name='verificationstatus', create_type=False), server_default='pending'),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_verification_records_id'), 'verification_records', ['id'], unique=False)
    op.create_index(op.f('ix_verification_records_city_scope'), 'verification_records', ['city_scope'], unique=False)

    # Create ballots table
    op.create_table(
        'ballots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('city_id', sa.String(), nullable=False),
        sa.Column('city_name', sa.String(), nullable=False),
        sa.Column('election_date', sa.Date(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('source_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ballots_id'), 'ballots', ['id'], unique=False)
    op.create_index(op.f('ix_ballots_city_id'), 'ballots', ['city_id'], unique=False)
    op.create_index(op.f('ix_ballots_election_date'), 'ballots', ['election_date'], unique=False)

    # Create contests table
    op.create_table(
        'contests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('ballot_id', sa.Integer(), nullable=False),
        sa.Column('type', postgresql.ENUM('race', 'measure', name='contesttype', create_type=False), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('jurisdiction', sa.String(), nullable=True),
        sa.Column('office', sa.String(), nullable=True),
        sa.Column('seat_count', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('display_order', sa.Integer(), server_default='0'),
        sa.ForeignKeyConstraint(['ballot_id'], ['ballots.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contests_id'), 'contests', ['id'], unique=False)

    # Create candidates table
    op.create_table(
        'candidates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('contest_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('filing_id', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('status', postgresql.ENUM('pending', 'verified', 'active', 'withdrawn', 'disqualified',
                  name='candidatestatus', create_type=False), nullable=False, server_default='pending'),
        sa.Column('profile_fields', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('photo_url', sa.String(), nullable=True),
        sa.Column('website', sa.String(), nullable=True),
        sa.Column('identity_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('identity_verified_at', sa.Date(), nullable=True),
        sa.Column('display_order', sa.Integer(), server_default='0'),
        sa.ForeignKeyConstraint(['contest_id'], ['contests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_candidates_id'), 'candidates', ['id'], unique=False)
    op.create_index(op.f('ix_candidates_filing_id'), 'candidates', ['filing_id'], unique=False)

    # Create measures table
    op.create_table(
        'measures',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('contest_id', sa.Integer(), nullable=False),
        sa.Column('measure_number', sa.String(), nullable=True),
        sa.Column('measure_text', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('fiscal_notes', sa.Text(), nullable=True),
        sa.Column('pro_statement', sa.Text(), nullable=True),
        sa.Column('con_statement', sa.Text(), nullable=True),
        sa.Column('pro_contacts', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('con_contacts', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['contest_id'], ['contests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_measures_id'), 'measures', ['id'], unique=False)

    # Create questions table
    op.create_table(
        'questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('contest_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=True),
        sa.Column('current_version_id', sa.Integer(), nullable=True),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('issue_tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('status', postgresql.ENUM('pending', 'approved', 'merged', 'removed',
                  name='questionstatus', create_type=False), nullable=False, server_default='pending'),
        sa.Column('cluster_id', sa.Integer(), nullable=True),
        sa.Column('embedding', postgresql.VECTOR(384), nullable=True),
        sa.Column('context', sa.Text(), nullable=True),
        sa.Column('upvotes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('downvotes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rank_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('representation_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_flagged', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('moderation_notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['contest_id'], ['contests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_questions_id'), 'questions', ['id'], unique=False)
    op.create_index(op.f('ix_questions_contest_id'), 'questions', ['contest_id'], unique=False)
    op.create_index(op.f('ix_questions_status'), 'questions', ['status'], unique=False)
    op.create_index(op.f('ix_questions_cluster_id'), 'questions', ['cluster_id'], unique=False)
    op.create_index(op.f('ix_questions_rank_score'), 'questions', ['rank_score'], unique=False)
    op.create_index(op.f('ix_questions_issue_tags'), 'questions', ['issue_tags'], unique=False, postgresql_using='gin')
    # Create vector index for embedding similarity search (using ivfflat)
    op.execute('CREATE INDEX idx_question_embedding ON questions USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)')

    # Create question_versions table
    op.create_table(
        'question_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('edit_author_id', sa.Integer(), nullable=True),
        sa.Column('edit_reason', sa.Text(), nullable=True),
        sa.Column('diff_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['edit_author_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_question_versions_id'), 'question_versions', ['id'], unique=False)
    op.create_index(op.f('ix_question_versions_question_id'), 'question_versions', ['question_id'], unique=False)

    # Create votes table
    op.create_table(
        'votes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('value', sa.Integer(), nullable=False),
        sa.Column('device_risk_score', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('weight', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_votes_id'), 'votes', ['id'], unique=False)
    op.create_index(op.f('ix_votes_user_id'), 'votes', ['user_id'], unique=False)
    op.create_index(op.f('ix_votes_question_id'), 'votes', ['question_id'], unique=False)
    op.create_index('idx_user_question_vote', 'votes', ['user_id', 'question_id'], unique=True)

    # Create video_answers table
    op.create_table(
        'video_answers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('candidate_id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('question_version_id', sa.Integer(), nullable=True),
        sa.Column('video_asset_id', sa.String(), nullable=False),
        sa.Column('video_url', sa.String(), nullable=True),
        sa.Column('duration', sa.Float(), nullable=False),
        sa.Column('transcript_id', sa.String(), nullable=True),
        sa.Column('transcript_text', sa.Text(), nullable=True),
        sa.Column('transcript_url', sa.String(), nullable=True),
        sa.Column('captions_url', sa.String(), nullable=True),
        sa.Column('provenance_hash', sa.String(), nullable=True),
        sa.Column('authenticity_metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', postgresql.ENUM('draft', 'processing', 'published', 'withdrawn',
                  name='answerstatus', create_type=False), nullable=False, server_default='draft'),
        sa.Column('position_summary', sa.Text(), nullable=True),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.Column('tradeoff_acknowledged', sa.Text(), nullable=True),
        sa.Column('implementation_plan', sa.Text(), nullable=True),
        sa.Column('measurement_criteria', sa.Text(), nullable=True),
        sa.Column('values_statement', sa.Text(), nullable=True),
        sa.Column('is_open_question', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('has_correction', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('correction_text', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_version_id'], ['question_versions.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_video_answers_id'), 'video_answers', ['id'], unique=False)
    op.create_index(op.f('ix_video_answers_candidate_id'), 'video_answers', ['candidate_id'], unique=False)
    op.create_index(op.f('ix_video_answers_question_id'), 'video_answers', ['question_id'], unique=False)

    # Create rebuttals table
    op.create_table(
        'rebuttals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('candidate_id', sa.Integer(), nullable=False),
        sa.Column('target_answer_id', sa.Integer(), nullable=False),
        sa.Column('target_claim_text', sa.Text(), nullable=False),
        sa.Column('target_claim_timestamp', sa.Float(), nullable=True),
        sa.Column('video_asset_id', sa.String(), nullable=False),
        sa.Column('video_url', sa.String(), nullable=True),
        sa.Column('duration', sa.Float(), nullable=False),
        sa.Column('transcript_id', sa.String(), nullable=True),
        sa.Column('transcript_text', sa.Text(), nullable=True),
        sa.Column('transcript_url', sa.String(), nullable=True),
        sa.Column('status', postgresql.ENUM('draft', 'processing', 'published', 'withdrawn',
                  name='answerstatus', create_type=False), nullable=False, server_default='draft'),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_answer_id'], ['video_answers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rebuttals_id'), 'rebuttals', ['id'], unique=False)
    op.create_index(op.f('ix_rebuttals_candidate_id'), 'rebuttals', ['candidate_id'], unique=False)
    op.create_index(op.f('ix_rebuttals_target_answer_id'), 'rebuttals', ['target_answer_id'], unique=False)

    # Create claims table
    op.create_table(
        'claims',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('answer_id', sa.Integer(), nullable=False),
        sa.Column('claim_snippet', sa.Text(), nullable=False),
        sa.Column('claim_timestamp', sa.Float(), nullable=True),
        sa.Column('sources', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('reviewer_notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['answer_id'], ['video_answers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_claims_id'), 'claims', ['id'], unique=False)
    op.create_index(op.f('ix_claims_answer_id'), 'claims', ['answer_id'], unique=False)

    # Create reports table
    op.create_table(
        'reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('reporter_id', sa.Integer(), nullable=True),
        sa.Column('target_type', sa.String(), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('reason', postgresql.ENUM('spam', 'doxxing', 'threats', 'harassment', 'off_topic',
                  'misinformation', 'other', name='reportreason', create_type=False), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', postgresql.ENUM('pending', 'under_review', 'resolved', 'dismissed',
                  name='reportstatus', create_type=False), nullable=False, server_default='pending'),
        sa.Column('resolved_by_id', sa.Integer(), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['reporter_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['resolved_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reports_id'), 'reports', ['id'], unique=False)
    op.create_index(op.f('ix_reports_reporter_id'), 'reports', ['reporter_id'], unique=False)
    op.create_index(op.f('ix_reports_status'), 'reports', ['status'], unique=False)

    # Create moderation_actions table
    op.create_table(
        'moderation_actions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('target_type', sa.String(), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('action_type', postgresql.ENUM('approve', 'remove', 'merge', 'flag', 'warn_user', 'suspend_user',
                  name='moderationactiontype', create_type=False), nullable=False),
        sa.Column('moderator_id', sa.Integer(), nullable=True),
        sa.Column('rationale_code', sa.String(), nullable=True),
        sa.Column('rationale_text', sa.Text(), nullable=True),
        sa.Column('report_id', sa.Integer(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['moderator_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['report_id'], ['reports.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_moderation_actions_id'), 'moderation_actions', ['id'], unique=False)
    op.create_index(op.f('ix_moderation_actions_target_id'), 'moderation_actions', ['target_id'], unique=False)
    op.create_index(op.f('ix_moderation_actions_moderator_id'), 'moderation_actions', ['moderator_id'], unique=False)

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('event_type', postgresql.ENUM('user_created', 'user_verified', 'question_submitted',
                  'question_voted', 'answer_published', 'rebuttal_published', 'moderation_action',
                  'candidate_verified', 'ballot_created', 'contest_created', 'security_alert',
                  name='auditeventtype', create_type=False), nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=True),
        sa.Column('target_type', sa.String(), nullable=True),
        sa.Column('target_id', sa.Integer(), nullable=True),
        sa.Column('event_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address_hash', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('city_scope', sa.String(), nullable=True),
        sa.Column('severity', sa.String(), nullable=False, server_default='info'),
        sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_audit_logs_event_type'), 'audit_logs', ['event_type'], unique=False)
    op.create_index(op.f('ix_audit_logs_actor_id'), 'audit_logs', ['actor_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_city_scope'), 'audit_logs', ['city_scope'], unique=False)

    # Create follows table
    op.create_table(
        'follows',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('target_type', postgresql.ENUM('contest', 'candidate', 'issue_tag',
                  name='followtargettype', create_type=False), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=True),
        sa.Column('target_value', sa.String(), nullable=True),
        sa.Column('notification_prefs', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_follows_id'), 'follows', ['id'], unique=False)
    op.create_index(op.f('ix_follows_user_id'), 'follows', ['user_id'], unique=False)
    op.create_index('idx_user_follow_target', 'follows',
                   ['user_id', 'target_type', 'target_id', 'target_value'], unique=True)


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign key dependencies)
    op.drop_table('follows')
    op.drop_table('audit_logs')
    op.drop_table('moderation_actions')
    op.drop_table('reports')
    op.drop_table('claims')
    op.drop_table('rebuttals')
    op.drop_table('video_answers')
    op.drop_table('votes')
    op.drop_table('question_versions')
    op.drop_table('questions')
    op.drop_table('measures')
    op.drop_table('candidates')
    op.drop_table('contests')
    op.drop_table('ballots')
    op.drop_table('verification_records')
    op.drop_table('users')

    # Drop enum types
    op.execute('DROP TYPE IF EXISTS followtargettype')
    op.execute('DROP TYPE IF EXISTS auditeventtype')
    op.execute('DROP TYPE IF EXISTS moderationactiontype')
    op.execute('DROP TYPE IF EXISTS reportreason')
    op.execute('DROP TYPE IF EXISTS reportstatus')
    op.execute('DROP TYPE IF EXISTS answerstatus')
    op.execute('DROP TYPE IF EXISTS questionstatus')
    op.execute('DROP TYPE IF EXISTS candidatestatus')
    op.execute('DROP TYPE IF EXISTS contesttype')
    op.execute('DROP TYPE IF EXISTS verificationmethod')
    op.execute('DROP TYPE IF EXISTS verificationstatus')
    op.execute('DROP TYPE IF EXISTS userrole')

    # Drop pgvector extension
    op.execute('DROP EXTENSION IF EXISTS vector')
