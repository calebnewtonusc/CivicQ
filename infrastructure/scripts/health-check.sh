#!/bin/bash

# ============================================================================
# CivicQ - Health Check Script
# ============================================================================
# This script performs comprehensive health checks on all services
#
# Usage:
#   ./health-check.sh [environment]
#
# Examples:
#   ./health-check.sh production
#   ./health-check.sh staging
#   ./health-check.sh development
# ============================================================================

set -e

# ============================================================================
# Configuration
# ============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Arguments
ENVIRONMENT="${1:-production}"

# Health check results
CHECKS_PASSED=0
CHECKS_FAILED=0

# ============================================================================
# Helper Functions
# ============================================================================
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
}

# ============================================================================
# Load Environment
# ============================================================================
load_environment() {
    local env_file="$PROJECT_ROOT/backend/.env.$ENVIRONMENT"

    if [ ! -f "$env_file" ]; then
        log_warning "Environment file not found: $env_file"
        log_warning "Using default values"
        return 1
    fi

    set -a
    source "$env_file"
    set +a
}

# ============================================================================
# Health Check Functions
# ============================================================================

check_docker_containers() {
    log_info "Checking Docker containers..."

    local compose_file="docker-compose.production.yml"
    if [ "$ENVIRONMENT" = "staging" ]; then
        compose_file="docker-compose.staging.yml"
    elif [ "$ENVIRONMENT" = "development" ]; then
        compose_file="docker-compose.yml"
    fi

    cd "$PROJECT_ROOT"

    # Check if compose file exists
    if [ ! -f "$compose_file" ]; then
        log_error "Docker Compose file not found: $compose_file"
        return 1
    fi

    # Get list of services
    local services=("postgres" "redis" "backend" "celery-worker" "celery-beat")

    for service in "${services[@]}"; do
        if docker-compose -f "$compose_file" ps "$service" | grep -q "Up"; then
            log_success "Container $service is running"
        else
            log_error "Container $service is not running"
        fi
    done
}

check_backend_health() {
    log_info "Checking backend API health..."

    local backend_url="${BACKEND_URL:-http://localhost:8000}"
    local health_endpoint="$backend_url/health"

    if curl -f -s -o /dev/null "$health_endpoint"; then
        log_success "Backend API is healthy"

        # Check response time
        local response_time=$(curl -o /dev/null -s -w '%{time_total}\n' "$health_endpoint")
        if (( $(echo "$response_time < 1.0" | bc -l) )); then
            log_success "Backend response time: ${response_time}s"
        else
            log_warning "Backend response time is slow: ${response_time}s"
        fi
    else
        log_error "Backend API health check failed"
    fi
}

check_database_connection() {
    log_info "Checking database connection..."

    local compose_file="docker-compose.production.yml"
    if [ "$ENVIRONMENT" = "staging" ]; then
        compose_file="docker-compose.staging.yml"
    elif [ "$ENVIRONMENT" = "development" ]; then
        compose_file="docker-compose.yml"
    fi

    cd "$PROJECT_ROOT"

    # Try to connect to database via backend
    if docker-compose -f "$compose_file" exec -T backend python -c "
from sqlalchemy import create_engine
import os
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    result = conn.execute('SELECT 1')
    print('Database connected')
" 2>&1 | grep -q "Database connected"; then
        log_success "Database connection successful"
    else
        log_error "Database connection failed"
    fi
}

check_redis_connection() {
    log_info "Checking Redis connection..."

    local compose_file="docker-compose.production.yml"
    if [ "$ENVIRONMENT" = "staging" ]; then
        compose_file="docker-compose.staging.yml"
    elif [ "$ENVIRONMENT" = "development" ]; then
        compose_file="docker-compose.yml"
    fi

    cd "$PROJECT_ROOT"

    # Try to ping Redis via backend
    if docker-compose -f "$compose_file" exec -T backend python -c "
import redis
import os
from urllib.parse import urlparse

redis_url = os.getenv('REDIS_URL')
parsed = urlparse(redis_url)
password = parsed.password if parsed.password else None

r = redis.Redis(
    host=parsed.hostname,
    port=parsed.port or 6379,
    password=password,
    decode_responses=True
)

if r.ping():
    print('Redis connected')
" 2>&1 | grep -q "Redis connected"; then
        log_success "Redis connection successful"
    else
        log_error "Redis connection failed"
    fi
}

check_celery_worker() {
    log_info "Checking Celery worker..."

    local compose_file="docker-compose.production.yml"
    if [ "$ENVIRONMENT" = "staging" ]; then
        compose_file="docker-compose.staging.yml"
    elif [ "$ENVIRONMENT" = "development" ]; then
        compose_file="docker-compose.yml"
    fi

    cd "$PROJECT_ROOT"

    # Check if worker is processing tasks
    if docker-compose -f "$compose_file" exec -T celery-worker celery -A app.worker inspect active 2>&1 | grep -q "OK"; then
        log_success "Celery worker is running"
    else
        log_error "Celery worker check failed"
    fi
}

