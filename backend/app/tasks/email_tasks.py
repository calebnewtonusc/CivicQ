"""
Email Celery Tasks

Async email sending tasks for all platform email types.
Handles retry logic, error tracking, and delivery monitoring.
"""

from celery import Task, shared_task
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from app.tasks.video_tasks import celery_app
from app.services.email_service import email_service
from app.services.email_service_extended import extended_email_service
from app.services.email_service_platform import platform_email_service
from app.services.email_service_system import system_email_service

logger = logging.getLogger(__name__)


class EmailTask(Task):
    """Base task with error handling and retry logic"""

    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3, 'countdown': 60}
    retry_backoff = True
    retry_jitter = True


# ============================================================================
# AUTHENTICATION EMAILS (from existing email_service)
# ============================================================================

@celery_app.task(base=EmailTask, name="send_verification_email")
def send_verification_email_task(
    to_email: str,
    verification_token: str,
    user_name: Optional[str] = None
) -> Dict[str, Any]:
    """Send email verification link (async)"""
    try:
        result = email_service.send_verification_email(
            to_email=to_email,
            verification_token=verification_token,
            user_name=user_name
        )
        logger.info(f"Verification email sent to {to_email}")
        return result
    except Exception as e:
        logger.error(f"Failed to send verification email to {to_email}: {e}")
        raise


@celery_app.task(base=EmailTask, name="send_password_reset_email")
def send_password_reset_email_task(
    to_email: str,
    reset_token: str,
    user_name: Optional[str] = None
) -> Dict[str, Any]:
    """Send password reset link (async)"""
    try:
        result = email_service.send_password_reset_email(
            to_email=to_email,
            reset_token=reset_token,
            user_name=user_name
        )
        logger.info(f"Password reset email sent to {to_email}")
        return result
    except Exception as e:
        logger.error(f"Failed to send password reset email to {to_email}: {e}")
        raise


@celery_app.task(base=EmailTask, name="send_2fa_code_email")
def send_2fa_code_email_task(
    to_email: str,
    code: str,
    user_name: Optional[str] = None
) -> Dict[str, Any]:
    """Send 2FA verification code (async)"""
    try:
        result = email_service.send_2fa_code_email(
            to_email=to_email,
            code=code,
            user_name=user_name
        )
        logger.info(f"2FA code email sent to {to_email}")
        return result
    except Exception as e:
        logger.error(f"Failed to send 2FA code email to {to_email}: {e}")
        raise


@celery_app.task(base=EmailTask, name="send_welcome_email")
def send_welcome_email_task(
    to_email: str,
    user_name: Optional[str] = None
) -> Dict[str, Any]:
    """Send welcome email (async)"""
    try:
        result = email_service.send_welcome_email(
            to_email=to_email,
            user_name=user_name
        )
        logger.info(f"Welcome email sent to {to_email}")
        return result
    except Exception as e:
        logger.error(f"Failed to send welcome email to {to_email}: {e}")
        raise


@celery_app.task(base=EmailTask, name="send_password_changed_email")
def send_password_changed_email_task(
    to_email: str,
    user_name: Optional[str] = None
) -> Dict[str, Any]:
    """Send password changed notification (async)"""
    try:
        result = email_service.send_password_changed_email(
            to_email=to_email,
            user_name=user_name
        )
        logger.info(f"Password changed email sent to {to_email}")
        return result
    except Exception as e:
        logger.error(f"Failed to send password changed email to {to_email}: {e}")
        raise


# ============================================================================
# QUESTION WORKFLOW EMAILS
# ============================================================================

@celery_app.task(base=EmailTask, name="send_question_submitted_email")
def send_question_submitted_email_task(
    to_email: str,
    user_name: str,
    candidate_name: str,
    category: str,
    question_text: str,
    question_url: str
) -> Dict[str, Any]:
    """Send question submitted confirmation (async)"""
    try:
        result = extended_email_service.send_question_submitted_email(
            to_email=to_email,
            user_name=user_name,
            candidate_name=candidate_name,
            category=category,
            question_text=question_text,
            question_url=question_url
        )
        logger.info(f"Question submitted email sent to {to_email}")
        return result
    except Exception as e:
        logger.error(f"Failed to send question submitted email to {to_email}: {e}")
        raise


