# CivicQ Load Testing Guide

Complete guide for load testing CivicQ to ensure it can handle 10,000+ concurrent users.

## Table of Contents

1. [Overview](#overview)
2. [Load Testing Tools](#load-testing-tools)
3. [Running Load Tests](#running-load-tests)
4. [Performance Benchmarks](#performance-benchmarks)
5. [Interpreting Results](#interpreting-results)
6. [Performance Targets](#performance-targets)
7. [Troubleshooting](#troubleshooting)

## Overview

Load testing simulates real-world usage patterns to:
- Identify performance bottlenecks
- Validate system can handle target load
- Measure response times under load
- Test auto-scaling behavior
- Verify cache effectiveness

### Test Scenarios

CivicQ load tests simulate:
- **Casual Browsers** (70%): Browse questions and vote
- **Active Voters** (20%): Browse, vote, watch videos
- **Question Submitters** (5%): Submit new questions
- **Candidates** (3%): View and respond to questions
- **Admins** (2%): Moderate content

## Load Testing Tools

### Locust (Primary Tool)

Python-based load testing framework.

**Advantages**:
- Realistic user behavior simulation
- Easy to write test scenarios
- Web-based UI for monitoring
- Distributed load generation
- Great for API testing

**Installation**:
```bash
cd load_tests
pip install -r requirements.txt
```

### Performance Benchmarks Script

Custom Python script for endpoint benchmarking.

**Usage**:
```bash
python load_tests/performance_benchmarks.py --host http://localhost:8000 --iterations 100
```

## Running Load Tests

### Prerequisites

1. **Test Environment**
   ```bash
   # Ensure services are running
   docker-compose up -d

   # Verify services
   curl http://localhost:8000/health
   ```

2. **Seed Test Data**
   ```bash
   # Import sample ballot data
   python backend/scripts/import_sample_data.py

   # Create test users
   python backend/scripts/create_test_users.py --count 100
   ```

### Local Load Testing

**Basic Test (Web UI)**:
```bash
cd /path/to/civicq
locust -f load_tests/locustfile.py --host=http://localhost:8000
```

Then:
1. Open http://localhost:8089
2. Set number of users (start with 100)
3. Set spawn rate (users/second, start with 10)
4. Click "Start Swarming"

**Headless Mode (CI/CD)**:
```bash
locust -f load_tests/locustfile.py \
  --host=http://localhost:8000 \
  --users 1000 \
  --spawn-rate 10 \
  --run-time 10m \
  --headless \
  --csv results/test_results
```

### Distributed Load Testing

For testing higher loads, run Locust in distributed mode.

**Master Node**:
```bash
locust -f load_tests/locustfile.py \
  --master \
  --expect-workers 4
```

**Worker Nodes** (run on separate machines):
```bash
locust -f load_tests/locustfile.py \
  --worker \
  --master-host=<master-ip>
```

### Cloud Load Testing

**Using AWS EC2**:

1. **Launch EC2 Instances**
   - Master: t3.medium (2 vCPU, 4 GB RAM)
   - Workers: t3.large x 4 (2 vCPU, 8 GB RAM each)

2. **Setup Script**:
   ```bash
   #!/bin/bash
   # Install Locust on all instances
   sudo apt-get update
   sudo apt-get install -y python3-pip
   pip3 install locust==2.20.0

   # Copy test files
   scp -r load_tests ubuntu@<instance-ip>:~/

   # On master
   locust -f ~/load_tests/locustfile.py --master --expect-workers 4

   # On each worker
   locust -f ~/load_tests/locustfile.py --worker --master-host=<master-private-ip>
   ```

3. **Run Test**:
   - Access master UI: http://<master-public-ip>:8089
   - Configure: 10,000 users, spawn rate 100
   - Duration: 30 minutes

## Performance Benchmarks

### Running Benchmarks

```bash
# Basic benchmark suite
python load_tests/performance_benchmarks.py

# Custom configuration
python load_tests/performance_benchmarks.py \
  --host http://api.civicq.org \
  --iterations 200 \
  --output results.json
```

### Benchmark Output

```
================================================================================
CivicQ Performance Benchmark Suite
================================================================================

Testing GET /health (50 iterations)...
  Success Rate: 100.0%
  Min: 12.45ms
  Avg: 18.23ms
  Median: 17.50ms
  P95: 24.10ms
  P99: 26.80ms
  Max: 28.90ms

Testing GET /api/ballots/los-angeles (100 iterations)...
  Success Rate: 100.0%
  Min: 45.20ms
  Avg: 62.15ms
  Median: 58.40ms
  P95: 85.30ms
  P99: 92.10ms
  Max: 98.50ms

...

PERFORMANCE SUMMARY
--------------------------------------------------------------------------------
Endpoint                                          Avg (ms)    P95 (ms)    Success %
--------------------------------------------------------------------------------
GET /health                                       18.23       24.10       100.0
GET /api/ballots/los-angeles                      62.15       85.30       100.0
GET /api/questions?page=1&limit=20                78.45       120.50      100.0
GET /api/questions/trending?limit=20              95.20       150.30      100.0
--------------------------------------------------------------------------------
OVERALL                                           68.51       95.05       100.0
================================================================================

CHECKING PERFORMANCE TARGETS
--------------------------------------------------------------------------------
PASS: GET /health
PASS: GET /api/ballots/los-angeles
PASS: GET /api/questions?page=1&limit=20
FAIL: GET /api/questions/trending?limit=20
  - Avg (95.20ms) approaching limit (target: <100ms for complex queries)
  - P95 (150.30ms) approaching limit
--------------------------------------------------------------------------------
Most performance targets met. Review failures above.
================================================================================
```

## Interpreting Results

### Key Metrics

1. **Response Time**
   - **Average**: Typical response time
   - **Median**: 50th percentile
   - **P95**: 95th percentile (most users experience this or better)
   - **P99**: 99th percentile (worst case for most users)
   - **Max**: Worst response time

2. **Throughput**
   - **Requests/Second (RPS)**: Total requests handled per second
   - **Users**: Number of concurrent simulated users
   - **Spawn Rate**: Rate at which users are added

3. **Failure Rate**
   - **Percentage**: Requests that failed (4xx, 5xx, timeouts)
   - **Target**: < 0.1% (999 out of 1000 requests succeed)

4. **Resource Usage**
   - **CPU**: Should stay < 80% under load
   - **Memory**: Should be stable (no leaks)
   - **Database Connections**: Should not hit pool limit
   - **Cache Hit Rate**: Should be > 80%

### Reading Locust Dashboard

**Statistics Tab**:
- Green: Healthy (low failure rate, good response times)
- Yellow: Degrading (increasing response times)
- Red: Failing (high error rate)

**Charts Tab**:
- Total Requests per Second
- Response Times (median, 95th percentile)
- Number of Users

**Failures Tab**:
- Types of errors
- Frequency
- Affected endpoints

**Exceptions Tab**:
- Python exceptions during test
- Usually indicates test script issues

## Performance Targets

### Response Time Targets

| Endpoint Type | Avg | P95 | P99 | Max |
|---------------|-----|-----|-----|-----|
| Simple GET (health, single resource) | < 50ms | < 100ms | < 150ms | < 200ms |
| List endpoints (paginated) | < 100ms | < 200ms | < 300ms | < 500ms |
| Complex queries (trending, analytics) | < 200ms | < 500ms | < 1000ms | < 2000ms |
| POST/PUT (data modification) | < 150ms | < 300ms | < 500ms | < 1000ms |
| Video upload | < 5s | < 10s | < 15s | < 30s |

### Throughput Targets

| User Load | Target RPS | Notes |
|-----------|------------|-------|
| 100 users | 500 RPS | Typical traffic |
| 1,000 users | 5,000 RPS | Peak traffic |
| 10,000 users | 50,000 RPS | Maximum capacity |

### Resource Targets

| Resource | Target | Critical Threshold |
|----------|--------|--------------------|
| CPU Usage | < 70% | 90% |
| Memory Usage | < 75% | 85% |
| Database Connections | < 80% of pool | 95% of pool |
| Cache Hit Rate | > 80% | < 70% |
| Disk I/O | < 70% | 90% |

## Test Scenarios

### Scenario 1: Normal Load (Baseline)

**Goal**: Establish baseline performance

```bash
locust -f load_tests/locustfile.py \
  --users 100 \
  --spawn-rate 10 \
  --run-time 10m \
  --headless
```

**Expected**:
- RPS: ~500
- Avg response time: < 100ms
- Failure rate: < 0.1%

### Scenario 2: Peak Load

**Goal**: Test during expected peak (election day)

```bash
locust -f load_tests/locustfile.py \
  --users 1000 \
  --spawn-rate 50 \
  --run-time 20m \
  --headless
```

**Expected**:
- RPS: ~5,000
- Avg response time: < 150ms
- Failure rate: < 0.5%

### Scenario 3: Stress Test

**Goal**: Find breaking point

```bash
locust -f load_tests/locustfile.py \
  --users 10000 \
  --spawn-rate 100 \
  --run-time 30m \
  --headless
```

**Expected**:
- RPS: ~50,000
- Avg response time: < 300ms
- Failure rate: < 1%

### Scenario 4: Spike Test

**Goal**: Test sudden traffic increase

```bash
# Start low
locust -f load_tests/locustfile.py \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --headless

# Then spike to high
# (stop and restart with higher users)
locust -f load_tests/locustfile.py \
  --users 5000 \
  --spawn-rate 500 \
  --run-time 10m \
  --headless
```

### Scenario 5: Endurance Test

**Goal**: Test system stability over time

```bash
locust -f load_tests/locustfile.py \
  --users 500 \
  --spawn-rate 25 \
  --run-time 4h \
  --headless
```

**Monitor for**:
- Memory leaks (increasing memory over time)
- Connection pool exhaustion
- Cache effectiveness over time
- Log file growth

## Troubleshooting

### High Response Times

**Symptoms**: Response times > targets

**Possible Causes**:
1. Database query inefficiency
2. Missing indexes
3. N+1 queries
4. Low cache hit rate
5. CPU/memory constraints

**Solutions**:
```bash
# Check database queries
# Enable query logging
DATABASE_ECHO=true python backend/main.py

# Check cache hit rate
curl http://localhost:8000/api/admin/metrics | jq '.cache.hit_rate'

# Profile slow endpoints
python -m cProfile -s cumtime backend/main.py
```

### High Failure Rate

**Symptoms**: > 1% request failures

**Possible Causes**:
1. Database connection pool exhausted
2. Rate limiting too aggressive
3. Application errors
4. Timeout too short

**Solutions**:
```bash
# Check logs
docker-compose logs backend | grep ERROR

# Check database connections
# In PostgreSQL:
SELECT count(*) FROM pg_stat_activity;

# Increase connection pool
# In config.py:
DATABASE_POOL_SIZE = 50
DATABASE_MAX_OVERFLOW = 100
```

### Memory Leaks

**Symptoms**: Increasing memory usage over time

**Solutions**:
```bash
# Use memory profiler
pip install memory-profiler
python -m memory_profiler backend/main.py

# Monitor with htop
htop -p $(pgrep -f "uvicorn")

# Check for unclosed connections
# Review code for:
# - Unclosed database sessions
# - Unclosed file handles
# - Large cached objects
```

### Cache Issues

**Symptoms**: Low cache hit rate (< 70%)

**Solutions**:
```bash
# Check Redis
redis-cli info stats

# Monitor cache keys
redis-cli --scan --pattern "civicq:*" | head -20

# Check TTLs
redis-cli ttl "civicq:ballot:1"

# Review cache logic
# - Are keys consistent?
# - Are TTLs appropriate?
# - Are invalidations too aggressive?
```

## Best Practices

1. **Start Small**: Begin with low load and gradually increase
2. **Warm Up**: Run warm-up period before measuring
3. **Realistic Scenarios**: Simulate actual user behavior
4. **Monitor Everything**: Track backend, database, cache, CDN
5. **Repeat Tests**: Run multiple times for consistency
6. **Test in Production-Like Environment**: Same infrastructure
7. **Gradual Load Increase**: Use spawn rate to avoid spikes
8. **Document Results**: Track performance over time
9. **Test Before Deployment**: Make it part of CI/CD
10. **Learn from Each Test**: Adjust and improve

## Continuous Load Testing

### CI/CD Integration

```yaml
# .github/workflows/load-test.yml
name: Load Testing

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:  # Manual trigger

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r load_tests/requirements.txt

      - name: Run load test
        run: |
          locust -f load_tests/locustfile.py \
            --host=${{ secrets.TEST_API_URL }} \
            --users 100 \
            --spawn-rate 10 \
            --run-time 5m \
            --headless \
            --csv results/load_test

      - name: Check performance targets
        run: |
          python load_tests/check_performance.py results/load_test_stats.csv

      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: load-test-results
          path: results/
```

## Summary

Load testing ensures CivicQ can:
- Handle 10,000+ concurrent users
- Maintain < 200ms average response time
- Achieve > 80% cache hit rate
- Sustain load for extended periods
- Recover gracefully from spikes

**Regular load testing is essential** for maintaining performance as the application grows.
