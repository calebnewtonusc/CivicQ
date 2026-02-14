"""
Admin API Routes

City staff and moderator endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.models.base import get_db
from app.core.security import require_admin
from app.models.user import User
from app.services.ballot_data_service import BallotDataService
from app.schemas.ballot_import import (
    BallotImportRequest,
    BallotImportResponse,
    BallotRefreshRequest,
    BallotImportStatus,
    CandidateContactUpdate,
    BulkContactImport,
    ImportSource,
)
from app.models.ballot import Candidate
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Moderation Endpoints
# ============================================================================

@router.get("/modqueue")
async def get_moderation_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get moderation queue (admin/moderator only)"""
    return {"message": "Get modqueue endpoint - to be implemented"}


@router.post("/modaction")
async def perform_moderation_action(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Perform a moderation action (admin/moderator only)"""
    return {"message": "Mod action endpoint - to be implemented"}


# ============================================================================
# Metrics Endpoints
# ============================================================================

@router.get("/metrics")
async def get_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get city metrics (city admin only)"""
    return {"message": "Get metrics endpoint - to be implemented"}


@router.get("/coverage")
async def get_coverage(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get answer coverage statistics (city admin only)"""
    return {"message": "Get coverage endpoint - to be implemented"}


@router.get("/export")
async def export_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Export data for public archive (city admin only)"""
    return {"message": "Export data endpoint - to be implemented"}


# ============================================================================
# Ballot Data Import Endpoints
# ============================================================================

@router.post("/ballots/import", response_model=BallotImportResponse)
async def import_ballot_data(
    request: BallotImportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Import ballot data from external APIs

    This endpoint allows city admins to quickly onboard a new city by importing
    ballot data from Google Civic Information API, VoteAmerica, and Ballotpedia.

    **Usage:**
    - Provide either `address` OR (`city_name` + `state`)
    - Optionally specify `election_date` (defaults to next election)
    - Choose which data sources to use

    **Returns:**
    - Ballot ID
    - Number of contests, candidates, and measures imported
    - Data quality warnings and errors

    **Example:**
    ```json
    {
        "city_name": "Los Angeles",
        "state": "CA",
        "election_date": "2024-11-05",
        "sources": ["google_civic", "ballotpedia"]
    }
    ```
    """
    try:
        # Validate request
        request.validate_request()

        service = BallotDataService(db)

        # Import by address or city
        if request.address:
            ballot = await service.import_ballot_by_address(
                address=request.address,
                election_date=request.election_date,
                sources=request.sources,
            )
        else:
            ballot = await service.import_ballot_by_city(
                city_name=request.city_name,
                state=request.state,
                election_date=request.election_date,
                sources=request.sources,
            )

        # Count imported items
        contests_count = len(ballot.contests)
        candidates_count = sum(len(c.candidates) for c in ballot.contests if c.type.value == "race")
        measures_count = sum(len(c.measures) for c in ballot.contests if c.type.value == "measure")

        return BallotImportResponse(
            success=True,
            ballot_id=ballot.id,
            city_name=ballot.city_name,
            election_date=ballot.election_date,
            contests_imported=contests_count,
            candidates_imported=candidates_count,
            measures_imported=measures_count,
            sources_used=request.sources,
            warnings=[],
            errors=[],
        )

    except ValueError as e:
        logger.error(f"Validation error during ballot import: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error importing ballot data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to import ballot data")


@router.post("/ballots/{ballot_id}/refresh", response_model=BallotImportResponse)
async def refresh_ballot_data(
    ballot_id: int,
    request: BallotRefreshRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Refresh existing ballot data from external APIs

    This re-fetches ballot data from external sources and updates the database.
    Useful for getting the latest candidate information, contact details, etc.

    **Note:** This will increment the ballot version number.
    """
    try:
        service = BallotDataService(db)

        ballot = await service.refresh_ballot_data(
            ballot_id=ballot_id,
            sources=request.sources,
        )

        # Count items
        contests_count = len(ballot.contests)
        candidates_count = sum(len(c.candidates) for c in ballot.contests if c.type.value == "race")
        measures_count = sum(len(c.measures) for c in ballot.contests if c.type.value == "measure")

        return BallotImportResponse(
            success=True,
            ballot_id=ballot.id,
            city_name=ballot.city_name,
            election_date=ballot.election_date,
            contests_imported=contests_count,
            candidates_imported=candidates_count,
            measures_imported=measures_count,
            sources_used=request.sources,
            warnings=[],
            errors=[],
        )

    except ValueError as e:
        logger.error(f"Error refreshing ballot: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error refreshing ballot data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to refresh ballot data")


@router.get("/ballots/{ballot_id}/import-status", response_model=BallotImportStatus)
async def get_ballot_import_status(
    ballot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get import status and data quality metrics for a ballot

    Returns:
    - Number of contests, candidates, measures
    - Contact information coverage
    - Verification status
    - Data sources used
    - Last update time
    """
    try:
        service = BallotDataService(db)
        status = await service.get_import_status(ballot_id)
        return status

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting import status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get import status")


@router.post("/ballots/{ballot_id}/update-contacts")
async def update_candidate_contacts(
    ballot_id: int,
    updates: BulkContactImport,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Bulk update candidate contact information

    This endpoint allows admins to manually add or update contact information
    for candidates that may not be available via external APIs.

    **Example:**
    ```json
    {
        "ballot_id": 123,
        "candidates": [
            {
                "candidate_id": 456,
                "email": "candidate@example.com",
                "phone": "+1-555-0123",
                "website": "https://example.com"
            }
        ]
    }
    ```
    """
    try:
        updated_count = 0

        for update in updates.candidates:
            candidate = db.query(Candidate).filter(Candidate.id == update.candidate_id).first()

            if not candidate:
                logger.warning(f"Candidate {update.candidate_id} not found")
                continue

            # Verify candidate belongs to this ballot
            if candidate.contest.ballot_id != ballot_id:
                logger.warning(f"Candidate {update.candidate_id} does not belong to ballot {ballot_id}")
                continue

            # Update contact info
            if update.email:
                candidate.email = update.email
            if update.phone:
                candidate.phone = update.phone
            if update.website:
                candidate.website = update.website

            updated_count += 1

        db.commit()

        return {
            "success": True,
            "updated_count": updated_count,
            "message": f"Updated contact information for {updated_count} candidates"
        }

    except Exception as e:
        logger.error(f"Error updating candidate contacts: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update candidate contacts")


@router.post("/ballots/{ballot_id}/publish")
async def publish_ballot(
    ballot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Publish a ballot (make it visible to voters)

    This sets the `is_published` flag to True, making the ballot
    visible on the frontend.
    """
    from app.models.ballot import Ballot

    ballot = db.query(Ballot).filter(Ballot.id == ballot_id).first()
    if not ballot:
        raise HTTPException(status_code=404, detail="Ballot not found")

    ballot.is_published = True
    db.commit()

    return {
        "success": True,
        "ballot_id": ballot.id,
        "message": f"Ballot for {ballot.city_name} published successfully"
    }


@router.post("/ballots/{ballot_id}/unpublish")
async def unpublish_ballot(
    ballot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Unpublish a ballot (hide from voters)

    This sets the `is_published` flag to False.
    """
    from app.models.ballot import Ballot

    ballot = db.query(Ballot).filter(Ballot.id == ballot_id).first()
    if not ballot:
        raise HTTPException(status_code=404, detail="Ballot not found")

    ballot.is_published = False
    db.commit()

    return {
        "success": True,
        "ballot_id": ballot.id,
        "message": f"Ballot for {ballot.city_name} unpublished successfully"
    }
