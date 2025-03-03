# src/stockalpha/api/routes/fundamental.py
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from stockalpha.api.schemas import FundamentalDataCreate, FundamentalDataRead
from stockalpha.models.entities import Company, FundamentalData
from stockalpha.utils.database import get_db

router = APIRouter()


@router.post("/fundamentals/", response_model=FundamentalDataRead)
def create_fundamental_data(
    fundamental: FundamentalDataCreate, db: Session = Depends(get_db)
):
    """Create a new fundamental data entry"""
    # Check if company exists
    company = db.query(Company).filter(Company.id == fundamental.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Check if data already exists for this period
    existing = (
        db.query(FundamentalData)
        .filter(
            FundamentalData.company_id == fundamental.company_id,
            FundamentalData.period == fundamental.period,
            FundamentalData.fiscal_year == fundamental.fiscal_year,
            FundamentalData.fiscal_quarter == fundamental.fiscal_quarter,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400, detail="Fundamental data already exists for this period"
        )

    # Create fundamental data
    db_fundamental = FundamentalData(**fundamental.dict())
    db.add(db_fundamental)
    db.commit()
    db.refresh(db_fundamental)

    return db_fundamental


@router.get("/fundamentals/", response_model=List[FundamentalDataRead])
def list_fundamentals(
    skip: int = 0,
    limit: int = 100,
    company_id: Optional[int] = None,
    period: Optional[str] = None,
    fiscal_year: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """List fundamental data with optional filtering"""
    query = db.query(FundamentalData)

    if company_id:
        query = query.filter(FundamentalData.company_id == company_id)

    if period:
        query = query.filter(FundamentalData.period == period)

    if fiscal_year:
        query = query.filter(FundamentalData.fiscal_year == fiscal_year)

    return (
        query.order_by(
            FundamentalData.fiscal_year.desc(), FundamentalData.fiscal_quarter.desc()
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/fundamentals/{fundamental_id}", response_model=FundamentalDataRead)
def get_fundamental(fundamental_id: int, db: Session = Depends(get_db)):
    """Get fundamental data by ID"""
    fundamental = (
        db.query(FundamentalData).filter(FundamentalData.id == fundamental_id).first()
    )
    if not fundamental:
        raise HTTPException(status_code=404, detail="Fundamental data not found")

    return fundamental


@router.get(
    "/companies/{company_id}/fundamentals/", response_model=List[FundamentalDataRead]
)
def get_company_fundamentals(
    company_id: int,
    period: Optional[str] = None,
    limit: int = 8,
    db: Session = Depends(get_db),
):
    """Get fundamental data for a specific company"""
    # Check if company exists
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Build query
    query = db.query(FundamentalData).filter(FundamentalData.company_id == company_id)

    if period:
        query = query.filter(FundamentalData.period == period)

    # Get fundamental data ordered by most recent first
    fundamentals = (
        query.order_by(
            FundamentalData.fiscal_year.desc(), FundamentalData.fiscal_quarter.desc()
        )
        .limit(limit)
        .all()
    )

    return fundamentals
