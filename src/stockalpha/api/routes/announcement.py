# src/stockalpha/api/routes/announcement.py
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from stockalpha.api.schemas import AnnouncementCreate, AnnouncementRead
from stockalpha.repositories import get_announcement_repository, get_company_repository
from stockalpha.utils.database import get_db

router = APIRouter()


# Dependencies for repositories
def get_announcement_repo():
    return get_announcement_repository()


def get_company_repo():
    return get_company_repository()


@router.post("/announcements/", response_model=AnnouncementRead)
def create_announcement(
    announcement: AnnouncementCreate,
    db: Session = Depends(get_db),
    announcement_repo=Depends(get_announcement_repo),
    company_repo=Depends(get_company_repo),
):
    """Create a new announcement"""
    # Check if company exists
    company = company_repo.get(db, id=announcement.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Create announcement
    return announcement_repo.create(db, obj_in=announcement)


@router.get("/announcements/", response_model=List[AnnouncementRead])
def list_announcements(
    skip: int = 0,
    limit: int = 100,
    company_id: Optional[int] = None,
    category: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    repo=Depends(get_announcement_repo),
):
    """List announcements with optional filtering"""
    return repo.get_filtered(
        db,
        company_id=company_id,
        category=category,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )


@router.get("/announcements/{announcement_id}", response_model=AnnouncementRead)
def get_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    repo=Depends(get_announcement_repo),
):
    """Get an announcement by ID"""
    announcement = repo.get(db, id=announcement_id)
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return announcement


@router.get(
    "/companies/{company_id}/announcements/", response_model=List[AnnouncementRead]
)
def get_company_announcements(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    announcement_repo=Depends(get_announcement_repo),
    company_repo=Depends(get_company_repo),
):
    """Get all announcements for a specific company"""
    # Check if company exists
    company = company_repo.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Get announcements
    return announcement_repo.get_by_company(
        db, company_id=company_id, skip=skip, limit=limit
    )