@celery_app.task(base=EmailTask, name="send_question_approved_email")
def send_question_approved_email_task(
    to_email: str,
    user_name: str,
    candidate_name: str,
    category: str,
    question_text: str,
    question_url: str,
    city_name: str
) -> Dict[str, Any]:
    """Send question approved notification (async)"""
    try:
        result = extended_email_service.send_question_approved_email(
            to_email=to_email,
            user_name=user_name,
            candidate_name=candidate_name,
            category=category,
            question_text=question_text,
            question_url=question_url,
            city_name=city_name
        )
        logger.info(f"Question approved email sent to {to_email}")
        return result
    except Exception as e:
        logger.error(f"Failed to send question approved email to {to_email}: {e}")
        raise


@celery_app.task(base=EmailTask, name="send_question_rejected_email")
def send_question_rejected_email_task(
    to_email: str,
    user_name: str,
    candidate_name: str,
    question_text: str,
    rejection_reason: str,
    submit_question_url: str
) -> Dict[str, Any]:
    """Send question rejected notification (async)"""
    try:
        result = extended_email_service.send_question_rejected_email(
            to_email=to_email,
            user_name=user_name,
            candidate_name=candidate_name,
            question_text=question_text,
            rejection_reason=rejection_reason,
            submit_question_url=submit_question_url
        )
        logger.info(f"Question rejected email sent to {to_email}")
        return result
    except Exception as e:
        logger.error(f"Failed to send question rejected email to {to_email}: {e}")
        raise


@celery_app.task(base=EmailTask, name="send_candidate_answered_email")
def send_candidate_answered_email_task(
    to_email: str,
    user_name: str,
    candidate_name: str,
    question_text: str,
    answer_text: str,
    answer_url: str,
    has_video: bool = False
) -> Dict[str, Any]:
    """Send notification when candidate answers question (async)"""
    try:
        result = extended_email_service.send_candidate_answered_email(
            to_email=to_email,
            user_name=user_name,
            candidate_name=candidate_name,
            question_text=question_text,
            answer_text=answer_text,
            answer_url=answer_url,
            has_video=has_video
        )
        logger.info(f"Candidate answered email sent to {to_email}")
        return result
    except Exception as e:
        logger.error(f"Failed to send candidate answered email to {to_email}: {e}")
        raise


@celery_app.task(base=EmailTask, name="send_new_question_to_candidate")
def send_new_question_to_candidate_task(
    to_email: str,
    candidate_name: str,
    city_name: str,
    category: str,
    question_text: str,
    answer_url: str,
    upvote_count: int = 0,
    priority_level: Optional[str] = None,
    max_video_length: int = 180
) -> Dict[str, Any]:
    """Send new question notification to candidate (async)"""
    try:
        result = extended_email_service.send_new_question_to_candidate(
            to_email=to_email,
            candidate_name=candidate_name,
            city_name=city_name,
            category=category,
            question_text=question_text,
            answer_url=answer_url,
            upvote_count=upvote_count,
            priority_level=priority_level,
            max_video_length=max_video_length
        )
        logger.info(f"New question notification sent to candidate {to_email}")
        return result
    except Exception as e:
        logger.error(f"Failed to send new question to candidate {to_email}: {e}")
        raise


# ============================================================================
# MODERATION EMAILS
# ============================================================================

