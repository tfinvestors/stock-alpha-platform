# src/stockalpha/api/routes/signal.py
from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from stockalpha.api.schemas import SignalCreate, SignalRead
from stockalpha.repositories import get_company_repository, get_signal_repository
from stockalpha.utils.database import get_db

router = APIRouter()


# Dependencies for repositories
def get_signal_repo():
    return get_signal_repository()


def get_company_repo():
    return get_company_repository()


@router.post("/signals/", response_model=SignalRead)
def create_signal(
    signal: SignalCreate,
    db: Session = Depends(get_db),
    signal_repo=Depends(get_signal_repo),
    company_repo=Depends(get_company_repo),
):
    """Create a new trading signal"""
    # Check if company exists
    company = company_repo.get(db, id=signal.company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Create signal
    return signal_repo.create(db, obj_in=signal)


@router.get("/signals/", response_model=List[SignalRead])
def list_signals(
    skip: int = 0,
    limit: int = 100,
    company_id: Optional[int] = None,
    signal_type: Optional[str] = None,
    direction: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    min_confidence: float = 0.0,
    db: Session = Depends(get_db),
    repo=Depends(get_signal_repo),
):
    """List trading signals with optional filtering"""
    return repo.get_filtered(
        db,
        company_id=company_id,
        signal_type=signal_type,
        direction=direction,
        start_date=start_date,
        end_date=end_date,
        min_confidence=min_confidence,
        skip=skip,
        limit=limit,
    )


@router.get("/signals/{signal_id}", response_model=SignalRead)
def get_signal(
    signal_id: int, db: Session = Depends(get_db), repo=Depends(get_signal_repo)
):
    """Get a trading signal by ID"""
    signal = repo.get(db, id=signal_id)
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    return signal


@router.get("/signals/latest/", response_model=List[SignalRead])
def get_latest_signals(
    days: int = 1,
    min_confidence: float = 0.7,
    limit: int = 10,
    db: Session = Depends(get_db),
    repo=Depends(get_signal_repo),
):
    """Get latest high-confidence trading signals"""
    return repo.get_latest(db, days=days, min_confidence=min_confidence, limit=limit)


@router.get("/companies/{company_id}/signals/", response_model=List[SignalRead])
def get_company_signals(
    company_id: int,
    days: int = 30,
    signal_type: Optional[str] = None,
    db: Session = Depends(get_db),
    signal_repo=Depends(get_signal_repo),
    company_repo=Depends(get_company_repo),
):
    """Get signals for a specific company"""
    # Check if company exists
    company = company_repo.get(db, id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Get signals
    return signal_repo.get_by_company(
        db, company_id=company_id, days=days, signal_type=signal_type
    )
