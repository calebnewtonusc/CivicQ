"""Add advanced authentication fields

Revision ID: add_advanced_auth
Revises: city_onboarding_001
Create Date: 2024-02-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_advanced_auth'
down_revision = 'city_onboarding_001'
branch_labels = None
depends_on = None


def upgrade():
    # Add email verification fields
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('email_verification_token', sa.String(), nullable=True))
    op.add_column('users', sa.Column('email_verification_expires', sa.DateTime(), nullable=True))

    # Add password reset fields
    op.add_column('users', sa.Column('password_reset_token', sa.String(), nullable=True))
    op.add_column('users', sa.Column('password_reset_expires', sa.DateTime(), nullable=True))

    # Add 2FA fields
    op.add_column('users', sa.Column('two_factor_enabled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('two_factor_secret', sa.String(), nullable=True))
    op.add_column('users', sa.Column('backup_codes', postgresql.JSON(), nullable=True))

    # Add OAuth fields
    op.add_column('users', sa.Column('oauth_provider', sa.String(), nullable=True))
    op.add_column('users', sa.Column('oauth_id', sa.String(), nullable=True))

    # Add last login tracking
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))

    # Create indexes for performance
    op.create_index('idx_users_email_verification_token', 'users', ['email_verification_token'])
    op.create_index('idx_users_password_reset_token', 'users', ['password_reset_token'])
    op.create_index('idx_users_oauth_provider_id', 'users', ['oauth_provider', 'oauth_id'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_users_oauth_provider_id', table_name='users')
    op.drop_index('idx_users_password_reset_token', table_name='users')
    op.drop_index('idx_users_email_verification_token', table_name='users')

    # Drop columns
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'oauth_id')
    op.drop_column('users', 'oauth_provider')
    op.drop_column('users', 'backup_codes')
    op.drop_column('users', 'two_factor_secret')
    op.drop_column('users', 'two_factor_enabled')
    op.drop_column('users', 'password_reset_expires')
    op.drop_column('users', 'password_reset_token')
    op.drop_column('users', 'email_verification_expires')
    op.drop_column('users', 'email_verification_token')
    op.drop_column('users', 'email_verified')
