# CivicQ Email System - Quick Reference

Fast lookup for common email operations.

## Quick Start

### 1. Send Email Synchronously

```python
from app.services.email_service import email_service

result = email_service.send_verification_email(
    to_email="user@example.com",
    verification_token="abc123",
    user_name="John Doe"
)
```

### 2. Send Email Asynchronously (Recommended)

```python
from app.tasks.email_tasks import send_verification_email_task

send_verification_email_task.delay(
    to_email="user@example.com",
    verification_token="abc123",
    user_name="John Doe"
)
```

### 3. Send Batch Emails

```python
from app.tasks.email_tasks import send_batch_emails_task

recipients = [
    {"to_email": "user1@example.com", "user_name": "User 1", ...},
    {"to_email": "user2@example.com", "user_name": "User 2", ...}
]

send_batch_emails_task.delay(
    email_type="weekly_voter_digest",
    recipients=recipients
)
```

---

## All Email Types

### Authentication Emails

```python
from app.tasks.email_tasks import *

# Email verification
send_verification_email_task.delay(to_email, verification_token, user_name)

# Password reset
send_password_reset_email_task.delay(to_email, reset_token, user_name)

# 2FA code
send_2fa_code_email_task.delay(to_email, code, user_name)

# Welcome email
send_welcome_email_task.delay(to_email, user_name)

# Password changed
send_password_changed_email_task.delay(to_email, user_name)
```

### Question Workflow Emails

```python
# Question submitted
send_question_submitted_email_task.delay(
    to_email, user_name, candidate_name, category, question_text, question_url
)

# Question approved
send_question_approved_email_task.delay(
    to_email, user_name, candidate_name, category, question_text, question_url, city_name
)

# Question rejected
send_question_rejected_email_task.delay(
    to_email, user_name, candidate_name, question_text, rejection_reason, submit_question_url
)

# Candidate answered
send_candidate_answered_email_task.delay(
    to_email, user_name, candidate_name, question_text, answer_text, answer_url, has_video
)

# New question for candidate
send_new_question_to_candidate_task.delay(
    to_email, candidate_name, city_name, category, question_text, answer_url,
    upvote_count, priority_level, max_video_length
)
```

### Moderation Emails

```python
# Content flagged (to moderator)
send_content_flagged_to_moderator_task.delay(
    to_email, moderator_name, content_type, author_name, author_email,
    flag_reason, content_text, moderation_url, report_count, ai_toxicity_score
)

# Content removed (to user)
send_content_removed_email_task.delay(
    to_email, user_name, content_type, removal_reason, content_text,
    removal_date, violation_details, guidelines_url, is_first_violation, is_second_violation
)

# User warning
send_user_warning_email_task.delay(
    to_email, user_name, warning_level, warning_reason, warning_date,
    violation_description, content_text, guidelines_url
)

# User suspended
send_user_suspended_email_task.delay(
    to_email, user_name, suspension_duration, suspension_end_date,
    suspension_reason, violation_details, guidelines_url, previous_warnings
)

# User banned
send_user_banned_email_task.delay(
    to_email, user_name, ban_date, ban_reason, violation_details, violation_history
)
```

### City/Admin Emails

```python
# City registration (to admin)
send_city_registration_to_admin_task.delay(
    to_email, city_name, state, county, population, registration_date,
    official_name, official_title, official_email, official_phone, department,
    admin_review_url, upcoming_elections, notes
)

# City verified
send_city_verified_email_task.delay(
    to_email, official_name, city_name, state, admin_dashboard_url,
    admin_guide_url, tutorials_url, training_url
)

# City rejected
send_city_rejected_email_task.delay(
    to_email, official_name, city_name, rejection_reason,
    detailed_requirements, requirements, resubmit_url
)

# Staff invitation
send_staff_invitation_email_task.delay(
    to_email, staff_name, city_name, state, staff_role,
    inviter_name, inviter_title, inviter_email, accept_invitation_url
)

# Weekly city digest
send_weekly_city_digest_email_task.delay(
    to_email, staff_name, city_name, state, week_start_date, week_end_date,
    new_questions, new_answers, new_voters, total_votes, active_candidates,
    top_questions, dashboard_url, moderation_url, analytics_url, settings_url,
    unsubscribe_url, pending_moderation, unanswered_questions, upcoming_elections,
    add_election_url, questions_trend, answers_trend, voters_trend, engagement_trend
)
```

### Candidate Emails

```python
# Verification request
send_candidate_verification_request_email_task.delay(
    to_email, candidate_name, position, election_name, city_name, state,
    election_date, verification_url, candidate_guide_url, faq_url
)

# Candidate verified
send_candidate_verified_email_task.delay(
    to_email, candidate_name, position, city_name, state, election_date,
    profile_url, dashboard_url, candidate_guide_url, video_guide_url, promote_url
)

# Unanswered questions reminder
send_unanswered_questions_reminder_email_task.delay(
    to_email, candidate_name, city_name, unanswered_count, top_questions,
    answer_questions_url, election_date, days_until_election,
    candidate_guide_url, video_guide_url, notification_settings_url
)

# Video upload success
send_video_upload_success_email_task.delay(
    to_email, candidate_name, question_text, video_duration, answer_url,
    transcription_available, transcription_text, edit_transcription_url,
    remaining_questions, answer_questions_url
)

# Video processing failed
send_video_processing_failed_email_task.delay(
    to_email, candidate_name, question_text, upload_date, error_reason,
    retry_upload_url, text_answer_url, video_guide_url, max_video_duration,
    error_code, upload_id, error_timestamp
)
```

