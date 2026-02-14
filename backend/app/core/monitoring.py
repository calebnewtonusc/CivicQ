"""
Complete Monitoring and Observability Infrastructure for CivicQ

This module provides comprehensive monitoring capabilities including:
- Error tracking and reporting
- Performance monitoring
- Health checks
- Custom metrics
- Database query monitoring
- External API monitoring
- Background job monitoring
"""

import logging
import time
import traceback
from typing import Optional, Dict, Any, Callable
from functools import wraps
from contextlib import contextmanager
import psutil
import redis
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.sentry import capture_exception, capture_message, add_breadcrumb, set_context
from app.core.metrics import (
    database_query_duration_seconds,
    database_query_errors_total,
    external_api_duration_seconds,
    external_api_requests_total,
    s3_operation_duration_seconds,
    s3_operations_total,
    redis_operation_duration_seconds,
    redis_operations_total,
)

logger = logging.getLogger(__name__)


class MonitoringContext:
    """
    Context manager for monitoring operations with automatic timing,
    error tracking, and metric collection.
    """

    def __init__(
        self,
        operation_name: str,
        operation_type: str,
        labels: Optional[Dict[str, str]] = None,
        track_in_sentry: bool = True,
    ):
        self.operation_name = operation_name
        self.operation_type = operation_type
        self.labels = labels or {}
        self.track_in_sentry = track_in_sentry
        self.start_time = None
        self.success = False

    def __enter__(self):
        self.start_time = time.time()
        if self.track_in_sentry:
            add_breadcrumb(
                message=f"Starting {self.operation_type}: {self.operation_name}",
                category=self.operation_type,
                level="info",
                data=self.labels,
            )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time

        # Track success/failure
        self.success = exc_type is None
        status = "success" if self.success else "error"

        # Log performance
        if duration > 1.0:  # Log slow operations
            logger.warning(
                f"Slow {self.operation_type}: {self.operation_name}",
                extra={
                    "duration_seconds": duration,
                    "operation": self.operation_name,
                    "operation_type": self.operation_type,
                    **self.labels,
                },
            )

        # Track metrics based on operation type
        if self.operation_type == "database_query":
            database_query_duration_seconds.labels(
                query_type=self.labels.get("query_type", "unknown")
            ).observe(duration)
            if not self.success:
                database_query_errors_total.labels(
                    error_type=exc_type.__name__ if exc_type else "unknown"
                ).inc()

        elif self.operation_type == "external_api":
            api_name = self.labels.get("api_name", "unknown")
            external_api_duration_seconds.labels(api_name=api_name).observe(duration)
            external_api_requests_total.labels(api_name=api_name, status=status).inc()

        elif self.operation_type == "s3_operation":
            operation = self.labels.get("operation", "unknown")
            s3_operation_duration_seconds.labels(operation=operation).observe(duration)
            s3_operations_total.labels(operation=operation, status=status).inc()

        elif self.operation_type == "redis_operation":
            operation = self.labels.get("operation", "unknown")
            redis_operation_duration_seconds.labels(operation=operation).observe(duration)
            redis_operations_total.labels(operation=operation, status=status).inc()

        # Capture errors in Sentry
        if not self.success and self.track_in_sentry:
            set_context(
                self.operation_type,
                {
                    "operation_name": self.operation_name,
                    "duration_seconds": duration,
                    **self.labels,
                },
            )
            capture_exception(exc_val)

        return False  # Don't suppress exceptions


@contextmanager
def monitor_database_query(query_type: str, query: Optional[str] = None):
    """
    Context manager for monitoring database queries

    Args:
        query_type: Type of query (select, insert, update, delete, etc.)
        query: Optional SQL query string for debugging

    Example:
        with monitor_database_query("select", "SELECT * FROM users"):
            result = db.execute(...)
    """
    with MonitoringContext(
        operation_name=query or query_type,
        operation_type="database_query",
        labels={"query_type": query_type},
    ):
        yield


@contextmanager
def monitor_external_api(api_name: str, endpoint: Optional[str] = None):
    """
    Context manager for monitoring external API calls

    Args:
        api_name: Name of the external API (e.g., "google_civic", "deepgram")
        endpoint: Optional endpoint being called

    Example:
        with monitor_external_api("google_civic", "/elections"):
            response = httpx.get(...)
    """
    with MonitoringContext(
        operation_name=endpoint or api_name,
        operation_type="external_api",
        labels={"api_name": api_name, "endpoint": endpoint or ""},
    ):
        yield


