"""
Tests for Ballot Data Import System

Tests the ballot import service, API clients, and data normalization.
"""

import pytest
from datetime import date
from unittest.mock import Mock, patch, AsyncMock
from app.services.ballot_data_service import BallotDataService
from app.services.ballot_data_clients import (
    GoogleCivicClient,
    BallotpediaClient,
    VoteAmericaClient,
)
from app.schemas.ballot_import import (
    ImportedBallot,
    ImportedContest,
    ImportedCandidate,
    ImportedMeasure,
    ImportSource,
    BallotImportRequest,
)
from app.models.ballot import Ballot, Contest, Candidate, ContestType


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def sample_imported_ballot():
    """Sample imported ballot data"""
    return ImportedBallot(
        city_id="los-angeles-ca",
        city_name="Los Angeles",
        state="CA",
        election_date=date(2024, 11, 5),
        election_name="November 2024 General Election",
        source=ImportSource.GOOGLE_CIVIC,
        sources=[ImportSource.GOOGLE_CIVIC],
        contests=[
            ImportedContest(
                title="Mayor",
                jurisdiction="City of Los Angeles",
                office="Mayor",
                seat_count=1,
                contest_type=ContestType.RACE,
                candidates=[
                    ImportedCandidate(
                        name="John Smith",
                        email="john@example.com",
                        party="Democratic",
                    ),
                    ImportedCandidate(
                        name="Jane Doe",
                        email="jane@example.com",
                        party="Republican",
                    ),
                ],
            ),
            ImportedContest(
                title="Proposition 1",
                jurisdiction="City of Los Angeles",
                contest_type=ContestType.MEASURE,
                candidates=[],
                measure=ImportedMeasure(
                    measure_number="Prop 1",
                    measure_text="Shall the city increase taxes?",
                    summary="This measure would increase taxes.",
                ),
            ),
        ],
        source_data={"source": "google_civic"},
    )


@pytest.fixture
def sample_google_civic_response():
    """Sample Google Civic API response"""
    return {
        "election": {
            "id": "9000",
            "name": "November 2024 General Election",
            "electionDay": "2024-11-05",
        },
        "normalizedInput": {
            "city": "Los Angeles",
            "state": "CA",
        },
        "contests": [
            {
                "office": "Mayor",
                "type": "General",
                "district": {"name": "City of Los Angeles"},
                "candidates": [
                    {
                        "name": "John Smith",
                        "party": "Democratic",
                        "email": "john@example.com",
                    },
                    {
                        "name": "Jane Doe",
                        "party": "Republican",
                        "email": "jane@example.com",
                    },
                ],
            },
            {
                "referendumTitle": "Proposition 1",
                "type": "Referendum",
                "district": {"name": "City of Los Angeles"},
                "referendumText": "Shall the city increase taxes?",
                "referendumSubtitle": "This measure would increase taxes.",
            },
        ],
    }


# ============================================================================
# Test Import Request Schema Validation
# ============================================================================

def test_ballot_import_request_validation():
    """Test BallotImportRequest validation"""

    # Valid request with city
    request = BallotImportRequest(
        city_name="Los Angeles",
        state="CA",
        election_date=date(2024, 11, 5),
    )
    request.validate_request()  # Should not raise

    # Valid request with address
    request = BallotImportRequest(
        address="123 Main St, Los Angeles, CA 90001",
    )
    request.validate_request()  # Should not raise

    # Invalid: both city and address
    request = BallotImportRequest(
        city_name="Los Angeles",
        state="CA",
        address="123 Main St",
    )
    with pytest.raises(ValueError, match="Provide either"):
        request.validate_request()

    # Invalid: neither city nor address
    request = BallotImportRequest()
    with pytest.raises(ValueError, match="must be provided"):
        request.validate_request()


# ============================================================================
# Test Data Normalization
# ============================================================================

