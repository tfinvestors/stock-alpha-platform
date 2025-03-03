# src/stockalpha/api/routes/market_data.py
from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from stockalpha.api.schemas import DateRangeParams, PriceDataCreate, PriceDataRead
from stockalpha.repositories import get_repository
from stockalpha.repositories.company_repository import CompanyRepository
from stockalpha.repositories.price_data_repository import PriceDataRepository
from stockalpha.utils.database import get_db

router = APIRouter()


# Repository dependencies
def get_price_repo():
    return get_repository(PriceDataRepository)


def get_company_repo():
    return get_repository(CompanyRepository)


@router.post("/market-data/", response_model=PriceDataRead)
def create_price_data(
    price_data: PriceDataCreate,
    db: Session = Depends(get_db),
    price_repo=Depends(get_price_repo),
    company_repo=Depends(get_company_repo),
):
    """Create a new price data point"""
    # Check if company exists
    company = company_repo.get(db, id=price_data.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Check if data already exists for this date
    existing = price_repo.get_by_date(
        db, company_id=price_data.company_id, date_value=price_data.date
    )

    if existing:
        raise HTTPException(
            status_code=400, detail="Price data already exists for this date"
        )

    # Create price data
    return price_repo.create(db, obj_in=price_data)


@router.post("/market-data/batch/", response_model=List[PriceDataRead])
def create_price_data_batch(
    price_data_list: List[PriceDataCreate],
    db: Session = Depends(get_db),
    repo=Depends(get_price_repo),
):
    """Create multiple price data points in batch"""
    return repo.create_batch(db, price_data_list=price_data_list)


@router.get("/market-data/", response_model=List[PriceDataRead])
def list_price_data(
    skip: int = 0,
    limit: int = 100,
    company_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    repo=Depends(get_price_repo),
):
    """List price data with optional filtering"""
    if company_id:
        return repo.get_by_company(
            db,
            company_id=company_id,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit,
        )
    else:
        # For general queries without company_id, use the model directly
        query = db.query(repo.model)

        if start_date:
            query = query.filter(repo.model.date >= start_date)

        if end_date:
            query = query.filter(repo.model.date <= end_date)

        return query.order_by(repo.model.date.desc()).offset(skip).limit(limit).all()


@router.get("/companies/{company_id}/market-data/", response_model=List[PriceDataRead])
def get_company_price_data(
    company_id: int,
    date_range: DateRangeParams = Depends(),
    db: Session = Depends(get_db),
    price_repo=Depends(get_price_repo),
    company_repo=Depends(get_company_repo),
):
    """Get price data for a specific company within a date range"""
    # Set default date range if not provided
    end_date = date_range.end_date or datetime.now().date()
    start_date = date_range.start_date or (end_date - timedelta(days=30))

    # Check if company exists
    company = company_repo.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Get price data
    return price_repo.get_by_company(
        db,
        company_id=company_id,
        start_date=start_date,
        end_date=end_date,
        limit=1000,  # Higher limit for time series data
    )
