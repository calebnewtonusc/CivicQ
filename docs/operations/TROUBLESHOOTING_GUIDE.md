# CivicQ Troubleshooting Guide

**Common issues and their solutions**

Version: 1.0
Last Updated: 2026-02-14

---

## Quick Diagnostic Commands

```bash
# Service status
docker-compose ps

# Recent logs
docker-compose logs --tail=50 backend

# System resources
htop  # or top
df -h  # disk
free -h  # memory

# Network connectivity
curl -I https://api.civicq.example.com/health
ping civicq.example.com

# Database connection
docker-compose exec postgres psql -U civicq -d civicq -c "SELECT 1;"

# Redis connection
docker-compose exec redis redis-cli -a $REDIS_PASSWORD ping
```

---

## Service Won't Start

### Backend Won't Start

**Symptoms:**
- Container exits immediately
- "Connection refused" errors
- Health check fails

**Diagnosis:**

```bash
# Check logs
docker-compose logs backend

# Common errors:
# - "Port already in use"
# - "Database connection failed"
# - "Module not found"
# - "Environment variable missing"
```

**Solutions:**

```bash
# Port conflict
sudo lsof -i :8000
kill -9 <PID>

# Database not ready
docker-compose up -d postgres
docker-compose logs postgres  # wait for "ready to accept connections"
docker-compose up -d backend

# Missing dependencies
docker-compose build --no-cache backend
docker-compose up -d backend

# Environment variables
cat backend/.env  # verify all required vars set
source backend/.env
docker-compose up -d backend

# Permission issues
sudo chown -R civicq:civicq /opt/civicq
chmod +x /opt/civicq/backend/scripts/*
```

### Frontend Won't Start

**Solutions:**

```bash
# Build failed
cd frontend
npm install
npm run build

# Nginx config error
docker-compose exec nginx nginx -t  # test config
docker-compose restart nginx

# Port conflict
sudo lsof -i :80
sudo lsof -i :443
```

### Database Won't Start

**Solutions:**

```bash
# Check logs
docker-compose logs postgres

# Data directory corruption
docker-compose down
sudo rm -rf /opt/civicq/data/postgres/*  # DANGER: deletes data!
# Restore from backup (see BACKUP_RECOVERY.md)

# Disk full
df -h
# Clean up old logs, backups, or expand disk

# Permissions
sudo chown -R 999:999 /opt/civicq/data/postgres
```

---

## Database Connection Issues

### "Too many connections"

```bash
# Check current connections
docker-compose exec postgres psql -U civicq -c "SELECT count(*) FROM pg_stat_activity;"

# See who's connected
docker-compose exec postgres psql -U civicq -c "
SELECT datname, usename, count(*)
FROM pg_stat_activity
GROUP BY datname, usename;
"

# Increase max connections (if needed)
docker-compose exec postgres psql -U civicq -c "ALTER SYSTEM SET max_connections = 300;"
docker-compose restart postgres

# Or fix connection leak in app
# Check for unclosed connections in code
```

### "Connection refused"

```bash
# Verify database is running
docker-compose ps postgres

# Check port
docker-compose exec postgres psql -U civicq -c "SHOW port;"

# Verify DATABASE_URL
echo $DATABASE_URL
# Should be: postgresql://civicq:PASSWORD@postgres:5432/civicq

# Test connection manually
docker-compose exec backend python -c "
from sqlalchemy import create_engine
import os
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    result = conn.execute('SELECT 1')
    print('Connection successful!')
"
```

### Slow queries

```bash
# Find slow queries
docker-compose exec postgres psql -U civicq -d civicq -c "
SELECT query, calls, total_exec_time, mean_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 1000
ORDER BY total_exec_time DESC
LIMIT 20;
"

# Enable pg_stat_statements if not enabled
docker-compose exec postgres psql -U civicq -c "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;"

# Kill long-running query
docker-compose exec postgres psql -U civicq -d civicq -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'active' AND now() - query_start > interval '10 minutes';
"
```

---

## Redis Connection Issues

### "Connection refused"

```bash
# Verify Redis is running
docker-compose ps redis

# Check Redis logs
docker-compose logs redis

# Test connection
docker-compose exec redis redis-cli -a $REDIS_PASSWORD ping
# Should return: PONG

# Check REDIS_URL
echo $REDIS_URL
# Should be: redis://:PASSWORD@redis:6379/0
```

### "Out of memory"

```bash
# Check memory usage
docker-compose exec redis redis-cli -a $REDIS_PASSWORD INFO memory

# Flush cache if safe
docker-compose exec redis redis-cli -a $REDIS_PASSWORD FLUSHDB

# Increase maxmemory
docker-compose exec redis redis-cli -a $REDIS_PASSWORD CONFIG SET maxmemory 1gb

# Or update docker-compose.yml
# command: redis-server --maxmemory 1gb
```

---

## Email Delivery Failures

### SendGrid errors

