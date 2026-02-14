# CivicQ Database Management Makefile
#
# Common database operations for development and production.
# Run 'make help' to see all available commands.

.PHONY: help migrate rollback seed-dev backup restore vacuum analyze health clean

# Default target
.DEFAULT_GOAL := help

# Python interpreter
PYTHON := python3

# Script paths
SCRIPTS := scripts
SEEDS := seeds
MIGRATIONS := migrations

help: ## Show this help message
	@echo "CivicQ Database Management Commands"
	@echo "===================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Migration Commands
migrate: ## Run all pending migrations
	@echo "Running database migrations..."
	@$(PYTHON) migration_runner.py migrate

migrate-create: ## Create a new migration (usage: make migrate-create MSG="description")
	@echo "Creating new migration: $(MSG)"
	@cd $(MIGRATIONS) && alembic revision -m "$(MSG)"

rollback: ## Rollback last migration
	@echo "Rolling back last migration..."
	@cd $(MIGRATIONS) && alembic downgrade -1

migration-history: ## Show migration history
	@cd $(MIGRATIONS) && alembic history

migration-current: ## Show current migration version
	@cd $(MIGRATIONS) && alembic current

# Seed Data Commands
seed-dev: ## Seed development data
	@echo "Seeding development data..."
	@$(PYTHON) $(SEEDS)/seed_dev.py

# Backup Commands
backup: ## Create database backup
	@echo "Creating database backup..."
	@$(PYTHON) $(SCRIPTS)/backup.py

backup-compressed: ## Create compressed backup
	@echo "Creating compressed backup..."
	@$(PYTHON) $(SCRIPTS)/backup.py --name civicq_backup_$(shell date +%Y%m%d_%H%M%S)

backup-schema: ## Backup schema only (no data)
	@echo "Backing up schema only..."
	@$(PYTHON) $(SCRIPTS)/backup.py --schema-only --name schema_backup_$(shell date +%Y%m%d)

backup-list: ## List all backups
	@$(PYTHON) $(SCRIPTS)/backup.py --list

backup-cleanup: ## Cleanup old backups (keep 10)
	@echo "Cleaning up old backups..."
	@$(PYTHON) $(SCRIPTS)/backup.py --cleanup 10

# Restore Commands
restore: ## Restore from backup (usage: make restore FILE=backup.sql.gz)
	@echo "Restoring from $(FILE)..."
	@$(PYTHON) $(SCRIPTS)/restore.py $(FILE)

restore-verify: ## Verify backup file (usage: make restore-verify FILE=backup.sql.gz)
	@$(PYTHON) $(SCRIPTS)/restore.py --verify $(FILE)

# Maintenance Commands
vacuum: ## Vacuum entire database
	@echo "Vacuuming database..."
	@$(PYTHON) $(SCRIPTS)/vacuum.py

vacuum-full: ## Full vacuum (locks tables, reclaims maximum space)
	@echo "Running VACUUM FULL..."
	@$(PYTHON) $(SCRIPTS)/vacuum.py --full

vacuum-table: ## Vacuum specific table (usage: make vacuum-table TABLE=questions)
	@echo "Vacuuming table $(TABLE)..."
	@$(PYTHON) $(SCRIPTS)/vacuum.py --table $(TABLE)

vacuum-candidates: ## Show tables that need vacuuming
	@$(PYTHON) $(SCRIPTS)/vacuum.py --candidates

vacuum-auto: ## Automatically vacuum tables exceeding threshold
	@echo "Auto-vacuuming tables..."
	@$(PYTHON) $(SCRIPTS)/vacuum.py --auto-vacuum

vacuum-stats: ## Show vacuum statistics
	@$(PYTHON) $(SCRIPTS)/vacuum.py --stats

# Analysis Commands
analyze: ## Run comprehensive database analysis
	@echo "Analyzing database..."
	@$(PYTHON) $(SCRIPTS)/analyze.py

analyze-json: ## Export analysis as JSON (usage: make analyze-json FILE=analysis.json)
	@$(PYTHON) $(SCRIPTS)/analyze.py --output $(FILE)

analyze-report: ## Generate and view analysis report
	@$(PYTHON) $(SCRIPTS)/analyze.py

# Health Check Commands
health: ## Quick database health check
	@$(PYTHON) -c "from database.utils import health_check; import json; print(json.dumps(health_check(), indent=2))"

health-full: ## Comprehensive health check
	@$(PYTHON) -c "from database.monitoring import DatabaseMonitor; monitor = DatabaseMonitor(); import json; print(json.dumps(monitor.run_health_check(), indent=2, default=str))"

# Monitoring Commands
monitor-connections: ## Monitor active connections
	@$(PYTHON) -c "from database.utils import get_active_connections; conns = get_active_connections(); print(f'Active connections: {len(conns)}')"

