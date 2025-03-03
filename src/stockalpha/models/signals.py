# src/stockalpha/models/signals.py
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


class Signal(Base):
    """Trading signal model"""

    company_id = Column(Integer, ForeignKey("company.id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)

    # Signal data
    signal_type = Column(
        String(50), nullable=False
    )  # 'announcement', 'technical', 'fundamental', 'combined'
    direction = Column(Integer, nullable=False)  # 1 for buy, -1 for sell, 0 for hold
    strength = Column(Float, nullable=False)  # 0.0 to 1.0
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    reason = Column(Text)

    # Source information
    source_announcement_id = Column(
        Integer, ForeignKey("announcement.id"), nullable=True
    )
    source_details = Column(JSON)

    __table_args__ = (
        Index("idx_company_date", "company_id", "date"),
        Index("idx_confidence", "confidence"),
        Index("idx_signal_type", "signal_type"),
        # Composite index for common filtering patterns
        Index("idx_signal_lookup", "company_id", "signal_type", "date"),
    )

    # Relationships
    company = relationship("Company")
    source_announcement = relationship("Announcement")


class Backtest(Base):
    """Backtest results model"""

    name = Column(String(100), nullable=False)
    description = Column(Text)
    strategy_type = Column(String(50), nullable=False)
    parameters = Column(JSON, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    # Performance metrics
    total_return = Column(Float)
    annualized_return = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    win_rate = Column(Float)

    # Detailed results
    trades_count = Column(Integer)
    trades = Column(JSON)  # List of trade details
    equity_curve = Column(JSON)  # Daily equity values

    # Metadata
    created_by = Column(String(100))
