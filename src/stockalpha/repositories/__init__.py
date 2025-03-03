# src/stockalpha/repositories/__init__.py
import logging
from functools import lru_cache
from typing import Type, TypeVar

from fastapi import Depends

from stockalpha.repositories.announcement_repository import AnnouncementRepository
from stockalpha.repositories.backtest_repository import BacktestRepository
from stockalpha.repositories.base_repository import BaseRepository
from stockalpha.repositories.company_repository import CompanyRepository
from stockalpha.repositories.fundamental_data_repository import (
    FundamentalDataRepository,
)
from stockalpha.repositories.price_data_repository import PriceDataRepository
from stockalpha.repositories.signal_repository import SignalRepository

logger = logging.getLogger(__name__)

# Type variable for repository types
RepoType = TypeVar("RepoType", bound=BaseRepository)

# Dictionary to store cached repository instances
_repositories = {}


def get_repository(repo_class: Type[RepoType]) -> RepoType:
    """
    Factory function for creating repository instances.

    This function combines lazy initialization with singleton pattern:
    - Creates repository instances only when needed
    - Caches instances for reuse
    - Can be used with FastAPI's dependency injection

    Example usage:
        company_repo = get_repository(CompanyRepository)

    Or with FastAPI:
        @app.get("/companies/")
        def read_companies(
            repo = Depends(lambda: get_repository(CompanyRepository))
        ):
            ...
    """
    if repo_class not in _repositories:
        logger.debug(f"Creating new repository instance: {repo_class.__name__}")
        _repositories[repo_class] = repo_class()

    return _repositories[repo_class]


# Convenience functions for commonly used repositories
def get_company_repository() -> CompanyRepository:
    return get_repository(CompanyRepository)


def get_announcement_repository() -> AnnouncementRepository:
    return get_repository(AnnouncementRepository)


def get_price_data_repository() -> PriceDataRepository:
    return get_repository(PriceDataRepository)


def get_fundamental_data_repository() -> FundamentalDataRepository:
    return get_repository(FundamentalDataRepository)


def get_signal_repository() -> SignalRepository:
    return get_repository(SignalRepository)


def get_backtest_repository() -> BacktestRepository:
    return get_repository(BacktestRepository)


# Log initialization message
logger.info("Repository factory initialized")
