"""
Extended Email Service Methods

All additional email sending methods for question workflow, moderation,
city/admin, candidate, and system emails.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime

from app.services.email_service import email_service as base_service


class ExtendedEmailService:
    """Extended email service with all platform email types"""

    def __init__(self, base_email_service):
        """Initialize with base email service"""
        self.base = base_email_service

    # ========================================================================
    # QUESTION WORKFLOW EMAILS
    # ========================================================================

    def send_question_submitted_email(
        self,
        to_email: str,
        user_name: str,
        candidate_name: str,
        category: str,
        question_text: str,
        question_url: str
    ) -> Dict[str, Any]:
        """Send confirmation email when a question is submitted"""
        context = {
            'user_name': user_name,
            'candidate_name': candidate_name,
            'category': category,
            'question_text': question_text,
            'question_url': question_url,
            'support_email': self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')
        }

        html_content = self.base._render_template('question_submitted.html', context)
        plain_content = f"""
Hi {user_name},

Thank you for submitting your question to CivicQ! We've received your question and it's now under review.

Your Question:
For: {candidate_name}
Category: {category}
"{question_text}"

What happens next?
1. Moderation Review: Our team will review your question (typically within 24 hours)
2. Notification: You'll receive an email once your question is approved
3. Candidate Response: Approved questions will be sent to the candidate
4. Community Voting: Other voters can upvote your question

View your question: {question_url}

Thank you for helping make our democracy more transparent!

Best regards,
The CivicQ Team
        """

        return self.base._send_email(
            to_email=to_email,
            subject=f"Question Submitted for {candidate_name}",
            html_content=html_content,
            plain_content=plain_content,
            category="question_submitted"
        )

    def send_question_approved_email(
        self,
        to_email: str,
        user_name: str,
        candidate_name: str,
        category: str,
        question_text: str,
        question_url: str,
        city_name: str
    ) -> Dict[str, Any]:
        """Send notification when a question is approved"""
        context = {
            'user_name': user_name,
            'candidate_name': candidate_name,
            'category': category,
            'question_text': question_text,
            'question_url': question_url,
            'city_name': city_name,
            'support_email': self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')
        }

        html_content = self.base._render_template('question_approved.html', context)
        plain_content = f"""
Hi {user_name},

Great news! Your question has been approved and is now live on CivicQ.

Your Question:
For: {candidate_name}
Category: {category}
"{question_text}"

The candidate has been notified and can now provide their response. You'll receive an email when they answer.

View your question: {question_url}

Thank you for engaging in your local democracy!

Best regards,
The CivicQ Team
        """

        return self.base._send_email(
            to_email=to_email,
            subject="Your Question Has Been Approved!",
            html_content=html_content,
            plain_content=plain_content,
            category="question_approved"
        )

    def send_question_rejected_email(
        self,
        to_email: str,
        user_name: str,
        candidate_name: str,
        question_text: str,
        rejection_reason: str,
        submit_question_url: str
    ) -> Dict[str, Any]:
        """Send notification when a question is rejected"""
        context = {
            'user_name': user_name,
            'candidate_name': candidate_name,
            'question_text': question_text,
            'rejection_reason': rejection_reason,
            'submit_question_url': submit_question_url,
            'support_email': self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')
        }

        html_content = self.base._render_template('question_rejected.html', context)
        plain_content = f"""
Hi {user_name},

Thank you for your submission. After review, we were unable to approve your question for the following reason:

Reason: {rejection_reason}

Your Question:
For: {candidate_name}
"{question_text}"

You can revise and resubmit your question or submit a new one.

Submit a new question: {submit_question_url}

