# src/stockalpha/repositories/signal_repository.py
from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from stockalpha.api.schemas import SignalCreate, SignalRead
from stockalpha.models.signals import Signal
from stockalpha.repositories.base_repository import BaseRepository


class SignalRepository(BaseRepository[Signal, SignalCreate, SignalCreate]):
    def __init__(self):
        super().__init__(Signal)

    def get_by_company(
        self,
        db: Session,
        company_id: int,
        days: int = 30,
        signal_type: Optional[str] = None,
    ) -> List[Signal]:
        """Get signals for a specific company"""
        # Prevent excessive queries
        days = min(days, 365)  # Limit to 1 year max

        cutoff_date = datetime.now().date() - timedelta(days=days)

        query = db.query(Signal).filter(
            Signal.company_id == company_id, Signal.date >= cutoff_date
        )

        if signal_type:
            query = query.filter(Signal.signal_type == signal_type)

        return query.order_by(Signal.date.desc()).all()

    def get_latest(
        self, db: Session, days: int = 1, min_confidence: float = 0.7, limit: int = 10
    ) -> List[Signal]:
        """Get latest high-confidence signals"""
        # Prevent excessive queries
        limit = min(limit, 500)
        days = min(days, 30)  # Reasonable max for "latest"

        cutoff_date = datetime.now().date() - timedelta(days=days)

        return (
            db.query(Signal)
            .filter(Signal.date >= cutoff_date, Signal.confidence >= min_confidence)
            .order_by(Signal.confidence.desc())
            .limit(limit)
            .all()
        )

    def get_filtered(
        self,
        db: Session,
        company_id: Optional[int] = None,
        signal_type: Optional[str] = None,
        direction: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        min_confidence: float = 0.0,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Signal]:
        """Get signals with various filters applied"""
        # Prevent excessive queries
        limit = min(limit, 500)

        query = db.query(Signal)

        if company_id:
            query = query.filter(Signal.company_id == company_id)

        if signal_type:
            query = query.filter(Signal.signal_type == signal_type)

        if direction is not None:
            query = query.filter(Signal.direction == direction)

        if start_date:
            query = query.filter(Signal.date >= start_date)

        if end_date:
            query = query.filter(Signal.date <= end_date)

        if min_confidence > 0:
            query = query.filter(Signal.confidence >= min_confidence)

        return query.order_by(Signal.date.desc()).offset(skip).limit(limit).all()

    def create_batch(
        self, db: Session, signal_list: List[SignalCreate]
    ) -> List[Signal]:
        """Create multiple signals in batch"""
        if not signal_list:
            return []

        # Prepare objects for bulk insert
        new_entries = []
        for signal in signal_list:
            # Try to use model_dump for Pydantic v2 compatibility
            try:
                obj_data = signal.model_dump()
            except AttributeError:
                obj_data = jsonable_encoder(signal)

            new_entries.append(Signal(**obj_data))

        # Bulk insert
        if new_entries:
            db.bulk_save_objects(new_entries)
            db.commit()

        # Return all created objects
        result = []
        for entry in new_entries:
            db.refresh(entry)
            result.append(entry)

        return result
