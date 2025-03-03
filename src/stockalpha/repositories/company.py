# src/stockalpha/repositories/company.py
from typing import List, Optional

from sqlalchemy.orm import Session

from stockalpha.api.schemas import CompanyCreate, CompanyRead, CompanyUpdate
from stockalpha.models.entities import Company
from stockalpha.repositories.base_repository import BaseRepository


class CompanyRepository(
    BaseRepository[Company, CompanyCreate, CompanyUpdate, CompanyRead]
):
    """Repository for Company model"""

    def __init__(self):
        super().__init__(Company)

    def get_by_ticker(self, db: Session, ticker: str) -> Optional[Company]:
        """Get company by ticker symbol"""
        return db.query(Company).filter(Company.ticker == ticker).first()

    def get_by_sector(
        self, db: Session, sector: str, skip: int = 0, limit: int = 100
    ) -> List[Company]:
        """Get companies by sector"""
        return (
            db.query(Company)
            .filter(Company.sector == sector)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_industry(
        self, db: Session, industry: str, skip: int = 0, limit: int = 100
    ) -> List[Company]:
        """Get companies by industry"""
        return (
            db.query(Company)
            .filter(Company.industry == industry)
            .offset(skip)
            .limit(limit)
            .all()
        )


# Create an instance to be used by dependents
company_repository = CompanyRepository()
