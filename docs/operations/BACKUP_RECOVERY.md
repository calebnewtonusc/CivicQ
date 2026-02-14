# CivicQ Backup & Recovery Guide

**Disaster recovery procedures and backup strategies**

Version: 1.0 | Last Updated: 2026-02-14

---

## Backup Strategy

### 3-2-1 Backup Rule

- **3** copies of data
- **2** different storage media
- **1** copy offsite

### Backup Schedule

| Component | Frequency | Retention | RTO | RPO |
|-----------|-----------|-----------|-----|-----|
| **Database** | Daily (2 AM) | 30 days | <4 hours | <24 hours |
| **Redis** | Daily (3 AM) | 7 days | <1 hour | <24 hours |
| **Media Files** | Continuous | 90 days | <1 hour | <1 hour |
| **Config Files** | On change | Forever | <1 hour | 0 |
| **Full System** | Weekly | 4 weeks | <8 hours | <7 days |

---

## Database Backups

### Automated Daily Backup

```bash
# /opt/civicq/scripts/backup-db.sh
#!/bin/bash
set -e

BACKUP_DIR="/opt/civicq/backups/db"
S3_BUCKET="civicq-backups"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="civicq-db-$DATE.sql.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

# Dump database
docker-compose -f /opt/civicq/docker-compose.production.yml exec -T postgres \
  pg_dump -U civicq -d civicq --clean --if-exists | gzip > "$BACKUP_DIR/$BACKUP_FILE"

# Verify backup
if [ -f "$BACKUP_DIR/$BACKUP_FILE" ]; then
  echo "Backup created: $BACKUP_FILE ($(du -h "$BACKUP_DIR/$BACKUP_FILE" | cut -f1))"
else
  echo "ERROR: Backup failed!"
  exit 1
fi

# Upload to S3
aws s3 cp "$BACKUP_DIR/$BACKUP_FILE" "s3://$S3_BUCKET/db/" --storage-class STANDARD_IA

# Keep last 30 days locally
find $BACKUP_DIR -name "civicq-db-*.sql.gz" -mtime +30 -delete

# Keep last 90 days in S3
aws s3 ls s3://$S3_BUCKET/db/ | while read -r line; do
  createDate=`echo $line|awk {'print $1" "$2'}`
  createDate=`date -d"$createDate" +%s`
  olderThan=`date -d "90 days ago" +%s`
  if [[ $createDate -lt $olderThan ]]; then
    fileName=`echo $line|awk {'print $4'}`
    if [[ $fileName != "" ]]; then
      aws s3 rm s3://$S3_BUCKET/db/$fileName
    fi
  fi
done

echo "Backup complete and uploaded to S3"
```

### Schedule with Cron

```bash
# Add to crontab
sudo crontab -e

# Daily at 2 AM
0 2 * * * /opt/civicq/scripts/backup-db.sh >> /var/log/civicq-backup.log 2>&1
```

### Manual Backup

```bash
# Quick backup
docker-compose exec postgres pg_dump -U civicq civicq | gzip > backup-$(date +%Y%m%d).sql.gz

# With compression and options
docker-compose exec postgres pg_dump -U civicq -d civicq \
  --format=custom \
  --compress=9 \
  --file=/tmp/backup.dump

# Copy from container
docker cp civicq-postgres-prod:/tmp/backup.dump ./backups/
```

---

## Database Restoration

### Full Restore

```bash
# 1. Stop all services except database
docker-compose stop backend celery-worker celery-beat nginx

# 2. Drop and recreate database
docker-compose exec postgres psql -U civicq -c "DROP DATABASE IF EXISTS civicq;"
docker-compose exec postgres psql -U civicq -c "CREATE DATABASE civicq;"

# 3. Restore from backup
gunzip < backups/civicq-db-20260214.sql.gz | \
  docker-compose exec -T postgres psql -U civicq -d civicq

# 4. Verify restoration
docker-compose exec postgres psql -U civicq -d civicq -c "
SELECT
  (SELECT COUNT(*) FROM users) as users,
  (SELECT COUNT(*) FROM questions) as questions,
  (SELECT COUNT(*) FROM cities) as cities;
"

# 5. Restart all services
docker-compose up -d

# 6. Smoke test
./scripts/health-check.sh
```

### Point-in-Time Recovery (PITR)

If using WAL archiving:

