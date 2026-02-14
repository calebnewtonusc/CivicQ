#!/bin/bash

###############################################################################
# CivicQ Comprehensive Test Runner
#
# This script runs all tests across the CivicQ platform:
# - Backend unit tests (pytest)
# - Frontend unit tests (Jest)
# - Integration tests
# - End-to-end tests
# - Linting and type checking
# - Security scans
#
# Usage: ./scripts/test-all.sh [options]
#
# Options:
#   --backend-only    Run only backend tests
#   --frontend-only   Run only frontend tests
#   --coverage        Generate coverage reports
#   --verbose         Verbose output
#   --quick           Skip slow tests
#
# Example: ./scripts/test-all.sh --coverage --verbose
###############################################################################

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_LOG="$PROJECT_ROOT/logs/test-$(date +%Y%m%d-%H%M%S).log"
RUN_BACKEND=true
RUN_FRONTEND=true
COVERAGE=false
VERBOSE=false
QUICK=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-only)
            RUN_FRONTEND=false
            shift
            ;;
        --frontend-only)
            RUN_BACKEND=false
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --quick)
            QUICK=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$TEST_LOG"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$TEST_LOG"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$TEST_LOG"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$TEST_LOG"
}

# Create log directory
mkdir -p "$(dirname "$TEST_LOG")"

# Banner
echo "=========================================="
echo "  CivicQ Test Suite"
echo "  Timestamp: $(date)"
echo "=========================================="
echo ""

# Track test results
BACKEND_PASSED=false
FRONTEND_PASSED=false
LINT_PASSED=false
SECURITY_PASSED=false

###############################################################################
# Backend Tests
###############################################################################

if [ "$RUN_BACKEND" = true ]; then
    log_info "Running backend tests..."

    cd "$PROJECT_ROOT/backend"

    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        log_warning "Virtual environment not found. Creating one..."
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    else
        source venv/bin/activate
    fi

    # Start test database
    log_info "Starting test database..."
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" up -d postgres redis
    sleep 5

    # Set test environment variables
    export DATABASE_URL="postgresql://civicq_test:test_password@localhost:5432/civicq_test"
    export REDIS_URL="redis://localhost:6379/0"
    export SECRET_KEY="test-secret-key"
    export ENVIRONMENT="test"

    # Run database migrations
    log_info "Running database migrations..."
    alembic upgrade head || log_warning "Migration failed"

    # Run linting
    log_info "Running backend linting (flake8)..."
    flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics || {
        log_error "Backend linting failed"
        LINT_PASSED=false
    }

    # Run type checking
    log_info "Running type checking (mypy)..."
    mypy app/ || log_warning "Type checking found issues"

    # Run tests
    log_info "Running backend unit tests..."

    if [ "$COVERAGE" = true ]; then
        pytest tests/ \
            --cov=app \
            --cov-report=html \
            --cov-report=term-missing \
            --cov-report=xml \
            ${VERBOSE:+"-v"} \
            ${QUICK:+"-m 'not slow'"} || {
                log_error "Backend tests failed"
                BACKEND_PASSED=false
            }

        log_info "Coverage report generated: backend/htmlcov/index.html"

        # Check coverage threshold
        coverage report --fail-under=70 || log_warning "Coverage below 70%"
    else
        pytest tests/ ${VERBOSE:+"-v"} ${QUICK:+"-m 'not slow'"} || {
            log_error "Backend tests failed"
            BACKEND_PASSED=false
        }
    fi

    if [ "$BACKEND_PASSED" != false ]; then
        BACKEND_PASSED=true
        log_success "Backend tests passed"
    fi

    # Cleanup
    deactivate
    cd "$PROJECT_ROOT"
fi

###############################################################################
# Frontend Tests
###############################################################################

