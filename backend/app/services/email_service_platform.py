"""
Platform Email Service Methods

City/Admin, Candidate, and System email sending methods.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime

from app.services.email_service import email_service as base_service


class PlatformEmailService:
    """Platform email service for city, candidate, and system emails"""

    def __init__(self, base_email_service):
        """Initialize with base email service"""
        self.base = base_email_service

    # ========================================================================
    # CITY / ADMIN EMAILS
    # ========================================================================

    def send_city_registration_to_admin(
        self,
        to_email: str,
        city_name: str,
        state: str,
        county: str,
        population: str,
        registration_date: str,
        official_name: str,
        official_title: str,
        official_email: str,
        official_phone: str,
        department: str,
        admin_review_url: str,
        upcoming_elections: Optional[List[str]] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send notification to admin about new city registration"""
        context = {
            'city_name': city_name,
            'state': state,
            'county': county,
            'population': population,
            'registration_date': registration_date,
            'official_name': official_name,
            'official_title': official_title,
            'official_email': official_email,
            'official_phone': official_phone,
            'department': department,
            'admin_review_url': admin_review_url,
            'upcoming_elections': upcoming_elections,
            'notes': notes,
            'support_email': self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')
        }

        html_content = self.base._render_template('city_registration_admin.html', context)
        plain_content = f"""
New City Registration

City: {city_name}, {state}
County: {county}
Population: {population}
Registration Date: {registration_date}

City Official Contact:
Name: {official_name}
Title: {official_title}
Email: {official_email}
Phone: {official_phone}
Department: {department}

Review and verify this registration: {admin_review_url}

Please review this registration within 48 hours.
        """

        return self.base._send_email(
            to_email=to_email,
            subject=f"New City Registration: {city_name}, {state}",
            html_content=html_content,
            plain_content=plain_content,
            category="city_registration"
        )

    def send_city_verified_email(
        self,
        to_email: str,
        official_name: str,
        city_name: str,
        state: str,
        admin_dashboard_url: str,
        admin_guide_url: str,
        tutorials_url: str,
        training_url: str
    ) -> Dict[str, Any]:
        """Send confirmation to city official when city is verified"""
        context = {
            'official_name': official_name,
            'city_name': city_name,
            'state': state,
            'admin_dashboard_url': admin_dashboard_url,
            'admin_guide_url': admin_guide_url,
            'tutorials_url': tutorials_url,
            'training_url': training_url,
            'support_email': self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')
        }

        html_content = self.base._render_template('city_verified.html', context)
        plain_content = f"""
Hi {official_name},

Congratulations! Your city has been successfully verified on CivicQ.

{city_name}, {state} is now live on CivicQ and ready to engage with voters!

Access your admin dashboard: {admin_dashboard_url}

Next Steps:
1. Add upcoming elections
2. Verify candidates
3. Configure city settings
4. Promote CivicQ to your constituents

Resources:
- Admin Guide: {admin_guide_url}
- Video Tutorials: {tutorials_url}
- Schedule Training: {training_url}

Welcome to CivicQ!

Best regards,
The CivicQ Team
        """

        return self.base._send_email(
            to_email=to_email,
            subject=f"City Verified - Welcome to CivicQ!",
            html_content=html_content,
            plain_content=plain_content,
            category="city_verified"
        )

    def send_city_rejected_email(
        self,
        to_email: str,
        official_name: str,
        city_name: str,
        rejection_reason: str,
        detailed_requirements: str,
        requirements: List[str],
        resubmit_url: str
    ) -> Dict[str, Any]:
        """Send notification when city registration needs more info"""
        context = {
            'official_name': official_name,
            'city_name': city_name,
            'rejection_reason': rejection_reason,
            'detailed_requirements': detailed_requirements,
            'requirements': requirements,
            'resubmit_url': resubmit_url,
            'support_email': self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')
        }

        html_content = self.base._render_template('city_rejected.html', context)
        plain_content = f"""
Hi {official_name},

Thank you for your interest in bringing CivicQ to {city_name}. We need additional information before we can verify your city.

Status: Pending Additional Verification
Reason: {rejection_reason}

{detailed_requirements}

Please provide:
{chr(10).join('- ' + req for req in requirements)}

Update your registration: {resubmit_url}

Please submit the requested information within 14 days.

Best regards,
The CivicQ Verification Team
        """

        return self.base._send_email(
            to_email=to_email,
            subject=f"City Registration Update - Additional Information Needed",
            html_content=html_content,
            plain_content=plain_content,
            category="city_rejected"
        )

    def send_staff_invitation_email(
        self,
        to_email: str,
        staff_name: str,
        city_name: str,
        state: str,
        staff_role: str,
        inviter_name: str,
        inviter_title: str,
        inviter_email: str,
        accept_invitation_url: str
    ) -> Dict[str, Any]:
        """Send invitation to join city staff team"""
        context = {
            'staff_name': staff_name,
            'city_name': city_name,
            'state': state,
            'staff_role': staff_role,
            'inviter_name': inviter_name,
            'inviter_title': inviter_title,
            'inviter_email': inviter_email,
            'accept_invitation_url': accept_invitation_url,
            'support_email': self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')
        }

        html_content = self.base._render_template('staff_invitation.html', context)
        plain_content = f"""
Hi {staff_name},

{inviter_name} has invited you to join the CivicQ admin team for {city_name}.

City: {city_name}, {state}
Role: {staff_role}
Invited By: {inviter_name} ({inviter_title})

Accept invitation: {accept_invitation_url}

This invitation will expire in 7 days.

Questions? Contact {inviter_name} at {inviter_email}

Best regards,
The CivicQ Team
        """

        return self.base._send_email(
            to_email=to_email,
            subject=f"Invitation to Join {city_name} CivicQ Team",
            html_content=html_content,
            plain_content=plain_content,
            category="staff_invitation"
        )

    def send_weekly_city_digest_email(
        self,
        to_email: str,
        staff_name: str,
        city_name: str,
        state: str,
        week_start_date: str,
        week_end_date: str,
        new_questions: int,
        new_answers: int,
        new_voters: int,
        total_votes: int,
        active_candidates: int,
        top_questions: List[Dict[str, Any]],
        dashboard_url: str,
        moderation_url: str,
        analytics_url: str,
        settings_url: str,
        unsubscribe_url: str,
        pending_moderation: int = 0,
        unanswered_questions: int = 0,
        upcoming_elections: Optional[List[Dict[str, Any]]] = None,
        add_election_url: Optional[str] = None,
        questions_trend: float = 0,
        answers_trend: float = 0,
        voters_trend: float = 0,
        engagement_trend: float = 0
    ) -> Dict[str, Any]:
        """Send weekly digest to city staff"""
        context = {
            'staff_name': staff_name,
            'city_name': city_name,
            'state': state,
            'week_start_date': week_start_date,
            'week_end_date': week_end_date,
            'new_questions': new_questions,
            'new_answers': new_answers,
            'new_voters': new_voters,
            'total_votes': total_votes,
            'active_candidates': active_candidates,
            'top_questions': top_questions,
            'dashboard_url': dashboard_url,
            'moderation_url': moderation_url,
            'analytics_url': analytics_url,
            'settings_url': settings_url,
            'unsubscribe_url': unsubscribe_url,
            'pending_moderation': pending_moderation,
            'unanswered_questions': unanswered_questions,
            'upcoming_elections': upcoming_elections,
            'add_election_url': add_election_url,
            'questions_trend': questions_trend,
            'answers_trend': answers_trend,
            'voters_trend': voters_trend,
            'engagement_trend': engagement_trend,
            'support_email': self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')
        }

        html_content = self.base._render_template('weekly_city_digest.html', context)
        plain_content = f"""
Hi {staff_name},

Weekly Activity Summary for {city_name}
Week of {week_start_date} - {week_end_date}

Activity Overview:
- New Questions: {new_questions}
- New Answers: {new_answers}
- New Voters: {new_voters}
- Total Votes: {total_votes}
- Active Candidates: {active_candidates}

{f'Action Required: {pending_moderation} items pending moderation' if pending_moderation > 0 else ''}

View full dashboard: {dashboard_url}

Best regards,
The CivicQ Team
        """

        return self.base._send_email(
            to_email=to_email,
            subject=f"Weekly Digest - {city_name}",
            html_content=html_content,
            plain_content=plain_content,
            category="weekly_city_digest"
        )

    # ========================================================================
    # CANDIDATE EMAILS
    # ========================================================================

    def send_candidate_verification_request_email(
        self,
        to_email: str,
        candidate_name: str,
        position: str,
        election_name: str,
        city_name: str,
        state: str,
        election_date: str,
        verification_url: str,
        candidate_guide_url: str,
        faq_url: str
    ) -> Dict[str, Any]:
        """Send verification request to candidate"""
        context = {
            'candidate_name': candidate_name,
            'position': position,
            'election_name': election_name,
            'city_name': city_name,
            'state': state,
            'election_date': election_date,
            'verification_url': verification_url,
            'candidate_guide_url': candidate_guide_url,
            'faq_url': faq_url,
            'support_email': self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')
        }

        html_content = self.base._render_template('candidate_verification_request.html', context)
        plain_content = f"""
Hi {candidate_name},

Thank you for creating a candidate profile on CivicQ! To complete your registration, we need to verify your candidacy.

Position: {position}
Election: {election_name}
City: {city_name}, {state}
Election Date: {election_date}

Complete verification: {verification_url}

We recommend completing verification at least 60 days before the election to maximize voter engagement.

Best regards,
The CivicQ Team
        """

        return self.base._send_email(
            to_email=to_email,
            subject="Verify Your Candidate Profile - CivicQ",
            html_content=html_content,
            plain_content=plain_content,
            category="candidate_verification"
        )

    def send_candidate_verified_email(
        self,
        to_email: str,
        candidate_name: str,
        position: str,
        city_name: str,
        state: str,
        election_date: str,
        profile_url: str,
        dashboard_url: str,
        candidate_guide_url: str,
        video_guide_url: str,
        promote_url: str
    ) -> Dict[str, Any]:
        """Send confirmation when candidate is verified"""
        context = {
            'candidate_name': candidate_name,
            'position': position,
            'city_name': city_name,
            'state': state,
            'election_date': election_date,
            'profile_url': profile_url,
            'dashboard_url': dashboard_url,
            'candidate_guide_url': candidate_guide_url,
            'video_guide_url': video_guide_url,
            'promote_url': promote_url,
            'support_email': self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')
        }

        html_content = self.base._render_template('candidate_verified.html', context)
        plain_content = f"""
Hi {candidate_name},

Congratulations! Your candidate profile has been verified and is now live on CivicQ.

{candidate_name}
Candidate for {position}
{city_name}, {state}
Election: {election_date}

View your profile: {profile_url}

Next Steps:
1. Complete your profile
2. Add platform positions
3. Be ready to answer voter questions
4. Share your profile with voters

Your Profile URL: {profile_url}

Good luck with your campaign!

Best regards,
The CivicQ Team
        """

        return self.base._send_email(
            to_email=to_email,
            subject="Candidate Profile Verified - You're Live!",
            html_content=html_content,
            plain_content=plain_content,
            category="candidate_verified"
        )

    def send_unanswered_questions_reminder_email(
        self,
        to_email: str,
        candidate_name: str,
        city_name: str,
        unanswered_count: int,
        top_questions: List[Dict[str, Any]],
        answer_questions_url: str,
        election_date: str,
        days_until_election: int,
        candidate_guide_url: str,
        video_guide_url: str,
        notification_settings_url: str
    ) -> Dict[str, Any]:
        """Send reminder about unanswered questions"""
        context = {
            'candidate_name': candidate_name,
            'city_name': city_name,
            'unanswered_count': unanswered_count,
            'top_questions': top_questions,
            'answer_questions_url': answer_questions_url,
            'election_date': election_date,
            'days_until_election': days_until_election,
            'candidate_guide_url': candidate_guide_url,
            'video_guide_url': video_guide_url,
            'notification_settings_url': notification_settings_url,
            'support_email': self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')
        }

        html_content = self.base._render_template('unanswered_questions_reminder.html', context)
        plain_content = f"""
Hi {candidate_name},

Voters in {city_name} are waiting to hear from you! You currently have {unanswered_count} unanswered question{'s' if unanswered_count != 1 else ''} on CivicQ.

Election Date: {election_date} ({days_until_election} days away)

Answer questions: {answer_questions_url}

Candidates who answer at least 80% of questions receive 2.5x more profile views and positive ratings from voters.

Best regards,
The CivicQ Team
        """

        return self.base._send_email(
            to_email=to_email,
            subject=f"You Have {unanswered_count} Unanswered Question{'s' if unanswered_count != 1 else ''}",
            html_content=html_content,
            plain_content=plain_content,
            category="unanswered_questions_reminder"
        )

    def send_video_upload_success_email(
        self,
        to_email: str,
        candidate_name: str,
        question_text: str,
        video_duration: int,
        answer_url: str,
        transcription_available: bool = False,
        transcription_text: Optional[str] = None,
        edit_transcription_url: Optional[str] = None,
        remaining_questions: int = 0,
        answer_questions_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send confirmation when video is successfully processed"""
        context = {
            'candidate_name': candidate_name,
            'question_text': question_text,
            'video_duration': video_duration,
            'answer_url': answer_url,
            'transcription_available': transcription_available,
            'transcription_text': transcription_text,
            'edit_transcription_url': edit_transcription_url,
            'remaining_questions': remaining_questions,
            'answer_questions_url': answer_questions_url,
            'support_email': self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')
        }

        html_content = self.base._render_template('video_upload_success.html', context)
        plain_content = f"""
Hi {candidate_name},

Great news! Your video response has been successfully uploaded and processed.

Question: {question_text[:100]}...
Video Duration: {video_duration} seconds
Status: Live
{'Transcription: Complete (auto-generated)' if transcription_available else ''}

View your answer: {answer_url}

Video answers typically receive 3x more views than text-only answers!

{f'You still have {remaining_questions} unanswered question{"s" if remaining_questions != 1 else ""}. Keep the momentum going!' if remaining_questions > 0 else ''}

Best regards,
The CivicQ Team
        """

        return self.base._send_email(
            to_email=to_email,
            subject="Video Upload Successful",
            html_content=html_content,
            plain_content=plain_content,
            category="video_upload_success"
        )

    def send_video_processing_failed_email(
        self,
        to_email: str,
        candidate_name: str,
        question_text: str,
        upload_date: str,
        error_reason: str,
        retry_upload_url: str,
        text_answer_url: str,
        video_guide_url: str,
        max_video_duration: int,
        error_code: Optional[str] = None,
        upload_id: Optional[str] = None,
        error_timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send notification when video processing fails"""
        context = {
            'candidate_name': candidate_name,
            'question_text': question_text,
            'upload_date': upload_date,
            'error_reason': error_reason,
            'retry_upload_url': retry_upload_url,
            'text_answer_url': text_answer_url,
            'video_guide_url': video_guide_url,
            'max_video_duration': max_video_duration,
            'error_code': error_code,
            'upload_id': upload_id,
            'error_timestamp': error_timestamp,
            'support_email': self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')
        }

        html_content = self.base._render_template('video_processing_failed.html', context)
        plain_content = f"""
Hi {candidate_name},

We encountered an issue processing your video response.

Question: {question_text[:100]}...
Upload Date: {upload_date}
Error: {error_reason}

Try again: {retry_upload_url}

Common Solutions:
- Ensure file size is under 500MB
- Use MP4 format (H.264 codec)
- Keep video under {max_video_duration} seconds
- Check for stable internet connection

Alternative: Submit a text answer now and add video later
{text_answer_url}

Error Details (for support):
Error Code: {error_code or 'N/A'}
Upload ID: {upload_id or 'N/A'}

Best regards,
The CivicQ Team
        """

        return self.base._send_email(
            to_email=to_email,
            subject="Video Upload Issue - Action Needed",
            html_content=html_content,
            plain_content=plain_content,
            category="video_processing_failed"
        )


# Global platform email service instance
platform_email_service = PlatformEmailService(base_service)