```bash
# Configure WAL archiving first
# postgresql.conf:
# wal_level = replica
# archive_mode = on
# archive_command = 'aws s3 cp %p s3://civicq-backups/wal/%f'

# Restore to specific time
docker-compose exec postgres pg_basebackup -U civicq -D /var/lib/postgresql/data/restore -Fp -Xs -P

# Create recovery.conf
cat > recovery.conf << EOF
restore_command = 'aws s3 cp s3://civicq-backups/wal/%f %p'
recovery_target_time = '2026-02-14 12:00:00'
EOF

# Restart PostgreSQL with recovery.conf
```

---

## Redis Backups

### Automated Backup

```bash
# /opt/civicq/scripts/backup-redis.sh
#!/bin/bash
set -e

BACKUP_DIR="/opt/civicq/backups/redis"
DATE=$(date +%Y%m%d-%H%M%S)

mkdir -p $BACKUP_DIR

# Trigger save
docker-compose exec redis redis-cli -a $REDIS_PASSWORD BGSAVE

# Wait for save to complete
while [ $(docker-compose exec redis redis-cli -a $REDIS_PASSWORD LASTSAVE) -eq $LAST_SAVE ]; do
  sleep 1
done

# Copy RDB file
docker cp civicq-redis-prod:/data/dump.rdb "$BACKUP_DIR/dump-$DATE.rdb"

# Upload to S3
aws s3 cp "$BACKUP_DIR/dump-$DATE.rdb" s3://civicq-backups/redis/

# Keep last 7 days
find $BACKUP_DIR -name "dump-*.rdb" -mtime +7 -delete

echo "Redis backup complete"
```

### Redis Restoration

```bash
# 1. Stop Redis
docker-compose stop redis

# 2. Copy backup file
cp backups/redis/dump-20260214.rdb data/redis/dump.rdb

# 3. Set permissions
sudo chown 999:999 data/redis/dump.rdb

# 4. Start Redis
docker-compose up -d redis

# 5. Verify
docker-compose exec redis redis-cli -a $REDIS_PASSWORD DBSIZE
```

---

## Media File Backups

### S3 Versioning (Recommended)

```bash
# Enable versioning on bucket
aws s3api put-bucket-versioning \
  --bucket civicq-media \
  --versioning-configuration Status=Enabled

# List versions
aws s3api list-object-versions --bucket civicq-media

# Restore specific version
aws s3api copy-object \
  --bucket civicq-media \
  --copy-source civicq-media/videos/abc123.mp4?versionId=VERSION_ID \
  --key videos/abc123.mp4
```

### S3 Cross-Region Replication

```bash
# Create replication bucket
aws s3api create-bucket \
  --bucket civicq-media-backup \
  --region us-east-1

# Enable versioning on both buckets
aws s3api put-bucket-versioning \
  --bucket civicq-media-backup \
  --versioning-configuration Status=Enabled

# Set up replication rule
aws s3api put-bucket-replication \
  --bucket civicq-media \
  --replication-configuration file://replication.json
```

---

## Configuration Backups

### Backup Scripts

```bash
# /opt/civicq/scripts/backup-config.sh
#!/bin/bash
set -e

BACKUP_DIR="/opt/civicq/backups/config"
DATE=$(date +%Y%m%d-%H%M%S)
ARCHIVE="config-$DATE.tar.gz"

mkdir -p $BACKUP_DIR

# Backup all config files
tar -czf "$BACKUP_DIR/$ARCHIVE" \
  /opt/civicq/backend/.env.production \
  /opt/civicq/frontend/.env.production \
  /opt/civicq/docker-compose.production.yml \
  /opt/civicq/nginx/nginx.conf \
  /opt/civicq/nginx/ssl/ \
  /etc/cron.d/civicq-* 2>/dev/null || true

# Upload to S3
aws s3 cp "$BACKUP_DIR/$ARCHIVE" s3://civicq-backups/config/

echo "Config backup complete: $ARCHIVE"
```

### Version Control

```bash
# Use Git for configuration management
cd /opt/civicq
git init
git add backend/.env.example frontend/.env.example docker-compose.production.yml
git commit -m "Config snapshot $(date +%Y%m%d)"
git push backup main
```

---

## Full System Backup

### Create System Image (AWS)

