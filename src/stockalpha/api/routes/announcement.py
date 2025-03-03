# src/stockalpha/api/routes/announcement.py
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from stockalpha.api.schemas import AnnouncementCreate, AnnouncementRead
from stockalpha.models.entities import Announcement, Company
from stockalpha.utils.database import get_db

router = APIRouter()


@router.post("/announcements/", response_model=AnnouncementRead)
def create_announcement(
    announcement: AnnouncementCreate, db: Session = Depends(get_db)
):
    """Create a new announcement"""
    # Check if company exists
    company = db.query(Company).filter(Company.id == announcement.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Create announcement
    db_announcement = Announcement(**announcement.dict())
    db.add(db_announcement)
    db.commit()
    db.refresh(db_announcement)

    return db_announcement


@router.get("/announcements/", response_model=List[AnnouncementRead])
def list_announcements(
    skip: int = 0,
    limit: int = 100,
    company_id: Optional[int] = None,
    category: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """List announcements with optional filtering"""
    query = db.query(Announcement)

    if company_id:
        query = query.filter(Announcement.company_id == company_id)

    if category:
        query = query.filter(Announcement.primary_category == category)

    if start_date:
        query = query.filter(Announcement.date >= start_date)

    if end_date:
        query = query.filter(Announcement.date <= end_date)

    return query.order_by(Announcement.date.desc()).offset(skip).limit(limit).all()


@router.get("/announcements/{announcement_id}", response_model=AnnouncementRead)
def get_announcement(announcement_id: int, db: Session = Depends(get_db)):
    """Get an announcement by ID"""
    announcement = (
        db.query(Announcement).filter(Announcement.id == announcement_id).first()
    )
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return announcement


@router.get(
    "/companies/{company_id}/announcements/", response_model=List[AnnouncementRead]
)
def get_company_announcements(
    company_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Get all announcements for a specific company"""
    # Check if company exists
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Get announcements
    announcements = (
        db.query(Announcement)
        .filter(Announcement.company_id == company_id)
        .order_by(Announcement.date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return announcements
