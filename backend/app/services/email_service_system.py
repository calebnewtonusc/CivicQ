"""
System Email Service Methods

Weekly digests, election reminders, and system notification emails.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime

from app.services.email_service import email_service as base_service


class SystemEmailService:
    """System email service for digests and notifications"""

    def __init__(self, base_email_service):
        """Initialize with base email service"""
        self.base = base_email_service

    # ========================================================================
    # SYSTEM EMAILS
    # ========================================================================

    def send_weekly_voter_digest_email(
        self,
        to_email: str,
        user_name: str,
        city_name: str,
        week_start_date: str,
        week_end_date: str,
        new_answers: Optional[List[Dict[str, Any]]] = None,
        trending_questions: Optional[List[Dict[str, Any]]] = None,
        upcoming_elections: Optional[List[Dict[str, Any]]] = None,
        user_questions_count: int = 0,
        user_votes_count: int = 0,
        user_answers_received: int = 0,
        total_questions: int = 0,
        total_answers: int = 0,
        total_voters: int = 0,
        engagement_rate: float = 0,
        days_until_next_election: Optional[int] = None,
        ask_question_url: str = "",
        browse_questions_url: str = "",
        browse_candidates_url: str = "",
        upvote_questions_url: str = "",
        share_url: str = "",
        unsubscribe_url: str = "",
        email_preferences_url: str = ""
    ) -> Dict[str, Any]:
        """Send weekly digest to voters"""
        context = {
            'user_name': user_name,
            'city_name': city_name,
            'week_start_date': week_start_date,
            'week_end_date': week_end_date,
            'new_answers': new_answers or [],
            'trending_questions': trending_questions or [],
            'upcoming_elections': upcoming_elections or [],
            'user_questions_count': user_questions_count,
            'user_votes_count': user_votes_count,
            'user_answers_received': user_answers_received,
            'total_questions': total_questions,
            'total_answers': total_answers,
            'total_voters': total_voters,
            'engagement_rate': engagement_rate,
            'days_until_next_election': days_until_next_election,
            'ask_question_url': ask_question_url,
            'browse_questions_url': browse_questions_url,
            'browse_candidates_url': browse_candidates_url,
            'upvote_questions_url': upvote_questions_url,
            'share_url': share_url,
            'unsubscribe_url': unsubscribe_url,
            'email_preferences_url': email_preferences_url,
            'support_email': self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')
        }

        html_content = self.base._render_template('weekly_voter_digest.html', context)
        plain_content = f"""
Hi {user_name},

Here's what's happening this week in {city_name} on CivicQ.
Week of {week_start_date} - {week_end_date}

New Candidate Answers: {len(new_answers or [])}
Trending Questions: {len(trending_questions or [])}

Your Activity:
- Questions Asked: {user_questions_count}
- Votes Cast: {user_votes_count}
- Answers Received: {user_answers_received}

Community Impact:
- Total Questions: {total_questions}
- Total Answers: {total_answers}
- Active Voters: {total_voters}
- Candidate Response Rate: {engagement_rate}%

{f'{days_until_next_election} days until the next election. Make sure you\'re informed!' if days_until_next_election else ''}

Browse all questions: {browse_questions_url}

Stay informed, stay engaged!

Best regards,
The CivicQ Team

Unsubscribe: {unsubscribe_url}
        """

        return self.base._send_email(
            to_email=to_email,
            subject=f"Your Weekly CivicQ Digest - {city_name}",
            html_content=html_content,
            plain_content=plain_content,
            category="weekly_voter_digest"
        )

    def send_election_reminder_7days_email(
        self,
        to_email: str,
        user_name: str,
        election_name: str,
        election_date: str,
        city_name: str,
        state: str,
        ballot_items: Optional[List[Dict[str, Any]]] = None,
        election_url: str = "",
        voter_registration_url: str = "",
        polling_place_url: str = "",
        poll_open_time: str = "7:00 AM",
        poll_close_time: str = "8:00 PM",
        id_required: bool = False,
        your_answered_questions: Optional[List[Dict[str, Any]]] = None,
        positions: Optional[List[Dict[str, Any]]] = None,
        all_candidates_url: str = "",
        early_voting_available: bool = False,
        early_voting_start: Optional[str] = None,
        early_voting_end: Optional[str] = None,
        early_voting_hours: Optional[str] = None,
        early_voting_url: Optional[str] = None,
        absentee_deadline: Optional[str] = None,
        absentee_url: Optional[str] = None,
        ask_question_url: str = "",
        browse_questions_url: str = "",
        voter_guide_url: str = "",
        share_url: str = ""
    ) -> Dict[str, Any]:
        """Send 7-day election reminder"""
        context = {
            'user_name': user_name,
            'election_name': election_name,
            'election_date': election_date,
            'city_name': city_name,
            'state': state,
            'ballot_items': ballot_items or [],
            'election_url': election_url,
            'voter_registration_url': voter_registration_url,
            'polling_place_url': polling_place_url,
            'poll_open_time': poll_open_time,
            'poll_close_time': poll_close_time,
            'id_required': id_required,
            'your_answered_questions': your_answered_questions or [],
            'positions': positions or [],
            'all_candidates_url': all_candidates_url,
            'early_voting_available': early_voting_available,
            'early_voting_start': early_voting_start,
            'early_voting_end': early_voting_end,
            'early_voting_hours': early_voting_hours,
            'early_voting_url': early_voting_url,
            'absentee_deadline': absentee_deadline,
            'absentee_url': absentee_url,
            'ask_question_url': ask_question_url,
            'browse_questions_url': browse_questions_url,
            'voter_guide_url': voter_guide_url,
            'share_url': share_url,
            'support_email': self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')
        }

        html_content = self.base._render_template('election_reminder_7days.html', context)
        plain_content = f"""
