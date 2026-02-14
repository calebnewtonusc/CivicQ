# CivicQ - Production Deployment Infrastructure

Complete, production-ready deployment infrastructure for CivicQ, deployable to any cloud provider.

## What's Included

This deployment infrastructure provides everything needed to deploy CivicQ to production:

### Docker Configuration
- **Multi-stage Dockerfiles** for backend (FastAPI), frontend (React), and Nginx
- **Separate build targets** for development, production, Celery worker, and Celery beat
- **Optimized images** with proper security (non-root users), caching, and health checks
- **Comprehensive .dockerignore** files to minimize build context

### Docker Compose
- `docker-compose.yml` - Local development environment
- `docker-compose.production.yml` - Production deployment configuration
- `docker-compose.staging.yml` - Staging environment

### Nginx Configuration
- Production-ready reverse proxy configuration
- SSL/TLS support with Let's Encrypt integration
- Rate limiting for API endpoints
- WebSocket support for real-time features
- Gzip compression and caching
- Security headers (CSP, HSTS, etc.)
- Static file serving optimizations

### Infrastructure as Code
- **Terraform for AWS** - Complete AWS infrastructure (VPC, RDS, ElastiCache, S3, CloudFront, ECS)
- **Variables and examples** - Comprehensive variable definitions with examples
- **Multi-environment support** - Development, staging, and production configurations

### CI/CD Pipelines
- **GitHub Actions workflows** for automated testing, building, and deployment
- **Docker build and push** - Multi-architecture builds (amd64, arm64)
- **Security scanning** - Trivy vulnerability scanning
- **Automated deployment** - Zero-downtime deployments with health checks
- **Rollback on failure** - Automatic rollback if deployment fails

### Deployment Scripts
All scripts are located in `infrastructure/scripts/`:

1. **deploy.sh** - Main deployment script with tests, backups, and health checks
2. **rollback.sh** - Emergency rollback to previous version
3. **backup.sh** - Database and media backup with S3 upload
4. **restore.sh** - Database and media restoration
5. **health-check.sh** - Comprehensive health checks for all services

All scripts are executable and include:
- Input validation
- Error handling
- Colored output
- Confirmation prompts for critical operations
- Logging

### Environment Configuration
- `.env.example` - Development environment template
- `.env.production.example` - Production environment template with comprehensive documentation
- `.env.staging.example` - Staging environment template

All files include:
- Detailed comments
- Security warnings
- Required vs optional variables
- Example values
- Deployment checklists

### Comprehensive Documentation

#### DEPLOYMENT_GUIDE.md (400+ lines)
Complete step-by-step deployment guide covering:
- Quick start (5-minute deploy)
- Prerequisites and requirements
- Deployment options (Docker Compose, Kubernetes, Managed Services)
- Step-by-step deployment for all cloud providers
- Configuration and environment setup
- Post-deployment tasks
- Monitoring and maintenance
- Troubleshooting guide

#### INFRASTRUCTURE_OVERVIEW.md (350+ lines)
Technical architecture documentation covering:
- High-level architecture diagrams
- Detailed component descriptions
- Data flow diagrams
- Security architecture
- Network architecture
- Storage architecture
- Monitoring and observability
- Disaster recovery procedures
- Cost optimization strategies

#### SCALING_GUIDE.md (500+ lines)
Comprehensive scaling guide covering:
- Performance benchmarks
- Horizontal scaling (containers, workers)
- Vertical scaling (instance sizes)
- Database scaling (indexes, replicas, sharding)
- Caching strategies (application, Redis, CDN)
- Load testing procedures
- Monitoring for scale
- Cost vs performance analysis

## Supported Cloud Providers

This infrastructure can be deployed to:

### AWS
- **ECS Fargate** - Serverless container orchestration
- **EC2** - Virtual machines with Docker Compose
- **EKS** - Kubernetes for advanced orchestration
- **RDS PostgreSQL** - Managed database
- **ElastiCache Redis** - Managed cache
- **S3** - Object storage
- **CloudFront** - CDN

### Google Cloud Platform
- **GKE** - Google Kubernetes Engine
- **Compute Engine** - VMs with Docker Compose
- **Cloud SQL** - Managed PostgreSQL
- **Memorystore** - Managed Redis
- **Cloud Storage** - Object storage
- **Cloud CDN** - Content delivery

### DigitalOcean
- **Droplets** - VPS with Docker Compose
- **Kubernetes** - Managed Kubernetes
- **Managed Databases** - PostgreSQL
- **Managed Redis** - Redis cluster
- **Spaces** - S3-compatible storage
- **CDN** - Built-in CDN

### Any VPS Provider
- Linode, Hetzner, Vultr, etc.
- Single server or multi-server setup
- Docker Compose deployment
- Manual or automated setup

## Quick Start

### Option 1: Deploy to VPS (Simplest)

```bash
# 1. SSH into your server
ssh user@your-server.com

# 2. Clone repository
git clone https://github.com/yourusername/civicq.git
cd civicq

# 3. Configure environment
cp backend/.env.production.example backend/.env.production
nano backend/.env.production  # Edit with your values

# 4. Deploy
./infrastructure/scripts/deploy.sh production
```

### Option 2: Deploy to AWS with Terraform

```bash
# 1. Configure Terraform
cd infrastructure/terraform/aws
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars  # Edit with your values

# 2. Deploy infrastructure
terraform init
terraform plan
terraform apply

# 3. Deploy application
cd ../../..
./infrastructure/scripts/deploy.sh production
```

### Option 3: Deploy via GitHub Actions

```bash
# 1. Configure GitHub secrets (see documentation)

# 2. Tag a release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 3. GitHub Actions automatically deploys
```

## File Structure