```bash
# Test SendGrid API key
curl -X POST https://api.sendgrid.com/v3/mail/send \
  -H "Authorization: Bearer $SENDGRID_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "personalizations": [{"to": [{"email": "test@example.com"}]}],
    "from": {"email": "noreply@civicq.example.com"},
    "subject": "Test",
    "content": [{"type": "text/plain", "value": "Test email"}]
  }'

# Check SendGrid dashboard for bounces/blocks
# https://app.sendgrid.com/email_activity

# Verify domain authentication
# Dashboard > Settings > Sender Authentication

# Common issues:
# - API key invalid/expired
# - Domain not verified
# - IP reputation issues
# - Rate limit exceeded
```

### SMTP errors

```bash
# Test SMTP connection
docker-compose exec backend python -c "
import smtplib
smtp = smtplib.SMTP('$SMTP_HOST', $SMTP_PORT)
smtp.starttls()
smtp.login('$SMTP_USER', '$SMTP_PASSWORD')
print('SMTP connection successful!')
smtp.quit()
"

# Common SMTP errors:
# - 535: Authentication failed
# - 550: Mailbox not found
# - 553: Invalid email address
# - Connection timeout: Firewall blocking port 587
```

---

## Video Processing Failures

### Upload fails

```bash
# Check S3 credentials
aws s3 ls s3://civicq-media --endpoint-url=$S3_ENDPOINT

# Test upload
echo "test" > /tmp/test.txt
aws s3 cp /tmp/test.txt s3://civicq-media/test.txt --endpoint-url=$S3_ENDPOINT

# Check CORS
aws s3api get-bucket-cors --bucket civicq-media --endpoint-url=$S3_ENDPOINT

# Check bucket policy
aws s3api get-bucket-policy --bucket civicq-media --endpoint-url=$S3_ENDPOINT
```

### Transcoding fails

```bash
# Check Celery worker logs
docker-compose logs celery-worker

# Check FFmpeg is installed
docker-compose exec celery-worker which ffmpeg
docker-compose exec celery-worker ffmpeg -version

# Test FFmpeg manually
docker-compose exec celery-worker ffmpeg -i /tmp/test.mp4 -c:v libx264 -c:a aac /tmp/output.mp4

# Check task queue
docker-compose exec redis redis-cli -a $REDIS_PASSWORD LLEN celery

# Retry failed task
docker-compose exec backend python -c "
from app.tasks import process_video
process_video.retry(args=[video_id])
"
```

---

## High Error Rates

### 500 errors

```bash
# Check backend logs
docker-compose logs backend | grep "ERROR"

# Check Sentry (if configured)
# https://sentry.io/organizations/civicq/issues/

# Common causes:
# - Unhandled exceptions
# - Database deadlocks
# - Out of memory
# - Third-party API failures

# Restart services
docker-compose restart backend
docker-compose restart celery-worker
```

### 502/503/504 errors

```bash
# Backend not responding
docker-compose ps backend  # Should be "Up"
curl http://localhost:8000/health  # Test directly

# Nginx config error
docker-compose exec nginx nginx -t

# Backend overloaded
docker-compose logs backend | grep "timeout"
# Scale up: docker-compose up -d --scale backend=4

# Database connection pool exhausted
# See "Too many connections" above
```

### 401/403 errors

```bash
# Token expired/invalid
# Check JWT_SECRET_KEY matches across deployments

# CORS error
# Check ALLOWED_ORIGINS in backend/.env
# Should include frontend URL

# Missing permissions
# Check user role in database
docker-compose exec postgres psql -U civicq -d civicq -c "
SELECT email, role FROM users WHERE email = 'user@example.com';
"
```

---

## Slow Performance

### Slow API responses

```bash
# Check database performance
docker-compose exec postgres psql -U civicq -d civicq -c "
SELECT query, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
"

# Add missing indexes
docker-compose exec postgres psql -U civicq -d civicq -c "
SELECT schemaname, tablename, attname, n_distinct
FROM pg_stats
WHERE schemaname = 'public' AND n_distinct > 100
AND NOT EXISTS (
    SELECT 1 FROM pg_indexes
    WHERE tablename = pg_stats.tablename
    AND indexdef LIKE '%' || attname || '%'
);
"

# Check for slow routes
docker-compose logs nginx | awk '{if ($NF > 1000) print $0}'  # >1s

# Enable query logging
docker-compose exec postgres psql -U civicq -c "
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries >1s
SELECT pg_reload_conf();
"
```

### High CPU usage

```bash
# Identify process
top -c
htop

# If backend CPU high:
# - Check for infinite loops in code
# - Check for expensive operations
# - Scale horizontally

# If database CPU high:
# - Check for missing indexes
# - Check for N+1 queries
# - Optimize queries
```

### High memory usage

```bash
# Check memory by container
docker stats

# If backend memory high:
# - Check for memory leaks
# - Restart workers periodically
# - Reduce connection pool size

# If database memory high:
# - Tune shared_buffers
# - Check for large result sets
# - Add LIMIT to queries
```

---

## Out of Disk Space

