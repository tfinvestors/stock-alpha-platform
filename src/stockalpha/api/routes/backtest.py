# src/stockalpha/api/routes/backtest.py
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from stockalpha.api.schemas import BacktestCreate, BacktestRead
from stockalpha.models.signals import Backtest, BacktestTrade
from stockalpha.utils.database import get_db

router = APIRouter()


@router.post("/backtests/", response_model=BacktestRead)
def create_backtest(backtest: BacktestCreate, db: Session = Depends(get_db)):
    """Create a new backtest"""
    db_backtest = Backtest(**backtest.dict())
    db.add(db_backtest)
    db.commit()
    db.refresh(db_backtest)

    return db_backtest


@router.get("/backtests/", response_model=List[BacktestRead])
def list_backtests(
    skip: int = 0,
    limit: int = 100,
    strategy_type: Optional[str] = None,
    min_return: Optional[float] = None,
    db: Session = Depends(get_db),
):
    """List backtests with optional filtering"""
    query = db.query(Backtest)

    if strategy_type:
        query = query.filter(Backtest.strategy_type == strategy_type)

    if min_return is not None:
        query = query.filter(Backtest.total_return >= min_return)

    return query.order_by(Backtest.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/backtests/{backtest_id}", response_model=BacktestRead)
def get_backtest(backtest_id: int, db: Session = Depends(get_db)):
    """Get a backtest by ID"""
    backtest = db.query(Backtest).filter(Backtest.id == backtest_id).first()
    if not backtest:
        raise HTTPException(status_code=404, detail="Backtest not found")

    return backtest


@router.post("/backtests/run/", response_model=BacktestRead)
def run_backtest(
    strategy_type: str = Body(...),
    parameters: Dict[str, Any] = Body(...),
    start_date: datetime = Body(...),
    end_date: datetime = Body(...),
    name: Optional[str] = Body(None),
    db: Session = Depends(get_db),
):
    """Run a new backtest with specified parameters"""
    # This would typically call your backtesting engine
    # For now, we'll just create a placeholder record

    # Create a name if not provided
    if not name:
        name = f"{strategy_type} Backtest - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    # Create backtest record
    backtest = Backtest(
        name=name,
        strategy_type=strategy_type,
        parameters=parameters,
        start_date=start_date,
        end_date=end_date,
        # Placeholder performance metrics - in a real app, these would come from the backtest engine
        total_return=0.0,
        annualized_return=0.0,
        sharpe_ratio=0.0,
        max_drawdown=0.0,
        win_rate=0.0,
        trades_count=0,
    )

    db.add(backtest)
    db.commit()
    db.refresh(backtest)

    return backtest


@router.delete("/backtests/{backtest_id}", response_model=dict)
def delete_backtest(backtest_id: int, db: Session = Depends(get_db)):
    """Delete a backtest"""
    backtest = db.query(Backtest).filter(Backtest.id == backtest_id).first()
    if not backtest:
        raise HTTPException(status_code=404, detail="Backtest not found")

    db.delete(backtest)
    db.commit()

    return {"message": "Backtest deleted successfully"}


@router.get("/backtests/compare/", response_model=List[BacktestRead])
def compare_backtests(
    backtest_ids: List[int] = Query(...), db: Session = Depends(get_db)
):
    """Compare multiple backtests"""
    backtests = db.query(Backtest).filter(Backtest.id.in_(backtest_ids)).all()

    # Check if all backtests were found
    if len(backtests) != len(backtest_ids):
        raise HTTPException(status_code=404, detail="One or more backtests not found")

    return backtests
