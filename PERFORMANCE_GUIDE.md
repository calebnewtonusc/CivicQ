# CivicQ Performance Optimization Guide

Complete guide to optimizing CivicQ for production at scale (10,000+ concurrent users).

## Table of Contents

1. [Overview](#overview)
2. [Performance Architecture](#performance-architecture)
3. [Backend Optimizations](#backend-optimizations)
4. [Frontend Optimizations](#frontend-optimizations)
5. [Database Optimizations](#database-optimizations)
6. [Caching Strategy](#caching-strategy)
7. [CDN Configuration](#cdn-configuration)
8. [Monitoring & Metrics](#monitoring--metrics)
9. [Performance Checklist](#performance-checklist)

## Overview

### Performance Goals

- **Page Load Time**: < 2 seconds
- **Time to Interactive (TTI)**: < 3 seconds
- **API Response Time**: < 200ms (avg), < 500ms (p95)
- **Database Query Time**: < 100ms (avg)
- **Cache Hit Rate**: > 80%
- **Concurrent Users**: 10,000+
- **Requests/Second**: 50,000+

### Current Performance Optimizations

- Multi-layer caching (CDN, HTTP, Application, Database)
- Response compression (Gzip/Brotli)
- Database query optimization
- Connection pooling
- Async processing for heavy operations
- Code splitting and lazy loading
- Image optimization
- CDN for static assets

## Performance Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  CDN        │ (Cloudflare - Global edge caching)
│  Cache      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Load       │ (Nginx - SSL termination, compression)
│  Balancer   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  HTTP       │ (FastAPI middleware - Response caching, ETag)
│  Cache      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  FastAPI    │ (Application layer)
│  App        │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Redis      │ (Application cache - Query results, sessions)
│  Cache      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  PostgreSQL │ (Database with query cache)
│  Database   │
└─────────────┘
```

## Backend Optimizations

### 1. API Response Optimization

**Compression**:
```python
# Enabled in middleware/caching.py
from app.middleware.caching import CompressionMiddleware

app.add_middleware(CompressionMiddleware)

# Automatic gzip/brotli compression for:
# - application/json
# - text/html, text/css, text/javascript
# - Minimum size: 1KB
```

**ETag Support**:
```python
from app.middleware.caching import ETagMiddleware

app.add_middleware(ETagMiddleware)

# Generates ETag for responses
# Supports If-None-Match for 304 responses
# Reduces bandwidth for unchanged resources
```

**Field Selection** (Sparse Fieldsets):
```python
# Allow clients to request specific fields
@app.get("/api/questions/{id}")
async def get_question(
    id: int,
    fields: Optional[str] = None  # e.g., "id,title,vote_count"
):
    question = get_question_from_db(id)

    if fields:
        requested_fields = fields.split(",")
        return {k: v for k, v in question.items() if k in requested_fields}

    return question
```

### 2. Async Processing

**Celery for Background Tasks**:
```python
# Heavy operations run asynchronously
from app.tasks.video_tasks import process_video

# In API endpoint
@app.post("/api/videos/upload")
async def upload_video(file: UploadFile):
    # Save file
    video_id = save_video_file(file)

    # Process asynchronously
    process_video.delay(video_id)

    return {"id": video_id, "status": "processing"}
```

**Batch Operations**:
```python
# Process multiple items efficiently
@app.post("/api/votes/batch")
async def batch_vote(votes: List[VoteData]):
    async with database.transaction():
        results = await database.execute_many(
            "INSERT INTO votes (...) VALUES (...)",
            [vote.dict() for vote in votes]
        )
    return {"processed": len(results)}
```

### 3. Connection Pooling

**Database Connection Pool**:
```python
# backend/app/core/database.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # Normal connections
    max_overflow=30,       # Additional connections during spikes
    pool_pre_ping=True,    # Verify connections before use
    pool_recycle=3600,     # Recycle connections after 1 hour
)
```

**Redis Connection Pool**:
```python
# backend/app/services/cache_service.py
redis_client = redis.from_url(
    REDIS_URL,
    max_connections=50,
    socket_connect_timeout=5,
    socket_timeout=5,
)
```

### 4. Rate Limiting

Already implemented in `app/core/rate_limit.py`:
- Login attempts: 5 per 15 minutes
- Password reset: 3 per hour
- Question submission: 10 per day
- Vote casting: 100 per hour

### 5. Response Caching

**Middleware Level** (`app/middleware/caching.py`):
- Caches GET requests
- Respects cache headers
- ETag generation
- Compression

**Application Level** (`app/services/cache_service.py`):
```python
from app.services.cache_service import cached

@cached(key_prefix="trending", ttl=900)  # 15 minutes
async def get_trending_questions(contest_id: int):
    return calculate_trending_questions(contest_id)
```

## Frontend Optimizations

### 1. Code Splitting

**Route-Based Splitting** (Already implemented):
```typescript
// App.tsx - Lazy load pages
const HomePage = lazy(() => import('./pages/HomePage'));
const BallotPage = lazy(() => import('./pages/BallotPage'));
const QuestionDetailPage = lazy(() => import('./pages/QuestionDetailPage'));

// Wrap in Suspense
<Suspense fallback={<LoadingSpinner />}>
  <Routes>
    <Route path="/" element={<HomePage />} />
    <Route path="/ballot/:citySlug" element={<BallotPage />} />
  </Routes>
</Suspense>
```

**Component-Level Splitting**:
```typescript
// Lazy load heavy components
const VideoPlayer = lazy(() => import('./components/VideoPlayer'));
const ChartComponent = lazy(() => import('./components/Chart'));
```

### 2. React Query Optimization

Configured in `frontend/src/utils/queryClient.ts`:

```typescript
// Optimized caching
staleTime: 5 * 60 * 1000,      // 5 minutes
gcTime: 10 * 60 * 1000,         // 10 minutes

// Prefetching
prefetchUtils.prefetchTrendingQuestions(contestId);

// Optimistic updates
optimisticUpdates.voteOnQuestion(questionId, 'upvote');
```

### 3. Image Optimization

**Optimized Image Component** (`frontend/src/components/OptimizedImage.tsx`):
- Lazy loading with Intersection Observer
- WebP format with fallback
- Responsive images (srcset)
- Loading placeholders

**Usage**:
```typescript
<OptimizedImage
  src="/images/candidate.jpg"
  alt="Candidate photo"
  width={300}
  height={400}
  sizes="(max-width: 768px) 100vw, 50vw"
/>
```

### 4. Bundle Optimization

**Webpack Configuration**:
```javascript
// package.json build scripts already optimized
"build": "react-scripts build"

// Creates optimized production build with:
// - Minification
// - Tree shaking
// - Code splitting
// - Asset hashing for cache busting
```

**Analyze Bundle**:
```bash
npm install --save-dev webpack-bundle-analyzer
npm run build -- --stats
npx webpack-bundle-analyzer build/bundle-stats.json
```

**Reduce Bundle Size**:
```bash
# Remove unused dependencies
npm uninstall <unused-package>

# Use lighter alternatives
# Example: date-fns instead of moment.js (already using date-fns)

# Import only what you need
import { format } from 'date-fns';  // Good
import * as dateFns from 'date-fns';  // Bad
```

### 5. Performance Monitoring

**Web Vitals**:
```typescript
// Add to index.tsx
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

function sendToAnalytics(metric) {
  // Send to backend
  fetch('/api/metrics/frontend', {
    method: 'POST',
    body: JSON.stringify(metric),
  });
}

getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getFCP(sendToAnalytics);
getLCP(sendToAnalytics);
getTTFB(sendToAnalytics);
```

## Database Optimizations

### 1. Query Optimization

**Use Select Related** (Eager Loading):
```python
# Bad - N+1 queries
questions = db.query(Question).all()
for question in questions:
    print(question.contest.name)  # Separate query for each!

# Good - Single query with join
questions = db.query(Question).options(
    joinedload(Question.contest)
).all()
for question in questions:
    print(question.contest.name)  # Already loaded!
```

**Use Defer/Load Only** (Lazy Loading):
```python
# Load only needed columns
questions = db.query(Question).options(
    defer(Question.description),  # Don't load large text field
    defer(Question.metadata),     # Don't load JSON field
).all()
```

### 2. Database Indexes

**Already Created** (see migrations):
- Primary keys (automatic)
- Foreign keys (automatic)
- Unique constraints (email, slug, etc.)

**Add Custom Indexes**:
```sql
-- For frequently filtered/sorted columns
CREATE INDEX idx_questions_created_at ON questions(created_at DESC);
CREATE INDEX idx_questions_vote_count ON questions(vote_count DESC);
CREATE INDEX idx_questions_status ON questions(status);

-- Composite indexes for common queries
CREATE INDEX idx_questions_contest_status ON questions(contest_id, status);

-- For full-text search
CREATE INDEX idx_questions_title_search ON questions USING GIN(to_tsvector('english', title));
```

### 3. Query Monitoring

```python
# Enable query logging in development
# backend/app/core/config.py
DATABASE_ECHO = True  # Logs all queries

# Use explain analyze for slow queries
from sqlalchemy import text

result = db.execute(text("""
    EXPLAIN ANALYZE
    SELECT * FROM questions
    WHERE contest_id = :contest_id
    ORDER BY vote_count DESC
    LIMIT 20
"""), {"contest_id": 1})

print(result.fetchall())
```

### 4. Connection Pooling

Already configured (see Backend Optimizations section).

### 5. Read Replicas (Future)

For high read load:
```python
# Master for writes
master_engine = create_engine(MASTER_DATABASE_URL)

# Replica for reads
replica_engine = create_engine(REPLICA_DATABASE_URL)

# Route queries
def get_db():
    if is_write_operation():
        return SessionLocal(bind=master_engine)
    else:
        return SessionLocal(bind=replica_engine)
```

## Caching Strategy

See [CACHING_STRATEGY.md](./CACHING_STRATEGY.md) for complete guide.

**Quick Reference**:

- **Ballot Data**: 1 hour TTL
- **Questions**: 15 minutes TTL
- **Trending**: 15 minutes TTL
- **Candidates**: 30 minutes TTL
- **City Settings**: 1 day TTL

**Implementation**:
```python
from app.utils.cache_helpers import DataCache

# Get cached data
ballot = DataCache.get_ballot(ballot_id)
if not ballot:
    ballot = fetch_from_db(ballot_id)
    DataCache.set_ballot(ballot_id, ballot)

# Invalidate on update
DataCache.invalidate_ballot(ballot_id)
```

## CDN Configuration

See [infrastructure/cdn/cloudflare.md](./infrastructure/cdn/cloudflare.md) for complete guide.

**Quick Setup**:

1. Add domain to Cloudflare
2. Configure DNS (A/CNAME records)
3. Set page rules for caching
4. Enable optimizations (Brotli, HTTP/2, HTTP/3)
5. Configure image optimization

**Benefits**:
- Global edge caching
- Reduced latency (serve from nearest location)
- Reduced origin load
- DDoS protection
- Free SSL/TLS

## Monitoring & Metrics

### Backend Metrics

**Access Metrics Endpoint**:
```bash
curl http://localhost:8000/api/admin/metrics

# Returns:
{
  "cache": {
    "hit_rate": 85.3,
    "total_keys": 1523,
    "memory_used": "45.2M"
  },
  "api": {
    "/api/questions": {
      "avg_response_time": 78.4,
      "p95_response_time": 145.2
    }
  },
  "database": {
    "select": {
      "avg_time": 45.2,
      "total_queries": 12453
    }
  }
}
```

**Metrics Tracked**:
- API response times
- Cache hit rates
- Database query times
- Error rates
- Request throughput

### Frontend Metrics

**Web Vitals** (already mentioned):
- **FCP** (First Contentful Paint): < 1.8s
- **LCP** (Largest Contentful Paint): < 2.5s
- **FID** (First Input Delay): < 100ms
- **CLS** (Cumulative Layout Shift): < 0.1
- **TTI** (Time to Interactive): < 3.8s

### Monitoring Tools

**Recommended**:
- **Sentry**: Error tracking (already configured)
- **Datadog**: Infrastructure monitoring
- **New Relic**: APM (Application Performance Monitoring)
- **Grafana + Prometheus**: Custom dashboards

**Setup Sentry** (already in config):
```python
# backend/app/core/sentry.py
import sentry_sdk

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.ENVIRONMENT,
    traces_sample_rate=0.1,  # 10% of transactions
)
```

## Performance Checklist

### Backend

- [x] Response compression (Gzip/Brotli)
- [x] ETag support for conditional requests
- [x] Multi-layer caching (HTTP, Application, Database)
- [x] Connection pooling (Database, Redis)
- [x] Async processing for heavy operations
- [x] Rate limiting
- [x] Database indexes
- [ ] Database query optimization (ongoing)
- [x] API response optimization
- [x] Error tracking (Sentry)

### Frontend

- [x] Code splitting (route-based)
- [x] Lazy loading components
- [x] Image optimization (lazy load, WebP, responsive)
- [x] React Query caching
- [x] Bundle optimization
- [ ] Service worker for offline support (optional)
- [ ] Pre-rendering for SEO (optional)
- [x] Web Vitals monitoring

### Infrastructure

- [x] CDN for static assets
- [x] Load balancer (Nginx)
- [x] SSL/TLS termination
- [ ] Auto-scaling (cloud deployment)
- [ ] Database read replicas (future)
- [x] Monitoring and alerts
- [x] Load testing

### Deployment

- [x] Environment variables for configuration
- [x] Docker containerization
- [x] Health check endpoints
- [ ] Blue-green deployment (recommended)
- [ ] Automated rollback (recommended)
- [x] Performance testing in CI/CD

## Performance Optimization Workflow

1. **Measure Current Performance**
   ```bash
   python load_tests/performance_benchmarks.py
   ```

2. **Identify Bottlenecks**
   - Slow API endpoints
   - High database query times
   - Low cache hit rate
   - Large bundle sizes

3. **Prioritize Optimizations**
   - High impact, low effort first
   - Focus on user-facing features

4. **Implement Optimizations**
   - One at a time for easier debugging
   - Test thoroughly

5. **Measure Improvement**
   ```bash
   # Before and after comparison
   python load_tests/performance_benchmarks.py --output before.json
   # (make changes)
   python load_tests/performance_benchmarks.py --output after.json
   python load_tests/compare_results.py before.json after.json
   ```

6. **Deploy to Production**
   - Monitor closely after deployment
   - Be ready to rollback

7. **Continuous Monitoring**
   - Set up alerts
   - Review metrics weekly
   - Regular load testing

## Quick Wins

Easy optimizations with high impact:

1. **Enable CDN** (if not already)
   - Instant global performance boost

2. **Add Missing Database Indexes**
   ```sql
   EXPLAIN ANALYZE <slow query>;
   -- Add index on filtered/sorted columns
   ```

3. **Increase Cache TTLs** (where appropriate)
   - More aggressive caching = better performance

4. **Enable Response Compression**
   - Already enabled, verify it's working

5. **Optimize Images**
   - Use OptimizedImage component
   - Convert to WebP format

6. **Reduce Bundle Size**
   - Remove unused dependencies
   - Use tree shaking

## Summary

CivicQ is optimized for production scale with:
- **Multi-layer caching**: CDN, HTTP, Application, Database
- **Compression**: Gzip/Brotli for all responses
- **Connection pooling**: Efficient resource usage
- **Async processing**: Non-blocking heavy operations
- **Code splitting**: Fast initial page load
- **Image optimization**: Lazy loading, WebP, responsive
- **Database optimization**: Indexes, query optimization
- **Monitoring**: Comprehensive metrics tracking

**Target**: Handle 10,000+ concurrent users with <200ms average API response time and >80% cache hit rate.

Regularly review performance metrics and run load tests to ensure targets are met.
