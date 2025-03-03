from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models"""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    @declared_attr
    def __tablename__(cls) -> Mapped[str]:  # ✅ Fix: Explicitly define Mapped[str]
        """Generate __tablename__ automatically from class name"""
        return mapped_column(
            default=cls.__name__.lower()
        )  # ⬅️ Corrected SQLAlchemy ORM mapping

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary"""
        if not hasattr(self, "__table__"):
            raise AttributeError(
                "Table metadata is missing. Ensure Base.metadata.create_all() is called."
            )
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
