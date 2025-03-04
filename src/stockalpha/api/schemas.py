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


class CompanyUpdate(BaseModel):
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
        from_attributes = True  # Changed from orm_mode = True


class AnnouncementRead(AnnouncementBase):
    id: int
    company_id: int
    primary_category: Optional[str] = None
    sub_categories: Optional[List[str]] = None
    sentiment_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Changed from orm_mode = True


class PriceDataRead(PriceDataBase):
    id: int
    company_id: int

    class Config:
        from_attributes = True  # Changed from orm_mode = True


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


# Backtest schemas
class BacktestBase(BaseModel):
    name: str
    strategy_type: str
    parameters: Dict[str, Any]
    start_date: datetime
    end_date: datetime
    description: Optional[str] = None


class BacktestCreate(BacktestBase):
    pass


class BacktestRead(BacktestBase):
    id: int
    total_return: Optional[float] = None
    annualized_return: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    win_rate: Optional[float] = None
    trades_count: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True  # This replaces orm_mode=True in Pydantic v2


# Signal schemas
class SignalBase(BaseModel):
    company_id: int
    date: datetime
    signal_type: str
    direction: int  # 1 for buy, -1 for sell, 0 for hold
    strength: float
    confidence: float
    reason: Optional[str] = None
    source_announcement_id: Optional[int] = None
    source_details: Optional[Dict[str, Any]] = None


class SignalCreate(SignalBase):
    pass


class SignalRead(SignalBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # This replaces orm_mode=True in Pydantic v2


# Fundamental data schemas
class FundamentalDataBase(BaseModel):
    company_id: int
    period: str  # 'annual' or 'quarterly'
    fiscal_year: int
    fiscal_quarter: Optional[int] = None
    report_date: datetime

    # Financial data (core metrics)
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    eps: Optional[float] = None
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    total_equity: Optional[float] = None

    # Extended data stored as JSON (optional)
    income_statement_data: Optional[Dict[str, Any]] = None
    balance_sheet_data: Optional[Dict[str, Any]] = None
    cash_flow_data: Optional[Dict[str, Any]] = None


class FundamentalDataCreate(FundamentalDataBase):
    pass


class FundamentalDataUpdate(BaseModel):
    period: Optional[str] = None
    fiscal_year: Optional[int] = None
    fiscal_quarter: Optional[int] = None
    report_date: Optional[datetime] = None
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    eps: Optional[float] = None
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    total_equity: Optional[float] = None
    income_statement_data: Optional[Dict[str, Any]] = None
    balance_sheet_data: Optional[Dict[str, Any]] = None
    cash_flow_data: Optional[Dict[str, Any]] = None


class FundamentalDataRead(FundamentalDataBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# PriceData update schema
class PriceDataUpdate(BaseModel):
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    adjusted_close: Optional[float] = None
    volume: Optional[float] = None


# Announcement update schema
class AnnouncementUpdate(BaseModel):
    date: Optional[datetime] = None
    title: Optional[str] = None
    content: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None
    primary_category: Optional[str] = None
    sub_categories: Optional[List[str]] = None
    sentiment_score: Optional[float] = None


# Backtest update schema
class BacktestUpdate(BaseModel):
    name: Optional[str] = None
    strategy_type: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: Optional[str] = None
    total_return: Optional[float] = None
    annualized_return: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    win_rate: Optional[float] = None
    trades_count: Optional[int] = None


# Signal update schema
class SignalUpdate(BaseModel):
    date: Optional[datetime] = None
    signal_type: Optional[str] = None
    direction: Optional[int] = None
    strength: Optional[float] = None
    confidence: Optional[float] = None
    reason: Optional[str] = None
    source_announcement_id: Optional[int] = None
    source_details: Optional[Dict[str, Any]] = None
