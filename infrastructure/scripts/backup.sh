#!/bin/bash

# ============================================================================
# CivicQ - Database Backup Script
# ============================================================================
# This script creates backups of the PostgreSQL database
#
# Usage:
#   ./backup.sh [environment] [backup_name]
#
# Examples:
#   ./backup.sh production
#   ./backup.sh production pre-deployment-2024-02-14
#   ./backup.sh staging
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
BACKUP_NAME="${2:-$(date +%Y%m%d-%H%M%S)}"

# Backup directory
BACKUP_DIR="$PROJECT_ROOT/backups/$ENVIRONMENT"
mkdir -p "$BACKUP_DIR"

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
# Backup Functions
# ============================================================================
backup_database() {
    log_info "Creating database backup..."

    local backup_file="$BACKUP_DIR/db-${BACKUP_NAME}.sql"
    local backup_file_compressed="$backup_file.gz"

    # Parse DATABASE_URL to get connection details
    # Format: postgresql://user:password@host:port/database
    local db_url_pattern="postgresql://([^:]+):([^@]+)@([^:]+):([^/]+)/(.*)"

    if [[ $DATABASE_URL =~ $db_url_pattern ]]; then
        local db_user="${BASH_REMATCH[1]}"
        local db_pass="${BASH_REMATCH[2]}"
        local db_host="${BASH_REMATCH[3]}"
        local db_port="${BASH_REMATCH[4]}"
        local db_name="${BASH_REMATCH[5]}"

        log_info "Database: $db_name@$db_host:$db_port"

        # Export password for pg_dump
        export PGPASSWORD="$db_pass"

        # Create backup
        if pg_dump -h "$db_host" -p "$db_port" -U "$db_user" -d "$db_name" \
            --format=plain \
            --no-owner \
            --no-acl \
            --verbose \
            > "$backup_file" 2>&1; then

            # Compress backup
            log_info "Compressing backup..."
            gzip -f "$backup_file"

            local backup_size=$(du -h "$backup_file_compressed" | cut -f1)
            log_success "Database backup created: $backup_file_compressed ($backup_size)"

            # Unset password
            unset PGPASSWORD

            return 0
        else
            log_error "Database backup failed"
            unset PGPASSWORD
            return 1
        fi
    else
        log_error "Invalid DATABASE_URL format"
        return 1
    fi
}

backup_docker_database() {
    log_info "Creating database backup from Docker container..."

    local backup_file="$BACKUP_DIR/db-${BACKUP_NAME}.sql.gz"
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

    # Create backup
    if docker exec "$db_container" pg_dump -U "${POSTGRES_USER:-civicq}" "${POSTGRES_DB:-civicq}" \
        --format=plain \
        --no-owner \
        --no-acl | gzip > "$backup_file"; then

        local backup_size=$(du -h "$backup_file" | cut -f1)
        log_success "Database backup created: $backup_file ($backup_size)"
        return 0
    else
        log_error "Database backup failed"
        return 1
    fi
}

backup_media_files() {
    log_info "Creating media files backup..."

    local media_backup="$BACKUP_DIR/media-${BACKUP_NAME}.tar.gz"

    # Check if media directory exists
    if [ -d "$PROJECT_ROOT/media" ]; then
        tar -czf "$media_backup" -C "$PROJECT_ROOT" media/
        local backup_size=$(du -h "$media_backup" | cut -f1)
        log_success "Media files backup created: $media_backup ($backup_size)"
    else
        log_warning "Media directory not found, skipping media backup"
    fi
}

cleanup_old_backups() {
    log_info "Cleaning up old backups..."

    # Keep last 30 backups
    local keep_count=30

    # Count current backups
    local current_count=$(find "$BACKUP_DIR" -name "db-*.sql.gz" | wc -l)

    if [ "$current_count" -gt "$keep_count" ]; then
        log_info "Removing old backups (keeping last $keep_count)..."

        # Remove oldest backups
        find "$BACKUP_DIR" -name "db-*.sql.gz" -type f -printf '%T@ %p\n' | \
            sort -n | \
            head -n -"$keep_count" | \
            cut -d' ' -f2- | \
            xargs rm -f

        log_success "Old backups removed"
    else
        log_info "No cleanup needed ($current_count backups)"
    fi
}

upload_to_s3() {
    if [ -z "${BACKUP_S3_BUCKET:-}" ]; then
        log_warning "BACKUP_S3_BUCKET not set, skipping S3 upload"
        return 0
    fi

    log_info "Uploading backup to S3..."

    local backup_file="$BACKUP_DIR/db-${BACKUP_NAME}.sql.gz"
    local s3_path="s3://${BACKUP_S3_BUCKET}/backups/$ENVIRONMENT/$(basename $backup_file)"

    if command -v aws &> /dev/null; then
        if aws s3 cp "$backup_file" "$s3_path" --storage-class STANDARD_IA; then
            log_success "Backup uploaded to S3: $s3_path"

            # Set lifecycle policy to move to Glacier after 30 days
            log_info "S3 lifecycle policies should be configured separately"
        else
            log_error "Failed to upload backup to S3"
            return 1
        fi
    else
        log_warning "AWS CLI not installed, skipping S3 upload"
    fi
}

# ============================================================================
# Main Backup Process
# ============================================================================
main() {
    echo ""
    echo "============================================================================"
    echo "  CivicQ Backup Script"
    echo "============================================================================"
    echo "  Environment: $ENVIRONMENT"
    echo "  Backup Name: $BACKUP_NAME"
    echo "  Backup Directory: $BACKUP_DIR"
    echo "============================================================================"
    echo ""

    # Load environment variables
    load_environment

    # Try Docker backup first, fallback to direct connection
    if ! backup_docker_database; then
        log_warning "Docker backup failed, trying direct connection..."
        if ! backup_database; then
            log_error "Both backup methods failed"
            exit 1
        fi
    fi

    # Backup media files
    backup_media_files

    # Upload to S3 if configured
    upload_to_s3

    # Cleanup old backups
    cleanup_old_backups

    echo ""
    echo "============================================================================"
    log_success "Backup completed successfully!"
    echo "============================================================================"
    echo ""
    echo "Backup location: $BACKUP_DIR"
    echo ""
    echo "To restore this backup, run:"
    echo "  ./infrastructure/scripts/restore.sh $ENVIRONMENT $BACKUP_NAME"
    echo ""
}

# Run main function
main
