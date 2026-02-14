#!/bin/bash

# ============================================================================
# CivicQ - Production Deployment Script
# ============================================================================
# This script automates the deployment of CivicQ to production
#
# Usage:
#   ./deploy.sh [environment] [options]
#
# Examples:
#   ./deploy.sh production            # Deploy to production
#   ./deploy.sh staging               # Deploy to staging
#   ./deploy.sh production --skip-tests  # Skip tests
#   ./deploy.sh production --no-backup   # Skip database backup
# ============================================================================

set -e  # Exit on error
set -u  # Exit on undefined variable

# ============================================================================
# Configuration
# ============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="${1:-production}"
SKIP_TESTS=false
SKIP_BACKUP=false
SKIP_MIGRATIONS=false
DRY_RUN=false

# ============================================================================
# Helper Functions
# ============================================================================
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_required_tools() {
    local tools=("docker" "docker-compose" "git")

    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "$tool is not installed. Please install it first."
            exit 1
        fi
    done

    log_success "All required tools are installed"
}

load_environment() {
    local env_file="$PROJECT_ROOT/backend/.env.$ENVIRONMENT"

    if [ ! -f "$env_file" ]; then
        log_error "Environment file not found: $env_file"
        exit 1
    fi

    log_info "Loading environment: $ENVIRONMENT"
    set -a
    source "$env_file"
    set +a

    log_success "Environment loaded"
}

validate_environment() {
    log_info "Validating environment configuration..."

    local required_vars=(
        "SECRET_KEY"
        "DATABASE_URL"
        "REDIS_URL"
        "S3_BUCKET"
        "S3_ACCESS_KEY"
        "S3_SECRET_KEY"
    )

    local missing_vars=()

    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            missing_vars+=("$var")
        fi
    done

    if [ ${#missing_vars[@]} -gt 0 ]; then
        log_error "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        exit 1
    fi

    log_success "Environment validation passed"
}

run_tests() {
    if [ "$SKIP_TESTS" = true ]; then
        log_warning "Skipping tests (--skip-tests flag set)"
        return 0
    fi

    log_info "Running tests..."

    # Backend tests
    log_info "Running backend tests..."
    cd "$PROJECT_ROOT/backend"
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" run --rm backend pytest

    # Frontend tests
    log_info "Running frontend tests..."
    cd "$PROJECT_ROOT/frontend"
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" run --rm frontend npm test -- --watchAll=false

    cd "$PROJECT_ROOT"
    log_success "All tests passed"
}

backup_database() {
    if [ "$SKIP_BACKUP" = true ]; then
        log_warning "Skipping database backup (--no-backup flag set)"
        return 0
    fi

    log_info "Creating database backup..."

    local backup_script="$SCRIPT_DIR/backup.sh"
    if [ -f "$backup_script" ]; then
        "$backup_script" "$ENVIRONMENT"
        log_success "Database backup created"
    else
        log_warning "Backup script not found, skipping backup"
    fi
}

build_images() {
    log_info "Building Docker images..."

    local compose_file="docker-compose.production.yml"
    if [ "$ENVIRONMENT" = "staging" ]; then
        compose_file="docker-compose.staging.yml"
    fi

    cd "$PROJECT_ROOT"

    # Build backend
    log_info "Building backend image..."
    docker-compose -f "$compose_file" build backend

    # Build frontend
    log_info "Building frontend image..."
    docker-compose -f "$compose_file" build --build-arg REACT_APP_API_URL="$BACKEND_URL/api" \
        --build-arg REACT_APP_BASE_URL="$FRONTEND_URL" \
        --build-arg REACT_APP_ENV="$ENVIRONMENT" \
        frontend || docker-compose -f "$compose_file" build nginx

    # Build Celery worker
    log_info "Building Celery worker image..."
    docker-compose -f "$compose_file" build celery-worker

    # Build Celery beat
    log_info "Building Celery beat image..."
    docker-compose -f "$compose_file" build celery-beat

    log_success "Docker images built successfully"
}

run_migrations() {
    if [ "$SKIP_MIGRATIONS" = true ]; then
        log_warning "Skipping database migrations (--skip-migrations flag set)"
        return 0
    fi

    log_info "Running database migrations..."

    local compose_file="docker-compose.production.yml"
    if [ "$ENVIRONMENT" = "staging" ]; then
        compose_file="docker-compose.staging.yml"
    fi

    cd "$PROJECT_ROOT"
    docker-compose -f "$compose_file" run --rm backend alembic upgrade head

    log_success "Database migrations completed"
}

deploy_containers() {
    log_info "Deploying containers..."

    local compose_file="docker-compose.production.yml"
    if [ "$ENVIRONMENT" = "staging" ]; then
        compose_file="docker-compose.staging.yml"
    fi

    cd "$PROJECT_ROOT"

    if [ "$DRY_RUN" = true ]; then
        log_info "DRY RUN: Would execute: docker-compose -f $compose_file up -d"
        return 0
    fi

    # Stop old containers gracefully
    log_info "Stopping old containers..."
    docker-compose -f "$compose_file" down --timeout 30

    # Start new containers
    log_info "Starting new containers..."
    docker-compose -f "$compose_file" up -d

    log_success "Containers deployed"
}

health_check() {
    log_info "Running health checks..."

    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        log_info "Health check attempt $attempt/$max_attempts..."

        if curl -f -s -o /dev/null "${BACKEND_URL}/health"; then
            log_success "Backend health check passed"
            break
        fi

        if [ $attempt -eq $max_attempts ]; then
            log_error "Health check failed after $max_attempts attempts"
            return 1
        fi

        sleep 5
        attempt=$((attempt + 1))
    done

    log_success "All health checks passed"
}

cleanup_old_images() {
    log_info "Cleaning up old Docker images..."

    # Remove dangling images
    docker image prune -f

    log_success "Cleanup completed"
}

# ============================================================================
# Parse Arguments
# ============================================================================
shift || true  # Remove first argument (environment)

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --no-backup)
            SKIP_BACKUP=true
            shift
            ;;
        --skip-migrations)
            SKIP_MIGRATIONS=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Usage: $0 [environment] [--skip-tests] [--no-backup] [--skip-migrations] [--dry-run]"
            exit 1
            ;;
    esac
