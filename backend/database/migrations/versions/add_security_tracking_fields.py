"""add security tracking fields

Revision ID: security_tracking_001
Revises: add_advanced_auth_fields
Create Date: 2026-02-14

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'security_tracking_001'
down_revision = 'add_advanced_auth_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add security tracking fields
    op.add_column('users', sa.Column('last_login_ip', sa.String(), nullable=True))
    op.add_column('users', sa.Column('last_login_user_agent', sa.String(), nullable=True))
    op.add_column('users', sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('account_locked_until', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('locked_reason', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove security tracking fields
    op.drop_column('users', 'locked_reason')
    op.drop_column('users', 'account_locked_until')
    op.drop_column('users', 'failed_login_attempts')
    op.drop_column('users', 'last_login_user_agent')
    op.drop_column('users', 'last_login_ip')