def test_normalize_city_id():
    """Test city ID normalization"""
    ballot = ImportedBallot(
        city_id="Los Angeles-CA",
        city_name="Los Angeles",
        state="CA",
        election_date=date(2024, 11, 5),
        election_name="Test Election",
        source=ImportSource.GOOGLE_CIVIC,
    )

    assert ballot.city_id == "los angeles-ca"


def test_normalize_state():
    """Test state normalization"""
    ballot = ImportedBallot(
        city_id="test-ca",
        city_name="Test",
        state="ca",
        election_date=date(2024, 11, 5),
        election_name="Test Election",
        source=ImportSource.GOOGLE_CIVIC,
    )

    assert ballot.state == "CA"


def test_normalize_candidate_name():
    """Test candidate name normalization"""
    candidate = ImportedCandidate(
        name="  John Smith  ",
    )

    assert candidate.name == "John Smith"


def test_normalize_email():
    """Test email normalization"""
    candidate = ImportedCandidate(
        name="John Smith",
        email="  John@Example.COM  ",
    )

    assert candidate.email == "john@example.com"


# ============================================================================
# Test Google Civic Client
# ============================================================================

@pytest.mark.asyncio
async def test_google_civic_parse_voter_info(sample_google_civic_response):
    """Test parsing Google Civic API response"""
    client = GoogleCivicClient()

    ballot = client._parse_voter_info(sample_google_civic_response)

    assert ballot is not None
    assert ballot.city_name == "Los Angeles"
    assert ballot.state == "CA"
    assert len(ballot.contests) == 2

    # Check race
    race = ballot.contests[0]
    assert race.title == "Mayor"
    assert race.contest_type == ContestType.RACE
    assert len(race.candidates) == 2
    assert race.candidates[0].name == "John Smith"

    # Check measure
    measure = ballot.contests[1]
    assert measure.title == "Proposition 1"
    assert measure.contest_type == ContestType.MEASURE
    assert measure.measure is not None
    assert measure.measure.measure_number == "Proposition 1"


@pytest.mark.asyncio
@patch('httpx.AsyncClient.get')
async def test_google_civic_get_ballot_by_address(mock_get, sample_google_civic_response):
    """Test fetching ballot by address"""
    client = GoogleCivicClient()
    client.api_key = "test_key"

    # Mock election list response
    elections_response = Mock()
    elections_response.json.return_value = {
        "elections": [{"id": "9000", "electionDay": "2024-11-05"}]
    }
    elections_response.raise_for_status = Mock()

    # Mock voter info response
    voter_info_response = Mock()
    voter_info_response.json.return_value = sample_google_civic_response
    voter_info_response.raise_for_status = Mock()

    # Set up mock to return different responses
    mock_get.return_value.__aenter__.side_effect = [
        elections_response,
        voter_info_response,
    ]

    ballot = await client.get_ballot_by_address(
        "123 Main St, Los Angeles, CA 90001"
    )

    assert ballot is not None
    assert ballot.city_name == "Los Angeles"


# ============================================================================
# Test Ballot Data Service
# ============================================================================

@pytest.mark.asyncio
async def test_merge_ballot_data_single_source(sample_imported_ballot):
    """Test merging with single data source"""
    db = Mock()
    service = BallotDataService(db)

    merged = service._merge_ballot_data([sample_imported_ballot])

    assert merged == sample_imported_ballot