check_celery_beat() {
    log_info "Checking Celery beat..."

    local compose_file="docker-compose.production.yml"
    if [ "$ENVIRONMENT" = "staging" ]; then
        compose_file="docker-compose.staging.yml"
    elif [ "$ENVIRONMENT" = "development" ]; then
        compose_file="docker-compose.yml"
    fi

    cd "$PROJECT_ROOT"

    # Check if beat scheduler is running
    if docker-compose -f "$compose_file" logs --tail=20 celery-beat 2>&1 | grep -q "beat: Starting..."; then
        log_success "Celery beat is running"
    else
        log_warning "Celery beat may not be running (check logs)"
    fi
}

check_storage() {
    log_info "Checking storage availability..."

    # Check S3 connection if configured
    if [ -n "${S3_BUCKET:-}" ]; then
        if command -v aws &> /dev/null; then
            if aws s3 ls "s3://$S3_BUCKET" >/dev/null 2>&1; then
                log_success "S3 bucket accessible: $S3_BUCKET"
            else
                log_error "S3 bucket not accessible: $S3_BUCKET"
            fi
        else
            log_warning "AWS CLI not installed, skipping S3 check"
        fi
    else
        log_warning "S3_BUCKET not configured, skipping S3 check"
    fi

    # Check local storage
    local media_dir="$PROJECT_ROOT/media"
    if [ -d "$media_dir" ]; then
        local disk_usage=$(df -h "$media_dir" | tail -1 | awk '{print $5}' | sed 's/%//')
        if [ "$disk_usage" -lt 80 ]; then
            log_success "Disk usage: ${disk_usage}%"
        else
            log_warning "Disk usage is high: ${disk_usage}%"
        fi
    fi
}

check_api_endpoints() {
    log_info "Checking critical API endpoints..."

    local backend_url="${BACKEND_URL:-http://localhost:8000}"

    # Check docs endpoint
    if curl -f -s -o /dev/null "$backend_url/docs"; then
        log_success "API docs accessible"
    else
        log_warning "API docs not accessible"
    fi

    # Check API v1 endpoint
    if curl -f -s -o /dev/null "$backend_url/api/v1"; then
        log_success "API v1 accessible"
    else
        log_error "API v1 not accessible"
    fi
}

check_ssl_certificate() {
    if [ "$ENVIRONMENT" != "production" ]; then
        log_info "Skipping SSL check (not production)"
        return 0
    fi

    log_info "Checking SSL certificate..."

    local domain="${DOMAIN:-}"
    if [ -z "$domain" ]; then
        log_warning "Domain not configured, skipping SSL check"
        return 0
    fi

    # Check SSL certificate expiration
    if command -v openssl &> /dev/null; then
        local cert_expiry=$(echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)

        if [ -n "$cert_expiry" ]; then
            local expiry_timestamp=$(date -d "$cert_expiry" +%s 2>/dev/null || date -j -f "%b %d %H:%M:%S %Y %Z" "$cert_expiry" +%s 2>/dev/null)
            local current_timestamp=$(date +%s)
            local days_until_expiry=$(( (expiry_timestamp - current_timestamp) / 86400 ))

            if [ "$days_until_expiry" -gt 30 ]; then
                log_success "SSL certificate valid for $days_until_expiry days"
            elif [ "$days_until_expiry" -gt 0 ]; then
                log_warning "SSL certificate expires in $days_until_expiry days"
            else
                log_error "SSL certificate has expired"
            fi
        else
            log_warning "Could not check SSL certificate"
        fi
    fi
}

# ============================================================================
# Main Health Check
# ============================================================================
main() {
    echo ""
    echo "============================================================================"
    echo "  CivicQ Health Check"
    echo "============================================================================"
    echo "  Environment: $ENVIRONMENT"
    echo "  Timestamp: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
    echo "============================================================================"
    echo ""

    # Load environment
    load_environment

    # Run all checks
    check_docker_containers
    check_database_connection
    check_redis_connection
    check_backend_health
    check_celery_worker
    check_celery_beat
    check_storage
    check_api_endpoints
    check_ssl_certificate

    # Summary
    echo ""
    echo "============================================================================"
    echo "  Health Check Summary"
    echo "============================================================================"

    local total_checks=$((CHECKS_PASSED + CHECKS_FAILED))

    echo -e "Total Checks: $total_checks"
    echo -e "${GREEN}Passed: $CHECKS_PASSED${NC}"
    echo -e "${RED}Failed: $CHECKS_FAILED${NC}"
    echo ""

    if [ $CHECKS_FAILED -eq 0 ]; then
        echo -e "${GREEN}All health checks passed!${NC}"
        echo "============================================================================"
        exit 0
    else
        echo -e "${RED}Some health checks failed!${NC}"
        echo "============================================================================"
        exit 1
    fi
}

# Run main function
main
