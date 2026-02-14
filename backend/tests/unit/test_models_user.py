"""
Unit tests for User and VerificationRecord models.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

from app.models.user import (
    User,
    VerificationRecord,
    UserRole,
    VerificationStatus,
    VerificationMethod,
)


class TestUserModel:
    """Test User model functionality."""

    def test_create_user(self, db_session):
        """Test creating a new user."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_here",
            full_name="Test User",
            role=UserRole.VOTER,
        )
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.role == UserRole.VOTER
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.email_verified is False
        assert user.verification_status == VerificationStatus.PENDING

    def test_user_unique_email(self, db_session):
        """Test that email must be unique."""
        user1 = User(
            email="test@example.com",
            hashed_password="hashed1",
        )
        user2 = User(
            email="test@example.com",
            hashed_password="hashed2",
        )

        db_session.add(user1)
        db_session.commit()

        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_roles(self, db_session):
        """Test different user roles."""
        roles = [UserRole.VOTER, UserRole.CANDIDATE, UserRole.ADMIN, UserRole.MODERATOR, UserRole.CITY_STAFF]

        for role in roles:
            user = User(
                email=f"{role.value}@example.com",
                hashed_password="hashed",
                role=role,
            )
            db_session.add(user)
            db_session.commit()

            assert user.role == role

    def test_user_city_scope(self, db_session):
        """Test user city scoping."""
        user = User(
            email="voter@example.com",
            hashed_password="hashed",
            city_id="san-francisco",
            city_name="San Francisco",
        )
        db_session.add(user)
        db_session.commit()

        assert user.city_id == "san-francisco"
        assert user.city_name == "San Francisco"

    def test_user_email_verification(self, db_session):
        """Test email verification flow."""
        user = User(
            email="verify@example.com",
            hashed_password="hashed",
            email_verification_token="token123",
            email_verification_expires=datetime.utcnow() + timedelta(days=1),
        )
        db_session.add(user)
        db_session.commit()

        assert user.email_verified is False
        assert user.email_verification_token == "token123"
        assert user.email_verification_expires > datetime.utcnow()

        # Verify email
        user.email_verified = True
        user.email_verification_token = None
        db_session.commit()

        assert user.email_verified is True
        assert user.email_verification_token is None

    def test_user_password_reset(self, db_session):
        """Test password reset flow."""
        user = User(
            email="reset@example.com",
            hashed_password="old_hash",
        )
        db_session.add(user)
        db_session.commit()

        # Request password reset
        user.password_reset_token = "reset_token_123"
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        db_session.commit()

        assert user.password_reset_token == "reset_token_123"
        assert user.password_reset_expires > datetime.utcnow()

    def test_user_two_factor_auth(self, db_session):
        """Test two-factor authentication setup."""
        user = User(
            email="2fa@example.com",
            hashed_password="hashed",
        )
        db_session.add(user)
        db_session.commit()

        assert user.two_factor_enabled is False
        assert user.two_factor_secret is None

        # Enable 2FA
        user.two_factor_enabled = True
        user.two_factor_secret = "SECRET_KEY"
        user.backup_codes = ["CODE1", "CODE2", "CODE3"]
        db_session.commit()

        assert user.two_factor_enabled is True
        assert user.two_factor_secret == "SECRET_KEY"
        assert len(user.backup_codes) == 3

    def test_user_oauth_provider(self, db_session):
        """Test OAuth provider integration."""
        user = User(
            email="oauth@example.com",
            hashed_password="hashed",
            oauth_provider="google",
            oauth_id="google_user_123",
        )
        db_session.add(user)
        db_session.commit()

        assert user.oauth_provider == "google"
        assert user.oauth_id == "google_user_123"

    def test_user_activity_tracking(self, db_session):
        """Test user activity tracking."""
        user = User(
            email="active@example.com",
            hashed_password="hashed",
        )
        db_session.add(user)
        db_session.commit()

        # Update activity
        user.last_login = datetime.utcnow()
        user.last_login_ip = "192.168.1.1"
        user.last_login_user_agent = "Mozilla/5.0"
        user.last_active = datetime.utcnow()
        db_session.commit()

        assert user.last_login is not None
        assert user.last_login_ip == "192.168.1.1"
        assert user.last_login_user_agent == "Mozilla/5.0"

    def test_user_security_tracking(self, db_session):
        """Test security features like account locking."""
        user = User(
            email="security@example.com",
            hashed_password="hashed",
        )
        db_session.add(user)
        db_session.commit()

        assert user.failed_login_attempts == 0
        assert user.account_locked_until is None

        # Increment failed attempts
        user.failed_login_attempts = 3
        db_session.commit()

        assert user.failed_login_attempts == 3

        # Lock account
        user.account_locked_until = datetime.utcnow() + timedelta(minutes=30)
        user.locked_reason = "Too many failed login attempts"
        db_session.commit()

        assert user.account_locked_until > datetime.utcnow()
        assert user.locked_reason is not None

    def test_user_repr(self, db_session):
        """Test user string representation."""
        user = User(
            email="repr@example.com",
            hashed_password="hashed",
            role=UserRole.CANDIDATE,
        )
        db_session.add(user)
        db_session.commit()

        assert repr(user) == "<User repr@example.com (candidate)>"


