# CivicQ Monitoring and Observability Infrastructure - Complete Implementation

Complete production-ready monitoring and observability infrastructure for CivicQ deployment.

## Implementation Summary

A comprehensive monitoring stack has been built for CivicQ, covering error tracking, performance monitoring, metrics collection, health checks, alerting, and incident response.

## Components Delivered

### 1. Error Tracking (Sentry)

#### Backend Integration
- **File**: `/backend/app/core/sentry.py` (Enhanced)
- **Features**:
  - FastAPI integration with automatic request tracking
  - SQLAlchemy query monitoring
  - Redis operation tracking
  - Celery task monitoring
  - Custom error fingerprinting
  - User context tracking
  - Breadcrumb filtering
  - Release tracking

#### Frontend Integration
- **File**: `/frontend/src/utils/sentry.ts` (New)
- **Features**:
  - React error boundaries
  - Session replay
  - Performance monitoring
  - User feedback widget
  - Automatic error reporting
  - Browser tracing integration

- **File**: `/frontend/src/components/ErrorBoundary.tsx` (Enhanced)
- **Features**:
  - Sentry-integrated error boundaries
  - User-friendly error pages
  - Report feedback functionality
  - Development error details

#### Configuration
```bash
# Backend
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
SENTRY_RELEASE=1.0.0

# Frontend
REACT_APP_SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
```

### 2. Application Performance Monitoring (APM)

#### Monitoring Core
- **File**: `/backend/app/core/monitoring.py` (New)
- **Features**:
  - Context managers for automatic timing and error tracking
  - Database query monitoring with slow query detection
  - External API call monitoring
  - S3/R2 operation tracking
  - Redis operation monitoring
  - N+1 query detection
  - Comprehensive health checkers

#### Usage Example
```python
from app.core.monitoring import monitor_database_query, monitor_external_api

# Monitor database query
with monitor_database_query("select", "SELECT * FROM users"):
    result = db.execute(query)

# Monitor external API
with monitor_external_api("google_civic", "/elections"):
    response = httpx.get(url)
```

### 3. Metrics (Prometheus + Grafana)

#### Prometheus Integration
- **File**: `/backend/app/core/metrics.py` (Existing - already had metrics)
- **Custom Metrics**:
  - HTTP requests (total, duration, status codes)
  - Business metrics (questions, votes, videos, users)
  - Database queries (duration, errors, connection pool)
  - Celery tasks (duration, queue length, success/failure)
  - External API calls (duration, errors)
  - S3 operations
  - Redis operations
  - System resources

#### Metrics Middleware
- **File**: `/backend/app/middleware/metrics.py` (New)
- **Features**:
  - Automatic HTTP request tracking
  - Path normalization (removes IDs/UUIDs)
  - Slow request logging
  - Sentry integration
  - Performance headers

#### Prometheus Configuration
- **Files**:
  - `/prometheus/prometheus.yml` - Main configuration
  - `/prometheus/alerts.yml` - Alert rules
  - `/prometheus/alertmanager.yml` - Alert routing
  - `/prometheus/blackbox.yml` - External endpoint monitoring
  - `/prometheus/docker-compose.monitoring.yml` - Full monitoring stack

**Exporters Configured**:
- FastAPI application (`/metrics` endpoint)
- PostgreSQL exporter (port 9187)
- Redis exporter (port 9121)
- Celery exporter (port 9808)
- Node exporter (port 9100)
- Blackbox exporter (port 9115)

#### Grafana Dashboards
- **Directory**: `/grafana/dashboards/`
- **Dashboards**:
  1. `system-overview.json` - System health, CPU, memory, disk, network
  2. `api-performance.json` - Request rates, error rates, latency, top endpoints
  3. `database-performance.json` - Queries, connections, cache hits, deadlocks
  4. Additional dashboards can be created for Celery and user activity

- **Provisioning**:
  - `/grafana/provisioning/datasources/prometheus.yml` - Auto-configure Prometheus
  - `/grafana/provisioning/dashboards/dashboard-provider.yml` - Auto-load dashboards

### 4. Health Checks

#### Backend Health Endpoints
- **File**: `/backend/app/api/health.py` (New)
- **Endpoints**:
  - `GET /health` - Basic liveness (always returns 200 if running)
  - `GET /health/ready` - Readiness (checks all dependencies)
  - `GET /health/db` - Database connectivity and performance
  - `GET /health/redis` - Redis connectivity and memory usage
  - `GET /health/celery` - Celery worker status
  - `GET /health/storage` - S3/R2 connectivity
  - `GET /health/system` - System resources (CPU, memory, disk)
  - `GET /health/detailed` - All checks combined

