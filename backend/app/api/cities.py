"""
City Onboarding and Management API

Endpoints for city registration, verification, setup, and management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
import secrets
import re

from app.models.city import City, CityStaff, CityInvitation, CityStatus, CityStaffRole
from app.models.user import User, UserRole, VerificationStatus
from app.models.ballot import Ballot, Contest, Candidate, Measure, ContestType
from app.models.question import Question
from app.schemas.city import (
    CityRegistrationRequest,
    CityVerificationRequest,
    CityBrandingUpdate,
    CityElectionUpdate,
    CitySettingsUpdate,
    CityOnboardingComplete,
    CityStaffInviteRequest,
    CityStaffUpdateRequest,
    CityStaffInvitationAcceptRequest,
    CityResponse,
    CityDetailResponse,
    CityListResponse,
    CityDashboardStats,
    BallotImportRequest,
    BallotImportResponse,
    CityStaffResponse,
)
from app.core.security import get_password_hash, get_current_user, create_access_token
from app.models.base import get_db


router = APIRouter(prefix="/cities", tags=["cities"])


def create_slug(name: str, state: str) -> str:
    """Create URL-friendly slug from city name"""
    # Remove special characters and convert to lowercase
    slug = re.sub(r'[^a-z0-9\s-]', '', name.lower())
    slug = re.sub(r'\s+', '-', slug.strip())
    # Add state code
    return f"{slug}-{state.lower()}"


def get_city_staff(db: Session, user: User, city_id: int, min_role: CityStaffRole = CityStaffRole.VIEWER) -> CityStaff:
    """
    Get city staff record and verify permissions.

    Args:
        db: Database session
        user: Current user
        city_id: City ID
        min_role: Minimum required role

    Returns:
        CityStaff record

    Raises:
        HTTPException: If user is not staff or doesn't have required role
    """
    # Superusers can access any city
    if user.is_superuser:
        city = db.query(City).filter(City.id == city_id).first()
        if not city:
            raise HTTPException(status_code=404, detail="City not found")
        # Create virtual staff record for superuser
        return CityStaff(
            city_id=city_id,
            user_id=user.id,
            role=CityStaffRole.OWNER,
            is_active=True
        )

    # Check if user is staff for this city
    staff = db.query(CityStaff).filter(
        CityStaff.city_id == city_id,
        CityStaff.user_id == user.id,
        CityStaff.is_active == True
    ).first()

    if not staff:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this city"
        )

    # Role hierarchy: owner > admin > editor > moderator > viewer
    role_hierarchy = {
        CityStaffRole.VIEWER: 0,
        CityStaffRole.MODERATOR: 1,
        CityStaffRole.EDITOR: 2,
        CityStaffRole.ADMIN: 3,
        CityStaffRole.OWNER: 4,
    }

    if role_hierarchy[staff.role] < role_hierarchy[min_role]:
        raise HTTPException(
            status_code=403,
            detail=f"This action requires {min_role.value} role or higher"
        )

    # Update last access
    staff.last_access = datetime.utcnow()
    db.commit()

    return staff


# Public endpoints


@router.post("/register", response_model=CityResponse, status_code=status.HTTP_201_CREATED)
async def register_city(
    request: CityRegistrationRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new city.

    This creates:
    1. A new city record (pending verification)
    2. A user account for the primary contact
    3. A city staff record linking them as owner

    The city will be in pending_verification status until approved by a superuser.
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.primary_contact_email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists. Please log in and contact support."
        )

    # Create slug
    slug = create_slug(request.name, request.state)

    # Check if slug already exists
    existing_city = db.query(City).filter(City.slug == slug).first()
    if existing_city:
        raise HTTPException(
            status_code=400,
            detail="A city with this name already exists in this state. Please contact support."
        )

    # Create city record
    city = City(
        name=request.name,
        slug=slug,
        state=request.state.upper(),
        county=request.county,
        population=request.population,
        primary_contact_name=request.primary_contact_name,
        primary_contact_email=request.primary_contact_email,
        primary_contact_phone=request.primary_contact_phone,
        primary_contact_title=request.primary_contact_title,
        official_email_domain=request.official_email_domain,
        documentation_urls=request.documentation_urls,
        status=CityStatus.PENDING_VERIFICATION,
        onboarding_step=1,  # Start at step 1 (verification pending)
    )
    db.add(city)
    db.flush()  # Get city ID

    # Create user account for primary contact
    user = User(
        email=request.primary_contact_email,
        hashed_password=get_password_hash(request.password),
        full_name=request.primary_contact_name,
        phone_number=request.primary_contact_phone,
        role=UserRole.CITY_STAFF,
        city_id=str(city.id),
        city_name=city.name,
        verification_status=VerificationStatus.PENDING,
    )
    db.add(user)
    db.flush()  # Get user ID

    # Link user as city owner
    staff = CityStaff(
        city_id=city.id,
        user_id=user.id,
        role=CityStaffRole.OWNER,
        is_active=True,
    )
    db.add(staff)

    db.commit()
    db.refresh(city)

    return city


@router.get("/list", response_model=CityListResponse)
async def list_cities(
    state: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all cities.

    Public endpoint to show all active cities using CivicQ.
    """
    query = db.query(City)

    # Filter by state
    if state:
        query = query.filter(City.state == state.upper())

    # Filter by status
    if status:
        query = query.filter(City.status == status)
    else:
        # By default, only show active cities
        query = query.filter(City.status == CityStatus.ACTIVE)

    # Get total
    total = query.count()

    # Get cities
    cities = query.order_by(City.name).offset(skip).limit(limit).all()

    return {"cities": cities, "total": total}


