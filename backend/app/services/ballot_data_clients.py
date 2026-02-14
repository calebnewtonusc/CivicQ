"""
External API Clients for Ballot Data

Clients for:
- Google Civic Information API
- VoteAmerica API
- Ballotpedia API
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import date
import httpx
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


class GoogleCivicClient:
    """
    Client for Google Civic Information API

    Docs: https://developers.google.com/civic-information
    """

    BASE_URL = "https://www.googleapis.com/civicinfo/v2"

    def __init__(self):
        self.api_key = settings.GOOGLE_CIVIC_API_KEY
        if not self.api_key:
            logger.warning("Google Civic API key not configured")

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
        """
        if not self.api_key:
            logger.error("Google Civic API key not configured")
            return None

        try:
            async with httpx.AsyncClient() as client:
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
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()

                return self._parse_voter_info(data)

        except httpx.HTTPError as e:
            logger.error(f"Google Civic API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing Google Civic API response: {e}")
            return None

    async def _get_election_id(self, client: httpx.AsyncClient, target_date: Optional[date] = None) -> Optional[str]:
        """Get the election ID for the target date or next upcoming election"""
        try:
            response = await client.get(
                f"{self.BASE_URL}/elections",
                params={"key": self.api_key},
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

            elections = data.get("elections", [])
            if not elections:
                return None

            # If target date specified, find matching election
            if target_date:
                for election in elections:
                    election_date_str = election.get("electionDay")
                    if election_date_str:
                        election_date = date.fromisoformat(election_date_str)
                        if election_date == target_date:
                            return election.get("id")

            # Otherwise return next upcoming election
            return elections[0].get("id")

        except Exception as e:
            logger.error(f"Error fetching elections: {e}")
            return None

    def _parse_voter_info(self, data: Dict[str, Any]) -> Optional[ImportedBallot]:
        """Parse Google Civic API voter info response"""
        election = data.get("election", {})
        normalized_input = data.get("normalizedInput", {})

        # Extract city from address
        city = normalized_input.get("city", "")
        state = normalized_input.get("state", "")
        city_id = f"{city.lower().replace(' ', '-')}-{state.lower()}"

        # Parse election date
        election_date_str = election.get("electionDay")
        if not election_date_str:
            logger.error("No election date in response")
            return None

        election_date = date.fromisoformat(election_date_str)

        # Parse contests
        contests = []
        for contest_data in data.get("contests", []):
            contest = self._parse_contest(contest_data)
            if contest:
                contests.append(contest)

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
            },
        )

    def _parse_contest(self, contest_data: Dict[str, Any]) -> Optional[ImportedContest]:
        """Parse a single contest from Google Civic API"""
        contest_type_str = contest_data.get("type", "General")

        # Determine if it's a race or measure
        # Google uses 'Referendum' type for measures
        is_measure = contest_type_str == "Referendum"

        candidates = []
        measure = None

        if is_measure:
            # Parse as ballot measure
            measure = ImportedMeasure(
                measure_number=contest_data.get("referendumTitle", ""),
                measure_text=contest_data.get("referendumText", ""),
                summary=contest_data.get("referendumSubtitle", ""),
                fiscal_notes=None,
                pro_statement=None,
                con_statement=None,
            )
        else:
            # Parse candidates
            for candidate_data in contest_data.get("candidates", []):
                candidate = self._parse_candidate(candidate_data)
                if candidate:
                    candidates.append(candidate)

        return ImportedContest(
            title=contest_data.get("office", contest_data.get("referendumTitle", "")),
            jurisdiction=contest_data.get("district", {}).get("name", ""),
            office=contest_data.get("office") if not is_measure else None,
            seat_count=contest_data.get("numberElected", 1),
            description=None,
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
