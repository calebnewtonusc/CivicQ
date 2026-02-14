# CivicQ Monitoring and Observability Guide

Complete guide to monitoring, observability, and incident response for CivicQ production deployment.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Components](#components)
- [Setup](#setup)
- [Configuration](#configuration)
- [Dashboards](#dashboards)
- [Alerts](#alerts)
- [Health Checks](#health-checks)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Overview

CivicQ uses a comprehensive monitoring stack that includes:

- **Sentry** - Error tracking and performance monitoring
- **Prometheus** - Metrics collection and time-series database
- **Grafana** - Visualization and dashboards
- **AlertManager** - Alert routing and notifications
- **Health Checks** - Automated service monitoring
- **Structured Logging** - JSON-formatted logs for analysis

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CivicQ Application                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ FastAPI  │  │PostgreSQL│  │  Redis   │  │  Celery  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
   ┌────────────────────────────────────────────────────┐
   │              Prometheus Exporters                   │
   │  • FastAPI metrics endpoint (/metrics)             │
   │  • PostgreSQL exporter                              │
   │  • Redis exporter                                   │
   │  • Celery exporter                                  │
   │  • Node exporter (system metrics)                   │
   └────────────────────┬───────────────────────────────┘
                        │
                        ▼
   ┌────────────────────────────────────────────────────┐
   │                  Prometheus                         │
   │  • Scrapes metrics every 15s                       │
   │  • Stores time-series data                         │
   │  • Evaluates alert rules                           │
   └────────────────────┬───────────────────────────────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐
   │ Grafana  │  │AlertMgr  │  │  Sentry  │
   │Dashboard │  │ Alerts   │  │  Errors  │
   └──────────┘  └──────────┘  └──────────┘
```

## Components

### 1. Sentry Integration

**Backend** (`app/core/sentry.py`):
- Automatic exception tracking
- Performance monitoring (APM)
- Breadcrumbs for debugging
- User context tracking
- Release tracking
- Integrations: FastAPI, SQLAlchemy, Redis, Celery

**Frontend** (`src/utils/sentry.ts`):
- React error boundaries
- Performance monitoring
- Session replay
- User feedback widget
- Automatic error reporting

**Configuration**:
```bash
# Backend .env
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
SENTRY_RELEASE=1.0.0
ENVIRONMENT=production

# Frontend .env
REACT_APP_SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
REACT_APP_VERSION=1.0.0
REACT_APP_ENVIRONMENT=production
```

### 2. Prometheus Metrics

**Custom Metrics** (`app/core/metrics.py`):
- HTTP requests (total, duration, status codes)
- Business metrics (questions, votes, videos)
- Database queries (duration, errors)
- Celery tasks (duration, queue length)
- External API calls (duration, errors)
- S3/R2 operations
- Redis operations

**Metrics Endpoint**: `http://localhost:8000/metrics`

**Usage Example**:
```python
from app.core.metrics import questions_submitted_total
from app.core.monitoring import monitor_database_query

# Track business event
questions_submitted_total.labels(
    city_id="los-angeles",
    contest_type="mayor"
).inc()

# Monitor database query
with monitor_database_query("select", "SELECT * FROM users"):
    result = db.execute(query)
```

### 3. Grafana Dashboards

Pre-configured dashboards in `/grafana/dashboards/`:

1. **System Overview** - Overall system health
2. **API Performance** - Request rates, latency, errors
3. **Database Performance** - Queries, connections, cache hits
4. **Celery Dashboard** - Task queues, worker health
5. **User Activity** - Registrations, engagement metrics

**Access**: http://localhost:3001 (default credentials: admin/admin)

### 4. Health Checks

**Endpoints**:
- `GET /health` - Basic liveness check
- `GET /health/ready` - Readiness check (all dependencies)
- `GET /health/db` - Database connectivity
- `GET /health/redis` - Redis connectivity
- `GET /health/celery` - Celery worker status
- `GET /health/storage` - S3/R2 connectivity
- `GET /health/system` - System resources (CPU, memory, disk)
- `GET /health/detailed` - All checks combined

**Script**: `./scripts/monitoring/check-health.sh`

```bash
# Run health check
./scripts/monitoring/check-health.sh

# Check specific URL
./scripts/monitoring/check-health.sh --url https://api.civicq.com

# JSON output
./scripts/monitoring/check-health.sh --json
```

### 5. Structured Logging

**Configuration** (`app/core/logging_config.py`):
- JSON format in production
- Request ID tracking
- User context
- Performance logging
- Log levels: DEBUG, INFO, WARNING, ERROR

**Usage**:
```python
import logging
logger = logging.getLogger(__name__)

logger.info("User registered", extra={
    "user_id": user.id,
    "city_id": user.city_id,
    "duration_ms": 123.45
})
```

## Setup

### Local Development

1. **Install dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Add your Sentry DSN and other configs
```

3. **Run application**:
```bash
uvicorn app.main:app --reload
```

4. **Access monitoring**:
- Metrics: http://localhost:8000/metrics
- Health: http://localhost:8000/health

### Production Setup

1. **Deploy monitoring stack**:
```bash
cd prometheus
docker-compose -f docker-compose.monitoring.yml up -d
```

This starts:
- Prometheus (port 9090)
- Grafana (port 3001)
- AlertManager (port 9093)
- Node Exporter (port 9100)
- PostgreSQL Exporter (port 9187)
- Redis Exporter (port 9121)
- Celery Exporter (port 9808)
- Blackbox Exporter (port 9115)

2. **Configure alerts**:
```bash
# Edit alert rules
vim prometheus/alerts.yml

# Edit alert routing
vim prometheus/alertmanager.yml

# Set environment variables
export SLACK_WEBHOOK_URL="https://hooks.slack.com/..."
export PAGERDUTY_SERVICE_KEY="..."
```

3. **Set up uptime monitoring**:
```bash
# Run continuously
./scripts/monitoring/uptime-monitor.sh --continuous \
  --interval 60 \
  --webhook $SLACK_WEBHOOK_URL
```

## Configuration

### Environment Variables

**Backend** (`.env`):
```bash
# Sentry
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
SENTRY_RELEASE=1.0.0

# Monitoring
ENABLE_METRICS=true
ENABLE_SLOW_QUERY_DETECTION=true  # Requires pg_stat_statements

# Logging
LOG_LEVEL=INFO
```

**Prometheus** (`prometheus/prometheus.yml`):
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'civicq-api'
    static_configs:
      - targets: ['civicq-api:8000']
```

**AlertManager** (`prometheus/alertmanager.yml`):
```yaml
receivers:
  - name: 'critical-alerts'
    slack_configs:
      - api_url: '${SLACK_WEBHOOK_URL}'
        channel: '#civicq-alerts-critical'
    pagerduty_configs:
      - service_key: '${PAGERDUTY_SERVICE_KEY}'
```

### Database Monitoring Setup

Enable PostgreSQL `pg_stat_statements` for slow query detection:

```sql
-- Add to postgresql.conf
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.track = all
pg_stat_statements.max = 10000

-- Restart PostgreSQL, then create extension
CREATE EXTENSION pg_stat_statements;
```

## Dashboards

### Creating Custom Dashboards

1. Open Grafana: http://localhost:3001
2. Click '+' → Dashboard
3. Add panel
4. Configure query:

**Example: Request rate**
```promql
sum(rate(civicq_http_requests_total[5m])) by (endpoint)
```

**Example: P95 response time**
```promql
histogram_quantile(0.95,
  sum(rate(civicq_http_request_duration_seconds_bucket[5m])) by (le, endpoint)
)
```

5. Save dashboard
6. Export JSON and save to `/grafana/dashboards/`

### Dashboard Annotations

Add deployment markers:
```bash
curl -X POST http://localhost:3001/api/annotations \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Deployed version 1.2.0",
    "tags": ["deployment"],
    "time": '$(date +%s000)'
  }'
```

## Alerts

### Alert Hierarchy

**Critical Alerts** (PagerDuty + Slack + Email):
- Service down (API, database, Redis)
- High error rate (>5%)
- Disk space critical (<10%)
- Memory critical (<10%)
- No Celery workers

**Warning Alerts** (Slack):
- Slow API responses (P95 >2s)
- Slow database queries (P95 >1s)
- Celery queue backup (>100 tasks)
- High CPU usage (>80%)
- High memory usage (>85%)

**Business Alerts** (Slack + Email to product team):
- User activity drop (>50% decrease)
- High question rejection rate (>50%)
- Moderation queue backup (>50 pending)

### Alert Configuration

**Define alert rule** (`prometheus/alerts.yml`):
```yaml
- alert: HighErrorRate
  expr: |
    sum(rate(civicq_http_requests_total{status=~"5.."}[5m]))
    / sum(rate(civicq_http_requests_total[5m])) > 0.05
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "High error rate detected"
    description: "Error rate is {{ $value | humanizePercentage }}"
```

**Route alert** (`prometheus/alertmanager.yml`):
```yaml
routes:
  - match:
      severity: critical
    receiver: 'critical-alerts'
    repeat_interval: 3h
```

### Silencing Alerts

During maintenance:
```bash
# Silence all alerts for 2 hours
amtool silence add \
  --comment "Planned maintenance" \
  --duration 2h \
  alertname=~".*"
```

## Health Checks

### Kubernetes Probes

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 15
  periodSeconds: 5
```

### External Monitoring

Configure UptimeRobot, Pingdom, or similar:
- **URL**: https://civicq.com/health/ready
- **Interval**: 5 minutes
- **Alert on**: HTTP status ≠ 200
- **Alert via**: Email, SMS, Slack

## Troubleshooting

### High Error Rate

1. Check Sentry for error details
2. View recent deployments in Grafana
3. Check logs for patterns:
```bash
# Recent errors
kubectl logs deployment/civicq-api --tail=100 | grep ERROR

# Find error patterns
kubectl logs deployment/civicq-api | jq 'select(.levelname=="ERROR")' | \
  jq -r '.message' | sort | uniq -c | sort -rn
```

4. Check API endpoint performance:
```promql
topk(10,
  rate(civicq_http_requests_total{status=~"5.."}[5m])
)
```

### Slow Queries

1. Check database dashboard in Grafana
2. Find slow queries:
```sql
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 1000
ORDER BY mean_exec_time DESC
LIMIT 10;
```

3. Use EXPLAIN ANALYZE:
```sql
EXPLAIN ANALYZE
SELECT * FROM questions WHERE city_id = 'los-angeles';
```

4. Check for N+1 queries in logs

### Memory Issues

1. Check system dashboard
2. Analyze memory usage:
```bash
# Container memory
docker stats civicq-api

# Python memory profiling
python -m memory_profiler app/main.py
```

3. Check for memory leaks in Sentry

### Celery Queue Backup

1. Check Celery dashboard
2. Inspect queue:
```python
from celery import Celery
app = Celery('app')
inspect = app.control.inspect()
print(inspect.active_queues())
```

3. Check worker logs:
```bash
docker logs civicq-celery-worker
```

4. Scale workers if needed:
```bash
docker-compose up -d --scale celery-worker=4
```

## Best Practices

### 1. Metric Naming

Follow Prometheus conventions:
- Use snake_case: `civicq_http_requests_total`
- Include units: `_seconds`, `_bytes`, `_total`
- Use labels for dimensions: `{city_id="la", status="200"}`

### 2. Alert Fatigue

- Set appropriate thresholds
- Use `for` clause to avoid flapping
- Implement inhibition rules
- Route alerts appropriately
- Regular alert review and tuning

### 3. Dashboard Organization

- One dashboard per service/component
- Include time range selector
- Add variable filters (environment, city, etc.)
- Use consistent colors and naming
- Add descriptions and documentation links

### 4. Log Management

- Use structured logging (JSON)
- Include request IDs
- Add user context (when appropriate)
- Set log retention policies
- Index critical fields

### 5. Performance Monitoring

- Track all external API calls
- Monitor database query performance
- Set SLOs (Service Level Objectives):
  - API latency P95 < 500ms
  - Error rate < 1%
  - Uptime > 99.9%

### 6. Security

- Disable metrics endpoint in production (use auth)
- Don't log sensitive data (passwords, tokens)
- Redact PII in Sentry
- Use HTTPS for all monitoring services
- Restrict access to Grafana/Prometheus

### 7. Cost Optimization

- Adjust scrape intervals based on needs
- Set appropriate retention periods
- Use recording rules for expensive queries
- Sample high-cardinality metrics
- Archive old logs to cheaper storage

## Next Steps

1. **Set up alerts**: Configure Slack/PagerDuty webhooks
2. **Create runbooks**: Document incident response procedures
3. **Set SLOs**: Define service level objectives
4. **Implement on-call**: Set up rotation schedule
5. **Regular reviews**: Weekly dashboard review, monthly alert tuning

## Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Sentry Documentation](https://docs.sentry.io/)
- [RUNBOOK.md](./RUNBOOK.md) - Incident response procedures
- [ALERT_REFERENCE.md](./ALERT_REFERENCE.md) - Alert definitions and actions