#### Health Check Scripts
- **File**: `/scripts/monitoring/check-health.sh` (New)
- **Features**:
  - Comprehensive health checks across all services
  - JSON or human-readable output
  - Verbose mode for debugging
  - Exit codes for automation

**Usage**:
```bash
# Basic check
./scripts/monitoring/check-health.sh

# Check production
./scripts/monitoring/check-health.sh --url https://api.civicq.com

# JSON output for automation
./scripts/monitoring/check-health.sh --json
```

#### Uptime Monitor
- **File**: `/scripts/monitoring/uptime-monitor.sh` (New)
- **Features**:
  - Continuous monitoring
  - Slack/email alerts on state change
  - Tracks service status history
  - Configurable check interval

**Usage**:
```bash
# Single check
./scripts/monitoring/uptime-monitor.sh

# Continuous monitoring
./scripts/monitoring/uptime-monitor.sh --continuous \
  --interval 60 \
  --webhook $SLACK_WEBHOOK_URL \
  --email ops@civicq.com
```

### 5. Alerts

#### Alert Rules
- **File**: `/prometheus/alerts.yml` (New)
- **Alert Categories**:

**Critical Alerts** (PagerDuty + Slack + Email):
- ServiceDown - API not responding
- HighErrorRate - >5% error rate
- DatabaseDown - Cannot connect to PostgreSQL
- RedisDown - Cannot connect to Redis
- NoCeleryWorkers - No active workers
- DiskSpaceCritical - <10% disk space
- MemoryCritical - <10% available memory
- SSLCertificateExpiringSoon - <7 days to expiry

**Warning Alerts** (Slack):
- SlowAPIResponses - P95 >2s
- SlowDatabaseQueries - P95 >1s
- CeleryQueueBackup - >100 pending tasks
- HighCeleryFailureRate - >10% failure rate
- VideoProcessingFailures - Processing errors
- HighCPUUsage - >80% CPU
- HighMemoryUsage - >85% memory
- DiskSpaceWarning - <20% disk space
- RedisMemoryHigh - >90% Redis memory
- DatabaseConnectionsHigh - >80% connection pool
- ExternalAPIsSlow - P95 >5s
- ExternalAPIErrors - >10% error rate

**Business Alerts** (Slack + Email to product team):
- UserActivityDrop - >50% decrease in logins
- HighQuestionRejectionRate - >50% rejection rate
- ModerationQueueBackup - >50 pending questions

#### Alert Manager
- **File**: `/prometheus/alertmanager.yml` (New)
- **Features**:
  - Alert routing by severity
  - Multiple notification channels (PagerDuty, Slack, Email)
  - Inhibition rules (suppress redundant alerts)
  - Customizable templates
  - Alert grouping and deduplication

**Configuration Required**:
```bash
# Set environment variables
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx
PAGERDUTY_SERVICE_KEY=xxx
SMTP_HOST=smtp.sendgrid.net
SMTP_USER=apikey
SMTP_PASSWORD=xxx
```

### 6. Structured Logging

#### Logging Configuration
- **File**: `/backend/app/core/logging_config.py` (Existing - already comprehensive)
- **Features**:
  - JSON format in production
  - Request ID tracking
  - User context
  - Performance logging
  - Configurable log levels per module

### 7. Application Integration

#### Main Application
- **File**: `/backend/app/main.py` (Enhanced)
- **Changes**:
  - Import Sentry initialization
  - Import metrics middleware
  - Import health router
  - Add Sentry initialization on startup
  - Add metrics middleware to app
  - Add `/metrics` endpoint
  - Include health router
  - Set application info for Prometheus
  - Log monitoring status on startup

#### Configuration
- **File**: `/backend/app/core/config.py` (Enhanced)
- **New Settings**:
  - `SENTRY_RELEASE` - Release tracking
  - `ENABLE_METRICS` - Toggle metrics collection
  - `ENABLE_SLOW_QUERY_DETECTION` - Toggle slow query detection

#### Dependencies
- **File**: `/backend/requirements.txt` (Updated)
- **New Dependencies**:
  - `prometheus-client==0.20.0` - Prometheus metrics
  - `psutil==5.9.8` - System resource monitoring

## Documentation

### Complete Guides Created

1. **MONITORING_GUIDE.md** (New)
   - Complete monitoring setup guide
   - Architecture overview
   - Component descriptions
   - Setup instructions (local and production)
   - Configuration reference
   - Dashboard usage
   - Alert configuration
   - Health check usage
   - Troubleshooting guide
   - Best practices

2. **RUNBOOK.md** (New)
   - Emergency contacts
   - Incident response process
   - Common incident procedures:
     - Service down
     - High error rate
     - Database issues
     - Celery queue backup
     - Memory issues
     - SSL certificate expiring
   - Service-specific procedures
   - Rollback procedures
   - Data recovery procedures
   - Communication templates

