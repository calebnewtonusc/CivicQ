"""
External API Clients for Ballot Data

Clients for:
- Google Civic Information API
- VoteAmerica API
- Ballotpedia API

Features:
- Retry logic with exponential backoff
- Rate limiting compliance
- Comprehensive error handling
- Response validation
- Data normalization
"""

import logging
import asyncio
from typing import Optional, List, Dict, Any, Callable
from datetime import date, datetime
import httpx
from functools import wraps
from app.core.config import settings
from app.schemas.ballot_import import (
    ImportedBallot,
    ImportedContest,
    ImportedCandidate,
    ImportedMeasure,
    ImportSource,
)
from app.models.ballot import ContestType

logger = logging.getLogger(__name__)


class APIClientError(Exception):
    """Base exception for API client errors"""
    pass


class RateLimitError(APIClientError):
    """Raised when API rate limit is exceeded"""
    pass


class ValidationError(APIClientError):
    """Raised when API response validation fails"""
    pass


def retry_with_backoff(max_retries: int = 3, initial_delay: float = 1.0):
    """
    Decorator for retrying functions with exponential backoff

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except httpx.HTTPStatusError as e:
                    last_exception = e

                    # Don't retry client errors (4xx) except rate limits
                    if 400 <= e.response.status_code < 500:
                        if e.response.status_code == 429:  # Rate limit
                            logger.warning(f"Rate limited on {func.__name__}, retrying in {delay}s")
                        else:
                            raise  # Don't retry other 4xx errors

                    # Retry server errors (5xx) and rate limits
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay}s..."
                        )
                        await asyncio.sleep(delay)
                        delay *= 2  # Exponential backoff
                    else:
                        logger.error(f"All {max_retries} retries failed for {func.__name__}")
                        raise

                except (httpx.RequestError, httpx.TimeoutException) as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Network error on attempt {attempt + 1}/{max_retries} for {func.__name__}: {e}. "
                            f"Retrying in {delay}s..."
                        )
                        await asyncio.sleep(delay)
                        delay *= 2
                    else:
                        logger.error(f"All {max_retries} retries failed for {func.__name__}")
                        raise APIClientError(f"Network error after {max_retries} retries: {e}")

            if last_exception:
                raise last_exception

        return wrapper
    return decorator


class GoogleCivicClient:
    """
    Client for Google Civic Information API

    Docs: https://developers.google.com/civic-information

    Features:
    - Automatic retry with exponential backoff
    - Rate limit handling
    - Comprehensive error handling
    - Response validation
    - Multiple election support
    """

    BASE_URL = "https://www.googleapis.com/civicinfo/v2"
    RATE_LIMIT_DELAY = 0.1  # 100ms between requests to avoid rate limits

    def __init__(self):
        self.api_key = settings.GOOGLE_CIVIC_API_KEY
        if not self.api_key:
            logger.warning("Google Civic API key not configured")
        self._last_request_time = 0.0

    async def _rate_limit(self):
        """Enforce rate limiting between requests"""
        import time
        now = time.time()
        time_since_last = now - self._last_request_time
        if time_since_last < self.RATE_LIMIT_DELAY:
            await asyncio.sleep(self.RATE_LIMIT_DELAY - time_since_last)
        self._last_request_time = time.time()

    @retry_with_backoff(max_retries=3, initial_delay=1.0)
    async def get_ballot_by_address(
        self,
        address: str,
        election_date: Optional[date] = None,
    ) -> Optional[ImportedBallot]:
        """
        Fetch ballot information for a specific address

        Args:
            address: Full address (street, city, state, zip)
            election_date: Target election date (optional)

        Returns:
            ImportedBallot or None

        Raises:
            APIClientError: On unrecoverable API errors
        """
        if not self.api_key:
            raise APIClientError("Google Civic API key not configured")

        await self._rate_limit()

        async with httpx.AsyncClient(timeout=30.0) as client:
            # First, get election ID
            election_id = await self._get_election_id(client, election_date)
            if not election_id:
                logger.warning("No upcoming election found")
                return None

            # Get voter info for this address
            params = {
                "key": self.api_key,
                "address": address,
                "electionId": election_id,
            }

            response = await client.get(
                f"{self.BASE_URL}/voterinfo",
                params=params,
            )
            response.raise_for_status()
            data = response.json()

            # Validate response structure
            if not self._validate_voter_info_response(data):
                raise ValidationError("Invalid voter info response structure")

            return self._parse_voter_info(data)

    async def get_all_elections(self) -> List[Dict[str, Any]]:
        """
        Get all available elections from Google Civic API

        Returns:
            List of election dictionaries
        """
        if not self.api_key:
            raise APIClientError("Google Civic API key not configured")

        await self._rate_limit()

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/elections",
                params={"key": self.api_key},
            )
            response.raise_for_status()
            data = response.json()

            return data.get("elections", [])

    @retry_with_backoff(max_retries=2, initial_delay=0.5)
    async def _get_election_id(self, client: httpx.AsyncClient, target_date: Optional[date] = None) -> Optional[str]:
        """
        Get the election ID for the target date or next upcoming election

        Args:
            client: HTTP client
            target_date: Target election date (optional)

        Returns:
            Election ID string or None
        """
        await self._rate_limit()

        response = await client.get(
            f"{self.BASE_URL}/elections",
            params={"key": self.api_key},
        )
        response.raise_for_status()
        data = response.json()

        elections = data.get("elections", [])
        if not elections:
            logger.warning("No elections found in Google Civic API")
            return None

        # If target date specified, find matching election
        if target_date:
            for election in elections:
                election_date_str = election.get("electionDay")
                if election_date_str:
                    try:
                        election_date = date.fromisoformat(election_date_str)
                        if election_date == target_date:
                            logger.info(f"Found election: {election.get('name')} on {election_date}")
                            return election.get("id")
                    except ValueError:
                        logger.warning(f"Invalid election date format: {election_date_str}")
                        continue

            logger.warning(f"No election found for target date: {target_date}")
            return None

        # Otherwise return next upcoming election
        logger.info(f"Using next upcoming election: {elections[0].get('name')}")
        return elections[0].get("id")

    def _validate_voter_info_response(self, data: Dict[str, Any]) -> bool:
        """
        Validate Google Civic API voter info response structure

        Args:
            data: API response data

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(data, dict):
            logger.error("Response is not a dictionary")
            return False

        if "election" not in data:
            logger.error("Missing 'election' field in response")
            return False

        election = data.get("election", {})
        if not election.get("electionDay"):
            logger.error("Missing 'electionDay' in election data")
            return False

        # Contests are optional (some addresses may not have contests)
        if "contests" in data:
            contests = data.get("contests", [])
            if not isinstance(contests, list):
                logger.error("'contests' field is not a list")
                return False

        return True

    def _parse_voter_info(self, data: Dict[str, Any]) -> Optional[ImportedBallot]:
        """
        Parse Google Civic API voter info response

        Args:
            data: API response data

        Returns:
            ImportedBallot or None
        """
        election = data.get("election", {})
        normalized_input = data.get("normalizedInput", {})

        # Extract city from address
        city = normalized_input.get("city", "")
        state = normalized_input.get("state", "")

        # Handle missing city/state
        if not city or not state:
            logger.warning("Missing city or state in normalized input")
            # Try to extract from polling locations
            polling_locations = data.get("pollingLocations", [])
            if polling_locations:
                location = polling_locations[0].get("address", {})
                city = city or location.get("city", "")
                state = state or location.get("state", "")

        if not city or not state:
            logger.error("Cannot determine city/state from response")
            return None

        city_id = f"{city.lower().replace(' ', '-')}-{state.lower()}"

        # Parse election date
        election_date_str = election.get("electionDay")
        if not election_date_str:
            logger.error("No election date in response")
            return None

        try:
            election_date = date.fromisoformat(election_date_str)
        except ValueError as e:
            logger.error(f"Invalid election date format: {election_date_str}: {e}")
            return None

        # Parse contests
        contests = []
        for idx, contest_data in enumerate(data.get("contests", [])):
            try:
                contest = self._parse_contest(contest_data)
                if contest:
                    contests.append(contest)
                else:
                    logger.warning(f"Skipped contest {idx}: failed to parse")
            except Exception as e:
                logger.error(f"Error parsing contest {idx}: {e}", exc_info=True)
                continue

        if not contests:
            logger.warning("No contests parsed from response")

        return ImportedBallot(
            city_id=city_id,
            city_name=city,
            state=state,
            election_date=election_date,
            election_name=election.get("name", ""),
            source=ImportSource.GOOGLE_CIVIC,
            sources=[ImportSource.GOOGLE_CIVIC],
            contests=contests,
            source_data={
                "source": "google_civic",
                "election_id": election.get("id"),
                "api_version": "v2",
                "normalized_address": {
                    "line1": normalized_input.get("line1"),
                    "city": city,
                    "state": state,
                    "zip": normalized_input.get("zip"),
                },
                "polling_locations_count": len(data.get("pollingLocations", [])),
                "contests_count": len(contests),
            },
        )

    def _parse_contest(self, contest_data: Dict[str, Any]) -> Optional[ImportedContest]:
        """
        Parse a single contest from Google Civic API

        Args:
            contest_data: Contest data from API

        Returns:
            ImportedContest or None
        """
        if not contest_data:
            return None

        contest_type_str = contest_data.get("type", "General")

        # Determine if it's a race or measure
        # Google uses 'Referendum' type for measures
        is_measure = contest_type_str == "Referendum"

        candidates = []
        measure = None

        if is_measure:
            # Parse as ballot measure
            measure_title = contest_data.get("referendumTitle", "")
            measure_text = contest_data.get("referendumText", "")

            if not measure_text:
                logger.warning(f"Measure '{measure_title}' has no text, skipping")
                return None

            measure = ImportedMeasure(
                measure_number=measure_title,
                measure_text=measure_text,
                summary=contest_data.get("referendumSubtitle", ""),
                fiscal_notes=contest_data.get("referendumBrief"),
                pro_statement=contest_data.get("referendumProStatement"),
                con_statement=contest_data.get("referendumConStatement"),
            )
        else:
            # Parse candidates
            candidate_list = contest_data.get("candidates", [])
            if not candidate_list:
                logger.warning(f"Race '{contest_data.get('office')}' has no candidates, skipping")
                return None

            for candidate_data in candidate_list:
                try:
                    candidate = self._parse_candidate(candidate_data)
                    if candidate:
                        candidates.append(candidate)
                except Exception as e:
                    logger.error(f"Error parsing candidate: {e}", exc_info=True)
                    continue

        # Extract district/jurisdiction info
        district = contest_data.get("district", {})
        jurisdiction = district.get("name", "") if isinstance(district, dict) else ""

        # Get contest title
        if is_measure:
            title = contest_data.get("referendumTitle", "Unknown Measure")
        else:
            title = contest_data.get("office", "Unknown Office")

        return ImportedContest(
            title=title,
            jurisdiction=jurisdiction,
            office=contest_data.get("office") if not is_measure else None,
            seat_count=contest_data.get("numberElected", 1),
            description=contest_data.get("referendumBrief") if is_measure else None,
            contest_type=ContestType.MEASURE if is_measure else ContestType.RACE,
            candidates=candidates,
            measure=measure,
        )

    def _parse_candidate(self, candidate_data: Dict[str, Any]) -> ImportedCandidate:
        """Parse a single candidate from Google Civic API"""
        # Extract contact info
        channels = candidate_data.get("channels", [])
        website = None
        for channel in channels:
            if channel.get("type") == "Website":
                website = channel.get("id")
                break

        return ImportedCandidate(
            name=candidate_data.get("name", ""),
            filing_id=None,
            email=candidate_data.get("email"),
            phone=candidate_data.get("phone"),
            website=website,
            photo_url=candidate_data.get("photoUrl"),
            party=candidate_data.get("party"),
            profile_fields={
                "party": candidate_data.get("party"),
                "candidateUrl": candidate_data.get("candidateUrl"),
            },
        )


