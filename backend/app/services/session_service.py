"""
Session Service

Redis-based session management for secure token handling and blacklisting.
Provides session storage, token blacklisting, and rate limiting support.
"""

import json
import redis
from typing import Optional, Dict, Any
from datetime import timedelta
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class SessionService:
    """Service for managing sessions and token blacklisting with Redis"""

    def __init__(self):
        """Initialize Redis connection"""
        self.redis_client = None
        try:
            if hasattr(settings, 'REDIS_URL') and settings.REDIS_URL:
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Redis connection established")
            else:
                logger.warning("Redis URL not configured - session features disabled")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            self.redis_client = None

    def _get_session_key(self, session_id: str) -> str:
        """Generate Redis key for session"""
        return f"session:{session_id}"

    def _get_token_blacklist_key(self, token: str) -> str:
        """Generate Redis key for blacklisted token"""
        return f"blacklist:token:{token}"

    def _get_user_session_key(self, user_id: int) -> str:
        """Generate Redis key for user sessions"""
        return f"user:sessions:{user_id}"

    def create_session(
        self,
        session_id: str,
        user_id: int,
        data: Dict[str, Any],
        expires_in: int = 86400  # 24 hours default
    ) -> bool:
        """
        Create a new session

        Args:
            session_id: Unique session identifier
            user_id: User ID
            data: Session data to store
            expires_in: Session expiration time in seconds

        Returns:
            True if session created successfully
        """
        if not self.redis_client:
            return True  # Fallback mode - no session management

        try:
            session_key = self._get_session_key(session_id)
            session_data = {
                "user_id": user_id,
                **data
            }

            # Store session data
            self.redis_client.setex(
                session_key,
                expires_in,
                json.dumps(session_data)
            )

            # Track session for user
            user_sessions_key = self._get_user_session_key(user_id)
            self.redis_client.sadd(user_sessions_key, session_id)
            self.redis_client.expire(user_sessions_key, expires_in)

            logger.info(f"Session created for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to create session: {str(e)}")
            return False

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data

        Args:
            session_id: Session identifier

        Returns:
            Session data or None if not found
        """
        if not self.redis_client:
            return None

        try:
            session_key = self._get_session_key(session_id)
            data = self.redis_client.get(session_key)

            if data:
                return json.loads(data)
            return None

        except Exception as e:
            logger.error(f"Failed to get session: {str(e)}")
            return None

    def update_session(
        self,
        session_id: str,
        data: Dict[str, Any],
        extend_ttl: bool = True
    ) -> bool:
        """
        Update session data

        Args:
            session_id: Session identifier
            data: New session data
            extend_ttl: Whether to extend session expiration

        Returns:
            True if session updated successfully
        """
        if not self.redis_client:
            return True

        try:
            session_key = self._get_session_key(session_id)
            existing_data = self.get_session(session_id)

            if not existing_data:
                return False

            # Merge data
            updated_data = {**existing_data, **data}

            # Get remaining TTL
            ttl = self.redis_client.ttl(session_key)
            if ttl > 0:
                self.redis_client.setex(
                    session_key,
                    ttl if not extend_ttl else 86400,  # Extend to 24 hours if requested
                    json.dumps(updated_data)
                )
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to update session: {str(e)}")
            return False

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session

        Args:
            session_id: Session identifier

        Returns:
            True if session deleted successfully
        """
        if not self.redis_client:
            return True

        try:
            session_key = self._get_session_key(session_id)
            session_data = self.get_session(session_id)

            if session_data:
                user_id = session_data.get("user_id")
                if user_id:
                    user_sessions_key = self._get_user_session_key(user_id)
                    self.redis_client.srem(user_sessions_key, session_id)

            self.redis_client.delete(session_key)
            logger.info(f"Session deleted: {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete session: {str(e)}")
            return False

    def delete_all_user_sessions(self, user_id: int) -> bool:
        """
        Delete all sessions for a user

        Args:
            user_id: User ID

        Returns:
            True if all sessions deleted successfully
        """
        if not self.redis_client:
            return True

        try:
            user_sessions_key = self._get_user_session_key(user_id)
            session_ids = self.redis_client.smembers(user_sessions_key)

            for session_id in session_ids:
                session_key = self._get_session_key(session_id)
                self.redis_client.delete(session_key)

            self.redis_client.delete(user_sessions_key)
            logger.info(f"All sessions deleted for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete user sessions: {str(e)}")
            return False

    def blacklist_token(self, token: str, expires_in: int = 86400) -> bool:
        """
        Blacklist a token (e.g., on logout or password change)

        Args:
            token: JWT token to blacklist
            expires_in: How long to keep token blacklisted (seconds)

        Returns:
            True if token blacklisted successfully
        """
        if not self.redis_client:
            return True

        try:
            blacklist_key = self._get_token_blacklist_key(token)
            self.redis_client.setex(blacklist_key, expires_in, "1")
            logger.info("Token blacklisted")
            return True

        except Exception as e:
            logger.error(f"Failed to blacklist token: {str(e)}")
            return False

    def is_token_blacklisted(self, token: str) -> bool:
        """
        Check if a token is blacklisted

        Args:
            token: JWT token to check

        Returns:
            True if token is blacklisted
        """
        if not self.redis_client:
            return False

        try:
            blacklist_key = self._get_token_blacklist_key(token)
            return self.redis_client.exists(blacklist_key) > 0

        except Exception as e:
            logger.error(f"Failed to check token blacklist: {str(e)}")
            return False

    def increment_rate_limit(
        self,
        key: str,
        limit: int,
        window: int = 3600
    ) -> tuple[int, bool]:
        """
        Increment rate limit counter

        Args:
            key: Rate limit key (e.g., "login:user@email.com")
            limit: Maximum number of attempts
            window: Time window in seconds

        Returns:
            Tuple of (current_count, is_allowed)
        """
        if not self.redis_client:
            return (0, True)

        try:
            rate_key = f"rate:{key}"
            current = self.redis_client.incr(rate_key)

            if current == 1:
                self.redis_client.expire(rate_key, window)

            is_allowed = current <= limit
            return (current, is_allowed)

        except Exception as e:
            logger.error(f"Failed to increment rate limit: {str(e)}")
            return (0, True)  # Allow on error

    def reset_rate_limit(self, key: str) -> bool:
        """
        Reset rate limit counter

        Args:
            key: Rate limit key

        Returns:
            True if reset successfully
        """
        if not self.redis_client:
            return True

        try:
            rate_key = f"rate:{key}"
            self.redis_client.delete(rate_key)
            return True

        except Exception as e:
            logger.error(f"Failed to reset rate limit: {str(e)}")
            return False


# Global session service instance
session_service = SessionService()