3. **ALERT_REFERENCE.md** (New)
   - All alert definitions
   - Severity levels
   - Impact descriptions
   - Response procedures
   - Prometheus queries
   - Thresholds and timing
   - Common response patterns
   - Alert tuning guidelines

## Deployment Instructions

### 1. Backend Deployment

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env and add:
# - SENTRY_DSN
# - SENTRY_RELEASE
# - ENABLE_METRICS=true

# 3. Run migrations if needed
alembic upgrade head

# 4. Start application
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Frontend Deployment

```bash
# 1. Configure environment
cd frontend
# Add to .env.production:
# - REACT_APP_SENTRY_DSN
# - REACT_APP_VERSION
# - REACT_APP_ENVIRONMENT=production

# 2. Update App.tsx to initialize Sentry
# Import: import { initSentry } from './utils/sentry';
# Call: initSentry(); (before rendering)

# 3. Build and deploy
npm run build
vercel --prod
```

### 3. Monitoring Stack Deployment

```bash
# 1. Configure environment
cd prometheus
cp .env.example .env
# Add:
# - SLACK_WEBHOOK_URL
# - PAGERDUTY_SERVICE_KEY
# - SMTP credentials
# - Database credentials

# 2. Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

# 3. Verify services
docker-compose ps

# 4. Access services
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001 (admin/admin)
# AlertManager: http://localhost:9093
```

### 4. Health Check Automation

```bash
# 1. Make scripts executable
chmod +x scripts/monitoring/*.sh

# 2. Test health checks
./scripts/monitoring/check-health.sh --url https://api.civicq.com

# 3. Set up cron job for uptime monitoring
crontab -e
# Add:
# */5 * * * * /path/to/scripts/monitoring/check-health.sh --json >> /var/log/civicq-health.log

# 4. Or run as systemd service (for continuous monitoring)
# See systemd service example in MONITORING_GUIDE.md
```

### 5. Kubernetes Deployment

```yaml
# Add to deployment.yaml
spec:
  template:
    spec:
      containers:
      - name: civicq-api
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

## Testing the Setup

### 1. Test Sentry Integration

```bash
# Backend - trigger test error
curl http://localhost:8000/test-error  # Create this endpoint temporarily

# Frontend - throw test error in console
throw new Error("Test Sentry error");
```

Check Sentry dashboard for errors.

### 2. Test Metrics

```bash
# View metrics
curl http://localhost:8000/metrics

# Check Prometheus
# Open http://localhost:9090
# Query: up{job="civicq-api"}

# Check Grafana
# Open http://localhost:3001
# View System Overview dashboard
```

### 3. Test Health Checks

```bash
# All checks
./scripts/monitoring/check-health.sh

# Specific checks
curl http://localhost:8000/health
curl http://localhost:8000/health/ready
curl http://localhost:8000/health/db
curl http://localhost:8000/health/redis
curl http://localhost:8000/health/celery
```

### 4. Test Alerts

```bash
# Trigger test alert in Prometheus
# Open http://localhost:9090/alerts
# View active alerts

# Test alert notification
amtool alert add alertname="TestAlert" --alertmanager.url=http://localhost:9093