@celery_app.task(base=EmailTask, name="send_content_flagged_to_moderator")
def send_content_flagged_to_moderator_task(
    to_email: str,
    moderator_name: str,
    content_type: str,
    author_name: str,
    author_email: str,
    flag_reason: str,
    content_text: str,
    moderation_url: str,
    report_count: int = 1,
    ai_toxicity_score: Optional[float] = None
) -> Dict[str, Any]:
    """Send flagged content notification to moderator (async)"""
    try:
        result = extended_email_service.send_content_flagged_to_moderator(
            to_email=to_email,
            moderator_name=moderator_name,
            content_type=content_type,
            author_name=author_name,
            author_email=author_email,
            flag_reason=flag_reason,
            content_text=content_text,
            moderation_url=moderation_url,
            report_count=report_count,
            ai_toxicity_score=ai_toxicity_score
        )
        logger.info(f"Content flagged email sent to moderator {to_email}")
        return result
    except Exception as e:
        logger.error(f"Failed to send content flagged email to {to_email}: {e}")
        raise


@celery_app.task(base=EmailTask, name="send_content_removed_email")
def send_content_removed_email_task(
    to_email: str,
    user_name: str,
    content_type: str,
    removal_reason: str,
    content_text: str,
    removal_date: str,
    violation_details: str,
    guidelines_url: str,
    is_first_violation: bool = True,
    is_second_violation: bool = False
) -> Dict[str, Any]:
    """Send content removed notification to user (async)"""
    try:
        result = extended_email_service.send_content_removed_email(
            to_email=to_email,
            user_name=user_name,
            content_type=content_type,
            removal_reason=removal_reason,
            content_text=content_text,
            removal_date=removal_date,
            violation_details=violation_details,
            guidelines_url=guidelines_url,
            is_first_violation=is_first_violation,
            is_second_violation=is_second_violation
        )
        logger.info(f"Content removed email sent to {to_email}")
        return result
    except Exception as e:
        logger.error(f"Failed to send content removed email to {to_email}: {e}")
        raise


@celery_app.task(base=EmailTask, name="send_user_warning_email")
def send_user_warning_email_task(
    to_email: str,
    user_name: str,
    warning_level: int,
    warning_reason: str,
    warning_date: str,
    violation_description: str,
    content_text: str,
    guidelines_url: str
) -> Dict[str, Any]:
    """Send warning notification to user (async)"""
    try:
        result = extended_email_service.send_user_warning_email(
            to_email=to_email,
            user_name=user_name,
            warning_level=warning_level,
            warning_reason=warning_reason,
            warning_date=warning_date,
            violation_description=violation_description,
            content_text=content_text,
            guidelines_url=guidelines_url
        )
        logger.info(f"User warning email sent to {to_email}")
        return result
    except Exception as e:
        logger.error(f"Failed to send user warning email to {to_email}: {e}")
        raise


@celery_app.task(base=EmailTask, name="send_user_suspended_email")
def send_user_suspended_email_task(
    to_email: str,
    user_name: str,
    suspension_duration: str,
    suspension_end_date: str,
    suspension_reason: str,
    violation_details: str,
    guidelines_url: str,
    previous_warnings: int = 0
) -> Dict[str, Any]:
    """Send suspension notification to user (async)"""
    try:
        result = extended_email_service.send_user_suspended_email(
            to_email=to_email,
            user_name=user_name,
            suspension_duration=suspension_duration,
            suspension_end_date=suspension_end_date,
            suspension_reason=suspension_reason,
            violation_details=violation_details,
            guidelines_url=guidelines_url,
            previous_warnings=previous_warnings
        )
        logger.info(f"User suspended email sent to {to_email}")
        return result
    except Exception as e:
        logger.error(f"Failed to send user suspended email to {to_email}: {e}")
        raise