```
CivicQ/
├── backend/
│   ├── Dockerfile                      # Multi-stage backend Dockerfile
│   ├── .dockerignore                   # Docker build exclusions
│   ├── .env.example                    # Development environment
│   ├── .env.production.example         # Production environment
│   └── .env.staging.example            # Staging environment
│
├── frontend/
│   ├── Dockerfile                      # Multi-stage frontend Dockerfile
│   ├── .dockerignore                   # Docker build exclusions
│   └── nginx.conf                      # Frontend nginx config
│
├── nginx/
│   ├── Dockerfile                      # Nginx reverse proxy Dockerfile
│   └── nginx.conf                      # Production nginx config
│
├── infrastructure/
│   ├── terraform/
│   │   └── aws/
│   │       ├── main.tf                 # AWS infrastructure
│   │       ├── variables.tf            # Terraform variables
│   │       └── terraform.tfvars.example # Variable examples
│   │
│   └── scripts/
│       ├── deploy.sh                   # Main deployment script
│       ├── rollback.sh                 # Rollback script
│       ├── backup.sh                   # Backup script
│       ├── restore.sh                  # Restore script
│       └── health-check.sh             # Health check script
│
├── .github/
│   └── workflows/
│       ├── docker-build-push.yml       # Docker build workflow
│       └── deploy-production.yml       # Deployment workflow
│
├── docker-compose.yml                  # Development environment
├── docker-compose.production.yml       # Production environment
├── docker-compose.staging.yml          # Staging environment
│
├── DEPLOYMENT_GUIDE.md                 # Complete deployment guide
├── INFRASTRUCTURE_OVERVIEW.md          # Architecture documentation
└── SCALING_GUIDE.md                    # Scaling guide
```

## Key Features

### Security
- Non-root containers
- SSL/TLS encryption
- Secrets management
- Security headers
- Rate limiting
- Input validation
- CORS configuration
- Network isolation

### High Availability
- Multi-container deployment
- Health checks
- Auto-restart on failure
- Load balancing
- Database replication
- Zero-downtime deployments

### Observability
- Comprehensive logging
- Health check endpoints
- Metrics collection (Prometheus-ready)
- Error tracking (Sentry)
- Performance monitoring

### Developer Experience
- One-command deployment
- Automated tests
- Rollback capability
- Database backups
- Clear documentation
- Example configurations

## System Requirements

### Minimum (100-1,000 users)
- 2 vCPU, 4GB RAM
- PostgreSQL: db.t4g.micro
- Redis: cache.t4g.micro
- Storage: 20GB
- **Cost: ~$50-100/month**

### Recommended (1,000-10,000 users)
- 4 vCPU, 8GB RAM
- PostgreSQL: db.t4g.medium
- Redis: cache.t4g.small
- Storage: 100GB
- **Cost: ~$200-350/month**

### Production (10,000+ users)
- 8+ vCPU, 16GB+ RAM
- PostgreSQL: db.m6g.large+
- Redis: cache.m6g.medium+
- Storage: 500GB+
- CDN enabled
- **Cost: ~$600-1,500/month**

## Required Services

1. **PostgreSQL 15+** with pgvector extension
2. **Redis 7+** for caching and Celery
3. **S3-compatible storage** (AWS S3, R2, Spaces, etc.)
4. **SMTP service** (SendGrid, AWS SES, etc.)
5. **SMS service** (Twilio)
6. **AI services** (OpenAI, Anthropic)

## Environment Variables

See `backend/.env.production.example` for all 70+ environment variables with detailed documentation.

**Critical variables:**
- `SECRET_KEY` - JWT signing key
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection
- `S3_BUCKET` - Media storage bucket
- `SENDGRID_API_KEY` - Email service
- `TWILIO_*` - SMS verification
- `OPENAI_API_KEY` - Video transcription
- `ANTHROPIC_API_KEY` - Question analysis

## Monitoring

Built-in health checks for:
- Backend API
- Database connectivity
- Redis connectivity
- Celery workers
- Celery beat scheduler
- S3 storage
- SSL certificates

Run health checks:
```bash
./infrastructure/scripts/health-check.sh production
```

## Backup and Recovery

**Automated Backups:**
- Database: Daily snapshots
- Media files: Versioned in S3
- Configuration: Git repository
- Retention: 30 days

**Backup Manually:**
```bash
./infrastructure/scripts/backup.sh production
```

**Restore:**
```bash
./infrastructure/scripts/restore.sh production <backup-name>
```

## CI/CD Pipeline

GitHub Actions automatically:
1. Run tests (backend + frontend)
2. Build Docker images (multi-arch)
3. Scan for vulnerabilities
4. Create database backup
5. Deploy to production
6. Run health checks
7. Rollback on failure
8. Send notifications

## Next Steps

1. **Read Documentation:**
   - [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Step-by-step deployment
   - [INFRASTRUCTURE_OVERVIEW.md](./INFRASTRUCTURE_OVERVIEW.md) - Architecture details
   - [SCALING_GUIDE.md](./SCALING_GUIDE.md) - Scaling strategies

2. **Configure Environment:**
   - Copy `.env.production.example` to `.env.production`
   - Fill in all required variables
   - Generate secure secrets

3. **Deploy:**
   - Choose deployment method (VPS, AWS, etc.)
   - Follow quick start guide
   - Run health checks

4. **Monitor:**
   - Setup monitoring dashboards
   - Configure alerts
   - Review logs

5. **Optimize:**
   - Load test your deployment
   - Tune performance
   - Optimize costs

## Support

- **Documentation:** See `/docs` directory and markdown files
- **Issues:** GitHub Issues
- **Security:** security@civicq.com

## License

See LICENSE file

---

**Created:** 2024-02-14
**Version:** 1.0.0
**Maintained by:** CivicQ Engineering Team
