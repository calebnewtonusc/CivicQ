# CivicQ Database Guide

Complete guide to the CivicQ database architecture, management, and operations.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Database Management](#database-management)
- [Performance Optimization](#performance-optimization)
- [Backup and Recovery](#backup-and-recovery)
- [Monitoring](#monitoring)
- [Common Operations](#common-operations)
- [Troubleshooting](#troubleshooting)

## Overview

CivicQ uses PostgreSQL as its primary database with the following extensions:

- **pgvector** - Vector similarity search for question clustering
- **pg_stat_statements** - Query performance tracking (optional)
- **pg_trgm** - Fuzzy text search (optional)

### Database Statistics

To view current database size and statistics:

```bash
python database/scripts/analyze.py
```

## Architecture

### Connection Pooling

CivicQ uses SQLAlchemy connection pooling with the following configuration:

```python
pool_size=10           # Base pool size
max_overflow=20        # Additional connections when needed
pool_pre_ping=True     # Test connections before use
pool_recycle=3600      # Recycle connections after 1 hour
```

**Monitoring Pool Health:**

```python
from database.monitoring import DatabaseMonitor

monitor = DatabaseMonitor()
pool_stats = monitor.check_connection_pool()
print(pool_stats)
```

### Schema Organization

The database schema is organized into logical domains:

- **User Management** - users, verification_records
- **City Multi-tenancy** - cities, city_staff, city_invitations
- **Electoral Data** - ballots, contests, candidates, measures
- **Questions & Voting** - questions, question_versions, votes
- **Video Answers** - video_answers, rebuttals, claims, videos
- **Moderation** - reports, moderation_actions, audit_logs
- **Social Features** - follows

## Database Management

### Migrations

CivicQ uses Alembic for database migrations.

**Run all pending migrations:**

```bash
python database/migration_runner.py migrate
```

**Create a new migration:**

```bash
alembic revision -m "description of changes"
```

**Rollback last migration:**

```bash
alembic downgrade -1
```

**View migration history:**

```bash
alembic history
```

### Seeding Data

#### Development Environment

Seed with realistic development data:

```bash
python database/seeds/seed_dev.py
```

This creates:
- 3 cities (San Francisco, Oakland, Berkeley)
- 30+ users (admin, voters, candidates, city staff)
- Sample ballots, contests, questions, and votes

**Test Credentials:**
- Admin: `admin@civicq.com` / `admin123`
- Voter: `voter1@example.com` / `password123`
- Candidate: `candidate1@example.com` / `password123`
- City Staff: `clerk@san-francisco.gov` / `password123`

#### Production Environment

Never use seed scripts in production. Instead, use proper data import tools.

## Performance Optimization

### Index Strategy

CivicQ implements a comprehensive indexing strategy:

#### B-tree Indexes

Standard indexes on:
- Primary keys (automatic)
- Foreign keys
- Frequently queried columns (email, city_id, etc.)

#### Composite Indexes

Multi-column indexes for common query patterns:

```sql
-- City + role queries
CREATE INDEX idx_users_city_role ON users(city_id, role);

-- Contest + status queries
CREATE INDEX idx_questions_contest_status ON questions(contest_id, status);

-- Ballot + election date queries
CREATE INDEX idx_ballots_city_election ON ballots(city_id, election_date);
```

#### Partial Indexes

Indexes on filtered subsets:

```sql
-- Active users only
CREATE INDEX idx_users_active ON users(id) WHERE is_active = true;

-- Published ballots only
CREATE INDEX idx_ballots_published ON ballots(city_id, election_date)
WHERE is_published = true;

-- Approved questions only
CREATE INDEX idx_questions_contest_rank ON questions(contest_id, rank_score)
WHERE status = 'approved';
```

#### GIN Indexes

For array and JSON columns:

```sql
-- Issue tags array
CREATE INDEX idx_questions_issue_tags ON questions USING gin(issue_tags);

-- Event data JSON
CREATE INDEX idx_audit_logs_event_data ON audit_logs USING gin(event_data);
```

#### Full-Text Search Indexes

For text search:

```sql
-- Question text search
CREATE INDEX idx_questions_text_search ON questions
USING gin(to_tsvector('english', question_text));

-- Transcript search
CREATE INDEX idx_video_answers_transcript_search ON video_answers
USING gin(to_tsvector('english', transcript_text))
WHERE transcript_text IS NOT NULL;
```

### Query Optimization

#### Identify Slow Queries

```bash
python database/scripts/analyze.py
```

Or manually check:

```python
from database.utils import get_slow_queries

slow_queries = get_slow_queries(min_duration_ms=1000)
for query in slow_queries:
    print(f"{query['mean_exec_time']:.2f}ms: {query['query'][:100]}")
```

#### Check Index Usage

```bash
python database/scripts/vacuum.py --stats
```

Or programmatically:

```python
from database.utils import get_index_usage, get_unused_indexes

# See which indexes are being used
usage = get_index_usage()

# Find unused indexes
unused = get_unused_indexes()
```

#### Enable Query Result Caching

Use application-level caching for expensive queries:

```python
from functools import lru_cache
from datetime import timedelta

@lru_cache(maxsize=100)
def get_popular_questions(contest_id: int):
    # Expensive query
    pass
```

### Connection Pool Tuning

Monitor pool utilization:

```python
from database.monitoring import DatabaseMonitor

monitor = DatabaseMonitor()
stats = monitor.check_connection_pool()

if stats['utilization_percent'] > 80:
    print("Consider increasing pool_size")
```

Adjust in `app/models/base.py`:

```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,      # Increase if needed
    max_overflow=40,   # Increase if needed
)
```

## Backup and Recovery

### Creating Backups

**Full database backup:**

```bash
python database/scripts/backup.py
```

**Compressed backup with custom name:**

```bash
python database/scripts/backup.py --name production_backup_20260214
```

**Schema only (no data):**

```bash
python database/scripts/backup.py --schema-only
```

**Specific tables:**

```bash
python database/scripts/backup.py --tables users questions votes
```

**List existing backups:**

```bash
python database/scripts/backup.py --list
```

**Cleanup old backups:**

```bash
python database/scripts/backup.py --cleanup 10  # Keep only 10 most recent
```

### Restoring Backups

**Restore from backup:**

```bash
python database/scripts/restore.py backups/civicq_backup_20260214.sql.gz
```

**Restore with clean (drops existing data):**

```bash
python database/scripts/restore.py --clean backups/backup.sql.gz
```

**List backup contents:**

```bash
python database/scripts/restore.py --list-contents backups/backup.sql.gz
```

**Verify backup integrity:**

```bash
python database/scripts/restore.py --verify backups/backup.sql.gz
```

### Automated Backups

Set up cron job for daily backups:

```bash
# Daily backup at 2 AM
0 2 * * * cd /path/to/civicq/backend && python database/scripts/backup.py --cleanup 30
```

## Monitoring

### Health Checks

**Quick health check:**

```python
from database.utils import health_check

status = health_check()
print(status)
```

**Comprehensive monitoring:**

```python
from database.monitoring import DatabaseMonitor

monitor = DatabaseMonitor()
health = monitor.run_health_check()

# Check for critical alerts
critical_alerts = [a for a in health['alerts'] if a['level'] == 'critical']
if critical_alerts:
    print("CRITICAL ISSUES DETECTED!")
    for alert in critical_alerts:
        print(f"  {alert['category']}: {alert['message']}")
```

### Performance Metrics

**Cache hit ratio:**

```python
from database.utils import get_cache_hit_ratio

stats = get_cache_hit_ratio()
print(f"Cache hit ratio: {stats['cache_hit_ratio']:.2f}%")
```

**Connection statistics:**

```python
from database.utils import get_active_connections

connections = get_active_connections()
print(f"Active connections: {len(connections)}")
```

**Table sizes:**

```python
from database.utils import get_table_stats

stats = get_table_stats('questions')
print(f"Questions table: {stats['size']} ({stats['row_count']} rows)")
```

### Alerting

Monitor for issues:

```python
from database.monitoring import DatabaseMonitor, AlertLevel

monitor = DatabaseMonitor()
health = monitor.run_health_check()

# Check for critical issues
if health['status'] == 'degraded':
    # Send alert to ops team
    send_alert(health['alerts'])
```

## Common Operations

### Vacuum and Analyze

**Vacuum entire database:**

```bash
python database/scripts/vacuum.py
```

**Vacuum specific table:**

```bash
python database/scripts/vacuum.py --table questions
```

**Full vacuum (reclaims more space but locks table):**

```bash
python database/scripts/vacuum.py --table questions --full
```

**Show tables needing vacuum:**

```bash
python database/scripts/vacuum.py --candidates --threshold 20
```

**Auto-vacuum based on threshold:**

```bash
python database/scripts/vacuum.py --auto-vacuum --threshold 20
```

**Analyze only (update statistics):**

```bash
python database/scripts/vacuum.py --table questions --analyze-only
```

### Reindexing

**Rebuild all indexes:**

```bash
REINDEX DATABASE civicq;
```

**Rebuild specific index:**

```bash
REINDEX INDEX idx_questions_contest_status;
```

**Rebuild table indexes:**

```bash
REINDEX TABLE questions;
```

### Database Analysis

**Full analysis with recommendations:**

```bash
python database/scripts/analyze.py
```

**Save results to file:**

```bash
python database/scripts/analyze.py --output analysis_results.json
```

**JSON output only:**

```bash
python database/scripts/analyze.py --json-only
```

## Troubleshooting

### Slow Queries

**Identify slow queries:**

```bash
python database/scripts/analyze.py
```

Look for queries in the "Query Performance" section.

**Enable query logging:**

In PostgreSQL config:

```
log_min_duration_statement = 1000  # Log queries > 1 second
```

**Use EXPLAIN ANALYZE:**

```sql
EXPLAIN ANALYZE
SELECT * FROM questions
WHERE contest_id = 123
AND status = 'approved'
ORDER BY rank_score DESC;
```

### Connection Pool Exhausted

**Symptoms:**
- "QueuePool limit of size X overflow Y reached"
- Slow response times

**Solutions:**

1. Check for connection leaks:
```python
from database.monitoring import DatabaseMonitor

monitor = DatabaseMonitor()
stats = monitor.get_connection_stats()
print(stats)  # Look for idle_in_transaction
```

2. Increase pool size:
```python
# In app/models/base.py
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=40,
)
```

3. Find long-running connections:
```python
from database.utils import get_active_connections

connections = get_active_connections()
for conn in connections:
    if conn['query_start']:
        print(f"Long query: {conn['query'][:100]}")
```

### Lock Contention

**Identify blocking queries:**

```python
from database.utils import get_blocking_queries

blocking = get_blocking_queries()
for block in blocking:
    print(f"PID {block['blocking_pid']} blocking {block['blocked_pid']}")
    print(f"Blocking query: {block['blocking_statement'][:100]}")
```

**Kill blocking query:**

```sql
SELECT pg_terminate_backend(pid);
```

### High Disk Usage

**Check table sizes:**

```python
from database.utils import get_table_names, get_table_stats

for table in get_table_names():
    stats = get_table_stats(table)
    print(f"{table}: {stats['size']}")
```

**Check for bloat:**

```bash
python database/scripts/vacuum.py --candidates
```

**Vacuum to reclaim space:**

```bash
python database/scripts/vacuum.py --auto-vacuum
```

### Cache Hit Ratio Too Low

**Check current ratio:**

```python
from database.utils import get_cache_hit_ratio

stats = get_cache_hit_ratio()
print(f"Cache hit ratio: {stats['cache_hit_ratio']:.2f}%")
```

**If < 90%, increase shared_buffers:**

In PostgreSQL config:

```
shared_buffers = 4GB  # Increase based on available RAM
```

Restart PostgreSQL after changing config.

## Best Practices

### Development

1. Always use migrations for schema changes
2. Test migrations on development data before production
3. Use seed data for consistent development environment
4. Run `analyze.py` before committing major changes

### Production

1. Take backups before any schema changes
2. Monitor database health daily
3. Set up automated backups (daily minimum)
4. Review slow query log weekly
5. Vacuum and analyze regularly (or enable autovacuum)
6. Monitor disk space and plan for growth

### Security

1. Use read-only database user for analytics
2. Never expose database credentials in code
3. Use environment variables for connection strings
4. Enable SSL for database connections in production
5. Regularly review and rotate database passwords
6. Encrypt backups before storing off-site

## Additional Resources

- [Schema Reference](SCHEMA_REFERENCE.md) - Complete schema documentation
- [Optimization Guide](OPTIMIZATION_GUIDE.md) - Performance tuning guide
- [Backup Recovery](BACKUP_RECOVERY.md) - Detailed backup procedures
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