@router.get("/{city_id}", response_model=CityDetailResponse)
async def get_city(
    city_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get city details (requires staff access)"""
    # Verify access
    get_city_staff(db, current_user, city_id, CityStaffRole.VIEWER)

    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    # Load staff with user details
    staff_list = []
    for staff in city.staff:
        user = db.query(User).filter(User.id == staff.user_id).first()
        staff_response = CityStaffResponse(
            id=staff.id,
            user_id=staff.user_id,
            role=staff.role.value,
            is_active=staff.is_active,
            invited_at=staff.invited_at,
            last_access=staff.last_access,
            user_email=user.email if user else None,
            user_full_name=user.full_name if user else None,
        )
        staff_list.append(staff_response)

    # Create response
    response = CityDetailResponse(
        **city.__dict__,
        status=city.status.value,
        staff=staff_list
    )

    return response


# City Management


@router.put("/{city_id}/branding", response_model=CityResponse)
async def update_branding(
    city_id: int,
    request: CityBrandingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update city branding (requires admin role)"""
    get_city_staff(db, current_user, city_id, CityStaffRole.ADMIN)

    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    # Update branding
    if request.logo_url is not None:
        city.logo_url = request.logo_url
    if request.primary_color is not None:
        city.primary_color = request.primary_color
    if request.secondary_color is not None:
        city.secondary_color = request.secondary_color

    # Move to next onboarding step if applicable
    if city.onboarding_step == 3:
        city.onboarding_step = 4

    db.commit()
    db.refresh(city)

    return city


@router.put("/{city_id}/election", response_model=CityResponse)
async def update_election(
    city_id: int,
    request: CityElectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update election information (requires admin role)"""
    get_city_staff(db, current_user, city_id, CityStaffRole.ADMIN)

    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    if request.next_election_date is not None:
        city.next_election_date = request.next_election_date
    if request.election_info_url is not None:
        city.election_info_url = request.election_info_url

    db.commit()
    db.refresh(city)

    return city


@router.put("/{city_id}/settings", response_model=CityResponse)
async def update_settings(
    city_id: int,
    request: CitySettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update city settings (requires admin role)"""
    get_city_staff(db, current_user, city_id, CityStaffRole.ADMIN)

    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    if request.timezone is not None:
        city.timezone = request.timezone
    if request.settings is not None:
        city.settings = request.settings
    if request.features is not None:
        city.features = request.features

    db.commit()
    db.refresh(city)

    return city


@router.post("/{city_id}/complete-onboarding", response_model=CityResponse)
async def complete_onboarding(
    city_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark city onboarding as complete"""
    get_city_staff(db, current_user, city_id, CityStaffRole.ADMIN)

    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    # Verify city is verified
    if city.status != CityStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail="City must be verified before completing onboarding"
        )

    city.onboarding_completed = True
    city.onboarding_step = 999  # Completed
    city.onboarding_data = None  # Clear temporary data

    db.commit()
    db.refresh(city)

    return city


# Staff Management


@router.post("/{city_id}/staff/invite", status_code=status.HTTP_201_CREATED)
async def invite_staff(
    city_id: int,
    request: CityStaffInviteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Invite someone to join city staff (requires admin role)"""
    get_city_staff(db, current_user, city_id, CityStaffRole.ADMIN)

    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        # Check if already staff
        existing_staff = db.query(CityStaff).filter(
            CityStaff.city_id == city_id,
            CityStaff.user_id == existing_user.id
        ).first()
        if existing_staff:
            raise HTTPException(
                status_code=400,
                detail="This user is already a staff member"
            )

    # Create invitation
    token = secrets.token_urlsafe(32)
    invitation = CityInvitation(
        city_id=city_id,
        email=request.email,
        role=CityStaffRole[request.role.upper()],
        token=token,
        invited_by_id=current_user.id,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(invitation)
    db.commit()

    # TODO: Send email with invitation link
    # invitation_url = f"{settings.FRONTEND_URL}/cities/{city_id}/accept-invite/{token}"

    return {
        "message": "Invitation sent",
        "token": token,
        "expires_at": invitation.expires_at
    }


@router.post("/accept-invite")
async def accept_invitation(
    request: CityStaffInvitationAcceptRequest,
    db: Session = Depends(get_db)
):
    """Accept a city staff invitation"""
    # Find invitation
    invitation = db.query(CityInvitation).filter(
        CityInvitation.token == request.token,
        CityInvitation.accepted == False
    ).first()

    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found or already accepted")

    # Check expiration
    if invitation.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invitation has expired")

    # Check if user exists
    user = db.query(User).filter(User.email == invitation.email).first()

    if not user:
        # Create new user
        if not request.password:
            raise HTTPException(
                status_code=400,
                detail="Password required for new account"
            )
        user = User(
            email=invitation.email,
            hashed_password=get_password_hash(request.password),
            role=UserRole.CITY_STAFF,
            city_id=str(invitation.city_id),
            verification_status=VerificationStatus.VERIFIED,  # Email verified by invitation
        )
        db.add(user)
        db.flush()

    # Add to city staff
    staff = CityStaff(
        city_id=invitation.city_id,
        user_id=user.id,
        role=invitation.role,
        invited_by_id=invitation.invited_by_id,
        is_active=True,
    )
    db.add(staff)

    # Mark invitation as accepted
    invitation.accepted = True
    invitation.accepted_at = datetime.utcnow()
    invitation.accepted_by_id = user.id

    db.commit()

    # Create access token
    access_token = create_access_token({"sub": user.email})

    return {
        "message": "Invitation accepted",
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/{city_id}/staff", response_model=List[CityStaffResponse])
async def list_staff(
    city_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List city staff members"""
    get_city_staff(db, current_user, city_id, CityStaffRole.VIEWER)

    staff_list = db.query(CityStaff).filter(CityStaff.city_id == city_id).all()

    response = []
    for staff in staff_list:
        user = db.query(User).filter(User.id == staff.user_id).first()
        response.append(CityStaffResponse(
            id=staff.id,
            user_id=staff.user_id,
            role=staff.role.value,
            is_active=staff.is_active,
            invited_at=staff.invited_at,
            last_access=staff.last_access,
            user_email=user.email if user else None,
            user_full_name=user.full_name if user else None,
        ))

    return response


# Dashboard


@router.get("/{city_id}/dashboard", response_model=CityDashboardStats)
async def get_dashboard_stats(
    city_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get city dashboard statistics"""
    get_city_staff(db, current_user, city_id, CityStaffRole.VIEWER)

    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    # Get counts
    total_voters = db.query(func.count(User.id)).filter(
        User.city_id == str(city_id),
        User.role == UserRole.VOTER
    ).scalar()

    total_ballots = db.query(func.count(Ballot.id)).filter(
        Ballot.city_id == str(city_id)
    ).scalar()

    total_contests = db.query(func.count(Contest.id)).join(Ballot).filter(
        Ballot.city_id == str(city_id)
    ).scalar()

    total_candidates = db.query(func.count(Candidate.id)).join(Contest).join(Ballot).filter(
        Ballot.city_id == str(city_id)
    ).scalar()

    total_questions = db.query(func.count(Question.id)).join(Contest).join(Ballot).filter(
        Ballot.city_id == str(city_id)
    ).scalar()

    # Recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)

    questions_this_week = db.query(func.count(Question.id)).join(Contest).join(Ballot).filter(
        Ballot.city_id == str(city_id),
        Question.created_at >= week_ago
    ).scalar()

    voters_this_week = db.query(func.count(User.id)).filter(
        User.city_id == str(city_id),
        User.role == UserRole.VOTER,
        User.created_at >= week_ago
    ).scalar()

    # Engagement metrics
    avg_questions_per_contest = total_questions / total_contests if total_contests > 0 else 0

    # Calculate average votes per question
    total_votes = db.query(func.sum(Question.upvotes + Question.downvotes)).join(Contest).join(Ballot).filter(
        Ballot.city_id == str(city_id)
    ).scalar() or 0
    avg_votes_per_question = total_votes / total_questions if total_questions > 0 else 0

    # Days until election
    days_until_election = None
    if city.next_election_date:
        delta = city.next_election_date - datetime.utcnow().date()
        days_until_election = delta.days if delta.days >= 0 else None

    return CityDashboardStats(
        total_voters=total_voters or 0,
        total_questions=total_questions or 0,
        total_candidates=total_candidates or 0,
        total_ballots=total_ballots or 0,
        total_contests=total_contests or 0,
        questions_this_week=questions_this_week or 0,
        voters_this_week=voters_this_week or 0,
        avg_questions_per_contest=avg_questions_per_contest,
        avg_votes_per_question=avg_votes_per_question,
        next_election_date=city.next_election_date,
        days_until_election=days_until_election,
    )


# Ballot Import


@router.post("/{city_id}/import-ballot", response_model=BallotImportResponse)
async def import_ballot(
    city_id: int,
    request: BallotImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Import ballot data.

    This is a simplified import for the setup wizard.
    Allows city staff to quickly import election data.
    """
    get_city_staff(db, current_user, city_id, CityStaffRole.EDITOR)

    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    # Create ballot
    ballot = Ballot(
        city_id=str(city_id),
        city_name=city.name,
        election_date=request.election_date,
        source_metadata=request.source_metadata or {"imported_by": "setup_wizard"},
        is_published=False,  # Not published until city activates it
    )
    db.add(ballot)
    db.flush()

    contests_created = 0
    candidates_created = 0
    measures_created = 0

    # Create contests
    for contest_data in request.contests:
        contest = Contest(
            ballot_id=ballot.id,
            type=ContestType[contest_data.type.upper()],
            title=contest_data.title,
            office=contest_data.office,
            jurisdiction=contest_data.jurisdiction,
            seat_count=contest_data.seat_count,
            description=contest_data.description,
            display_order=contests_created,
        )
        db.add(contest)
        db.flush()
        contests_created += 1

        # Create candidates
        if contest_data.type.lower() == "race":
            for candidate_data in contest_data.candidates:
                candidate = Candidate(
                    contest_id=contest.id,
                    name=candidate_data.name,
                    email=candidate_data.email,
                    phone=candidate_data.phone,
                    filing_id=candidate_data.filing_id,
                    website=candidate_data.website,
                    display_order=candidates_created,
                )
                db.add(candidate)
                candidates_created += 1

        # Create measure
        elif contest_data.type.lower() == "measure":
            measure = Measure(
                contest_id=contest.id,
                measure_number=contest_data.measure_number,
                measure_text=contest_data.measure_text or "",
                summary=contest_data.summary,
            )
            db.add(measure)
            measures_created += 1

    # Update city ballot count
    city.total_ballots = db.query(func.count(Ballot.id)).filter(
        Ballot.city_id == str(city_id)
    ).scalar()

    # Update onboarding step
    if city.onboarding_step == 2:
        city.onboarding_step = 3

    db.commit()

    return BallotImportResponse(
        ballot_id=ballot.id,
        contests_created=contests_created,
        candidates_created=candidates_created,
        measures_created=measures_created,
        message=f"Successfully imported ballot with {contests_created} contests"
    )


# Admin endpoints


@router.post("/{city_id}/verify", response_model=CityResponse)
async def verify_city(
    city_id: int,
    request: CityVerificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Verify a city (superuser only)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Only superusers can verify cities"
        )

    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    if request.approved:
        city.status = CityStatus.ACTIVE
        city.verified_at = datetime.utcnow()
        city.verified_by = current_user.email
        city.verification_method = request.verification_method
        city.verification_notes = request.verification_notes
        city.onboarding_step = 2  # Move to ballot import step
    else:
        city.status = CityStatus.SUSPENDED
        city.verification_notes = request.verification_notes

    db.commit()
    db.refresh(city)

    return city