@contextmanager
def monitor_s3_operation(operation: str, key: Optional[str] = None):
    """
    Context manager for monitoring S3/R2 operations

    Args:
        operation: Type of operation (upload, download, delete, etc.)
        key: Optional S3 key being accessed

    Example:
        with monitor_s3_operation("upload", "videos/abc123.mp4"):
            s3_client.upload_file(...)
    """
    with MonitoringContext(
        operation_name=key or operation,
        operation_type="s3_operation",
        labels={"operation": operation, "key": key or ""},
    ):
        yield


@contextmanager
def monitor_redis_operation(operation: str, key: Optional[str] = None):
    """
    Context manager for monitoring Redis operations

    Args:
        operation: Type of operation (get, set, delete, etc.)
        key: Optional Redis key being accessed

    Example:
        with monitor_redis_operation("set", "user:123"):
            redis_client.set(...)
    """
    with MonitoringContext(
        operation_name=key or operation,
        operation_type="redis_operation",
        labels={"operation": operation, "key": key or ""},
    ):
        yield


def track_database_query(query_type: str):
    """
    Decorator for tracking database queries

    Args:
        query_type: Type of query (select, insert, update, delete, etc.)

    Example:
        @track_database_query("select")
        async def get_user(user_id: int):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with monitor_database_query(query_type, func.__name__):
                return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with monitor_database_query(query_type, func.__name__):
                return func(*args, **kwargs)

        import inspect

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def track_external_api(api_name: str):
    """
    Decorator for tracking external API calls

    Args:
        api_name: Name of the external API

    Example:
        @track_external_api("google_civic")
        async def fetch_ballot_data():
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with monitor_external_api(api_name, func.__name__):
                return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with monitor_external_api(api_name, func.__name__):
                return func(*args, **kwargs)

        import inspect

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class HealthChecker:
    """
    Comprehensive health check utilities for monitoring system components
    """

    @staticmethod
    def check_database(db: Session) -> Dict[str, Any]:
        """
        Check database connectivity and performance

        Returns:
            Dict with status and details
        """
        try:
            start_time = time.time()
            db.execute(text("SELECT 1"))
            duration = time.time() - start_time

            # Check connection pool status
            pool = db.get_bind().pool
            pool_status = {
                "size": pool.size(),
                "checked_in": pool.checkedin(),
                "overflow": pool.overflow(),
                "max_overflow": pool._max_overflow,
            }

            return {
                "status": "healthy",
                "response_time_ms": round(duration * 1000, 2),
                "pool": pool_status,
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            capture_exception(e)
            return {
                "status": "unhealthy",
                "error": str(e),
                "error_type": type(e).__name__,
            }

    @staticmethod
    def check_redis(redis_url: str) -> Dict[str, Any]:
        """
        Check Redis connectivity and performance

        Returns:
            Dict with status and details
        """
        try:
            redis_client = redis.from_url(redis_url)
            start_time = time.time()
            redis_client.ping()
            duration = time.time() - start_time

            # Get Redis info
            info = redis_client.info()
            memory_used_mb = info.get("used_memory", 0) / (1024 * 1024)

            return {
                "status": "healthy",
                "response_time_ms": round(duration * 1000, 2),
                "memory_used_mb": round(memory_used_mb, 2),
                "connected_clients": info.get("connected_clients", 0),
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            capture_exception(e)
            return {
                "status": "unhealthy",
                "error": str(e),
                "error_type": type(e).__name__,
            }

    @staticmethod
    def check_celery() -> Dict[str, Any]:
        """
        Check Celery worker status

        Returns:
            Dict with status and details
        """
        try:
            from app.tasks import celery_app

            # Check active workers
            inspector = celery_app.control.inspect()
            active = inspector.active()
            stats = inspector.stats()

            if not active:
                return {
                    "status": "unhealthy",
                    "error": "No active Celery workers found",
                }

            worker_count = len(active.keys())
            return {
                "status": "healthy",
                "active_workers": worker_count,
                "workers": list(active.keys()),
                "stats": stats,
            }
        except Exception as e:
            logger.error(f"Celery health check failed: {e}")
            capture_exception(e)
            return {
                "status": "unhealthy",
                "error": str(e),
                "error_type": type(e).__name__,
            }

    @staticmethod
    def check_storage() -> Dict[str, Any]:
        """
        Check S3/R2 storage connectivity

        Returns:
            Dict with status and details
        """
        try:
            import boto3
            from botocore.exceptions import ClientError

            if not settings.S3_BUCKET:
                return {
                    "status": "not_configured",
                    "message": "S3 storage not configured",
                }

            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                endpoint_url=settings.S3_ENDPOINT,
                region_name=settings.S3_REGION,
            )

            start_time = time.time()
            s3_client.head_bucket(Bucket=settings.S3_BUCKET)
            duration = time.time() - start_time

            return {
                "status": "healthy",
                "response_time_ms": round(duration * 1000, 2),
                "bucket": settings.S3_BUCKET,
            }
        except Exception as e:
            logger.error(f"S3 health check failed: {e}")
            capture_exception(e)
            return {
                "status": "unhealthy",
                "error": str(e),
                "error_type": type(e).__name__,
            }

    @staticmethod
    def check_system_resources() -> Dict[str, Any]:
        """
        Check system resource usage (CPU, memory, disk)

        Returns:
            Dict with system resource information
        """
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent
            disk_free_gb = disk.free / (1024**3)

            # Determine overall status
            status = "healthy"
            warnings = []

            if cpu_percent > 80:
                warnings.append(f"High CPU usage: {cpu_percent}%")
            if memory_percent > 85:
                warnings.append(f"High memory usage: {memory_percent}%")
            if disk_percent > 90:
                warnings.append(f"High disk usage: {disk_percent}%")

            if warnings:
                status = "warning"

            return {
                "status": status,
                "warnings": warnings if warnings else None,
                "cpu_percent": round(cpu_percent, 2),
                "memory_percent": round(memory_percent, 2),
                "memory_available_gb": round(memory_available_gb, 2),
                "disk_percent": round(disk_percent, 2),
                "disk_free_gb": round(disk_free_gb, 2),
            }
        except Exception as e:
            logger.error(f"System resource check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
            }


def detect_slow_queries(db: Session, threshold_ms: float = 1000):
    """
    Detect and log slow database queries

    Args:
        db: Database session
        threshold_ms: Threshold in milliseconds for slow queries

    Note: This requires query logging to be enabled in PostgreSQL
    """
    try:
        # Query PostgreSQL's pg_stat_statements for slow queries
        query = text(
            """
            SELECT query, mean_exec_time, calls, total_exec_time
            FROM pg_stat_statements
            WHERE mean_exec_time > :threshold
            ORDER BY mean_exec_time DESC
            LIMIT 10
        """
        )

        result = db.execute(query, {"threshold": threshold_ms})
        slow_queries = result.fetchall()

        if slow_queries:
            logger.warning(
                f"Detected {len(slow_queries)} slow queries (threshold: {threshold_ms}ms)"
            )
            for query in slow_queries:
                capture_message(
                    f"Slow query detected: {query.mean_exec_time:.2f}ms",
                    level="warning",
                    tags={
                        "query": query.query[:200],  # First 200 chars
                        "mean_exec_time_ms": query.mean_exec_time,
                        "calls": query.calls,
                    },
                )

        return slow_queries
    except Exception as e:
        # pg_stat_statements extension might not be enabled
        logger.debug(f"Could not check for slow queries: {e}")
        return []


def detect_n_plus_one_queries():
    """
    Detect N+1 query patterns using SQLAlchemy event listeners

    This should be enabled in development/staging environments
    """
    from sqlalchemy import event
    from sqlalchemy.engine import Engine

    query_counts = {}

    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        # Track query patterns
        query_pattern = statement.split()[0:3]  # First few words
        query_key = " ".join(query_pattern)

        if query_key not in query_counts:
            query_counts[query_key] = 0
        query_counts[query_key] += 1

        # Warn if same query type is repeated many times
        if query_counts[query_key] > 10:
            logger.warning(
                f"Potential N+1 query detected: {query_key} executed {query_counts[query_key]} times"
            )
            capture_message(
                f"Potential N+1 query: {query_key}",
                level="warning",
                tags={"query_pattern": query_key, "execution_count": query_counts[query_key]},
            )
