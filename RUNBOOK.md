# CivicQ Operations Runbook

Incident response procedures and troubleshooting guide for CivicQ production operations.

## Table of Contents

- [Emergency Contacts](#emergency-contacts)
- [Incident Response Process](#incident-response-process)
- [Common Incidents](#common-incidents)
- [Service-Specific Procedures](#service-specific-procedures)
- [Rollback Procedures](#rollback-procedures)
- [Data Recovery](#data-recovery)

## Emergency Contacts

### On-Call Rotation

- **Primary**: Check PagerDuty schedule
- **Secondary**: Check PagerDuty schedule
- **Escalation**: Engineering Manager

### External Services

- **Hosting**: AWS/Vercel support
- **Database**: RDS support (if applicable)
- **CDN**: Cloudflare support
- **Monitoring**: Sentry support

## Incident Response Process

### 1. Acknowledge

1. Acknowledge alert in PagerDuty/Slack
2. Create incident channel: `#incident-YYYY-MM-DD-description`
3. Update status page (if applicable)

### 2. Assess

1. Check dashboards:
   - Grafana system overview
   - Sentry error dashboard
   - Health check endpoints

2. Determine severity:
   - **SEV1**: Complete service outage, data loss
   - **SEV2**: Partial outage, degraded performance
   - **SEV3**: Minor issue, no immediate user impact

3. Identify affected components

### 3. Mitigate

1. Follow incident-specific procedures (see below)
2. Document actions in incident channel
3. Keep stakeholders updated (every 30 min for SEV1)

### 4. Resolve

1. Verify fix with health checks
2. Monitor for 30 minutes
3. Close incident in PagerDuty
4. Update status page

### 5. Post-Mortem

Within 48 hours of SEV1/SEV2:
1. Write post-mortem document
2. Identify root cause
3. Create action items to prevent recurrence
4. Share with team

## Common Incidents

### Service Down

**Alert**: `ServiceDown`

**Symptoms**:
- Health check returns 5xx or timeout
- Zero traffic on dashboards
- Users report site inaccessible

**Diagnosis**:
```bash
# Check if service is running
./scripts/monitoring/check-health.sh --url https://api.civicq.com

# Check container/pod status
docker ps | grep civicq
# OR
kubectl get pods -l app=civicq-api

# Check logs
docker logs civicq-api --tail=100
# OR
kubectl logs deployment/civicq-api --tail=100
```

**Resolution**:

1. **If container crashed**:
```bash
# Docker
docker-compose restart civicq-api

# Kubernetes
kubectl rollout restart deployment/civicq-api
```

2. **If deployment failed**:
```bash
# Check deployment status
kubectl describe deployment civicq-api

# Check for image pull errors
kubectl get events --sort-by=.lastTimestamp

# Rollback if needed
kubectl rollout undo deployment/civicq-api
```

3. **If infrastructure issue**:
- Check cloud provider status
- Verify DNS configuration
- Check load balancer health

**Prevention**:
- Implement health checks in deployment
- Use readiness/liveness probes
- Set up auto-restart policies

---

### High Error Rate

**Alert**: `HighErrorRate`

**Symptoms**:
- Error rate >5% for 5 minutes
- Spike in 5xx responses
- Errors in Sentry

**Diagnosis**:
```bash
# Check recent deployments
kubectl rollout history deployment/civicq-api

# Check Sentry for error patterns
# https://sentry.io/organizations/civicq/issues/

# Check logs for errors
kubectl logs deployment/civicq-api --tail=1000 | grep ERROR

# Check specific endpoint errors
curl -s https://api.civicq.com/metrics | grep 'civicq_http_requests_total{status="500"}'
```

**Resolution**:

1. **If caused by recent deployment**:
```bash
# Rollback immediately
kubectl rollout undo deployment/civicq-api

# Verify rollback
kubectl rollout status deployment/civicq-api
./scripts/monitoring/check-health.sh
```

2. **If database connection errors**:
```bash
# Check database health
./scripts/monitoring/check-health.sh --url https://api.civicq.com/health/db

# Check connection pool
# In PostgreSQL:
SELECT count(*) FROM pg_stat_activity;

# Restart API to reset connections (last resort)
kubectl rollout restart deployment/civicq-api
```

3. **If external API errors**:
- Check third-party service status
- Implement circuit breaker
- Fall back to cached data if possible

**Prevention**:
- Gradual rollouts (canary deployments)
- Pre-deployment smoke tests
- Rate limiting on external APIs
- Implement retries with exponential backoff

---

### Database Issues

**Alert**: `DatabaseDown` or `SlowDatabaseQueries`

**Symptoms**:
- Cannot connect to database
- Queries taking >1 second
- Connection pool exhausted

**Diagnosis**:
```bash
# Check database health
./scripts/monitoring/check-health.sh --url https://api.civicq.com/health/db

# Connect to database
psql $DATABASE_URL

# Check active connections
SELECT count(*), state FROM pg_stat_activity GROUP BY state;

# Check slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 1000
ORDER BY mean_exec_time DESC
LIMIT 10;

# Check locks
SELECT * FROM pg_locks WHERE NOT granted;
```

**Resolution**:

1. **Connection exhaustion**:
```sql
-- Kill idle connections
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
AND state_change < NOW() - INTERVAL '10 minutes';
```

2. **Slow queries**:
```sql
-- Cancel long-running query
SELECT pg_cancel_backend(pid)
FROM pg_stat_activity
WHERE state = 'active'
AND query_start < NOW() - INTERVAL '5 minutes';

-- Add missing index
CREATE INDEX CONCURRENTLY idx_name ON table_name(column);
```

3. **Deadlocks**:
```sql
-- View deadlocks
SELECT * FROM pg_stat_database WHERE deadlocks > 0;

-- Adjust application code to acquire locks in consistent order
```

**Prevention**:
- Monitor connection pool size
- Set statement timeout
- Add indexes for frequent queries
- Use connection pooling (PgBouncer)
- Regular VACUUM and ANALYZE

---

### Celery Queue Backup

**Alert**: `CeleryQueueBackup`

**Symptoms**:
- Queue length >100 tasks
- Videos not processing
- Ballot refresh delayed

**Diagnosis**:
```bash
# Check Celery workers
./scripts/monitoring/check-health.sh --url https://api.civicq.com/health/celery

# Inspect queues
docker exec -it civicq-celery-worker celery -A app.tasks inspect active_queues

# Check worker count
docker ps | grep celery-worker
```

**Resolution**:

1. **Scale workers horizontally**:
```bash
# Docker Compose
docker-compose up -d --scale celery-worker=4

# Kubernetes
kubectl scale deployment civicq-celery-worker --replicas=4
```

2. **Purge failed tasks** (if safe):
```bash
celery -A app.tasks purge
```

3. **Check for stuck tasks**:
```python
from app.tasks import celery_app

# Revoke stuck tasks
celery_app.control.revoke('task-id', terminate=True)
```

**Prevention**:
- Set task time limits
- Implement task result expiration
- Monitor queue length
- Auto-scaling based on queue depth

---

### High Memory Usage

**Alert**: `HighMemoryUsage`

**Symptoms**:
- Memory usage >85%
- OOMKiller killing processes
- Slow response times

**Diagnosis**:
```bash
# Check system memory
free -h

# Check container memory
docker stats civicq-api

# Check Python memory usage
python -m memory_profiler app/main.py

# Check for memory leaks in Sentry
```

**Resolution**:

1. **Restart service** (immediate):
```bash
kubectl rollout restart deployment/civicq-api
```

2. **Identify memory leak**:
- Check Sentry for repeated errors
- Profile with `memory_profiler`
- Review recent code changes

3. **Scale resources**:
```yaml
# Update deployment
resources:
  limits:
    memory: "2Gi"  # Increased from 1Gi
  requests:
    memory: "1Gi"
```

**Prevention**:
- Implement request timeouts
- Use pagination for large queries
- Clear unused caches
- Regular memory profiling
- Set appropriate resource limits

---

### SSL Certificate Expiring

**Alert**: `SSLCertificateExpiringSoon`

**Symptoms**:
- Certificate expires in <7 days
- Browser warnings

**Resolution**:

1. **Renew certificate** (Let's Encrypt):
```bash
certbot renew
systemctl reload nginx
```

2. **Update in cloud provider**:
- Upload new certificate
- Update load balancer

3. **Verify**:
```bash
echo | openssl s_client -servername civicq.com -connect civicq.com:443 2>/dev/null | openssl x509 -noout -dates
```

**Prevention**:
- Enable auto-renewal
- Monitor certificate expiration
- Set up alerts 30 days before expiry

## Service-Specific Procedures

### Frontend (React)

**Location**: Vercel deployment

**Rollback**:
```bash
# Via Vercel CLI
vercel rollback

# Via Vercel dashboard
# Go to deployments → Select previous → Promote to Production
```

**Cache clear**:
```bash
# Purge CDN cache
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/purge_cache" \
  -H "Authorization: Bearer $CF_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything":true}'
```

### Backend (FastAPI)

**Location**: Docker/Kubernetes

**Restart**:
```bash
# Docker
docker-compose restart civicq-api

# Kubernetes
kubectl rollout restart deployment/civicq-api
```

**Logs**:
```bash
# Recent logs
kubectl logs deployment/civicq-api --tail=100 --follow

# Errors only
kubectl logs deployment/civicq-api | grep ERROR

# Specific user
kubectl logs deployment/civicq-api | grep "user_id: 123"
```

### Database (PostgreSQL)

**Backup**:
```bash
# Manual backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
psql $DATABASE_URL < backup_20240214_120000.sql
```

**Maintenance**:
```sql
-- VACUUM to reclaim space
VACUUM ANALYZE;

-- Reindex
REINDEX DATABASE civicq;

-- Update statistics
ANALYZE;
```

### Redis

**Flush cache** (if corrupted):
```bash
redis-cli FLUSHALL
```

**Check memory**:
```bash
redis-cli INFO memory
```

## Rollback Procedures

### Application Rollback

**Docker Compose**:
```bash
# 1. Stop current version
docker-compose down

# 2. Checkout previous version
git checkout <previous-commit>

# 3. Rebuild and start
docker-compose up -d --build
```

**Kubernetes**:
```bash
# View rollout history
kubectl rollout history deployment/civicq-api

# Rollback to previous version
kubectl rollout undo deployment/civicq-api

# Rollback to specific version
kubectl rollout undo deployment/civicq-api --to-revision=3

# Monitor rollback
kubectl rollout status deployment/civicq-api
```

### Database Rollback

**Schema changes**:
```bash
# Using Alembic
alembic downgrade -1  # One migration back
alembic downgrade <revision>  # To specific revision

# Verify
alembic current
```

## Data Recovery

### PostgreSQL Point-in-Time Recovery

```bash
# Restore from base backup
pg_basebackup -D /var/lib/postgresql/data -P -U postgres

# Restore to specific time
# In recovery.conf:
restore_command = 'cp /archive/%f %p'
recovery_target_time = '2024-02-14 12:00:00'
```

### S3/R2 Recovery

```bash
# List versions
aws s3api list-object-versions --bucket civicq-videos --prefix videos/

# Restore specific version
aws s3api get-object \
  --bucket civicq-videos \
  --key videos/abc123.mp4 \
  --version-id <version-id> \
  restored.mp4
```

### Redis Recovery

```bash
# If AOF enabled
redis-cli --rdb /var/lib/redis/dump.rdb

# Restore
cp backup.rdb /var/lib/redis/dump.rdb
systemctl restart redis
```

## Communication Templates

### Status Update (Slack)

```
🔴 INCIDENT ALERT - [SEVERITY]

Component: [Component name]
Impact: [User-facing impact]
Status: Investigating/Mitigating/Resolved
Started: [Time]

Latest update:
[What we know and what we're doing]

Next update in 30 minutes.

Incident channel: #incident-YYYY-MM-DD-description
```

### Post-Mortem Template

See [POST_MORTEM_TEMPLATE.md](./POST_MORTEM_TEMPLATE.md)

## Emergency Procedures

### Complete Service Outage

1. **Activate incident response**
2. **Post status update** on status page
3. **Check all services** systematically
4. **Consider failover** to backup infrastructure (if available)
5. **Communicate** every 30 minutes
6. **Document** all actions in incident channel

### Data Breach

1. **Isolate affected systems immediately**
2. **Notify security team**
3. **Preserve evidence** (don't delete logs)
4. **Follow breach response plan**
5. **Notify affected users** (if required by law)
6. **File incident report**

### DDoS Attack

1. **Enable DDoS protection** (Cloudflare, AWS Shield)
2. **Rate limit aggressive IPs**
3. **Scale infrastructure** if needed
4. **Contact hosting provider**
5. **Document attack patterns**
