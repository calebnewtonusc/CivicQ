"""
Moderation and Reporting API Routes
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.base import get_db

router = APIRouter()


@router.post("/reports")
async def submit_report(db: Session = Depends(get_db)):
    """Submit a report"""
    return {"message": "Submit report endpoint - to be implemented"}
