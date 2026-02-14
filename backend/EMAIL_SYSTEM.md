# CivicQ Email System Documentation

Complete production-grade email system with 24 transactional email templates, SendGrid integration, async task processing, and comprehensive testing.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Email Templates](#email-templates)
4. [Service Layer](#service-layer)
5. [Async Tasks](#async-tasks)
6. [Configuration](#configuration)
7. [Testing](#testing)
8. [Production Deployment](#production-deployment)
9. [Monitoring](#monitoring)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The CivicQ email system provides production-ready transactional email functionality for all platform operations:

- **24 Professional Email Templates** - Mobile-responsive HTML emails with plain-text fallbacks
- **SendGrid Integration** - Production email delivery with retry logic and tracking
- **Async Processing** - Celery-based background task processing
- **Rate Limiting** - Redis-backed rate limiting to prevent abuse
- **Comprehensive Testing** - Unit and integration tests for all email types
- **Development Mode** - Email logging for development without sending

### Email Categories

1. **Authentication** (5 emails)
   - Email verification
   - Password reset
   - 2FA codes
   - Welcome email
   - Password changed notification

2. **Question Workflow** (5 emails)
   - Question submitted
   - Question approved
   - Question rejected
   - Candidate answered
   - New question for candidate

3. **Moderation** (5 emails)
   - Content flagged (to moderator)
   - Content removed (to user)
   - User warning
   - Account suspension
   - Account ban

4. **City/Admin** (5 emails)
   - City registration (to admin)
   - City verified
   - City rejected
   - Staff invitation
   - Weekly city digest

5. **Candidate** (5 emails)
   - Verification request
   - Candidate verified
   - Unanswered questions reminder
   - Video upload success
   - Video processing failed

6. **System** (4 emails)
   - Weekly voter digest
   - Election reminder (7 days)
   - Election reminder (1 day)
   - Email changed notification

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Email System Architecture                │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   API Route  │────────▶│ Email Service │────────▶│ Celery Task  │
│              │         │   Methods     │         │   Queue      │
└──────────────┘         └──────────────┘         └──────────────┘
                                │                         │
                                │                         ▼
                                │                  ┌──────────────┐
                                │                  │ Celery Worker│
                                │                  └──────────────┘
                                ▼                         │
                         ┌──────────────┐                │
                         │   Jinja2     │                │
                         │  Templates   │                │
                         └──────────────┘                │
                                │                         │
                                ▼                         ▼
                         ┌──────────────┐         ┌──────────────┐
                         │    HTML      │         │   SendGrid   │
                         │   Rendering  │         │     API      │
                         └──────────────┘         └──────────────┘
                                │                         │
                                └────────┬────────────────┘
                                         ▼
                                  ┌──────────────┐
                                  │ Email Sent to│
                                  │  Recipient   │
                                  └──────────────┘
```

### Components

#### 1. Email Service (`app/services/email_service.py`)
- Core email sending functionality
- Template rendering with Jinja2
- SendGrid client management
- Rate limiting
- Retry logic

#### 2. Extended Services
- `email_service_extended.py` - Question workflow & moderation emails
- `email_service_platform.py` - City/admin & candidate emails
- `email_service_system.py` - System & digest emails

#### 3. Celery Tasks (`app/tasks/email_tasks.py`)
- Async email task definitions
- Background processing
- Error handling and retries
- Batch email support

#### 4. Email Templates (`app/templates/emails/`)
- Base template with branding
- Individual templates for each email type
- Mobile-responsive design
- Plain-text fallbacks

---

## Email Templates

### Template Structure

All email templates extend `base_email.html` for consistent branding:

```jinja2
{% extends "base_email.html" %}

{% block title %}Email Title{% endblock %}

{% block content %}
<!-- Email-specific content -->
{% endblock %}
```

### Base Template Features

- **Professional Branding** - CivicQ gradient header
- **Mobile Responsive** - Works on all devices
- **Consistent Styling** - Buttons, dividers, warning boxes
- **Footer** - Support contact, unsubscribe links
- **Accessibility** - Proper semantic HTML

### Template Locations

```
app/templates/emails/
├── base_email.html                    # Base template
│
├── Authentication Emails
├── verification_email.html
├── password_reset.html
├── 2fa_code.html
├── welcome_email.html
├── password_changed.html
│
├── Question Workflow Emails
├── question_submitted.html
├── question_approved.html
├── question_rejected.html
├── candidate_answered.html
├── new_question_for_candidate.html
│
├── Moderation Emails
├── content_flagged_moderator.html
├── content_removed.html
├── user_warning.html
├── user_suspended.html
├── user_banned.html
│
├── City/Admin Emails
├── city_registration_admin.html
├── city_verified.html
├── city_rejected.html
├── staff_invitation.html
├── weekly_city_digest.html
│
├── Candidate Emails
├── candidate_verification_request.html
├── candidate_verified.html
├── unanswered_questions_reminder.html
├── video_upload_success.html
├── video_processing_failed.html
│
└── System Emails
    ├── weekly_voter_digest.html
    ├── election_reminder_7days.html
    ├── election_reminder_1day.html
    └── email_changed.html
```

---

## Service Layer

### Base Email Service

```python
from app.services.email_service import email_service

# Send verification email
email_service.send_verification_email(
    to_email="user@example.com",
    verification_token="abc123",
    user_name="John Doe"
)

# Send password reset
email_service.send_password_reset_email(
    to_email="user@example.com",
    reset_token="xyz789",
    user_name="John Doe"
)
```

### Question Workflow Emails

```python
from app.services.email_service_extended import extended_email_service

# Question submitted
extended_email_service.send_question_submitted_email(
    to_email="voter@example.com",
    user_name="Jane Voter",
    candidate_name="John Candidate",
    category="Education",
    question_text="What is your plan for schools?",
    question_url="https://civicq.org/questions/123"
)

# Candidate answered
extended_email_service.send_candidate_answered_email(
    to_email="voter@example.com",
    user_name="Jane Voter",
    candidate_name="John Candidate",
    question_text="What is your plan for schools?",
    answer_text="Here is my detailed plan...",
    answer_url="https://civicq.org/answers/123",
    has_video=True
)
```

### City/Admin Emails

```python
from app.services.email_service_platform import platform_email_service

# City verified
platform_email_service.send_city_verified_email(
    to_email="admin@springfield.gov",
    official_name="Jane Smith",
    city_name="Springfield",
    state="IL",
    admin_dashboard_url="https://civicq.org/admin",
    admin_guide_url="https://civicq.org/guide",
    tutorials_url="https://civicq.org/tutorials",
    training_url="https://civicq.org/training"
)

# Staff invitation
platform_email_service.send_staff_invitation_email(
    to_email="staff@springfield.gov",
    staff_name="Bob Johnson",
    city_name="Springfield",
    state="IL",
    staff_role="Moderator",
    inviter_name="Jane Smith",
    inviter_title="City Clerk",
    inviter_email="jane@springfield.gov",
    accept_invitation_url="https://civicq.org/invite/abc123"
)
```

### System Emails

```python
from app.services.email_service_system import system_email_service

# Weekly voter digest
system_email_service.send_weekly_voter_digest_email(
    to_email="voter@example.com",
    user_name="Jane Voter",
    city_name="Springfield",
    week_start_date="2026-02-10",
    week_end_date="2026-02-16",
    new_answers=[...],
    trending_questions=[...],
    user_questions_count=3,
    user_votes_count=15,
    ask_question_url="https://civicq.org/ask"
)

# Election reminder (1 day)
system_email_service.send_election_reminder_1day_email(
    to_email="voter@example.com",
    user_name="Jane Voter",
    election_name="Springfield General Election",
    election_date="2026-11-03",
    city_name="Springfield",
    state="IL",
    polling_place_url="https://votespringfield.gov",
    poll_open_time="7:00 AM",
    poll_close_time="8:00 PM"
)
```

---

## Async Tasks

All emails can be sent asynchronously using Celery tasks:

### Basic Usage

```python
from app.tasks.email_tasks import (
    send_verification_email_task,
    send_question_submitted_email_task,
    send_candidate_answered_email_task
)

# Queue email for async sending
send_verification_email_task.delay(
    to_email="user@example.com",
    verification_token="abc123",
    user_name="John Doe"
)

# Queue with custom retry
send_question_submitted_email_task.apply_async(
    kwargs={
        "to_email": "voter@example.com",
        "user_name": "Jane",
        # ... other params
    },
    retry=True,
    retry_policy={
        'max_retries': 3,
        'interval_start': 0,
        'interval_step': 60,
    }
)
```

### Batch Emails

```python
from app.tasks.email_tasks import send_batch_emails_task

# Send emails to multiple recipients
recipients = [
    {
        "to_email": "voter1@example.com",
        "user_name": "Voter 1",
        # ... other params
    },
    {
        "to_email": "voter2@example.com",
        "user_name": "Voter 2",
        # ... other params
    }
]

result = send_batch_emails_task.delay(
    email_type="weekly_voter_digest",
    recipients=recipients
)
```

### Task Monitoring

```python
# Check task status
result = send_verification_email_task.delay(...)
print(result.state)  # PENDING, STARTED, SUCCESS, FAILURE

# Get result
if result.ready():
    email_result = result.get()
    print(email_result)  # {'success': True, 'message_id': '...'}
```

---

## Configuration

### Environment Variables

Required in `.env`:

```bash
# SendGrid (Production)
SENDGRID_API_KEY=SG.your-sendgrid-api-key
EMAIL_FROM=noreply@civicq.org

# Alternative: SMTP (Development)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# URLs for email links
FRONTEND_URL=https://civicq.org
BACKEND_URL=https://api.civicq.org

# Redis for rate limiting
REDIS_URL=redis://localhost:6379/0

# Celery for async tasks
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

### SendGrid Setup

1. **Create SendGrid Account**
   - Sign up at https://sendgrid.com/
   - Verify your sender domain

2. **Generate API Key**
   - Go to Settings > API Keys
   - Create key with "Mail Send" permission
   - Copy key to `SENDGRID_API_KEY`

3. **Verify Sender**
   - Go to Settings > Sender Authentication
   - Verify your domain or single sender email
   - Set as `EMAIL_FROM`

4. **Configure Webhooks** (Optional)
   - Set up event webhooks for delivery tracking
   - Track opens, clicks, bounces, spam reports

### Rate Limiting

Email rate limiting prevents abuse:

```python
from app.services.email_service import EmailRateLimiter

limiter = EmailRateLimiter()

# Check if user can send email (10 emails per hour)
if limiter.check_rate_limit('user@example.com', limit=10, window=3600):
    # Send email
    pass
else:
    # Rate limit exceeded
    raise Exception("Too many emails")
```

Default limits:
- **10 emails per hour** per user
- **Configurable** via `check_rate_limit()` parameters

---

## Testing

### Running Tests

```bash
# Run all email tests
pytest tests/test_emails.py -v

# Run specific test class
pytest tests/test_emails.py::TestQuestionWorkflowEmails -v

# Run with coverage
pytest tests/test_emails.py --cov=app/services --cov=app/tasks

# Run integration tests (requires live services)
pytest tests/test_emails.py -m integration
```

### Test Email Locally

```python
# Development mode - emails are logged, not sent
from app.services.email_service import email_service

result = email_service.send_verification_email(
    to_email="test@example.com",
    verification_token="test-token"
)

# Check logs for email content
# [INFO] [DEV MODE] Email to test@example.com: Verify Your CivicQ Email Address
```

### Preview Email Templates

Create a preview script (`scripts/preview_email.py`):

```python
from app.services.email_service import email_service

context = {
    'user_name': 'John Doe',
    'candidate_name': 'Jane Candidate',
    'question_text': 'What is your plan for education?',
    'question_url': 'https://civicq.org/questions/123',
    'support_email': 'support@civicq.org'
}

html = email_service._render_template('question_submitted.html', context)

# Save to file for browser preview
with open('preview.html', 'w') as f:
    f.write(html)

print("Preview saved to preview.html")
```

### Manual Email Testing

```python
# Send test email to yourself
from app.tasks.email_tasks import send_verification_email_task

send_verification_email_task.delay(
    to_email="your-email@example.com",
    verification_token="test-token-123",
    user_name="Test User"
)

# Check your inbox for the email
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] **SendGrid Configured**
  - API key set in environment
  - Sender domain verified
  - Email templates tested

- [ ] **Redis Available**
  - Redis instance running
  - Connection tested
  - Rate limiting working

- [ ] **Celery Workers Running**
  - Celery workers started
  - Task queue functional
  - Monitoring configured

- [ ] **Environment Variables Set**
  - All required vars configured
  - Production URLs updated
  - Secrets secured

- [ ] **Templates Customized**
  - Branding updated
  - Support email set
  - Legal disclaimers added

### Deployment Steps

#### 1. Configure SendGrid

```bash
# Set production API key
export SENDGRID_API_KEY="SG.production-key"
export EMAIL_FROM="noreply@civicq.org"
```

#### 2. Start Celery Workers

```bash
# Start Celery worker for email tasks
celery -A app.tasks.email_tasks worker \
    --loglevel=info \
    --concurrency=4 \
    --queue=email

# Start Celery beat for scheduled emails
celery -A app.tasks.email_tasks beat \
    --loglevel=info
```

#### 3. Configure Monitoring

```python
# Add Sentry for error tracking
SENTRY_DSN=your-sentry-dsn

# Monitor Celery with Flower
celery -A app.tasks.email_tasks flower \
    --port=5555 \
    --broker=redis://localhost:6379/1
```

#### 4. Set Up Email Webhooks

Configure SendGrid webhooks to track:
- Email delivered
- Email opened
- Email clicked
- Email bounced
- Spam reports

Webhook endpoint: `https://api.civicq.org/api/webhooks/sendgrid`

### Scaling

**Horizontal Scaling:**
```bash
# Run multiple Celery workers
celery -A app.tasks.email_tasks worker --concurrency=10 --autoscale=10,3
```

**Queue Separation:**
```bash
# Separate queues for priority
celery worker --queues=email_high,email_normal,email_low
```

**Rate Limiting:**
```python
# Adjust rate limits for production
RATE_LIMIT_QUESTIONS_PER_DAY=10
RATE_LIMIT_VOTES_PER_HOUR=100
```

---

## Monitoring

### Key Metrics

1. **Email Delivery Rate**
   - Track successful sends vs failures
   - Monitor bounce rate
   - Track spam complaints

2. **Task Queue Health**
   - Queue length
   - Processing time
   - Failed tasks
   - Worker utilization

3. **Rate Limiting**
   - Rate limit hits
   - Blocked users
   - Email volume trends

### Monitoring Tools

#### Celery Flower

```bash
# Start Flower dashboard
celery -A app.tasks.email_tasks flower --port=5555

# Access at http://localhost:5555
```

Features:
- Real-time task monitoring
- Worker status
- Task history
- Rate statistics

#### SendGrid Analytics

Access via SendGrid dashboard:
- Delivery statistics
- Open/click rates
- Geographic data
- Device breakdown

#### Custom Logging

```python
import logging

logger = logging.getLogger(__name__)

# Log email events
logger.info(f"Email sent to {to_email}: {subject}")
logger.warning(f"Email rate limit exceeded for {email}")
logger.error(f"Email send failed: {error}")
```

### Alerts

Set up alerts for:
- **High bounce rate** (> 5%)
- **Spam complaints** (> 0.1%)
- **Queue backlog** (> 1000 tasks)
- **Worker failures**
- **Rate limit abuse**

---

## Troubleshooting

### Common Issues

#### 1. Emails Not Sending

**Symptoms:** Emails queued but not delivered

**Diagnosis:**
```bash
# Check Celery workers
celery -A app.tasks.email_tasks inspect active

# Check task status
celery -A app.tasks.email_tasks inspect stats

# Check logs
tail -f logs/celery.log
```

**Solutions:**
- Verify SendGrid API key
- Check worker status
- Review rate limits
- Check Redis connection

#### 2. Template Rendering Errors

**Symptoms:** `TemplateNotFound` or rendering errors

**Diagnosis:**
```python
# Test template manually
from app.services.email_service import email_service

try:
    html = email_service._render_template('test.html', {})
except Exception as e:
    print(f"Template error: {e}")
```

**Solutions:**
- Verify template exists in `app/templates/emails/`
- Check template syntax
- Verify context variables
- Check Jinja2 configuration

#### 3. Rate Limiting Issues

**Symptoms:** Users blocked from sending emails

**Diagnosis:**
```python
# Check rate limit status
from app.services.email_service import EmailRateLimiter

limiter = EmailRateLimiter()
redis_client = limiter.redis_client
count = redis_client.get('email_rate:user@example.com')
print(f"Current count: {count}")
```

**Solutions:**
- Increase rate limits
- Reset user limits manually
- Check Redis connection
- Review rate limit logic

#### 4. SendGrid Errors

**Common Error Codes:**
- `400` - Bad request (check email format)
- `401` - Invalid API key
- `403` - Forbidden (sender not verified)
- `429` - Rate limit exceeded
- `500` - SendGrid server error

**Solutions:**
```python
# Enable detailed error logging
import logging
logging.getLogger('sendgrid').setLevel(logging.DEBUG)

# Check SendGrid status
# https://status.sendgrid.com/
```

#### 5. Celery Task Failures

**Symptoms:** Tasks fail repeatedly

**Diagnosis:**
```bash
# Check failed tasks
celery -A app.tasks.email_tasks inspect failed

# Purge failed tasks
celery -A app.tasks.email_tasks purge
```

**Solutions:**
- Review task error logs
- Increase retry attempts
- Fix underlying issue
- Restart workers

### Debug Mode

Enable debug logging:

```python
# In app/core/config.py
LOG_LEVEL = "DEBUG"

# Or via environment
export LOG_LEVEL=DEBUG
```

### Support Resources

- **SendGrid Docs:** https://docs.sendgrid.com/
- **Celery Docs:** https://docs.celeryproject.org/
- **Jinja2 Docs:** https://jinja.palletsprojects.com/
- **CivicQ Support:** support@civicq.org

---

## Best Practices

### Email Design

1. **Keep it Simple** - Clear subject lines, concise content
2. **Mobile First** - 50%+ of emails opened on mobile
3. **Clear CTAs** - Prominent action buttons
4. **Plain Text** - Always include plain-text version
5. **Unsubscribe** - Include opt-out links (required by law)

### Sending

1. **Async by Default** - Use Celery tasks for all emails
2. **Rate Limit** - Prevent abuse with rate limiting
3. **Retry Logic** - Handle temporary failures gracefully
4. **Track Deliverability** - Monitor bounce/spam rates
5. **Test Thoroughly** - Test all templates before production

### Security

1. **Validate Emails** - Sanitize email addresses
2. **Secure Tokens** - Use cryptographically secure tokens
3. **Rate Limiting** - Prevent email bombing
4. **HTTPS Links** - Only include HTTPS links in emails
5. **SPF/DKIM** - Configure email authentication

### Performance

1. **Batch Sends** - Use batch tasks for bulk emails
2. **Queue Priority** - Prioritize critical emails
3. **Worker Scaling** - Scale workers based on load
4. **Template Caching** - Cache compiled templates
5. **Connection Pooling** - Reuse SendGrid connections

---

## API Reference

### Email Service Classes

```python
# Base email service
from app.services.email_service import email_service

# Extended services
from app.services.email_service_extended import extended_email_service
from app.services.email_service_platform import platform_email_service
from app.services.email_service_system import system_email_service

# Rate limiter
from app.services.email_service import EmailRateLimiter
```

### Celery Tasks

```python
from app.tasks.email_tasks import (
    # Authentication
    send_verification_email_task,
    send_password_reset_email_task,
    send_2fa_code_email_task,
    send_welcome_email_task,
    send_password_changed_email_task,

    # Question Workflow
    send_question_submitted_email_task,
    send_question_approved_email_task,
    send_question_rejected_email_task,
    send_candidate_answered_email_task,
    send_new_question_to_candidate_task,

    # Moderation
    send_content_flagged_to_moderator_task,
    send_content_removed_email_task,
    send_user_warning_email_task,
    send_user_suspended_email_task,
    send_user_banned_email_task,

    # City/Admin
    send_city_registration_to_admin_task,
    send_city_verified_email_task,
    send_city_rejected_email_task,
    send_staff_invitation_email_task,
    send_weekly_city_digest_email_task,

    # Candidate
    send_candidate_verification_request_email_task,
    send_candidate_verified_email_task,
    send_unanswered_questions_reminder_email_task,
    send_video_upload_success_email_task,
    send_video_processing_failed_email_task,

    # System
    send_weekly_voter_digest_email_task,
    send_election_reminder_7days_email_task,
    send_election_reminder_1day_email_task,
    send_email_changed_notification_task,

    # Batch
    send_batch_emails_task
)
```

---

## Changelog

### Version 1.0.0 (2026-02-14)

Initial release with complete email system:

- 24 professional email templates
- SendGrid integration
- Celery async task processing
- Rate limiting with Redis
- Comprehensive testing
- Full documentation

---

## License

Copyright 2026 CivicQ. All rights reserved.

---

## Contact

For questions or support:
- Email: support@civicq.org
- Documentation: https://docs.civicq.org
- GitHub: https://github.com/civicq/backend
