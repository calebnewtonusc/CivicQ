# CivicQ Database Management

Complete database utilities, optimization tools, and management scripts for CivicQ.

## Quick Start

```bash
# Run database health check
make health

# Run comprehensive analysis
make analyze

# Create backup
make backup

# Seed development data
make seed-dev

# Run migrations
make migrate
```

## Directory Structure

```
database/
├── migrations/          # Alembic database migrations
│   └── versions/       # Migration version files
├── scripts/            # Database management scripts
│   ├── backup.py      # Database backup utility
│   ├── restore.py     # Database restore utility
│   ├── vacuum.py      # Vacuum and maintenance
│   └── analyze.py     # Database analysis tool
├── seeds/              # Seed data scripts
│   └── seed_dev.py    # Development seed data
├── sql/                # SQL queries and views
├── utils.py            # Database utility functions
├── monitoring.py       # Database monitoring
├── Makefile            # Common database operations
└── docs/               # Documentation
    ├── DATABASE_GUIDE.md
    ├── SCHEMA_REFERENCE.md
    └── OPTIMIZATION_GUIDE.md
```

## Documentation

- **[DATABASE_GUIDE.md](DATABASE_GUIDE.md)** - Complete guide to database management, backup/recovery, and common operations
- **[SCHEMA_REFERENCE.md](SCHEMA_REFERENCE.md)** - Complete schema documentation with all tables, columns, and relationships
- **[OPTIMIZATION_GUIDE.md](OPTIMIZATION_GUIDE.md)** - Performance optimization guide with query patterns and best practices

## Common Tasks

### Database Migrations

```bash
# Run all pending migrations
make migrate

# Create new migration
make migrate-create MSG="add user settings"

# Rollback last migration
make rollback

# View migration history
make migration-history
```

### Backup and Restore

```bash
# Create backup
make backup

# Create compressed backup with timestamp
make backup-compressed

# List all backups
make backup-list

# Restore from backup
make restore FILE=backups/backup.sql.gz

# Verify backup
make restore-verify FILE=backups/backup.sql.gz

# Cleanup old backups (keep 10 most recent)
make backup-cleanup
```

### Database Maintenance

```bash
# Vacuum entire database
make vacuum

# Vacuum specific table
make vacuum-table TABLE=questions

# Show tables needing vacuum
make vacuum-candidates

# Auto-vacuum tables exceeding threshold
make vacuum-auto

# Full vacuum (more aggressive)
make vacuum-full
```

### Database Analysis

```bash
# Run comprehensive analysis
make analyze

# Export analysis to JSON
make analyze-json FILE=analysis.json

# Check specific metrics
make monitor-cache         # Cache hit ratio
make monitor-connections   # Active connections
make monitor-slow-queries  # Slow queries
make monitor-locks        # Lock contention
make monitor-bloat        # Table bloat
```

### Index Management

```bash
# Find unused indexes
make indexes-unused

# Find tables that might need indexes
make indexes-missing

# Show index usage statistics
make indexes-usage
```

### Health Checks

```bash
# Quick health check
make health

# Comprehensive health check
make health-full

# Database size
make db-size

# List all tables
make tables

# Table information
make table-info TABLE=questions
```

## Scheduled Maintenance

### Daily Tasks

```bash
make daily
```

This runs:
- Auto-vacuum for bloated tables
- Database analysis
- Automated backup
- Backup cleanup

Set up in cron:

```bash
# Daily maintenance at 2 AM
0 2 * * * cd /path/to/civicq/backend/database && make daily
```

### Weekly Tasks

```bash
make weekly
```

This runs:
- Full vacuum
- Comprehensive analysis
- Compressed backup
- Full health check

Set up in cron:

```bash
# Weekly maintenance on Sunday at 3 AM
0 3 * * 0 cd /path/to/civicq/backend/database && make weekly
```

## Development Workflow

### Setting Up Development Environment

```bash
# 1. Run migrations
make migrate

# 2. Seed development data
make seed-dev

# 3. Verify everything works
make health
```

### Resetting Development Database

```bash
# WARNING: This deletes all data
make dev-reset
```

### Testing Backups

```bash
# Create backup
make backup

# Verify backup
make backup-list

# Test restore (in test environment)
make restore FILE=backups/civicq_backup_20260214.sql.gz
```

## Production Workflow

### Pre-Deployment Checklist

