"""
Caching Middleware

HTTP response caching with ETag support, compression, and intelligent cache control.
"""

import hashlib
import gzip
import logging
from typing import Callable, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import Headers

from app.services.cache_service import cache_service
from app.core.cache_keys import CacheKeys

logger = logging.getLogger(__name__)


class CachingMiddleware(BaseHTTPMiddleware):
    """
    HTTP caching middleware with ETag support and response compression
    """

    # Routes that should be cached
    CACHEABLE_ROUTES = {
        "/api/ballots": CacheKeys.TTL_5_MINUTES,
        "/api/contests": CacheKeys.TTL_5_MINUTES,
        "/api/questions": CacheKeys.TTL_5_MINUTES,
        "/api/candidates": CacheKeys.TTL_30_MINUTES,
        "/api/cities": CacheKeys.TTL_1_HOUR,
        "/api/videos": CacheKeys.TTL_1_HOUR,
    }

    # Routes that should never be cached
    UNCACHEABLE_ROUTES = [
        "/api/auth",
        "/api/admin",
        "/api/moderation",
        "/health",
        "/metrics",
    ]

    def __init__(self, app, enable_compression: bool = True):
        super().__init__(app)
        self.enable_compression = enable_compression

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with caching logic

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response with appropriate cache headers
        """
        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)

        # Check if route should be cached
        if not self._should_cache(request):
            return await call_next(request)

        # Build cache key
        cache_key = self._build_cache_key(request)

        # Check for cached response
        cached_response = cache_service.get(cache_key)
        if cached_response:
            logger.debug(f"Cache hit: {cache_key}")
            return self._create_response_from_cache(cached_response, request)

        # Get fresh response
        response = await call_next(request)

        # Cache successful responses
        if response.status_code == 200:
            await self._cache_response(cache_key, request, response)

        # Add cache control headers
        self._add_cache_headers(response, request.url.path)

        return response

    def _should_cache(self, request: Request) -> bool:
        """
        Determine if request should be cached

        Args:
            request: HTTP request

        Returns:
            True if request should be cached
        """
        path = request.url.path

        # Never cache auth or admin routes
        for uncacheable in self.UNCACHEABLE_ROUTES:
            if path.startswith(uncacheable):
                return False

        # Cache specific routes
        for cacheable in self.CACHEABLE_ROUTES.keys():
            if path.startswith(cacheable):
                return True

        return False

    def _build_cache_key(self, request: Request) -> str:
        """
        Build cache key from request

        Args:
            request: HTTP request

        Returns:
            Cache key string
        """
        path = request.url.path
        query_params = str(request.query_params)

        # Include relevant headers in cache key
        accept_encoding = request.headers.get("accept-encoding", "")
        accept = request.headers.get("accept", "")

        # Create hash of all cache key components
        key_components = f"{path}:{query_params}:{accept}:{accept_encoding}"
        key_hash = hashlib.md5(key_components.encode()).hexdigest()[:12]

        return CacheKeys.api_response(path, key_hash)

    async def _cache_response(
        self,
        cache_key: str,
        request: Request,
        response: Response
    ):
        """
        Cache response data

        Args:
            cache_key: Cache key
            request: HTTP request
            response: HTTP response
        """
        try:
            # Read response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            # Determine TTL based on route
            ttl = self._get_ttl_for_route(request.url.path)

            # Calculate ETag
            etag = self._calculate_etag(body)

            # Store in cache
            cache_data = {
                "body": body.decode("utf-8"),
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "etag": etag,
            }

            cache_service.set(cache_key, cache_data, ttl=ttl)
            logger.debug(f"Cached response: {cache_key} (TTL: {ttl}s)")

            # Reconstruct response with body
            response.body_iterator = self._to_async_iterator(body)

        except Exception as e:
            logger.error(f"Failed to cache response: {e}")

    def _create_response_from_cache(
        self,
        cached_data: dict,
        request: Request
    ) -> Response:
        """
        Create response from cached data

        Args:
            cached_data: Cached response data
            request: HTTP request

        Returns:
            HTTP response
        """
        # Check ETag for conditional requests
        if_none_match = request.headers.get("if-none-match")
        if if_none_match and if_none_match == cached_data.get("etag"):
            return Response(status_code=304, headers={"ETag": if_none_match})

        # Create response
        body = cached_data["body"]
        headers = cached_data["headers"]
        headers["ETag"] = cached_data["etag"]
        headers["X-Cache"] = "HIT"

        # Apply compression if supported
        if self.enable_compression and "gzip" in request.headers.get("accept-encoding", ""):
            body = self._compress_response(body.encode())
            headers["Content-Encoding"] = "gzip"
            headers["Content-Length"] = str(len(body))
            return Response(content=body, status_code=200, headers=headers)

        return Response(content=body, status_code=200, headers=headers)

    def _get_ttl_for_route(self, path: str) -> int:
        """
        Get TTL for route

        Args:
            path: Request path

        Returns:
            TTL in seconds
        """
        for route, ttl in self.CACHEABLE_ROUTES.items():
            if path.startswith(route):
                return ttl
        return CacheKeys.TTL_5_MINUTES

    def _add_cache_headers(self, response: Response, path: str):
        """
        Add cache control headers to response

        Args:
            response: HTTP response
            path: Request path
        """
        ttl = self._get_ttl_for_route(path)

        # Set Cache-Control header
        response.headers["Cache-Control"] = f"public, max-age={ttl}"

        # Add Vary header for content negotiation
        response.headers["Vary"] = "Accept-Encoding, Accept"

        # Mark as cache miss if not already set
        if "X-Cache" not in response.headers:
            response.headers["X-Cache"] = "MISS"

    @staticmethod
    def _calculate_etag(body: bytes) -> str:
        """
        Calculate ETag for response body

        Args:
            body: Response body

        Returns:
            ETag string
        """
        return f'"{hashlib.md5(body).hexdigest()}"'

    @staticmethod
    def _compress_response(body: bytes) -> bytes:
        """
        Compress response body with gzip

        Args:
            body: Response body

        Returns:
            Compressed body
        """
        return gzip.compress(body, compresslevel=6)

    @staticmethod
    async def _to_async_iterator(body: bytes):
        """Convert bytes to async iterator"""
        yield body


class ETagMiddleware(BaseHTTPMiddleware):
    """
    ETag middleware for conditional requests

    Generates ETags for responses and handles If-None-Match headers.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with ETag support

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response with ETag header
        """
        # Only process GET and HEAD requests
        if request.method not in ["GET", "HEAD"]:
            return await call_next(request)

        # Get response
        response = await call_next(request)

        # Only add ETag to successful responses
        if response.status_code != 200:
            return response

        # Read response body
        try:
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            # Calculate ETag
            etag = f'"{hashlib.md5(body).hexdigest()}"'

            # Check If-None-Match header
            if_none_match = request.headers.get("if-none-match")
            if if_none_match == etag:
                return Response(
                    status_code=304,
                    headers={
                        "ETag": etag,
                        "Cache-Control": response.headers.get("Cache-Control", ""),
                    }
                )

            # Add ETag to response
            response.headers["ETag"] = etag

            # Reconstruct response
            response.body_iterator = CachingMiddleware._to_async_iterator(body)

        except Exception as e:
            logger.error(f"Failed to add ETag: {e}")

        return response


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Response compression middleware

    Compresses responses with gzip when client supports it.
    """

    # Minimum size to compress (bytes)
    MIN_SIZE = 1024

    # Compressible content types
    COMPRESSIBLE_TYPES = [
        "application/json",
        "application/javascript",
        "text/html",
        "text/css",
        "text/plain",
        "text/xml",
        "application/xml",
    ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with compression

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler

        Returns:
            Compressed HTTP response if applicable
        """
        # Check if client accepts gzip
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding.lower():
            return await call_next(request)

        # Get response
        response = await call_next(request)

        # Check if already compressed
        if response.headers.get("content-encoding"):
            return response

        # Check content type
        content_type = response.headers.get("content-type", "")
        if not any(ct in content_type for ct in self.COMPRESSIBLE_TYPES):
            return response

        try:
            # Read response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            # Only compress if body is large enough
            if len(body) < self.MIN_SIZE:
                response.body_iterator = CachingMiddleware._to_async_iterator(body)
                return response

            # Compress body
            compressed = gzip.compress(body, compresslevel=6)

            # Only use compression if it actually reduces size
            if len(compressed) < len(body):
                response.headers["Content-Encoding"] = "gzip"
                response.headers["Content-Length"] = str(len(compressed))
                response.headers["Vary"] = "Accept-Encoding"
                response.body_iterator = CachingMiddleware._to_async_iterator(compressed)
                logger.debug(f"Compressed response: {len(body)} -> {len(compressed)} bytes")
            else:
                response.body_iterator = CachingMiddleware._to_async_iterator(body)

        except Exception as e:
            logger.error(f"Compression failed: {e}")

        return response