# Check Slack/email for notification
```

## Maintenance Tasks

### Daily
- Monitor Grafana dashboards
- Check Sentry for new errors
- Review critical alerts

### Weekly
- Review dashboard metrics trends
- Check for alert fatigue
- Update on-call schedule

### Monthly
- Review and tune alert thresholds
- Update runbooks with new learnings
- Review Sentry error trends
- Check monitoring stack updates

### Quarterly
- Review SLOs and adjust if needed
- Audit monitoring coverage
- Update documentation
- Review and archive old logs

## Key Metrics to Watch

### Service Health
- Uptime percentage (target: 99.9%)
- Error rate (target: <1%)
- P95 response time (target: <500ms)

### Business Metrics
- Daily active users
- Questions submitted per day
- Videos uploaded per day
- User engagement rate

### System Metrics
- CPU usage (alert: >80%)
- Memory usage (alert: >85%)
- Disk usage (alert: >90%)
- Database connections (alert: >80% of max)

### Performance Metrics
- API P95 latency (target: <500ms)
- Database P95 query time (target: <100ms)
- Celery queue length (alert: >100)
- Video processing time (target: <2 minutes)

## Next Steps

1. **Configure Sentry projects**
   - Create backend project in Sentry
   - Create frontend project in Sentry
   - Add DSNs to environment variables

2. **Set up notification channels**
   - Create Slack channels (#civicq-alerts-critical, #civicq-alerts-warning)
   - Configure Slack webhooks
   - Set up PagerDuty service
   - Configure email distribution lists

3. **Deploy monitoring stack**
   - Deploy to production environment
   - Configure firewall rules
   - Set up SSL certificates
   - Test all integrations

4. **Create on-call schedule**
   - Define rotation schedule
   - Add to PagerDuty
   - Document escalation procedures

5. **Train team**
   - Review runbooks with team
   - Practice incident response
   - Document common issues
   - Schedule regular drills

## Files Created/Modified

### New Files
- `/backend/app/core/monitoring.py` - Monitoring core utilities
- `/backend/app/middleware/metrics.py` - Metrics middleware
- `/backend/app/api/health.py` - Health check endpoints
- `/frontend/src/utils/sentry.ts` - Frontend Sentry integration
- `/prometheus/prometheus.yml` - Prometheus configuration
- `/prometheus/alerts.yml` - Alert rules
- `/prometheus/alertmanager.yml` - Alert routing
- `/prometheus/blackbox.yml` - Blackbox exporter config
- `/prometheus/docker-compose.monitoring.yml` - Monitoring stack
- `/grafana/provisioning/datasources/prometheus.yml` - Grafana datasource
- `/grafana/provisioning/dashboards/dashboard-provider.yml` - Dashboard provider
- `/grafana/dashboards/system-overview.json` - System dashboard
- `/grafana/dashboards/api-performance.json` - API dashboard
- `/grafana/dashboards/database-performance.json` - Database dashboard
- `/grafana/dashboards/README.md` - Dashboard documentation
- `/scripts/monitoring/check-health.sh` - Health check script
- `/scripts/monitoring/uptime-monitor.sh` - Uptime monitoring script
- `/MONITORING_GUIDE.md` - Complete monitoring guide
- `/RUNBOOK.md` - Incident response procedures
- `/ALERT_REFERENCE.md` - Alert reference guide
- `/MONITORING_IMPLEMENTATION_COMPLETE.md` - This document

### Enhanced Files
- `/backend/app/core/sentry.py` - Already existed, added missing config
- `/backend/app/core/config.py` - Added monitoring settings
- `/backend/app/main.py` - Integrated monitoring
- `/backend/requirements.txt` - Added monitoring dependencies
- `/frontend/src/components/ErrorBoundary.tsx` - Enhanced with Sentry

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                     User Traffic                              │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│                  Load Balancer / CDN                          │
│              (SSL, DDoS Protection)                           │
└───────────┬──────────────────────────┬────────────────────────┘
            │                          │
            ▼                          ▼
┌─────────────────────┐    ┌──────────────────────┐
│  Frontend (React)   │    │  Backend (FastAPI)   │
│  - Sentry Client    │    │  - Sentry SDK        │
│  - Error Boundary   │    │  - Metrics /metrics  │
│  - Performance      │    │  - Health Checks     │
└─────────────────────┘    └──────────┬───────────┘
                                      │
                ┌─────────────────────┼─────────────────────┐
                │                     │                     │
                ▼                     ▼                     ▼
        ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
        │ PostgreSQL   │    │    Redis     │    │   Celery     │
        │ + Exporter   │    │  + Exporter  │    │  + Exporter  │
        └──────────────┘    └──────────────┘    └──────────────┘
                │                     │                     │
                └─────────────────────┼─────────────────────┘
                                      │
                                      ▼
                            ┌──────────────────┐
                            │   Prometheus     │
                            │ (Metrics Store)  │
                            └────────┬─────────┘
                                     │
                        ┌────────────┼────────────┐
                        │            │            │
                        ▼            ▼            ▼
                ┌──────────┐  ┌───────────┐  ┌─────────┐
                │ Grafana  │  │AlertManager│ │ Sentry  │
                │Dashboard │  │  Alerts    │  │ Errors  │
                └──────────┘  └─────┬─────┘  └─────────┘
                                    │
                        ┌───────────┼───────────┐
                        │           │           │
                        ▼           ▼           ▼
                   ┌────────┐ ┌────────┐ ┌─────────┐
                   │ Slack  │ │PagerDuty│ │ Email  │
                   └────────┘ └────────┘ └─────────┘
```

## Success Criteria

- All health check endpoints return appropriate status codes
- Metrics are being collected and visible in Prometheus
- Grafana dashboards display data correctly
- Alerts trigger appropriately in test scenarios
- Sentry captures frontend and backend errors
- Health check scripts run successfully
- Documentation is complete and accurate

## Conclusion

The CivicQ monitoring and observability infrastructure is now complete and production-ready. This comprehensive setup provides:

- Real-time error tracking and performance monitoring
- Detailed metrics collection and visualization
- Automated health checks and alerting
- Comprehensive incident response procedures
- Complete documentation for operations team

The system is designed to ensure high availability, quick incident response, and proactive issue detection for CivicQ in production.
