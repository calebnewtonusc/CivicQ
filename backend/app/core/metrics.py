"""
Prometheus Metrics for CivicQ

Custom business and infrastructure metrics for monitoring and alerting.
"""

from prometheus_client import Counter, Histogram, Gauge, Info
from functools import wraps
import time
from typing import Callable

# ============================================================================
# HTTP Metrics
# ============================================================================

http_requests_total = Counter(
    "civicq_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

http_request_duration_seconds = Histogram(
    "civicq_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

# ============================================================================
# Business Metrics - Questions
# ============================================================================

questions_submitted_total = Counter(
    "civicq_questions_submitted_total",
    "Total questions submitted",
    ["city_id", "contest_type"]
)

questions_approved_total = Counter(
    "civicq_questions_approved_total",
    "Total questions approved",
    ["city_id", "contest_type"]
)

questions_rejected_total = Counter(
    "civicq_questions_rejected_total",
    "Total questions rejected",
    ["city_id", "contest_type", "reason"]
)

questions_pending = Gauge(
    "civicq_questions_pending",
    "Number of questions pending moderation",
    ["city_id"]
)

questions_per_hour = Gauge(
    "civicq_questions_per_hour",
    "Questions submitted per hour",
    ["city_id"]
)

# ============================================================================
# Business Metrics - Votes
# ============================================================================

votes_cast_total = Counter(
    "civicq_votes_cast_total",
    "Total votes cast on questions",
    ["city_id", "vote_type"]
)

# ============================================================================
# Business Metrics - Video Processing
# ============================================================================

video_uploads_total = Counter(
    "civicq_video_uploads_total",
    "Total video uploads",
    ["city_id", "status"]
)

video_processing_duration_seconds = Histogram(
    "civicq_video_processing_duration_seconds",
    "Video processing duration in seconds",
    ["processing_step"],
    buckets=(1, 5, 10, 30, 60, 120, 300, 600, 1800)
)

video_processing_errors_total = Counter(
    "civicq_video_processing_errors_total",
    "Total video processing errors",
    ["error_type"]
)

video_transcription_duration_seconds = Histogram(
    "civicq_video_transcription_duration_seconds",
    "Video transcription duration in seconds",
    buckets=(1, 5, 10, 30, 60, 120, 300)
)

# ============================================================================
# Business Metrics - User Activity
# ============================================================================

user_registrations_total = Counter(
    "civicq_user_registrations_total",
    "Total user registrations",
    ["city_id", "role"]
)

user_logins_total = Counter(
    "civicq_user_logins_total",
    "Total user logins",
    ["city_id", "method"]
)

active_users = Gauge(
    "civicq_active_users",
    "Number of active users in the last 24 hours",
    ["city_id"]
)

# ============================================================================
# Database Metrics
# ============================================================================

database_connections = Gauge(
    "civicq_database_connections",
    "Number of database connections",
    ["state"]
)

database_query_duration_seconds = Histogram(
    "civicq_database_query_duration_seconds",
    "Database query duration in seconds",
    ["query_type"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5)
)

database_query_errors_total = Counter(
    "civicq_database_query_errors_total",
    "Total database query errors",
    ["error_type"]
)

# ============================================================================
# Celery/Queue Metrics
# ============================================================================

celery_tasks_total = Counter(
    "civicq_celery_tasks_total",
    "Total Celery tasks",
    ["task_name", "status"]
)

celery_task_duration_seconds = Histogram(
    "civicq_celery_task_duration_seconds",
    "Celery task duration in seconds",
    ["task_name"],
    buckets=(0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0)
)

celery_queue_length = Gauge(
    "civicq_celery_queue_length",
    "Number of tasks in Celery queue",
    ["queue_name"]
)

# ============================================================================
# Redis Metrics
# ============================================================================

redis_operations_total = Counter(
    "civicq_redis_operations_total",
    "Total Redis operations",
    ["operation", "status"]
)

redis_operation_duration_seconds = Histogram(
    "civicq_redis_operation_duration_seconds",
    "Redis operation duration in seconds",
    ["operation"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)

# ============================================================================
# External API Metrics
# ============================================================================

external_api_requests_total = Counter(
    "civicq_external_api_requests_total",
    "Total external API requests",
    ["api_name", "status"]
)

external_api_duration_seconds = Histogram(
    "civicq_external_api_duration_seconds",
    "External API request duration in seconds",
    ["api_name"],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0)
)

# ============================================================================
# S3/Storage Metrics
# ============================================================================

s3_operations_total = Counter(
    "civicq_s3_operations_total",
    "Total S3 operations",
    ["operation", "status"]
)

s3_operation_duration_seconds = Histogram(
    "civicq_s3_operation_duration_seconds",
    "S3 operation duration in seconds",
    ["operation"],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0)
)

# ============================================================================
# Application Info
# ============================================================================

app_info = Info("civicq_app", "CivicQ application information")

# ============================================================================
# Decorators for Automatic Metric Collection
# ============================================================================


def track_time(metric: Histogram, labels: dict = None):
    """
    Decorator to track execution time of a function

    Usage:
        @track_time(video_processing_duration_seconds, {"processing_step": "transcription"})
        def transcribe_video(video_id):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                if labels:
                    metric.labels(**labels).observe(duration)
                else:
                    metric.observe(duration)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                if labels:
                    metric.labels(**labels).observe(duration)
                else:
                    metric.observe(duration)

        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def track_counter(counter: Counter, labels: dict = None):
    """
    Decorator to increment a counter when a function is called

    Usage:
        @track_counter(questions_submitted_total, {"city_id": "1", "contest_type": "mayor"})
        def submit_question(question):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if labels:
                counter.labels(**labels).inc()
            else:
                counter.inc()
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if labels:
                counter.labels(**labels).inc()
            else:
                counter.inc()
            return func(*args, **kwargs)

        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
