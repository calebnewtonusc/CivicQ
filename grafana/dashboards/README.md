# CivicQ Grafana Dashboards

This directory contains pre-configured Grafana dashboards for monitoring CivicQ.

## Available Dashboards

### 1. System Overview (`system-overview.json`)
Comprehensive system health monitoring:
- Service status (API, PostgreSQL, Redis, Celery)
- CPU, memory, and disk usage
- Network traffic
- System resource alerts

### 2. API Performance (`api-performance.json`)
API request and response monitoring:
- Request rate (req/sec)
- Error rates (4xx, 5xx)
- Response time percentiles (P50, P95, P99)
- Top slowest endpoints
- Requests by endpoint
- 24-hour statistics

### 3. Database Performance (`database-performance.json`)
PostgreSQL monitoring:
- Connection pool usage
- Query duration by type
- Transaction rates (commits/rollbacks)
- Database size growth
- Cache hit ratio
- Deadlock detection
- Slow query tracking

### 4. Celery Performance (create manually or use template)
Background job monitoring:
- Active workers
- Queue length by queue
- Task execution time
- Task success/failure rates
- Worker health

### 5. User Activity (create manually or use template)
Business metrics:
- User registrations
- Active users
- Questions submitted
- Votes cast
- Video uploads
- City engagement

## Importing Dashboards

These dashboards are automatically loaded by Grafana when using the docker-compose setup.

### Manual Import:
1. Open Grafana (default: http://localhost:3001)
2. Login with admin credentials
3. Click '+' → Import
4. Upload JSON file or paste JSON content
5. Select Prometheus datasource
6. Click Import

## Customization

All dashboards can be edited through the Grafana UI:
1. Open dashboard
2. Click settings (gear icon)
3. Make changes
4. Save dashboard
5. Export JSON to persist changes

## Alert Configuration

Alerts are configured in:
- Prometheus: `/prometheus/alerts.yml`
- AlertManager: `/prometheus/alertmanager.yml`

Dashboard-level alerts can also be configured in Grafana UI.
