"""
Unit tests for Authentication Service.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException

from app.services.auth_service import AuthService
from app.models.user import User, UserRole, VerificationStatus
from app.schemas.user import UserCreate, UserLogin
from app.core.security import verify_password


class TestAuthServiceCreateUser:
    """Test user creation functionality."""

    def test_create_user_success(self, db_session):
        """Test successful user creation."""
        user_data = UserCreate(
            email="newuser@example.com",
            password="SecurePass123!",
            full_name="New User",
            city="San Francisco",
        )

        with patch('app.services.auth_service.AuthService.request_email_verification'):
            user = AuthService.create_user(db_session, user_data)

        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.full_name == "New User"
        assert user.role == UserRole.VOTER
        assert user.verification_status == VerificationStatus.PENDING
        assert user.email_verified is False
        assert verify_password("SecurePass123!", user.hashed_password)

    def test_create_user_duplicate_email(self, db_session):
        """Test that creating user with duplicate email fails."""
        user_data = UserCreate(
            email="duplicate@example.com",
            password="SecurePass123!",
            full_name="First User",
            city="Boston",
        )

        with patch('app.services.auth_service.AuthService.request_email_verification'):
            AuthService.create_user(db_session, user_data)

        # Try to create another user with same email
        with pytest.raises(HTTPException) as exc_info:
            AuthService.create_user(db_session, user_data)

        assert exc_info.value.status_code == 400
        assert "already registered" in str(exc_info.value.detail)

    def test_create_user_sends_verification_email(self, db_session):
        """Test that email verification is sent on user creation."""
        user_data = UserCreate(
            email="verify@example.com",
            password="SecurePass123!",
            full_name="Verify User",
            city="Seattle",
        )

        with patch('app.services.auth_service.AuthService.request_email_verification') as mock_verify:
            user = AuthService.create_user(db_session, user_data)
            mock_verify.assert_called_once()

    def test_create_user_handles_email_failure(self, db_session):
        """Test that user creation succeeds even if email fails."""
        user_data = UserCreate(
            email="emailfail@example.com",
            password="SecurePass123!",
            full_name="Email Fail User",
            city="Portland",
        )

        with patch('app.services.auth_service.AuthService.request_email_verification') as mock_verify:
            mock_verify.side_effect = Exception("Email service error")

            # Should not raise exception
            user = AuthService.create_user(db_session, user_data)
            assert user.id is not None


class TestAuthServiceAuthentication:
    """Test user authentication functionality."""

    def test_authenticate_user_success(self, db_session):
        """Test successful user authentication."""
        # Create user
        user_data = UserCreate(
            email="auth@example.com",
            password="SecurePass123!",
            full_name="Auth User",
            city="Chicago",
        )

        with patch('app.services.auth_service.AuthService.request_email_verification'):
            user = AuthService.create_user(db_session, user_data)
            user.is_active = True
            db_session.commit()

        # Authenticate
        login_data = UserLogin(
            email="auth@example.com",
            password="SecurePass123!",
        )

        with patch('app.services.auth_service.session_service.track_login'):
            authenticated_user, token = AuthService.authenticate_user(db_session, login_data)

        assert authenticated_user.id == user.id
        assert token is not None

    def test_authenticate_user_wrong_password(self, db_session):
        """Test authentication with wrong password."""
        user_data = UserCreate(
            email="wrongpass@example.com",
            password="SecurePass123!",
            full_name="Wrong Pass User",
            city="Miami",
        )

        with patch('app.services.auth_service.AuthService.request_email_verification'):
            AuthService.create_user(db_session, user_data)

        login_data = UserLogin(
            email="wrongpass@example.com",
            password="WrongPassword!",
        )

        with pytest.raises(HTTPException) as exc_info:
            AuthService.authenticate_user(db_session, login_data)

        assert exc_info.value.status_code == 401
        assert "Incorrect" in str(exc_info.value.detail)

    def test_authenticate_user_nonexistent_email(self, db_session):
        """Test authentication with non-existent email."""
        login_data = UserLogin(
            email="doesnotexist@example.com",
            password="AnyPassword!",
        )

        with pytest.raises(HTTPException) as exc_info:
            AuthService.authenticate_user(db_session, login_data)

        assert exc_info.value.status_code == 401

    def test_authenticate_inactive_user(self, db_session):
        """Test that inactive users cannot authenticate."""
        user_data = UserCreate(
            email="inactive@example.com",
            password="SecurePass123!",
            full_name="Inactive User",
            city="Denver",
        )

        with patch('app.services.auth_service.AuthService.request_email_verification'):
            user = AuthService.create_user(db_session, user_data)
            user.is_active = False
            db_session.commit()

        login_data = UserLogin(
            email="inactive@example.com",
            password="SecurePass123!",
        )

        with pytest.raises(HTTPException) as exc_info:
            AuthService.authenticate_user(db_session, login_data)

        assert exc_info.value.status_code == 403 or exc_info.value.status_code == 401


class TestAuthServicePasswordReset:
    """Test password reset functionality."""

    def test_request_password_reset(self, db_session):
        """Test requesting a password reset."""
        # Create user
        user_data = UserCreate(
            email="reset@example.com",
            password="OldPassword123!",
            full_name="Reset User",
            city="Austin",
        )

        with patch('app.services.auth_service.AuthService.request_email_verification'):
            user = AuthService.create_user(db_session, user_data)

        # Request password reset
        with patch('app.services.email_service.email_service.send_password_reset_email'):
            AuthService.request_password_reset(db_session, "reset@example.com")

        db_session.refresh(user)
        assert user.password_reset_token is not None
        assert user.password_reset_expires is not None
        assert user.password_reset_expires > datetime.utcnow()

    def test_request_password_reset_nonexistent_user(self, db_session):
        """Test requesting password reset for non-existent user."""
        # Should not raise exception for security (don't reveal if email exists)
        with patch('app.services.email_service.email_service.send_password_reset_email'):
            AuthService.request_password_reset(db_session, "doesnotexist@example.com")


class TestAuthServiceEmailVerification:
    """Test email verification functionality."""

    def test_verify_email_success(self, db_session):
        """Test successful email verification."""
        # Create user
        user_data = UserCreate(
            email="verifyemail@example.com",
            password="SecurePass123!",
            full_name="Verify Email User",
            city="Phoenix",
        )

        with patch('app.services.auth_service.AuthService.request_email_verification'):
            user = AuthService.create_user(db_session, user_data)

        # Set verification token
        token = "test_verification_token"
        user.email_verification_token = token
        user.email_verification_expires = datetime.utcnow() + timedelta(days=1)
        db_session.commit()

        # Verify email
        AuthService.verify_email(db_session, token)

        db_session.refresh(user)
        assert user.email_verified is True
        assert user.email_verification_token is None

    def test_verify_email_invalid_token(self, db_session):
        """Test email verification with invalid token."""
        with pytest.raises(HTTPException) as exc_info:
            AuthService.verify_email(db_session, "invalid_token")

        assert exc_info.value.status_code == 400

    def test_verify_email_expired_token(self, db_session):
        """Test email verification with expired token."""
        # Create user
        user_data = UserCreate(
            email="expired@example.com",
            password="SecurePass123!",
            full_name="Expired Token User",
            city="Houston",
        )

        with patch('app.services.auth_service.AuthService.request_email_verification'):
            user = AuthService.create_user(db_session, user_data)

        # Set expired verification token
        token = "expired_token"
        user.email_verification_token = token
        user.email_verification_expires = datetime.utcnow() - timedelta(days=1)
        db_session.commit()

        with pytest.raises(HTTPException) as exc_info:
            AuthService.verify_email(db_session, token)

        assert exc_info.value.status_code == 400


class TestAuthServiceAccountSecurity:
    """Test account security features."""

    def test_track_failed_login_attempt(self, db_session):
        """Test tracking failed login attempts."""
        # Create user
        user_data = UserCreate(
            email="security@example.com",
            password="SecurePass123!",
            full_name="Security User",
            city="Philadelphia",
        )

        with patch('app.services.auth_service.AuthService.request_email_verification'):
            user = AuthService.create_user(db_session, user_data)

        # Simulate failed login
        AuthService.track_failed_login(db_session, user.id)

        db_session.refresh(user)
        assert user.failed_login_attempts == 1

    def test_account_lockout_after_max_attempts(self, db_session):
        """Test account lockout after max failed attempts."""
        # Create user
        user_data = UserCreate(
            email="lockout@example.com",
            password="SecurePass123!",
            full_name="Lockout User",
            city="Dallas",
        )

        with patch('app.services.auth_service.AuthService.request_email_verification'):
            user = AuthService.create_user(db_session, user_data)

        # Simulate multiple failed logins
        for _ in range(5):
            AuthService.track_failed_login(db_session, user.id)

        db_session.refresh(user)
        assert user.account_locked_until is not None
        assert user.account_locked_until > datetime.utcnow()

    def test_reset_failed_login_attempts(self, db_session):
        """Test resetting failed login attempts after successful login."""
        # Create user
        user_data = UserCreate(
            email="resetattempts@example.com",
            password="SecurePass123!",
            full_name="Reset Attempts User",
            city="San Diego",
        )

        with patch('app.services.auth_service.AuthService.request_email_verification'):
            user = AuthService.create_user(db_session, user_data)

        # Simulate failed attempts
        user.failed_login_attempts = 3
        db_session.commit()

        # Reset attempts
        AuthService.reset_failed_login_attempts(db_session, user.id)

        db_session.refresh(user)
        assert user.failed_login_attempts == 0


class TestAuthServiceTokenGeneration:
    """Test token generation functionality."""

    def test_generate_access_token(self, db_session):
        """Test generating access token for user."""
        # Create user
        user_data = UserCreate(
            email="token@example.com",
            password="SecurePass123!",
            full_name="Token User",
            city="San Jose",
        )

        with patch('app.services.auth_service.AuthService.request_email_verification'):
            user = AuthService.create_user(db_session, user_data)

        token = AuthService.generate_access_token(user)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_user_info(self, db_session):
        """Test that token contains user information."""
        # Create user
        user_data = UserCreate(
            email="tokeninfo@example.com",
            password="SecurePass123!",
            full_name="Token Info User",
            city="Columbus",
        )

        with patch('app.services.auth_service.AuthService.request_email_verification'):
            user = AuthService.create_user(db_session, user_data)

        with patch('app.core.security.create_access_token') as mock_create_token:
            mock_create_token.return_value = "mocked_token"
            token = AuthService.generate_access_token(user)

            # Verify create_access_token was called with user info
            mock_create_token.assert_called_once()
            call_args = mock_create_token.call_args[0][0]
            assert "sub" in call_args or "email" in call_args


# Mock functions for services that may not be fully implemented
def mock_request_email_verification(db, user):
    """Mock email verification request."""
    pass


def mock_track_login(db, user_id):
    """Mock login tracking."""
    pass