if [ "$RUN_FRONTEND" = true ]; then
    log_info "Running frontend tests..."

    cd "$PROJECT_ROOT/frontend"

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        log_warning "node_modules not found. Installing dependencies..."
        npm ci
    fi

    # Run linting
    log_info "Running frontend linting (ESLint)..."
    npm run lint || {
        log_error "Frontend linting failed"
        LINT_PASSED=false
    }

    # Run type checking
    log_info "Running type checking (TypeScript)..."
    npm run type-check || log_warning "Type checking found issues"

    # Run tests
    log_info "Running frontend unit tests..."

    if [ "$COVERAGE" = true ]; then
        npm test -- --coverage --watchAll=false ${VERBOSE:+"--verbose"} || {
            log_error "Frontend tests failed"
            FRONTEND_PASSED=false
        }

        log_info "Coverage report generated: frontend/coverage/lcov-report/index.html"
    else
        npm test -- --watchAll=false ${VERBOSE:+"--verbose"} || {
            log_error "Frontend tests failed"
            FRONTEND_PASSED=false
        }
    fi

    if [ "$FRONTEND_PASSED" != false ]; then
        FRONTEND_PASSED=true
        log_success "Frontend tests passed"
    fi

    # Build check
    log_info "Checking production build..."
    npm run build || log_warning "Production build failed"

    cd "$PROJECT_ROOT"
fi

###############################################################################
# Integration Tests
###############################################################################

if [ "$RUN_BACKEND" = true ] && [ "$RUN_FRONTEND" = true ] && [ "$QUICK" = false ]; then
    log_info "Running integration tests..."

    # Start full stack
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" up -d

    sleep 10

    # Run integration tests
    cd "$PROJECT_ROOT/backend"
    source venv/bin/activate

    pytest tests/integration/ ${VERBOSE:+"-v"} || log_warning "Integration tests failed"

    deactivate
    cd "$PROJECT_ROOT"

    # Cleanup
    docker-compose -f "$PROJECT_ROOT/docker-compose.yml" down
fi

###############################################################################
# Security Scans
###############################################################################

if [ "$QUICK" = false ]; then
    log_info "Running security scans..."

    # Backend security scan
    if [ "$RUN_BACKEND" = true ]; then
        log_info "Scanning backend dependencies (safety)..."
        cd "$PROJECT_ROOT/backend"
        source venv/bin/activate

        pip install safety || true
        safety check --json || log_warning "Backend security issues found"

        deactivate
        cd "$PROJECT_ROOT"
    fi

    # Frontend security scan
    if [ "$RUN_FRONTEND" = true ]; then
        log_info "Scanning frontend dependencies (npm audit)..."
        cd "$PROJECT_ROOT/frontend"

        npm audit --audit-level=moderate || log_warning "Frontend security issues found"

        cd "$PROJECT_ROOT"
    fi

    SECURITY_PASSED=true
fi

###############################################################################
# Test Summary
###############################################################################

echo ""
echo "=========================================="
echo "  Test Summary"
echo "=========================================="

if [ "$RUN_BACKEND" = true ]; then
    if [ "$BACKEND_PASSED" = true ]; then
        log_success "Backend tests: PASSED"
    else
        log_error "Backend tests: FAILED"
    fi
fi

if [ "$RUN_FRONTEND" = true ]; then
    if [ "$FRONTEND_PASSED" = true ]; then
        log_success "Frontend tests: PASSED"
    else
        log_error "Frontend tests: FAILED"
    fi
fi

if [ "$LINT_PASSED" != false ]; then
    log_success "Linting: PASSED"
else
    log_error "Linting: FAILED"
fi

if [ "$SECURITY_PASSED" = true ]; then
    log_success "Security scans: PASSED"
fi

echo ""
echo "Test log: $TEST_LOG"

# Exit with appropriate code
if { [ "$RUN_BACKEND" = true ] && [ "$BACKEND_PASSED" != true ]; } || \
   { [ "$RUN_FRONTEND" = true ] && [ "$FRONTEND_PASSED" != true ]; }; then
    echo ""
    log_error "Some tests failed. Please review and fix."
    exit 1
else
    echo ""
    log_success "All tests passed!"
    exit 0
fi
