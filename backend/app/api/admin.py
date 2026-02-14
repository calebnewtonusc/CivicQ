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
    page: int = 1,
    page_size: int = 20,
    filter_type: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get moderation queue (admin/moderator only)"""
    from app.models.question import Question, QuestionStatus
    from app.models.moderation import Report, ReportStatus

    offset = (page - 1) * page_size

    # Get pending questions
    pending_questions = db.query(Question).filter(
        Question.status == QuestionStatus.PENDING
    ).count()

    # Get pending reports
    pending_reports = db.query(Report).filter(
        Report.status == ReportStatus.PENDING
    ).count()

    # Get flagged content
    flagged_questions = db.query(Question).filter(
        Question.is_flagged > 0
    ).count()

    items = []

    if filter_type == "questions" or not filter_type:
        questions = db.query(Question).filter(
            Question.status == QuestionStatus.PENDING
        ).offset(offset).limit(page_size).all()

        for q in questions:
            items.append({
                "id": q.id,
                "type": "question",
                "content": q.question_text,
                "author_id": q.author_id,
                "created_at": q.created_at.isoformat() if q.created_at else None,
                "status": q.status.value,
                "flags": q.is_flagged,
            })

    if filter_type == "reports" or (not filter_type and len(items) < page_size):
        reports = db.query(Report).filter(
            Report.status == ReportStatus.PENDING
        ).offset(offset).limit(page_size - len(items)).all()

        for r in reports:
            items.append({
                "id": r.id,
                "type": "report",
                "target_type": r.target_type,
                "target_id": r.target_id,
                "reason": r.reason.value,
                "description": r.description,
                "reporter_id": r.reporter_id,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "status": r.status.value,
            })

    return {
        "items": items,
        "total_pending_questions": pending_questions,
        "total_pending_reports": pending_reports,
        "total_flagged": flagged_questions,
        "page": page,
        "page_size": page_size,
    }


@router.post("/modaction")
async def perform_moderation_action(
    action: str,
    target_type: str,
    target_id: int,
    reason: str = None,
    notes: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Perform a moderation action (admin/moderator only)"""
    from app.models.moderation import ModerationAction, ModerationActionType, AuditLog, AuditEventType
    from app.models.question import Question, QuestionStatus

    # Create moderation action record
    mod_action = ModerationAction(
        target_type=target_type,
        target_id=target_id,
        action_type=ModerationActionType[action.upper()],
        moderator_id=current_user.id,
        rationale_code=reason,
        rationale_text=notes,
    )
    db.add(mod_action)

    # Apply the action
    if target_type == "question":
        question = db.query(Question).filter(Question.id == target_id).first()
        if question:
            if action == "approve":
                question.status = QuestionStatus.APPROVED
            elif action == "remove":
                question.status = QuestionStatus.REMOVED
                question.moderation_notes = f"{reason}: {notes or ''}"

    # Log audit event
    audit = AuditLog(
        event_type=AuditEventType.MODERATION_ACTION,
        actor_id=current_user.id,
        target_type=target_type,
        target_id=target_id,
        event_data={
            "action": action,
            "reason": reason,
            "notes": notes,
        },
    )
    db.add(audit)

    db.commit()

    return {
        "success": True,
        "action": action,
        "target_type": target_type,
        "target_id": target_id,
    }


# ============================================================================
# Metrics Endpoints
# ============================================================================

