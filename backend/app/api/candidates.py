"""
Candidate API Routes
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.base import get_db

router = APIRouter()


@router.get("/{candidate_id}")
async def get_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Get candidate details"""
    return {"message": f"Get candidate {candidate_id} - to be implemented"}


@router.post("/{candidate_id}/answers")
async def submit_answer(candidate_id: int, db: Session = Depends(get_db)):
    """Submit a video answer (candidate only)"""
    return {"message": "Submit answer endpoint - to be implemented"}


@router.post("/{candidate_id}/rebuttals")
async def submit_rebuttal(candidate_id: int, db: Session = Depends(get_db)):
    """Submit a rebuttal (candidate only)"""
    return {"message": "Submit rebuttal endpoint - to be implemented"}
