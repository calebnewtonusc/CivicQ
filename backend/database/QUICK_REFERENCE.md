# CivicQ Database Quick Reference

Fast reference for common database operations. For detailed documentation, see [DATABASE_GUIDE.md](DATABASE_GUIDE.md).

## Emergency Commands

```bash
# Database is slow
make analyze                    # Identify issues
make vacuum-auto               # Clean up bloat
make monitor-slow-queries      # Find slow queries

# Database is down
make health                    # Check health
make monitor-connections       # Check connections
make monitor-locks            # Check for locks

# Need to restore
make backup-list              # List backups
make restore FILE=backup.sql  # Restore backup

# Running out of space
make db-size                  # Check database size
make monitor-bloat           # Check table bloat
make vacuum-full             # Reclaim space (locks tables!)
```

## Daily Commands

```bash
# Morning health check
make health
make monitor-cache

# Create backup
make backup

# Check for issues
make analyze
```

## Common Operations

### Migrations

```bash
make migrate                           # Run migrations
make migrate-create MSG="description"  # Create migration
make rollback                         # Rollback last
```

### Backups

```bash
make backup                 # Create backup
make backup-list           # List backups
make restore FILE=file.sql # Restore
make backup-cleanup        # Remove old backups
```

### Maintenance

```bash
make vacuum              # Vacuum database
make vacuum-auto         # Auto-vacuum bloated tables
make vacuum-table TABLE=questions  # Vacuum specific table
```

### Monitoring

```bash
make health                  # Quick health check
make analyze                 # Full analysis
make monitor-cache          # Cache hit ratio
make monitor-connections    # Active connections
make monitor-slow-queries   # Slow queries
make monitor-bloat          # Table bloat
```

### Development

```bash
make seed-dev              # Seed development data
make dev-reset            # Reset database (WARNING: deletes all data)
make shell                # Open database shell
```

## Python Quick Reference

### Health Check

```python
from database.utils import health_check

status = health_check()
print(f"Status: {status['status']}")
print(f"Cache hit ratio: {status['cache_hit_ratio']}%")
```

### Create Backup

```python
from database.scripts.backup import DatabaseBackup

backup = DatabaseBackup()
path = backup.create_backup()
print(f"Backup created: {path}")
```

### Database Monitoring

```python
from database.monitoring import DatabaseMonitor

monitor = DatabaseMonitor()
health = monitor.run_health_check()

# Check for critical issues
critical = [a for a in health['alerts'] if a['level'] == 'critical']
if critical:
    print("CRITICAL ISSUES:")
    for alert in critical:
        print(f"  {alert['message']}")
```

### Query Performance

```python
from database.utils import get_slow_queries

slow = get_slow_queries(min_duration_ms=1000)
for query in slow[:10]:
    print(f"{query['mean_exec_time']:.2f}ms: {query['query'][:100]}")
```

### Connection Management

```python
from database.utils import get_db_session

# Use context manager
with get_db_session() as db:
    users = db.query(User).all()
    # Connection automatically returned to pool
```

## Performance Checklist

- [ ] Cache hit ratio > 95%
- [ ] Connection pool utilization < 80%
- [ ] No slow queries > 1 second
- [ ] Table bloat < 20%
- [ ] No blocking queries
- [ ] All foreign keys indexed
- [ ] Regular backups enabled
- [ ] Vacuum running regularly

## Common Issues

### Slow Queries

```bash
# 1. Identify slow queries
make monitor-slow-queries

# 2. Check indexes
make indexes-usage
make indexes-missing

# 3. Run analysis
make analyze
```

### Connection Pool Exhausted

```bash
# 1. Check connections
make monitor-connections

# 2. Look for locks
make monitor-locks

# 3. Check health
make health
```

### Low Cache Hit Ratio

```bash
# 1. Check current ratio
make monitor-cache

# 2. Increase shared_buffers in postgresql.conf
# 3. Restart PostgreSQL
```

### Table Bloat

```bash
# 1. Check bloat
make monitor-bloat

# 2. Auto-vacuum
make vacuum-auto

# 3. If severe, full vacuum (locks tables)
make vacuum-full
```

## Database Connection String

```bash
# Development
DATABASE_URL=postgresql://user:password@localhost:5432/civicq

# Production (use environment variable)
DATABASE_URL=${DATABASE_URL}
```

## Important Tables

```
users              - All users (voters, candidates, staff)
cities             - Cities using CivicQ
ballots            - Election ballots
contests           - Races and measures
candidates         - Candidates in races
questions          - Voter questions
votes              - Question votes
video_answers      - Candidate video responses
audit_logs         - Audit trail
```

## Index Naming Convention

```
idx_{table}_{column(s)}           - Regular index
idx_{table}_{column(s)}_{type}    - Specific type (gin, gist, etc.)
```

## Quick SQL Queries

### Get table sizes

```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Check active queries

```sql
SELECT
    pid,
    usename,
    query_start,
    state,
    query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY query_start;
```

### Kill blocking query

```sql
SELECT pg_terminate_backend(pid);
```

### Check cache hit ratio

```sql
SELECT
    sum(heap_blks_hit) / nullif(sum(heap_blks_hit) + sum(heap_blks_read), 0) * 100 AS cache_hit_ratio
FROM pg_statio_user_tables;
```

## Useful Environment Variables

```bash
DATABASE_URL              # Database connection string
DATABASE_ECHO            # Log all SQL queries (development)
PGPASSWORD              # PostgreSQL password (for scripts)
```

## Getting Help

```bash
make help                # Show all commands
python script.py --help  # Script-specific help
```

## Documentation Links

- [DATABASE_GUIDE.md](DATABASE_GUIDE.md) - Complete guide
- [SCHEMA_REFERENCE.md](SCHEMA_REFERENCE.md) - Schema docs
- [OPTIMIZATION_GUIDE.md](OPTIMIZATION_GUIDE.md) - Performance tuning
- [README.md](README.md) - Overview

## Support Contacts

- Database Issues: DBA team
- Performance: Engineering team
- Backups: DevOps team
