"""
Email Service Tests

Comprehensive tests for all email functionality including templates,
sending, and Celery task integration.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from app.services.email_service import email_service, EmailRateLimiter
from app.services.email_service_extended import extended_email_service
from app.services.email_service_platform import platform_email_service
from app.services.email_service_system import system_email_service
from app.tasks.email_tasks import (
    send_verification_email_task,
    send_question_submitted_email_task,
    send_candidate_answered_email_task,
    send_weekly_voter_digest_email_task
)


# ============================================================================
# BASE EMAIL SERVICE TESTS
# ============================================================================

class TestEmailService:
    """Test base email service functionality"""

    def test_email_service_initialization(self):
        """Test email service initializes correctly"""
        assert email_service is not None
        assert email_service.jinja_env is not None

    def test_render_template(self):
        """Test template rendering"""
        context = {
            'user_name': 'John Doe',
            'app_name': 'CivicQ',
            'support_email': 'support@civicq.org'
        }

        # Test with existing template
        html = email_service._render_template('base_email.html', context)
        assert html is not None
        assert 'CivicQ' in html

    def test_generate_fallback_html(self):
        """Test fallback HTML generation"""
        context = {
            'user_name': 'John Doe',
            'message': 'Test message'
        }

        html = email_service._generate_fallback_html(context)
        assert 'John Doe' in html
        assert 'Test message' in html

    @patch('app.services.email_service.SendGridAPIClient')
    def test_send_email_success(self, mock_sendgrid):
        """Test successful email sending"""
        # Mock SendGrid response
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.headers = {'X-Message-Id': 'test-message-id'}
        mock_sendgrid.return_value.send.return_value = mock_response

        # Send email
        result = email_service._send_email(
            to_email='test@example.com',
            subject='Test Email',
            html_content='<p>Test content</p>',
            plain_content='Test content'
        )

        assert result['success'] is True
        assert 'message_id' in result

    @patch('app.services.email_service.SendGridAPIClient')
    def test_send_email_retry_on_failure(self, mock_sendgrid):
        """Test email retry logic on failure"""
        # Mock SendGrid to fail then succeed
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500

        mock_response_success = Mock()
        mock_response_success.status_code = 202
        mock_response_success.headers = {'X-Message-Id': 'test-message-id'}

        mock_sendgrid.return_value.send.side_effect = [
            Exception("Network error"),
            mock_response_success
        ]

        result = email_service._send_email(
            to_email='test@example.com',
            subject='Test Email',
            html_content='<p>Test</p>',
            retry_count=2,
            retry_delay=0
        )

        # Should succeed after retry
        assert mock_sendgrid.return_value.send.call_count == 2


class TestEmailRateLimiter:
    """Test email rate limiting"""

    @patch('app.services.email_service.redis.from_url')
    def test_rate_limit_allows_within_limit(self, mock_redis):
        """Test rate limiter allows emails within limit"""
        mock_redis_client = MagicMock()
        mock_redis_client.get.return_value = '5'  # 5 emails sent
        mock_redis.return_value = mock_redis_client

        limiter = EmailRateLimiter()
        limiter.redis_client = mock_redis_client

        # Should allow (under limit of 10)
        result = limiter.check_rate_limit('test@example.com', limit=10)
        assert result is True

    @patch('app.services.email_service.redis.from_url')
    def test_rate_limit_blocks_over_limit(self, mock_redis):
        """Test rate limiter blocks emails over limit"""
        mock_redis_client = MagicMock()
        mock_redis_client.get.return_value = '10'  # 10 emails sent
        mock_redis.return_value = mock_redis_client

        limiter = EmailRateLimiter()
        limiter.redis_client = mock_redis_client

        # Should block (at limit of 10)
        result = limiter.check_rate_limit('test@example.com', limit=10)
        assert result is False


# ============================================================================
# AUTHENTICATION EMAIL TESTS
# ============================================================================

class TestAuthenticationEmails:
    """Test authentication email functionality"""

    @patch.object(email_service, '_send_email')
    def test_send_verification_email(self, mock_send):
        """Test verification email sending"""
        mock_send.return_value = {'success': True, 'message_id': 'test-id'}

        result = email_service.send_verification_email(
            to_email='test@example.com',
            verification_token='test-token-123',
            user_name='John Doe'
        )

        assert mock_send.called
        assert mock_send.call_args[1]['to_email'] == 'test@example.com'
        assert 'Verify' in mock_send.call_args[1]['subject']

    @patch.object(email_service, '_send_email')
    def test_send_password_reset_email(self, mock_send):
        """Test password reset email sending"""
        mock_send.return_value = {'success': True}

        result = email_service.send_password_reset_email(
            to_email='test@example.com',
            reset_token='reset-token-123',
            user_name='John Doe'
        )

        assert mock_send.called
        assert 'Password' in mock_send.call_args[1]['subject']

    @patch.object(email_service, '_send_email')
    def test_send_2fa_code_email(self, mock_send):
        """Test 2FA code email sending"""
        mock_send.return_value = {'success': True}

        result = email_service.send_2fa_code_email(
            to_email='test@example.com',
            code='123456',
            user_name='John Doe'
        )

        assert mock_send.called
        assert '123456' in mock_send.call_args[1]['html_content']


# ============================================================================
# QUESTION WORKFLOW EMAIL TESTS
# ============================================================================

class TestQuestionWorkflowEmails:
    """Test question workflow email functionality"""

    @patch.object(extended_email_service.base, '_send_email')
    def test_send_question_submitted_email(self, mock_send):
        """Test question submitted email"""
        mock_send.return_value = {'success': True}

        result = extended_email_service.send_question_submitted_email(
            to_email='voter@example.com',
            user_name='Jane Voter',
            candidate_name='John Candidate',
            category='Education',
            question_text='What is your plan for schools?',
            question_url='https://civicq.org/questions/123'
        )

        assert mock_send.called
        assert 'submitted' in mock_send.call_args[1]['subject'].lower()

    @patch.object(extended_email_service.base, '_send_email')
    def test_send_question_approved_email(self, mock_send):
        """Test question approved email"""
        mock_send.return_value = {'success': True}

        result = extended_email_service.send_question_approved_email(
            to_email='voter@example.com',
            user_name='Jane Voter',
            candidate_name='John Candidate',
            category='Education',
            question_text='What is your plan for schools?',
            question_url='https://civicq.org/questions/123',
            city_name='Springfield'
        )

        assert mock_send.called
        assert 'approved' in mock_send.call_args[1]['subject'].lower()

    @patch.object(extended_email_service.base, '_send_email')
    def test_send_candidate_answered_email(self, mock_send):
        """Test candidate answered email"""
        mock_send.return_value = {'success': True}

        result = extended_email_service.send_candidate_answered_email(
            to_email='voter@example.com',
            user_name='Jane Voter',
            candidate_name='John Candidate',
            question_text='What is your plan?',
            answer_text='Here is my detailed plan...',
            answer_url='https://civicq.org/answers/123',
            has_video=True
        )

        assert mock_send.called
        assert 'answered' in mock_send.call_args[1]['subject'].lower()


# ============================================================================
# MODERATION EMAIL TESTS
# ============================================================================

class TestModerationEmails:
    """Test moderation email functionality"""

    @patch.object(extended_email_service.base, '_send_email')
    def test_send_content_flagged_to_moderator(self, mock_send):
        """Test content flagged email to moderator"""
        mock_send.return_value = {'success': True}

        result = extended_email_service.send_content_flagged_to_moderator(
            to_email='moderator@civicq.org',
            moderator_name='Mod Name',
            content_type='question',
            author_name='User Name',
            author_email='user@example.com',
            flag_reason='Inappropriate language',
            content_text='Flagged content text',
            moderation_url='https://civicq.org/moderate/123',
            report_count=3,
            ai_toxicity_score=85.5
        )

        assert mock_send.called
        assert 'flagged' in mock_send.call_args[1]['subject'].lower()

    @patch.object(extended_email_service.base, '_send_email')
    def test_send_user_warning_email(self, mock_send):
        """Test user warning email"""
        mock_send.return_value = {'success': True}

        result = extended_email_service.send_user_warning_email(
            to_email='user@example.com',
            user_name='User Name',
            warning_level=1,
            warning_reason='Inappropriate language',
            warning_date='2026-02-14',
            violation_description='You used inappropriate language',
            content_text='Content text',
            guidelines_url='https://civicq.org/guidelines'
        )

        assert mock_send.called
        assert 'warning' in mock_send.call_args[1]['subject'].lower()


# ============================================================================
# CANDIDATE EMAIL TESTS
# ============================================================================

class TestCandidateEmails:
    """Test candidate email functionality"""

    @patch.object(platform_email_service.base, '_send_email')
    def test_send_candidate_verified_email(self, mock_send):
        """Test candidate verified email"""
        mock_send.return_value = {'success': True}

        result = platform_email_service.send_candidate_verified_email(
            to_email='candidate@example.com',
            candidate_name='John Candidate',
            position='Mayor',
            city_name='Springfield',
            state='IL',
            election_date='2026-11-03',
            profile_url='https://civicq.org/candidates/123',
            dashboard_url='https://civicq.org/dashboard',
            candidate_guide_url='https://civicq.org/guide',
            video_guide_url='https://civicq.org/video-guide',
            promote_url='https://civicq.org/promote'
        )

        assert mock_send.called
        assert 'verified' in mock_send.call_args[1]['subject'].lower()

    @patch.object(platform_email_service.base, '_send_email')
    def test_send_unanswered_questions_reminder(self, mock_send):
        """Test unanswered questions reminder email"""
        mock_send.return_value = {'success': True}

        result = platform_email_service.send_unanswered_questions_reminder_email(
            to_email='candidate@example.com',
            candidate_name='John Candidate',
            city_name='Springfield',
            unanswered_count=5,
            top_questions=[
                {'text': 'Question 1', 'upvotes': 10, 'days_ago': 2, 'category': 'Education'},
                {'text': 'Question 2', 'upvotes': 8, 'days_ago': 1, 'category': 'Economy'}
            ],
            answer_questions_url='https://civicq.org/answer',
            election_date='2026-11-03',
            days_until_election=30,
            candidate_guide_url='https://civicq.org/guide',
            video_guide_url='https://civicq.org/video',
            notification_settings_url='https://civicq.org/settings'
        )

        assert mock_send.called
        assert 'unanswered' in mock_send.call_args[1]['subject'].lower()


# ============================================================================
# SYSTEM EMAIL TESTS
# ============================================================================

class TestSystemEmails:
    """Test system email functionality"""

    @patch.object(system_email_service.base, '_send_email')
    def test_send_weekly_voter_digest(self, mock_send):
        """Test weekly voter digest email"""
        mock_send.return_value = {'success': True}

        result = system_email_service.send_weekly_voter_digest_email(
            to_email='voter@example.com',
            user_name='Jane Voter',
            city_name='Springfield',
            week_start_date='2026-02-10',
            week_end_date='2026-02-16',
            new_answers=[],
            trending_questions=[],
            user_questions_count=3,
            user_votes_count=15,
            total_questions=50,
            total_answers=35,
            ask_question_url='https://civicq.org/ask',
            browse_questions_url='https://civicq.org/questions'
        )

        assert mock_send.called
        assert 'digest' in mock_send.call_args[1]['subject'].lower()

    @patch.object(system_email_service.base, '_send_email')
    def test_send_election_reminder_1day(self, mock_send):
        """Test 1-day election reminder email"""
        mock_send.return_value = {'success': True}

        result = system_email_service.send_election_reminder_1day_email(
            to_email='voter@example.com',
            user_name='Jane Voter',
            election_name='Springfield General Election',
            election_date='2026-11-03',
            city_name='Springfield',
            state='IL',
            polling_place_url='https://votespringfield.gov/polling',
            poll_open_time='7:00 AM',
            poll_close_time='8:00 PM',
            id_required=True,
            all_candidates_url='https://civicq.org/candidates',
            voter_registration_url='https://votespringfield.gov/register'
        )

        assert mock_send.called
        assert 'tomorrow' in mock_send.call_args[1]['subject'].lower()


# ============================================================================
# CELERY TASK TESTS
# ============================================================================

class TestEmailTasks:
    """Test Celery email tasks"""

    @patch('app.tasks.email_tasks.email_service.send_verification_email')
    def test_verification_email_task(self, mock_send):
        """Test verification email Celery task"""
        mock_send.return_value = {'success': True}

        result = send_verification_email_task(
            to_email='test@example.com',
            verification_token='token-123',
            user_name='Test User'
        )

        assert mock_send.called
        assert result['success'] is True

    @patch('app.tasks.email_tasks.extended_email_service.send_question_submitted_email')
    def test_question_submitted_task(self, mock_send):
        """Test question submitted Celery task"""
        mock_send.return_value = {'success': True}

        result = send_question_submitted_email_task(
            to_email='voter@example.com',
            user_name='Voter',
            candidate_name='Candidate',
            category='Education',
            question_text='Question?',
            question_url='https://civicq.org/q/123'
        )

        assert mock_send.called


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestEmailIntegration:
    """Integration tests for email system"""

    @pytest.mark.integration
    @patch('app.services.email_service.SendGridAPIClient')
    def test_full_email_workflow(self, mock_sendgrid):
        """Test complete email workflow from creation to sending"""
        # Mock SendGrid
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.headers = {'X-Message-Id': 'integration-test-id'}
        mock_sendgrid.return_value.send.return_value = mock_response

        # Test verification email workflow
        result = email_service.send_verification_email(
            to_email='integration@example.com',
            verification_token='integration-token',
            user_name='Integration Test'
        )

        # Verify result
        assert 'success' in result or 'dev_mode' in result

    @pytest.mark.integration
    def test_template_rendering_for_all_emails(self):
        """Test that all email templates can be rendered"""
        test_context = {
            'user_name': 'Test User',
            'candidate_name': 'Test Candidate',
            'city_name': 'Test City',
            'support_email': 'support@civicq.org',
            'app_name': 'CivicQ'
        }

        templates = [
            'base_email.html',
            'verification_email.html',
            'password_reset.html',
            'welcome_email.html',
            'question_submitted.html',
            'question_approved.html',
            'candidate_answered.html'
        ]

        for template in templates:
            try:
                html = email_service._render_template(template, test_context)
                assert html is not None
                assert len(html) > 0
            except Exception as e:
                pytest.fail(f"Failed to render {template}: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