```bash
# Create AMI
aws ec2 create-image \
  --instance-id i-xxxxx \
  --name "civicq-full-backup-$(date +%Y%m%d)" \
  --description "Full system backup" \
  --no-reboot

# Create snapshot of all volumes
aws ec2 describe-volumes --filters Name=attachment.instance-id,Values=i-xxxxx \
  | jq -r '.Volumes[].VolumeId' \
  | while read vol; do
      aws ec2 create-snapshot --volume-id $vol --description "Backup $(date +%Y%m%d)"
    done
```

### Docker Volume Backup

```bash
# Backup all volumes
docker run --rm \
  -v civicq_postgres_data:/source:ro \
  -v /opt/civicq/backups:/backup \
  alpine tar -czf /backup/postgres-data-$(date +%Y%m%d).tar.gz -C /source .

docker run --rm \
  -v civicq_redis_data:/source:ro \
  -v /opt/civicq/backups:/backup \
  alpine tar -czf /backup/redis-data-$(date +%Y%m%d).tar.gz -C /source .
```

---

## Disaster Recovery Scenarios

### Scenario 1: Database Corruption

**Detection:**
- Application errors
- Data inconsistencies
- Cannot query database

**Recovery:**

```bash
# 1. Stop all writes
docker-compose stop backend celery-worker

# 2. Assess damage
docker-compose exec postgres psql -U civicq -d civicq
# Try various queries to identify extent

# 3. If minor: Try repair
docker-compose exec postgres psql -U civicq -d civicq -c "REINDEX DATABASE civicq;"
docker-compose exec postgres psql -U civicq -d civicq -c "VACUUM FULL;"

# 4. If major: Restore from backup (see above)

# 5. Verify and resume
./scripts/health-check.sh
docker-compose up -d
```

### Scenario 2: Complete Server Failure

**Recovery:**

```bash
# 1. Provision new server
# 2. Install Docker and dependencies
# 3. Clone repository
git clone https://github.com/your-org/civicq.git /opt/civicq

# 4. Restore configuration
aws s3 cp s3://civicq-backups/config/config-latest.tar.gz /tmp/
tar -xzf /tmp/config-latest.tar.gz -C /

# 5. Restore database
aws s3 cp s3://civicq-backups/db/civicq-db-latest.sql.gz /tmp/
docker-compose up -d postgres
gunzip < /tmp/civicq-db-latest.sql.gz | docker-compose exec -T postgres psql -U civicq -d civicq

# 6. Restore Redis
aws s3 cp s3://civicq-backups/redis/dump-latest.rdb /opt/civicq/data/redis/dump.rdb

# 7. Start all services
docker-compose up -d

# 8. Verify
./scripts/health-check.sh

# 9. Update DNS if IP changed

# RTO: 2-4 hours
```

### Scenario 3: Accidental Data Deletion

**Recovery:**

```bash
# If deleted within last 24 hours:
# 1. Stop writes immediately
docker-compose stop backend

# 2. Identify what was deleted and when
# Check audit logs

# 3. Restore from most recent backup before deletion
# See database restoration above

# 4. If only specific records:
docker-compose exec postgres psql -U civicq -d civicq

# Restore specific rows from backup:
# pg_restore with --data-only --table=users

# RPO: Up to 24 hours of data loss
```

### Scenario 4: Security Breach

**Recovery:**

```bash
# 1. Isolate system immediately
sudo ufw deny all
docker-compose down

# 2. Assess extent of breach
# - Review logs
# - Check for unauthorized access
# - Identify compromised data

# 3. Restore from known-good backup
# Use backup from before breach occurred

# 4. Rotate ALL credentials
# - Database passwords
# - API keys
# - JWT secrets
# - SSL certificates

# 5. Apply security patches

# 6. Gradually restore service with monitoring

# 7. Notify affected users per GDPR/CCPA requirements

# See SECURITY.md for full incident response plan
```

---

## Testing Restore Procedures

### Monthly Restore Test

