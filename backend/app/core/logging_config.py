"""
Logging Configuration for CivicQ

Structured logging setup with JSON formatting for production.
Includes request ID tracking, performance logging, and error context.
"""

import logging
import sys
import time
from typing import Any, Dict
from pythonjsonlogger import jsonlogger
from app.core.config import settings
from app.core.request_id import RequestIdFilter


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that adds additional context to logs
    """

    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)

        # Add timestamp
        log_record["timestamp"] = self.formatTime(record)

        # Add environment
        log_record["environment"] = settings.ENVIRONMENT

        # Add request ID if available
        if hasattr(record, "request_id") and record.request_id:
            log_record["request_id"] = record.request_id

        # Add extra context
        if hasattr(record, "user_id"):
            log_record["user_id"] = record.user_id
        if hasattr(record, "city_id"):
            log_record["city_id"] = record.city_id
        if hasattr(record, "duration_ms"):
            log_record["duration_ms"] = record.duration_ms
        if hasattr(record, "error_type"):
            log_record["error_type"] = record.error_type
        if hasattr(record, "stack_trace"):
            log_record["stack_trace"] = record.stack_trace


class PerformanceLogger:
    """
    Context manager for logging performance metrics
    """

    def __init__(self, operation_name: str, logger: logging.Logger, threshold_ms: float = 1000):
        self.operation_name = operation_name
        self.logger = logger
        self.threshold_ms = threshold_ms
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000

        # Log if operation is slow
        if duration_ms > self.threshold_ms:
            self.logger.warning(
                f"Slow operation: {self.operation_name}",
                extra={"duration_ms": duration_ms, "operation": self.operation_name}
            )
        else:
            self.logger.debug(
                f"Operation completed: {self.operation_name}",
                extra={"duration_ms": duration_ms, "operation": self.operation_name}
            )


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
        formatter = CustomJsonFormatter(
            "%(timestamp)s %(name)s %(levelname)s %(message)s %(request_id)s"
        )
    else:
        # Enhanced development formatter with request ID
        formatter = logging.Formatter(
            "%(asctime)s - [%(request_id)s] - %(name)s - %(levelname)s - %(message)s"
        )

    handler.setFormatter(formatter)

    # Add request ID filter to all handlers
    request_id_filter = RequestIdFilter()
    handler.addFilter(request_id_filter)

    logger.addHandler(handler)

    # Configure log levels for different modules
    if settings.ENVIRONMENT == "production":
        # In production, be more selective about what we log
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.error").setLevel(logging.INFO)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("celery").setLevel(logging.INFO)
    else:
        # In development, show more details
        logging.getLogger("uvicorn.access").setLevel(logging.INFO)
        logging.getLogger("uvicorn.error").setLevel(logging.DEBUG)
        if settings.DATABASE_ECHO:
            logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
        else:
            logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    # Configure third-party library logging
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("s3transfer").setLevel(logging.WARNING)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
