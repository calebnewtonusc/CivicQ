"""
Sentry Integration for Error Tracking and Performance Monitoring

Configures Sentry for comprehensive error tracking, performance monitoring,
release tracking, and user feedback collection.
"""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import logging

from app.core.config import settings


def init_sentry():
    """
    Initialize Sentry SDK with comprehensive integrations
    """
    if not settings.SENTRY_DSN:
        logging.info("Sentry DSN not configured, skipping Sentry initialization")
        return

    # Determine sample rates based on environment
    traces_sample_rate = 0.1 if settings.ENVIRONMENT == "production" else 1.0
    profiles_sample_rate = 0.1 if settings.ENVIRONMENT == "production" else 1.0

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,

        # Release tracking
        release=settings.SENTRY_RELEASE,

        # Integrations
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
            RedisIntegration(),
            CeleryIntegration(),
            LoggingIntegration(
                level=logging.INFO,  # Capture info and above
                event_level=logging.ERROR  # Send errors as events
            ),
        ],

        # Performance monitoring
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate,

        # Error sampling
        sample_rate=1.0,  # Capture all errors

        # Max breadcrumbs
        max_breadcrumbs=50,

        # Attach stacktraces to messages
        attach_stacktrace=True,

        # Send default PII (Personally Identifiable Information)
        send_default_pii=False,  # Don't send PII by default

        # Before send hook for error filtering and enrichment
        before_send=before_send_hook,

        # Before breadcrumb hook for breadcrumb filtering
        before_breadcrumb=before_breadcrumb_hook,

        # Transaction ignore patterns
        ignore_errors=[
            "fastapi.exceptions.HTTPException",  # Don't track expected HTTP errors
            KeyboardInterrupt,
        ],
    )

    logging.info(f"Sentry initialized for environment: {settings.ENVIRONMENT}")


def before_send_hook(event, hint):
    """
    Hook called before sending events to Sentry
    Used for error filtering, enrichment, and fingerprinting
    """
    # Don't send client errors (4xx) to Sentry
    if "exc_info" in hint:
        exc_type, exc_value, tb = hint["exc_info"]
        if hasattr(exc_value, "status_code") and 400 <= exc_value.status_code < 500:
            return None

    # Add custom fingerprinting for better error grouping
    if "exception" in event:
        exceptions = event["exception"].get("values", [])
        if exceptions:
            exc = exceptions[0]
            exc_type = exc.get("type", "")
            exc_value = exc.get("value", "")

            # Custom fingerprints for database errors
            if "DatabaseError" in exc_type or "OperationalError" in exc_type:
                event["fingerprint"] = ["database-error", exc_type]

            # Custom fingerprints for external API errors
            elif "httpx" in exc_type.lower() or "ClientError" in exc_type:
                event["fingerprint"] = ["external-api-error", exc_type]

            # Custom fingerprints for validation errors
            elif "ValidationError" in exc_type:
                event["fingerprint"] = ["validation-error", exc_type]

    # Add environment tags
    event.setdefault("tags", {})
    event["tags"]["environment"] = settings.ENVIRONMENT

    return event


def before_breadcrumb_hook(crumb, hint):
    """
    Hook called before recording breadcrumbs
    Used to filter out noisy breadcrumbs
    """
    # Filter out health check requests
    if crumb.get("category") == "httplib" and "/health" in str(crumb.get("data", {}).get("url", "")):
        return None

    # Filter out static file requests
    if crumb.get("category") == "httplib" and any(
        ext in str(crumb.get("data", {}).get("url", ""))
        for ext in [".css", ".js", ".png", ".jpg", ".ico"]
    ):
        return None

    return crumb


def set_user_context(user_id: str = None, email: str = None, city_id: str = None, role: str = None):
    """
    Set user context for Sentry error tracking

    Args:
        user_id: User ID
        email: User email (will be scrubbed if PII protection is on)
        city_id: City ID for multi-tenant context
        role: User role (voter, candidate, admin, etc.)
    """
    sentry_sdk.set_user({
        "id": user_id,
        "email": email,
        "city_id": city_id,
        "role": role,
    })


def set_context(context_name: str, context_data: dict):
    """
    Add custom context to Sentry events

    Args:
        context_name: Name of the context (e.g., "ballot", "video_processing")
        context_data: Dictionary of context data
    """
    sentry_sdk.set_context(context_name, context_data)


def capture_message(message: str, level: str = "info", **kwargs):
    """
    Capture a message in Sentry

    Args:
        message: Message to capture
        level: Log level (debug, info, warning, error, fatal)
        **kwargs: Additional context
    """
    sentry_sdk.capture_message(message, level=level, **kwargs)


def capture_exception(error: Exception, **kwargs):
    """
    Capture an exception in Sentry

    Args:
        error: Exception to capture
        **kwargs: Additional context
    """
    sentry_sdk.capture_exception(error, **kwargs)


def add_breadcrumb(message: str, category: str = "default", level: str = "info", data: dict = None):
    """
    Add a breadcrumb for debugging context

    Args:
        message: Breadcrumb message
        category: Breadcrumb category
        level: Log level
        data: Additional data
    """
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {}
    )
