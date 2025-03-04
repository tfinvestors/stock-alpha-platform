# src/stockalpha/main.py
import argparse
import logging
import sys
from pathlib import Path

from stockalpha.utils.config import settings

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def init_database():
    """Initialize the database"""
    from stockalpha.utils.database import init_db

    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")


def start_api():
    """Start the FastAPI server"""
    import uvicorn

    from stockalpha.api.main import app

    logger.info("Starting API server...")
    uvicorn.run(
        "stockalpha.api.main:app",
        host=settings.api_host,  # Get from settings
        port=settings.api_port,  # Get from settings
        reload=settings.environment == "development",
    )


def start_worker():
    """Start the background worker for processing tasks"""
    try:
        # We're adding an import placeholder for now - you'll implement this later
        # from stockalpha.workers.tasks import process_tasks

        logger.info("Starting background worker...")
        # process_tasks()  # This will be uncommented when the module is created

        # For now, use a placeholder message
        logger.info("Worker started. (Task processing will be implemented later)")
    except ImportError as e:
        logger.error(f"Failed to start worker: {e}")
        logger.info("Worker module will be implemented in a future phase")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Stock Alpha Platform")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Init database command
    init_parser = subparsers.add_parser("init-db", help="Initialize the database")

    # API command
    api_parser = subparsers.add_parser("api", help="Start the API server")

    # Worker command
    worker_parser = subparsers.add_parser("worker", help="Start the background worker")

    # Parse arguments
    args = parser.parse_args()

    # Log the command being executed
    if args.command:
        logger.info(f"Executing command: {args.command}")

    # Run command
    if args.command == "init-db":
        init_database()
    elif args.command == "api":
        start_api()
    elif args.command == "worker":
        start_worker()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
