# CivicQ Alert Reference Guide

Complete reference for all monitoring alerts, what they mean, and how to respond.

## Table of Contents

- [Critical Alerts](#critical-alerts)
- [Warning Alerts](#warning-alerts)
- [Business Alerts](#business-alerts)
- [Alert Severity Levels](#alert-severity-levels)
- [Common Response Patterns](#common-response-patterns)

## Alert Severity Levels

| Severity | Response Time | Notification | Escalation |
|----------|--------------|--------------|------------|
| Critical | Immediate | PagerDuty + Slack + Email | After 15 min |
| Warning | Within 1 hour | Slack | After 2 hours |
| Info | Best effort | Slack | None |

## Critical Alerts

### ServiceDown

**Description**: CivicQ API is not responding to health checks.

**Query**:
```promql
up{job="civicq-api"} == 0
```

**Threshold**: Down for 2 minutes

**Impact**: Users cannot access the application

**Action**:
1. Check service status:
   ```bash
   kubectl get pods -l app=civicq-api
   kubectl logs deployment/civicq-api --tail=50
   ```

2. If pod crashed, check logs for errors
3. If no pods running, check deployment:
   ```bash
   kubectl describe deployment civicq-api
   ```

4. Restart service:
   ```bash
   kubectl rollout restart deployment/civicq-api
   ```

5. If issue persists, check:
   - Cloud provider status
   - Load balancer health
   - DNS configuration

**Runbook**: [RUNBOOK.md - Service Down](#service-down)

---

### HighErrorRate

**Description**: Error rate exceeds 5% of total requests.

**Query**:
```promql
sum(rate(civicq_http_requests_total{status=~"5.."}[5m])) /
sum(rate(civicq_http_requests_total[5m])) > 0.05
```

**Threshold**: >5% for 5 minutes

**Impact**: Users experiencing errors, potential data loss

**Action**:
1. Check Sentry for error details:
   - Error type and frequency
   - Affected endpoints
   - Stack traces

2. Check recent deployments:
   ```bash
   kubectl rollout history deployment/civicq-api
   ```

3. If caused by recent deployment, rollback:
   ```bash
   kubectl rollout undo deployment/civicq-api
   ```

4. If not deployment-related, check:
   - Database connectivity (`/health/db`)
   - External API status
   - Resource constraints (CPU, memory)

5. Review error logs:
   ```bash
   kubectl logs deployment/civicq-api | grep ERROR | tail -100
   ```

**Runbook**: [RUNBOOK.md - High Error Rate](#high-error-rate)

---

### DatabaseDown

**Description**: Cannot connect to PostgreSQL database.

**Query**:
```promql
up{job="postgres"} == 0
```

**Threshold**: Down for 1 minute

**Impact**: Complete service outage, no data access

**Action**:
1. Check database health:
   ```bash
   ./scripts/monitoring/check-health.sh --url https://api.civicq.com/health/db
   ```

2. Try connecting directly:
   ```bash
   psql $DATABASE_URL
   ```

3. If connection refused:
   - Check database service status
   - Verify network connectivity
   - Check firewall rules

4. If authentication fails:
   - Verify credentials
   - Check database user permissions

5. For managed databases (RDS, etc.):
   - Check cloud provider console
   - Verify instance status
   - Check security groups

6. If database crashed, check logs and restart

**Runbook**: [RUNBOOK.md - Database Issues](#database-issues)

---

### RedisDown

**Description**: Cannot connect to Redis cache/queue.

**Query**:
```promql
up{job="redis"} == 0
```

**Threshold**: Down for 2 minutes

**Impact**:
- Session management broken
- Rate limiting not working
- Celery tasks not queuing

**Action**:
1. Check Redis health:
   ```bash
   ./scripts/monitoring/check-health.sh --url https://api.civicq.com/health/redis
   redis-cli ping
   ```

2. Check Redis service:
   ```bash
   docker ps | grep redis
   docker logs civicq-redis
   ```

3. Restart if needed:
   ```bash
   docker-compose restart redis
   ```

4. Check memory usage (Redis may crash if OOM):
   ```bash
   redis-cli INFO memory
   ```

5. If memory issue, clear cache or increase memory limit

**Runbook**: [RUNBOOK.md - Redis](#redis)

---

### NoCeleryWorkers

**Description**: No Celery workers are active to process background jobs.

**Query**:
```promql
celery_workers == 0
```

**Threshold**: No workers for 5 minutes

**Impact**:
- Videos not processing
- Ballot refresh not running
- Email notifications delayed

**Action**:
1. Check Celery worker status:
   ```bash
   docker ps | grep celery-worker
   kubectl get pods -l app=celery-worker
   ```

2. Check worker logs:
   ```bash
   docker logs civicq-celery-worker
   kubectl logs deployment/civicq-celery-worker
   ```

3. Restart workers:
   ```bash
   docker-compose restart celery-worker
   kubectl rollout restart deployment/civicq-celery-worker
   ```

4. Verify workers are registered:
   ```bash
   celery -A app.tasks inspect active
   ```

5. If workers keep crashing, check for:
   - Task code errors
   - Memory issues
   - Redis connectivity

**Runbook**: [RUNBOOK.md - Celery Queue Backup](#celery-queue-backup)

---

### DiskSpaceCritical

**Description**: Disk space below 10% available.

**Query**:
```promql
(node_filesystem_avail_bytes{mountpoint="/"} /
 node_filesystem_size_bytes{mountpoint="/"}) < 0.10
```

**Threshold**: <10% free for 5 minutes

**Impact**:
- Service may crash
- Cannot write logs
- Database writes may fail

**Action**:
1. Check disk usage:
   ```bash
   df -h
   du -sh /* | sort -h
   ```

2. Common space consumers:
   - Logs: `/var/log/`
   - Docker: `/var/lib/docker/`
   - Database: `/var/lib/postgresql/`

3. Clear space:
   ```bash
   # Docker cleanup
   docker system prune -a --volumes

   # Log rotation
   find /var/log -name "*.log" -mtime +30 -delete

   # Old database backups
   find /backups -mtime +30 -delete
   ```

4. If issue persists, increase volume size

---

### MemoryCritical

**Description**: Available memory below 10%.

**Query**:
```promql
(node_memory_MemAvailable_bytes /
 node_memory_MemTotal_bytes) < 0.10
```

**Threshold**: <10% available for 5 minutes

**Impact**:
- OOMKiller may kill processes
- Severe performance degradation

**Action**:
1. Check memory usage:
   ```bash
   free -h
   top -o %MEM
   ```

2. Identify memory hogs:
   ```bash
   ps aux --sort=-%mem | head -10
   ```

3. Restart high-memory services (temporary fix):
   ```bash
   kubectl rollout restart deployment/civicq-api
   ```

4. Long-term fixes:
   - Increase server memory
   - Fix memory leaks
   - Optimize queries
   - Add caching

**Runbook**: [RUNBOOK.md - High Memory Usage](#high-memory-usage)

---

### SSLCertificateExpiringSoon

**Description**: SSL certificate expires in less than 7 days.

**Query**:
```promql
probe_ssl_earliest_cert_expiry - time() < 86400 * 7
```

**Threshold**: <7 days until expiry

**Impact**: Site will be inaccessible when cert expires

**Action**:
1. Check certificate expiration:
   ```bash
   echo | openssl s_client -servername civicq.com \
     -connect civicq.com:443 2>/dev/null | \
     openssl x509 -noout -dates
   ```

2. Renew certificate:
   ```bash
   # Let's Encrypt
   certbot renew
   systemctl reload nginx

   # Or update in cloud provider (AWS, Cloudflare, etc.)
   ```

3. Verify renewal:
   ```bash
   curl -vI https://civicq.com 2>&1 | grep "expire"
   ```

4. Update monitoring if auto-renewal is set up

---

## Warning Alerts

### SlowAPIResponses

**Description**: 95th percentile response time exceeds 2 seconds.

**Query**:
```promql
histogram_quantile(0.95,
  sum(rate(civicq_http_request_duration_seconds_bucket[5m])) by (le, endpoint)
) > 2
```

**Threshold**: P95 >2s for 10 minutes

**Impact**: Poor user experience, potential timeouts

**Action**:
1. Identify slow endpoints in Grafana
2. Check database query performance:
   ```sql
   SELECT query, mean_exec_time, calls
   FROM pg_stat_statements
   WHERE mean_exec_time > 100
   ORDER BY mean_exec_time DESC LIMIT 10;
   ```

3. Check for N+1 queries in logs
4. Review recent code changes
5. Add database indexes if needed
6. Implement caching for expensive queries
7. Consider request timeout limits

---

### SlowDatabaseQueries

**Description**: 95th percentile database query time exceeds 1 second.

**Query**:
```promql
histogram_quantile(0.95,
  sum(rate(civicq_database_query_duration_seconds_bucket[5m])) by (le, query_type)
) > 1
```

**Threshold**: P95 >1s for 10 minutes

**Impact**: Slow API responses, potential timeouts

**Action**:
1. Find slow queries:
   ```sql
   SELECT query, mean_exec_time, calls, total_exec_time
   FROM pg_stat_statements
   WHERE mean_exec_time > 1000
   ORDER BY mean_exec_time DESC LIMIT 10;
   ```

2. Use EXPLAIN ANALYZE:
   ```sql
   EXPLAIN (ANALYZE, BUFFERS) SELECT ...;
   ```

3. Add missing indexes:
   ```sql
   CREATE INDEX CONCURRENTLY idx_name ON table(column);
   ```

4. Optimize query:
   - Add WHERE clauses
   - Use JOIN instead of subqueries
   - Limit result sets
   - Use covering indexes

5. Update table statistics:
   ```sql
   ANALYZE table_name;
   ```

---

### CeleryQueueBackup

**Description**: Celery queue has more than 100 pending tasks.

**Query**:
```promql
celery_queue_length > 100
```

**Threshold**: >100 tasks for 15 minutes

**Impact**:
- Videos delayed
- Ballot refresh delayed
- User notifications delayed

**Action**:
1. Check queue length:
   ```bash
   celery -A app.tasks inspect active_queues
   ```

2. Check worker count:
   ```bash
   celery -A app.tasks inspect stats
   ```

3. Scale workers:
   ```bash
   docker-compose up -d --scale celery-worker=4
   kubectl scale deployment civicq-celery-worker --replicas=4
   ```

4. Check for stuck tasks:
   ```bash
   celery -A app.tasks inspect active
   ```

5. If tasks are failing, check logs for errors

6. Consider:
   - Task timeout settings
   - Worker memory limits
   - Task retry limits

---

### HighCeleryFailureRate

**Description**: More than 10% of Celery tasks are failing.

**Query**:
```promql
sum(rate(civicq_celery_tasks_total{status="failure"}[10m])) by (task_name) /
sum(rate(civicq_celery_tasks_total[10m])) by (task_name) > 0.10
```

**Threshold**: >10% failure rate for 10 minutes

**Impact**: Background jobs not completing

**Action**:
1. Check Sentry for task errors
2. Review task logs:
   ```bash
   docker logs civicq-celery-worker | grep ERROR
   ```

3. Check for:
   - Database connectivity
   - External API failures
   - S3/storage issues
   - Memory errors

4. Review task code for bugs
5. Check task retry configuration
6. Fix identified issues and redeploy

---

### HighCPUUsage

**Description**: CPU usage exceeds 80%.

**Query**:
```promql
100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
```

**Threshold**: >80% for 15 minutes

**Impact**: Slow response times, potential instability

**Action**:
1. Check CPU usage:
   ```bash
   top
   htop
   ```

2. Identify CPU-intensive processes:
   ```bash
   ps aux --sort=-%cpu | head -10
   ```

3. Check for:
   - Infinite loops
   - Inefficient algorithms
   - Excessive parallelism
   - CPU-intensive tasks

4. Short-term: Scale horizontally
5. Long-term: Optimize code

---

### HighMemoryUsage

**Description**: Memory usage exceeds 85%.

**Query**:
```promql
((node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) /
 node_memory_MemTotal_bytes) > 0.85
```

**Threshold**: >85% for 15 minutes

**Impact**: Risk of OOM, performance degradation

**Action**:
1. Monitor memory trends
2. Check for memory leaks
3. Review recent deployments
4. Profile application memory usage
5. Increase server memory if needed

---

## Business Alerts

### UserActivityDrop

**Description**: User logins dropped >50% compared to 24h ago.

**Query**:
```promql
sum(rate(civicq_user_logins_total[1h])) /
sum(rate(civicq_user_logins_total[1h] offset 24h)) < 0.5
```

**Threshold**: <50% of normal for 30 minutes

**Impact**: Potential product issue or outage

**Action**:
1. Check if service is working properly
2. Review recent frontend deployments
3. Check authentication service
4. Look for user-facing errors in Sentry
5. Check social media for complaints
6. Review analytics for traffic patterns
7. Notify product team

---

### HighQuestionRejectionRate

**Description**: More than 50% of questions are being rejected.

**Query**:
```promql
sum(rate(civicq_questions_rejected_total[1h])) by (city_id) /
sum(rate(civicq_questions_submitted_total[1h])) by (city_id) > 0.50
```

**Threshold**: >50% for 1 hour

**Impact**: User frustration, potential toxicity filter issue

**Action**:
1. Check moderation dashboard
2. Review rejection reasons
3. Check toxicity model performance
4. Review recent moderation rule changes
5. Sample rejected questions manually
6. Notify moderation team
7. Adjust thresholds if needed

---

### ModerationQueueBackup

**Description**: More than 50 questions pending moderation.

**Query**:
```promql
civicq_questions_pending > 50
```

**Threshold**: >50 pending for 2 hours

**Impact**: Delayed question approval

**Action**:
1. Check number of moderators online
2. Notify moderation team
3. Consider:
   - Adjusting auto-moderation
   - Recruiting volunteer moderators
   - Implementing queue prioritization
4. If critical event, add temporary moderators

---

## Common Response Patterns

### Deployment-Related Issues

1. Check recent deployments
2. Review changes
3. Rollback if issue started after deployment
4. Fix and redeploy

### Database-Related Issues

1. Check connection pool
2. Review slow queries
3. Add indexes
4. Optimize queries
5. Scale database if needed

### External Dependency Issues

1. Check service status pages
2. Implement circuit breaker
3. Use cached data if available
4. Notify users of degraded service
5. Contact vendor if critical

### Resource Exhaustion

1. Immediate: Scale up/out
2. Short-term: Optimize or limit usage
3. Long-term: Capacity planning
4. Consider auto-scaling

## Alert Tuning

Review alerts monthly:

1. **False Positives**: Adjust thresholds or add conditions
2. **Alert Fatigue**: Consolidate or remove noisy alerts
3. **Missing Alerts**: Add new alerts for blind spots
4. **Outdated Alerts**: Remove alerts for deprecated features

## References

- [MONITORING_GUIDE.md](./MONITORING_GUIDE.md) - Complete monitoring setup
- [RUNBOOK.md](./RUNBOOK.md) - Detailed incident procedures
- [Prometheus Alert Rules](./prometheus/alerts.yml) - Alert definitions
- [Grafana Dashboards](./grafana/dashboards/) - Visualization
