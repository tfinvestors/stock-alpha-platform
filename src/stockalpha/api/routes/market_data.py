# src/stockalpha/api/routes/market_data.py
from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from stockalpha.api.schemas import DateRangeParams, PriceDataCreate, PriceDataRead
from stockalpha.models.entities import Company, PriceData
from stockalpha.utils.database import get_db

router = APIRouter()


@router.post("/market-data/", response_model=PriceDataRead)
def create_price_data(price_data: PriceDataCreate, db: Session = Depends(get_db)):
    """Create a new price data point"""
    # Check if company exists
    company = db.query(Company).filter(Company.id == price_data.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Check if data already exists for this date
    existing = (
        db.query(PriceData)
        .filter(
            PriceData.company_id == price_data.company_id,
            PriceData.date == price_data.date,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400, detail="Price data already exists for this date"
        )

    # Create price data
    db_price_data = PriceData(**price_data.dict())
    db.add(db_price_data)
    db.commit()
    db.refresh(db_price_data)

    return db_price_data


@router.post("/market-data/batch/", response_model=List[PriceDataRead])
def create_price_data_batch(
    price_data_list: List[PriceDataCreate], db: Session = Depends(get_db)
):
    """Create multiple price data points in batch"""
    results = []

    for price_data in price_data_list:
        # Check if company exists
        company = db.query(Company).filter(Company.id == price_data.company_id).first()
        if not company:
            continue

        # Check if data already exists for this date
        existing = (
            db.query(PriceData)
            .filter(
                PriceData.company_id == price_data.company_id,
                PriceData.date == price_data.date,
            )
            .first()
        )

        if existing:
            continue

        # Create price data
        db_price_data = PriceData(**price_data.dict())
        db.add(db_price_data)
        results.append(db_price_data)

    db.commit()

    # Refresh all instances
    for result in results:
        db.refresh(result)

    return results


@router.get("/market-data/", response_model=List[PriceDataRead])
def list_price_data(
    skip: int = 0,
    limit: int = 100,
    company_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    """List price data with optional filtering"""
    query = db.query(PriceData)

    if company_id:
        query = query.filter(PriceData.company_id == company_id)

    if start_date:
        query = query.filter(PriceData.date >= start_date)

    if end_date:
        query = query.filter(PriceData.date <= end_date)

    return query.order_by(PriceData.date.desc()).offset(skip).limit(limit).all()


@router.get("/companies/{company_id}/market-data/", response_model=List[PriceDataRead])
def get_company_price_data(
    company_id: int,
    date_range: DateRangeParams = Depends(),
    db: Session = Depends(get_db),
):
    """Get price data for a specific company within a date range"""
    # Set default date range if not provided
    end_date = date_range.end_date or datetime.now().date()
    start_date = date_range.start_date or (end_date - timedelta(days=30))

    # Check if company exists
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Get price data
    price_data = (
        db.query(PriceData)
        .filter(
            PriceData.company_id == company_id,
            PriceData.date >= start_date,
            PriceData.date <= end_date,
        )
        .order_by(PriceData.date)
        .all()
    )

    return price_data
