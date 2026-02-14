"""
Request ID Middleware and Context Management

Tracks request IDs across the entire request lifecycle for distributed tracing.
"""

import uuid
import logging
from contextvars import ContextVar
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Context variable to store request ID across async calls
request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="")


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID to all requests"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get or generate request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Store in context var for access in other parts of the app
        request_id_ctx_var.set(request_id)

        # Add to request state
        request.state.request_id = request_id

        # Process request
        response = await call_next(request)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response


class RequestIdFilter(logging.Filter):
    """Logging filter to add request ID to all log records"""

    def filter(self, record):
        record.request_id = request_id_ctx_var.get("")
        return True


def get_request_id() -> str:
    """Get the current request ID from context"""
    return request_id_ctx_var.get("")
