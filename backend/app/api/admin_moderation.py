"""
Admin Moderation API Routes

Question moderation, user management, and content moderation endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.base import get_db
from app.models.user import User, UserRole
from app.models.question import Question, QuestionStatus, Vote
from app.models.answer import VideoAnswer, AnswerStatus
from app.models.moderation import Report, ModerationAction, AuditLog, ReportStatus, ModerationActionType, AuditEventType
from app.core.security import get_current_user, require_admin
from pydantic import BaseModel

router = APIRouter()


# ============================================================================
# Pydantic Models
# ============================================================================

class AdminStats(BaseModel):
    total_users: int
    active_users_24h: int
    total_questions: int
    pending_questions: int
    flagged_content: int
    total_answers: int
    total_votes: int
    engagement_rate: float


class ModerationRequest(BaseModel):
    action: str  # 'approve', 'reject', 'merge', 'flag', 'remove'
    reason: Optional[str] = None
    notes: Optional[str] = None
    merge_into_id: Optional[int] = None


class UserModerationAction(BaseModel):
    action: str  # 'warn', 'suspend', 'ban', 'restore'
    reason: str
    duration_days: Optional[int] = None
    notes: Optional[str] = None


class BulkOperationResult(BaseModel):
    success_count: int
    failure_count: int
    errors: List[dict] = []


# ============================================================================
# Dashboard Stats
# ============================================================================

@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    city_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get admin dashboard statistics"""

    # Base query filters
    city_filter = [User.city_id == city_id] if city_id else []

    # Total users
    total_users = db.query(func.count(User.id)).filter(*city_filter).scalar()

    # Active users in last 24h
    yesterday = datetime.utcnow() - timedelta(days=1)
    active_users_24h = db.query(func.count(User.id)).filter(
        User.last_active >= yesterday,
        *city_filter
    ).scalar()

    # Questions
    total_questions = db.query(func.count(Question.id)).scalar()
    pending_questions = db.query(func.count(Question.id)).filter(
        Question.status == QuestionStatus.PENDING
    ).scalar()

    # Flagged content
    flagged_content = db.query(func.count(Report.id)).filter(
        Report.status == ReportStatus.PENDING
    ).scalar()

    # Answers
    total_answers = db.query(func.count(VideoAnswer.id)).scalar()

    # Votes
    total_votes = db.query(func.count(Vote.id)).scalar()

    # Engagement rate (votes per question)
    engagement_rate = (total_votes / total_questions * 100) if total_questions > 0 else 0

    return AdminStats(
        total_users=total_users or 0,
        active_users_24h=active_users_24h or 0,
        total_questions=total_questions or 0,
        pending_questions=pending_questions or 0,
        flagged_content=flagged_content or 0,
        total_answers=total_answers or 0,
        total_votes=total_votes or 0,
        engagement_rate=round(engagement_rate, 2),
    )


@router.get("/alerts")
async def get_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get system alerts for admin dashboard"""

    alerts = []

    # Check for high number of pending questions
    pending_count = db.query(func.count(Question.id)).filter(
        Question.status == QuestionStatus.PENDING
    ).scalar()

    if pending_count and pending_count > 50:
        alerts.append({
            "id": 1,
            "type": "High Pending Queue",
            "message": f"{pending_count} questions pending moderation",
            "severity": "warning",
            "created_at": datetime.utcnow().isoformat(),
        })

    # Check for unresolved reports
    report_count = db.query(func.count(Report.id)).filter(
        Report.status == ReportStatus.PENDING
    ).scalar()

    if report_count and report_count > 20:
        alerts.append({
            "id": 2,
            "type": "Unresolved Reports",
            "message": f"{report_count} content reports need review",
            "severity": "warning",
            "created_at": datetime.utcnow().isoformat(),
        })

    return alerts


@router.get("/activity")
async def get_recent_activity(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get recent admin activity from audit log"""

    logs = db.query(AuditLog).order_by(desc(AuditLog.created_at)).limit(limit).all()
    return logs


# ============================================================================
# Question Moderation
# ============================================================================

@router.get("/questions/pending")
async def get_pending_questions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get pending questions for moderation"""

    offset = (page - 1) * page_size

    total = db.query(func.count(Question.id)).filter(
        Question.status == QuestionStatus.PENDING
    ).scalar()

    questions = db.query(Question).filter(
        Question.status == QuestionStatus.PENDING
    ).order_by(desc(Question.created_at)).offset(offset).limit(page_size).all()

    return {
        "items": questions,
        "total": total or 0,
        "page": page,
        "page_size": page_size,
        "total_pages": ((total or 0) + page_size - 1) // page_size,
    }


@router.post("/questions/{question_id}/approve")
async def approve_question(
    question_id: int,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Approve a pending question"""

    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    question.status = QuestionStatus.APPROVED

    # Log moderation action
    action = ModerationAction(
        target_type="question",
        target_id=question_id,
        action_type=ModerationActionType.APPROVE,
        moderator_id=current_user.id,
        rationale_text=notes,
    )
    db.add(action)

    # Log audit event
    audit = AuditLog(
        event_type=AuditEventType.MODERATION_ACTION,
        actor_id=current_user.id,
        target_type="question",
        target_id=question_id,
        event_data={"action": "approve", "notes": notes},
    )
    db.add(audit)

    db.commit()
    db.refresh(question)

    return question


