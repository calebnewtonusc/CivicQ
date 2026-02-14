"""
Unit tests for City, CityStaff, and CityInvitation models.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

from app.models.city import (
    City,
    CityStaff,
    CityInvitation,
    CityStatus,
    CityStaffRole,
)
from app.models.user import User


class TestCityModel:
    """Test City model functionality."""

    def test_create_city(self, db_session):
        """Test creating a new city."""
        city = City(
            name="San Francisco",
            slug="san-francisco",
            state="CA",
            primary_contact_name="Jane Clerk",
            primary_contact_email="clerk@sf.gov",
        )
        db_session.add(city)
        db_session.commit()

        assert city.id is not None
        assert city.name == "San Francisco"
        assert city.slug == "san-francisco"
        assert city.state == "CA"
        assert city.status == CityStatus.PENDING_VERIFICATION

    def test_city_unique_slug(self, db_session):
        """Test that city slug must be unique."""
        city1 = City(
            name="San Francisco",
            slug="san-francisco",
            state="CA",
            primary_contact_name="Jane Clerk",
            primary_contact_email="clerk1@sf.gov",
        )
        city2 = City(
            name="San Francisco County",
            slug="san-francisco",
            state="CA",
            primary_contact_name="John Clerk",
            primary_contact_email="clerk2@sf.gov",
        )

        db_session.add(city1)
        db_session.commit()

        db_session.add(city2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_city_status_transitions(self, db_session):
        """Test city status transitions."""
        city = City(
            name="Boston",
            slug="boston",
            state="MA",
            primary_contact_name="City Clerk",
            primary_contact_email="clerk@boston.gov",
            status=CityStatus.PENDING_VERIFICATION,
        )
        db_session.add(city)
        db_session.commit()

        # Verify city
        city.status = CityStatus.ACTIVE
        city.verified_at = datetime.utcnow()
        city.verified_by = "admin@civicq.com"
        db_session.commit()

        assert city.status == CityStatus.ACTIVE
        assert city.verified_at is not None

    def test_city_with_full_details(self, db_session):
        """Test creating a city with all details."""
        city = City(
            name="Seattle",
            slug="seattle",
            state="WA",
            county="King County",
            population=753675,
            primary_contact_name="City Clerk",
            primary_contact_email="clerk@seattle.gov",
            primary_contact_phone="206-555-1234",
            primary_contact_title="City Clerk",
            official_email_domain="seattle.gov",
            timezone="America/Los_Angeles",
        )
        db_session.add(city)
        db_session.commit()

        assert city.county == "King County"
        assert city.population == 753675
        assert city.timezone == "America/Los_Angeles"

    def test_city_branding(self, db_session):
        """Test city branding configuration."""
        city = City(
            name="Portland",
            slug="portland",
            state="OR",
            primary_contact_name="Clerk",
            primary_contact_email="clerk@portland.gov",
            logo_url="https://example.com/logo.png",
            primary_color="#0066CC",
            secondary_color="#FF6600",
        )
        db_session.add(city)
        db_session.commit()

        assert city.logo_url == "https://example.com/logo.png"
        assert city.primary_color == "#0066CC"
        assert city.secondary_color == "#FF6600"

    def test_city_settings(self, db_session):
        """Test city settings configuration."""
        city = City(
            name="Austin",
            slug="austin",
            state="TX",
            primary_contact_name="Clerk",
            primary_contact_email="clerk@austin.gov",
            settings={
                "require_voter_verification": True,
                "allow_anonymous_questions": False,
                "moderation_mode": "pre-approval",
            },
        )
        db_session.add(city)
        db_session.commit()

        assert city.settings["require_voter_verification"] is True
        assert city.settings["moderation_mode"] == "pre-approval"

    def test_city_features(self, db_session):
        """Test city feature flags."""
        city = City(
            name="Denver",
            slug="denver",
            state="CO",
            primary_contact_name="Clerk",
            primary_contact_email="clerk@denver.gov",
            features={
                "video_answers": True,
                "ballot_integration": True,
                "two_factor_auth": False,
            },
        )
        db_session.add(city)
        db_session.commit()

        assert city.features["video_answers"] is True
        assert city.features["ballot_integration"] is True

    def test_city_election_info(self, db_session):
        """Test city election information."""
        from datetime import date

        city = City(
            name="Phoenix",
            slug="phoenix",
            state="AZ",
            primary_contact_name="Clerk",
            primary_contact_email="clerk@phoenix.gov",
            next_election_date=date(2024, 11, 5),
            election_info_url="https://phoenix.gov/elections",
        )
        db_session.add(city)
        db_session.commit()

        assert city.next_election_date == date(2024, 11, 5)
        assert city.election_info_url is not None

    def test_city_onboarding(self, db_session):
        """Test city onboarding tracking."""
        city = City(
            name="Chicago",
            slug="chicago",
            state="IL",
            primary_contact_name="Clerk",
            primary_contact_email="clerk@chicago.gov",
            onboarding_completed=False,
            onboarding_step=2,
            onboarding_data={"current_step": "ballot_import"},
        )
        db_session.add(city)
        db_session.commit()

        assert city.onboarding_completed is False
        assert city.onboarding_step == 2


class TestCityStaffModel:
    """Test CityStaff model functionality."""

    def test_create_city_staff(self, db_session):
        """Test adding staff to a city."""
        city = City(
            name="Boston",
            slug="boston",
            state="MA",
            primary_contact_name="Clerk",
            primary_contact_email="clerk@boston.gov",
        )
        db_session.add(city)

        user = User(
            email="staff@boston.gov",
            hashed_password="hashed",
        )
        db_session.add(user)
        db_session.commit()

        staff = CityStaff(
            city_id=city.id,
            user_id=user.id,
            role=CityStaffRole.ADMIN,
        )
        db_session.add(staff)
        db_session.commit()

        assert staff.id is not None
        assert staff.city_id == city.id
        assert staff.user_id == user.id
        assert staff.role == CityStaffRole.ADMIN
        assert staff.is_active is True

    def test_city_staff_roles(self, db_session):
        """Test different staff roles."""
        city = City(
            name="Seattle",
            slug="seattle",
            state="WA",
            primary_contact_name="Clerk",
            primary_contact_email="clerk@seattle.gov",
        )
        db_session.add(city)
        db_session.commit()

        roles = [
            CityStaffRole.OWNER,
            CityStaffRole.ADMIN,
            CityStaffRole.EDITOR,
            CityStaffRole.MODERATOR,
            CityStaffRole.VIEWER,
        ]

        for i, role in enumerate(roles):
            user = User(
                email=f"{role.value}@seattle.gov",
                hashed_password="hashed",
            )
            db_session.add(user)
            db_session.commit()

            staff = CityStaff(
                city_id=city.id,
                user_id=user.id,
                role=role,
            )
            db_session.add(staff)
            db_session.commit()

            assert staff.role == role

    def test_city_staff_invitation_tracking(self, db_session):
        """Test staff invitation tracking."""
        city = City(
            name="Portland",
            slug="portland",
            state="OR",
            primary_contact_name="Clerk",
            primary_contact_email="clerk@portland.gov",
        )
        db_session.add(city)

        inviter = User(email="admin@portland.gov", hashed_password="hashed")
        invitee = User(email="staff@portland.gov", hashed_password="hashed")
        db_session.add_all([inviter, invitee])
        db_session.commit()

        staff = CityStaff(
            city_id=city.id,
            user_id=invitee.id,
            role=CityStaffRole.EDITOR,
            invited_by_id=inviter.id,
        )
        db_session.add(staff)
        db_session.commit()

        assert staff.invited_by_id == inviter.id
        assert staff.invited_at is not None

    def test_city_staff_relationship(self, db_session):
        """Test relationship between city and staff."""
        city = City(
            name="Austin",
            slug="austin",
            state="TX",
            primary_contact_name="Clerk",
            primary_contact_email="clerk@austin.gov",
        )
        db_session.add(city)
        db_session.commit()

        # Add multiple staff members
        for i in range(3):
            user = User(email=f"staff{i}@austin.gov", hashed_password="hashed")
            db_session.add(user)
            db_session.commit()

            staff = CityStaff(
                city_id=city.id,
                user_id=user.id,
                role=CityStaffRole.EDITOR,
            )
            db_session.add(staff)
        db_session.commit()

        db_session.refresh(city)
        assert len(city.staff) == 3

    def test_city_staff_cascade_delete(self, db_session):
        """Test that staff records are deleted when city is deleted."""
        city = City(
            name="Denver",
            slug="denver",
            state="CO",
            primary_contact_name="Clerk",
            primary_contact_email="clerk@denver.gov",
        )
        db_session.add(city)

        user = User(email="staff@denver.gov", hashed_password="hashed")
        db_session.add(user)
        db_session.commit()

        staff = CityStaff(
            city_id=city.id,
            user_id=user.id,
            role=CityStaffRole.ADMIN,
        )
        db_session.add(staff)
        db_session.commit()

        city_id = city.id
        db_session.delete(city)
        db_session.commit()

        # Staff record should be deleted
        result = db_session.query(CityStaff).filter_by(city_id=city_id).first()
        assert result is None


class TestCityInvitationModel:
    """Test CityInvitation model functionality."""

    def test_create_city_invitation(self, db_session):
        """Test creating a city staff invitation."""
        city = City(
            name="Miami",
            slug="miami",
            state="FL",
            primary_contact_name="Clerk",
            primary_contact_email="clerk@miami.gov",
        )
        db_session.add(city)

        inviter = User(email="admin@miami.gov", hashed_password="hashed")
        db_session.add(inviter)
        db_session.commit()

        invitation = CityInvitation(
            city_id=city.id,
            email="newstaff@miami.gov",
            role=CityStaffRole.EDITOR,
            token="unique_token_123",
            invited_by_id=inviter.id,
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        db_session.add(invitation)
        db_session.commit()

        assert invitation.id is not None
        assert invitation.email == "newstaff@miami.gov"
        assert invitation.role == CityStaffRole.EDITOR
        assert invitation.accepted is False

    def test_city_invitation_acceptance(self, db_session):
        """Test accepting a city staff invitation."""
        city = City(
            name="Philadelphia",
            slug="philadelphia",
            state="PA",
            primary_contact_name="Clerk",
            primary_contact_email="clerk@phila.gov",
        )
        db_session.add(city)

        inviter = User(email="admin@phila.gov", hashed_password="hashed")
        acceptor = User(email="staff@phila.gov", hashed_password="hashed")
        db_session.add_all([inviter, acceptor])
        db_session.commit()

        invitation = CityInvitation(
            city_id=city.id,
            email="staff@phila.gov",
            role=CityStaffRole.MODERATOR,
            token="token_456",
            invited_by_id=inviter.id,
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        db_session.add(invitation)
        db_session.commit()

        # Accept invitation
        invitation.accepted = True
        invitation.accepted_at = datetime.utcnow()
        invitation.accepted_by_id = acceptor.id
        db_session.commit()

        assert invitation.accepted is True
        assert invitation.accepted_at is not None

    def test_city_invitation_expiration(self, db_session):
        """Test invitation expiration."""
        city = City(
            name="Houston",
            slug="houston",
            state="TX",
            primary_contact_name="Clerk",
            primary_contact_email="clerk@houston.gov",
        )
        db_session.add(city)

        inviter = User(email="admin@houston.gov", hashed_password="hashed")
        db_session.add(inviter)
        db_session.commit()

        # Expired invitation
        invitation = CityInvitation(
            city_id=city.id,
            email="staff@houston.gov",
            role=CityStaffRole.VIEWER,
            token="token_789",
            invited_by_id=inviter.id,
            expires_at=datetime.utcnow() - timedelta(days=1),
        )
        db_session.add(invitation)
        db_session.commit()

        assert invitation.expires_at < datetime.utcnow()

    def test_city_invitation_unique_token(self, db_session):
        """Test that invitation tokens must be unique."""
        city = City(
            name="Phoenix",
            slug="phoenix",
            state="AZ",
            primary_contact_name="Clerk",
            primary_contact_email="clerk@phoenix.gov",
        )
        db_session.add(city)

        inviter = User(email="admin@phoenix.gov", hashed_password="hashed")
        db_session.add(inviter)
        db_session.commit()

        token = "duplicate_token"

        invitation1 = CityInvitation(
            city_id=city.id,
            email="staff1@phoenix.gov",
            role=CityStaffRole.EDITOR,
            token=token,
            invited_by_id=inviter.id,
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        db_session.add(invitation1)
        db_session.commit()

        invitation2 = CityInvitation(
            city_id=city.id,
            email="staff2@phoenix.gov",
            role=CityStaffRole.EDITOR,
            token=token,
            invited_by_id=inviter.id,
            expires_at=datetime.utcnow() + timedelta(days=7),
        )
        db_session.add(invitation2)

        with pytest.raises(IntegrityError):
            db_session.commit()
