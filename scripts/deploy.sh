#!/bin/bash

###############################################################################
# CivicQ Production Deployment Script
#
# This script automates the deployment of CivicQ to production infrastructure.
# It handles:
# - Pre-deployment checks and validation
# - Database migrations
# - Docker container deployment
# - Health checks and rollback on failure
# - Post-deployment verification
#
# Usage: ./scripts/deploy.sh [environment]
#   environment: staging | production (default: production)
#
# Example: ./scripts/deploy.sh production
###############################################################################

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT="${1:-production}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPLOYMENT_LOG="$PROJECT_ROOT/logs/deployment-$(date +%Y%m%d-%H%M%S).log"
BACKUP_DIR="$PROJECT_ROOT/backups"
HEALTH_CHECK_RETRIES=30
HEALTH_CHECK_INTERVAL=10

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$DEPLOYMENT_LOG"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$DEPLOYMENT_LOG"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$DEPLOYMENT_LOG"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$DEPLOYMENT_LOG"
}

# Error handler
error_exit() {
    log_error "$1"
    log_error "Deployment failed. Check logs at: $DEPLOYMENT_LOG"
    exit 1
}

# Create necessary directories
mkdir -p "$(dirname "$DEPLOYMENT_LOG")"
mkdir -p "$BACKUP_DIR"

# Banner
echo "=========================================="
echo "  CivicQ Deployment Script"
echo "  Environment: $ENVIRONMENT"
echo "  Timestamp: $(date)"
echo "=========================================="
echo ""

log_info "Starting deployment to $ENVIRONMENT environment..."

# Step 1: Pre-deployment checks
log_info "Running pre-deployment checks..."

# Check if environment file exists
if [ ! -f "$PROJECT_ROOT/.env.$ENVIRONMENT" ]; then
    error_exit "Environment file .env.$ENVIRONMENT not found"
fi

# Load environment variables
set -a
source "$PROJECT_ROOT/.env.$ENVIRONMENT"
set +a

log_success "Environment variables loaded"

# Check required environment variables
REQUIRED_VARS=(
    "DATABASE_URL"
    "SECRET_KEY"
    "REDIS_URL"
)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var:-}" ]; then
        error_exit "Required environment variable $var is not set"
    fi
done

log_success "Pre-deployment checks passed"

# Step 2: Backup current database
log_info "Creating database backup..."

BACKUP_FILE="$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sql"

docker exec civicq-postgres-prod pg_dump \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_DB" \
    -F c \
    -f "/tmp/backup.dump" || error_exit "Database backup failed"

docker cp civicq-postgres-prod:/tmp/backup.dump "$BACKUP_FILE" || error_exit "Failed to copy backup file"

log_success "Database backup created: $BACKUP_FILE"

# Step 3: Pull latest code (if deploying from git)
if [ -d "$PROJECT_ROOT/.git" ]; then
    log_info "Pulling latest code from repository..."

    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    log_info "Current branch: $CURRENT_BRANCH"

    # Stash any local changes
    git stash save "Pre-deployment stash $(date)" || true

    # Pull latest changes
    git pull origin "$CURRENT_BRANCH" || error_exit "Failed to pull latest code"

    log_success "Code updated successfully"
fi

# Step 4: Build Docker images
log_info "Building Docker images..."

docker-compose -f "$PROJECT_ROOT/docker-compose.production.yml" build --no-cache || error_exit "Docker build failed"

log_success "Docker images built successfully"

# Step 5: Run database migrations
log_info "Running database migrations..."

# Create temporary container to run migrations
docker-compose -f "$PROJECT_ROOT/docker-compose.production.yml" run --rm backend \
    alembic upgrade head || error_exit "Database migrations failed"

log_success "Database migrations completed"

# Step 6: Stop old containers
log_info "Stopping old containers..."

docker-compose -f "$PROJECT_ROOT/docker-compose.production.yml" down || true

log_success "Old containers stopped"

# Step 7: Start new containers
log_info "Starting new containers..."

docker-compose -f "$PROJECT_ROOT/docker-compose.production.yml" up -d || error_exit "Failed to start containers"

log_success "Containers started"

# Step 8: Health checks
log_info "Running health checks..."

check_health() {
    local service=$1
    local url=$2
    local retries=$HEALTH_CHECK_RETRIES

    log_info "Checking health of $service..."

    while [ $retries -gt 0 ]; do
        if curl -f -s "$url" > /dev/null; then
            log_success "$service is healthy"
            return 0
        fi

        log_warning "$service not ready yet. Retrying in $HEALTH_CHECK_INTERVAL seconds... ($retries retries left)"
        sleep $HEALTH_CHECK_INTERVAL
        retries=$((retries - 1))
    done

    log_error "$service failed health check"
    return 1
}

# Check backend health
check_health "Backend" "http://localhost:8000/health" || {
    log_error "Backend health check failed. Rolling back..."
    docker-compose -f "$PROJECT_ROOT/docker-compose.production.yml" down
    # TODO: Restore from backup
    error_exit "Deployment failed. Backend is unhealthy."
}

# Check frontend health
check_health "Frontend" "http://localhost" || {
    log_warning "Frontend health check failed, but continuing..."
}

# Step 9: Smoke tests
log_info "Running smoke tests..."

# Test backend API endpoints
SMOKE_TEST_ENDPOINTS=(
    "http://localhost:8000/health"
    "http://localhost:8000/api/v1/cities"
    "http://localhost:8000/api/v1/ballots"
)

for endpoint in "${SMOKE_TEST_ENDPOINTS[@]}"; do
    log_info "Testing endpoint: $endpoint"

    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint")

    if [ "$HTTP_STATUS" -eq 200 ] || [ "$HTTP_STATUS" -eq 401 ]; then
        log_success "Endpoint $endpoint is responding (HTTP $HTTP_STATUS)"
    else
        log_warning "Endpoint $endpoint returned HTTP $HTTP_STATUS"
    fi
done

log_success "Smoke tests completed"

# Step 10: Post-deployment tasks
log_info "Running post-deployment tasks..."

# Clear caches
docker exec civicq-redis-prod redis-cli -a "$REDIS_PASSWORD" FLUSHDB || log_warning "Failed to clear Redis cache"

# Restart background workers
docker-compose -f "$PROJECT_ROOT/docker-compose.production.yml" restart celery-worker celery-beat || log_warning "Failed to restart workers"

log_success "Post-deployment tasks completed"

# Step 11: Deployment summary
echo ""
echo "=========================================="
echo "  Deployment Summary"
echo "=========================================="
echo "Environment: $ENVIRONMENT"
echo "Timestamp: $(date)"
echo "Backup: $BACKUP_FILE"
echo "Log: $DEPLOYMENT_LOG"
echo ""

# Show running containers
log_info "Running containers:"
docker-compose -f "$PROJECT_ROOT/docker-compose.production.yml" ps

echo ""
log_success "Deployment completed successfully!"
echo ""
echo "Next steps:"
echo "  1. Monitor application logs: docker-compose -f docker-compose.production.yml logs -f"
echo "  2. Check application metrics and monitoring"
echo "  3. Verify user-facing functionality"
echo "  4. Notify team of successful deployment"
echo ""

# Optional: Send deployment notification
if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
    log_info "Sending deployment notification to Slack..."
    curl -X POST "$SLACK_WEBHOOK_URL" \
        -H 'Content-Type: application/json' \
        -d "{\"text\":\"CivicQ $ENVIRONMENT deployment completed successfully at $(date)\"}" || log_warning "Failed to send Slack notification"
fi

exit 0
