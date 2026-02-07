"""
Admin API Routes

City staff and moderator endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.base import get_db

router = APIRouter()


@router.get("/modqueue")
async def get_moderation_queue(db: Session = Depends(get_db)):
    """Get moderation queue (admin/moderator only)"""
    return {"message": "Get modqueue endpoint - to be implemented"}


@router.post("/modaction")
async def perform_moderation_action(db: Session = Depends(get_db)):
    """Perform a moderation action (admin/moderator only)"""
    return {"message": "Mod action endpoint - to be implemented"}


@router.get("/metrics")
async def get_metrics(db: Session = Depends(get_db)):
    """Get city metrics (city admin only)"""
    return {"message": "Get metrics endpoint - to be implemented"}


@router.get("/coverage")
async def get_coverage(db: Session = Depends(get_db)):
    """Get answer coverage statistics (city admin only)"""
    return {"message": "Get coverage endpoint - to be implemented"}


@router.get("/export")
async def export_data(db: Session = Depends(get_db)):
    """Export data for public archive (city admin only)"""
    return {"message": "Export data endpoint - to be implemented"}