@router.post("/questions/{question_id}/reject")
async def reject_question(
    question_id: int,
    reason: str,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Reject a pending question"""

    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    question.status = QuestionStatus.REMOVED
    question.moderation_notes = f"Rejected: {reason}. {notes or ''}"

    # Log moderation action
    action = ModerationAction(
        target_type="question",
        target_id=question_id,
        action_type=ModerationActionType.REMOVE,
        moderator_id=current_user.id,
        rationale_code=reason,
        rationale_text=notes,
    )
    db.add(action)

    # Log audit event
    audit = AuditLog(
        event_type=AuditEventType.MODERATION_ACTION,
        actor_id=current_user.id,
        target_type="question",
        target_id=question_id,
        event_data={"action": "reject", "reason": reason, "notes": notes},
    )
    db.add(audit)

    db.commit()

    return {"success": True, "message": "Question rejected"}


@router.post("/questions/merge")
async def merge_questions(
    source_ids: List[int],
    target_id: int,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Merge duplicate questions into a target question"""

    target = db.query(Question).filter(Question.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target question not found")

    for source_id in source_ids:
        source = db.query(Question).filter(Question.id == source_id).first()
        if source:
            source.status = QuestionStatus.MERGED
            source.cluster_id = target_id

            # Transfer votes to target
            target.upvotes += source.upvotes
            target.downvotes += source.downvotes

            # Log action
            action = ModerationAction(
                target_type="question",
                target_id=source_id,
                action_type=ModerationActionType.MERGE,
                moderator_id=current_user.id,
                rationale_text=f"Merged into question {target_id}. {notes or ''}",
            )
            db.add(action)

    db.commit()
    db.refresh(target)

    return target


@router.post("/questions/bulk-approve")
async def bulk_approve_questions(
    question_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Bulk approve multiple questions"""

    success_count = 0
    failure_count = 0
    errors = []

    for question_id in question_ids:
        try:
            question = db.query(Question).filter(Question.id == question_id).first()
            if question:
                question.status = QuestionStatus.APPROVED
                success_count += 1
            else:
                failure_count += 1
                errors.append({"id": question_id, "error": "Not found"})
        except Exception as e:
            failure_count += 1
            errors.append({"id": question_id, "error": str(e)})

    db.commit()

    return BulkOperationResult(
        success_count=success_count,
        failure_count=failure_count,
        errors=errors,
    )


@router.post("/questions/bulk-reject")
async def bulk_reject_questions(
    question_ids: List[int],
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Bulk reject multiple questions"""

    success_count = 0
    failure_count = 0
    errors = []

    for question_id in question_ids:
        try:
            question = db.query(Question).filter(Question.id == question_id).first()
            if question:
                question.status = QuestionStatus.REMOVED
                question.moderation_notes = f"Rejected: {reason}"
                success_count += 1
            else:
                failure_count += 1
                errors.append({"id": question_id, "error": "Not found"})
        except Exception as e:
            failure_count += 1
            errors.append({"id": question_id, "error": str(e)})

    db.commit()

    return BulkOperationResult(
        success_count=success_count,
        failure_count=failure_count,
        errors=errors,
    )


@router.get("/questions/{question_id}/duplicates")
async def find_duplicates(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Find potential duplicate questions using simple text matching"""

    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Simple duplicate detection: find questions in same contest with similar text
    # In production, you'd use more sophisticated text similarity algorithms
    duplicates = db.query(Question).filter(
        Question.contest_id == question.contest_id,
        Question.id != question_id,
        Question.status != QuestionStatus.REMOVED,
    ).limit(10).all()

    return duplicates


# ============================================================================
# User Management
# ============================================================================

@router.get("/users")
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get users with filtering and pagination"""

    offset = (page - 1) * page_size

    query = db.query(User)

    if role:
        query = query.filter(User.role == role)

    if status:
        if status == "active":
            query = query.filter(User.is_active == True)
        elif status == "inactive":
            query = query.filter(User.is_active == False)

    if search:
        query = query.filter(
            or_(
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%"),
            )
        )

    total = query.count()
    users = query.offset(offset).limit(page_size).all()

    # Enhance with activity data
    items = []
    for user in users:
        questions_count = db.query(func.count(Question.id)).filter(Question.author_id == user.id).scalar()
        votes_count = db.query(func.count(Vote.id)).filter(Vote.user_id == user.id).scalar()
        reports_count = db.query(func.count(Report.id)).filter(Report.reporter_id == user.id).scalar()

        items.append({
            "user": user,
            "questions_submitted": questions_count or 0,
            "votes_cast": votes_count or 0,
            "reports_filed": reports_count or 0,
            "warnings": 0,  # Would need separate warnings tracking
            "account_status": "active" if user.is_active else "inactive",
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


# Moderation endpoint stubs would continue...