class VoteAmericaClient:
    """
    Client for VoteAmerica API

    Docs: https://www.voteamerica.com/api/
    """

    BASE_URL = "https://api.voteamerica.com/v1"

    def __init__(self):
        self.api_key = settings.VOTE_AMERICA_API_KEY
        if not self.api_key:
            logger.warning("VoteAmerica API key not configured")

    async def get_ballot_by_address(
        self,
        address: str,
        election_date: Optional[date] = None,
    ) -> Optional[ImportedBallot]:
        """
        Fetch ballot information for a specific address

        Args:
            address: Full address
            election_date: Target election date

        Returns:
            ImportedBallot or None
        """
        if not self.api_key:
            logger.error("VoteAmerica API key not configured")
            return None

        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self.api_key}"}

                response = await client.get(
                    f"{self.BASE_URL}/ballot",
                    params={"address": address},
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                return self._parse_ballot_data(data)

        except httpx.HTTPError as e:
            logger.error(f"VoteAmerica API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing VoteAmerica API response: {e}")
            return None

    async def get_ballot_by_city(
        self,
        city_name: str,
        state: str,
        election_date: date,
    ) -> Optional[ImportedBallot]:
        """Get ballot by city (VoteAmerica may not support this directly)"""
        logger.warning("VoteAmerica API may not support city-wide queries")
        # Use a sample address in the city center
        address = f"{city_name}, {state}"
        return await self.get_ballot_by_address(address, election_date)

    def _parse_ballot_data(self, data: Dict[str, Any]) -> Optional[ImportedBallot]:
        """Parse VoteAmerica ballot data"""
        # Note: Actual implementation depends on VoteAmerica API structure
        # This is a placeholder - adjust based on actual API response
        contests = []

        for contest_data in data.get("contests", []):
            contest = ImportedContest(
                title=contest_data.get("title", ""),
                jurisdiction=contest_data.get("jurisdiction", ""),
                office=contest_data.get("office"),
                seat_count=contest_data.get("seats", 1),
                description=contest_data.get("description"),
                contest_type=ContestType.RACE,  # Determine based on contest type
                candidates=[
                    ImportedCandidate(
                        name=c.get("name", ""),
                        filing_id=c.get("id"),
                        email=c.get("email"),
                        phone=c.get("phone"),
                        party=c.get("party"),
                        website=c.get("website"),
                    )
                    for c in contest_data.get("candidates", [])
                ],
            )
            contests.append(contest)

        return ImportedBallot(
            city_id=data.get("city_id", ""),
            city_name=data.get("city", ""),
            state=data.get("state", ""),
            election_date=date.fromisoformat(data.get("election_date", "")),
            election_name=data.get("election_name", ""),
            source=ImportSource.VOTE_AMERICA,
            sources=[ImportSource.VOTE_AMERICA],
            contests=contests,
            source_data={
                "source": "vote_america",
            },
        )


class BallotpediaClient:
    """
    Client for Ballotpedia API

    Docs: https://ballotpedia.org/API-documentation
    """

    BASE_URL = "https://ballotpedia.org/api/v4"

    def __init__(self):
        self.api_key = settings.BALLOTPEDIA_API_KEY
        if not self.api_key:
            logger.warning("Ballotpedia API key not configured")

    async def get_ballot_by_address(
        self,
        address: str,
        election_date: Optional[date] = None,
    ) -> Optional[ImportedBallot]:
        """
        Fetch ballot information for a specific address

        Args:
            address: Full address
            election_date: Target election date

        Returns:
            ImportedBallot or None
        """
        if not self.api_key:
            logger.error("Ballotpedia API key not configured")
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/ballot",
                    params={
                        "access_token": self.api_key,
                        "address": address,
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                return self._parse_ballot_data(data)

        except httpx.HTTPError as e:
            logger.error(f"Ballotpedia API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing Ballotpedia API response: {e}")
            return None

    async def get_ballot_by_city(
        self,
        city_name: str,
        state: str,
        election_date: date,
    ) -> Optional[ImportedBallot]:
        """
        Fetch ballot information for an entire city

        Args:
            city_name: City name
            state: State abbreviation
            election_date: Election date

        Returns:
            ImportedBallot or None
        """
        if not self.api_key:
            logger.error("Ballotpedia API key not configured")
            return None

        try:
            async with httpx.AsyncClient() as client:
                # Get elections for this city
                response = await client.get(
                    f"{self.BASE_URL}/elections",
                    params={
                        "access_token": self.api_key,
                        "city": city_name,
                        "state": state,
                        "date": election_date.isoformat(),
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                return self._parse_ballot_data(data, city_name, state)

        except httpx.HTTPError as e:
            logger.error(f"Ballotpedia API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing Ballotpedia API response: {e}")
            return None

    def _parse_ballot_data(
        self,
        data: Dict[str, Any],
        city_name: Optional[str] = None,
        state: Optional[str] = None,
    ) -> Optional[ImportedBallot]:
        """Parse Ballotpedia ballot data"""
        # Extract location info
        if not city_name:
            city_name = data.get("city", "")
        if not state:
            state = data.get("state", "")

        city_id = f"{city_name.lower().replace(' ', '-')}-{state.lower()}"

        # Parse election date
        election_date_str = data.get("election_date")
        if election_date_str:
            election_date = date.fromisoformat(election_date_str)
        else:
            logger.error("No election date in Ballotpedia response")
            return None

        # Parse contests
        contests = []
        for contest_data in data.get("races", []):
            contest = self._parse_race(contest_data)
            if contest:
                contests.append(contest)

        for measure_data in data.get("measures", []):
            contest = self._parse_measure(measure_data)
            if contest:
                contests.append(contest)

        return ImportedBallot(
            city_id=city_id,
            city_name=city_name,
            state=state,
            election_date=election_date,
            election_name=data.get("election_name", ""),
            source=ImportSource.BALLOTPEDIA,
            sources=[ImportSource.BALLOTPEDIA],
            contests=contests,
            source_data={
                "source": "ballotpedia",
                "election_id": data.get("election_id"),
            },
        )

    def _parse_race(self, race_data: Dict[str, Any]) -> ImportedContest:
        """Parse a race from Ballotpedia"""
        candidates = []
        for candidate_data in race_data.get("candidates", []):
            candidates.append(
                ImportedCandidate(
                    name=candidate_data.get("name", ""),
                    filing_id=candidate_data.get("candidate_id"),
                    email=candidate_data.get("email"),
                    phone=candidate_data.get("phone"),
                    website=candidate_data.get("website"),
                    photo_url=candidate_data.get("photo_url"),
                    party=candidate_data.get("party"),
                    profile_fields={
                        "party": candidate_data.get("party"),
                        "incumbent": candidate_data.get("incumbent", False),
                        "bio": candidate_data.get("bio"),
                        "occupation": candidate_data.get("occupation"),
                        "education": candidate_data.get("education"),
                    },
                )
            )

        return ImportedContest(
            title=race_data.get("title", ""),
            jurisdiction=race_data.get("jurisdiction", ""),
            office=race_data.get("office"),
            seat_count=race_data.get("seats", 1),
            description=race_data.get("description"),
            contest_type=ContestType.RACE,
            candidates=candidates,
        )

    def _parse_measure(self, measure_data: Dict[str, Any]) -> ImportedContest:
        """Parse a ballot measure from Ballotpedia"""
        measure = ImportedMeasure(
            measure_number=measure_data.get("measure_number", ""),
            measure_text=measure_data.get("text", ""),
            summary=measure_data.get("summary"),
            fiscal_notes=measure_data.get("fiscal_impact"),
            pro_statement=measure_data.get("support_statement"),
            con_statement=measure_data.get("opposition_statement"),
        )

        return ImportedContest(
            title=measure_data.get("title", ""),
            jurisdiction=measure_data.get("jurisdiction", ""),
            office=None,
            seat_count=None,
            description=measure_data.get("description"),
            contest_type=ContestType.MEASURE,
            candidates=[],
            measure=measure,
        )
