"""
Pytest configuration and fixtures for CivicQ backend tests.
"""

import pytest
import os
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models.base import Base
from app.core.database import get_db

# Import factories for easy access in tests
from tests.fixtures.factories import (
    UserFactory,
    CityFactory,
    QuestionFactory,
    ContestFactory,
    CandidateFactory,
    VoteFactory,
    VideoFactory,
    ScenarioBuilder,
)


# Test database URL (in-memory SQLite for fast tests)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# For integration tests, optionally use PostgreSQL
if os.getenv("USE_TEST_POSTGRES"):
    SQLALCHEMY_TEST_DATABASE_URL = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://civicq_test:test@localhost/civicq_test"
    )
    engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
else:
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
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

        def exists(self, key):
            return key in self.data

        def expire(self, key, seconds):
            return True

        def incr(self, key):
            self.data[key] = self.data.get(key, 0) + 1
            return self.data[key]

    mock_redis_instance = MockRedis()
    monkeypatch.setattr("app.core.cache.redis_client", mock_redis_instance)
    return mock_redis_instance


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    return UserFactory.create_voter(db_session)


@pytest.fixture
def test_admin(db_session):
    """Create a test admin user."""
    return UserFactory.create_admin(db_session)


@pytest.fixture
def test_candidate(db_session):
    """Create a test candidate user."""
    return UserFactory.create_candidate(db_session)


@pytest.fixture
def test_city(db_session):
    """Create a test city."""
    return CityFactory.create(db_session)


@pytest.fixture
def test_contest(db_session, test_city):
    """Create a test contest."""
    return ContestFactory.create(db_session, city_id=test_city.slug)


@pytest.fixture
def auth_headers(client, test_user):
    """Generate authentication headers for test user."""
    from app.core.security import create_access_token

    token = create_access_token({"sub": str(test_user.id), "email": test_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, test_admin):
    """Generate authentication headers for admin user."""
    from app.core.security import create_access_token

    token = create_access_token({"sub": str(test_admin.id), "email": test_admin.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_email_service(monkeypatch):
    """Mock email service for testing."""
    from unittest.mock import MagicMock

    mock_service = MagicMock()
    monkeypatch.setattr("app.services.email_service.email_service", mock_service)
    return mock_service


@pytest.fixture
def mock_storage_service(monkeypatch):
    """Mock storage service for testing."""
    from unittest.mock import MagicMock

    mock_service = MagicMock()
    mock_service.upload_file.return_value = "https://storage.example.com/test.jpg"
    monkeypatch.setattr("app.services.storage_service.storage_service", mock_service)
    return mock_service


@pytest.fixture
def mock_video_service(monkeypatch):
    """Mock video processing service for testing."""
    from unittest.mock import MagicMock

    mock_service = MagicMock()
    monkeypatch.setattr("app.services.video_processing_service.video_service", mock_service)
    return mock_service


@pytest.fixture
def mock_ballot_api(monkeypatch):
    """Mock ballot API client for testing."""
    from unittest.mock import MagicMock

    mock_client = MagicMock()
    mock_client.get_ballot_data.return_value = {
        "contests": [
            {
                "title": "Mayor",
                "type": "race",
                "candidates": ["Alice Smith", "Bob Johnson"]
            }
        ]
    }
    monkeypatch.setattr("app.services.ballot_data_service.ballot_client", mock_client)
    return mock_client
