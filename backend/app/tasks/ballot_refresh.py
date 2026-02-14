"""
Celery Tasks for Ballot Data Refresh

Background jobs to automatically refresh ballot data from external APIs.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from celery import Task
from sqlalchemy.orm import Session

from app.tasks import celery_app
from app.models.base import SessionLocal
from app.models.ballot import Ballot
from app.services.ballot_data_service import BallotDataService
from app.schemas.ballot_import import ImportSource

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session management"""
    _db: Optional[Session] = None

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        """Close database session after task completes"""
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(base=DatabaseTask, name="tasks.refresh_ballot")
def refresh_ballot_task(
    ballot_id: int,
    sources: Optional[List[str]] = None,
):
    """
    Refresh a single ballot from external APIs

    Args:
        ballot_id: Ballot ID to refresh
        sources: List of data sources to use (optional)
    """
    logger.info(f"Starting ballot refresh task for ballot {ballot_id}")

    try:
        db = SessionLocal()
        service = BallotDataService(db)

        # Convert source strings to enum
        source_enums = None
        if sources:
            source_enums = [ImportSource(s) for s in sources]

        # Refresh the ballot
        ballot = service.refresh_ballot_data(ballot_id, sources=source_enums)

        logger.info(f"Successfully refreshed ballot {ballot_id}: {ballot.city_name}")

        db.close()

        return {
            "success": True,
            "ballot_id": ballot.id,
            "city_name": ballot.city_name,
            "contests_count": len(ballot.contests),
        }

    except Exception as e:
        logger.error(f"Error refreshing ballot {ballot_id}: {e}", exc_info=True)
        return {
            "success": False,
            "ballot_id": ballot_id,
            "error": str(e),
        }


@celery_app.task(base=DatabaseTask, name="tasks.refresh_all_upcoming_ballots")
def refresh_all_upcoming_ballots_task(days_ahead: int = 60):
    """
    Refresh all ballots for upcoming elections

    Args:
        days_ahead: Refresh ballots for elections within this many days (default: 60)
    """
    logger.info(f"Starting refresh for all upcoming ballots (next {days_ahead} days)")

    try:
        db = SessionLocal()

        # Find all ballots with elections in the next N days
        cutoff_date = datetime.now().date() + timedelta(days=days_ahead)
        today = datetime.now().date()

        ballots = db.query(Ballot).filter(
            Ballot.election_date >= today,
            Ballot.election_date <= cutoff_date,
        ).all()

        logger.info(f"Found {len(ballots)} ballots to refresh")

        # Queue individual refresh tasks
        results = []
        for ballot in ballots:
            result = refresh_ballot_task.delay(ballot.id)
            results.append({
                "ballot_id": ballot.id,
                "task_id": result.id,
            })

        db.close()

        return {
            "success": True,
            "ballots_queued": len(results),
            "tasks": results,
        }

    except Exception as e:
        logger.error(f"Error queuing ballot refresh tasks: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }


@celery_app.task(base=DatabaseTask, name="tasks.refresh_ballot_daily")
def refresh_ballot_daily_task(ballot_id: int):
    """
    Daily refresh task for a specific ballot

    This can be scheduled to run daily for high-priority ballots
    (e.g., elections happening within 2 weeks)
    """
    logger.info(f"Daily refresh for ballot {ballot_id}")

    try:
        db = SessionLocal()
        ballot = db.query(Ballot).filter(Ballot.id == ballot_id).first()

        if not ballot:
            logger.error(f"Ballot {ballot_id} not found")
            db.close()
            return {"success": False, "error": "Ballot not found"}

        # Check if election is still upcoming
        if ballot.election_date < datetime.now().date():
            logger.info(f"Ballot {ballot_id} election has passed, skipping refresh")
            db.close()
            return {
                "success": True,
                "skipped": True,
                "reason": "Election date has passed",
            }

        db.close()

        # Trigger refresh
        return refresh_ballot_task(ballot_id)

    except Exception as e:
        logger.error(f"Error in daily refresh task for ballot {ballot_id}: {e}", exc_info=True)
        return {
            "success": False,
            "ballot_id": ballot_id,
            "error": str(e),
        }


@celery_app.task(name="tasks.schedule_ballot_refreshes")
def schedule_ballot_refreshes_task():
    """
    Schedule periodic refreshes for upcoming elections

    This task should be run daily (via cron or Celery beat) to:
    1. Refresh ballots for elections within 2 weeks (daily)
    2. Refresh ballots for elections within 60 days (weekly)
    """
    logger.info("Scheduling ballot refreshes")

    try:
        db = SessionLocal()
        today = datetime.now().date()

        # High priority: Elections within 2 weeks (refresh daily)
        two_weeks = today + timedelta(days=14)
        urgent_ballots = db.query(Ballot).filter(
            Ballot.election_date >= today,
            Ballot.election_date <= two_weeks,
        ).all()

        logger.info(f"Scheduling daily refresh for {len(urgent_ballots)} urgent ballots")
        for ballot in urgent_ballots:
            refresh_ballot_task.delay(ballot.id)

        # Medium priority: Elections within 60 days (refresh if not updated recently)
        sixty_days = today + timedelta(days=60)
        one_week_ago = datetime.now() - timedelta(days=7)

        medium_priority_ballots = db.query(Ballot).filter(
            Ballot.election_date > two_weeks,
            Ballot.election_date <= sixty_days,
            Ballot.updated_at < one_week_ago,  # Not updated in last week
        ).all()

        logger.info(f"Scheduling refresh for {len(medium_priority_ballots)} medium-priority ballots")
        for ballot in medium_priority_ballots:
            refresh_ballot_task.delay(ballot.id)

        db.close()

        return {
            "success": True,
            "urgent_ballots_scheduled": len(urgent_ballots),
            "medium_priority_scheduled": len(medium_priority_ballots),
        }

    except Exception as e:
        logger.error(f"Error scheduling ballot refreshes: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }


# Celery Beat Schedule (add this to your Celery configuration)
celery_app.conf.beat_schedule = {
    "schedule-ballot-refreshes-daily": {
        "task": "tasks.schedule_ballot_refreshes",
        "schedule": 86400.0,  # Run daily (every 24 hours)
    },
}
