# src/stockalpha/api/middleware.py
import logging
import time
import traceback
from typing import Callable

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


async def request_handler(request: Request, call_next):
    """Handle requests with logging and timing"""
    start_time = time.time()
    request_id = request.headers.get("X-Request-ID", "unknown")

    logger.info(
        f"Request started: {request.method} {request.url.path} " f"(ID: {request_id})"
    )

    try:
        response = await call_next(request)

        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"(ID: {request_id}) - Status: {response.status_code} - "
            f"Time: {process_time:.4f}s"
        )

        return response

    except Exception as e:
        process_time = time.time() - start_time

        logger.error(
            f"Request failed: {request.method} {request.url.path} "
            f"(ID: {request_id}) - Error: {str(e)} - "
            f"Time: {process_time:.4f}s"
        )
        logger.error(traceback.format_exc())

        # Return a 500 error response
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )


def add_middleware(app: FastAPI):
    """Add middleware to FastAPI application"""

    @app.middleware("http")
    async def middleware(request: Request, call_next: Callable):
        return await request_handler(request, call_next)

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(
            f"HTTP error: {request.method} {request.url.path} - "
            f"Status: {exc.status_code} - Detail: {exc.detail}"
        )
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        logger.warning(
            f"Validation error: {request.method} {request.url.path} - "
            f"Detail: {str(exc)}"
        )
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        logger.error(
            f"Database error: {request.method} {request.url.path} - "
            f"Error: {str(exc)}"
        )
        return JSONResponse(
            status_code=500, content={"detail": "Database error occurred"}
        )