```bash
# Check disk usage
df -h
du -sh /opt/civicq/*

# Find large files
find /opt/civicq -type f -size +100M -exec ls -lh {} \;

# Clean up:

# Docker system
docker system prune -a --volumes  # CAUTION: removes unused volumes

# Logs
find /var/log -name "*.log" -mtime +30 -delete
find /opt/civicq -name "*.log" -mtime +14 -delete

# Old backups
find /opt/civicq/backups -mtime +90 -delete

# Database bloat
docker-compose exec postgres psql -U civicq -d civicq -c "VACUUM FULL;"

# Expand disk (AWS)
aws ec2 modify-volume --volume-id vol-xxxxx --size 200
# Then resize partition:
sudo growpart /dev/xvda 1
sudo resize2fs /dev/xvda1
```

---

## Out of Memory

```bash
# Check memory
free -h

# Identify memory hog
ps aux --sort=-%mem | head -20

# Quick fix: Restart services
docker-compose restart

# Long-term fix:
# - Increase server memory
# - Optimize queries
# - Reduce connection pools
# - Add caching

# Kill memory hog (last resort)
kill -9 <PID>
```

---

## SSL Certificate Issues

### Certificate expired

```bash
# Check expiry
openssl x509 -in /etc/letsencrypt/live/civicq.example.com/fullchain.pem -noout -enddate

# Renew
certbot renew --force-renewal
docker-compose restart nginx

# Set up auto-renewal if not done
sudo crontab -e
# Add: 0 0 * * * certbot renew --quiet && docker-compose -f /opt/civicq/docker-compose.production.yml restart nginx
```

### "Certificate not trusted"

```bash
# Verify certificate chain
openssl s_client -connect civicq.example.com:443 -showcerts

# Check intermediate certificates included
cat /etc/letsencrypt/live/civicq.example.com/fullchain.pem

# Should contain:
# 1. Your certificate
# 2. Let's Encrypt intermediate cert
```

---

## DNS/Domain Issues

### Domain not resolving

```bash
# Check DNS propagation
dig civicq.example.com
nslookup civicq.example.com

# Check from multiple locations
# https://dnschecker.org/

# Verify DNS records
dig civicq.example.com A
dig api.civicq.example.com A
dig media.civicq.example.com CNAME

# TTL may cause delay (wait up to TTL seconds)
```

---

## Common User-Reported Issues

### "Can't log in"

```bash
# Check user exists
docker-compose exec postgres psql -U civicq -d civicq -c "
SELECT email, is_verified, is_active FROM users WHERE email = 'user@example.com';
"

# Reset password
docker-compose exec backend python -c "
from app.services.auth import reset_password
reset_password('user@example.com', 'NewPassword123!')
"

# Verify account
docker-compose exec postgres psql -U civicq -d civicq -c "
UPDATE users SET is_verified = true WHERE email = 'user@example.com';
"
```

### "Video won't play"

```bash
# Check video exists in S3
aws s3 ls s3://civicq-media/videos/ --recursive | grep <video_id>

# Check video URL
curl -I <video_url>  # Should return 200

# Check CDN
curl -I <cdn_url>  # Should return 200

# Check video format
# Must be mp4 with H.264 video, AAC audio
ffprobe <video_file>

# Regenerate thumbnail
docker-compose exec backend python -c "
from app.tasks import generate_thumbnail
generate_thumbnail.delay(video_id)
"
```

### "Question not appearing"

```bash
# Check question status
docker-compose exec postgres psql -U civicq -d civicq -c "
SELECT id, text, status, is_approved, created_at
FROM questions
WHERE id = <question_id>;
"

# Approve question
docker-compose exec postgres psql -U civicq -d civicq -c "
UPDATE questions SET is_approved = true, status = 'approved' WHERE id = <question_id>;
"

# Clear cache
docker-compose exec redis redis-cli -a $REDIS_PASSWORD DEL "questions:*"
```

---

## Emergency Recovery

### Complete system failure

```bash
# 1. Restore from backup
# See BACKUP_RECOVERY.md

# 2. Verify all services
./scripts/health-check.sh

# 3. Check data integrity
docker-compose exec postgres psql -U civicq -d civicq -c "
SELECT
  (SELECT COUNT(*) FROM users) as users,
  (SELECT COUNT(*) FROM questions) as questions,
  (SELECT COUNT(*) FROM cities) as cities;
"

# 4. Test critical workflows
# - User registration
# - Question submission
# - Video upload
# - Email delivery

# 5. Monitor closely for 24-48 hours
```

---

## Getting Help

If issue persists:

1. **Check logs**: `docker-compose logs --tail=100 <service>`
2. **Check documentation**: `/docs` directory
3. **Search issues**: GitHub Issues
4. **Contact support**: support@civicq.org
5. **Emergency**: [On-call procedures](MONITORING_RUNBOOK.md)

---

## Preventive Maintenance

To avoid issues:

- [ ] Daily health checks
- [ ] Weekly log reviews
- [ ] Monthly dependency updates
- [ ] Regular backups and restore tests
- [ ] Performance monitoring
- [ ] Security audits
- [ ] Capacity planning

See [OPERATIONS_MANUAL.md](OPERATIONS_MANUAL.md) for routines.

---

**Document Version**: 1.0
**Last Updated**: 2026-02-14
**Next Review**: Quarterly
