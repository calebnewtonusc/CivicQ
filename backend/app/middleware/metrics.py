"""
Metrics Middleware for Automatic Request Tracking

This middleware automatically tracks all HTTP requests with Prometheus metrics
and provides detailed performance monitoring.
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.core.metrics import (
    http_requests_total,
    http_request_duration_seconds,
)
from app.core.sentry import add_breadcrumb, set_context

logger = logging.getLogger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically track HTTP request metrics
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip metrics collection for metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)

        # Start timing
        start_time = time.time()

        # Extract request info
        method = request.method
        path = request.url.path

        # Clean up path for metrics (remove IDs and UUIDs)
        endpoint = self._normalize_path(path)

        # Add Sentry breadcrumb
        add_breadcrumb(
            message=f"{method} {endpoint}",
            category="http.request",
            level="info",
            data={
                "method": method,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else None,
            },
        )

        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code

            # Track metrics
            http_requests_total.labels(
                method=method, endpoint=endpoint, status=str(status_code)
            ).inc()

            # Track duration
            duration = time.time() - start_time
            http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(
                duration
            )

            # Add performance headers
            response.headers["X-Response-Time"] = f"{duration:.4f}"

            # Log slow requests
            if duration > 1.0:
                logger.warning(
                    f"Slow request: {method} {endpoint} took {duration:.2f}s",
                    extra={
                        "method": method,
                        "endpoint": endpoint,
                        "duration_seconds": duration,
                        "status_code": status_code,
                    },
                )

            # Add context to Sentry
            set_context(
                "http.response",
                {
                    "status_code": status_code,
                    "duration_seconds": duration,
                    "endpoint": endpoint,
                },
            )

            return response

        except Exception as e:
            # Track error
            duration = time.time() - start_time
            http_requests_total.labels(method=method, endpoint=endpoint, status="500").inc()

            http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(
                duration
            )

            logger.error(
                f"Request failed: {method} {endpoint}",
                exc_info=True,
                extra={
                    "method": method,
                    "endpoint": endpoint,
                    "duration_seconds": duration,
                    "error": str(e),
                },
            )

            # Re-raise the exception to be handled by global exception handler
            raise

    def _normalize_path(self, path: str) -> str:
        """
        Normalize path by replacing IDs and UUIDs with placeholders
        to avoid creating too many unique metric labels

        Examples:
            /api/users/123 -> /api/users/{id}
            /api/ballots/abc-123-def -> /api/ballots/{id}
            /api/cities/los-angeles/contests -> /api/cities/{slug}/contests
        """
        import re

        # Replace UUIDs
        path = re.sub(
            r"/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            "/{id}",
            path,
            flags=re.IGNORECASE,
        )

        # Replace numeric IDs
        path = re.sub(r"/\d+", "/{id}", path)

        # Replace common slug patterns (alphanumeric with hyphens)
        # But preserve API version numbers and known static paths
        parts = path.split("/")
        normalized_parts = []

        for i, part in enumerate(parts):
            # Skip empty parts
            if not part:
                normalized_parts.append(part)
                continue

            # Preserve known static parts
            static_parts = {
                "api",
                "v1",
                "v2",
                "auth",
                "login",
                "logout",
                "register",
                "health",
                "metrics",
                "docs",
                "redoc",
                "ballots",
                "contests",
                "questions",
                "candidates",
                "cities",
                "videos",
                "admin",
                "moderation",
                "users",
                "votes",
                "answers",
                "upload",
                "download",
                "status",
            }

            if part.lower() in static_parts:
                normalized_parts.append(part)
            # Check if it looks like a slug (contains hyphens or is alphanumeric)
            elif "-" in part or (part.isalnum() and not part.isdigit()):
                # If previous part suggests this is a dynamic segment
                if i > 0 and normalized_parts[-1] in [
                    "cities",
                    "ballots",
                    "contests",
                    "questions",
                    "candidates",
                    "users",
                    "videos",
                ]:
                    normalized_parts.append("{slug}")
                else:
                    normalized_parts.append(part)
            else:
                normalized_parts.append(part)

        return "/".join(normalized_parts)


def metrics_endpoint(request: Request) -> Response:
    """
    Endpoint to expose Prometheus metrics

    This should be mounted at /metrics
    """
    from starlette.responses import Response

    # Generate latest metrics
    metrics_output = generate_latest()

    return Response(content=metrics_output, media_type=CONTENT_TYPE_LATEST)
