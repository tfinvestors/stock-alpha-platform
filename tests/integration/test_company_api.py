# tests/integration/test_company_api.py
import pytest


def test_create_company(client):
    """Test create company API endpoint"""
    # Create company
    response = client.post(
        "/api/v1/companies/",
        json={
            "ticker": "GOOG",
            "name": "Alphabet Inc.",
            "sector": "Technology",
            "industry": "Internet Content & Information",
        },
    )

    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "GOOG"
    assert data["name"] == "Alphabet Inc."
    assert "id" in data

    # Try to create duplicate company
    response = client.post(
        "/api/v1/companies/",
        json={
            "ticker": "GOOG",
            "name": "Alphabet Inc.",
            "sector": "Technology",
            "industry": "Internet Content & Information",
        },
    )

    # Check response
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_get_company(client):
    """Test get company API endpoint"""
    # Create a company first
    create_response = client.post(
        "/api/v1/companies/",
        json={
            "ticker": "AMZN",
            "name": "Amazon.com, Inc.",
            "sector": "Consumer Cyclical",
            "industry": "Internet Retail",
        },
    )
    company_id = create_response.json()["id"]

    # Get company by ID
    response = client.get(f"/api/v1/companies/{company_id}")

    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AMZN"
    assert data["name"] == "Amazon.com, Inc."

    # Get company by ticker
    response = client.get("/api/v1/companies/ticker/AMZN")

    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AMZN"
    assert data["id"] == company_id

    # Try to get non-existent company
    response = client.get("/api/v1/companies/999999")
    assert response.status_code == 404

    response = client.get("/api/v1/companies/ticker/NONEXISTENT")
    assert response.status_code == 404
