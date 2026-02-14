# CivicQ Production Deployment Guide

Complete guide for deploying CivicQ to production on any cloud provider.

## Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Deployment Options](#deployment-options)
- [Step-by-Step Deployment](#step-by-step-deployment)
- [Cloud Provider Setup](#cloud-provider-setup)
- [Configuration](#configuration)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Deploy to Production (5 minutes)

```bash
# 1. Clone and navigate to project
git clone https://github.com/yourusername/civicq.git
cd civicq

# 2. Configure environment
cp backend/.env.production.example backend/.env.production
# Edit backend/.env.production with your values

# 3. Deploy
./infrastructure/scripts/deploy.sh production
```

---

## Prerequisites

### Required Tools

- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Git** (2.0+)
- **OpenSSL** (for generating secrets)
- **PostgreSQL Client** (for database operations)
- **AWS CLI** or **gcloud CLI** (for cloud deployments)

### Required Services

1. **PostgreSQL Database** (15+) with pgvector extension
2. **Redis** (7+) for caching and Celery
3. **S3-compatible Object Storage** (AWS S3, R2, DigitalOcean Spaces)
4. **SMTP/Email Service** (SendGrid, AWS SES, etc.)
5. **SMS Service** (Twilio) for phone verification

### Domain and SSL

- Domain name with DNS control
- SSL certificate (Let's Encrypt recommended)

---

## Deployment Options

CivicQ supports multiple deployment strategies:

### Option 1: Docker Compose (Recommended for VPS)

Best for: DigitalOcean, Linode, Hetzner, any VPS

**Pros:**
- Simple setup
- Lower cost
- Full control
- Easy to understand

**Cons:**
- Manual scaling
- Single server (add load balancer for HA)

### Option 2: Kubernetes (EKS/GKE)

Best for: Large scale, enterprise deployments

**Pros:**
- Auto-scaling
- High availability
- Advanced orchestration
- Cloud-native

**Cons:**
- Higher complexity
- Higher cost
- Requires K8s knowledge

### Option 3: Managed Services

Best for: Hands-off deployment

**Pros:**
- Fully managed
- Auto-scaling
- Minimal ops

**Cons:**
- Highest cost
- Vendor lock-in

---

## Step-by-Step Deployment

### Phase 1: Infrastructure Setup

#### 1. Create Database

**AWS RDS:**
```bash
# Using Terraform
cd infrastructure/terraform/aws
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars
terraform init
terraform plan
terraform apply
```

**Manual Setup:**
```sql
CREATE DATABASE civicq;
CREATE USER civicq_prod WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE civicq TO civicq_prod;

-- Install pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
```

#### 2. Create Redis Instance

**AWS ElastiCache:**
- Engine: Redis 7.0
- Node type: cache.t4g.medium (minimum)
- Cluster mode: Disabled
- Auth token: Enabled (save the token)

#### 3. Create S3 Bucket

```bash
# Create bucket
aws s3 mb s3://civicq-media-production --region us-west-2

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket civicq-media-production \
  --versioning-configuration Status=Enabled

# Configure CORS
aws s3api put-bucket-cors \
  --bucket civicq-media-production \
  --cors-configuration file://infrastructure/aws/s3-cors.json
```

#### 4. Create CloudFront Distribution (Optional)

```bash
aws cloudfront create-distribution \
  --origin-domain-name civicq-media-production.s3.us-west-2.amazonaws.com \
  --default-root-object index.html
```

### Phase 2: Application Configuration

#### 1. Generate Secrets

```bash
# Generate SECRET_KEY (32 bytes)
openssl rand -hex 32

# Generate database password
openssl rand -base64 32

# Generate Redis password
openssl rand -base64 32
```

#### 2. Configure Environment

Copy and edit the production environment file:

```bash
cp backend/.env.production.example backend/.env.production
```

**Critical Variables:**

```bash
# Security
SECRET_KEY=<your-generated-secret-key>

# Database
DATABASE_URL=postgresql://civicq_prod:PASSWORD@your-rds-endpoint:5432/civicq

# Redis
REDIS_URL=redis://:PASSWORD@your-redis-endpoint:6379/0
CELERY_BROKER_URL=redis://:PASSWORD@your-redis-endpoint:6379/1
CELERY_RESULT_BACKEND=redis://:PASSWORD@your-redis-endpoint:6379/1

# S3
S3_BUCKET=civicq-media-production
S3_ACCESS_KEY=<aws-access-key>
S3_SECRET_KEY=<aws-secret-key>
CDN_URL=https://d1234567890.cloudfront.net

# URLs
FRONTEND_URL=https://civicq.com
BACKEND_URL=https://api.civicq.com
ALLOWED_ORIGINS=https://civicq.com,https://www.civicq.com

# External Services
SENDGRID_API_KEY=<sendgrid-api-key>
TWILIO_ACCOUNT_SID=<twilio-sid>
TWILIO_AUTH_TOKEN=<twilio-token>
OPENAI_API_KEY=<openai-key>
ANTHROPIC_API_KEY=<anthropic-key>

# Monitoring
SENTRY_DSN=<sentry-dsn>
```

### Phase 3: Deployment

#### Option A: Deploy via Scripts (VPS)

1. **Setup Server:**

```bash
# SSH into your server
ssh user@your-server.com

# Install dependencies
sudo apt update
sudo apt install -y docker.io docker-compose-plugin git

# Clone repository
git clone https://github.com/yourusername/civicq.git
cd civicq
```

2. **Configure Environment:**

```bash
# Copy environment files
cp backend/.env.production.example backend/.env.production

# Edit with your values
nano backend/.env.production
```

3. **Run Initial Deployment:**

```bash
# Make scripts executable
chmod +x infrastructure/scripts/*.sh

# Run deployment
./infrastructure/scripts/deploy.sh production
```

#### Option B: Deploy via GitHub Actions

1. **Configure Secrets:**

Go to GitHub Settings > Secrets and add:

```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION
DEPLOYMENT_HOST
DEPLOYMENT_USER
SSH_PRIVATE_KEY
BACKEND_URL
FRONTEND_URL
BACKUP_S3_BUCKET
SLACK_WEBHOOK_URL (optional)
```

2. **Create Release:**

```bash
# Tag release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

The GitHub Actions workflow will automatically:
- Run tests
- Build Docker images
- Create database backup
- Deploy to production
- Run health checks
- Notify on Slack

### Phase 4: Post-Deployment

#### 1. Run Database Migrations

```bash
# Via Docker Compose
docker-compose -f docker-compose.production.yml exec backend alembic upgrade head

# Or via deployment script (already included)
./infrastructure/scripts/deploy.sh production
```

#### 2. Create Admin User

```bash
docker-compose -f docker-compose.production.yml exec backend python -c "
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()
admin = User(
    email='admin@civicq.com',
    hashed_password=get_password_hash('changeme'),
    full_name='Admin User',
    is_superuser=True,
    is_verified=True
)
db.add(admin)
db.commit()
print('Admin user created')
"
```

#### 3. Configure SSL

**Using Let's Encrypt:**

```bash
# Install certbot
sudo apt install certbot

# Generate certificate
sudo certbot certonly --standalone \
  -d civicq.com \
  -d www.civicq.com \
  -d api.civicq.com

# Copy certificates
sudo cp /etc/letsencrypt/live/civicq.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/civicq.com/privkey.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/civicq.com/chain.pem nginx/ssl/

# Restart nginx
docker-compose -f docker-compose.production.yml restart nginx
```

#### 4. Setup Auto-Renewal

```bash
# Create renewal script
echo '#!/bin/bash
certbot renew --quiet
docker-compose -f /opt/civicq/docker-compose.production.yml restart nginx
' | sudo tee /etc/cron.weekly/certbot-renew

sudo chmod +x /etc/cron.weekly/certbot-renew
```

#### 5. Verify Deployment

```bash
# Run health checks
./infrastructure/scripts/health-check.sh production

# Check logs
docker-compose -f docker-compose.production.yml logs -f

# Test endpoints
curl https://api.civicq.com/health
curl https://civicq.com
```

---

## Cloud Provider Setup

### AWS (ECS Fargate)

1. **Deploy Infrastructure:**

```bash
cd infrastructure/terraform/aws
terraform init
terraform apply
```

2. **Push Images to ECR:**

```bash
# Authenticate
aws ecr get-login-password --region us-west-2 | \
  docker login --username AWS --password-stdin \
  123456789012.dkr.ecr.us-west-2.amazonaws.com

# Build and push
docker build -t civicq-backend:latest backend/
docker tag civicq-backend:latest \
  123456789012.dkr.ecr.us-west-2.amazonaws.com/civicq-backend:latest
docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/civicq-backend:latest
```

### Google Cloud (GKE)

1. **Create Cluster:**

```bash
gcloud container clusters create civicq-prod \
  --region us-west1 \
  --num-nodes 3 \
  --machine-type n1-standard-2
```

2. **Deploy:**

```bash
kubectl apply -f infrastructure/kubernetes/
```

### DigitalOcean

1. **Create Droplet:**

```bash
# Create droplet via dashboard or CLI
doctl compute droplet create civicq-prod \
  --region nyc3 \
  --size s-2vcpu-4gb \
  --image ubuntu-22-04-x64
```

2. **Deploy:**

```bash
ssh root@your-droplet-ip
git clone https://github.com/yourusername/civicq.git
cd civicq
./infrastructure/scripts/deploy.sh production
```

---

## Configuration

### Environment Variables

See `backend/.env.production.example` for all variables.

**Critical Settings:**

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key | `openssl rand -hex 32` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@host:5432/db` |
| `REDIS_URL` | Redis connection | `redis://:pass@host:6379/0` |
| `S3_BUCKET` | Media storage bucket | `civicq-media-prod` |
| `ALLOWED_ORIGINS` | CORS origins | `https://civicq.com` |
| `SENTRY_DSN` | Error tracking | Sentry dashboard |

### Scaling Configuration

**Horizontal Scaling (Multiple Containers):**

```yaml
# docker-compose.production.yml
services:
  backend:
    deploy:
      replicas: 3  # Run 3 backend instances

  celery-worker:
    deploy:
      replicas: 2  # Run 2 worker instances
```

**Vertical Scaling (More Resources):**

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

---

## Monitoring and Maintenance

### Health Monitoring

```bash
# Manual health check
./infrastructure/scripts/health-check.sh production

# Automated monitoring (cron)
0 * * * * /opt/civicq/infrastructure/scripts/health-check.sh production | mail -s "CivicQ Health Check" admin@civicq.com
```

### Log Management

```bash
# View all logs
docker-compose -f docker-compose.production.yml logs -f

# View specific service
docker-compose -f docker-compose.production.yml logs -f backend

# Export logs
docker-compose -f docker-compose.production.yml logs > logs.txt
```

### Database Backups

```bash
# Manual backup
./infrastructure/scripts/backup.sh production

# Automated backups (cron)
0 2 * * * /opt/civicq/infrastructure/scripts/backup.sh production
```

### Updates and Rollbacks

**Update to New Version:**

```bash
# Pull latest code
git pull origin main

# Deploy
./infrastructure/scripts/deploy.sh production
```

**Rollback:**

```bash
./infrastructure/scripts/rollback.sh production v1.0.0
```

---

## Troubleshooting

### Common Issues

#### 1. Health Check Fails

```bash
# Check container status
docker-compose -f docker-compose.production.yml ps

# Check backend logs
docker-compose -f docker-compose.production.yml logs backend

# Verify environment variables
docker-compose -f docker-compose.production.yml exec backend env | grep DATABASE_URL
```

#### 2. Database Connection Issues

```bash
# Test connection
docker-compose -f docker-compose.production.yml exec backend python -c "
from sqlalchemy import create_engine
import os
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    print(conn.execute('SELECT 1'))
"
```

#### 3. Redis Connection Issues

```bash
# Test Redis
docker-compose -f docker-compose.production.yml exec backend python -c "
import redis
import os
from urllib.parse import urlparse
url = urlparse(os.getenv('REDIS_URL'))
r = redis.Redis(host=url.hostname, port=url.port, password=url.password)
print(r.ping())
"
```

#### 4. S3 Upload Failures

```bash
# Test S3 credentials
aws s3 ls s3://civicq-media-production

# Check bucket permissions
aws s3api get-bucket-acl --bucket civicq-media-production
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Check database performance
docker-compose -f docker-compose.production.yml exec postgres \
  psql -U civicq -c "SELECT * FROM pg_stat_activity;"

# Check Redis memory
docker-compose -f docker-compose.production.yml exec redis redis-cli INFO memory
```

### Emergency Procedures

**Complete System Failure:**

```bash
# 1. Stop all services
docker-compose -f docker-compose.production.yml down

# 2. Restore from backup
./infrastructure/scripts/restore.sh production <backup-name>

# 3. Restart services
docker-compose -f docker-compose.production.yml up -d

# 4. Verify
./infrastructure/scripts/health-check.sh production
```

---

## Support

- **Documentation:** See `/docs` directory
- **Issues:** GitHub Issues
- **Community:** Discord/Slack channel
- **Email:** support@civicq.com

---

## Next Steps

After successful deployment:

1. Review [INFRASTRUCTURE_OVERVIEW.md](./INFRASTRUCTURE_OVERVIEW.md)
2. Setup monitoring dashboards
3. Configure automated backups
4. Review security settings
5. Load test the application
6. Document your custom configuration

---

**Last Updated:** 2024-02-14
**Version:** 1.0.0