### System Emails

```python
# Weekly voter digest
send_weekly_voter_digest_email_task.delay(
    to_email, user_name, city_name, week_start_date, week_end_date,
    new_answers, trending_questions, upcoming_elections,
    user_questions_count, user_votes_count, user_answers_received,
    total_questions, total_answers, total_voters, engagement_rate,
    days_until_next_election, ask_question_url, browse_questions_url,
    browse_candidates_url, upvote_questions_url, share_url,
    unsubscribe_url, email_preferences_url
)

# Election reminder (7 days)
send_election_reminder_7days_email_task.delay(
    to_email, user_name, election_name, election_date, city_name, state,
    ballot_items, election_url, voter_registration_url, polling_place_url,
    poll_open_time, poll_close_time, id_required, your_answered_questions,
    positions, all_candidates_url, early_voting_available, early_voting_start,
    early_voting_end, early_voting_hours, early_voting_url, absentee_deadline,
    absentee_url, ask_question_url, browse_questions_url, voter_guide_url, share_url
)

# Election reminder (1 day)
send_election_reminder_1day_email_task.delay(
    to_email, user_name, election_name, election_date, city_name, state,
    polling_place_url, poll_open_time, poll_close_time, polling_location,
    id_required, positions, all_candidates_url, your_answered_questions,
    voter_registration_url, voter_hotline, election_protection_number, voter_rights_url
)

# Email changed notification
send_email_changed_notification_task.delay(
    to_email, user_name, old_email, new_email, change_date,
    security_settings_url, help_url, security_url
)
```

---

## Environment Setup

### Required Variables

```bash
# SendGrid
SENDGRID_API_KEY=SG.your-key
EMAIL_FROM=noreply@civicq.org

# URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

---

## Common Tasks

### Start Celery Worker

```bash
celery -A app.tasks.email_tasks worker --loglevel=info
```

### Start Celery Beat (Scheduled Tasks)

```bash
celery -A app.tasks.email_tasks beat --loglevel=info
```

### Monitor with Flower

```bash
celery -A app.tasks.email_tasks flower --port=5555
# Access at http://localhost:5555
```

### Run Tests

```bash
# All email tests
pytest tests/test_emails.py -v

# Specific test
pytest tests/test_emails.py::TestQuestionWorkflowEmails -v

# With coverage
pytest tests/test_emails.py --cov=app/services --cov=app/tasks
```

### Preview Email Template

```python
from app.services.email_service import email_service

context = {'user_name': 'Test', 'support_email': 'support@civicq.org'}
html = email_service._render_template('base_email.html', context)

with open('preview.html', 'w') as f:
    f.write(html)
```

---

## Troubleshooting

### Check Task Status

```python
result = send_verification_email_task.delay(...)
print(result.state)  # PENDING, STARTED, SUCCESS, FAILURE
```

### Check Rate Limit

```python
from app.services.email_service import EmailRateLimiter

limiter = EmailRateLimiter()
can_send = limiter.check_rate_limit('user@example.com', limit=10, window=3600)
```

### Reset Rate Limit

```python
limiter.reset_rate_limit('user@example.com')
```

### Check Celery Queue

```bash
celery -A app.tasks.email_tasks inspect active
celery -A app.tasks.email_tasks inspect stats
```

### Purge Queue

```bash
celery -A app.tasks.email_tasks purge
```

---

## File Locations

```
app/
├── services/
│   ├── email_service.py              # Base email service
│   ├── email_service_extended.py     # Question & moderation
│   ├── email_service_platform.py     # City & candidate
│   └── email_service_system.py       # System emails
│
├── tasks/
│   └── email_tasks.py                # Celery tasks
│
└── templates/emails/
    ├── base_email.html               # Base template
    ├── Authentication (5 templates)
    ├── Question Workflow (5 templates)
    ├── Moderation (5 templates)
    ├── City/Admin (5 templates)
    ├── Candidate (5 templates)
    └── System (4 templates)

tests/
└── test_emails.py                    # Email tests

EMAIL_SYSTEM.md                       # Full documentation
EMAIL_QUICK_REFERENCE.md              # This file
```

---

## Best Practices

1. **Always use async tasks** for sending emails
2. **Check rate limits** before sending
3. **Validate email addresses** before queuing
4. **Include unsubscribe links** in bulk emails
5. **Test templates** before deploying
6. **Monitor bounce rates** and spam complaints
7. **Use plain text fallbacks** for all emails
8. **Log all email events** for debugging
9. **Handle failures gracefully** with retries
10. **Scale workers** based on email volume

---

## Support

- Full Documentation: `EMAIL_SYSTEM.md`
- Email: support@civicq.org
- GitHub Issues: https://github.com/civicq/backend/issues
