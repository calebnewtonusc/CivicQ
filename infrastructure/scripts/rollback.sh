#!/bin/bash

# ============================================================================
# CivicQ - Rollback Script
# ============================================================================
# This script rolls back to a previous deployment
#
# Usage:
#   ./rollback.sh [environment] [git_commit_or_tag]
#
# Examples:
#   ./rollback.sh production v1.2.3
#   ./rollback.sh staging abc123f
#   ./rollback.sh production HEAD~1
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
TARGET_VERSION="${2:-}"

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

# ============================================================================
# Validation
# ============================================================================
if [ -z "$TARGET_VERSION" ]; then
    log_error "Target version is required"
    echo ""
    echo "Usage: $0 [environment] [git_commit_or_tag]"
    echo ""
    echo "Examples:"
    echo "  $0 production v1.2.3"
    echo "  $0 staging abc123f"
    echo "  $0 production HEAD~1"
    exit 1
fi

# ============================================================================
# Main Rollback Process
# ============================================================================
main() {
    echo ""
    echo "============================================================================"
    echo "  CivicQ Rollback Script"
    echo "============================================================================"
    echo "  Environment: $ENVIRONMENT"
    echo "  Target Version: $TARGET_VERSION"
    echo "============================================================================"
    echo ""

    # Confirmation
    log_warning "This will rollback the deployment to $TARGET_VERSION"
    read -p "Are you sure you want to continue? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        log_info "Rollback cancelled"
        exit 0
    fi

    # Save current state
    log_info "Saving current state..."
    CURRENT_COMMIT=$(git rev-parse HEAD)
    log_info "Current commit: $CURRENT_COMMIT"

    # Create backup of current deployment
    log_info "Creating backup of current deployment..."
    "$SCRIPT_DIR/backup.sh" "$ENVIRONMENT" || log_warning "Backup failed, continuing..."

    # Checkout target version
    log_info "Checking out target version: $TARGET_VERSION"
    cd "$PROJECT_ROOT"

    if ! git checkout "$TARGET_VERSION"; then
        log_error "Failed to checkout $TARGET_VERSION"
        exit 1
    fi

    log_success "Checked out $TARGET_VERSION"

    # Verify we're at the right version
    NEW_COMMIT=$(git rev-parse HEAD)
    log_info "Now at commit: $NEW_COMMIT"

    # Deploy the rolled-back version
    log_info "Deploying rolled-back version..."

    local compose_file="docker-compose.production.yml"
    if [ "$ENVIRONMENT" = "staging" ]; then
        compose_file="docker-compose.staging.yml"
    fi

    # Build images
    log_info "Building images..."
    docker-compose -f "$compose_file" build

    # Check if database rollback is needed
    log_warning "Database migrations are NOT automatically rolled back"
    log_warning "You may need to manually run: alembic downgrade [target_revision]"
    read -p "Do you need to rollback database migrations? (yes/no): " db_rollback

    if [ "$db_rollback" = "yes" ]; then
        read -p "Enter target Alembic revision (or 'skip' to skip): " alembic_revision
        if [ "$alembic_revision" != "skip" ]; then
            log_info "Rolling back database to revision: $alembic_revision"
            docker-compose -f "$compose_file" run --rm backend alembic downgrade "$alembic_revision"
            log_success "Database rolled back"
        fi
    fi

    # Deploy containers
    log_info "Deploying containers..."
    docker-compose -f "$compose_file" down --timeout 30
    docker-compose -f "$compose_file" up -d

    # Health check
    log_info "Running health checks..."
    sleep 10

    if "$SCRIPT_DIR/health-check.sh" "$ENVIRONMENT"; then
        log_success "Health checks passed"
    else
        log_error "Health checks failed!"
        log_error "The rollback may have issues. Check logs immediately."

        read -p "Do you want to rollback to the previous state ($CURRENT_COMMIT)? (yes/no): " revert
        if [ "$revert" = "yes" ]; then
            log_info "Reverting to previous state..."
            git checkout "$CURRENT_COMMIT"
            docker-compose -f "$compose_file" build
            docker-compose -f "$compose_file" down --timeout 30
            docker-compose -f "$compose_file" up -d
            log_warning "Reverted to previous state"
        fi
        exit 1
    fi

    echo ""
    echo "============================================================================"
    log_success "Rollback completed successfully!"
    echo "============================================================================"
    echo ""
    echo "Rollback details:"
    echo "  - Previous version: $CURRENT_COMMIT"
    echo "  - Current version: $NEW_COMMIT ($TARGET_VERSION)"
    echo ""
    echo "Next steps:"
    echo "  1. Monitor logs: docker-compose -f $compose_file logs -f"
    echo "  2. Verify functionality"
    echo "  3. If issues persist, restore from backup: ./infrastructure/scripts/restore.sh"
    echo ""

    # Log rollback event
    log_info "Logging rollback event..."
    echo "$(date -u +"%Y-%m-%d %H:%M:%S UTC") - Rolled back from $CURRENT_COMMIT to $NEW_COMMIT ($TARGET_VERSION) in $ENVIRONMENT" >> "$PROJECT_ROOT/deployment.log"
}

# Run main function
main