@celery_app.task(base=EmailTask, name="send_user_banned_email")
def send_user_banned_email_task(
    to_email: str,
    user_name: str,
    ban_date: str,
    ban_reason: str,
    violation_details: str,
    violation_history: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Send ban notification to user (async)"""
    try:
        result = extended_email_service.send_user_banned_email(
            to_email=to_email,
            user_name=user_name,
            ban_date=ban_date,
            ban_reason=ban_reason,
            violation_details=violation_details,
            violation_history=violation_history
        )
        logger.info(f"User banned email sent to {to_email}")
        return result
    except Exception as e:
        logger.error(f"Failed to send user banned email to {to_email}: {e}")
        raise


# ============================================================================
# CITY / ADMIN EMAILS
# ============================================================================

@celery_app.task(base=EmailTask, name="send_city_registration_to_admin")
def send_city_registration_to_admin_task(**kwargs) -> Dict[str, Any]:
    """Send city registration notification to admin (async)"""
    try:
        result = platform_email_service.send_city_registration_to_admin(**kwargs)
        logger.info(f"City registration email sent to admin {kwargs.get('to_email')}")
        return result
    except Exception as e:
        logger.error(f"Failed to send city registration email: {e}")
        raise


@celery_app.task(base=EmailTask, name="send_city_verified_email")
def send_city_verified_email_task(**kwargs) -> Dict[str, Any]:
    """Send city verified notification (async)"""
    try:
        result = platform_email_service.send_city_verified_email(**kwargs)
        logger.info(f"City verified email sent to {kwargs.get('to_email')}")
        return result
    except Exception as e:
        logger.error(f"Failed to send city verified email: {e}")
        raise


@celery_app.task(base=EmailTask, name="send_city_rejected_email")
def send_city_rejected_email_task(**kwargs) -> Dict[str, Any]:
    """Send city registration rejection notification (async)"""
    try:
        result = platform_email_service.send_city_rejected_email(**kwargs)
        logger.info(f"City rejected email sent to {kwargs.get('to_email')}")
        return result
    except Exception as e:
        logger.error(f"Failed to send city rejected email: {e}")
        raise


@celery_app.task(base=EmailTask, name="send_staff_invitation_email")
def send_staff_invitation_email_task(**kwargs) -> Dict[str, Any]:
    """Send staff invitation email (async)"""
    try:
        result = platform_email_service.send_staff_invitation_email(**kwargs)
        logger.info(f"Staff invitation sent to {kwargs.get('to_email')}")
        return result
    except Exception as e:
        logger.error(f"Failed to send staff invitation: {e}")
        raise


@celery_app.task(base=EmailTask, name="send_weekly_city_digest_email")
def send_weekly_city_digest_email_task(**kwargs) -> Dict[str, Any]:
    """Send weekly city digest to staff (async)"""
    try:
        result = platform_email_service.send_weekly_city_digest_email(**kwargs)
        logger.info(f"Weekly city digest sent to {kwargs.get('to_email')}")
        return result
    except Exception as e:
        logger.error(f"Failed to send weekly city digest: {e}")
        raise


# ============================================================================
# CANDIDATE EMAILS
# ============================================================================

@celery_app.task(base=EmailTask, name="send_candidate_verification_request_email")
def send_candidate_verification_request_email_task(**kwargs) -> Dict[str, Any]:
    """Send candidate verification request (async)"""
    try:
        result = platform_email_service.send_candidate_verification_request_email(**kwargs)
        logger.info(f"Candidate verification request sent to {kwargs.get('to_email')}")
        return result
    except Exception as e:
        logger.error(f"Failed to send candidate verification request: {e}")
        raise


@celery_app.task(base=EmailTask, name="send_candidate_verified_email")
def send_candidate_verified_email_task(**kwargs) -> Dict[str, Any]:
    """Send candidate verified notification (async)"""
    try:
        result = platform_email_service.send_candidate_verified_email(**kwargs)
        logger.info(f"Candidate verified email sent to {kwargs.get('to_email')}")
        return result
    except Exception as e:
        logger.error(f"Failed to send candidate verified email: {e}")
        raise


@celery_app.task(base=EmailTask, name="send_unanswered_questions_reminder_email")
def send_unanswered_questions_reminder_email_task(**kwargs) -> Dict[str, Any]:
    """Send unanswered questions reminder to candidate (async)"""
    try:
        result = platform_email_service.send_unanswered_questions_reminder_email(**kwargs)
        logger.info(f"Unanswered questions reminder sent to {kwargs.get('to_email')}")
        return result
    except Exception as e:
        logger.error(f"Failed to send unanswered questions reminder: {e}")
        raise


@celery_app.task(base=EmailTask, name="send_video_upload_success_email")
def send_video_upload_success_email_task(**kwargs) -> Dict[str, Any]:
    """Send video upload success notification (async)"""
    try:
        result = platform_email_service.send_video_upload_success_email(**kwargs)
        logger.info(f"Video upload success email sent to {kwargs.get('to_email')}")
        return result
    except Exception as e:
        logger.error(f"Failed to send video upload success email: {e}")
        raise


@celery_app.task(base=EmailTask, name="send_video_processing_failed_email")
def send_video_processing_failed_email_task(**kwargs) -> Dict[str, Any]:
    """Send video processing failed notification (async)"""
    try:
        result = platform_email_service.send_video_processing_failed_email(**kwargs)
        logger.info(f"Video processing failed email sent to {kwargs.get('to_email')}")
        return result
    except Exception as e:
        logger.error(f"Failed to send video processing failed email: {e}")
        raise


# ============================================================================
# SYSTEM EMAILS
# ============================================================================

@celery_app.task(base=EmailTask, name="send_weekly_voter_digest_email")
def send_weekly_voter_digest_email_task(**kwargs) -> Dict[str, Any]:
    """Send weekly voter digest (async)"""
    try:
        result = system_email_service.send_weekly_voter_digest_email(**kwargs)
        logger.info(f"Weekly voter digest sent to {kwargs.get('to_email')}")
        return result
    except Exception as e:
        logger.error(f"Failed to send weekly voter digest: {e}")
        raise


@celery_app.task(base=EmailTask, name="send_election_reminder_7days_email")
def send_election_reminder_7days_email_task(**kwargs) -> Dict[str, Any]:
    """Send 7-day election reminder (async)"""
    try:
        result = system_email_service.send_election_reminder_7days_email(**kwargs)
        logger.info(f"7-day election reminder sent to {kwargs.get('to_email')}")
        return result
    except Exception as e:
        logger.error(f"Failed to send 7-day election reminder: {e}")
        raise


@celery_app.task(base=EmailTask, name="send_election_reminder_1day_email")
def send_election_reminder_1day_email_task(**kwargs) -> Dict[str, Any]:
    """Send 1-day election reminder (async)"""
    try:
        result = system_email_service.send_election_reminder_1day_email(**kwargs)
        logger.info(f"1-day election reminder sent to {kwargs.get('to_email')}")
        return result
    except Exception as e:
        logger.error(f"Failed to send 1-day election reminder: {e}")
        raise


@celery_app.task(base=EmailTask, name="send_email_changed_notification")
def send_email_changed_notification_task(**kwargs) -> Dict[str, Any]:
    """Send email changed notification (async)"""
    try:
        result = system_email_service.send_email_changed_notification(**kwargs)
        logger.info(f"Email changed notification sent to {kwargs.get('to_email')}")
        return result
    except Exception as e:
        logger.error(f"Failed to send email changed notification: {e}")
        raise


# ============================================================================
# BATCH EMAIL TASKS
# ============================================================================

@celery_app.task(base=EmailTask, name="send_batch_emails")
def send_batch_emails_task(
    email_type: str,
    recipients: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Send emails to multiple recipients in batch

    Args:
        email_type: Type of email to send (matches task name)
        recipients: List of dicts with recipient email and context data

    Returns:
        Summary of batch send results
    """
    results = {
        'total': len(recipients),
        'sent': 0,
        'failed': 0,
        'errors': []
    }

    for recipient_data in recipients:
        try:
            # Get the appropriate task
            task_name = f"send_{email_type}_email"
            task = celery_app.tasks.get(task_name)

            if not task:
                raise ValueError(f"Unknown email type: {email_type}")

            # Send email
            task.apply_async(kwargs=recipient_data)
            results['sent'] += 1

        except Exception as e:
            logger.error(f"Failed to queue email for {recipient_data.get('to_email')}: {e}")
            results['failed'] += 1
            results['errors'].append({
                'recipient': recipient_data.get('to_email'),
                'error': str(e)
            })

    logger.info(f"Batch email send complete: {results['sent']}/{results['total']} sent")
    return results
