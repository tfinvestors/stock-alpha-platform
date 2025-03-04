# src/stockalpha/api/routes/company.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from stockalpha.api.schemas import CompanyCreate, CompanyRead
from stockalpha.repositories import get_repository
from stockalpha.repositories.company import CompanyRepository
from stockalpha.utils.database import get_db

router = APIRouter()


# Repository dependency
def get_company_repo():
    return get_repository(CompanyRepository)


@router.post("/companies/", response_model=CompanyRead)
def create_company(
    company: CompanyCreate,
    db: Session = Depends(get_db),
    repo=Depends(get_company_repo),
):
    """Create a new company"""
    # Check if company already exists
    db_company = repo.get_by_ticker(db, ticker=company.ticker)
    if db_company:
        raise HTTPException(status_code=400, detail="Company already exists")

    # Create new company
    return repo.create(db, obj_in=company)


@router.get("/companies/", response_model=List[CompanyRead])
def list_companies(
    skip: int = 0,
    limit: int = 100,
    sector: str = Query(None),
    industry: str = Query(None),  # Added industry filter
    db: Session = Depends(get_db),
    repo=Depends(get_company_repo),
):
    """List companies with optional filtering"""
    if sector:
        return repo.get_by_sector(db, sector=sector, skip=skip, limit=limit)
    elif industry:
        return repo.get_by_industry(db, industry=industry, skip=skip, limit=limit)
    else:
        return repo.get_multi(db, skip=skip, limit=limit)


@router.get("/companies/{company_id}", response_model=CompanyRead)
def get_company(
    company_id: int, db: Session = Depends(get_db), repo=Depends(get_company_repo)
):
    """Get a company by ID"""
    company = repo.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return company


@router.get("/companies/ticker/{ticker}", response_model=CompanyRead)
def get_company_by_ticker(
    ticker: str, db: Session = Depends(get_db), repo=Depends(get_company_repo)
):
    """Get a company by ticker symbol"""
    company = repo.get_by_ticker(db, ticker=ticker)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return company
