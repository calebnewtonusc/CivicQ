"""
Alembic Migration: Add Video Models

Creates tables for video storage, processing, and analytics.

Revision ID: add_video_models
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_video_models'
down_revision = 'add_advanced_auth'
branch_labels = None
depends_on = None


def upgrade():
    # Create videos table
    op.create_table(
        'videos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('answer_id', sa.Integer(), nullable=True),

        # Basic Info
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),

        # Upload Info
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),

        # Video Properties
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('fps', sa.Float(), nullable=True),
        sa.Column('codec', sa.String(50), nullable=True),
        sa.Column('bitrate', sa.Integer(), nullable=True),

        # Processing Status
        sa.Column('status', sa.String(20), nullable=False, server_default='uploading'),
        sa.Column('processing_started_at', sa.DateTime(), nullable=True),
        sa.Column('processing_completed_at', sa.DateTime(), nullable=True),
        sa.Column('processing_error', sa.Text(), nullable=True),
        sa.Column('processing_progress', sa.Integer(), server_default='0'),

        # Storage
        sa.Column('storage_provider', sa.String(50), nullable=False),
        sa.Column('bucket_name', sa.String(255), nullable=False),
        sa.Column('storage_region', sa.String(100), nullable=True),
        sa.Column('original_key', sa.String(500), nullable=False),
        sa.Column('original_url', sa.String(1000), nullable=True),

        # Transcoded versions
        sa.Column('transcoded_versions', postgresql.JSON(), nullable=True),

        # HLS/DASH Streaming
        sa.Column('hls_master_playlist_key', sa.String(500), nullable=True),
        sa.Column('hls_master_playlist_url', sa.String(1000), nullable=True),
        sa.Column('dash_manifest_key', sa.String(500), nullable=True),
        sa.Column('dash_manifest_url', sa.String(1000), nullable=True),

        # Thumbnails
        sa.Column('thumbnail_key', sa.String(500), nullable=True),
        sa.Column('thumbnail_url', sa.String(1000), nullable=True),
        sa.Column('sprite_sheet_key', sa.String(500), nullable=True),
        sa.Column('sprite_sheet_url', sa.String(1000), nullable=True),
        sa.Column('thumbnail_timestamps', postgresql.JSON(), nullable=True),

        # Transcription
        sa.Column('transcription_key', sa.String(500), nullable=True),
        sa.Column('transcription_url', sa.String(1000), nullable=True),
        sa.Column('transcription_text', sa.Text(), nullable=True),
        sa.Column('transcription_language', sa.String(10), nullable=True),
        sa.Column('has_captions', sa.Boolean(), server_default='false'),
        sa.Column('captions_vtt_key', sa.String(500), nullable=True),
        sa.Column('captions_vtt_url', sa.String(1000), nullable=True),

        # CDN
        sa.Column('cdn_enabled', sa.Boolean(), server_default='true'),
        sa.Column('cdn_distribution_id', sa.String(255), nullable=True),

        # Analytics
        sa.Column('view_count', sa.Integer(), server_default='0'),
        sa.Column('watch_time_seconds', sa.Integer(), server_default='0'),

        # Metadata
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['answer_id'], ['answers.id'], ondelete='SET NULL'),
    )

    # Create indexes
    op.create_index('ix_videos_user_id', 'videos', ['user_id'])
    op.create_index('ix_videos_answer_id', 'videos', ['answer_id'])
    op.create_index('ix_videos_status', 'videos', ['status'])
    op.create_index('ix_videos_created_at', 'videos', ['created_at'])

    # Create video_analytics table
    op.create_table(
        'video_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('video_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),

        # Session info
        sa.Column('session_id', sa.String(100), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),

        # Playback info
        sa.Column('quality_selected', sa.String(20), nullable=True),
        sa.Column('watch_duration_seconds', sa.Float(), nullable=False),
        sa.Column('completion_percentage', sa.Float(), nullable=False),

        # Engagement
        sa.Column('paused_count', sa.Integer(), server_default='0'),
        sa.Column('seeked_count', sa.Integer(), server_default='0'),
        sa.Column('quality_changes', sa.Integer(), server_default='0'),

        # Buffering
        sa.Column('buffering_events', sa.Integer(), server_default='0'),
        sa.Column('total_buffering_time_seconds', sa.Float(), server_default='0'),

        # Timestamps
        sa.Column('started_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )

    # Create indexes
    op.create_index('ix_video_analytics_video_id', 'video_analytics', ['video_id'])
    op.create_index('ix_video_analytics_user_id', 'video_analytics', ['user_id'])


def downgrade():
    op.drop_index('ix_video_analytics_user_id', table_name='video_analytics')
    op.drop_index('ix_video_analytics_video_id', table_name='video_analytics')
    op.drop_table('video_analytics')

    op.drop_index('ix_videos_created_at', table_name='videos')
    op.drop_index('ix_videos_status', table_name='videos')
    op.drop_index('ix_videos_answer_id', table_name='videos')
    op.drop_index('ix_videos_user_id', table_name='videos')
    op.drop_table('videos')