@router.get("/metrics")
async def get_metrics(
    start_date: str = None,
    end_date: str = None,
    city_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get city metrics (city admin only)"""
    from app.models.question import Question, Vote, QuestionStatus
    from app.models.answer import VideoAnswer, AnswerStatus
    from app.models.ballot import Contest
    from datetime import datetime, timedelta
    from sqlalchemy import func, and_

    # Date filtering
    filters = []
    if start_date:
        filters.append(Question.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        filters.append(Question.created_at <= datetime.fromisoformat(end_date))
    if city_id:
        # Filter by city through contest -> ballot
        pass

    # User engagement metrics
    total_users = db.query(func.count(User.id)).scalar()

    last_7_days = datetime.utcnow() - timedelta(days=7)
    last_30_days = datetime.utcnow() - timedelta(days=30)

    active_users_7d = db.query(func.count(User.id)).filter(
        User.last_active >= last_7_days
    ).scalar()

    active_users_30d = db.query(func.count(User.id)).filter(
        User.last_active >= last_30_days
    ).scalar()

    # Question metrics
    total_questions = db.query(func.count(Question.id)).filter(*filters).scalar()
    approved_questions = db.query(func.count(Question.id)).filter(
        Question.status == QuestionStatus.APPROVED,
        *filters
    ).scalar()

    questions_7d = db.query(func.count(Question.id)).filter(
        Question.created_at >= last_7_days
    ).scalar()

    # Answer metrics
    total_answers = db.query(func.count(VideoAnswer.id)).scalar()
    published_answers = db.query(func.count(VideoAnswer.id)).filter(
        VideoAnswer.status == AnswerStatus.PUBLISHED
    ).scalar()

    answers_7d = db.query(func.count(VideoAnswer.id)).filter(
        VideoAnswer.created_at >= last_7_days
    ).scalar()

    # Vote metrics
    total_votes = db.query(func.count(Vote.id)).scalar()
    votes_7d = db.query(func.count(Vote.id)).filter(
        Vote.created_at >= last_7_days
    ).scalar()

    # Engagement rate (votes per question)
    engagement_rate = (total_votes / total_questions * 100) if total_questions > 0 else 0

    # Average votes per question
    avg_votes_per_question = total_votes / total_questions if total_questions > 0 else 0

    # Answer rate (percentage of questions with answers)
    questions_with_answers = db.query(func.count(func.distinct(VideoAnswer.question_id))).scalar()
    answer_rate = (questions_with_answers / total_questions * 100) if total_questions > 0 else 0

    # Top contests by activity
    top_contests = db.query(
        Contest.id,
        Contest.title,
        func.count(Question.id).label('question_count')
    ).join(Question).group_by(Contest.id, Contest.title).order_by(
        func.count(Question.id).desc()
    ).limit(10).all()

    return {
        "users": {
            "total": total_users or 0,
            "active_7d": active_users_7d or 0,
            "active_30d": active_users_30d or 0,
        },
        "questions": {
            "total": total_questions or 0,
            "approved": approved_questions or 0,
            "last_7_days": questions_7d or 0,
            "avg_votes": round(avg_votes_per_question, 2),
        },
        "answers": {
            "total": total_answers or 0,
            "published": published_answers or 0,
            "last_7_days": answers_7d or 0,
            "coverage_rate": round(answer_rate, 2),
        },
        "engagement": {
            "total_votes": total_votes or 0,
            "votes_7d": votes_7d or 0,
            "engagement_rate": round(engagement_rate, 2),
        },
        "top_contests": [
            {
                "id": c.id,
                "title": c.title,
                "question_count": c.question_count,
            }
            for c in top_contests
        ],
    }


@router.get("/coverage")
async def get_coverage(
    city_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get answer coverage statistics (city admin only)"""
    from app.models.question import Question, QuestionStatus
    from app.models.answer import VideoAnswer, AnswerStatus
    from app.models.ballot import Contest, Candidate
    from sqlalchemy import func

    # Get all contests
    contest_query = db.query(Contest)
    if city_id:
        from app.models.ballot import Ballot
        contest_query = contest_query.join(Ballot).filter(Ballot.city_id == city_id)

    contests = contest_query.all()

    coverage_data = []

    for contest in contests:
        # Count questions
        total_questions = db.query(func.count(Question.id)).filter(
            Question.contest_id == contest.id,
            Question.status == QuestionStatus.APPROVED
        ).scalar()

        # Count answered questions
        answered_questions = db.query(func.count(func.distinct(VideoAnswer.question_id))).join(
            Question
        ).filter(
            Question.contest_id == contest.id,
            VideoAnswer.status == AnswerStatus.PUBLISHED
        ).scalar()

        # Get candidates
        candidates_count = db.query(func.count(Candidate.id)).filter(
            Candidate.contest_id == contest.id
        ).scalar()

        # Calculate coverage
        coverage_percent = (answered_questions / total_questions * 100) if total_questions > 0 else 0

        coverage_data.append({
            "contest_id": contest.id,
            "contest_title": contest.title,
            "total_questions": total_questions or 0,
            "answered_questions": answered_questions or 0,
            "coverage_percent": round(coverage_percent, 2),
            "candidates_count": candidates_count or 0,
        })

    # Overall statistics
    total_questions_all = sum(c["total_questions"] for c in coverage_data)
    total_answered_all = sum(c["answered_questions"] for c in coverage_data)
    overall_coverage = (total_answered_all / total_questions_all * 100) if total_questions_all > 0 else 0

    return {
        "overall_coverage": round(overall_coverage, 2),
        "total_questions": total_questions_all,
        "total_answered": total_answered_all,
        "contests": coverage_data,
    }


@router.get("/export")
async def export_data(
    format: str = "csv",
    data_type: str = "questions",
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Export data for public archive (city admin only)"""
    from fastapi.responses import StreamingResponse
    from io import StringIO
    import csv
    from datetime import datetime
    from app.models.question import Question, QuestionStatus
    from app.models.answer import VideoAnswer

    # Date filters
    filters = []
    if start_date:
        filters.append(Question.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        filters.append(Question.created_at <= datetime.fromisoformat(end_date))

    if data_type == "questions":
        # Export questions
        questions = db.query(Question).filter(
            Question.status == QuestionStatus.APPROVED,
            *filters
        ).all()

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Question Text', 'Contest ID', 'Status', 'Upvotes', 'Downvotes', 'Created At'])

        for q in questions:
            writer.writerow([
                q.id,
                q.question_text,
                q.contest_id,
                q.status.value,
                q.upvotes,
                q.downvotes,
                q.created_at.isoformat() if q.created_at else '',
            ])

        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=questions_export_{datetime.utcnow().strftime('%Y%m%d')}.csv"}
        )

    elif data_type == "answers":
        # Export answers
        answers = db.query(VideoAnswer).filter(
            VideoAnswer.status == AnswerStatus.PUBLISHED
        ).all()

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Candidate ID', 'Question ID', 'Duration', 'Status', 'Created At'])

        for a in answers:
            writer.writerow([
                a.id,
                a.candidate_id,
                a.question_id,
                a.duration,
                a.status.value,
                a.created_at.isoformat() if a.created_at else '',
            ])

        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=answers_export_{datetime.utcnow().strftime('%Y%m%d')}.csv"}
        )

    return {"message": "Invalid data type"}


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
