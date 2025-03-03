# src/stockalpha/repositories/price_data_repository.py
from datetime import date, datetime
from typing import List, Optional, Set, Tuple

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from stockalpha.api.schemas import PriceDataCreate, PriceDataRead
from stockalpha.models.entities import PriceData
from stockalpha.repositories.base_repository import BaseRepository


class PriceDataRepository(BaseRepository[PriceData, PriceDataCreate, PriceDataCreate]):
    def __init__(self):
        super().__init__(PriceData)

    def get_by_company(
        self,
        db: Session,
        company_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[PriceData]:
        """Get price data for a specific company with optional date range"""
        query = db.query(PriceData).filter(PriceData.company_id == company_id)

        if start_date:
            query = query.filter(PriceData.date >= start_date)

        if end_date:
            query = query.filter(PriceData.date <= end_date)

        return query.order_by(PriceData.date).offset(skip).limit(limit).all()

    def get_by_date(
        self, db: Session, company_id: int, date_value: date
    ) -> Optional[PriceData]:
        """Get price data for a specific date"""
        return (
            db.query(PriceData)
            .filter(PriceData.company_id == company_id, PriceData.date == date_value)
            .first()
        )

    def create_batch(
        self, db: Session, price_data_list: List[PriceDataCreate]
    ) -> List[PriceData]:
        """Create multiple price data entries in batch - optimized version"""
        if not price_data_list:
            return []

        # Get unique company_ids and dates from the input list
        company_ids = list({p.company_id for p in price_data_list})
        dates = list({p.date for p in price_data_list})

        # Bulk retrieve existing entries
        existing_entries = (
            db.query(PriceData)
            .filter(PriceData.company_id.in_(company_ids), PriceData.date.in_(dates))
            .all()
        )

        # Create a set of (company_id, date) tuples for quick lookup
        existing_keys: Set[Tuple[int, datetime]] = {
            (entry.company_id, entry.date) for entry in existing_entries
        }

        # Create new objects for entries that don't exist yet
        new_entries = []
        for price_data in price_data_list:
            key = (price_data.company_id, price_data.date)
            if key not in existing_keys:
                # Try to use model_dump for Pydantic v2 compatibility
                try:
                    obj_data = price_data.model_dump()
                except AttributeError:
                    obj_data = jsonable_encoder(price_data)

                new_entries.append(PriceData(**obj_data))

        # Bulk insert new entries
        if new_entries:
            db.bulk_save_objects(new_entries)
            db.commit()

        # Return all created objects
        result = []
        for entry in new_entries:
            db.refresh(entry)
            result.append(entry)

        return result
