# src/stockalpha/models/entities.py
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime

from stockalpha.models.base import Base


class Company(Base):
    """Company entity model"""

    ticker = Column(String(10), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    sector = Column(String(100))
    industry = Column(String(100))

    # Relationships
    announcements = relationship("Announcement", back_populates="company")
    price_data = relationship("PriceData", back_populates="company")
    fundamental_data = relationship("FundamentalData", back_populates="company")


class Announcement(Base):
    """Company announcement model"""

    company_id = Column(Integer, ForeignKey("company.id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    source = Column(String(100))
    url = Column(String(500))

    # Classification data
    primary_category = Column(String(50))
    sub_categories = Column(JSON)
    sentiment_score = Column(Float)
    entities = Column(JSON)

    __table_args__ = (
        Index("idx_date_category", "date", "primary_category"),
        Index("idx_company_date", "company_id", "date"),
    )

    # Processing metadata
    processed = Column(Boolean, default=False)

    # Relationships
    company = relationship("Company", back_populates="announcements")


class PriceData(Base):
    """Stock price data model"""

    company_id = Column(Integer, ForeignKey("company.id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    adjusted_close = Column(Float)
    volume = Column(Float)
    __table_args__ = (Index("idx_company_date", "company_id", "date", unique=True),)

    # Relationships
    company = relationship("Company", back_populates="price_data")


class FundamentalData(Base):
    """Company fundamental data model"""

    company_id = Column(Integer, ForeignKey("company.id"), nullable=False, index=True)
    period = Column(String(10), nullable=False)  # 'annual' or 'quarterly'
    fiscal_year = Column(Integer, nullable=False)
    fiscal_quarter = Column(Integer)
    report_date = Column(DateTime, nullable=False)

    # Financial data (core metrics)
    revenue = Column(Float)
    net_income = Column(Float)
    eps = Column(Float)
    total_assets = Column(Float)
    total_liabilities = Column(Float)
    total_equity = Column(Float)

    # Extended data stored as JSON
    income_statement_data = Column(JSON)
    balance_sheet_data = Column(JSON)
    cash_flow_data = Column(JSON)

    __table_args__ = (
        Index("idx_company_fiscal", "company_id", "fiscal_year", "fiscal_quarter"),
        # This unique constraint ensures we don't have duplicate entries
        Index(
            "idx_unique_fundamental",
            "company_id",
            "period",
            "fiscal_year",
            "fiscal_quarter",
            unique=True,
        ),
    )

    # Relationships
    company = relationship("Company", back_populates="fundamental_data")
