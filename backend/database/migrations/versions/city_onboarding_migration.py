"""Add city onboarding tables

Revision ID: city_onboarding_001
Revises: d49625079456
Create Date: 2026-02-14 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'city_onboarding_001'
down_revision = 'd49625079456'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create city status enum
    op.execute("""
        CREATE TYPE citystatus AS ENUM (
            'pending_verification', 'active', 'suspended', 'inactive'
        )
    """)

    # Create city staff role enum
    op.execute("""
        CREATE TYPE citystaffrole AS ENUM (
            'owner', 'admin', 'editor', 'moderator', 'viewer'
        )
    """)

    # Create cities table
    op.create_table(
        'cities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('state', sa.String(2), nullable=False),
        sa.Column('county', sa.String(), nullable=True),
        sa.Column('population', sa.Integer(), nullable=True),
        sa.Column('primary_contact_name', sa.String(), nullable=False),
        sa.Column('primary_contact_email', sa.String(), nullable=False),
        sa.Column('primary_contact_phone', sa.String(), nullable=True),
        sa.Column('primary_contact_title', sa.String(), nullable=True),
        sa.Column('status', postgresql.ENUM('pending_verification', 'active', 'suspended', 'inactive',
                  name='citystatus', create_type=False), nullable=False, server_default='pending_verification'),
        sa.Column('verification_method', sa.String(), nullable=True),
        sa.Column('verification_notes', sa.Text(), nullable=True),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('verified_by', sa.String(), nullable=True),
        sa.Column('documentation_urls', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('official_email_domain', sa.String(), nullable=True),
        sa.Column('logo_url', sa.String(), nullable=True),
        sa.Column('primary_color', sa.String(7), nullable=True),
        sa.Column('secondary_color', sa.String(7), nullable=True),
        sa.Column('timezone', sa.String(), nullable=False, server_default='America/Los_Angeles'),
        sa.Column('settings', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('features', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('next_election_date', sa.Date(), nullable=True),
        sa.Column('election_info_url', sa.String(), nullable=True),
        sa.Column('subscription_tier', sa.String(), nullable=False, server_default='free'),
        sa.Column('subscription_expires', sa.DateTime(), nullable=True),
        sa.Column('total_voters', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_questions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_ballots', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('onboarding_completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('onboarding_step', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('onboarding_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cities_id'), 'cities', ['id'], unique=False)
    op.create_index(op.f('ix_cities_slug'), 'cities', ['slug'], unique=True)
    op.create_index(op.f('ix_cities_state'), 'cities', ['state'], unique=False)
    op.create_index(op.f('ix_cities_status'), 'cities', ['status'], unique=False)

    # Create city_staff table
    op.create_table(
        'city_staff',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('city_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', postgresql.ENUM('owner', 'admin', 'editor', 'moderator', 'viewer',
                  name='citystaffrole', create_type=False), nullable=False, server_default='viewer'),
        sa.Column('invited_by_id', sa.Integer(), nullable=True),
        sa.Column('invited_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_access', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['city_id'], ['cities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['invited_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_city_staff_id'), 'city_staff', ['id'], unique=False)
    op.create_index(op.f('ix_city_staff_city_id'), 'city_staff', ['city_id'], unique=False)
    op.create_index(op.f('ix_city_staff_user_id'), 'city_staff', ['user_id'], unique=False)
    op.create_index('idx_city_user_staff', 'city_staff', ['city_id', 'user_id'], unique=True)

    # Create city_invitations table
    op.create_table(
        'city_invitations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('city_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('role', postgresql.ENUM('owner', 'admin', 'editor', 'moderator', 'viewer',
                  name='citystaffrole', create_type=False), nullable=False, server_default='viewer'),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('invited_by_id', sa.Integer(), nullable=True),
        sa.Column('invited_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('accepted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('accepted_at', sa.DateTime(), nullable=True),
        sa.Column('accepted_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['city_id'], ['cities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['invited_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['accepted_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_city_invitations_id'), 'city_invitations', ['id'], unique=False)
    op.create_index(op.f('ix_city_invitations_email'), 'city_invitations', ['email'], unique=False)
    op.create_index(op.f('ix_city_invitations_token'), 'city_invitations', ['token'], unique=True)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('city_invitations')
    op.drop_table('city_staff')
    op.drop_table('cities')

    # Drop enum types
    op.execute('DROP TYPE IF EXISTS citystaffrole')
    op.execute('DROP TYPE IF EXISTS citystatus')
