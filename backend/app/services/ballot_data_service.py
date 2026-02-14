"""
Ballot Data Service

Fetches and normalizes ballot data from multiple external APIs:
- Google Civic Information API
- VoteAmerica API
- Ballotpedia API

This service handles:
1. Data fetching from external sources
2. Normalization to CivicQ format
3. Deduplication and merging
4. Database persistence
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.ballot import Ballot, Contest, Candidate, Measure, ContestType, CandidateStatus
from app.services.ballot_data_clients import (
    GoogleCivicClient,
    VoteAmericaClient,
    BallotpediaClient,
)
from app.schemas.ballot_import import (
    ImportedBallot,
    ImportedContest,
    ImportedCandidate,
    ImportSource,
)

logger = logging.getLogger(__name__)


class BallotDataService:
    """
    Service for fetching and importing ballot data from external sources
    """

    def __init__(self, db: Session):
        self.db = db
        self.google_civic = GoogleCivicClient()
        self.vote_america = VoteAmericaClient()
        self.ballotpedia = BallotpediaClient()

    async def import_ballot_by_address(
        self,
        address: str,
        election_date: Optional[date] = None,
        sources: Optional[List[ImportSource]] = None,
    ) -> Ballot:
        """
        Import ballot data for a specific address

        Args:
            address: Voter address (street, city, state, zip)
            election_date: Target election date (defaults to next election)
            sources: List of data sources to use (defaults to all)

        Returns:
            Created/updated Ballot object
        """
        if sources is None:
            sources = [ImportSource.GOOGLE_CIVIC, ImportSource.VOTE_AMERICA, ImportSource.BALLOTPEDIA]

        logger.info(f"Importing ballot data for address: {address}")

        # Fetch data from all sources
        imported_ballots = []

        if ImportSource.GOOGLE_CIVIC in sources:
            try:
                ballot = await self.google_civic.get_ballot_by_address(address, election_date)
                if ballot:
                    imported_ballots.append(ballot)
                    logger.info(f"Fetched ballot from Google Civic API")
            except Exception as e:
                logger.error(f"Error fetching from Google Civic API: {e}")

        if ImportSource.VOTE_AMERICA in sources:
            try:
                ballot = await self.vote_america.get_ballot_by_address(address, election_date)
                if ballot:
                    imported_ballots.append(ballot)
                    logger.info(f"Fetched ballot from VoteAmerica API")
            except Exception as e:
                logger.error(f"Error fetching from VoteAmerica API: {e}")

        if ImportSource.BALLOTPEDIA in sources:
            try:
                ballot = await self.ballotpedia.get_ballot_by_address(address, election_date)
                if ballot:
                    imported_ballots.append(ballot)
                    logger.info(f"Fetched ballot from Ballotpedia API")
            except Exception as e:
                logger.error(f"Error fetching from Ballotpedia API: {e}")

        if not imported_ballots:
            raise ValueError("No ballot data found for this address")

        # Merge data from multiple sources
        merged_ballot = self._merge_ballot_data(imported_ballots)

        # Persist to database
        ballot = await self._create_or_update_ballot(merged_ballot)

        logger.info(f"Successfully imported ballot: {ballot.city_name} - {ballot.election_date}")
        return ballot

    async def import_ballot_by_city(
        self,
        city_name: str,
        state: str,
        election_date: date,
        sources: Optional[List[ImportSource]] = None,
    ) -> Ballot:
        """
        Import ballot data for an entire city

        Args:
            city_name: City name
            state: State abbreviation (e.g., "CA", "NY")
            election_date: Election date
            sources: List of data sources to use (defaults to all)

        Returns:
            Created/updated Ballot object
        """
        if sources is None:
            sources = [ImportSource.GOOGLE_CIVIC, ImportSource.VOTE_AMERICA, ImportSource.BALLOTPEDIA]

        logger.info(f"Importing ballot data for city: {city_name}, {state}")

        # Fetch data from all sources
        imported_ballots = []

        if ImportSource.BALLOTPEDIA in sources:
            try:
                ballot = await self.ballotpedia.get_ballot_by_city(city_name, state, election_date)
                if ballot:
                    imported_ballots.append(ballot)
                    logger.info(f"Fetched ballot from Ballotpedia API")
            except Exception as e:
                logger.error(f"Error fetching from Ballotpedia API: {e}")

        if ImportSource.VOTE_AMERICA in sources:
            try:
                ballot = await self.vote_america.get_ballot_by_city(city_name, state, election_date)
                if ballot:
                    imported_ballots.append(ballot)
                    logger.info(f"Fetched ballot from VoteAmerica API")
            except Exception as e:
                logger.error(f"Error fetching from VoteAmerica API: {e}")

        if not imported_ballots:
            raise ValueError(f"No ballot data found for {city_name}, {state}")

        # Merge data from multiple sources
        merged_ballot = self._merge_ballot_data(imported_ballots)

        # Persist to database
        ballot = await self._create_or_update_ballot(merged_ballot)

        logger.info(f"Successfully imported ballot: {ballot.city_name} - {ballot.election_date}")
        return ballot

    async def refresh_ballot_data(self, ballot_id: int, sources: Optional[List[ImportSource]] = None) -> Ballot:
        """
        Refresh existing ballot data from external sources

        Args:
            ballot_id: Ballot ID to refresh
            sources: List of data sources to use (defaults to all)

        Returns:
            Updated Ballot object
        """
        ballot = self.db.query(Ballot).filter(Ballot.id == ballot_id).first()
        if not ballot:
            raise ValueError(f"Ballot {ballot_id} not found")

        logger.info(f"Refreshing ballot data for: {ballot.city_name} - {ballot.election_date}")

        # Re-import using city method
        city_parts = ballot.city_id.split("-")
        if len(city_parts) >= 2:
            state = city_parts[-1].upper()
            city_name = ballot.city_name
        else:
            raise ValueError(f"Cannot parse city_id: {ballot.city_id}")

        return await self.import_ballot_by_city(city_name, state, ballot.election_date, sources)

    def _merge_ballot_data(self, imported_ballots: List[ImportedBallot]) -> ImportedBallot:
        """
        Merge ballot data from multiple sources

        Prioritization:
        1. Google Civic API (most authoritative)
        2. Ballotpedia (comprehensive candidate info)
        3. VoteAmerica (additional context)
        """
        if not imported_ballots:
            raise ValueError("No ballots to merge")

        if len(imported_ballots) == 1:
            return imported_ballots[0]

        # Sort by source priority
        source_priority = {
            ImportSource.GOOGLE_CIVIC: 1,
            ImportSource.BALLOTPEDIA: 2,
            ImportSource.VOTE_AMERICA: 3,
        }
        sorted_ballots = sorted(imported_ballots, key=lambda b: source_priority.get(b.source, 99))

        # Start with highest priority ballot
        merged = sorted_ballots[0]

        # Merge contests from other sources
        for ballot in sorted_ballots[1:]:
            merged = self._merge_two_ballots(merged, ballot)

        logger.info(f"Merged {len(imported_ballots)} ballot sources")
        return merged

    def _merge_two_ballots(self, primary: ImportedBallot, secondary: ImportedBallot) -> ImportedBallot:
        """Merge two ballots, with primary taking precedence"""

        # Use primary metadata, but merge source_data
        merged = primary.model_copy(deep=True)
        merged.source_data = {**secondary.source_data, **primary.source_data}
        merged.sources.extend([s for s in secondary.sources if s not in merged.sources])

        # Merge contests
        primary_contest_map = {c.title.lower(): c for c in merged.contests}

        for contest in secondary.contests:
            title_key = contest.title.lower()

            if title_key in primary_contest_map:
                # Merge candidates for existing contest
                primary_contest = primary_contest_map[title_key]
                self._merge_contest_candidates(primary_contest, contest)
            else:
                # Add new contest
                merged.contests.append(contest)

        return merged

    def _merge_contest_candidates(self, primary: ImportedContest, secondary: ImportedContest):
        """Merge candidates from two contests"""
        primary_candidate_map = {c.name.lower(): c for c in primary.candidates}

        for candidate in secondary.candidates:
            name_key = candidate.name.lower()

            if name_key in primary_candidate_map:
                # Merge candidate data (add any missing fields)
                primary_candidate = primary_candidate_map[name_key]
                if not primary_candidate.email and candidate.email:
                    primary_candidate.email = candidate.email
                if not primary_candidate.phone and candidate.phone:
                    primary_candidate.phone = candidate.phone
                if not primary_candidate.website and candidate.website:
                    primary_candidate.website = candidate.website
                if not primary_candidate.photo_url and candidate.photo_url:
                    primary_candidate.photo_url = candidate.photo_url
                # Merge profile fields
                if candidate.profile_fields:
                    primary_candidate.profile_fields = {
                        **candidate.profile_fields,
                        **primary_candidate.profile_fields
                    }
            else:
                # Add new candidate
                primary.candidates.append(candidate)

    async def _create_or_update_ballot(self, imported_ballot: ImportedBallot) -> Ballot:
        """
        Create or update ballot in database
        """
        # Check if ballot already exists
        existing_ballot = self.db.query(Ballot).filter(
            Ballot.city_id == imported_ballot.city_id,
            Ballot.election_date == imported_ballot.election_date,
        ).first()

        if existing_ballot:
            logger.info(f"Updating existing ballot: {existing_ballot.id}")
            ballot = existing_ballot
            ballot.version += 1
            ballot.source_metadata = imported_ballot.source_data

            # Delete existing contests (cascade will handle candidates/measures)
            for contest in ballot.contests:
                self.db.delete(contest)
            self.db.flush()
        else:
            logger.info(f"Creating new ballot for {imported_ballot.city_name}")
            ballot = Ballot(
                city_id=imported_ballot.city_id,
                city_name=imported_ballot.city_name,
                election_date=imported_ballot.election_date,
                version=1,
                source_metadata=imported_ballot.source_data,
                is_published=False,
            )
            self.db.add(ballot)
            self.db.flush()

        # Create contests
        for idx, imported_contest in enumerate(imported_ballot.contests):
            contest = Contest(
                ballot_id=ballot.id,
                type=imported_contest.contest_type,
                title=imported_contest.title,
                jurisdiction=imported_contest.jurisdiction,
                office=imported_contest.office,
                seat_count=imported_contest.seat_count or 1,
                description=imported_contest.description,
                display_order=idx,
            )
            self.db.add(contest)
            self.db.flush()

            # Create candidates for races
            if imported_contest.contest_type == ContestType.RACE:
                for candidate_idx, imported_candidate in enumerate(imported_contest.candidates):
                    candidate = Candidate(
                        contest_id=contest.id,
                        name=imported_candidate.name,
                        filing_id=imported_candidate.filing_id,
                        email=imported_candidate.email,
                        phone=imported_candidate.phone,
                        website=imported_candidate.website,
                        photo_url=imported_candidate.photo_url,
                        profile_fields=imported_candidate.profile_fields,
                        status=CandidateStatus.PENDING,
                        identity_verified=False,
                        display_order=candidate_idx,
                    )
                    self.db.add(candidate)

            # Create measure for ballot measures
            elif imported_contest.contest_type == ContestType.MEASURE:
                if imported_contest.measure:
                    measure = Measure(
                        contest_id=contest.id,
                        measure_number=imported_contest.measure.measure_number,
                        measure_text=imported_contest.measure.measure_text,
                        summary=imported_contest.measure.summary,
                        fiscal_notes=imported_contest.measure.fiscal_notes,
                        pro_statement=imported_contest.measure.pro_statement,
                        con_statement=imported_contest.measure.con_statement,
                    )
                    self.db.add(measure)

        self.db.commit()
        self.db.refresh(ballot)

        logger.info(f"Ballot saved with {len(ballot.contests)} contests")
        return ballot

    async def get_import_status(self, ballot_id: int) -> Dict[str, Any]:
        """
        Get import status and data quality metrics for a ballot
        """
        ballot = self.db.query(Ballot).filter(Ballot.id == ballot_id).first()
        if not ballot:
            raise ValueError(f"Ballot {ballot_id} not found")

        total_contests = len(ballot.contests)
        total_candidates = sum(len(c.candidates) for c in ballot.contests)

        candidates_with_contact = sum(
            1 for c in ballot.contests
            for candidate in c.candidates
            if candidate.email or candidate.phone
        )

        candidates_verified = sum(
            1 for c in ballot.contests
            for candidate in c.candidates
            if candidate.identity_verified
        )

        return {
            "ballot_id": ballot.id,
            "city_name": ballot.city_name,
            "election_date": ballot.election_date.isoformat(),
            "version": ballot.version,
            "is_published": ballot.is_published,
            "last_updated": ballot.updated_at.isoformat(),
            "sources": ballot.source_metadata.get("sources", []) if ballot.source_metadata else [],
            "statistics": {
                "total_contests": total_contests,
                "total_candidates": total_candidates,
                "candidates_with_contact": candidates_with_contact,
                "candidates_verified": candidates_verified,
                "contact_info_percentage": round(
                    (candidates_with_contact / total_candidates * 100) if total_candidates > 0 else 0, 1
                ),
                "verification_percentage": round(
                    (candidates_verified / total_candidates * 100) if total_candidates > 0 else 0, 1
                ),
            },
        }
