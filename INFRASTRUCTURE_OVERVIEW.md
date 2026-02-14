# CivicQ Infrastructure Overview

Comprehensive overview of CivicQ's production infrastructure architecture, components, and design decisions.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [System Components](#system-components)
- [Data Flow](#data-flow)
- [Security Architecture](#security-architecture)
- [Network Architecture](#network-architecture)
- [Storage Architecture](#storage-architecture)
- [Monitoring and Observability](#monitoring-and-observability)
- [Disaster Recovery](#disaster-recovery)

---

## Architecture Overview

CivicQ uses a modern, cloud-native microservices architecture designed for scalability, reliability, and security.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                    ┌────▼────┐
                    │   CDN   │ (CloudFront/Cloudflare)
                    │ (Static)│
                    └────┬────┘
                         │
                    ┌────▼────────┐
                    │     ALB     │ (Application Load Balancer)
                    │  /Nginx     │
                    └─┬─────────┬─┘
                      │         │
          ┌───────────▼───┐   ┌▼────────────────┐
          │   Frontend    │   │    Backend      │
          │   (React)     │   │   (FastAPI)     │
          │   Nginx       │   │   Uvicorn       │
          └───────────────┘   └─┬──────────────┬┘
                                │              │
                    ┌───────────▼──┐    ┌─────▼──────────┐
                    │  PostgreSQL  │    │     Redis      │
                    │  (pgvector)  │    │  (Cache/Queue) │
                    └──────────────┘    └────────┬───────┘
                                                 │
                                        ┌────────▼─────────┐
                                        │  Celery Workers  │
                                        │  (Background)    │
                                        └──────────────────┘
                                                 │
                                        ┌────────▼─────────┐
                                        │   S3/Storage     │
                                        │  (Media Files)   │
                                        └──────────────────┘
```

### Design Principles

1. **Scalability:** Horizontal scaling for all stateless components
2. **Reliability:** Multi-AZ deployment, automated backups, health checks
3. **Security:** Defense in depth, encryption at rest and in transit
4. **Observability:** Comprehensive logging, metrics, and tracing
5. **Cost Efficiency:** Right-sizing resources, auto-scaling

---

## System Components

### 1. Frontend (React + Nginx)

**Technology Stack:**
- React 18 with TypeScript
- Nginx for static file serving
- React Query for data fetching
- Zustand for state management

**Deployment:**
- Multi-stage Docker build
- Optimized production bundle
- Gzip compression enabled
- Browser caching configured

**Responsibilities:**
- User interface rendering
- Client-side routing
- State management
- API communication

**Scaling:**
- Horizontal: Multiple Nginx containers behind load balancer
- CDN caching for static assets
- Service worker for offline support

### 2. Backend (FastAPI + Uvicorn)

**Technology Stack:**
- Python 3.11
- FastAPI framework
- Uvicorn ASGI server
- SQLAlchemy 2.0 (async)
- Pydantic v2 for validation

**Deployment:**
- Multi-worker Uvicorn (4 workers per container)
- Health check endpoint
- Graceful shutdown handling

**Responsibilities:**
- REST API endpoints
- Business logic
- Authentication/Authorization
- Database operations
- Real-time features (WebSocket)

**Scaling:**
- Horizontal: Multiple backend containers
- Vertical: 2-4 vCPU, 4-8GB RAM per container
- Auto-scaling based on CPU/memory

### 3. Database (PostgreSQL 15 + pgvector)

**Configuration:**
- PostgreSQL 15 with pgvector extension
- Multi-AZ deployment for HA
- Read replicas for scaling reads

**Optimizations:**
- Connection pooling (SQLAlchemy)
- Indexes on frequently queried columns
- Partitioning for large tables
- Regular VACUUM and ANALYZE

**Backup Strategy:**
- Automated daily backups
- Point-in-time recovery (PITR)
- Backup retention: 30 days
- Cross-region backup replication

**Responsibilities:**
- User data
- Questions and votes
- Candidate profiles
- Election data
- Vector embeddings

### 4. Redis (Cache + Message Broker)

**Configuration:**
- Redis 7.0
- Cluster mode for production
- Persistence enabled (AOF)

**Use Cases:**
- Session storage
- Rate limiting
- Caching (API responses, queries)
- Celery message broker
- Real-time features (pub/sub)

**Scaling:**
- Vertical: 4-16GB RAM
- Horizontal: Redis Cluster with sharding

### 5. Celery (Background Tasks)

**Workers:**
- Video processing
- Email sending
- Data imports
- Analytics computation

**Beat Scheduler:**
- Ballot data refresh
- Analytics updates
- Cleanup tasks
- Report generation

**Configuration:**
- Concurrency: 4-8 workers
- Task retry with exponential backoff
- Task timeout: 300s (video processing: 900s)

### 6. Nginx (Reverse Proxy + Load Balancer)

**Features:**
- SSL/TLS termination
- Rate limiting
- Gzip compression
- Static file caching
- WebSocket proxying
- Security headers

**Configuration:**
- 4096 worker connections
- HTTP/2 enabled
- OCSP stapling
- DDoS protection

### 7. Object Storage (S3)

**Configuration:**
- S3 (or compatible: R2, Spaces)
- Versioning enabled
- Lifecycle policies
- Server-side encryption

**Content:**
- User-uploaded videos
- Profile images
- Documents/sources
- Video thumbnails
- Sprite sheets

**CDN Integration:**
- CloudFront distribution
- Edge caching
- Signed URLs for private content

---

## Data Flow

### User Request Flow

```
1. User → CDN (Static Assets)
2. User → ALB/Nginx → Frontend (HTML/JS)
3. User → ALB/Nginx → Backend API
4. Backend → Redis (Cache Check)
5. Backend → PostgreSQL (Data Fetch)
6. Backend → S3 (Media URLs)
7. Backend → Response → User
```

### Background Task Flow

```
1. API Request → Backend
2. Backend → Celery Task Queue (Redis)
3. Celery Worker → Pick Task
4. Worker → Process (e.g., video transcoding)
5. Worker → S3 Upload
6. Worker → PostgreSQL Update
7. Worker → Complete Task
```

### Real-Time Update Flow

```
1. User Action → Backend WebSocket
2. Backend → Redis Pub/Sub
3. All Connected Clients ← Receive Update
```

---

## Security Architecture

### Layers of Security

#### 1. Network Security

- VPC with private/public subnets
- Security groups (least privilege)
- Network ACLs
- WAF rules for common attacks
- DDoS protection (CloudFlare/Shield)

#### 2. Application Security

- HTTPS only (TLS 1.2+)
- CORS properly configured
- CSP headers
- XSS protection
- CSRF tokens
- SQL injection prevention (ORMs)
- Input validation (Pydantic)

#### 3. Authentication & Authorization

- JWT tokens (access + refresh)
- OAuth 2.0 (Google, Facebook)
- MFA support (TOTP)
- Password hashing (bcrypt)
- Session management (Redis)
- Role-based access control (RBAC)

#### 4. Data Security

- Encryption at rest (AES-256)
- Encryption in transit (TLS)
- Database encryption
- Secrets management (AWS Secrets Manager)
- PII data protection
- GDPR compliance

#### 5. API Security

- Rate limiting (per user/IP)
- API authentication required
- Request size limits
- Timeout protection
- Error message sanitization

---

## Network Architecture

### Production VPC Layout

```
VPC: 10.0.0.0/16
├── Public Subnets (10.0.1.0/24, 10.0.2.0/24)
│   ├── ALB
│   ├── NAT Gateway
│   └── Bastion Host
│
└── Private Subnets (10.0.10.0/24, 10.0.11.0/24)
    ├── Backend Containers
    ├── Celery Workers
    ├── RDS PostgreSQL
    └── ElastiCache Redis
```

### Availability Zones

- Multi-AZ deployment for all critical components
- Minimum 2 AZs for production
- 3 AZs for high availability

### Load Balancing

**Application Load Balancer:**
- Health checks every 30s
- Unhealthy threshold: 3 failures
- Healthy threshold: 2 successes
- Sticky sessions enabled
- Connection draining: 30s

---

## Storage Architecture

### Database Storage

**PostgreSQL:**
- SSD storage (gp3)
- Initial: 20GB
- Auto-scaling: up to 100GB
- IOPS: 3000 baseline
- Throughput: 125 MB/s

**Partitioning Strategy:**
- Questions table: by creation date (monthly)
- Votes table: by creation date (monthly)
- Analytics table: by date (daily)

### Object Storage

**S3 Bucket Structure:**
```
civicq-media-production/
├── videos/
│   ├── originals/
│   ├── transcoded/
│   └── thumbnails/
├── images/
│   ├── profiles/
│   ├── candidates/
│   └── measures/
└── documents/
    └── sources/
```

**Lifecycle Policies:**
- Transition to IA after 30 days
- Transition to Glacier after 90 days
- Delete non-current versions after 365 days

---

## Monitoring and Observability

### Metrics

**Infrastructure:**
- CPU utilization
- Memory usage
- Disk I/O
- Network throughput

**Application:**
- Request rate
- Error rate
- Response time (p50, p95, p99)
- Active users

**Database:**
- Connection count
- Query performance
- Replication lag
- Lock waits

### Logging

**Centralized Logging:**
- CloudWatch Logs (AWS)
- Log aggregation (ELK/Loki)
- Retention: 30 days

**Log Types:**
- Application logs
- Access logs
- Error logs
- Audit logs

### Alerting

**Critical Alerts:**
- Service down
- High error rate (>5%)
- Database connection failures
- Disk space >80%

**Warning Alerts:**
- High CPU (>70%)
- High memory (>80%)
- Slow queries (>1s)
- High latency (>500ms)

### Tracing

- Distributed tracing (Sentry)
- Request ID propagation
- Performance profiling

---

## Disaster Recovery

### Backup Strategy

**Database Backups:**
- Automated daily snapshots
- Manual backups before deployments
- Backup retention: 30 days
- Cross-region replication

**Application Backups:**
- Configuration files in Git
- Docker images in registry
- Infrastructure as Code (Terraform)

### Recovery Procedures

**RTO (Recovery Time Objective):** 1 hour
**RPO (Recovery Point Objective):** 24 hours

**Recovery Steps:**
1. Restore database from latest backup
2. Deploy application from tagged release
3. Restore media files from S3
4. Verify data integrity
5. Run health checks

### Failover Strategy

**Database:**
- Automatic failover to standby (Multi-AZ)
- Failover time: <60 seconds
- DNS update automatic

**Application:**
- Multiple containers across AZs
- Health check failures trigger replacement
- Zero-downtime deployments

---

## Cost Optimization

### Current Estimated Costs (Monthly)

**Small Deployment (1000 users):**
- Compute: $100-150
- Database: $50-100
- Storage: $20-50
- CDN: $10-30
- **Total: ~$200-350/month**

**Medium Deployment (10,000 users):**
- Compute: $300-500
- Database: $150-300
- Storage: $100-200
- CDN: $50-100
- **Total: ~$600-1,100/month**

**Large Deployment (100,000 users):**
- Compute: $1,000-2,000
- Database: $500-1,000
- Storage: $500-1,000
- CDN: $200-500
- **Total: ~$2,200-4,500/month**

### Optimization Strategies

1. **Right-sizing:** Match resources to actual usage
2. **Reserved Instances:** 30-60% savings for stable workloads
3. **Spot Instances:** For Celery workers (70% savings)
4. **Auto-scaling:** Scale down during low traffic
5. **S3 Lifecycle:** Move old files to cheaper storage
6. **CDN Caching:** Reduce origin requests

---

## Next Steps

- Review [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- Read [SCALING_GUIDE.md](./SCALING_GUIDE.md)
- Setup monitoring dashboards
- Configure automated backups
- Load test the system

---

**Last Updated:** 2024-02-14
**Version:** 1.0.0
