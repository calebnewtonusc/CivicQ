"""
Unit tests for authentication endpoints.
"""

import pytest
from fastapi import status


class TestUserRegistration:
    """Tests for user registration."""

    def test_register_new_user(self, client, sample_user_data):
        """Test successful user registration."""
        response = client.post("/api/v1/auth/register", json=sample_user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == sample_user_data["email"]
        assert data["name"] == sample_user_data["name"]
        assert "id" in data
        assert "password" not in data  # Password should not be returned

    def test_register_duplicate_email(self, client, sample_user_data):
        """Test registration with duplicate email."""
        # Register first user
        client.post("/api/v1/auth/register", json=sample_user_data)

        # Try to register again with same email
        response = client.post("/api/v1/auth/register", json=sample_user_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client, sample_user_data):
        """Test registration with invalid email format."""
        sample_user_data["email"] = "invalid-email"
        response = client.post("/api/v1/auth/register", json=sample_user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_missing_required_fields(self, client):
        """Test registration with missing required fields."""
        incomplete_data = {"email": "test@example.com"}
        response = client.post("/api/v1/auth/register", json=incomplete_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserLogin:
    """Tests for user login."""

    def test_login_success(self, client, sample_user_data):
        """Test successful login."""
        # Register user first
        client.post("/api/v1/auth/register", json=sample_user_data)

        # Login
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": sample_user_data["email"],
                "password": "test_password",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client, sample_user_data):
        """Test login with invalid credentials."""
        # Register user first
        client.post("/api/v1/auth/register", json=sample_user_data)

        # Login with wrong password
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": sample_user_data["email"],
                "password": "wrong_password",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "password",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestUserProfile:
    """Tests for user profile endpoints."""

    def test_get_current_user(self, client, authenticated_user):
        """Test getting current user profile."""
        response = client.get(
            "/api/v1/users/me", headers=authenticated_user["headers"]
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == authenticated_user["user"]["email"]

    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication."""
        response = client.get("/api/v1/users/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_user_profile(self, client, authenticated_user):
        """Test updating user profile."""
        updated_data = {"name": "Updated Name"}
        response = client.patch(
            "/api/v1/users/me",
            json=updated_data,
            headers=authenticated_user["headers"],
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"
