# ============================================================================
# CivicQ Backend - Multi-Stage Production Dockerfile
# ============================================================================
# This Dockerfile creates optimized production builds for:
# - FastAPI backend API server
# - Celery worker (background tasks)
# - Celery beat (scheduled tasks)
#
# Build stages:
# 1. base - Base Python image with system dependencies
# 2. dependencies - Python dependencies installation
# 3. development - Development environment with hot reload
# 4. production - Optimized production build
# ============================================================================

# ============================================================================
# Stage 1: Base - System Dependencies
# ============================================================================
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # PostgreSQL client for database operations
    postgresql-client \
    # GCC compiler for Python C extensions
    gcc \
    g++ \
    # FFmpeg for video processing
    ffmpeg \
    # Image processing libraries (for Pillow)
    libjpeg-dev \
    libpng-dev \
    libwebp-dev \
    # OpenCV dependencies
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # Network utilities
    curl \
    wget \
    # Build tools
    build-essential \
    libpq-dev \
    # Clean up
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r civicq && useradd -r -g civicq -u 1000 civicq

# Create application directory
WORKDIR /app

# ============================================================================
# Stage 2: Dependencies - Python Package Installation
# ============================================================================
FROM base AS dependencies

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Download sentence-transformers model (for embeddings)
# This pre-downloads the model to avoid runtime downloads
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# ============================================================================
# Stage 3: Development - Development Environment
# ============================================================================
FROM dependencies AS development

# Install development tools
RUN pip install --no-cache-dir \
    ipython \
    ipdb \
    watchdog

# Copy application code
COPY --chown=civicq:civicq . .

# Create directories for logs and media
RUN mkdir -p /app/logs /app/media && \
    chown -R civicq:civicq /app

# Switch to non-root user
USER civicq

# Expose port
EXPOSE 8000

# Development startup with hot reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]

# ============================================================================
# Stage 4: Production - Optimized Production Build
# ============================================================================
FROM dependencies AS production

# Copy only necessary application files
COPY --chown=civicq:civicq app/ /app/app/
COPY --chown=civicq:civicq alembic/ /app/alembic/
COPY --chown=civicq:civicq alembic.ini /app/alembic.ini
COPY --chown=civicq:civicq scripts/ /app/scripts/

# Create necessary directories
RUN mkdir -p /app/logs /app/media && \
    chown -R civicq:civicq /app

# Switch to non-root user for security
USER civicq

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production startup (without reload)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--log-level", "info"]

# ============================================================================
# Stage 5: Celery Worker - Background Task Processing
# ============================================================================
FROM production AS celery-worker

# Override CMD for Celery worker
CMD ["celery", "-A", "app.worker", "worker", "--loglevel=info", "--concurrency=4", "--max-tasks-per-child=100"]

# ============================================================================
# Stage 6: Celery Beat - Scheduled Task Scheduler
# ============================================================================
FROM production AS celery-beat

# Override CMD for Celery beat
CMD ["celery", "-A", "app.worker", "beat", "--loglevel=info"]
