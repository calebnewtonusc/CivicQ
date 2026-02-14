"""
Rate Limiting Middleware

Provides rate limiting for authentication and other sensitive endpoints.
Uses Redis for distributed rate limiting.
"""

from fastapi import Request, HTTPException, status
from typing import Callable
import logging

from app.services.session_service import session_service

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiting using Redis"""

    @staticmethod
    def check_rate_limit(
        key: str,
        limit: int,
        window: int = 3600,
        error_message: str = "Too many requests. Please try again later."
    ):
        """
        Check rate limit decorator

        Args:
            key: Rate limit key prefix
            limit: Maximum number of requests
            window: Time window in seconds
            error_message: Error message to return

        Returns:
            Decorator function
        """
        def decorator(func: Callable):
            async def wrapper(*args, **kwargs):
                # Extract request from args/kwargs
                request = None
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
                if not request and 'request' in kwargs:
                    request = kwargs['request']

                if request:
                    # Get client IP
                    client_ip = request.client.host if request.client else "unknown"

                    # Create rate limit key
                    rate_key = f"{key}:{client_ip}"

                    # Check rate limit
                    count, is_allowed = session_service.increment_rate_limit(
                        rate_key,
                        limit,
                        window
                    )

                    if not is_allowed:
                        logger.warning(
                            f"Rate limit exceeded for {rate_key}: {count}/{limit}"
                        )
                        raise HTTPException(
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail=error_message,
                            headers={"Retry-After": str(window)}
                        )

                return await func(*args, **kwargs)

            return wrapper
        return decorator

    @staticmethod
    def check_email_rate_limit(email: str, limit: int = 5, window: int = 3600):
        """
        Check email-based rate limit

        Args:
            email: User's email
            limit: Maximum number of requests
            window: Time window in seconds

        Raises:
            HTTPException: If rate limit exceeded
        """
        rate_key = f"email:{email}"
        count, is_allowed = session_service.increment_rate_limit(
            rate_key,
            limit,
            window
        )

        if not is_allowed:
            logger.warning(f"Rate limit exceeded for email {email}: {count}/{limit}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many requests for this email. Please try again in {window // 60} minutes.",
                headers={"Retry-After": str(window)}
            )

    @staticmethod
    def check_login_attempts(email: str, limit: int = 5, window: int = 900):
        """
        Check login attempt rate limit

        Args:
            email: User's email
            limit: Maximum number of login attempts
            window: Time window in seconds (default 15 minutes)

        Raises:
            HTTPException: If rate limit exceeded
        """
        rate_key = f"login:{email}"
        count, is_allowed = session_service.increment_rate_limit(
            rate_key,
            limit,
            window
        )

        if not is_allowed:
            logger.warning(f"Login rate limit exceeded for {email}: {count}/{limit}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many login attempts. Please try again in {window // 60} minutes.",
                headers={"Retry-After": str(window)}
            )

    @staticmethod
    def reset_login_attempts(email: str):
        """
        Reset login attempt counter after successful login

        Args:
            email: User's email
        """
        rate_key = f"login:{email}"
        session_service.reset_rate_limit(rate_key)


# Rate limit decorators for common use cases

def rate_limit_auth(limit: int = 5, window: int = 900):
    """
    Rate limit authentication endpoints

    Args:
        limit: Maximum requests (default: 5)
        window: Time window in seconds (default: 15 minutes)
    """
    return RateLimiter.check_rate_limit(
        "auth",
        limit,
        window,
        f"Too many authentication attempts. Please try again in {window // 60} minutes."
    )


def rate_limit_password_reset(limit: int = 3, window: int = 3600):
    """
    Rate limit password reset requests

    Args:
        limit: Maximum requests (default: 3)
        window: Time window in seconds (default: 1 hour)
    """
    return RateLimiter.check_rate_limit(
        "password_reset",
        limit,
        window,
        f"Too many password reset requests. Please try again in {window // 60} minutes."
    )


def rate_limit_2fa(limit: int = 10, window: int = 900):
    """
    Rate limit 2FA verification attempts

    Args:
        limit: Maximum requests (default: 10)
        window: Time window in seconds (default: 15 minutes)
    """
    return RateLimiter.check_rate_limit(
        "2fa",
        limit,
        window,
        f"Too many verification attempts. Please try again in {window // 60} minutes."
    )
