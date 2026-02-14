"""
Cache Service

Comprehensive Redis caching service with invalidation strategies,
cache warming, and statistics tracking.
"""

import json
import logging
import hashlib
from typing import Any, Optional, List, Callable, Dict
from datetime import datetime, timedelta
from functools import wraps
import redis
from redis.exceptions import RedisError

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Redis-based caching service with advanced features"""

    def __init__(self):
        """Initialize cache service with Redis connection"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache service initialized successfully")
        except RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None

    def _is_available(self) -> bool:
        """Check if Redis is available"""
        return self.redis_client is not None

    def _serialize(self, value: Any) -> str:
        """Serialize value to JSON string"""
        try:
            return json.dumps(value, default=str)
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to serialize value: {e}")
            raise

    def _deserialize(self, value: str) -> Any:
        """Deserialize JSON string to value"""
        try:
            return json.loads(value)
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to deserialize value: {e}")
            return None

    # Basic Cache Operations

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self._is_available():
            return None

        try:
            value = self.redis_client.get(key)
            if value is None:
                logger.debug(f"Cache miss: {key}")
                return None

            logger.debug(f"Cache hit: {key}")
            return self._deserialize(value)
        except RedisError as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        nx: bool = False
    ) -> bool:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None for no expiration)
            nx: Only set if key doesn't exist

        Returns:
            True if successful, False otherwise
        """
        if not self._is_available():
            return False

        try:
            serialized = self._serialize(value)
            if nx:
                result = self.redis_client.set(key, serialized, ex=ttl, nx=True)
            else:
                result = self.redis_client.set(key, serialized, ex=ttl)

            if result:
                logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return bool(result)
        except RedisError as e:
            logger.error(f"Redis set error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Delete key from cache

        Args:
            key: Cache key

        Returns:
            True if key was deleted, False otherwise
        """
        if not self._is_available():
            return False

        try:
            result = self.redis_client.delete(key)
            if result:
                logger.debug(f"Cache delete: {key}")
            return bool(result)
        except RedisError as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        if not self._is_available():
            return False

        try:
            return bool(self.redis_client.exists(key))
        except RedisError as e:
            logger.error(f"Redis exists error for key {key}: {e}")
            return False

    def ttl(self, key: str) -> int:
        """
        Get remaining TTL for key

        Args:
            key: Cache key

        Returns:
            Remaining TTL in seconds, -1 if no TTL, -2 if key doesn't exist
        """
        if not self._is_available():
            return -2

        try:
            return self.redis_client.ttl(key)
        except RedisError as e:
            logger.error(f"Redis TTL error for key {key}: {e}")
            return -2

    # Batch Operations

    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple values from cache

        Args:
            keys: List of cache keys

        Returns:
            Dictionary of key-value pairs
        """
        if not self._is_available() or not keys:
            return {}

        try:
            values = self.redis_client.mget(keys)
            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    result[key] = self._deserialize(value)

            logger.debug(f"Cache get_many: {len(result)}/{len(keys)} hits")
            return result
        except RedisError as e:
            logger.error(f"Redis mget error: {e}")
            return {}

    def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Set multiple values in cache

        Args:
            mapping: Dictionary of key-value pairs
            ttl: Time-to-live in seconds

        Returns:
            True if successful, False otherwise
        """
        if not self._is_available() or not mapping:
            return False

        try:
            pipe = self.redis_client.pipeline()
            for key, value in mapping.items():
                serialized = self._serialize(value)
                pipe.set(key, serialized, ex=ttl)
            pipe.execute()

            logger.debug(f"Cache set_many: {len(mapping)} keys (TTL: {ttl}s)")
            return True
        except RedisError as e:
            logger.error(f"Redis mset error: {e}")
            return False

    def delete_many(self, keys: List[str]) -> int:
        """
        Delete multiple keys from cache

        Args:
            keys: List of cache keys

        Returns:
            Number of keys deleted
        """
        if not self._is_available() or not keys:
            return 0

        try:
            count = self.redis_client.delete(*keys)
            logger.debug(f"Cache delete_many: {count} keys deleted")
            return count
        except RedisError as e:
            logger.error(f"Redis delete_many error: {e}")
            return 0

    # Pattern-based Operations

    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern

        Args:
            pattern: Redis key pattern (e.g., "user:*")

        Returns:
            Number of keys deleted
        """
        if not self._is_available():
            return 0

        try:
            keys = list(self.redis_client.scan_iter(match=pattern, count=100))
            if not keys:
                return 0

            count = self.redis_client.delete(*keys)
            logger.info(f"Cache invalidate pattern '{pattern}': {count} keys deleted")
            return count
        except RedisError as e:
            logger.error(f"Redis delete_pattern error for {pattern}: {e}")
            return 0

    def get_keys(self, pattern: str = "*") -> List[str]:
        """
        Get all keys matching pattern

        Args:
            pattern: Redis key pattern

        Returns:
            List of matching keys
        """
        if not self._is_available():
            return []

        try:
            keys = list(self.redis_client.scan_iter(match=pattern, count=100))
            return keys
        except RedisError as e:
            logger.error(f"Redis get_keys error for {pattern}: {e}")
            return []

    # Cache Warming

    def warm_cache(
        self,
        key: str,
        loader_func: Callable,
        ttl: Optional[int] = None,
        force: bool = False
    ) -> Optional[Any]:
        """
        Warm cache with data from loader function

        Args:
            key: Cache key
            loader_func: Function that loads the data
            ttl: Time-to-live in seconds
            force: Force refresh even if cached

        Returns:
            Loaded/cached value
        """
        if not force:
            cached = self.get(key)
            if cached is not None:
                return cached

        try:
            value = loader_func()
            if value is not None:
                self.set(key, value, ttl=ttl)
                logger.info(f"Cache warmed: {key}")
            return value
        except Exception as e:
            logger.error(f"Cache warming failed for {key}: {e}")
            return None

    def warm_many(
        self,
        items: List[tuple],  # List of (key, loader_func, ttl) tuples
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Warm multiple cache entries

        Args:
            items: List of (key, loader_func, ttl) tuples
            force: Force refresh even if cached

        Returns:
            Dictionary of loaded values
        """
        results = {}
        for key, loader_func, ttl in items:
            try:
                value = self.warm_cache(key, loader_func, ttl=ttl, force=force)
                if value is not None:
                    results[key] = value
            except Exception as e:
                logger.error(f"Failed to warm cache for {key}: {e}")

        logger.info(f"Cache warming completed: {len(results)}/{len(items)} items")
        return results

    # Cache Statistics

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache statistics
        """
        if not self._is_available():
            return {"available": False}

        try:
            info = self.redis_client.info("stats")
            memory = self.redis_client.info("memory")

            return {
                "available": True,
                "total_keys": self.redis_client.dbsize(),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                ),
                "memory_used": memory.get("used_memory_human", "0"),
                "memory_peak": memory.get("used_memory_peak_human", "0"),
                "evicted_keys": info.get("evicted_keys", 0),
            }
        except RedisError as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"available": False, "error": str(e)}

    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage"""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)

    def clear_all(self) -> bool:
        """
        Clear all cache (use with caution!)

        Returns:
            True if successful, False otherwise
        """
        if not self._is_available():
            return False

        try:
            self.redis_client.flushdb()
            logger.warning("Cache cleared: all keys deleted")
            return True
        except RedisError as e:
            logger.error(f"Failed to clear cache: {e}")
            return False

    # Utility Methods

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment counter

        Args:
            key: Cache key
            amount: Amount to increment

        Returns:
            New value or None if error
        """
        if not self._is_available():
            return None

        try:
            return self.redis_client.incr(key, amount)
        except RedisError as e:
            logger.error(f"Redis increment error for {key}: {e}")
            return None

    def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Decrement counter

        Args:
            key: Cache key
            amount: Amount to decrement

        Returns:
            New value or None if error
        """
        if not self._is_available():
            return None

        try:
            return self.redis_client.decr(key, amount)
        except RedisError as e:
            logger.error(f"Redis decrement error for {key}: {e}")
            return None

    def expire(self, key: str, ttl: int) -> bool:
        """
        Set expiration on existing key

        Args:
            key: Cache key
            ttl: Time-to-live in seconds

        Returns:
            True if successful, False otherwise
        """
        if not self._is_available():
            return False

        try:
            return bool(self.redis_client.expire(key, ttl))
        except RedisError as e:
            logger.error(f"Redis expire error for {key}: {e}")
            return False


