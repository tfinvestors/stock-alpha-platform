# src/stockalpha/api/main.py
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from stockalpha.api.routes import (
    announcement,
    backtest,
    company,
    fundamental,
    market_data,
    signal,
)
from stockalpha.utils.config import settings

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title=settings.api_title,
        description=settings.api_description,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict this to specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(
        company.router, prefix=settings.api_v1_prefix, tags=["Companies"]
    )
    app.include_router(
        announcement.router, prefix=settings.api_v1_prefix, tags=["Announcements"]
    )
    app.include_router(
        market_data.router, prefix=settings.api_v1_prefix, tags=["Market Data"]
    )
    app.include_router(
        fundamental.router, prefix=settings.api_v1_prefix, tags=["Fundamentals"]
    )
    app.include_router(signal.router, prefix=settings.api_v1_prefix, tags=["Signals"])
    app.include_router(
        backtest.router, prefix=settings.api_v1_prefix, tags=["Backtesting"]
    )

    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
