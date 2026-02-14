# CivicQ Operations Manual

**Day-to-day operations guide for production systems**

Version: 1.0
Last Updated: 2026-02-14

---

## Table of Contents

1. [Daily Operations](#daily-operations)
2. [Weekly Maintenance](#weekly-maintenance)
3. [Monthly Review](#monthly-review)
4. [Health Monitoring](#health-monitoring)
5. [Log Management](#log-management)
6. [Database Maintenance](#database-maintenance)
7. [Certificate Management](#certificate-management)
8. [Dependency Updates](#dependency-updates)
9. [Security Patches](#security-patches)
10. [Common Tasks](#common-tasks)

---

## Daily Operations

### Morning Checklist (9:00 AM)

```bash
#!/bin/bash
# Save as: /opt/civicq/scripts/daily-check.sh

echo "=== CivicQ Daily Health Check ==="
echo "Date: $(date)"
echo ""

# 1. Check all services are running
echo "1. Service Status:"
docker-compose -f /opt/civicq/docker-compose.production.yml ps

# 2. Check system resources
echo -e "\n2. System Resources:"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')%"
echo "Memory Usage: $(free -h | awk 'NR==2{printf "%.2f%%", $3*100/$2}')"
echo "Disk Usage: $(df -h / | awk 'NR==2{print $5}')"

# 3. Check database connection
echo -e "\n3. Database:"
docker-compose exec -T postgres psql -U civicq -d civicq -c "SELECT COUNT(*) as user_count FROM users;" 2>/dev/null && echo "✓ Database OK" || echo "✗ Database Error"

# 4. Check Redis
echo -e "\n4. Redis:"
docker-compose exec -T redis redis-cli -a $REDIS_PASSWORD ping 2>/dev/null && echo "✓ Redis OK" || echo "✗ Redis Error"

# 5. Check API health
echo -e "\n5. API Health:"
curl -sf https://api.civicq.example.com/health && echo "✓ API OK" || echo "✗ API Error"

# 6. Check frontend
echo -e "\n6. Frontend:"
curl -sf -I https://civicq.example.com | head -n1

# 7. Check Celery workers
echo -e "\n7. Celery Workers:"
docker-compose exec -T backend celery -A app.worker inspect active -j | jq -r 'to_entries | .[] | "\(.key): \(.value | length) tasks"'

# 8. Recent errors (last hour)
echo -e "\n8. Recent Errors (last hour):"
docker-compose logs --since 1h backend 2>&1 | grep -i error | wc -l

# 9. Storage usage
echo -e "\n9. Storage:"
aws s3 ls s3://civicq-media --recursive --human-readable --summarize 2>/dev/null | tail -n2

echo -e "\n=== Check Complete ==="
```

**Run daily check:**

```bash
# Make executable
chmod +x /opt/civicq/scripts/daily-check.sh

# Run manually
./scripts/daily-check.sh

# Or add to crontab (9 AM daily)
0 9 * * * /opt/civicq/scripts/daily-check.sh | mail -s "CivicQ Daily Report" admin@example.com
```

### Dashboard Monitoring

**Check these dashboards daily:**

1. **Application Metrics** (if using DataDog/New Relic)
   - Request rate
   - Error rate
   - Response time (p50, p95, p99)
   - Active users

2. **Infrastructure Metrics**
   - CPU usage (should be < 70%)
   - Memory usage (should be < 80%)
   - Disk usage (should be < 85%)
   - Network I/O

3. **Database Metrics**
   - Connection pool usage
   - Query performance
   - Slow queries (> 1s)
   - Replication lag (if applicable)

4. **User Activity**
   - New registrations
   - Questions submitted
   - Votes cast
   - Video views

### Alert Response

**When you receive an alert:**

1. **Acknowledge** the alert within 15 minutes
2. **Assess** severity and impact
3. **Investigate** root cause
4. **Mitigate** if critical (restore service first)
5. **Document** incident in log
6. **Follow up** with permanent fix

See [MONITORING_RUNBOOK.md](MONITORING_RUNBOOK.md) for specific alert procedures.

---

## Weekly Maintenance

### Every Monday (10:00 AM)

#### 1. Review Logs

```bash
# Check error rates
docker-compose logs backend --since 7d 2>&1 | grep -i error > /tmp/weekly-errors.log
echo "Errors in last 7 days: $(wc -l < /tmp/weekly-errors.log)"

# Top errors
grep "ERROR" /tmp/weekly-errors.log | cut -d: -f2- | sort | uniq -c | sort -rn | head -10

# Check for anomalies
docker-compose logs nginx --since 7d | grep -E "50[0-9]|40[0-9]" | wc -l
```

#### 2. Database Maintenance

```bash
# Vacuum and analyze
docker-compose exec postgres psql -U civicq -d civicq -c "VACUUM ANALYZE;"

# Check table sizes
docker-compose exec postgres psql -U civicq -d civicq -c "
SELECT
  relname as table_name,
  pg_size_pretty(pg_total_relation_size(relid)) as total_size,
  pg_size_pretty(pg_relation_size(relid)) as table_size,
  pg_size_pretty(pg_total_relation_size(relid) - pg_relation_size(relid)) as indexes_size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 10;
"

# Check slow queries (last 7 days)
docker-compose exec postgres psql -U civicq -d civicq -c "
SELECT query, calls, total_exec_time, mean_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 1000
ORDER BY mean_exec_time DESC
LIMIT 10;
"
```

#### 3. Backup Verification

```bash
# Verify latest database backup exists
ls -lh /opt/civicq/backups/db/latest.sql.gz

# Verify latest Redis backup
docker-compose exec redis redis-cli -a $REDIS_PASSWORD LASTSAVE

# Test restore to staging (optional but recommended)
# See BACKUP_RECOVERY.md
```

#### 4. Security Review

```bash
# Check for failed login attempts
docker-compose exec postgres psql -U civicq -d civicq -c "
SELECT email, COUNT(*) as failed_attempts, MAX(created_at) as last_attempt
FROM audit_logs
WHERE action = 'login_failed' AND created_at > NOW() - INTERVAL '7 days'
GROUP BY email
HAVING COUNT(*) > 10
ORDER BY failed_attempts DESC;
"

# Check SSL certificate expiry
echo | openssl s_client -servername civicq.example.com -connect civicq.example.com:443 2>/dev/null | openssl x509 -noout -dates

# Review user permissions
docker-compose exec postgres psql -U civicq -d civicq -c "
SELECT role, COUNT(*)
FROM users
GROUP BY role;
"
```

#### 5. Performance Review

```bash
# Average response times (from nginx logs)
docker-compose exec nginx cat /var/log/nginx/access.log | awk '{print $NF}' | awk '{sum+=$1; count++} END {print "Average response time:", sum/count, "ms"}'

# Request rate
docker-compose exec nginx cat /var/log/nginx/access.log | wc -l

# Top endpoints by request count
docker-compose exec nginx cat /var/log/nginx/access.log | awk '{print $7}' | sort | uniq -c | sort -rn | head -10

# Top error endpoints
docker-compose exec nginx cat /var/log/nginx/access.log | awk '{if ($9 >= 500) print $7}' | sort | uniq -c | sort -rn | head -10
```

---

## Monthly Review

### First Monday of Each Month

#### 1. Infrastructure Cost Review

```bash
# AWS costs (requires AWS CLI)
aws ce get-cost-and-usage \
  --time-period Start=$(date -d "1 month ago" +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics "UnblendedCost" \
  --group-by Type=DIMENSION,Key=SERVICE

# Review and optimize:
# - Unused resources
# - Over-provisioned instances
# - Data transfer costs
# - Storage costs
```

#### 2. Capacity Planning

```bash
# Database growth rate
docker-compose exec postgres psql -U civicq -d civicq -c "
SELECT
  DATE_TRUNC('month', created_at) as month,
  COUNT(*) as new_users
FROM users
WHERE created_at > NOW() - INTERVAL '6 months'
GROUP BY month
ORDER BY month;
"

# Storage growth
# Track S3 bucket size over time

# Predict capacity needs for next 3 months
# See SCALING_GUIDE.md
```

#### 3. Security Audit

```bash
# Review access logs
# Review user permissions
# Review API key usage
# Check for security patches
# Review firewall rules
# Check for suspicious activity

# Run automated security scan
docker-compose exec backend python -m app.scripts.security_audit
```

#### 4. Dependency Updates

```bash
# Check for outdated dependencies
cd backend
pip list --outdated

cd ../frontend
npm outdated

# Plan updates for next maintenance window
# See section on Dependency Updates below
```

#### 5. Performance Baseline

```bash
# Run performance tests
ab -n 1000 -c 10 https://civicq.example.com/ > /tmp/perf-baseline-$(date +%Y%m).txt

# Compare to previous month
# Document any degradation
```

#### 6. Disaster Recovery Test

```bash
# Test backup restoration (on staging)
# Test failover procedures
# Verify RTO/RPO targets
# Update runbooks based on findings

# See BACKUP_RECOVERY.md
```

#### 7. Documentation Review

- [ ] Update runbooks with any new procedures
- [ ] Document incidents and resolutions
- [ ] Update architecture diagrams if changes made
- [ ] Review and update on-call rotation
- [ ] Update contact information

---

## Health Monitoring

### Key Metrics to Monitor

#### Application Health

| Metric | Threshold | Action |
|--------|-----------|--------|
| API Response Time (p95) | < 500ms | Investigate if > 1s |
| Error Rate | < 1% | Alert if > 5% |
| Uptime | > 99.9% | Investigate any downtime |
| Active Users | Track trend | Alert on sudden drops |

#### Infrastructure Health

| Metric | Threshold | Action |
|--------|-----------|--------|
| CPU Usage | < 70% | Scale up if sustained > 80% |
| Memory Usage | < 80% | Scale up if > 90% |
| Disk Usage | < 85% | Cleanup or expand if > 90% |
| Network I/O | Monitor | Alert on anomalies |

#### Database Health

| Metric | Threshold | Action |
|--------|-----------|--------|
| Connection Pool | < 80% | Increase pool if sustained high |
| Query Time (avg) | < 100ms | Optimize queries if > 500ms |
| Replication Lag | < 1s | Alert if > 10s |
| Disk I/O Wait | < 10% | Optimize or upgrade if high |

#### Cache Health

| Metric | Threshold | Action |
|--------|-----------|--------|
| Redis Memory | < 80% | Increase if > 90% |
| Cache Hit Rate | > 80% | Review cache strategy if low |
| Evictions | Low | Increase memory if high |

### Health Check Endpoints

```bash
# API health
curl https://api.civicq.example.com/health

# Expected response:
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "version": "1.0.0",
  "timestamp": "2026-02-14T12:00:00Z"
}

# Detailed health (admin only)
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  https://api.civicq.example.com/api/v1/admin/health

# Expected response:
{
  "status": "healthy",
  "components": {
    "database": {
      "status": "healthy",
      "connections": 45,
      "max_connections": 200,
      "response_time_ms": 12
    },
    "redis": {
      "status": "healthy",
      "memory_used_mb": 234,
      "memory_max_mb": 512,
      "hit_rate": 0.87
    },
    "celery": {
      "status": "healthy",
      "active_tasks": 3,
      "workers": 4
    },
    "storage": {
      "status": "healthy",
      "total_size_gb": 145.7
    }
  }
}
```

---

## Log Management

### Log Locations

```bash
# Application logs
/opt/civicq/backend/logs/app.log
/opt/civicq/backend/logs/error.log

# Nginx logs
/var/log/nginx/access.log
/var/log/nginx/error.log

# Docker logs
docker-compose logs backend
docker-compose logs nginx
docker-compose logs postgres
docker-compose logs redis
docker-compose logs celery-worker
```

### Log Rotation

Configure logrotate:

```bash
# Create /etc/logrotate.d/civicq
cat > /etc/logrotate.d/civicq << 'EOF'
/opt/civicq/backend/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 civicq civicq
    sharedscripts
    postrotate
        docker-compose -f /opt/civicq/docker-compose.production.yml restart backend
    endscript
}

/var/log/nginx/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        docker-compose -f /opt/civicq/docker-compose.production.yml exec nginx nginx -s reload
    endscript
}
EOF

# Test logrotate
logrotate -d /etc/logrotate.d/civicq
```

### Log Analysis

```bash
# Error frequency by hour
grep "ERROR" /opt/civicq/backend/logs/app.log | cut -d' ' -f1,2 | cut -d: -f1 | sort | uniq -c

# Top error messages
grep "ERROR" /opt/civicq/backend/logs/app.log | cut -d']' -f2- | sort | uniq -c | sort -rn | head -10

# HTTP status codes
awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -rn

# Slow requests (> 1s)
awk '{if ($NF > 1000) print $0}' /var/log/nginx/access.log

# Top IPs by request count
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -20

# Search for specific error
grep -r "SpecificError" /opt/civicq/backend/logs/ | tail -20
```

### Centralized Logging (Optional)

**Papertrail Example:**

```bash
# Install remote_syslog2
wget https://github.com/papertrail/remote_syslog2/releases/download/v0.20/remote_syslog_linux_amd64.tar.gz
tar xzf remote_syslog_linux_amd64.tar.gz
sudo cp remote_syslog/remote_syslog /usr/local/bin

# Configure
cat > /etc/log_files.yml << 'EOF'
files:
  - /opt/civicq/backend/logs/app.log
  - /var/log/nginx/access.log
  - /var/log/nginx/error.log
destination:
  host: logs.papertrailapp.com
  port: 12345
  protocol: tls
EOF

# Start service
sudo remote_syslog -c /etc/log_files.yml
```

---

## Database Maintenance

### Daily Tasks

```bash
# Check replication status (if using replicas)
docker-compose exec postgres psql -U civicq -c "SELECT * FROM pg_stat_replication;"

# Check for blocking queries
docker-compose exec postgres psql -U civicq -d civicq -c "
SELECT pid, now() - pg_stat_activity.query_start AS duration, query, state
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
AND state != 'idle';
"
```

### Weekly Tasks

```bash
# Vacuum analyze (already in weekly checklist)
docker-compose exec postgres psql -U civicq -d civicq -c "VACUUM ANALYZE;"

# Reindex (if needed)
docker-compose exec postgres psql -U civicq -d civicq -c "REINDEX DATABASE civicq;"

# Update statistics
docker-compose exec postgres psql -U civicq -d civicq -c "ANALYZE;"
```

### Monthly Tasks

```bash
# Full vacuum (during maintenance window)
docker-compose exec postgres psql -U civicq -d civicq -c "VACUUM FULL ANALYZE;"

# Check for bloat
docker-compose exec postgres psql -U civicq -d civicq -c "
SELECT
  schemaname || '.' || tablename AS table,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename::regclass)) AS size,
  n_dead_tup,
  n_live_tup,
  ROUND(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC
LIMIT 10;
"
```

### Database Backups

```bash
# Manual backup
docker-compose exec postgres pg_dump -U civicq civicq | gzip > /opt/civicq/backups/db/civicq-$(date +%Y%m%d-%H%M%S).sql.gz

# Automated daily backup (crontab)
0 2 * * * /opt/civicq/scripts/backup-db.sh

# backup-db.sh script:
#!/bin/bash
BACKUP_DIR=/opt/civicq/backups/db
DATE=$(date +%Y%m%d-%H%M%S)
docker-compose -f /opt/civicq/docker-compose.production.yml exec -T postgres pg_dump -U civicq civicq | gzip > $BACKUP_DIR/civicq-$DATE.sql.gz

# Keep last 30 days
find $BACKUP_DIR -name "civicq-*.sql.gz" -mtime +30 -delete

# Upload to S3
aws s3 cp $BACKUP_DIR/civicq-$DATE.sql.gz s3://civicq-backups/db/
```

---

## Certificate Management

### Check Certificate Expiry

```bash
# Check when certificate expires
echo | openssl s_client -servername civicq.example.com -connect civicq.example.com:443 2>/dev/null | openssl x509 -noout -dates

# Days until expiry
echo | openssl s_client -servername civicq.example.com -connect civicq.example.com:443 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2 | xargs -I {} date -d "{}" +%s | awk -v today=$(date +%s) '{print int(($1-today)/86400)" days"}'
```

### Renew Certificate

```bash
# Let's Encrypt auto-renewal (already configured)
certbot renew --dry-run

# Manual renewal if needed
certbot renew --force-renewal

# Update nginx after renewal
docker-compose -f /opt/civicq/docker-compose.production.yml restart nginx
```

### Certificate Monitoring

```bash
# Add to daily crontab
0 6 * * * /opt/civicq/scripts/check-cert.sh

# check-cert.sh
#!/bin/bash
DAYS=$(echo | openssl s_client -servername civicq.example.com -connect civicq.example.com:443 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2 | xargs -I {} date -d "{}" +%s | awk -v today=$(date +%s) '{print int(($1-today)/86400)}')

if [ $DAYS -lt 30 ]; then
  echo "WARNING: SSL certificate expires in $DAYS days" | mail -s "Certificate Expiry Warning" admin@example.com
fi
```

---

## Dependency Updates

### Backend (Python)

```bash
# Check for updates
cd /opt/civicq/backend
pip list --outdated

# Update specific package (test in staging first!)
pip install --upgrade package-name

# Update requirements.txt
pip freeze > requirements.txt

# Test thoroughly before deploying
pytest

# Deploy update
docker-compose -f docker-compose.production.yml build backend
docker-compose -f docker-compose.production.yml up -d backend
```

### Frontend (npm)

```bash
# Check for updates
cd /opt/civicq/frontend
npm outdated

# Update specific package
npm update package-name

# Update all minor/patch versions
npm update

# Update major versions (careful!)
npm install package-name@latest

# Test build
npm run build

# Deploy
docker-compose -f docker-compose.production.yml build nginx
docker-compose -f docker-compose.production.yml up -d nginx
```

### Update Schedule

- **Security patches**: Immediately
- **Minor updates**: Monthly maintenance window
- **Major updates**: Quarterly, with thorough testing

---

## Security Patches

### Monitor Security Advisories

- GitHub Security Advisories
- npm audit
- pip-audit
- CVE databases
- Cloud provider security bulletins

### Apply Security Patches

```bash
# Check for vulnerabilities
cd /opt/civicq/backend
pip-audit

cd /opt/civicq/frontend
npm audit

# Fix automatically (review changes!)
npm audit fix

# High-severity fixes only
npm audit fix --audit-level=high

# Document and test all changes
# Deploy during maintenance window
```

---

## Common Tasks

### Restart Services

```bash
# Restart all services
docker-compose -f /opt/civicq/docker-compose.production.yml restart

# Restart specific service
docker-compose restart backend
docker-compose restart nginx
docker-compose restart postgres
docker-compose restart redis
docker-compose restart celery-worker

# Zero-downtime restart (with multiple instances)
# Scale up, wait, scale down old instances
```

### View Logs

```bash
# Follow logs
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend

# Logs since timestamp
docker-compose logs --since 2026-02-14T12:00:00 backend

# Search logs
docker-compose logs backend | grep "ERROR"
```

### Database Operations

```bash
# Connect to database
docker-compose exec postgres psql -U civicq -d civicq

# Run query
docker-compose exec postgres psql -U civicq -d civicq -c "SELECT COUNT(*) FROM users;"

# Run migration
docker-compose exec backend alembic upgrade head

# Rollback migration
docker-compose exec backend alembic downgrade -1
```

### User Management

```bash
# Create admin user
docker-compose exec backend python -c "
from app.services.auth import create_admin_user
create_admin_user('admin@example.com', 'password', 'Admin Name')
"

# Reset user password
docker-compose exec postgres psql -U civicq -d civicq -c "
UPDATE users SET hashed_password = '\$2b\$12\$NEW_HASH' WHERE email = 'user@example.com';
"

# Verify user
docker-compose exec postgres psql -U civicq -d civicq -c "
UPDATE users SET is_verified = true WHERE email = 'user@example.com';
"
```

### Clear Cache

```bash
# Flush Redis cache
docker-compose exec redis redis-cli -a $REDIS_PASSWORD FLUSHDB

# Clear specific keys
docker-compose exec redis redis-cli -a $REDIS_PASSWORD DEL "cache:questions:*"
```

### Scale Services

```bash
# Scale backend to 4 instances
docker-compose up -d --scale backend=4

# Scale Celery workers
docker-compose up -d --scale celery-worker=8
```

---

## Emergency Procedures

### Service Down

1. Check service status: `docker-compose ps`
2. Check logs: `docker-compose logs service-name`
3. Restart service: `docker-compose restart service-name`
4. If persists, escalate per [MONITORING_RUNBOOK.md](MONITORING_RUNBOOK.md)

### Database Issues

1. Check connections: `docker-compose exec postgres psql -U civicq -c "SELECT count(*) FROM pg_stat_activity;"`
2. Check for blocking queries (see Database Maintenance)
3. If unresponsive, restart: `docker-compose restart postgres`
4. Verify data integrity after restart

### High Load

1. Identify source: Check logs and metrics
2. Scale horizontally if possible
3. Enable rate limiting if DDoS
4. Contact on-call engineer

### Data Loss/Corruption

1. **STOP** all write operations immediately
2. Assess extent of damage
3. Restore from backup per [BACKUP_RECOVERY.md](BACKUP_RECOVERY.md)
4. Document incident

---

## Maintenance Windows

### Scheduled Maintenance

**Standard maintenance window**: Sundays 2:00-4:00 AM local time

**Pre-maintenance checklist:**

- [ ] Announce maintenance 72 hours in advance
- [ ] Backup all data
- [ ] Test changes in staging
- [ ] Prepare rollback plan
- [ ] Notify team

**During maintenance:**

1. Set maintenance mode
2. Stop services
3. Apply updates
4. Run tests
5. Restart services
6. Verify functionality
7. Monitor for issues

**Post-maintenance:**

- [ ] Verify all services healthy
- [ ] Check error rates
- [ ] Monitor performance
- [ ] Document changes
- [ ] Send completion notice

---

## Contact & Escalation

- **Operations team**: ops@civicq.org
- **On-call engineer**: See [MONITORING_RUNBOOK.md](MONITORING_RUNBOOK.md)
- **Emergency hotline**: [TBD]
- **Escalation matrix**: [TBD]

---

**Document Version**: 1.0
**Last Updated**: 2026-02-14
**Next Review**: Quarterly