```bash
# /opt/civicq/scripts/test-restore.sh
#!/bin/bash
# Run on staging environment

set -e

echo "=== CivicQ Restore Test ==="
echo "Date: $(date)"

# 1. Download latest backup
LATEST_BACKUP=$(aws s3 ls s3://civicq-backups/db/ | sort | tail -n 1 | awk '{print $4}')
echo "Using backup: $LATEST_BACKUP"
aws s3 cp "s3://civicq-backups/db/$LATEST_BACKUP" /tmp/

# 2. Restore to staging
gunzip < "/tmp/$LATEST_BACKUP" | docker-compose -f docker-compose.staging.yml exec -T postgres psql -U civicq -d civicq

# 3. Verify data integrity
docker-compose -f docker-compose.staging.yml exec postgres psql -U civicq -d civicq -c "
SELECT
  (SELECT COUNT(*) FROM users) as users,
  (SELECT COUNT(*) FROM questions) as questions,
  (SELECT COUNT(*) FROM cities) as cities;
"

# 4. Test application
curl -f http://staging.civicq.internal/health || exit 1

# 5. Record results
echo "Restore test successful!" | mail -s "Restore Test: PASS" ops@civicq.org

echo "=== Test Complete ==="
```

### Annual Disaster Recovery Drill

```bash
# Full DR drill checklist:
# [ ] Provision new server from scratch
# [ ] Restore all backups
# [ ] Verify all functionality
# [ ] Measure RTO/RPO
# [ ] Document lessons learned
# [ ] Update procedures
```

---

## Backup Monitoring

### Check Backup Health

```bash
# /opt/civicq/scripts/check-backups.sh
#!/bin/bash

echo "=== Backup Health Check ==="

# Database backups
LAST_DB_BACKUP=$(ls -t /opt/civicq/backups/db/*.sql.gz | head -1)
LAST_DB_AGE=$(($(date +%s) - $(stat -c %Y "$LAST_DB_BACKUP")))

if [ $LAST_DB_AGE -gt 86400 ]; then
  echo "WARNING: Last database backup is $((LAST_DB_AGE / 3600)) hours old"
  echo "Last backup: $LAST_DB_BACKUP" | mail -s "Backup Warning" ops@civicq.org
else
  echo "✓ Database backup OK ($(($LAST_DB_AGE / 3600)) hours old)"
fi

# S3 backups
S3_BACKUPS=$(aws s3 ls s3://civicq-backups/db/ | tail -1)
echo "Latest S3 backup: $S3_BACKUPS"

# Redis backups
LAST_REDIS_BACKUP=$(ls -t /opt/civicq/backups/redis/*.rdb | head -1)
echo "Latest Redis backup: $LAST_REDIS_BACKUP"

echo "=== Check Complete ==="
```

---

## Retention Policies

### Legal Requirements

- **User data**: 7 years (varies by jurisdiction)
- **Financial records**: 7 years
- **Audit logs**: 1 year minimum
- **Election data**: Until election + 22 months (federal)

### Storage Classes

| Age | Storage Class | Cost | Retrieval |
|-----|--------------|------|-----------|
| 0-30 days | S3 Standard | $$$ | Instant |
| 30-90 days | S3 IA | $$ | Instant |
| 90+ days | S3 Glacier | $ | Hours |
| Archive | S3 Deep Archive | $ | 12+ hours |

```bash
# Lifecycle policy
aws s3api put-bucket-lifecycle-configuration \
  --bucket civicq-backups \
  --lifecycle-configuration file://lifecycle.json

# lifecycle.json
{
  "Rules": [
    {
      "Id": "Archive old backups",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        },
        {
          "Days": 365,
          "StorageClass": "DEEP_ARCHIVE"
        }
      ],
      "Expiration": {
        "Days": 2555
      }
    }
  ]
}
```

---

## Recovery Time/Point Objectives

### RTO (Recovery Time Objective)

| Component | RTO Target | Actual |
|-----------|-----------|--------|
| Database | 4 hours | Test monthly |
| Application | 2 hours | Test monthly |
| Media files | 1 hour | Continuous |
| Full system | 8 hours | Test annually |

### RPO (Recovery Point Objective)

| Component | RPO Target | Backup Frequency |
|-----------|-----------|------------------|
| Database | 24 hours | Daily |
| Redis | 24 hours | Daily |
| Media files | 1 hour | Continuous (versioning) |
| Config | 0 (on change) | Git + S3 |

---

## Contact & Escalation

**Backup Issues:**
- Ops team: ops@civicq.org
- On-call: See MONITORING_RUNBOOK.md

**Disaster Recovery:**
- **Severity 1**: Call emergency hotline
- **Severity 2**: Email ops team
- **Severity 3**: Create ticket

---

**Document Version**: 1.0
**Last Updated**: 2026-02-14
**Next Review**: Quarterly or after DR event
