"""
Pytest configuration and fixtures for CivicQ backend tests.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models.base import Base
from app.core.database import get_db


# Test database URL (in-memory SQLite for fast tests)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a FastAPI test client with database override."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "city": "San Francisco",
        "role": "voter",
    }


@pytest.fixture
def sample_candidate_data():
    """Sample candidate data for testing."""
    return {
        "name": "Jane Candidate",
        "email": "jane@example.com",
        "race": "Mayor",
        "party": "Independent",
        "filing_id": "CAND-2024-001",
    }


@pytest.fixture
def sample_question_data():
    """Sample question data for testing."""
    return {
        "text": "What is your plan for affordable housing?",
        "issue_tags": ["housing", "economy"],
        "contest_id": 1,
    }


@pytest.fixture
def sample_ballot_data():
    """Sample ballot data for testing."""
    return {
        "city": "San Francisco",
        "election_date": "2024-11-05",
        "contests": [
            {
                "title": "Mayor",
                "type": "race",
                "candidates": ["Candidate A", "Candidate B"],
            },
            {
                "title": "Proposition A",
                "type": "measure",
                "description": "Housing Bond",
            },
        ],
    }


@pytest.fixture
def authenticated_user(client, sample_user_data):
    """Create and authenticate a test user."""
    # Register user
    response = client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code == 201

    user_data = response.json()

    # Login and get token
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": sample_user_data["email"],
            "password": "test_password",
        },
    )
    assert response.status_code == 200

    token_data = response.json()

    return {
        "user": user_data,
        "token": token_data["access_token"],
        "headers": {"Authorization": f"Bearer {token_data['access_token']}"},
    }


@pytest.fixture
def authenticated_candidate(client, sample_candidate_data):
    """Create and authenticate a test candidate."""
    # Register candidate
    response = client.post("/api/v1/auth/register", json=sample_candidate_data)
    assert response.status_code == 201

    candidate_data = response.json()

    # Login and get token
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": sample_candidate_data["email"],
            "password": "test_password",
        },
    )
    assert response.status_code == 200

    token_data = response.json()

    return {
        "candidate": candidate_data,
        "token": token_data["access_token"],
        "headers": {"Authorization": f"Bearer {token_data['access_token']}"},
    }


@pytest.fixture
def mock_redis(monkeypatch):
    """Mock Redis for testing."""

    class MockRedis:
        def __init__(self):
            self.data = {}

        def get(self, key):
            return self.data.get(key)

        def set(self, key, value, ex=None):
            self.data[key] = value

        def delete(self, key):
            if key in self.data:
                del self.data[key]

        def flushdb(self):
            self.data.clear()

    mock_redis_instance = MockRedis()
    monkeypatch.setattr("app.core.cache.redis_client", mock_redis_instance)
    return mock_redis_instance
