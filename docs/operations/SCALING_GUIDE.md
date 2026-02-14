# CivicQ Scaling Guide

**How to scale CivicQ from 1,000 to 1,000,000+ voters**

Version: 1.0
Last Updated: 2026-02-14

---

## Table of Contents

1. [When to Scale](#when-to-scale)
2. [Scaling Metrics](#scaling-metrics)
3. [Vertical Scaling](#vertical-scaling)
4. [Horizontal Scaling](#horizontal-scaling)
5. [Database Scaling](#database-scaling)
6. [Redis Scaling](#redis-scaling)
7. [Celery Worker Scaling](#celery-worker-scaling)
8. [CDN Optimization](#cdn-optimization)
9. [Auto-Scaling](#auto-scaling)
10. [Load Balancer Setup](#load-balancer-setup)
11. [Cost Optimization](#cost-optimization)

---

## When to Scale

### Key Indicators

**Scale UP when:**
- CPU usage sustained > 70% for 1+ hours
- Memory usage sustained > 80%
- Database connections > 80% of pool
- Response time p95 > 1 second
- Error rate > 2%
- Queue backlog growing
- User complaints about slowness

**Scale DOWN when:**
- Resources under-utilized for 7+ days
- Cost optimization needed
- Traffic patterns stabilized lower

### Traffic Capacity by Tier

| Tier | Users | Concurrent | Requests/sec | Monthly Cost |
|------|-------|-----------|--------------|--------------|
| **Small** | 1K-5K | 50-100 | 10-50 | $50-150 |
| **Medium** | 5K-25K | 100-500 | 50-200 | $150-500 |
| **Large** | 25K-100K | 500-2K | 200-1K | $500-2K |
| **XL** | 100K-500K | 2K-10K | 1K-5K | $2K-10K |
| **XXL** | 500K+ | 10K+ | 5K+ | $10K+ |

---

## Scaling Metrics

### Monitor These Metrics

```bash
# CPU Usage
top -bn1 | grep "Cpu(s)"

# Memory Usage
free -h

# Disk I/O
iostat -x 1

# Network
iftop

# Database connections
docker-compose exec postgres psql -U civicq -c "SELECT count(*) FROM pg_stat_activity;"

# API response time
curl -w "@curl-format.txt" -s https://api.civicq.example.com/health

# curl-format.txt:
time_namelookup: %{time_namelookup}\n
time_connect: %{time_connect}\n
time_appconnect: %{time_appconnect}\n
time_pretransfer: %{time_pretransfer}\n
time_redirect: %{time_redirect}\n
time_starttransfer: %{time_starttransfer}\n
time_total: %{time_total}\n
```

### Scaling Decision Matrix

| Metric | Current | Threshold | Action |
|--------|---------|-----------|--------|
| CPU | >70% sustained | 80% | Scale up/out |
| Memory | >80% | 90% | Scale up |
| Disk | >85% | 90% | Expand storage |
| DB Connections | >160/200 | 180/200 | Add read replicas |
| Response Time | >500ms p95 | >1000ms | Optimize/scale |
| Error Rate | >1% | >5% | Fix bugs/scale |

---

## Vertical Scaling

### Upgrade Server Resources

**When to use:** Quick fix, single-server deployments, database

**AWS EC2 Example:**

```bash
# Current: t3.medium (2 vCPU, 4GB RAM)
# Upgrade to: t3.large (2 vCPU, 8GB RAM)

# 1. Create AMI backup
aws ec2 create-image --instance-id i-xxxxx --name "civicq-before-resize"

# 2. Stop instance
aws ec2 stop-instances --instance-ids i-xxxxx

# 3. Modify instance type
aws ec2 modify-instance-attribute --instance-id i-xxxxx --instance-type "{\"Value\": \"t3.large\"}"

# 4. Start instance
aws ec2 start-instances --instance-ids i-xxxxx

# Total downtime: ~5 minutes
```

**Database Vertical Scaling (AWS RDS):**

```bash
# Upgrade from db.t3.medium to db.t3.large
aws rds modify-db-instance \
  --db-instance-identifier civicq-db \
  --db-instance-class db.t3.large \
  --apply-immediately

# Downtime: ~5-15 minutes during maintenance window
```

**Google Cloud:**

```bash
# Resize instance
gcloud compute instances set-machine-type civicq-instance \
  --machine-type n1-standard-4 \
  --zone us-west2-a

# Resize Cloud SQL
gcloud sql instances patch civicq-db \
  --tier=db-n1-standard-4
```

---

## Horizontal Scaling

### Add More Servers (Recommended)

**When to use:** High availability, better redundancy, easier rollbacks

### Backend Scaling

**With Docker Compose:**

```bash
# Scale to 4 backend instances
docker-compose up -d --scale backend=4

# Verify
docker-compose ps backend
```

**With Kubernetes:**

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: civicq-backend
spec:
  replicas: 4  # Increase from 2
  selector:
    matchLabels:
      app: civicq-backend
  template:
    metadata:
      labels:
        app: civicq-backend
    spec:
      containers:
      - name: backend
        image: civicq/backend:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
```

```bash
# Apply changes
kubectl apply -f deployment.yaml

# Scale via command
kubectl scale deployment civicq-backend --replicas=6
```

**AWS ECS:**

```bash
# Update service desired count
aws ecs update-service \
  --cluster civicq-production \
  --service civicq-backend \
  --desired-count 4
```

---

## Database Scaling

### Read Replicas

**When to use:** Read-heavy workload (80%+ reads)

**AWS RDS:**

```bash
# Create read replica
aws rds create-db-instance-read-replica \
  --db-instance-identifier civicq-db-replica-1 \
  --source-db-instance-identifier civicq-db \
  --db-instance-class db.t3.medium \
  --availability-zone us-west-2b

# Get replica endpoint
aws rds describe-db-instances \
  --db-instance-identifier civicq-db-replica-1 \
  --query 'DBInstances[0].Endpoint.Address'
```

**Configure Application:**

```python
# backend/app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Primary (write)
PRIMARY_DB_URL = os.getenv("DATABASE_URL")
primary_engine = create_engine(PRIMARY_DB_URL, pool_size=20, max_overflow=40)
PrimarySession = sessionmaker(bind=primary_engine)

# Replica (read)
REPLICA_DB_URL = os.getenv("REPLICA_DATABASE_URL")
if REPLICA_DB_URL:
    replica_engine = create_engine(REPLICA_DB_URL, pool_size=20, max_overflow=40)
    ReplicaSession = sessionmaker(bind=replica_engine)
else:
    ReplicaSession = PrimarySession

# Usage:
# For writes: use PrimarySession
# For reads: use ReplicaSession
```

### Connection Pooling

```python
# Optimize connection pool
engine = create_engine(
    DATABASE_URL,
    pool_size=20,          # Connections to keep open
    max_overflow=40,       # Extra connections when needed
    pool_pre_ping=True,    # Verify connections
    pool_recycle=3600,     # Recycle connections every hour
)
```

### Database Partitioning

**When to use:** Very large tables (10M+ rows)

```sql
-- Partition questions by city_id
CREATE TABLE questions_partitioned (
    id BIGSERIAL,
    city_id INTEGER,
    -- other columns
) PARTITION BY HASH (city_id);

CREATE TABLE questions_part_0 PARTITION OF questions_partitioned
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE questions_part_1 PARTITION OF questions_partitioned
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE questions_part_2 PARTITION OF questions_partitioned
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE questions_part_3 PARTITION OF questions_partitioned
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

### Query Optimization

```sql
-- Add missing indexes
CREATE INDEX CONCURRENTLY idx_questions_city_contest ON questions(city_id, contest_id);
CREATE INDEX CONCURRENTLY idx_votes_composite ON votes(question_id, user_id);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM questions WHERE city_id = 1;

-- Update statistics
ANALYZE questions;
```

---

## Redis Scaling

### Redis Cluster (for high availability)

**When to use:** Cache > 5GB, high availability required

**Redis Cluster Setup:**

```bash
# Create 6-node cluster (3 masters, 3 replicas)
docker run -d --name redis-1 -p 7001:7001 redis:7 redis-server --port 7001 --cluster-enabled yes
docker run -d --name redis-2 -p 7002:7002 redis:7 redis-server --port 7002 --cluster-enabled yes
docker run -d --name redis-3 -p 7003:7003 redis:7 redis-server --port 7003 --cluster-enabled yes
docker run -d --name redis-4 -p 7004:7004 redis:7 redis-server --port 7004 --cluster-enabled yes
docker run -d --name redis-5 -p 7005:7005 redis:7 redis-server --port 7005 --cluster-enabled yes
docker run -d --name redis-6 -p 7006:7006 redis:7 redis-server --port 7006 --cluster-enabled yes

# Create cluster
redis-cli --cluster create \
  127.0.0.1:7001 127.0.0.1:7002 127.0.0.1:7003 \
  127.0.0.1:7004 127.0.0.1:7005 127.0.0.1:7006 \
  --cluster-replicas 1
```

**AWS ElastiCache Cluster:**

```bash
# Create Redis cluster
aws elasticache create-replication-group \
  --replication-group-id civicq-redis-cluster \
  --replication-group-description "CivicQ Redis Cluster" \
  --engine redis \
  --cache-node-type cache.r5.large \
  --num-node-groups 3 \
  --replicas-per-node-group 1 \
  --automatic-failover-enabled
```

### Redis Sentinel (for failover)

```bash
# sentinel.conf
sentinel monitor civicq-redis 127.0.0.1 6379 2
sentinel down-after-milliseconds civicq-redis 5000
sentinel parallel-syncs civicq-redis 1
sentinel failover-timeout civicq-redis 10000

# Start sentinel
redis-sentinel /path/to/sentinel.conf
```

---

## Celery Worker Scaling

### Scale Workers Based on Queue Length

```bash
# Check queue length
docker-compose exec redis redis-cli -a $REDIS_PASSWORD LLEN celery

# Scale workers
docker-compose up -d --scale celery-worker=8

# Monitor workers
docker-compose exec backend celery -A app.worker inspect active
docker-compose exec backend celery -A app.worker inspect stats
```

### Worker Autoscaling

```python
# Start worker with autoscaling
celery -A app.worker worker \
  --autoscale=10,3 \
  --max-tasks-per-child=100

# 10 = max workers
# 3 = min workers
```

### Separate Queues by Priority

```python
# Define queues
CELERY_TASK_ROUTES = {
    'app.tasks.process_video': {'queue': 'video'},
    'app.tasks.send_email': {'queue': 'email'},
    'app.tasks.refresh_ballot': {'queue': 'default'},
}

# Start workers for specific queues
celery -A app.worker worker -Q video -c 4  # 4 workers for video
celery -A app.worker worker -Q email -c 2  # 2 workers for email
celery -A app.worker worker -Q default -c 4  # 4 workers for default
```

---

## CDN Optimization

### CloudFront Configuration

```json
{
  "DistributionConfig": {
    "Origins": {
      "Items": [
        {
          "Id": "S3-civicq-media",
          "DomainName": "civicq-media.s3.amazonaws.com",
          "S3OriginConfig": {
            "OriginAccessIdentity": "origin-access-identity/cloudfront/ABCDEFG"
          }
        }
      ]
    },
    "DefaultCacheBehavior": {
      "TargetOriginId": "S3-civicq-media",
      "ViewerProtocolPolicy": "redirect-to-https",
      "AllowedMethods": {
        "Items": ["GET", "HEAD"],
        "CachedMethods": {
          "Items": ["GET", "HEAD"]
        }
      },
      "Compress": true,
      "MinTTL": 0,
      "DefaultTTL": 86400,
      "MaxTTL": 31536000,
      "ForwardedValues": {
        "QueryString": false,
        "Cookies": {"Forward": "none"}
      }
    },
    "PriceClass": "PriceClass_100",  # US/Europe only
    "Enabled": true
  }
}
```

### Cache Invalidation

```bash
# Invalidate CDN cache after updates
aws cloudfront create-invalidation \
  --distribution-id E1234567890 \
  --paths "/*"

# Invalidate specific paths
aws cloudfront create-invalidation \
  --distribution-id E1234567890 \
  --paths "/videos/*" "/images/*"
```

---

## Auto-Scaling

### AWS Auto Scaling Group

```bash
# Create launch template
aws ec2 create-launch-template \
  --launch-template-name civicq-backend \
  --version-description "v1" \
  --launch-template-data file://launch-template.json

# launch-template.json
{
  "ImageId": "ami-xxxxx",
  "InstanceType": "t3.medium",
  "KeyName": "civicq-key",
  "SecurityGroupIds": ["sg-xxxxx"],
  "UserData": "IyEvYmluL2Jhc2gK..."  # base64 encoded startup script
}

# Create auto scaling group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name civicq-backend-asg \
  --launch-template LaunchTemplateName=civicq-backend \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 4 \
  --vpc-zone-identifier "subnet-xxxxx,subnet-yyyyy" \
  --target-group-arns arn:aws:elasticloadbalancing:...

# Create scaling policy (CPU-based)
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name civicq-backend-asg \
  --policy-name scale-up-on-cpu \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration file://cpu-policy.json

# cpu-policy.json
{
  "PredefinedMetricSpecification": {
    "PredefinedMetricType": "ASGAverageCPUUtilization"
  },
  "TargetValue": 70.0
}
```

### Kubernetes HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: civicq-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: civicq-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## Load Balancer Setup

### Nginx Load Balancer

```nginx
# /etc/nginx/conf.d/civicq-lb.conf
upstream backend {
    least_conn;  # Use least connections algorithm

    server backend1.internal:8000 max_fails=3 fail_timeout=30s;
    server backend2.internal:8000 max_fails=3 fail_timeout=30s;
    server backend3.internal:8000 max_fails=3 fail_timeout=30s;
    server backend4.internal:8000 max_fails=3 fail_timeout=30s;

    keepalive 32;
}

server {
    listen 443 ssl http2;
    server_name api.civicq.example.com;

    # SSL config...

    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Health check
        proxy_next_upstream error timeout http_502 http_503 http_504;
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### AWS Application Load Balancer

```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name civicq-alb \
  --subnets subnet-xxxxx subnet-yyyyy \
  --security-groups sg-xxxxx \
  --scheme internet-facing \
  --type application

# Create target group
aws elbv2 create-target-group \
  --name civicq-backend-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxxxx \
  --health-check-enabled \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3

# Create listener
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:... \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:... \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...

# Register targets
aws elbv2 register-targets \
  --target-group-arn arn:aws:elasticloadbalancing:... \
  --targets Id=i-xxxxx Id=i-yyyyy Id=i-zzzzz
```

---

## Cost Optimization

### Reserved Instances (AWS)

```bash
# Purchase 1-year reserved instance (save ~40%)
aws ec2 purchase-reserved-instances-offering \
  --reserved-instances-offering-id offering-xxxxx \
  --instance-count 2

# Purchase 3-year reserved instance (save ~60%)
aws ec2 purchase-reserved-instances-offering \
  --reserved-instances-offering-id offering-yyyyy \
  --instance-count 2
```

### Spot Instances (for workers)

```bash
# Use spot instances for Celery workers (save ~70%)
aws ec2 request-spot-instances \
  --spot-price "0.05" \
  --instance-count 4 \
  --type "one-time" \
  --launch-specification file://spot-spec.json
```

### Database Optimization

- Use smallest instance that meets performance needs
- Enable automated backups only (not manual snapshots)
- Use storage autoscaling to avoid over-provisioning
- Archive old data to S3

### CDN Cost Savings

- Use Cloudflare (free tier) instead of CloudFront
- Use Cloudflare R2 (no egress fees) instead of S3
- Enable compression
- Set appropriate cache TTLs

### Monitoring Costs

```bash
# AWS Cost Explorer
aws ce get-cost-and-usage \
  --time-period Start=2026-01-01,End=2026-02-01 \
  --granularity MONTHLY \
  --metrics "UnblendedCost" \
  --group-by Type=DIMENSION,Key=SERVICE

# Identify cost anomalies
aws ce get-anomalies \
  --date-interval Start=2026-01-01,End=2026-02-14
```

---

## Scaling Checklist

### Before Scaling Up

- [ ] Review current metrics and trends
- [ ] Identify bottleneck (CPU, memory, disk, network, database)
- [ ] Estimate cost impact
- [ ] Test in staging environment
- [ ] Plan rollback strategy
- [ ] Schedule during low-traffic period
- [ ] Notify team

### During Scaling

- [ ] Monitor metrics in real-time
- [ ] Watch for errors
- [ ] Verify health checks passing
- [ ] Test end-to-end functionality
- [ ] Document changes

### After Scaling

- [ ] Verify performance improvement
- [ ] Monitor for 24-48 hours
- [ ] Adjust monitoring thresholds
- [ ] Update documentation
- [ ] Review costs

---

## Performance Benchmarks

### Target Metrics by Scale

| Scale | Users | Response Time (p95) | Throughput (req/s) | Database | Redis | Cost/mo |
|-------|-------|-------------------|-------------------|----------|-------|---------|
| Small | 5K | <500ms | 50 | 2vCPU/4GB | 1GB | $100 |
| Medium | 25K | <500ms | 200 | 4vCPU/8GB | 2GB | $400 |
| Large | 100K | <500ms | 1K | 8vCPU/16GB | 4GB | $1,500 |
| XL | 500K | <500ms | 5K | 16vCPU/32GB | 8GB | $6,000 |

---

**Document Version**: 1.0
**Last Updated**: 2026-02-14
**Next Review**: Quarterly
