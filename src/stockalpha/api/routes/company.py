# src/stockalpha/api/routes/company.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from stockalpha.api.schemas import CompanyCreate, CompanyRead
from stockalpha.models.entities import Company
from stockalpha.utils.database import get_db

router = APIRouter()


@router.post("/companies/", response_model=CompanyRead)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    """Create a new company"""
    # Check if company already exists
    db_company = db.query(Company).filter(Company.ticker == company.ticker).first()
    if db_company:
        raise HTTPException(status_code=400, detail="Company already exists")

    # Create new company
    db_company = Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)

    return db_company


@router.get("/companies/", response_model=List[CompanyRead])
def list_companies(
    skip: int = 0,
    limit: int = 100,
    sector: str = Query(None),
    db: Session = Depends(get_db),
):
    """List companies with optional filtering"""
    query = db.query(Company)

    if sector:
        query = query.filter(Company.sector == sector)

    return query.offset(skip).limit(limit).all()


@router.get("/companies/{company_id}", response_model=CompanyRead)
def get_company(company_id: int, db: Session = Depends(get_db)):
    """Get a company by ID"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return company


@router.get("/companies/ticker/{ticker}", response_model=CompanyRead)
def get_company_by_ticker(ticker: str, db: Session = Depends(get_db)):
    """Get a company by ticker symbol"""
    company = db.query(Company).filter(Company.ticker == ticker).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return company
