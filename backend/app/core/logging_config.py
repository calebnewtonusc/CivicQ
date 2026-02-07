"""
Logging Configuration for CivicQ

Structured logging setup with JSON formatting for production.
"""

import logging
import sys
from pythonjsonlogger import jsonlogger
from app.core.config import settings


def setup_logging():
    """Configure application logging"""

    # Root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # Remove existing handlers
    logger.handlers = []

    # Create handler
    handler = logging.StreamHandler(sys.stdout)

    # Use JSON formatter in production, simple formatter in development
    if settings.ENVIRONMENT == "production":
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    return logger
