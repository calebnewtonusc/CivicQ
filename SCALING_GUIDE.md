# CivicQ Scaling Guide

Comprehensive guide for scaling CivicQ from hundreds to millions of users.

## Table of Contents

- [Scaling Overview](#scaling-overview)
- [Performance Benchmarks](#performance-benchmarks)
- [Horizontal Scaling](#horizontal-scaling)
- [Vertical Scaling](#vertical-scaling)
- [Database Scaling](#database-scaling)
- [Caching Strategies](#caching-strategies)
- [CDN and Asset Optimization](#cdn-and-asset-optimization)
- [Load Testing](#load-testing)
- [Monitoring for Scale](#monitoring-for-scale)
- [Cost vs Performance](#cost-vs-performance)

---

## Scaling Overview

### Growth Stages

| Stage | Users | Requests/sec | Infrastructure |
|-------|-------|--------------|----------------|
| **Startup** | 100-1,000 | <10 | Single server |
| **Growth** | 1,000-10,000 | 10-100 | Multi-container |
| **Scale** | 10,000-100,000 | 100-1,000 | Multi-region |
| **Enterprise** | 100,000+ | 1,000+ | Global CDN |

### Bottlenecks by Stage

**Startup (100-1K users):**
- None initially
- Single database sufficient

**Growth (1K-10K users):**
- Database connections
- Single server CPU/memory
- API rate limits

**Scale (10K-100K users):**
- Database query performance
- Redis memory
- Video processing queue
- Network bandwidth

**Enterprise (100K+ users):**
- Database write scalability
- Cross-region latency
- Real-time connections
- Storage costs

---

## Performance Benchmarks

### Current Performance (Single Instance)

**Hardware:**
- 2 vCPU, 4GB RAM
- PostgreSQL: db.t4g.medium
- Redis: cache.t4g.small

**Metrics:**
- API Requests: ~500/sec
- WebSocket Connections: ~1,000 concurrent
- Database Queries: ~2,000/sec
- Video Processing: ~10 concurrent

**Response Times (p95):**
- API GET: <100ms
- API POST: <200ms
- Database Query: <50ms
- Page Load: <2s

### Target Performance Goals

| Metric | Target | Critical |
|--------|--------|----------|
| API Latency (p95) | <200ms | <500ms |
| Page Load | <3s | <5s |
| Error Rate | <0.1% | <1% |
| Uptime | 99.9% | 99.0% |

---

## Horizontal Scaling

### Backend API Scaling

**Docker Compose (Simple):**

```yaml
services:
  backend:
    deploy:
      replicas: 3  # Run 3 instances
      resources:
        limits:
          cpus: '1'
          memory: 2G
```

**Kubernetes (Advanced):**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: civicq-backend
spec:
  replicas: 5
  template:
    spec:
      containers:
      - name: backend
        image: civicq-backend:latest
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: civicq-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: civicq-backend
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Celery Worker Scaling

**Auto-scaling Workers:**

```yaml
celery-worker:
  deploy:
    replicas: 5
    resources:
      limits:
        cpus: '2'
        memory: 4G
```

**Queue-based Scaling:**

Monitor queue length and scale workers automatically:

```python
# celery_autoscale.py
from celery import Celery
import redis

app = Celery('tasks')
r = redis.Redis()

def scale_workers():
    queue_length = r.llen('celery')

    if queue_length > 100:
        # Scale up
        target_workers = min(queue_length // 20, 20)
    elif queue_length < 10:
        # Scale down
        target_workers = max(3, queue_length // 5)

    # Update deployment
    # kubectl scale deployment celery-worker --replicas={target_workers}
```

### Load Balancing

**Nginx Configuration:**

```nginx
upstream backend_cluster {
    least_conn;  # Least connections algorithm
    server backend-1:8000 max_fails=3 fail_timeout=30s;
    server backend-2:8000 max_fails=3 fail_timeout=30s;
    server backend-3:8000 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

server {
    location /api/ {
        proxy_pass http://backend_cluster;
    }
}
```

---

## Vertical Scaling

### When to Scale Vertically

Scale vertically (bigger instances) when:
- High CPU/memory usage (>80%)
- Individual operations are CPU-bound
- More cost-effective than horizontal scaling
- Simpler to manage

### Backend Scaling Tiers

| Tier | vCPU | RAM | Cost/mo | Max RPS |
|------|------|-----|---------|---------|
| Small | 1 | 2GB | $30 | ~200 |
| Medium | 2 | 4GB | $60 | ~500 |
| Large | 4 | 8GB | $120 | ~1,500 |
| XLarge | 8 | 16GB | $240 | ~3,000 |

### Database Scaling Tiers

| Tier | Instance | vCPU | RAM | Storage | Cost/mo |
|------|----------|------|-----|---------|---------|
| Small | db.t4g.small | 2 | 2GB | 20GB | $25 |
| Medium | db.t4g.medium | 2 | 4GB | 100GB | $70 |
| Large | db.m6g.large | 2 | 8GB | 200GB | $130 |
| XLarge | db.m6g.xlarge | 4 | 16GB | 500GB | $260 |
| 2XLarge | db.m6g.2xlarge | 8 | 32GB | 1TB | $520 |

---

## Database Scaling

### Phase 1: Query Optimization

**Add Indexes:**

```sql
-- Frequently queried columns
CREATE INDEX idx_questions_city_id ON questions(city_id);
CREATE INDEX idx_questions_created_at ON questions(created_at DESC);
CREATE INDEX idx_votes_question_id ON votes(question_id);
CREATE INDEX idx_votes_user_id ON votes(user_id);

-- Composite indexes
CREATE INDEX idx_questions_city_created ON questions(city_id, created_at DESC);

-- Vector index for embeddings
CREATE INDEX idx_questions_embedding ON questions USING ivfflat (embedding vector_cosine_ops);
```

**Optimize Queries:**

```python
# Bad: N+1 queries
questions = session.query(Question).all()
for q in questions:
    print(q.user.name)  # Separate query for each user

# Good: Eager loading
questions = session.query(Question).options(
    joinedload(Question.user)
).all()
```

### Phase 2: Connection Pooling

**SQLAlchemy Configuration:**

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # Connections to keep open
    max_overflow=40,       # Additional connections when needed
    pool_pre_ping=True,    # Verify connections before using
    pool_recycle=3600,     # Recycle connections after 1 hour
)
```

### Phase 3: Read Replicas

**Setup Read Replicas:**

```python
# models.py
from sqlalchemy import create_engine

# Master for writes
master_engine = create_engine(MASTER_DATABASE_URL)

# Replica for reads
replica_engine = create_engine(REPLICA_DATABASE_URL)

# Session factory
def get_db():
    return Session(bind=master_engine)

def get_readonly_db():
    return Session(bind=replica_engine)

# Usage
@app.get("/questions")
def get_questions(db: Session = Depends(get_readonly_db)):
    # Uses read replica
    return db.query(Question).all()

@app.post("/questions")
def create_question(db: Session = Depends(get_db)):
    # Uses master
    question = Question(...)
    db.add(question)
    db.commit()
```

### Phase 4: Partitioning

**Time-based Partitioning:**

```sql
-- Partition questions by month
CREATE TABLE questions_2024_01 PARTITION OF questions
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE questions_2024_02 PARTITION OF questions
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Automatic partition management
CREATE FUNCTION create_partition_for_month() RETURNS void AS $$
DECLARE
    partition_date DATE;
    partition_name TEXT;
BEGIN
    partition_date := DATE_TRUNC('month', CURRENT_DATE + INTERVAL '1 month');
    partition_name := 'questions_' || TO_CHAR(partition_date, 'YYYY_MM');

    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF questions FOR VALUES FROM (%L) TO (%L)',
        partition_name,
        partition_date,
        partition_date + INTERVAL '1 month'
    );
END;
$$ LANGUAGE plpgsql;
```

### Phase 5: Sharding (Advanced)

For 1M+ users, implement database sharding:

```python
# sharding.py
def get_shard(user_id: int) -> str:
    """Determine which database shard to use"""
    shard_count = 4
    shard_id = user_id % shard_count
    return f"shard_{shard_id}"

def get_shard_engine(user_id: int):
    shard = get_shard(user_id)
    return shard_engines[shard]

# Usage
@app.get("/users/{user_id}")
def get_user(user_id: int):
    engine = get_shard_engine(user_id)
    with Session(engine) as session:
        return session.query(User).get(user_id)
```

---

## Caching Strategies

### Level 1: Application Caching

**In-Memory Cache:**

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_popular_questions():
    # Expensive database query
    return db.query(Question).order_by(
        Question.vote_count.desc()
    ).limit(100).all()
```

### Level 2: Redis Caching

**API Response Caching:**

```python
from redis import Redis
import json

redis_client = Redis.from_url(REDIS_URL)

@app.get("/api/questions")
async def get_questions(city_id: int):
    cache_key = f"questions:{city_id}"

    # Try cache first
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # Query database
    questions = db.query(Question).filter_by(city_id=city_id).all()

    # Cache for 5 minutes
    redis_client.setex(
        cache_key,
        300,
        json.dumps([q.dict() for q in questions])
    )

    return questions
```

**Cache Invalidation:**

```python
@app.post("/api/questions")
async def create_question(question: QuestionCreate):
    # Create question
    new_question = Question(**question.dict())
    db.add(new_question)
    db.commit()

    # Invalidate cache
    redis_client.delete(f"questions:{question.city_id}")

    return new_question
```

### Level 3: CDN Caching

**Nginx Cache Configuration:**

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g inactive=60m;

location /api/v1/questions {
    proxy_cache api_cache;
    proxy_cache_valid 200 5m;
    proxy_cache_valid 404 1m;
    proxy_cache_key "$request_uri";
    proxy_cache_use_stale error timeout http_500 http_502 http_503;

    add_header X-Cache-Status $upstream_cache_status;
    proxy_pass http://backend;
}
```

---

## CDN and Asset Optimization

### Frontend Optimization

**Code Splitting:**

```javascript
// Lazy load routes
const Home = lazy(() => import('./pages/Home'));
const Questions = lazy(() => import('./pages/Questions'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/questions" element={<Questions />} />
      </Routes>
    </Suspense>
  );
}
```

**Image Optimization:**

```nginx
# WebP conversion
location ~* \.(jpg|jpeg|png)$ {
    set $webp_suffix "";

    if ($http_accept ~* "webp") {
        set $webp_suffix ".webp";
    }

    try_files $uri$webp_suffix $uri =404;

    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Video Optimization

**Adaptive Bitrate Streaming:**

```python
# video_processor.py
def create_hls_variants(video_path):
    """Create multiple quality variants"""
    variants = [
        {"height": 1080, "bitrate": "5000k"},
        {"height": 720, "bitrate": "2500k"},
        {"height": 480, "bitrate": "1000k"},
        {"height": 360, "bitrate": "500k"},
    ]

    for variant in variants:
        ffmpeg.input(video_path).output(
            f"{video_path}_{variant['height']}p.m3u8",
            vcodec='libx264',
            video_bitrate=variant['bitrate'],
            maxrate=variant['bitrate'],
            bufsize=f"{int(variant['bitrate'][:-1]) * 2}k",
            vf=f"scale=-2:{variant['height']}",
            hls_time=10,
            hls_list_size=0,
        ).run()
```

---

## Load Testing

### Tools

**Apache Bench (Simple):**

```bash
# Test API endpoint
ab -n 10000 -c 100 https://api.civicq.com/health

# Results
# Requests per second: 1234.56
# Time per request: 81.02 ms (mean)
```

**k6 (Advanced):**

```javascript
// load_test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp up
    { duration: '5m', target: 100 },  // Steady state
    { duration: '2m', target: 200 },  // Peak
    { duration: '5m', target: 200 },
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% under 500ms
    http_req_failed: ['rate<0.01'],   // Error rate < 1%
  },
};

export default function () {
  let res = http.get('https://api.civicq.com/api/v1/questions');
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  sleep(1);
}
```

**Run Load Test:**

```bash
k6 run --vus 100 --duration 10m load_test.js
```

### Interpreting Results

**Good Performance:**
- p95 latency < 500ms
- Error rate < 1%
- No connection timeouts
- Database connections stable

**Performance Issues:**
- p95 latency > 1s
- Error rate > 5%
- Connection pool exhausted
- High CPU/memory usage

---

## Monitoring for Scale

### Key Metrics to Track

**Application Metrics:**

```python
from prometheus_client import Counter, Histogram, Gauge

# Request counter
request_count = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])

# Response time histogram
request_duration = Histogram('api_request_duration_seconds', 'API request duration', ['endpoint'])

# Active connections
active_connections = Gauge('api_active_connections', 'Active connections')

# Usage in FastAPI
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    request_duration.labels(endpoint=request.url.path).observe(duration)

    return response
```

### Alerting Rules

**Prometheus Alerts:**

```yaml
groups:
  - name: civicq_alerts
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: rate(api_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High API error rate"

      # High latency
      - alert: HighLatency
        expr: histogram_quantile(0.95, api_request_duration_seconds) > 1
        for: 5m
        annotations:
          summary: "API latency is high"

      # Database connections
      - alert: DatabaseConnectionsHigh
        expr: database_connections > 80
        for: 5m
        annotations:
          summary: "Database connection pool nearly exhausted"
```

---

## Cost vs Performance

### Optimization Matrix

| Optimization | Cost Impact | Performance Impact | Complexity |
|--------------|-------------|-------------------|------------|
| Add CDN | +$50/mo | High (latency) | Low |
| Caching (Redis) | +$30/mo | High (RPS) | Medium |
| Read Replicas | +100% DB cost | Medium (read perf) | Medium |
| Auto-scaling | Variable | High (reliability) | High |
| Upgrade instances | +50-200% | Medium | Low |

### ROI Analysis

**Example: Adding Redis Cache**

**Cost:**
- Redis instance: $30/mo
- Engineering time: 4 hours

**Benefits:**
- 50% reduction in database load
- 80% faster API responses
- Can handle 3x more users
- Defer database upgrade ($100/mo saved)

**ROI:** Positive after month 1

---

## Scaling Checklist

### Before 1,000 Users
- [ ] Single server deployment
- [ ] Basic monitoring
- [ ] Daily backups
- [ ] CDN for static assets

### Before 10,000 Users
- [ ] Multiple backend containers
- [ ] Redis caching
- [ ] Database connection pooling
- [ ] Auto-scaling enabled
- [ ] Comprehensive monitoring

### Before 100,000 Users
- [ ] Database read replicas
- [ ] Multi-region deployment
- [ ] Advanced caching strategies
- [ ] Load testing performed
- [ ] Incident response plan

### Before 1,000,000 Users
- [ ] Database sharding
- [ ] Global CDN
- [ ] Real-time monitoring
- [ ] Chaos engineering
- [ ] 24/7 on-call rotation

---

**Last Updated:** 2024-02-14
**Version:** 1.0.0
