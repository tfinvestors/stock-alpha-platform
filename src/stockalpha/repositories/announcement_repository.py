# src/stockalpha/repositories/announcement_repository.py
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from stockalpha.api.schemas import AnnouncementCreate, AnnouncementRead
from stockalpha.models.entities import Announcement
from stockalpha.repositories.base_repository import BaseRepository


class AnnouncementRepository(
    BaseRepository[Announcement, AnnouncementCreate, AnnouncementCreate]
):
    def __init__(self):
        super().__init__(Announcement)

    def get_by_company(
        self, db: Session, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[Announcement]:
        """Get announcements for a specific company"""
        return (
            db.query(Announcement)
            .filter(Announcement.company_id == company_id)
            .order_by(Announcement.date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_category(
        self, db: Session, category: str, skip: int = 0, limit: int = 100
    ) -> List[Announcement]:
        """Get announcements by primary category"""
        return (
            db.query(Announcement)
            .filter(Announcement.primary_category == category)
            .order_by(Announcement.date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_date_range(
        self,
        db: Session,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Announcement]:
        """Get announcements within a date range"""
        query = db.query(Announcement).filter(Announcement.date >= start_date)

        if end_date:
            query = query.filter(Announcement.date <= end_date)

        return query.order_by(Announcement.date.desc()).offset(skip).limit(limit).all()

    def get_filtered(
        self,
        db: Session,
        company_id: Optional[int] = None,
        category: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Announcement]:
        """Get announcements with various filters applied"""
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
