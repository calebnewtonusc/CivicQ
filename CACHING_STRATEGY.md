# CivicQ Caching Strategy

Comprehensive guide to CivicQ's multi-layer caching strategy for handling 10,000+ concurrent users.

## Table of Contents

1. [Overview](#overview)
2. [Cache Layers](#cache-layers)
3. [Cache Configuration](#cache-configuration)
4. [TTL Strategy](#ttl-strategy)
5. [Invalidation Strategies](#invalidation-strategies)
6. [Cache Warming](#cache-warming)
7. [Monitoring](#monitoring)
8. [Best Practices](#best-practices)

## Overview

CivicQ implements a multi-layer caching strategy:

```
User Request
    |
    v
[CDN Cache] (Cloudflare)
    |
    v
[HTTP Cache] (Response Caching Middleware)
    |
    v
[Application Cache] (Redis)
    |
    v
[Database Query Cache] (Redis + PostgreSQL)
    |
    v
[Database]
```

### Benefits

- **Reduced Latency**: Serve content from edge locations
- **Reduced Load**: Minimize database queries
- **Improved Scalability**: Handle more users with same infrastructure
- **Better UX**: Faster page loads and interactions

## Cache Layers

### 1. CDN Cache (Cloudflare)

**What**: Global content delivery network
**Caches**: Static assets, images, videos, select API responses
**TTL**: 1 day to 1 year depending on content type

Configuration: See `/infrastructure/cdn/cloudflare.md`

### 2. HTTP Response Cache

**What**: FastAPI middleware for caching API responses
**Caches**: GET request responses
**TTL**: 5 minutes to 1 hour depending on endpoint
**Implementation**: `/backend/app/middleware/caching.py`

Features:
- ETag support for conditional requests
- Gzip/Brotli compression
- Automatic cache key generation
- Response streaming

### 3. Application Cache (Redis)

**What**: In-memory data structure store
**Caches**: Query results, computed data, session data
**TTL**: 5 minutes to 1 day depending on data type
**Implementation**: `/backend/app/services/cache_service.py`

### 4. Database Query Cache

**What**: PostgreSQL query result caching
**Caches**: Complex query results
**TTL**: Varies by query complexity

## Cache Configuration

### Redis Configuration

```python
# backend/app/core/config.py
REDIS_URL = "redis://localhost:6379/0"

# Connection pooling
REDIS_MAX_CONNECTIONS = 50
REDIS_SOCKET_TIMEOUT = 5
REDIS_SOCKET_CONNECT_TIMEOUT = 5
```

### Cache Service Usage

```python
from app.services.cache_service import cache_service
from app.core.cache_keys import CacheKeys, CACHE_TTL_MAP

# Get from cache
ballot = cache_service.get(CacheKeys.ballot(ballot_id))

# Set in cache
cache_service.set(
    CacheKeys.ballot(ballot_id),
    ballot_data,
    ttl=CACHE_TTL_MAP["ballot"]
)

# Delete from cache
cache_service.delete(CacheKeys.ballot(ballot_id))

# Pattern-based deletion
cache_service.delete_pattern(CacheKeys.pattern_ballot(ballot_id))
```

## TTL Strategy

### Cache TTL by Data Type

| Data Type | TTL | Reason |
|-----------|-----|--------|
| **Ballot Data** | 1 hour | Changes infrequently, critical for performance |
| **Ballot List** | 5 minutes | May change as new ballots added |
| **Contest Data** | 1 hour | Relatively static during election |
| **Contest List** | 5 minutes | May update frequently |
| **Question** | 15 minutes | Vote counts change, but not critical to be real-time |
| **Question List** | 5 minutes | New questions submitted regularly |
| **Trending Questions** | 15 minutes | Changes with voting, but acceptable lag |
| **Candidate Profile** | 30 minutes | Updates occasionally |
| **Candidate List** | 30 minutes | Rarely changes during election |
| **City Settings** | 1 day | Very rarely changes |
| **City List** | 1 hour | New cities added infrequently |
| **Analytics Data** | 1 hour | Historical data, doesn't need real-time |
| **Video Metadata** | 1 hour | Rarely changes after upload |
| **Video Stream URL** | 6 hours | Presigned URLs with expiration |

### Implementation

```python
# /backend/app/core/cache_keys.py

CACHE_TTL_MAP = {
    "ballot": CacheKeys.TTL_1_HOUR,        # 3600s
    "ballot_list": CacheKeys.TTL_5_MINUTES,  # 300s
    "contest": CacheKeys.TTL_1_HOUR,
    "question": CacheKeys.TTL_15_MINUTES,
    "trending_questions": CacheKeys.TTL_15_MINUTES,
    "candidate": CacheKeys.TTL_30_MINUTES,
    "city": CacheKeys.TTL_1_DAY,           # 86400s
    "analytics": CacheKeys.TTL_1_HOUR,
    "video_url": CacheKeys.TTL_6_HOURS,    # 21600s
}
```

## Invalidation Strategies

### 1. Time-Based Invalidation (TTL)

Automatic expiration after TTL.

**Pros**: Simple, no manual intervention
**Cons**: May serve stale data until expiration

### 2. Event-Based Invalidation

Invalidate cache when data changes.

```python
from app.utils.cache_helpers import CacheInvalidation

# When question is created
CacheInvalidation.on_question_create(contest_id)

# When vote is cast
CacheInvalidation.on_vote_cast(question_id, contest_id)

# When candidate updates profile
CacheInvalidation.on_candidate_update(candidate_id, contest_id)

# When video is uploaded
CacheInvalidation.on_video_upload(candidate_id, question_id)
```

### 3. Pattern-Based Invalidation

Invalidate all related caches.

```python
from app.core.cache_keys import CacheKeys

# Invalidate all ballot-related caches
cache_service.delete_pattern(CacheKeys.pattern_ballot(ballot_id))

# Invalidate all trending data
cache_service.delete_pattern(CacheKeys.pattern_trending())

# Invalidate all city data
cache_service.delete_pattern(CacheKeys.pattern_city(city_slug))
```

### 4. Manual Invalidation

For admin operations or deployments.

```python
# Clear specific cache
cache_service.delete(CacheKeys.ballot(ballot_id))

# Clear all caches (use sparingly!)
cache_service.clear_all()
```

### Invalidation Triggers

| Event | Invalidation Action |
|-------|---------------------|
| Question submitted | Invalidate question lists, trending |
| Vote cast | Invalidate question, trending, contest stats |
| Video uploaded | Invalidate candidate responses, question |
| Candidate profile updated | Invalidate candidate, candidate list |
| Ballot imported | Invalidate all ballot/contest caches |
| City settings updated | Invalidate city cache |
| Question moderated | Invalidate question, lists |

## Cache Warming

Pre-populate cache with frequently accessed data.

### When to Warm Cache

- Application startup
- After cache clear
- Before expected traffic spike
- After data import/migration

### Implementation

```python
from app.utils.cache_helpers import CacheWarming

# Warm ballot data
CacheWarming.warm_ballot_data(
    ballot_id,
    loader_func=lambda: fetch_ballot_from_db(ballot_id)
)

# Warm trending questions
CacheWarming.warm_trending_questions(
    contest_id,
    loader_func=lambda: calculate_trending_questions(contest_id)
)

# Warm all candidates for contest
CacheWarming.warm_candidate_profiles(
    contest_id,
    candidate_loader=lambda: fetch_contest_candidates(contest_id)
)
```

### Automated Cache Warming

```python
# On application startup
@app.on_event("startup")
async def warm_caches():
    # Warm most accessed cities
    popular_cities = ["los-angeles", "san-francisco", "san-diego"]
    for city_slug in popular_cities:
        CacheWarming.warm_city_data(city_slug, lambda: fetch_city(city_slug))

    # Warm trending questions for active contests
    active_contests = get_active_contests()
    for contest in active_contests:
        CacheWarming.warm_trending_questions(
            contest.id,
            lambda: calculate_trending(contest.id)
        )
```

## Monitoring

### Cache Statistics

```python
from app.services.cache_service import cache_service

# Get cache stats
stats = cache_service.get_stats()
# {
#     "available": true,
#     "total_keys": 1523,
#     "hits": 45234,
#     "misses": 5621,
#     "hit_rate": 88.96,
#     "memory_used": "45.2M",
#     "memory_peak": "52.1M",
#     "evicted_keys": 0
# }
```

### Performance Metrics

```python
from app.utils.performance_monitoring import PerformanceMetrics

# Get cache performance
cache_metrics = PerformanceMetrics.get_cache_metrics()

# Get API performance
api_metrics = PerformanceMetrics.get_api_metrics("/api/questions", "GET")
```

### Monitoring Dashboard

Access metrics at `/api/admin/metrics` (requires admin auth):

```json
{
  "cache": {
    "hit_rate": 88.96,
    "total_keys": 1523,
    "memory_used": "45.2M"
  },
  "api": {
    "/api/questions": {
      "avg_response_time": 45.2,
      "p95_response_time": 120.5
    }
  }
}
```

### Alerts

Set up monitoring alerts for:
- Cache hit rate < 70%
- Redis memory > 80% usage
- API response time > 500ms (p95)
- Cache eviction rate > 100/min

## Best Practices

### 1. Cache Keys

Use consistent, descriptive cache keys:

```python
# Good
CacheKeys.ballot(ballot_id)  # "civicq:ballot:123"
CacheKeys.question_list(contest_id, page, sort)  # "civicq:questions:contest:5:page:1:sort:trending"

# Bad
"ballot_123"
"questions_5_1_trending"
```

### 2. TTL Selection

Choose appropriate TTLs:
- **Too short**: Defeats caching purpose, high database load
- **Too long**: Stale data, poor UX
- **Just right**: Balance freshness and performance

### 3. Cache Invalidation

- Prefer event-based over time-based for critical data
- Use pattern matching for related data
- Be careful with "clear all" - very expensive

### 4. Cache Penetration Prevention

Prevent cache stampede when popular item expires:

```python
from app.services.cache_service import cached

@cached(key_prefix="question", ttl=900)  # 15 minutes
async def get_question(question_id: int):
    return await fetch_question_from_db(question_id)
```

### 5. Null Value Caching

Cache "not found" results to prevent repeated DB queries:

```python
result = cache_service.get(key)
if result is None:
    result = fetch_from_db()
    if result is None:
        # Cache null result with short TTL
        cache_service.set(key, {"not_found": True}, ttl=60)
    else:
        cache_service.set(key, result, ttl=3600)
```

### 6. Monitor and Adjust

- Regularly review cache hit rates
- Adjust TTLs based on access patterns
- Monitor memory usage
- Track slow queries

### 7. Graceful Degradation

Always handle cache failures gracefully:

```python
def get_ballot(ballot_id: int):
    # Try cache first
    cached = cache_service.get(CacheKeys.ballot(ballot_id))
    if cached:
        return cached

    # Fall back to database
    ballot = fetch_from_db(ballot_id)

    # Try to cache (but don't fail if caching fails)
    try:
        cache_service.set(CacheKeys.ballot(ballot_id), ballot, ttl=3600)
    except Exception as e:
        logger.error(f"Failed to cache ballot: {e}")

    return ballot
```

## Cache Performance Targets

### Target Metrics

- **Cache Hit Rate**: > 80%
- **Cache Response Time**: < 5ms
- **API Response Time (cached)**: < 50ms
- **API Response Time (uncached)**: < 200ms
- **Memory Usage**: < 80% of allocated
- **Eviction Rate**: < 10 keys/minute

### Capacity Planning

For 10,000 concurrent users:

- **Redis Memory**: 4-8 GB
- **Cache Keys**: ~50,000-100,000
- **Requests/Second**: ~5,000
- **Cache Hits/Second**: ~4,000 (80% hit rate)
- **Database Queries/Second**: ~1,000 (20% cache misses)

## Troubleshooting

### Low Hit Rate

**Symptoms**: Hit rate < 70%
**Causes**:
- TTLs too short
- Frequent invalidations
- Poor cache key design
- High cardinality (unique queries)

**Solutions**:
- Increase TTLs where appropriate
- Review invalidation logic
- Use consistent cache keys
- Implement query result caching

### High Memory Usage

**Symptoms**: Memory > 80%
**Causes**:
- Too many keys
- Large cached objects
- TTLs too long
- Memory leak

**Solutions**:
- Reduce TTLs
- Compress large objects
- Implement LRU eviction
- Monitor for leaks

### Cache Stampede

**Symptoms**: Sudden spike in database load when cache expires
**Causes**:
- Popular item expires
- Many requests simultaneously try to rebuild cache

**Solutions**:
- Use cache locking (only one request rebuilds)
- Implement probabilistic early expiration
- Use background cache warming

## Summary

CivicQ's caching strategy:
- **Multi-layer**: CDN, HTTP, Application, Database
- **Intelligent TTLs**: Based on data freshness requirements
- **Event-driven invalidation**: Keep cache fresh
- **Proactive warming**: Prepare for traffic
- **Comprehensive monitoring**: Track performance
- **Graceful degradation**: Handle failures

Target: 80%+ cache hit rate, <50ms cached response time, handle 10,000+ concurrent users.
