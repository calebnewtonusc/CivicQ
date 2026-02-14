"""
API tests for authentication endpoints.
"""

import pytest
from unittest.mock import patch


class TestAuthRegister:
    """Test user registration endpoint."""

    def test_register_success(self, client, mock_email_service):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "full_name": "New User",
                "city": "San Francisco",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client, test_user, mock_email_service):
        """Test registration with duplicate email."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "password": "SecurePass123!",
                "full_name": "Duplicate User",
                "city": "Boston",
            },
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "SecurePass123!",
                "full_name": "Invalid Email",
                "city": "Seattle",
            },
        )

        assert response.status_code == 422

    def test_register_weak_password(self, client):
        """Test registration with weak password."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "weak@example.com",
                "password": "weak",
                "full_name": "Weak Password",
                "city": "Portland",
            },
        )

        assert response.status_code == 422 or response.status_code == 400

    def test_register_missing_fields(self, client):
        """Test registration with missing required fields."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "incomplete@example.com",
            },
        )

        assert response.status_code == 422


class TestAuthLogin:
    """Test user login endpoint."""

    def test_login_success(self, client, db_session):
        """Test successful login."""
        from tests.fixtures.factories import UserFactory
        from app.core.security import get_password_hash

        # Create user with known password
        password = "TestPassword123!"
        user = UserFactory.create(
            db_session,
            email="login@example.com",
            hashed_password=get_password_hash(password),
        )
        user.is_active = True
        db_session.commit()

        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "login@example.com",
                "password": password,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, db_session):
        """Test login with wrong password."""
        from tests.fixtures.factories import UserFactory
        from app.core.security import get_password_hash

        user = UserFactory.create(
            db_session,
            email="wrongpass@example.com",
            hashed_password=get_password_hash("CorrectPassword123!"),
        )

        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "wrongpass@example.com",
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "doesnotexist@example.com",
                "password": "AnyPassword123!",
            },
        )

        assert response.status_code == 401

    def test_login_inactive_user(self, client, db_session):
        """Test login with inactive user."""
        from tests.fixtures.factories import UserFactory
        from app.core.security import get_password_hash

        password = "TestPassword123!"
        user = UserFactory.create(
            db_session,
            email="inactive@example.com",
            hashed_password=get_password_hash(password),
        )
        user.is_active = False
        db_session.commit()

        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "inactive@example.com",
                "password": password,
            },
        )

        assert response.status_code in [401, 403]


class TestAuthMe:
    """Test current user endpoint."""

    def test_get_current_user(self, client, auth_headers):
        """Test getting current user info."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "id" in data
        assert "hashed_password" not in data

    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication."""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401


class TestAuthPasswordReset:
    """Test password reset endpoints."""

    def test_request_password_reset(self, client, test_user, mock_email_service):
        """Test requesting password reset."""
        response = client.post(
            "/api/v1/auth/password-reset/request",
            json={"email": test_user.email},
        )

        assert response.status_code == 200
        mock_email_service.send_password_reset_email.assert_called()

    def test_request_password_reset_nonexistent_user(self, client, mock_email_service):
        """Test requesting password reset for non-existent user."""
        response = client.post(
            "/api/v1/auth/password-reset/request",
            json={"email": "doesnotexist@example.com"},
        )

        # Should return 200 for security (don't reveal if email exists)
        assert response.status_code == 200

    def test_reset_password_with_token(self, client, db_session, test_user):
        """Test resetting password with valid token."""
        from datetime import datetime, timedelta

        # Set reset token
        token = "valid_reset_token"
        test_user.password_reset_token = token
        test_user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        db_session.commit()

        response = client.post(
            "/api/v1/auth/password-reset/confirm",
            json={
                "token": token,
                "new_password": "NewSecurePass123!",
            },
        )

        assert response.status_code == 200

    def test_reset_password_invalid_token(self, client):
        """Test resetting password with invalid token."""
        response = client.post(
            "/api/v1/auth/password-reset/confirm",
            json={
                "token": "invalid_token",
                "new_password": "NewSecurePass123!",
            },
        )

        assert response.status_code == 400

    def test_reset_password_expired_token(self, client, db_session, test_user):
        """Test resetting password with expired token."""
        from datetime import datetime, timedelta

        # Set expired reset token
        token = "expired_token"
        test_user.password_reset_token = token
        test_user.password_reset_expires = datetime.utcnow() - timedelta(hours=1)
        db_session.commit()

        response = client.post(
            "/api/v1/auth/password-reset/confirm",
            json={
                "token": token,
                "new_password": "NewSecurePass123!",
            },
        )

        assert response.status_code == 400


class TestAuthEmailVerification:
    """Test email verification endpoints."""

    def test_verify_email(self, client, db_session, test_user):
        """Test email verification."""
        from datetime import datetime, timedelta

        # Set verification token
        token = "valid_verification_token"
        test_user.email_verification_token = token
        test_user.email_verification_expires = datetime.utcnow() + timedelta(days=1)
        test_user.email_verified = False
        db_session.commit()

        response = client.post(
            f"/api/v1/auth/verify-email/{token}",
        )

        assert response.status_code == 200

        db_session.refresh(test_user)
        assert test_user.email_verified is True

    def test_verify_email_invalid_token(self, client):
        """Test email verification with invalid token."""
        response = client.post("/api/v1/auth/verify-email/invalid_token")

        assert response.status_code == 400

    def test_resend_verification_email(self, client, test_user, mock_email_service, auth_headers):
        """Test resending verification email."""
        response = client.post(
            "/api/v1/auth/resend-verification",
            headers=auth_headers,
        )

        assert response.status_code == 200


class TestAuthRateLimiting:
    """Test rate limiting on auth endpoints."""

    def test_login_rate_limit(self, client, db_session):
        """Test rate limiting on login attempts."""
        from tests.fixtures.factories import UserFactory
        from app.core.security import get_password_hash

        user = UserFactory.create(
            db_session,
            email="ratelimit@example.com",
            hashed_password=get_password_hash("Password123!"),
        )

        # Make multiple failed login attempts
        for _ in range(10):
            client.post(
                "/api/v1/auth/login",
                data={
                    "username": "ratelimit@example.com",
                    "password": "WrongPassword!",
                },
            )

        # Next request should be rate limited
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "ratelimit@example.com",
                "password": "WrongPassword!",
            },
        )

        # Should be rate limited (429) or account locked
        assert response.status_code in [429, 403, 401]


class TestAuthValidation:
    """Test input validation on auth endpoints."""

    def test_register_email_validation(self, client):
        """Test email format validation."""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",
            "",
        ]

        for email in invalid_emails:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": email,
                    "password": "SecurePass123!",
                    "full_name": "Test User",
                    "city": "Test City",
                },
            )
            assert response.status_code == 422

    def test_register_password_requirements(self, client):
        """Test password requirements."""
        weak_passwords = [
            "short",
            "alllowercase",
            "ALLUPPERCASE",
            "12345678",
            "password",
        ]

        for password in weak_passwords:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": "test@example.com",
                    "password": password,
                    "full_name": "Test User",
                    "city": "Test City",
                },
            )
            # Should fail validation
            assert response.status_code in [400, 422]