Best regards,
The CivicQ Team
        """

        return self.base._send_email(
            to_email=to_email,
            subject="Question Update - Revision Needed",
            html_content=html_content,
            plain_content=plain_content,
            category="question_rejected"
        )

    def send_candidate_answered_email(
        self,
        to_email: str,
        user_name: str,
        candidate_name: str,
        question_text: str,
        answer_text: str,
        answer_url: str,
        has_video: bool = False
    ) -> Dict[str, Any]:
        """Send notification when a candidate answers a user's question"""
        context = {
            'user_name': user_name,
            'candidate_name': candidate_name,
            'question_text': question_text,
            'answer_text': answer_text,
            'answer_url': answer_url,
            'has_video': has_video,
            'support_email': self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')
        }

        html_content = self.base._render_template('candidate_answered.html', context)
        plain_content = f"""
Hi {user_name},

Exciting news! {candidate_name} has answered your question on CivicQ.

Your Question:
"{question_text}"

{candidate_name}'s Response:
{answer_text}

{'[Video response available]' if has_video else ''}

View the full response: {answer_url}

Thank you for using CivicQ to engage with your local candidates!

Best regards,
The CivicQ Team
        """

        return self.base._send_email(
            to_email=to_email,
            subject=f"{candidate_name} Answered Your Question!",
            html_content=html_content,
            plain_content=plain_content,
            category="candidate_answered"
        )

    def send_new_question_to_candidate(
        self,
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
        """Send notification to candidate about new question"""
        context = {
            'candidate_name': candidate_name,
            'city_name': city_name,
            'category': category,
            'question_text': question_text,
            'answer_url': answer_url,
            'upvote_count': upvote_count,
            'priority_level': priority_level,
            'max_video_length': max_video_length,
            'support_email': self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')
        }

        html_content = self.base._render_template('new_question_for_candidate.html', context)
        plain_content = f"""
Hi {candidate_name},

A voter in {city_name} has submitted a new question for you on CivicQ.

Question:
Category: {category}
Upvotes: {upvote_count}
{f'Priority: {priority_level}' if priority_level else ''}

"{question_text}"

Answer this question: {answer_url}

Answering questions helps you build trust with voters and showcase your platform. We recommend responding within 48 hours for the best engagement.

Best regards,
The CivicQ Team
        """

        return self.base._send_email(
            to_email=to_email,
            subject="New Question from a Voter",
            html_content=html_content,
            plain_content=plain_content,
            category="new_question_candidate"
        )

    # ========================================================================
    # MODERATION EMAILS
    # ========================================================================

    def send_content_flagged_to_moderator(
        self,
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
        """Send notification to moderator about flagged content"""
        context = {
            'moderator_name': moderator_name,
            'content_type': content_type,
            'author_name': author_name,
            'author_email': author_email,
            'flag_reason': flag_reason,
            'content_text': content_text,
            'moderation_url': moderation_url,
            'report_count': report_count,
            'ai_toxicity_score': ai_toxicity_score,
            'support_email': self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')
        }

        html_content = self.base._render_template('content_flagged_moderator.html', context)
        plain_content = f"""
Hi {moderator_name},

Content has been flagged for moderation review on CivicQ.

Details:
Content Type: {content_type}
Author: {author_name} ({author_email})
Flag Reason: {flag_reason}
Reports: {report_count}
{f'AI Toxicity Score: {ai_toxicity_score}%' if ai_toxicity_score else ''}

Content:
{content_text}

Review and take action: {moderation_url}

Best regards,
The CivicQ Team
        """

        return self.base._send_email(
            to_email=to_email,
            subject=f"Content Flagged for Review - {content_type}",
            html_content=html_content,
            plain_content=plain_content,
            category="content_flagged"
        )

    def send_content_removed_email(
        self,
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
        """Send notification when user's content is removed"""
        context = {
            'user_name': user_name,
            'content_type': content_type,
            'removal_reason': removal_reason,
            'content_text': content_text,
            'removal_date': removal_date,
            'violation_details': violation_details,
            'guidelines_url': guidelines_url,
            'is_first_violation': is_first_violation,
            'is_second_violation': is_second_violation,
            'support_email': self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')
        }

        html_content = self.base._render_template('content_removed.html', context)
        plain_content = f"""
Hi {user_name},

Your content on CivicQ has been removed for violating our community guidelines.

Content Type: {content_type}
Reason: {removal_reason}
Date: {removal_date}

Removed Content:
{content_text}

{violation_details}

This is {'your first' if is_first_violation else 'your second' if is_second_violation else 'a repeated'} violation. Future violations may result in account suspension or ban.

Review Community Guidelines: {guidelines_url}

Best regards,
The CivicQ Moderation Team
        """

        return self.base._send_email(
            to_email=to_email,
            subject="Content Removed - Community Guidelines Violation",
            html_content=html_content,
            plain_content=plain_content,
            category="content_removed"
        )

    def send_user_warning_email(
        self,
        to_email: str,
        user_name: str,
        warning_level: int,
        warning_reason: str,
        warning_date: str,
        violation_description: str,
        content_text: str,
        guidelines_url: str
    ) -> Dict[str, Any]:
        """Send warning notification to user"""
        context = {
            'user_name': user_name,
            'warning_level': warning_level,
            'warning_reason': warning_reason,
            'warning_date': warning_date,
            'violation_description': violation_description,
            'content_text': content_text,
            'guidelines_url': guidelines_url,
            'support_email': self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')
        }

        html_content = self.base._render_template('user_warning.html', context)
        plain_content = f"""
Hi {user_name},

This is an official warning regarding your recent activity on CivicQ.

Warning Level: {warning_level} of 3
Reason: {warning_reason}
Date: {warning_date}

{violation_description}

Content in Question:
{content_text}

{'This is your first warning. Please review our community guidelines.' if warning_level == 1 else 'This is your second warning. One more violation will result in account suspension.' if warning_level == 2 else 'This is your final warning. Any additional violations will result in immediate suspension or ban.'}

Review Community Guidelines: {guidelines_url}

Best regards,
The CivicQ Moderation Team
        """

        return self.base._send_email(
            to_email=to_email,
            subject=f"Warning - Community Guidelines Violation (Warning {warning_level}/3)",
            html_content=html_content,
            plain_content=plain_content,
            category="user_warning"
        )

    def send_user_suspended_email(
        self,
        to_email: str,
        user_name: str,
        suspension_duration: str,
        suspension_end_date: str,
        suspension_reason: str,
        violation_details: str,
        guidelines_url: str,
        previous_warnings: int = 0
    ) -> Dict[str, Any]:
        """Send notification when user is suspended"""
        context = {
            'user_name': user_name,
            'suspension_duration': suspension_duration,
            'suspension_end_date': suspension_end_date,
            'suspension_reason': suspension_reason,
            'violation_details': violation_details,
            'guidelines_url': guidelines_url,
            'previous_warnings': previous_warnings,
            'support_email': self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')
        }

        html_content = self.base._render_template('user_suspended.html', context)
        plain_content = f"""
Hi {user_name},

Your CivicQ account has been temporarily suspended due to violations of our community guidelines.

Suspension Duration: {suspension_duration}
Suspension Ends: {suspension_end_date}
Reason: {suspension_reason}

{violation_details}

{'You received ' + str(previous_warnings) + ' warning(s) prior to this suspension.' if previous_warnings > 0 else ''}

Your account will be automatically reactivated on {suspension_end_date}. Additional violations after this suspension may result in permanent ban.

Review Community Guidelines: {guidelines_url}

Best regards,
The CivicQ Moderation Team
        """

        return self.base._send_email(
            to_email=to_email,
            subject="Account Suspended - Community Guidelines Violation",
            html_content=html_content,
            plain_content=plain_content,
            category="user_suspended"
        )

    def send_user_banned_email(
        self,
        to_email: str,
        user_name: str,
        ban_date: str,
        ban_reason: str,
        violation_details: str,
        violation_history: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Send notification when user is permanently banned"""
        context = {
            'user_name': user_name,
            'ban_date': ban_date,
            'ban_reason': ban_reason,
            'violation_details': violation_details,
            'violation_history': violation_history or [],
            'support_email': self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')
        }

        html_content = self.base._render_template('user_banned.html', context)
        plain_content = f"""
Hi {user_name},

Your CivicQ account has been permanently banned due to severe or repeated violations of our community guidelines.

Account Status: Permanently Banned
Effective Date: {ban_date}
Reason: {ban_reason}

{violation_details}

This decision is final. Permanent bans are issued only in cases of severe violations, repeated violations after warnings and suspensions, or illegal activity.

Appeals may be submitted within 30 days to {self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')}.

Best regards,
The CivicQ Moderation Team
        """

        return self.base._send_email(
            to_email=to_email,
            subject="Account Permanently Banned",
            html_content=html_content,
            plain_content=plain_content,
            category="user_banned"
        )


# Global extended email service instance
extended_email_service = ExtendedEmailService(base_service)
