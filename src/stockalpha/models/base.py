from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    """Base class for all database models"""

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate __tablename__ automatically from class name"""
        return type(
            cls
        ).__name__.lower()  # ✅ Use `type(cls).__name__` instead of `cls.__name__`

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary"""
        if not hasattr(self, "__table__"):
            raise AttributeError(
                "Table metadata is missing. Ensure Base.metadata.create_all() is called."
            )
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
