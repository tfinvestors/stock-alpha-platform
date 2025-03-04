# tests/unit/test_company_repository.py
import pytest

from stockalpha.api.schemas import CompanyCreate
from stockalpha.repositories.company import company_repository


def test_create_company(db_session):
    """Test creating a company"""
    # Create company data
    company_data = CompanyCreate(
        ticker="AAPL",
        name="Apple Inc.",
        sector="Technology",
        industry="Consumer Electronics",
    )

    # Create company
    company = company_repository.create(db_session, obj_in=company_data)

    # Check company was created
    assert company.id is not None
    assert company.ticker == "AAPL"
    assert company.name == "Apple Inc."
    assert company.sector == "Technology"
    assert company.industry == "Consumer Electronics"

    # Check company can be retrieved
    retrieved = company_repository.get(db_session, id=company.id)
    assert retrieved is not None
    assert retrieved.id == company.id
    assert retrieved.ticker == company.ticker


def test_get_by_ticker(db_session):
    """Test getting a company by ticker"""
    # Create company data
    company_data = CompanyCreate(
        ticker="MSFT",
        name="Microsoft Corporation",
        sector="Technology",
        industry="Software",
    )

    # Create company
    created = company_repository.create(db_session, obj_in=company_data)

    # Get company by ticker
    company = company_repository.get_by_ticker(db_session, ticker="MSFT")

    # Check company was retrieved
    assert company is not None
    assert company.id == created.id
    assert company.ticker == "MSFT"

    # Try to get non-existent company
    non_existent = company_repository.get_by_ticker(db_session, ticker="NONEXISTENT")
    assert non_existent is None
