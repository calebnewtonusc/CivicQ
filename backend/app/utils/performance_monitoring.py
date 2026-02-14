"""
Performance Monitoring Utilities

Tracks and reports performance metrics including response times,
cache hit rates, database query performance, and frontend metrics.
"""

import time
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from functools import wraps
from contextlib import contextmanager

from app.services.cache_service import cache_service
from app.core.cache_keys import CacheKeys

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """Track and store performance metrics"""

    @staticmethod
    def record_api_response_time(endpoint: str, method: str, duration_ms: float, status_code: int):
        """
        Record API response time

        Args:
            endpoint: API endpoint
            method: HTTP method
            duration_ms: Duration in milliseconds
            status_code: HTTP status code
        """
        key = f"metrics:api:{method}:{endpoint}"

        # Store in sorted set with timestamp
        timestamp = time.time()
        cache_service.redis_client.zadd(
            f"{key}:times",
            {str(timestamp): duration_ms}
        )

        # Keep only last 1000 entries
        cache_service.redis_client.zremrangebyrank(f"{key}:times", 0, -1001)

        # Increment counter
        cache_service.increment(f"{key}:count")

        # Track by status code
        cache_service.increment(f"{key}:status:{status_code}")

        # Log slow requests
        if duration_ms > 1000:
            logger.warning(
                f"Slow API request: {method} {endpoint} took {duration_ms:.2f}ms "
                f"(status: {status_code})"
            )

    @staticmethod
    def get_api_metrics(endpoint: str, method: str) -> Dict[str, Any]:
        """
        Get API metrics for endpoint

        Args:
            endpoint: API endpoint
            method: HTTP method

        Returns:
            Dictionary of metrics
        """
        key = f"metrics:api:{method}:{endpoint}"

        # Get response times
        times = cache_service.redis_client.zrange(f"{key}:times", 0, -1, withscores=True)
        if times:
            durations = [float(score) for _, score in times]
            sorted_durations = sorted(durations)

            metrics = {
                "endpoint": f"{method} {endpoint}",
                "total_requests": cache_service.get(f"{key}:count") or 0,
                "avg_response_time": sum(durations) / len(durations),
                "min_response_time": min(durations),
                "max_response_time": max(durations),
                "median_response_time": sorted_durations[len(sorted_durations) // 2],
                "p95_response_time": sorted_durations[int(len(sorted_durations) * 0.95)],
                "p99_response_time": sorted_durations[int(len(sorted_durations) * 0.99)],
            }

            return metrics

        return {"endpoint": f"{method} {endpoint}", "total_requests": 0}

    @staticmethod
    def record_cache_hit(key: str):
        """Record cache hit"""
        cache_service.increment("metrics:cache:hits")
        cache_service.increment(f"metrics:cache:key:{key}:hits")

    @staticmethod
    def record_cache_miss(key: str):
        """Record cache miss"""
        cache_service.increment("metrics:cache:misses")
        cache_service.increment(f"metrics:cache:key:{key}:misses")

    @staticmethod
    def get_cache_metrics() -> Dict[str, Any]:
        """
        Get cache performance metrics

        Returns:
            Dictionary of cache metrics
        """
        hits = cache_service.get("metrics:cache:hits") or 0
        misses = cache_service.get("metrics:cache:misses") or 0
        total = hits + misses

        hit_rate = (hits / total * 100) if total > 0 else 0

        # Get Redis stats
        redis_stats = cache_service.get_stats()

        return {
            "application_hits": hits,
            "application_misses": misses,
            "application_total": total,
            "application_hit_rate": round(hit_rate, 2),
            "redis_stats": redis_stats,
        }

    @staticmethod
    def record_db_query_time(query_type: str, duration_ms: float):
        """
        Record database query time

        Args:
            query_type: Type of query (select, insert, update, delete)
            duration_ms: Duration in milliseconds
        """
        key = f"metrics:db:{query_type}"

        # Store in sorted set
        timestamp = time.time()
        cache_service.redis_client.zadd(
            f"{key}:times",
            {str(timestamp): duration_ms}
        )

        # Keep only last 1000 entries
        cache_service.redis_client.zremrangebyrank(f"{key}:times", 0, -1001)

        # Increment counter
        cache_service.increment(f"{key}:count")

        # Log slow queries
        if duration_ms > 100:
            logger.warning(f"Slow database query: {query_type} took {duration_ms:.2f}ms")

    @staticmethod
    def get_db_metrics(query_type: str) -> Dict[str, Any]:
        """
        Get database metrics

        Args:
            query_type: Type of query

        Returns:
            Dictionary of metrics
        """
        key = f"metrics:db:{query_type}"

        times = cache_service.redis_client.zrange(f"{key}:times", 0, -1, withscores=True)
        if times:
            durations = [float(score) for _, score in times]
            sorted_durations = sorted(durations)

            return {
                "query_type": query_type,
                "total_queries": cache_service.get(f"{key}:count") or 0,
                "avg_time": sum(durations) / len(durations),
                "min_time": min(durations),
                "max_time": max(durations),
                "p95_time": sorted_durations[int(len(sorted_durations) * 0.95)],
            }

        return {"query_type": query_type, "total_queries": 0}

    @staticmethod
    def record_frontend_metric(metric_name: str, value: float, user_agent: str = ""):
        """
        Record frontend performance metric

        Args:
            metric_name: Metric name (fcp, lcp, tti, cls, etc.)
            value: Metric value in milliseconds
            user_agent: User agent string
        """
        key = f"metrics:frontend:{metric_name}"

        # Store in sorted set
        timestamp = time.time()
        cache_service.redis_client.zadd(
            f"{key}:values",
            {str(timestamp): value}
        )

        # Keep only last 1000 entries
        cache_service.redis_client.zremrangebyrank(f"{key}:values", 0, -1001)

        # Increment counter
        cache_service.increment(f"{key}:count")

    @staticmethod
    def get_frontend_metrics(metric_name: str) -> Dict[str, Any]:
        """
        Get frontend performance metrics

        Args:
            metric_name: Metric name

        Returns:
            Dictionary of metrics
        """
        key = f"metrics:frontend:{metric_name}"

        values = cache_service.redis_client.zrange(f"{key}:values", 0, -1, withscores=True)
        if values:
            vals = [float(score) for _, score in values]
            sorted_vals = sorted(vals)

            return {
                "metric": metric_name,
                "samples": len(vals),
                "avg": sum(vals) / len(vals),
                "min": min(vals),
                "max": max(vals),
                "median": sorted_vals[len(sorted_vals) // 2],
                "p75": sorted_vals[int(len(sorted_vals) * 0.75)],
                "p95": sorted_vals[int(len(sorted_vals) * 0.95)],
            }

        return {"metric": metric_name, "samples": 0}

    @staticmethod
    def get_all_metrics() -> Dict[str, Any]:
        """
        Get all performance metrics

        Returns:
            Comprehensive metrics dictionary
        """
        return {
            "cache": PerformanceMetrics.get_cache_metrics(),
            "database": {
                "select": PerformanceMetrics.get_db_metrics("select"),
                "insert": PerformanceMetrics.get_db_metrics("insert"),
                "update": PerformanceMetrics.get_db_metrics("update"),
                "delete": PerformanceMetrics.get_db_metrics("delete"),
            },
            "frontend": {
                "fcp": PerformanceMetrics.get_frontend_metrics("fcp"),
                "lcp": PerformanceMetrics.get_frontend_metrics("lcp"),
                "tti": PerformanceMetrics.get_frontend_metrics("tti"),
                "cls": PerformanceMetrics.get_frontend_metrics("cls"),
            },
            "timestamp": datetime.now().isoformat(),
        }


# Decorators and Context Managers

def measure_time(metric_name: str):
    """
    Decorator to measure function execution time

    Args:
        metric_name: Name for the metric

    Usage:
        @measure_time("process_video")
        def process_video(video_id):
            # ... processing logic
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.time() - start_time) * 1000
                logger.info(f"{metric_name} took {duration_ms:.2f}ms")
                # Store metric
                key = f"metrics:function:{metric_name}"
                cache_service.redis_client.zadd(
                    f"{key}:times",
                    {str(time.time()): duration_ms}
                )

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.time() - start_time) * 1000
                logger.info(f"{metric_name} took {duration_ms:.2f}ms")
                key = f"metrics:function:{metric_name}"
                cache_service.redis_client.zadd(
                    f"{key}:times",
                    {str(time.time()): duration_ms}
                )

        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


@contextmanager
def measure_db_query(query_type: str):
    """
    Context manager to measure database query time

    Args:
        query_type: Type of query

    Usage:
        with measure_db_query("select"):
            results = db.query(Question).all()
    """
    start_time = time.time()
    try:
        yield
    finally:
        duration_ms = (time.time() - start_time) * 1000
        PerformanceMetrics.record_db_query_time(query_type, duration_ms)


class PerformanceMonitor:
    """Real-time performance monitoring"""

    def __init__(self):
        self.start_time = time.time()

    def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall system health status

        Returns:
            System health metrics
        """
        cache_metrics = PerformanceMetrics.get_cache_metrics()

        # Determine health status
        cache_healthy = cache_metrics.get("redis_stats", {}).get("available", False)

        # Get recent API performance
        recent_errors = 0  # Would track from error logs in production

        health_status = "healthy"
        if not cache_healthy:
            health_status = "degraded"
        if recent_errors > 10:
            health_status = "unhealthy"

        return {
            "status": health_status,
            "uptime_seconds": time.time() - self.start_time,
            "cache_available": cache_healthy,
            "cache_hit_rate": cache_metrics.get("application_hit_rate", 0),
            "timestamp": datetime.now().isoformat(),
        }

    def get_performance_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive performance report

        Returns:
            Performance report
        """
        return {
            "system_health": self.get_system_health(),
            "metrics": PerformanceMetrics.get_all_metrics(),
        }


# Global performance monitor instance
performance_monitor = PerformanceMonitor()