monitor-slow-queries: ## Show slow queries
	@$(PYTHON) -c "from database.monitoring import DatabaseMonitor; monitor = DatabaseMonitor(); slow = monitor.check_slow_queries(); print(f'Found {len(slow)} slow queries'); [print(f\"{q['duration_ms']:.0f}ms: {q['query_preview']}\") for q in slow[:10]]"

monitor-locks: ## Check for lock contention
	@$(PYTHON) -c "from database.monitoring import DatabaseMonitor; monitor = DatabaseMonitor(); locks = monitor.check_locks(); print(f\"Blocking queries: {locks['total_blocking']}\")"

monitor-cache: ## Check cache hit ratio
	@$(PYTHON) -c "from database.utils import get_cache_hit_ratio; stats = get_cache_hit_ratio(); print(f\"Cache hit ratio: {stats.get('cache_hit_ratio', 0):.2f}%\")"

monitor-bloat: ## Check table bloat
	@$(PYTHON) -c "from database.utils import get_bloat_stats; bloat = get_bloat_stats(); print(f'Found {len(bloat)} bloated tables'); [print(f\"{t['tablename']}: {t['dead_tuple_percent']:.2f}% dead tuples\") for t in bloat[:10]]"

# Index Commands
indexes-unused: ## Find unused indexes
	@$(PYTHON) -c "from database.utils import get_unused_indexes; unused = get_unused_indexes(); print(f'Found {len(unused)} unused indexes'); [print(f\"{idx['tablename']}.{idx['indexname']}: {idx['index_size']}\") for idx in unused[:20]]"

indexes-missing: ## Find tables that might need indexes
	@$(PYTHON) -c "from database.utils import get_missing_indexes; missing = get_missing_indexes(); print(f'Found {len(missing)} tables with high seq scans'); [print(f\"{t['tablename']}: {t['seq_scan']} scans\") for t in missing[:20]]"

indexes-usage: ## Show index usage statistics
	@$(PYTHON) -c "from database.utils import get_index_usage; usage = get_index_usage(); [print(f\"{idx['indexname']}: {idx['idx_scan']} scans\") for idx in usage[:20]]"

# Utility Commands
shell: ## Open database shell
	@echo "Opening database shell..."
	@$(PYTHON) -c "from app.core.config import settings; import os; os.system(f'psql {settings.DATABASE_URL}')"

tables: ## List all tables
	@$(PYTHON) -c "from database.utils import get_table_names; tables = get_table_names(); print('\n'.join(tables))"

table-info: ## Show table information (usage: make table-info TABLE=questions)
	@$(PYTHON) -c "from database.utils import get_table_stats; import json; stats = get_table_stats('$(TABLE)'); print(json.dumps(stats, indent=2, default=str))"

db-size: ## Show database size
	@$(PYTHON) -c "from database.utils import get_database_size; stats = get_database_size(); print(f\"Database: {stats.get('database_name')}\"); print(f\"Size: {stats.get('size')}\")"

# Clean Commands
clean: ## Clean up temporary files
	@echo "Cleaning up temporary files..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Development Commands
dev-reset: ## Reset development database (WARNING: deletes all data)
	@echo "WARNING: This will delete all data and reseed!"
	@read -p "Are you sure? (yes/no): " confirm && [ "$$confirm" = "yes" ] || exit 1
	@$(MAKE) migrate
	@$(MAKE) seed-dev

# Production Commands
prod-backup: ## Production backup with timestamp and cleanup
	@echo "Creating production backup..."
	@$(PYTHON) $(SCRIPTS)/backup.py --name prod_backup_$(shell date +%Y%m%d_%H%M%S)
	@$(PYTHON) $(SCRIPTS)/backup.py --cleanup 30

prod-maintenance: ## Run production maintenance tasks
	@echo "Running production maintenance..."
	@$(MAKE) vacuum-auto
	@$(MAKE) analyze
	@$(MAKE) backup-cleanup

# Scheduled Tasks
daily: ## Daily maintenance (vacuum, analyze, backup)
	@echo "Running daily maintenance..."
	@$(MAKE) vacuum-auto
	@$(MAKE) analyze-json FILE=daily_analysis_$(shell date +%Y%m%d).json
	@$(MAKE) backup
	@$(MAKE) backup-cleanup

weekly: ## Weekly maintenance (full vacuum, reindex)
	@echo "Running weekly maintenance..."
	@$(MAKE) vacuum-full
	@$(MAKE) analyze
	@$(MAKE) backup-compressed
	@$(MAKE) health-full

# Documentation
docs: ## Show database documentation links
	@echo "CivicQ Database Documentation"
	@echo "============================="
	@echo ""
	@echo "  DATABASE_GUIDE.md       - Complete database guide"
	@echo "  SCHEMA_REFERENCE.md     - Schema reference"
	@echo "  OPTIMIZATION_GUIDE.md   - Performance optimization"
	@echo ""
