# src/stockalpha/api/routes/signal.py
from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from stockalpha.api.schemas import SignalCreate, SignalRead
from stockalpha.models.entities import Company
from stockalpha.models.signals import Signal
from stockalpha.utils.database import get_db

router = APIRouter()


@router.post("/signals/", response_model=SignalRead)
def create_signal(signal: SignalCreate, db: Session = Depends(get_db)):
    """Create a new trading signal"""
    # Check if company exists
    company = db.query(Company).filter(Company.id == signal.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Create signal
    db_signal = Signal(**signal.dict())
    db.add(db_signal)
    db.commit()
    db.refresh(db_signal)

    return db_signal


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
):
    """List trading signals with optional filtering"""
    query = db.query(Signal)

    if company_id:
        query = query.filter(Signal.company_id == company_id)

    if signal_type:
        query = query.filter(Signal.signal_type == signal_type)

    if direction is not None:
        query = query.filter(Signal.direction == direction)

    if start_date:
        query = query.filter(Signal.date >= start_date)

    if end_date:
        query = query.filter(Signal.date <= end_date)

    if min_confidence > 0:
        query = query.filter(Signal.confidence >= min_confidence)

    return query.order_by(Signal.date.desc()).offset(skip).limit(limit).all()


@router.get("/signals/{signal_id}", response_model=SignalRead)
def get_signal(signal_id: int, db: Session = Depends(get_db)):
    """Get a trading signal by ID"""
    signal = db.query(Signal).filter(Signal.id == signal_id).first()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    return signal


@router.get("/signals/latest/", response_model=List[SignalRead])
def get_latest_signals(
    days: int = 1,
    min_confidence: float = 0.7,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """Get latest high-confidence trading signals"""
    cutoff_date = datetime.now().date() - timedelta(days=days)

    signals = (
        db.query(Signal)
        .filter(Signal.date >= cutoff_date, Signal.confidence >= min_confidence)
        .order_by(Signal.confidence.desc())
        .limit(limit)
        .all()
    )

    return signals


@router.get("/companies/{company_id}/signals/", response_model=List[SignalRead])
def get_company_signals(
    company_id: int,
    days: int = 30,
    signal_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get signals for a specific company"""
    # Check if company exists
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Calculate date range
    cutoff_date = datetime.now().date() - timedelta(days=days)

    # Build query
    query = db.query(Signal).filter(
        Signal.company_id == company_id, Signal.date >= cutoff_date
    )

    if signal_type:
        query = query.filter(Signal.signal_type == signal_type)

    # Get signals
    signals = query.order_by(Signal.date.desc()).all()

    return signals
