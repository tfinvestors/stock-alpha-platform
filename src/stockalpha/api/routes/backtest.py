# src/stockalpha/api/routes/backtest.py
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from stockalpha.api.schemas import BacktestCreate, BacktestRead
from stockalpha.repositories import get_backtest_repository
from stockalpha.utils.database import get_db

router = APIRouter()


# Dependency for the backtest repository
def get_backtest_repo():
    return get_backtest_repository()


@router.post("/backtests/", response_model=BacktestRead)
def create_backtest(
    backtest: BacktestCreate,
    db: Session = Depends(get_db),
    repo=Depends(get_backtest_repo),
):
    """Create a new backtest"""
    return repo.create(db, obj_in=backtest)


@router.get("/backtests/", response_model=List[BacktestRead])
def list_backtests(
    skip: int = 0,
    limit: int = 100,
    strategy_type: Optional[str] = None,
    min_return: Optional[float] = None,
    db: Session = Depends(get_db),
    repo=Depends(get_backtest_repo),
):
    """List backtests with optional filtering"""
    return repo.get_filtered(
        db, strategy_type=strategy_type, min_return=min_return, skip=skip, limit=limit
    )


@router.get("/backtests/{backtest_id}", response_model=BacktestRead)
def get_backtest(
    backtest_id: int, db: Session = Depends(get_db), repo=Depends(get_backtest_repo)
):
    """Get a backtest by ID"""
    backtest = repo.get(db, id=backtest_id)
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
    repo=Depends(get_backtest_repo),
):
    """Run a new backtest with specified parameters"""
    # Create a name if not provided
    if not name:
        name = f"{strategy_type} Backtest - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    # Create backtest record
    backtest = BacktestCreate(
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

    return repo.create(db, obj_in=backtest)


@router.delete("/backtests/{backtest_id}", response_model=dict)
def delete_backtest(
    backtest_id: int, db: Session = Depends(get_db), repo=Depends(get_backtest_repo)
):
    """Delete a backtest"""
    backtest = repo.get(db, id=backtest_id)
    if not backtest:
        raise HTTPException(status_code=404, detail="Backtest not found")

    repo.remove(db, id=backtest_id)
    return {"message": "Backtest deleted successfully"}


@router.get("/backtests/compare/", response_model=List[BacktestRead])
def compare_backtests(
    backtest_ids: List[int] = Query(...),
    db: Session = Depends(get_db),
    repo=Depends(get_backtest_repo),
):
    """Compare multiple backtests"""
    backtests = repo.get_multiple_by_ids(db, backtest_ids=backtest_ids)

    # Check if all backtests were found
    if len(backtests) != len(backtest_ids):
        raise HTTPException(status_code=404, detail="One or more backtests not found")

    return backtests
