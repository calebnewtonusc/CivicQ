# CivicQ Database Optimization Guide

Comprehensive guide to optimizing database performance for CivicQ.

## Table of Contents

- [Query Optimization](#query-optimization)
- [Index Optimization](#index-optimization)
- [Connection Pool Tuning](#connection-pool-tuning)
- [Cache Optimization](#cache-optimization)
- [Vacuum and Maintenance](#vacuum-and-maintenance)
- [Query Patterns](#query-patterns)
- [Performance Monitoring](#performance-monitoring)

## Query Optimization

### Identifying N+1 Query Problems

N+1 queries occur when you fetch a list of objects and then query for related objects in a loop.

**Bad (N+1):**

```python
# Fetches questions (1 query)
questions = db.query(Question).filter_by(contest_id=123).all()

# Then fetches author for each question (N queries)
for question in questions:
    author = question.author  # Separate query for each!
    print(author.full_name)
```

**Good (Eager Loading):**

```python
from sqlalchemy.orm import joinedload

# Single query with JOIN
questions = (
    db.query(Question)
    .filter_by(contest_id=123)
    .options(joinedload(Question.author))
    .all()
)

for question in questions:
    print(question.author.full_name)  # No additional query!
```

### Using Eager Loading

**Load single relationship:**

```python
from sqlalchemy.orm import joinedload

candidates = (
    db.query(Candidate)
    .options(joinedload(Candidate.user))
    .filter_by(contest_id=contest_id)
    .all()
)
```

**Load multiple relationships:**

```python
from sqlalchemy.orm import joinedload

questions = (
    db.query(Question)
    .options(
        joinedload(Question.author),
        joinedload(Question.votes),
        joinedload(Question.contest)
    )
    .filter_by(contest_id=contest_id)
    .all()
)
```

**Load nested relationships:**

```python
video_answers = (
    db.query(VideoAnswer)
    .options(
        joinedload(VideoAnswer.candidate).joinedload(Candidate.user),
        joinedload(VideoAnswer.question).joinedload(Question.author)
    )
    .all()
)
```

### Pagination

Always paginate large result sets:

```python
from sqlalchemy import desc

def get_questions(contest_id: int, page: int = 1, per_page: int = 20):
    return (
        db.query(Question)
        .filter_by(contest_id=contest_id, status='approved')
        .order_by(desc(Question.rank_score))
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
```

### Counting Efficiently

**Inefficient:**

```python
# Loads all objects into memory
total = len(db.query(Question).filter_by(contest_id=123).all())
```

**Efficient:**

```python
from sqlalchemy import func

# Only counts in database
total = db.query(func.count(Question.id)).filter_by(contest_id=123).scalar()
```

### Aggregation Queries

**Vote counts per question:**

```python
from sqlalchemy import func

vote_counts = (
    db.query(
        Vote.question_id,
        func.count(Vote.id).label('vote_count'),
        func.sum(Vote.value).label('vote_sum')
    )
    .filter(Vote.question_id.in_(question_ids))
    .group_by(Vote.question_id)
    .all()
)
```

**Average rank score by contest:**

```python
avg_scores = (
    db.query(
        Question.contest_id,
        func.avg(Question.rank_score).label('avg_rank')
    )
    .filter(Question.status == 'approved')
    .group_by(Question.contest_id)
    .all()
)
```

### Bulk Operations

**Bulk insert:**

```python
from database.utils import bulk_insert

# Much faster than individual inserts
data = [
    {"user_id": 1, "question_id": 1, "value": 1},
    {"user_id": 2, "question_id": 1, "value": 1},
    # ... more rows
]

bulk_insert(db, Vote, data)
```

**Bulk update:**

```python
from database.utils import bulk_update

data = [
    {"id": 1, "rank_score": 0.95},
    {"id": 2, "rank_score": 0.87},
    # ... more rows
]

bulk_update(db, Question, data)
```

### Select Only Needed Columns

**Inefficient (loads all columns):**

```python
users = db.query(User).all()
names = [u.full_name for u in users]
```

**Efficient (loads only needed columns):**

```python
names = db.query(User.full_name).all()
```

### Using Database Views

For complex queries used frequently, create views:

```sql
-- Create view for popular questions
CREATE VIEW popular_questions AS
SELECT
    q.id,
    q.contest_id,
    q.question_text,
    q.rank_score,
    COUNT(v.id) as vote_count,
    SUM(v.value) as vote_sum,
    u.full_name as author_name
FROM questions q
LEFT JOIN votes v ON v.question_id = q.id
LEFT JOIN users u ON u.id = q.author_id
WHERE q.status = 'approved'
GROUP BY q.id, u.full_name
ORDER BY q.rank_score DESC;
```

Then query the view:

```python
results = db.execute(text("SELECT * FROM popular_questions WHERE contest_id = :id"), {"id": contest_id})
```

## Index Optimization

### Checking Index Usage

**Find unused indexes:**

```bash
python database/scripts/analyze.py
```

Or programmatically:

```python
from database.utils import get_unused_indexes

unused = get_unused_indexes()
for idx in unused:
    print(f"{idx['tablename']}.{idx['indexname']}: {idx['index_size']} (never used)")
```

**Check which indexes are being used:**

```python
from database.utils import get_index_usage

usage = get_index_usage()
for idx in usage:
    print(f"{idx['indexname']}: {idx['idx_scan']} scans")
```

### Creating Effective Indexes

**Index foreign keys:**

```sql
-- Always index foreign keys
CREATE INDEX idx_votes_user_id ON votes(user_id);
CREATE INDEX idx_votes_question_id ON votes(question_id);
```

**Composite indexes for common queries:**

```sql
-- If you frequently query by city_id AND status
CREATE INDEX idx_users_city_status ON users(city_id, status);

-- Order matters! Put most selective column first
CREATE INDEX idx_ballots_city_date ON ballots(city_id, election_date);
```

**Partial indexes for filtered queries:**

```sql
-- Only index active users
CREATE INDEX idx_users_active ON users(id) WHERE is_active = true;

-- Only index published ballots
CREATE INDEX idx_ballots_published ON ballots(city_id, election_date)
WHERE is_published = true;
```

**Covering indexes (include columns):**

```sql
-- Include frequently accessed columns
CREATE INDEX idx_questions_contest_covering ON questions(contest_id)
INCLUDE (question_text, rank_score, status);
```

### Index Maintenance

**Rebuild indexes:**

```sql
-- Rebuild all indexes on a table
REINDEX TABLE questions;

-- Rebuild specific index
REINDEX INDEX idx_questions_contest_status;
```

**Monitor index bloat:**

```python
from database.utils import get_bloat_stats

bloat = get_bloat_stats()
for table in bloat:
    if table['dead_tuple_percent'] > 20:
        print(f"{table['tablename']}: {table['dead_tuple_percent']:.2f}% dead tuples")
```

## Connection Pool Tuning

### Monitoring Pool Health

```python
from database.monitoring import DatabaseMonitor

monitor = DatabaseMonitor()
stats = monitor.check_connection_pool()

print(f"Pool size: {stats['pool_size']}")
print(f"Checked out: {stats['checked_out']}")
print(f"Utilization: {stats['utilization_percent']:.1f}%")
```

### Optimal Pool Sizing

**Formula:**

```
pool_size = (number_of_cores * 2) + effective_spindle_count
```

For typical web application:

```python
# app/models/base.py
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,          # Base connections
    max_overflow=20,       # Extra connections when busy
    pool_recycle=3600,     # Recycle after 1 hour
    pool_pre_ping=True,    # Test connections before use
)
```

### Connection Pooling Best Practices

1. **Always close connections:**

```python
# Use context manager
with get_db_session() as db:
    # Do work
    pass
# Connection automatically returned to pool
```

2. **Set timeout for long operations:**

```python
from sqlalchemy import create_engine

engine = create_engine(
    settings.DATABASE_URL,
    pool_timeout=30,  # Wait max 30 seconds for connection
)
```

3. **Monitor for leaks:**

```python
from database.monitoring import DatabaseMonitor

monitor = DatabaseMonitor()
conn_stats = monitor.get_connection_stats()

# Look for idle in transaction
if conn_stats['idle_in_transaction'] > 5:
    print("Possible connection leak!")
```

## Cache Optimization

### Checking Cache Performance

```python
from database.utils import get_cache_hit_ratio, get_table_cache_stats

# Overall cache ratio
stats = get_cache_hit_ratio()
print(f"Cache hit ratio: {stats['cache_hit_ratio']:.2f}%")

# Per-table cache stats
table_stats = get_table_cache_stats()
for table in table_stats:
    print(f"{table['tablename']}: {table['cache_hit_ratio']:.2f}%")
```

### PostgreSQL Cache Settings

In `postgresql.conf`:

```ini
# Shared buffer pool (25% of RAM for dedicated DB server)
shared_buffers = 4GB

# Effective cache size (50-75% of RAM)
effective_cache_size = 12GB

# Work memory per operation
work_mem = 64MB

# Maintenance operations memory
maintenance_work_mem = 512MB
```

### Application-Level Caching

**Cache expensive queries:**

```python
from functools import lru_cache
from typing import List

@lru_cache(maxsize=100)
def get_popular_questions(contest_id: int) -> List[Question]:
    return (
        db.query(Question)
        .filter_by(contest_id=contest_id, status='approved')
        .order_by(desc(Question.rank_score))
        .limit(20)
        .all()
    )
```

**Use Redis for shared cache:**

```python
import redis
import json

cache = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_questions(contest_id: int):
    # Check cache first
    cache_key = f"questions:contest:{contest_id}"
    cached = cache.get(cache_key)

    if cached:
        return json.loads(cached)

    # Query database
    questions = get_questions_from_db(contest_id)

    # Cache for 5 minutes
    cache.setex(cache_key, 300, json.dumps(questions))

    return questions
```

## Vacuum and Maintenance

### Autovacuum Configuration

In `postgresql.conf`:

```ini
# Enable autovacuum
autovacuum = on

# Autovacuum after 20% of table changes
autovacuum_vacuum_scale_factor = 0.2
autovacuum_analyze_scale_factor = 0.1

# More aggressive for large tables
autovacuum_vacuum_cost_limit = 1000
autovacuum_vacuum_cost_delay = 10ms
```

### Manual Vacuum Operations

**Check tables needing vacuum:**

```bash
python database/scripts/vacuum.py --candidates --threshold 20
```

**Vacuum specific table:**

```bash
python database/scripts/vacuum.py --table questions
```

**Full vacuum (reclaims maximum space):**

```bash
python database/scripts/vacuum.py --table questions --full
```

**Auto-vacuum based on threshold:**

```bash
python database/scripts/vacuum.py --auto-vacuum --threshold 20
```

### Analyze for Query Planning

**Update statistics:**

```bash
python database/scripts/vacuum.py --analyze-only --table questions
```

**Automatic analyze after data changes:**

```python
from sqlalchemy import event
from app.models.question import Question

@event.listens_for(Question, 'after_bulk_insert')
def analyze_after_insert(mapper, connection, target):
    connection.execute(text("ANALYZE questions"))
```

## Query Patterns

### Common CivicQ Query Patterns

**Get questions for a contest (with pagination):**

```python
def get_contest_questions(
    db: Session,
    contest_id: int,
    status: str = 'approved',
    page: int = 1,
    per_page: int = 20
):
    return (
        db.query(Question)
        .options(
            joinedload(Question.author),
            joinedload(Question.contest)
        )
        .filter(
            Question.contest_id == contest_id,
            Question.status == status
        )
        .order_by(desc(Question.rank_score))
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
```

**Get user's votes for questions:**

```python
def get_user_votes(db: Session, user_id: int, question_ids: List[int]):
    votes = (
        db.query(Vote.question_id, Vote.value)
        .filter(
            Vote.user_id == user_id,
            Vote.question_id.in_(question_ids)
        )
        .all()
    )

    return {v.question_id: v.value for v in votes}
```

**Get candidates with answer counts:**

```python
from sqlalchemy import func

def get_candidates_with_stats(db: Session, contest_id: int):
    return (
        db.query(
            Candidate,
            func.count(VideoAnswer.id).label('answer_count')
        )
        .outerjoin(VideoAnswer)
        .filter(Candidate.contest_id == contest_id)
        .group_by(Candidate.id)
        .order_by(Candidate.display_order)
        .all()
    )
```

**Search questions by text:**

```python
from sqlalchemy import func

def search_questions(db: Session, search_term: str, contest_id: int):
    return (
        db.query(Question)
        .filter(
            Question.contest_id == contest_id,
            func.to_tsvector('english', Question.question_text).match(search_term)
        )
        .order_by(desc(Question.rank_score))
        .all()
    )
```

**Get trending questions (most votes in last 24 hours):**

```python
from datetime import datetime, timedelta

def get_trending_questions(db: Session, contest_id: int, limit: int = 10):
    since = datetime.utcnow() - timedelta(hours=24)

    return (
        db.query(
            Question,
            func.count(Vote.id).label('recent_votes')
        )
        .join(Vote)
        .filter(
            Question.contest_id == contest_id,
            Question.status == 'approved',
            Vote.created_at >= since
        )
        .group_by(Question.id)
        .order_by(desc('recent_votes'))
        .limit(limit)
        .all()
    )
```

## Performance Monitoring

### Regular Health Checks

**Daily health check:**

```bash
python database/scripts/analyze.py --output daily_health.json
```

**Monitor slow queries:**

```python
from database.monitoring import DatabaseMonitor

monitor = DatabaseMonitor()
slow = monitor.check_slow_queries(threshold_ms=500)

if slow:
    print(f"Found {len(slow)} slow queries")
    for query in slow[:5]:
        print(f"  {query['duration_ms']:.0f}ms: {query['query_preview']}")
```

**Check for lock contention:**

```python
from database.monitoring import DatabaseMonitor

monitor = DatabaseMonitor()
locks = monitor.check_locks()

if locks['total_blocking'] > 0:
    print(f"WARNING: {locks['total_blocking']} blocking queries")
```

### Performance Metrics to Track

1. **Cache Hit Ratio** - Should be > 95%
2. **Connection Pool Utilization** - Should be < 80%
3. **Average Query Time** - Baseline and track changes
4. **Slow Query Count** - Should trend down
5. **Table Bloat** - Keep dead tuples < 20%
6. **Disk Space** - Monitor growth rate

### Setting Up Alerts

```python
from database.monitoring import DatabaseMonitor, AlertLevel

def check_database_health():
    monitor = DatabaseMonitor()
    health = monitor.run_health_check()

    # Check for critical issues
    critical = [
        a for a in health['alerts']
        if a['level'] == AlertLevel.CRITICAL
    ]

    if critical:
        send_alert_to_ops_team(critical)

    return health['status']
```

## Best Practices Summary

1. **Always use indexes on foreign keys**
2. **Use eager loading to prevent N+1 queries**
3. **Paginate large result sets**
4. **Use bulk operations for multiple inserts/updates**
5. **Monitor and optimize slow queries regularly**
6. **Keep cache hit ratio above 95%**
7. **Vacuum regularly to prevent bloat**
8. **Use partial indexes for filtered queries**
9. **Profile queries with EXPLAIN ANALYZE**
10. **Monitor connection pool utilization**