done

# ============================================================================
# Main Deployment Flow
# ============================================================================
main() {
    echo ""
    echo "============================================================================"
    echo "  CivicQ Deployment Script"
    echo "============================================================================"
    echo "  Environment: $ENVIRONMENT"
    echo "  Skip Tests: $SKIP_TESTS"
    echo "  Skip Backup: $SKIP_BACKUP"
    echo "  Skip Migrations: $SKIP_MIGRATIONS"
    echo "  Dry Run: $DRY_RUN"
    echo "============================================================================"
    echo ""

    # Confirmation for production
    if [ "$ENVIRONMENT" = "production" ] && [ "$DRY_RUN" = false ]; then
        read -p "Are you sure you want to deploy to PRODUCTION? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            log_warning "Deployment cancelled"
            exit 0
        fi
    fi

    # Execute deployment steps
    check_required_tools
    load_environment
    validate_environment
    run_tests
    backup_database
    build_images
    run_migrations
    deploy_containers
    health_check
    cleanup_old_images

    echo ""
    echo "============================================================================"
    log_success "Deployment completed successfully!"
    echo "============================================================================"
    echo ""
    echo "Next steps:"
    echo "  1. Monitor logs: docker-compose -f docker-compose.$ENVIRONMENT.yml logs -f"
    echo "  2. Check status: docker-compose -f docker-compose.$ENVIRONMENT.yml ps"
    echo "  3. Run health check: ./infrastructure/scripts/health-check.sh"
    echo ""

    if [ "$ENVIRONMENT" = "production" ]; then
        echo "  4. Monitor application: $FRONTEND_URL"
        echo "  5. Check API: $BACKEND_URL/docs"
    fi

    echo ""
}

# Run main function
main
