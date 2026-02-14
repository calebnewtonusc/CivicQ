"""
Ballot and Contest Discovery API Routes

Handles ballot lookup, city discovery, and election information.
"""

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from app.models.base import get_db
from app.models.ballot import Ballot, Contest, Candidate
from app.schemas.ballot import BallotResponse, ContestResponse, CandidateResponse

router = APIRouter()


@router.get("/cities")
async def get_cities(db: Session = Depends(get_db)):
    """
    Get list of cities with active elections

    Returns all cities that have published ballots in the system.
    Public endpoint - no authentication required.

    Args:
        db: Database session

    Returns:
        List of cities with election information
    """
    # Query distinct cities with published ballots
    cities = db.query(
        Ballot.city_id,
        Ballot.city_name,
        func.count(Ballot.id).label('ballot_count'),
        func.min(Ballot.election_date).label('next_election')
    ).filter(
        Ballot.is_published == True
    ).group_by(
        Ballot.city_id,
        Ballot.city_name
    ).order_by(
        Ballot.city_name
    ).all()

    return {
        "cities": [
            {
                "city_id": city.city_id,
                "city_name": city.city_name,
                "ballot_count": city.ballot_count,
                "next_election": city.next_election.isoformat() if city.next_election else None
            }
            for city in cities
        ]
    }


@router.get("/elections")
async def get_elections(
    city: str = Query(..., description="City name or city ID"),
    db: Session = Depends(get_db)
):
    """
    Get elections for a city

    Returns all published ballots/elections for a specific city.
    Public endpoint - no authentication required.

    Args:
        city: City name or city ID
        db: Database session

    Returns:
        List of elections/ballots for the city
    """
    # Query ballots for the city (match by city_id or city_name)
    ballots = db.query(Ballot).filter(
        Ballot.is_published == True,
        (Ballot.city_id == city) | (Ballot.city_name.ilike(f"%{city}%"))
    ).order_by(
        Ballot.election_date.desc()
    ).all()

    if not ballots:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No elections found for city: {city}"
        )

    return {
        "elections": [
            {
                "id": ballot.id,
                "city_id": ballot.city_id,
                "city_name": ballot.city_name,
                "election_date": ballot.election_date.isoformat(),
                "version": ballot.version,
                "contest_count": len(ballot.contests)
            }
            for ballot in ballots
        ]
    }


@router.get("/ballot", response_model=BallotResponse)
async def get_ballot(
    city: str = Query(..., description="City name or city ID"),
    election_date: Optional[str] = Query(None, description="Election date (YYYY-MM-DD)"),
    address: Optional[str] = Query(None, description="User address for personalized ballot"),
    db: Session = Depends(get_db)
):
    """
    Get personalized ballot based on city and optional address

    Returns a ballot with all contests and candidates.
    If address is provided, can be used for jurisdiction-specific filtering (future enhancement).

    Args:
        city: City name or city ID
        election_date: Optional election date filter
        address: Optional user address for personalization
        db: Database session

    Returns:
        Ballot with contests and candidates

    Raises:
        HTTPException 404: If no ballot found
    """
    # Build query
    query = db.query(Ballot).filter(
        Ballot.is_published == True,
        (Ballot.city_id == city) | (Ballot.city_name.ilike(f"%{city}%"))
    )

    # Filter by election date if provided
    if election_date:
        try:
            parsed_date = date.fromisoformat(election_date)
            query = query.filter(Ballot.election_date == parsed_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid election_date format. Use YYYY-MM-DD"
            )
    else:
        # Get the most recent/upcoming election if no date specified
        query = query.order_by(Ballot.election_date.desc())

    ballot = query.first()

    if not ballot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No ballot found for city: {city}"
        )

    # Load contests with candidates and question counts
    contests_data = []
    for contest in ballot.contests:
        # Get candidate count and question count
        candidate_count = len(contest.candidates)
        question_count = db.query(func.count(distinct('*'))).filter_by(contest_id=contest.id).scalar() or 0

        # Get answered count (questions with at least one video answer)
        from app.models.question import Question
        from app.models.answer import VideoAnswer
        answered_count = db.query(func.count(distinct(Question.id))).join(
            VideoAnswer, VideoAnswer.question_id == Question.id
        ).filter(
            Question.contest_id == contest.id
        ).scalar() or 0

        contest_response = ContestResponse(
            id=contest.id,
            ballot_id=contest.ballot_id,
            contest_type=contest.type,
            title=contest.title,
            office=contest.office,
            jurisdiction=contest.jurisdiction,
            candidates=[CandidateResponse.model_validate(c) for c in contest.candidates],
            question_count=question_count,
            answered_count=answered_count
        )
        contests_data.append(contest_response)

    # Create ballot response
    ballot_response = BallotResponse(
        id=ballot.id,
        city=ballot.city_name,
        election_date=ballot.election_date,
        contests=contests_data,
        created_at=ballot.created_at
    )

    return ballot_response


@router.get("/ballots", response_model=List[BallotResponse])
async def get_ballots(
    city_id: Optional[str] = Query(None, description="Filter by city ID"),
    is_published: Optional[bool] = Query(None, description="Filter by published status"),
    db: Session = Depends(get_db)
):
    """
    Get all ballots (plural endpoint)

    Returns all ballots, optionally filtered by city or publication status.
    Public endpoint - no authentication required.

    Args:
        city_id: Optional city ID filter
        is_published: Optional published status filter
        db: Database session

    Returns:
        List of ballots
    """
    query = db.query(Ballot)

    if city_id:
        query = query.filter(Ballot.city_id == city_id)

    if is_published is not None:
        query = query.filter(Ballot.is_published == is_published)

    ballots = query.order_by(Ballot.election_date.desc()).all()

    return [BallotResponse.model_validate(ballot) for ballot in ballots]


@router.get("/ballots/{ballot_id}", response_model=BallotResponse)
async def get_ballot_by_id(
    ballot_id: int,
    db: Session = Depends(get_db)
):
    """
    Get ballot by ID

    Returns a specific ballot with all contests and candidates.
    Public endpoint - no authentication required.

    Args:
        ballot_id: Ballot ID
        db: Database session

    Returns:
        Ballot with contests and candidates

    Raises:
        HTTPException 404: If ballot not found
    """
    ballot = db.query(Ballot).filter(
        Ballot.id == ballot_id,
        Ballot.is_published == True
    ).first()

    if not ballot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ballot not found"
        )

    return BallotResponse.model_validate(ballot)


@router.get("/ballots/city/{city_id}/date/{election_date}", response_model=BallotResponse)
async def get_ballot_by_city_and_date(
    city_id: str,
    election_date: str,
    db: Session = Depends(get_db)
):
    """
    Get ballot by city and election date

    Returns a ballot for a specific city and election date.
    Public endpoint - no authentication required.

    Args:
        city_id: City ID
        election_date: Election date (YYYY-MM-DD)
        db: Database session

    Returns:
        Ballot with contests and candidates

    Raises:
        HTTPException 404: If ballot not found
        HTTPException 400: If date format is invalid
    """
    try:
        parsed_date = date.fromisoformat(election_date)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid election_date format. Use YYYY-MM-DD"
        )

    ballot = db.query(Ballot).filter(
        Ballot.city_id == city_id,
        Ballot.election_date == parsed_date,
        Ballot.is_published == True
    ).first()

    if not ballot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No ballot found for city {city_id} on {election_date}"
        )

    return BallotResponse.model_validate(ballot)
