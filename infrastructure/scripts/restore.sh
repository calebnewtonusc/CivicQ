#!/bin/bash

# ============================================================================
# CivicQ - Database Restore Script
# ============================================================================
# This script restores a PostgreSQL database from backup
#
# Usage:
#   ./restore.sh [environment] [backup_name]
#
# Examples:
#   ./restore.sh production 20240214-153000
#   ./restore.sh staging pre-deployment-2024-02-14
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
BACKUP_NAME="${2:-}"

# Backup directory
BACKUP_DIR="$PROJECT_ROOT/backups/$ENVIRONMENT"

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
if [ -z "$BACKUP_NAME" ]; then
    log_error "Backup name is required"
    echo ""
    echo "Available backups:"
    ls -1t "$BACKUP_DIR"/db-*.sql.gz 2>/dev/null | head -10 | while read file; do
        basename "$file" | sed 's/^db-/  - /' | sed 's/\.sql\.gz$//'
    done
    echo ""
    echo "Usage: $0 [environment] [backup_name]"
    exit 1
fi

BACKUP_FILE="$BACKUP_DIR/db-${BACKUP_NAME}.sql.gz"

if [ ! -f "$BACKUP_FILE" ]; then
    log_error "Backup file not found: $BACKUP_FILE"
    echo ""
    echo "Available backups:"
    ls -1t "$BACKUP_DIR"/db-*.sql.gz 2>/dev/null | head -10 | while read file; do
        basename "$file" | sed 's/^db-/  - /' | sed 's/\.sql\.gz$//'
    done
    exit 1
fi

# ============================================================================
# Load Environment
# ============================================================================
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
}

# ============================================================================
# Restore Functions
# ============================================================================
restore_database() {
    log_info "Restoring database from backup..."

    # Parse DATABASE_URL
    local db_url_pattern="postgresql://([^:]+):([^@]+)@([^:]+):([^/]+)/(.*)"

    if [[ $DATABASE_URL =~ $db_url_pattern ]]; then
        local db_user="${BASH_REMATCH[1]}"
        local db_pass="${BASH_REMATCH[2]}"
        local db_host="${BASH_REMATCH[3]}"
        local db_port="${BASH_REMATCH[4]}"
        local db_name="${BASH_REMATCH[5]}"

        log_info "Database: $db_name@$db_host:$db_port"

        # Export password
        export PGPASSWORD="$db_pass"

        # Decompress and restore
        log_info "Decompressing backup..."
        gunzip -c "$BACKUP_FILE" | psql -h "$db_host" -p "$db_port" -U "$db_user" -d "$db_name"

        log_success "Database restored successfully"

        # Unset password
        unset PGPASSWORD

        return 0
    else
        log_error "Invalid DATABASE_URL format"
        return 1
    fi
}

restore_docker_database() {
    log_info "Restoring database to Docker container..."

    local compose_file="docker-compose.production.yml"

    if [ "$ENVIRONMENT" = "staging" ]; then
        compose_file="docker-compose.staging.yml"
    elif [ "$ENVIRONMENT" = "development" ]; then
        compose_file="docker-compose.yml"
    fi

    cd "$PROJECT_ROOT"

    # Get database container name
    local db_container=$(docker-compose -f "$compose_file" ps -q postgres 2>/dev/null || docker-compose -f "$compose_file" ps -q db 2>/dev/null)

    if [ -z "$db_container" ]; then
        log_error "Database container not found"
        return 1
    fi

    # Restore
    log_info "Restoring backup..."
    gunzip -c "$BACKUP_FILE" | docker exec -i "$db_container" psql -U "${POSTGRES_USER:-civicq}" -d "${POSTGRES_DB:-civicq}"

    log_success "Database restored successfully"
    return 0
}

restore_media_files() {
    local media_backup="$BACKUP_DIR/media-${BACKUP_NAME}.tar.gz"

    if [ ! -f "$media_backup" ]; then
        log_warning "Media backup not found: $media_backup"
        return 0
    fi

    log_info "Restoring media files..."

    # Extract media files
    tar -xzf "$media_backup" -C "$PROJECT_ROOT"

    log_success "Media files restored"
}

# ============================================================================
# Main Restore Process
# ============================================================================
main() {
    echo ""
    echo "============================================================================"
    echo "  CivicQ Restore Script"
    echo "============================================================================"
    echo "  Environment: $ENVIRONMENT"
    echo "  Backup: $BACKUP_NAME"
    echo "  Backup File: $BACKUP_FILE"
    echo "============================================================================"
    echo ""

    # Warning
    log_warning "This will OVERWRITE the current database with the backup"
    log_warning "All current data will be LOST"

    # Confirmation
    read -p "Are you ABSOLUTELY SURE you want to continue? Type 'restore' to confirm: " confirm
    if [ "$confirm" != "restore" ]; then
        log_info "Restore cancelled"
        exit 0
    fi

    # Create a safety backup before restoring
    log_info "Creating safety backup of current state..."
    "$SCRIPT_DIR/backup.sh" "$ENVIRONMENT" "pre-restore-$(date +%Y%m%d-%H%M%S)" || log_warning "Safety backup failed"

    # Load environment
    load_environment

    # Stop services to prevent data corruption
    log_info "Stopping services..."
    cd "$PROJECT_ROOT"

    local compose_file="docker-compose.production.yml"
    if [ "$ENVIRONMENT" = "staging" ]; then
        compose_file="docker-compose.staging.yml"
    elif [ "$ENVIRONMENT" = "development" ]; then
        compose_file="docker-compose.yml"
    fi

    docker-compose -f "$compose_file" stop backend celery-worker celery-beat || true

    # Restore database
    if ! restore_docker_database; then
        log_warning "Docker restore failed, trying direct connection..."
        if ! restore_database; then
            log_error "Both restore methods failed"

            # Restart services
            docker-compose -f "$compose_file" start

            exit 1
        fi
    fi

    # Restore media files
    restore_media_files

    # Restart services
    log_info "Restarting services..."
    docker-compose -f "$compose_file" start

    # Wait for services to be ready
    log_info "Waiting for services to start..."
    sleep 10

    # Run health check
    if "$SCRIPT_DIR/health-check.sh" "$ENVIRONMENT"; then
        log_success "Health check passed"
    else
        log_warning "Health check failed - please verify manually"
    fi

    echo ""
    echo "============================================================================"
    log_success "Restore completed!"
    echo "============================================================================"
    echo ""
    echo "Next steps:"
    echo "  1. Verify data integrity"
    echo "  2. Check application logs"
    echo "  3. Test critical functionality"
    echo ""
}

# Run main function
main