1. Create backup: `make prod-backup`
2. Test migrations on staging
3. Review analysis: `make analyze`
4. Check health: `make health-full`
5. Verify connection pool: `make monitor-connections`

### Post-Deployment Tasks

1. Run migrations: `make migrate`
2. Verify health: `make health`
3. Check for slow queries: `make monitor-slow-queries`
4. Monitor for 24 hours

### Regular Maintenance

```bash
# Daily
make prod-backup         # Create backup
make vacuum-auto         # Auto-vacuum
make analyze            # Analysis

# Weekly
make prod-maintenance   # Full maintenance
```

## Monitoring and Alerting

### Key Metrics to Monitor

1. **Cache Hit Ratio** - Should be > 95%
   ```bash
   make monitor-cache
   ```

2. **Connection Pool Utilization** - Should be < 80%
   ```bash
   make monitor-connections
   ```

3. **Slow Queries** - Track and optimize
   ```bash
   make monitor-slow-queries
   ```

4. **Table Bloat** - Keep dead tuples < 20%
   ```bash
   make monitor-bloat
   ```

5. **Lock Contention** - Should be minimal
   ```bash
   make monitor-locks
   ```

### Setting Up Alerts

```python
from database.monitoring import DatabaseMonitor, AlertLevel

def check_database():
    monitor = DatabaseMonitor()
    health = monitor.run_health_check()

    # Alert on critical issues
    critical = [a for a in health['alerts'] if a['level'] == 'critical']
    if critical:
        send_alert(critical)

    return health['status']
```

## Troubleshooting

### Slow Queries

```bash
# Identify slow queries
make analyze

# Check index usage
make indexes-usage

# Look for missing indexes
make indexes-missing
```

### High Disk Usage

```bash
# Check database size
make db-size

# Check table sizes
make tables | xargs -I {} make table-info TABLE={}

# Check for bloat
make monitor-bloat

# Vacuum to reclaim space
make vacuum-auto
```

### Connection Pool Exhausted

```bash
# Check active connections
make monitor-connections

# Look for locks
make monitor-locks

# Review health
make health-full
```

### Low Cache Hit Ratio

```bash
# Check current ratio
make monitor-cache

# Increase shared_buffers in postgresql.conf
# Restart PostgreSQL
```

## Database Utilities API

### Python API

```python
# Health check
from database.utils import health_check
status = health_check()

# Create backup
from database.scripts.backup import DatabaseBackup
backup = DatabaseBackup()
backup_path = backup.create_backup()

# Run analysis
from database.scripts.analyze import DatabaseAnalyzer
analyzer = DatabaseAnalyzer()
results = analyzer.analyze_all()

# Monitoring
from database.monitoring import DatabaseMonitor
monitor = DatabaseMonitor()
health = monitor.run_health_check()
```

### Command Line

All scripts support `--help`:

```bash
python database/scripts/backup.py --help
python database/scripts/restore.py --help
python database/scripts/vacuum.py --help
python database/scripts/analyze.py --help
```

## Performance Optimization

See [OPTIMIZATION_GUIDE.md](OPTIMIZATION_GUIDE.md) for detailed performance tuning.

Key optimization areas:

1. **Indexes** - Ensure all foreign keys and common queries are indexed
2. **Query Optimization** - Use eager loading, avoid N+1 queries
3. **Connection Pooling** - Tune pool size and monitor utilization
4. **Caching** - Implement application-level caching for expensive queries
5. **Vacuum** - Regular maintenance to prevent bloat

## Security Best Practices

1. **Never commit database credentials** - Use environment variables
2. **Use read-only user for reporting** - Create separate read-only user
3. **Encrypt backups** - Encrypt before storing off-site
4. **Rotate passwords regularly** - Change database passwords quarterly
5. **Monitor audit logs** - Review security events regularly
6. **Enable SSL connections** - Use encrypted connections in production

## Getting Help

- See documentation in [docs/](docs/)
- Run `make help` for all available commands
- Check [DATABASE_GUIDE.md](DATABASE_GUIDE.md) for detailed operations
- Review [SCHEMA_REFERENCE.md](SCHEMA_REFERENCE.md) for schema details

## Contributing

When adding new database features:

1. Create migration for schema changes
2. Update seed data if needed
3. Add indexes for new foreign keys
4. Update documentation
5. Test backup/restore with new schema
6. Run `make analyze` to check performance impact