Hi {user_name},

Your local election is just 7 days away! Make sure you're prepared to vote.

{election_name}
{election_date}
{city_name}, {state}

Prepare to Vote:
- Verify registration: {voter_registration_url}
- Find polling place: {polling_place_url}
- Poll hours: {poll_open_time} - {poll_close_time}
- ID required: {'Yes - Photo ID' if id_required else 'Recommended but not required'}

{f'Early Voting: {early_voting_start} - {early_voting_end}' if early_voting_available else ''}
{f'Absentee Deadline: {absentee_deadline}' if absentee_deadline else ''}

Compare candidates and review answers: {all_candidates_url}

Every vote counts. Make your voice heard on {election_date}!

Best regards,
The CivicQ Team
        """

        return self.base._send_email(
            to_email=to_email,
            subject=f"Election in 7 Days - {election_name}",
            html_content=html_content,
            plain_content=plain_content,
            category="election_reminder_7days"
        )

    def send_election_reminder_1day_email(
        self,
        to_email: str,
        user_name: str,
        election_name: str,
        election_date: str,
        city_name: str,
        state: str,
        polling_place_url: str,
        poll_open_time: str = "7:00 AM",
        poll_close_time: str = "8:00 PM",
        polling_location: Optional[str] = None,
        id_required: bool = False,
        positions: Optional[List[Dict[str, Any]]] = None,
        all_candidates_url: str = "",
        your_answered_questions: Optional[List[Dict[str, Any]]] = None,
        voter_registration_url: str = "",
        voter_hotline: str = "1-866-OUR-VOTE",
        election_protection_number: str = "1-866-OUR-VOTE",
        voter_rights_url: str = ""
    ) -> Dict[str, Any]:
        """Send 1-day election reminder"""
        context = {
            'user_name': user_name,
            'election_name': election_name,
            'election_date': election_date,
            'city_name': city_name,
            'state': state,
            'polling_place_url': polling_place_url,
            'poll_open_time': poll_open_time,
            'poll_close_time': poll_close_time,
            'polling_location': polling_location,
            'id_required': id_required,
            'positions': positions or [],
            'all_candidates_url': all_candidates_url,
            'your_answered_questions': your_answered_questions or [],
            'voter_registration_url': voter_registration_url,
            'voter_hotline': voter_hotline,
            'election_protection_number': election_protection_number,
            'voter_rights_url': voter_rights_url,
            'support_email': self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')
        }

        html_content = self.base._render_template('election_reminder_1day.html', context)
        plain_content = f"""
Hi {user_name},

TOMORROW IS ELECTION DAY!

{election_name}
TOMORROW: {election_date}
{city_name}, {state}

Critical Information:
- When: {election_date}
- Poll Hours: {poll_open_time} - {poll_close_time}
- Your Polling Place: {polling_location or f'Find it: {polling_place_url}'}
- ID Required: {'Yes - Photo ID' if id_required else 'Recommended'}

What to Bring:
- {'Valid Photo ID (REQUIRED)' if id_required else 'Photo ID (recommended)'}
- Voter registration card (if you have it)
- Sample ballot or notes

Quick Candidate Review: {all_candidates_url}

Vote Smart Tips:
- Go early (polls are least crowded right after opening)
- Check your registration: {voter_registration_url}
- In line at {poll_close_time}? You can still vote!

Voter Hotline: {voter_hotline}

See you at the polls tomorrow!

Your vote matters. Your participation strengthens our democracy!

Best regards,
The CivicQ Team
        """

        return self.base._send_email(
            to_email=to_email,
            subject=f"Vote Tomorrow! - {election_name}",
            html_content=html_content,
            plain_content=plain_content,
            category="election_reminder_1day"
        )

    def send_email_changed_notification(
        self,
        to_email: str,
        user_name: str,
        old_email: str,
        new_email: str,
        change_date: str,
        security_settings_url: str,
        help_url: str,
        security_url: str
    ) -> Dict[str, Any]:
        """Send notification when email is changed (to both old and new)"""
        context = {
            'user_name': user_name,
            'old_email': old_email,
            'new_email': new_email,
            'change_date': change_date,
            'security_settings_url': security_settings_url,
            'help_url': help_url,
            'security_url': security_url,
            'support_email': self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')
        }

        html_content = self.base._render_template('email_changed.html', context)
        plain_content = f"""
Hi {user_name},

This email confirms that your CivicQ account email address was successfully changed.

Previous Email: {old_email}
New Email: {new_email}
Changed: {change_date}

From now on:
- Use {new_email} to log in to CivicQ
- All future notifications will be sent to your new email
- Your old email address will no longer work for login

If you didn't change your email:
Your account may have been compromised. Contact our support team immediately at {self.base._send_email.__self__.__dict__.get('EMAIL_FROM', 'support@civicq.org')}

Security Tips:
- Use a strong, unique password
- Enable two-factor authentication
- Never share your password
- Review account activity regularly

Review Security Settings: {security_settings_url}

This notification was sent to both your old and new email addresses for security purposes.

Best regards,
The CivicQ Team
        """

        return self.base._send_email(
            to_email=to_email,
            subject="Email Address Changed - CivicQ",
            html_content=html_content,
            plain_content=plain_content,
            category="email_changed"
        )


# Global system email service instance
system_email_service = SystemEmailService(base_service)
