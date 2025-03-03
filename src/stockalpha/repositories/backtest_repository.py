# src/stockalpha/repositories/backtest_repository.py
from typing import List, Optional

from sqlalchemy.orm import Session

from stockalpha.api.schemas import BacktestCreate, BacktestRead
from stockalpha.models.signals import Backtest
from stockalpha.repositories.base_repository import BaseRepository


class BacktestRepository(BaseRepository[Backtest, BacktestCreate, BacktestCreate]):
    def __init__(self):
        super().__init__(Backtest)

    def get_by_strategy(
        self, db: Session, strategy_type: str, skip: int = 0, limit: int = 100
    ) -> List[Backtest]:
        """Get backtests by strategy type"""
        # Prevent excessive queries
        limit = min(limit, 500)

        return (
            db.query(Backtest)
            .filter(Backtest.strategy_type == strategy_type)
            .order_by(Backtest.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_filtered(
        self,
        db: Session,
        strategy_type: Optional[str] = None,
        min_return: Optional[float] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Backtest]:
        """Get backtests with various filters applied"""
        # Prevent excessive queries
        limit = min(limit, 500)

        query = db.query(Backtest)

        if strategy_type:
            query = query.filter(Backtest.strategy_type == strategy_type)

        if min_return is not None:
            query = query.filter(Backtest.total_return >= min_return)

        return (
            query.order_by(Backtest.created_at.desc()).offset(skip).limit(limit).all()
        )

    def get_multiple_by_ids(
        self, db: Session, backtest_ids: List[int]
    ) -> List[Backtest]:
        """Get multiple backtests by their IDs"""
        return (
            db.query(Backtest)
            .filter(Backtest.id.in_(backtest_ids))
            .order_by(Backtest.created_at.desc())
            .all()
        )
