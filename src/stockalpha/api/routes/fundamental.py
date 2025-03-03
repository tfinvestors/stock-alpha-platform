# src/stockalpha/api/routes/fundamental.py
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from stockalpha.api.schemas import FundamentalDataCreate, FundamentalDataRead
from stockalpha.repositories import get_repository
from stockalpha.repositories.company_repository import CompanyRepository
from stockalpha.repositories.fundamental_data_repository import (
    FundamentalDataRepository,
)
from stockalpha.utils.database import get_db

router = APIRouter()


# Repository dependencies
def get_fundamental_repo():
    return get_repository(FundamentalDataRepository)


def get_company_repo():
    return get_repository(CompanyRepository)


@router.post("/fundamentals/", response_model=FundamentalDataRead)
def create_fundamental_data(
    fundamental: FundamentalDataCreate,
    db: Session = Depends(get_db),
    fundamental_repo=Depends(get_fundamental_repo),
    company_repo=Depends(get_company_repo),
):
    """Create a new fundamental data entry"""
    # Check if company exists
    company = company_repo.get(db, id=fundamental.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Check if data already exists for this period
    existing = fundamental_repo.get_by_period(
        db,
        company_id=fundamental.company_id,
        fiscal_year=fundamental.fiscal_year,
        fiscal_quarter=fundamental.fiscal_quarter,
        period=fundamental.period,
    )

    if existing:
        raise HTTPException(
            status_code=400, detail="Fundamental data already exists for this period"
        )

    # Create fundamental data
    return fundamental_repo.create(db, obj_in=fundamental)


@router.get("/fundamentals/", response_model=List[FundamentalDataRead])
def list_fundamentals(
    skip: int = 0,
    limit: int = 100,
    company_id: Optional[int] = None,
    period: Optional[str] = None,
    fiscal_year: Optional[int] = None,
    db: Session = Depends(get_db),
    repo=Depends(get_fundamental_repo),
):
    """List fundamental data with optional filtering"""
    return repo.get_filtered(
        db,
        company_id=company_id,
        period=period,
        fiscal_year=fiscal_year,
        skip=skip,
        limit=limit,
    )


@router.get("/fundamentals/{fundamental_id}", response_model=FundamentalDataRead)
def get_fundamental(
    fundamental_id: int,
    db: Session = Depends(get_db),
    repo=Depends(get_fundamental_repo),
):
    """Get fundamental data by ID"""
    fundamental = repo.get(db, id=fundamental_id)
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
    fundamental_repo=Depends(get_fundamental_repo),
    company_repo=Depends(get_company_repo),
):
    """Get fundamental data for a specific company"""
    # Check if company exists
    company = company_repo.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Get fundamental data
    return fundamental_repo.get_by_company(
        db, company_id=company_id, period=period, limit=limit
    )
