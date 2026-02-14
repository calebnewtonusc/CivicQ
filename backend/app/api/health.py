"""
Comprehensive Health Check Endpoints for CivicQ

Provides multiple health check endpoints for monitoring different system components:
- /health - Basic liveness check
- /health/ready - Readiness check (all dependencies healthy)
- /health/db - Database connectivity
- /health/redis - Redis connectivity
- /health/celery - Celery worker status
- /health/storage - S3/R2 storage connectivity
- /health/system - System resource usage
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.monitoring import HealthChecker
from app.database.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    """
    Basic liveness check

    Returns 200 if the application is running.
    Use this for Kubernetes liveness probes.
    """
    return {
        "status": "healthy",
        "service": "civicq-api",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
    }


@router.get("/health/ready", tags=["Health"])
async def readiness_check(db: Session = Depends(get_db)):
    """
    Comprehensive readiness check

    Checks all critical dependencies and returns 200 only if all are healthy.
    Use this for Kubernetes readiness probes.
    """
    checks = {}
    overall_status = "healthy"
    status_code = status.HTTP_200_OK

    # Check database
    try:
        db_check = HealthChecker.check_database(db)
        checks["database"] = db_check
        if db_check["status"] != "healthy":
            overall_status = "unhealthy"
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    except Exception as e:
        checks["database"] = {"status": "error", "error": str(e)}
        overall_status = "unhealthy"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    # Check Redis
    try:
        redis_check = HealthChecker.check_redis(settings.REDIS_URL)
        checks["redis"] = redis_check
        if redis_check["status"] != "healthy":
            overall_status = "unhealthy"
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    except Exception as e:
        checks["redis"] = {"status": "error", "error": str(e)}
        overall_status = "unhealthy"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    # Check Celery (optional - don't fail readiness if Celery is down)
    try:
        celery_check = HealthChecker.check_celery()
        checks["celery"] = celery_check
        # Don't mark as unhealthy if Celery is down, just warn
        if celery_check["status"] != "healthy":
            if overall_status == "healthy":
                overall_status = "degraded"
    except Exception as e:
        checks["celery"] = {"status": "error", "error": str(e)}
        if overall_status == "healthy":
            overall_status = "degraded"

    # Check storage (optional - don't fail readiness if S3 is down)
    try:
        storage_check = HealthChecker.check_storage()
        checks["storage"] = storage_check
        if storage_check["status"] == "unhealthy":
            if overall_status == "healthy":
                overall_status = "degraded"
    except Exception as e:
        checks["storage"] = {"status": "error", "error": str(e)}
        if overall_status == "healthy":
            overall_status = "degraded"

    response = {
        "status": overall_status,
        "service": "civicq-api",
        "environment": settings.ENVIRONMENT,
        "checks": checks,
    }

    return JSONResponse(content=response, status_code=status_code)


@router.get("/health/db", tags=["Health"])
async def database_health(db: Session = Depends(get_db)):
    """
    Database connectivity and performance check

    Returns detailed information about database connection pool and query performance.
    """
    try:
        check_result = HealthChecker.check_database(db)

        status_code = (
            status.HTTP_200_OK
            if check_result["status"] == "healthy"
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )

        return JSONResponse(content=check_result, status_code=status_code)
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return JSONResponse(
            content={
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__,
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@router.get("/health/redis", tags=["Health"])
async def redis_health():
    """
    Redis connectivity and performance check

    Returns detailed information about Redis connection and memory usage.
    """
    try:
        check_result = HealthChecker.check_redis(settings.REDIS_URL)

        status_code = (
            status.HTTP_200_OK
            if check_result["status"] == "healthy"
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )

        return JSONResponse(content=check_result, status_code=status_code)
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return JSONResponse(
            content={
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__,
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@router.get("/health/celery", tags=["Health"])
async def celery_health():
    """
    Celery worker status check

    Returns information about active Celery workers and their statistics.
    """
    try:
        check_result = HealthChecker.check_celery()

        status_code = (
            status.HTTP_200_OK
            if check_result["status"] == "healthy"
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )

        return JSONResponse(content=check_result, status_code=status_code)
    except Exception as e:
        logger.error(f"Celery health check failed: {e}")
        return JSONResponse(
            content={
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__,
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@router.get("/health/storage", tags=["Health"])
async def storage_health():
    """
    S3/R2 storage connectivity check

    Returns information about object storage connectivity and performance.
    """
    try:
        check_result = HealthChecker.check_storage()

        # Not configured is OK
        if check_result["status"] == "not_configured":
            status_code = status.HTTP_200_OK
        elif check_result["status"] == "healthy":
            status_code = status.HTTP_200_OK
        else:
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        return JSONResponse(content=check_result, status_code=status_code)
    except Exception as e:
        logger.error(f"Storage health check failed: {e}")
        return JSONResponse(
            content={
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__,
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@router.get("/health/system", tags=["Health"])
async def system_health():
    """
    System resource usage check

    Returns information about CPU, memory, and disk usage.
    """
    try:
        check_result = HealthChecker.check_system_resources()

        # Warning status still returns 200
        status_code = (
            status.HTTP_200_OK
            if check_result["status"] in ["healthy", "warning"]
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )

        return JSONResponse(content=check_result, status_code=status_code)
    except Exception as e:
        logger.error(f"System health check failed: {e}")
        return JSONResponse(
            content={
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__,
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@router.get("/health/detailed", tags=["Health"])
async def detailed_health(db: Session = Depends(get_db)):
    """
    Detailed health check with all system components

    Returns comprehensive health information for all monitored components.
    This endpoint is useful for debugging but may be slower than individual checks.
    """
    checks = {}

    # Database
    try:
        checks["database"] = HealthChecker.check_database(db)
    except Exception as e:
        checks["database"] = {"status": "error", "error": str(e)}

    # Redis
    try:
        checks["redis"] = HealthChecker.check_redis(settings.REDIS_URL)
    except Exception as e:
        checks["redis"] = {"status": "error", "error": str(e)}

    # Celery
    try:
        checks["celery"] = HealthChecker.check_celery()
    except Exception as e:
        checks["celery"] = {"status": "error", "error": str(e)}

    # Storage
    try:
        checks["storage"] = HealthChecker.check_storage()
    except Exception as e:
        checks["storage"] = {"status": "error", "error": str(e)}

    # System resources
    try:
        checks["system"] = HealthChecker.check_system_resources()
    except Exception as e:
        checks["system"] = {"status": "error", "error": str(e)}

    # Determine overall status
    unhealthy_count = sum(1 for c in checks.values() if c.get("status") == "unhealthy")
    error_count = sum(1 for c in checks.values() if c.get("status") == "error")

    if unhealthy_count > 0 or error_count > 0:
        overall_status = "unhealthy"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        warning_count = sum(1 for c in checks.values() if c.get("status") == "warning")
        overall_status = "degraded" if warning_count > 0 else "healthy"
        status_code = status.HTTP_200_OK

    response = {
        "status": overall_status,
        "service": "civicq-api",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
        "checks": checks,
        "summary": {
            "total_checks": len(checks),
            "healthy": sum(1 for c in checks.values() if c.get("status") == "healthy"),
            "unhealthy": unhealthy_count,
            "errors": error_count,
            "warnings": sum(1 for c in checks.values() if c.get("status") == "warning"),
        },
    }

    return JSONResponse(content=response, status_code=status_code)
