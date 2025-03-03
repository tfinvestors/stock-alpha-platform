# src/stockalpha/repositories/fundamental_data_repository.py
from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from stockalpha.api.schemas import FundamentalDataCreate, FundamentalDataRead
from stockalpha.models.entities import FundamentalData
from stockalpha.repositories.base_repository import BaseRepository


class FundamentalDataRepository(
    BaseRepository[FundamentalData, FundamentalDataCreate, FundamentalDataCreate]
):
    def __init__(self):
        super().__init__(FundamentalData)

    def get_by_company(
        self, db: Session, company_id: int, period: Optional[str] = None, limit: int = 8
    ) -> List[FundamentalData]:
        """Get fundamental data for a specific company"""
        # Prevent excessive queries
        limit = min(limit, 1000)

        query = db.query(FundamentalData).filter(
            FundamentalData.company_id == company_id
        )

        if period:
            query = query.filter(FundamentalData.period == period)

        return (
            query.order_by(
                FundamentalData.fiscal_year.desc(),
                FundamentalData.fiscal_quarter.desc(),
            )
            .limit(limit)
            .all()
        )

    def get_by_period(
        self,
        db: Session,
        company_id: int,
        fiscal_year: int,
        fiscal_quarter: Optional[int] = None,
        period: Optional[str] = None,
    ) -> Optional[FundamentalData]:
        """Get fundamental data by fiscal period"""
        query = db.query(FundamentalData).filter(
            FundamentalData.company_id == company_id,
            FundamentalData.fiscal_year == fiscal_year,
        )

        if fiscal_quarter is not None:
            query = query.filter(FundamentalData.fiscal_quarter == fiscal_quarter)

        if period:
            query = query.filter(FundamentalData.period == period)

        return query.first()

    def get_filtered(
        self,
        db: Session,
        company_id: Optional[int] = None,
        period: Optional[str] = None,
        fiscal_year: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FundamentalData]:
        """Get fundamental data with various filters applied"""
        # Prevent excessive queries
        limit = min(limit, 1000)

        query = db.query(FundamentalData)

        if company_id:
            query = query.filter(FundamentalData.company_id == company_id)

        if period:
            query = query.filter(FundamentalData.period == period)

        if fiscal_year:
            query = query.filter(FundamentalData.fiscal_year == fiscal_year)

        return (
            query.order_by(
                FundamentalData.fiscal_year.desc(),
                FundamentalData.fiscal_quarter.desc(),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_batch(
        self, db: Session, fundamental_data_list: List[FundamentalDataCreate]
    ) -> List[FundamentalData]:
        """Create multiple fundamental data entries in batch"""
        if not fundamental_data_list:
            return []

        # Check for duplicates and prepare new entries
        new_entries = []
        for data in fundamental_data_list:
            # Check if data already exists for this period
            existing = (
                db.query(FundamentalData)
                .filter(
                    FundamentalData.company_id == data.company_id,
                    FundamentalData.period == data.period,
                    FundamentalData.fiscal_year == data.fiscal_year,
                    FundamentalData.fiscal_quarter == data.fiscal_quarter,
                )
                .first()
            )

            if not existing:
                # Try to use model_dump for Pydantic v2 compatibility
                try:
                    obj_data = data.model_dump()
                except AttributeError:
                    obj_data = jsonable_encoder(data)

                new_entries.append(FundamentalData(**obj_data))

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
