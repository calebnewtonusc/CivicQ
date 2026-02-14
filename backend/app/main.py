"""
CivicQ API - Main Application Entry Point

This is the core FastAPI application for CivicQ, a civic engagement platform
for local elections that turns campaigning into structured Q&A.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import time

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.sentry import init_sentry
from app.core.metrics import app_info
from app.middleware.metrics import MetricsMiddleware, metrics_endpoint
from app.api import (
    auth,
    ballots,
    contests,
    questions,
    candidates,
    moderation,
    admin,
    cities,
    videos,
)
from app.api.admin_moderation import router as admin_moderation_router
from app.api.v1.endpoints import llm
from app.api import health

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize Sentry
init_sentry()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="CivicQ API",
    description="A civic engagement platform for local elections",
    version="1.0.0",
    docs_url="/api/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT != "production" else None,
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware for security
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# Add metrics middleware
if settings.ENABLE_METRICS:
    app.add_middleware(MetricsMiddleware)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Metrics endpoint
@app.get("/metrics", tags=["Monitoring"])
async def get_metrics(request: Request):
    """Prometheus metrics endpoint"""
    return metrics_endpoint(request)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "CivicQ API",
        "version": "1.0.0",
        "docs": "/api/docs" if settings.ENVIRONMENT != "production" else "Documentation disabled in production",
    }


# Include API routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(ballots.router, prefix="/api", tags=["Ballots"])
app.include_router(contests.router, prefix="/api/contests", tags=["Contests"])
app.include_router(questions.router, prefix="/api", tags=["Questions"])
app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates"])
app.include_router(moderation.router, prefix="/api", tags=["Moderation"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin - Ballot Import"])
app.include_router(admin_moderation_router, prefix="/api/admin", tags=["Admin - Moderation"])
app.include_router(cities.router, prefix="/api", tags=["Cities"])
app.include_router(videos.router, prefix="/api/videos", tags=["Videos"])
app.include_router(llm.router, prefix="/api/llm", tags=["AI Features"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "type": "internal_error"
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Tasks to run on application startup"""
    logger.info("Starting CivicQ API")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    # Set application info for Prometheus
    app_info.info({
        'version': '1.0.0',
        'environment': settings.ENVIRONMENT,
        'debug': str(settings.DEBUG),
    })

    logger.info("Monitoring and observability initialized")
    logger.info(f"Metrics enabled: {settings.ENABLE_METRICS}")
    logger.info(f"Sentry enabled: {settings.SENTRY_DSN is not None}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Tasks to run on application shutdown"""
    logger.info("Shutting down CivicQ API")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
