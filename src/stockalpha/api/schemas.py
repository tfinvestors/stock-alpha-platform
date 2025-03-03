# src/stockalpha/api/schemas.py
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


# Base schemas
class CompanyBase(BaseModel):
    ticker: str
    name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None


class AnnouncementBase(BaseModel):
    date: datetime
    title: str
    content: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None


class PriceDataBase(BaseModel):
    date: datetime
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: float
    adjusted_close: Optional[float] = None
    volume: Optional[float] = None


# Create schemas
class CompanyCreate(CompanyBase):
    pass


class AnnouncementCreate(AnnouncementBase):
    company_id: int


class PriceDataCreate(PriceDataBase):
    company_id: int


# Response schemas
class CompanyRead(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AnnouncementRead(AnnouncementBase):
    id: int
    company_id: int
    primary_category: Optional[str] = None
    sub_categories: Optional[List[str]] = None
    sentiment_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class PriceDataRead(PriceDataBase):
    id: int
    company_id: int

    class Config:
        orm_mode = True


# Query schemas
class DateRangeParams(BaseModel):
    start_date: date
    end_date: Optional[date] = None


class AnnouncementQuery(DateRangeParams):
    company_id: Optional[int] = Field(default=None, gt=0)
    category: Optional[str] = None
    sentiment_min: Optional[float] = None
    sentiment_max: Optional[float] = None


class PriceDataQuery(DateRangeParams):
    interval: Optional[str] = "1d"  # 1d, 1h, etc.