@pytest.mark.asyncio
async def test_merge_ballot_data_multiple_sources(sample_imported_ballot):
    """Test merging data from multiple sources"""
    db = Mock()
    service = BallotDataService(db)

    # Create a second ballot from Ballotpedia with additional data
    ballotpedia_ballot = ImportedBallot(
        city_id="los-angeles-ca",
        city_name="Los Angeles",
        state="CA",
        election_date=date(2024, 11, 5),
        election_name="November 2024 General Election",
        source=ImportSource.BALLOTPEDIA,
        sources=[ImportSource.BALLOTPEDIA],
        contests=[
            ImportedContest(
                title="Mayor",
                jurisdiction="City of Los Angeles",
                office="Mayor",
                seat_count=1,
                contest_type=ContestType.RACE,
                candidates=[
                    ImportedCandidate(
                        name="John Smith",
                        website="https://johnsmith.vote",  # Additional data
                        party="Democratic",
                    ),
                ],
            ),
        ],
        source_data={"source": "ballotpedia"},
    )

    merged = service._merge_ballot_data([sample_imported_ballot, ballotpedia_ballot])

    assert len(merged.contests) == 2  # Mayor + Prop 1
    assert len(merged.sources) == 2

    # Check that data was merged
    mayor_contest = next(c for c in merged.contests if c.title == "Mayor")
    john_smith = next(c for c in mayor_contest.candidates if c.name == "John Smith")

    assert john_smith.email == "john@example.com"  # From Google Civic
    assert john_smith.website == "https://johnsmith.vote"  # From Ballotpedia


@pytest.mark.asyncio
async def test_merge_contest_candidates():
    """Test merging candidates from two contests"""
    db = Mock()
    service = BallotDataService(db)

    primary = ImportedContest(
        title="Mayor",
        jurisdiction="Test",
        office="Mayor",
        contest_type=ContestType.RACE,
        candidates=[
            ImportedCandidate(name="John Smith", email="john@example.com"),
        ],
    )

    secondary = ImportedContest(
        title="Mayor",
        jurisdiction="Test",
        office="Mayor",
        contest_type=ContestType.RACE,
        candidates=[
            ImportedCandidate(name="John Smith", phone="+1-555-0123"),
            ImportedCandidate(name="Jane Doe", email="jane@example.com"),
        ],
    )

    service._merge_contest_candidates(primary, secondary)

    assert len(primary.candidates) == 2

    john = next(c for c in primary.candidates if c.name == "John Smith")
    assert john.email == "john@example.com"
    assert john.phone == "+1-555-0123"

    jane = next(c for c in primary.candidates if c.name == "Jane Doe")
    assert jane.email == "jane@example.com"


# ============================================================================
# Test Database Persistence
# ============================================================================

@pytest.mark.asyncio
async def test_create_ballot_from_imported_data(sample_imported_ballot):
    """Test creating database ballot from imported data"""
    # This is an integration test that requires a real database
    # Skip if no test database is configured
    pytest.skip("Integration test - requires database")


# ============================================================================
# Test API Integration (requires API keys)
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.skipif(
    not pytest.config.getoption("--real-apis", default=False),
    reason="Requires --real-apis flag and API keys"
)
async def test_real_google_civic_api():
    """Test real Google Civic API call (requires API key)"""
    client = GoogleCivicClient()

    if not client.api_key:
        pytest.skip("Google Civic API key not configured")

    ballot = await client.get_ballot_by_address(
        "1600 Pennsylvania Avenue NW, Washington, DC 20500"
    )

    # Basic validation
    if ballot:
        assert ballot.city_name
        assert ballot.state
        assert ballot.election_date


# ============================================================================
# Test Error Handling
# ============================================================================

@pytest.mark.asyncio
async def test_google_civic_no_api_key():
    """Test Google Civic client without API key"""
    client = GoogleCivicClient()
    client.api_key = None

    ballot = await client.get_ballot_by_address("123 Main St")

    assert ballot is None


@pytest.mark.asyncio
async def test_import_with_no_data():
    """Test import when no data is available"""
    db = Mock()
    service = BallotDataService(db)

    # Mock clients to return None
    service.google_civic.get_ballot_by_city = AsyncMock(return_value=None)
    service.ballotpedia.get_ballot_by_city = AsyncMock(return_value=None)
    service.vote_america.get_ballot_by_city = AsyncMock(return_value=None)

    with pytest.raises(ValueError, match="No ballot data found"):
        await service.import_ballot_by_city(
            city_name="Test City",
            state="CA",
            election_date=date(2024, 11, 5),
        )


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_addoption(parser):
    """Add command line options"""
    parser.addoption(
        "--real-apis",
        action="store_true",
        default=False,
        help="Run tests that call real APIs (requires API keys)",
    )