class TestVerificationRecordModel:
    """Test VerificationRecord model functionality."""

    def test_create_verification_record(self, db_session):
        """Test creating a verification record."""
        user = User(
            email="verify@example.com",
            hashed_password="hashed",
        )
        db_session.add(user)
        db_session.commit()

        record = VerificationRecord(
            user_id=user.id,
            method=VerificationMethod.EMAIL,
            city_scope="san-francisco",
            status=VerificationStatus.VERIFIED,
            verified_at=datetime.utcnow(),
        )
        db_session.add(record)
        db_session.commit()

        assert record.id is not None
        assert record.user_id == user.id
        assert record.method == VerificationMethod.EMAIL
        assert record.status == VerificationStatus.VERIFIED

    def test_verification_methods(self, db_session):
        """Test different verification methods."""
        user = User(
            email="methods@example.com",
            hashed_password="hashed",
        )
        db_session.add(user)
        db_session.commit()

        methods = [
            VerificationMethod.SMS,
            VerificationMethod.EMAIL,
            VerificationMethod.MAIL_CODE,
            VerificationMethod.VOTER_ROLL,
            VerificationMethod.ID_PROOFING,
        ]

        for method in methods:
            record = VerificationRecord(
                user_id=user.id,
                method=method,
                city_scope="test-city",
            )
            db_session.add(record)
            db_session.commit()

            assert record.method == method

    def test_verification_status_flow(self, db_session):
        """Test verification status transitions."""
        user = User(
            email="status@example.com",
            hashed_password="hashed",
        )
        db_session.add(user)
        db_session.commit()

        record = VerificationRecord(
            user_id=user.id,
            method=VerificationMethod.SMS,
            city_scope="test-city",
            status=VerificationStatus.PENDING,
        )
        db_session.add(record)
        db_session.commit()

        assert record.status == VerificationStatus.PENDING

        # Verify
        record.status = VerificationStatus.VERIFIED
        record.verified_at = datetime.utcnow()
        db_session.commit()

        assert record.status == VerificationStatus.VERIFIED
        assert record.verified_at is not None

    def test_verification_with_provider(self, db_session):
        """Test verification with external provider."""
        user = User(
            email="provider@example.com",
            hashed_password="hashed",
        )
        db_session.add(user)
        db_session.commit()

        record = VerificationRecord(
            user_id=user.id,
            method=VerificationMethod.ID_PROOFING,
            provider="id.me",
            city_scope="test-city",
            metadata={"provider_session_id": "session_123"},
        )
        db_session.add(record)
        db_session.commit()

        assert record.provider == "id.me"
        assert record.metadata["provider_session_id"] == "session_123"

    def test_verification_expiration(self, db_session):
        """Test verification expiration."""
        user = User(
            email="expire@example.com",
            hashed_password="hashed",
        )
        db_session.add(user)
        db_session.commit()

        record = VerificationRecord(
            user_id=user.id,
            method=VerificationMethod.EMAIL,
            city_scope="test-city",
            expires_at=datetime.utcnow() + timedelta(days=365),
        )
        db_session.add(record)
        db_session.commit()

        assert record.expires_at > datetime.utcnow()

    def test_verification_user_relationship(self, db_session):
        """Test relationship between user and verification records."""
        user = User(
            email="relation@example.com",
            hashed_password="hashed",
        )
        db_session.add(user)
        db_session.commit()

        # Create multiple verification records
        for i in range(3):
            record = VerificationRecord(
                user_id=user.id,
                method=VerificationMethod.SMS,
                city_scope=f"city-{i}",
            )
            db_session.add(record)
        db_session.commit()

        db_session.refresh(user)
        assert len(user.verification_records) == 3

    def test_verification_cascade_delete(self, db_session):
        """Test that verification records are deleted when user is deleted."""
        user = User(
            email="cascade@example.com",
            hashed_password="hashed",
        )
        db_session.add(user)
        db_session.commit()

        record = VerificationRecord(
            user_id=user.id,
            method=VerificationMethod.EMAIL,
            city_scope="test-city",
        )
        db_session.add(record)
        db_session.commit()

        user_id = user.id
        db_session.delete(user)
        db_session.commit()

        # Verification record should be deleted
        result = db_session.query(VerificationRecord).filter_by(user_id=user_id).first()
        assert result is None

    def test_verification_repr(self, db_session):
        """Test verification record string representation."""
        user = User(
            email="repr@example.com",
            hashed_password="hashed",
        )
        db_session.add(user)
        db_session.commit()

        record = VerificationRecord(
            user_id=user.id,
            method=VerificationMethod.SMS,
            city_scope="test-city",
            status=VerificationStatus.VERIFIED,
        )
        db_session.add(record)
        db_session.commit()

        expected = f"<VerificationRecord user={user.id} method=sms status=verified>"
        assert repr(record) == expected