# Decorator for caching function results
def cached(
    key_prefix: str,
    ttl: int = 300,
    key_builder: Optional[Callable] = None
):
    """
    Decorator to cache function results

    Args:
        key_prefix: Prefix for cache key
        ttl: Time-to-live in seconds
        key_builder: Optional function to build cache key from arguments

    Usage:
        @cached(key_prefix="user", ttl=300)
        def get_user(user_id: int):
            return fetch_user_from_db(user_id)
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                # Default: hash the arguments
                arg_hash = hashlib.md5(
                    str((args, sorted(kwargs.items()))).encode()
                ).hexdigest()[:8]
                cache_key = f"{key_prefix}:{arg_hash}"

            # Try to get from cache
            cached_value = cache_service.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Call function and cache result
            result = await func(*args, **kwargs)
            if result is not None:
                cache_service.set(cache_key, result, ttl=ttl)

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                arg_hash = hashlib.md5(
                    str((args, sorted(kwargs.items()))).encode()
                ).hexdigest()[:8]
                cache_key = f"{key_prefix}:{arg_hash}"

            # Try to get from cache
            cached_value = cache_service.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Call function and cache result
            result = func(*args, **kwargs)
            if result is not None:
                cache_service.set(cache_key, result, ttl=ttl)

            return result

        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


# Global cache service instance
cache_service = CacheService()
