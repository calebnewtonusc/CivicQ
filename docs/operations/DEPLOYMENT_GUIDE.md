# CivicQ Deployment Guide

**Complete step-by-step deployment guide for production environments**

Version: 1.0
Last Updated: 2026-02-14
Estimated Time: 2-4 hours (first deployment)

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Deployment Architecture](#deployment-architecture)
4. [AWS Deployment](#aws-deployment)
5. [Google Cloud Deployment](#google-cloud-deployment)
6. [DigitalOcean Deployment](#digitalocean-deployment)
7. [VPS Deployment (Any Provider)](#vps-deployment-any-provider)
8. [Environment Configuration](#environment-configuration)
9. [Database Setup](#database-setup)
10. [Redis Setup](#redis-setup)
11. [Storage Configuration (S3/R2)](#storage-configuration-s3r2)
12. [Email Service Setup](#email-service-setup)
13. [CDN Setup](#cdn-setup)
14. [SSL/TLS Configuration](#ssltls-configuration)
15. [Domain and DNS Configuration](#domain-and-dns-configuration)
16. [First-Time Admin Setup](#first-time-admin-setup)
17. [Smoke Testing](#smoke-testing)
18. [Post-Deployment](#post-deployment)

---

## Prerequisites

### Required Accounts

- [ ] GitHub account (for code repository)
- [ ] Cloud provider account (AWS, Google Cloud, DigitalOcean, or VPS)
- [ ] Domain registrar account (Namecheap, Google Domains, etc.)
- [ ] SendGrid account (or SMTP provider)
- [ ] Twilio account (for SMS verification)
- [ ] Sentry account (optional, for error tracking)

### Required Tools

Install these tools on your local machine:

```bash
# Git
git --version  # Should be 2.30+

# Docker
docker --version  # Should be 20.10+
docker-compose --version  # Should be 1.29+

# PostgreSQL client (for database management)
psql --version  # Should be 15+

# AWS CLI (if using AWS)
aws --version  # Should be 2.0+

# Google Cloud CLI (if using GCP)
gcloud --version

# DigitalOcean CLI (if using DO)
doctl version

# Optional: Terraform for infrastructure as code
terraform --version
```

### Required Credentials

Before starting, gather these credentials:

- [ ] Database password (strong, 32+ characters)
- [ ] Redis password (strong, 32+ characters)
- [ ] JWT secret key (generate with `openssl rand -hex 32`)
- [ ] S3 access key and secret
- [ ] SendGrid API key
- [ ] Twilio account SID, auth token, phone number
- [ ] Google OAuth credentials (optional)
- [ ] Facebook OAuth credentials (optional)
- [ ] Sentry DSN (optional)

### System Requirements

**Minimum for Small City (1,000-5,000 voters):**
- Backend: 2 vCPU, 4GB RAM, 50GB SSD
- Database: 2 vCPU, 4GB RAM, 100GB SSD
- Redis: 1 vCPU, 1GB RAM, 10GB SSD
- Total: ~$50-100/month

**Recommended for Medium City (10,000-50,000 voters):**
- Backend: 4 vCPU, 8GB RAM, 100GB SSD
- Database: 4 vCPU, 8GB RAM, 200GB SSD
- Redis: 2 vCPU, 2GB RAM, 20GB SSD
- CDN: CloudFront or Cloudflare
- Total: ~$200-400/month

**Large City (100,000+ voters):**
- See [SCALING_GUIDE.md](SCALING_GUIDE.md)

---

## Pre-Deployment Checklist

Before deploying, complete this checklist:

### Legal and Administrative

- [ ] Obtain city authorization and approval
- [ ] Review election law compliance requirements
- [ ] Establish data retention and privacy policies
- [ ] Create terms of service and privacy policy documents
- [ ] Determine admin user list and permissions

### Technical Preparation

- [ ] Fork/clone CivicQ repository
- [ ] Review `.env.example` files for both backend and frontend
- [ ] Purchase and configure domain name
- [ ] Generate all required secret keys
- [ ] Create cloud accounts and billing setup
- [ ] Plan backup and disaster recovery strategy

### Security

- [ ] Enable 2FA on all service accounts
- [ ] Set up password manager for credentials
- [ ] Configure firewall rules
- [ ] Plan SSL certificate strategy (Let's Encrypt recommended)
- [ ] Review security best practices in [SECURITY_GUIDE.md](SECURITY_GUIDE.md)

---

## Deployment Architecture

CivicQ consists of these components:

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                              │
└─────────────┬───────────────────────────────────────────────┘
              │
      ┌───────▼────────┐
      │   CloudFlare   │  ← CDN + DDoS Protection
      │  (or similar)  │
      └───────┬────────┘
              │
      ┌───────▼────────┐
      │  Load Balancer │  ← SSL Termination
      └───────┬────────┘
              │
    ┌─────────┴─────────┐
    │                   │
┌───▼────┐        ┌─────▼──────┐
│ Nginx  │        │   Nginx    │  ← Reverse Proxy + Static Files
└───┬────┘        └─────┬──────┘
    │                   │
┌───▼────────┐    ┌─────▼──────────┐
│  Frontend  │    │    Backend     │  ← React App / FastAPI
│   (React)  │    │   (FastAPI)    │
└────────────┘    └────┬───────────┘
                       │
            ┌──────────┼──────────┐
            │          │          │
      ┌─────▼───┐  ┌──▼────┐  ┌──▼────────┐
      │PostgreSQL│  │ Redis │  │  Celery   │
      │ +pgvector│  │       │  │  Workers  │
      └──────────┘  └───────┘  └───────────┘
                                     │
                              ┌──────▼──────┐
                              │  S3/R2/CDN  │
                              │   (Media)   │
                              └─────────────┘
```

**Key Components:**

1. **Frontend**: React 18 + TypeScript, served via Nginx
2. **Backend**: FastAPI (Python 3.11), running in Uvicorn
3. **Database**: PostgreSQL 15+ with pgvector extension
4. **Cache**: Redis for rate limiting and caching
5. **Workers**: Celery for background tasks (video processing, emails)
6. **Storage**: S3-compatible object storage for videos/images
7. **CDN**: CloudFront/Cloudflare for media delivery
8. **Proxy**: Nginx for SSL termination and reverse proxy

---

## AWS Deployment

### Step 1: Set Up VPC and Networking

```bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure

# Create VPC (or use default)
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=civicq-vpc}]'

# Create subnets (public and private)
aws ec2 create-subnet --vpc-id vpc-xxxxx --cidr-block 10.0.1.0/24 --availability-zone us-west-2a
aws ec2 create-subnet --vpc-id vpc-xxxxx --cidr-block 10.0.2.0/24 --availability-zone us-west-2b

# Create internet gateway
aws ec2 create-internet-gateway --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=civicq-igw}]'
aws ec2 attach-internet-gateway --vpc-id vpc-xxxxx --internet-gateway-id igw-xxxxx

# Create security groups
aws ec2 create-security-group --group-name civicq-web --description "Web traffic" --vpc-id vpc-xxxxx
aws ec2 create-security-group --group-name civicq-db --description "Database access" --vpc-id vpc-xxxxx

# Allow HTTP/HTTPS
aws ec2 authorize-security-group-ingress --group-id sg-xxxxx --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id sg-xxxxx --protocol tcp --port 443 --cidr 0.0.0.0/0
```

### Step 2: Create RDS PostgreSQL Database

```bash
# Create DB subnet group
aws rds create-db-subnet-group \
  --db-subnet-group-name civicq-db-subnet \
  --db-subnet-group-description "CivicQ Database Subnets" \
  --subnet-ids subnet-xxxxx subnet-yyyyy

# Create RDS instance with pgvector support
aws rds create-db-instance \
  --db-instance-identifier civicq-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 15.4 \
  --master-username civicq \
  --master-user-password 'YOUR_STRONG_PASSWORD' \
  --allocated-storage 100 \
  --storage-type gp3 \
  --vpc-security-group-ids sg-xxxxx \
  --db-subnet-group-name civicq-db-subnet \
  --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00" \
  --publicly-accessible false \
  --multi-az true \
  --enable-performance-insights \
  --tags Key=Name,Value=civicq-production

# Wait for DB to be available
aws rds wait db-instance-available --db-instance-identifier civicq-db

# Get endpoint
aws rds describe-db-instances --db-instance-identifier civicq-db --query 'DBInstances[0].Endpoint.Address'
```

### Step 3: Create ElastiCache Redis

```bash
# Create cache subnet group
aws elasticache create-cache-subnet-group \
  --cache-subnet-group-name civicq-redis-subnet \
  --cache-subnet-group-description "CivicQ Redis Subnets" \
  --subnet-ids subnet-xxxxx subnet-yyyyy

# Create Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id civicq-redis \
  --engine redis \
  --engine-version 7.0 \
  --cache-node-type cache.t3.micro \
  --num-cache-nodes 1 \
  --cache-subnet-group-name civicq-redis-subnet \
  --security-group-ids sg-xxxxx \
  --preferred-maintenance-window "sun:05:00-sun:06:00" \
  --snapshot-retention-limit 5 \
  --snapshot-window "03:00-05:00"

# Get endpoint
aws elasticache describe-cache-clusters --cache-cluster-id civicq-redis --show-cache-node-info
```

### Step 4: Create S3 Bucket

```bash
# Create bucket
aws s3api create-bucket \
  --bucket civicq-media-production \
  --region us-west-2 \
  --create-bucket-configuration LocationConstraint=us-west-2

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket civicq-media-production \
  --versioning-configuration Status=Enabled

# Set up lifecycle policy (delete old versions after 90 days)
cat > lifecycle.json << 'EOF'
{
  "Rules": [
    {
      "Id": "DeleteOldVersions",
      "Status": "Enabled",
      "NoncurrentVersionExpiration": {
        "NoncurrentDays": 90
      }
    }
  ]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
  --bucket civicq-media-production \
  --lifecycle-configuration file://lifecycle.json

# Set CORS policy
cat > cors.json << 'EOF'
{
  "CORSRules": [
    {
      "AllowedOrigins": ["https://civicq.com", "https://www.civicq.com"],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 3000
    }
  ]
}
EOF

aws s3api put-bucket-cors \
  --bucket civicq-media-production \
  --cors-configuration file://cors.json

# Create IAM user for S3 access
aws iam create-user --user-name civicq-s3-access

# Attach S3 policy
cat > s3-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::civicq-media-production",
        "arn:aws:s3:::civicq-media-production/*"
      ]
    }
  ]
}
EOF

aws iam put-user-policy \
  --user-name civicq-s3-access \
  --policy-name S3Access \
  --policy-document file://s3-policy.json

# Create access keys
aws iam create-access-key --user-name civicq-s3-access
# Save these keys securely!
```

### Step 5: Deploy Application with ECS

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name civicq-production

# Create ECR repositories
aws ecr create-repository --repository-name civicq/backend
aws ecr create-repository --repository-name civicq/frontend
aws ecr create-repository --repository-name civicq/nginx

# Build and push Docker images
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com

# Build images
docker build -t civicq/backend ./backend
docker build -t civicq/nginx ./nginx

# Tag and push
docker tag civicq/backend:latest ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/civicq/backend:latest
docker push ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/civicq/backend:latest

# Create task definition (see task-definition.json)
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster civicq-production \
  --service-name civicq-backend \
  --task-definition civicq-backend \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}"
```

### Step 6: Set Up Application Load Balancer

```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name civicq-alb \
  --subnets subnet-xxxxx subnet-yyyyy \
  --security-groups sg-xxxxx

# Create target group
aws elbv2 create-target-group \
  --name civicq-backend-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxxxx \
  --target-type ip \
  --health-check-path /health

# Create listener
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:... \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:... \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...
```

### Step 7: Set Up CloudFront CDN

```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
  --distribution-config file://cloudfront-config.json

# Example cloudfront-config.json
cat > cloudfront-config.json << 'EOF'
{
  "CallerReference": "civicq-cdn-2026",
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-civicq-media",
        "DomainName": "civicq-media-production.s3.us-west-2.amazonaws.com",
        "S3OriginConfig": {
          "OriginAccessIdentity": ""
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-civicq-media",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 2,
      "Items": ["GET", "HEAD"]
    },
    "MinTTL": 0,
    "DefaultTTL": 86400,
    "MaxTTL": 31536000
  },
  "Enabled": true
}
EOF
```

---

## Google Cloud Deployment

### Step 1: Set Up GCP Project

```bash
# Install gcloud CLI
# See: https://cloud.google.com/sdk/docs/install

# Initialize and authenticate
gcloud init
gcloud auth login

# Create project
gcloud projects create civicq-production --name="CivicQ Production"
gcloud config set project civicq-production

# Enable required APIs
gcloud services enable \
  compute.googleapis.com \
  sql-component.googleapis.com \
  sqladmin.googleapis.com \
  storage-api.googleapis.com \
  container.googleapis.com \
  cloudresourcemanager.googleapis.com

# Set default region
gcloud config set compute/region us-west2
gcloud config set compute/zone us-west2-a
```

### Step 2: Create Cloud SQL PostgreSQL

```bash
# Create Cloud SQL instance
gcloud sql instances create civicq-db \
  --database-version=POSTGRES_15 \
  --tier=db-custom-2-7680 \
  --region=us-west2 \
  --network=default \
  --no-assign-ip \
  --enable-bin-log \
  --backup-start-time=03:00 \
  --maintenance-window-day=SUN \
  --maintenance-window-hour=04

# Set root password
gcloud sql users set-password postgres \
  --instance=civicq-db \
  --password='YOUR_STRONG_PASSWORD'

# Create database
gcloud sql databases create civicq --instance=civicq-db

# Create application user
gcloud sql users create civicq \
  --instance=civicq-db \
  --password='YOUR_STRONG_PASSWORD'

# Get connection name
gcloud sql instances describe civicq-db --format="value(connectionName)"
# Format: PROJECT:REGION:INSTANCE
```

### Step 3: Create Memorystore Redis

```bash
# Create Redis instance
gcloud redis instances create civicq-redis \
  --size=1 \
  --region=us-west2 \
  --redis-version=redis_7_0 \
  --network=default \
  --maintenance-window-day=sunday \
  --maintenance-window-hour=5

# Get Redis host and port
gcloud redis instances describe civicq-redis --region=us-west2
```

### Step 4: Create Cloud Storage Bucket

```bash
# Create bucket
gcloud storage buckets create gs://civicq-media-production \
  --location=us-west2 \
  --uniform-bucket-level-access

# Set lifecycle policy
cat > lifecycle.json << 'EOF'
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "numNewerVersions": 3,
          "isLive": false
        }
      }
    ]
  }
}
EOF

gcloud storage buckets update gs://civicq-media-production --lifecycle-file=lifecycle.json

# Set CORS
cat > cors.json << 'EOF'
[
  {
    "origin": ["https://civicq.com"],
    "method": ["GET", "PUT", "POST", "DELETE"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]
EOF

gcloud storage buckets update gs://civicq-media-production --cors-file=cors.json

# Create service account for bucket access
gcloud iam service-accounts create civicq-storage \
  --display-name="CivicQ Storage Access"

# Grant permissions
gcloud storage buckets add-iam-policy-binding gs://civicq-media-production \
  --member="serviceAccount:civicq-storage@civicq-production.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# Create and download key
gcloud iam service-accounts keys create civicq-storage-key.json \
  --iam-account=civicq-storage@civicq-production.iam.gserviceaccount.com
```

### Step 5: Deploy with Cloud Run

```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/civicq-production/backend ./backend
gcloud builds submit --tag gcr.io/civicq-production/nginx ./nginx

# Deploy backend
gcloud run deploy civicq-backend \
  --image gcr.io/civicq-production/backend \
  --platform managed \
  --region us-west2 \
  --allow-unauthenticated \
  --min-instances 1 \
  --max-instances 10 \
  --memory 2Gi \
  --cpu 2 \
  --set-env-vars "DATABASE_URL=postgresql://civicq:PASSWORD@/civicq?host=/cloudsql/PROJECT:REGION:INSTANCE" \
  --set-cloudsql-instances PROJECT:REGION:INSTANCE

# Deploy frontend
gcloud run deploy civicq-frontend \
  --image gcr.io/civicq-production/nginx \
  --platform managed \
  --region us-west2 \
  --allow-unauthenticated \
  --min-instances 1 \
  --max-instances 5
```

### Step 6: Set Up Cloud CDN

```bash
# Create load balancer with CDN
gcloud compute backend-buckets create civicq-media-backend \
  --gcs-bucket-name=civicq-media-production \
  --enable-cdn

# Create URL map
gcloud compute url-maps create civicq-cdn \
  --default-backend-bucket=civicq-media-backend

# Create target HTTP proxy
gcloud compute target-http-proxies create civicq-cdn-proxy \
  --url-map=civicq-cdn

# Create forwarding rule
gcloud compute forwarding-rules create civicq-cdn-rule \
  --global \
  --target-http-proxy=civicq-cdn-proxy \
  --ports=80
```

---

## DigitalOcean Deployment

### Step 1: Set Up DigitalOcean Account

```bash
# Install doctl
# macOS: brew install doctl
# Linux: snap install doctl

# Authenticate
doctl auth init

# Create project
doctl projects create --name "CivicQ Production" --purpose "Civic engagement platform"
```

### Step 2: Create Managed Database

```bash
# Create PostgreSQL cluster
doctl databases create civicq-db \
  --engine pg \
  --version 15 \
  --region nyc3 \
  --size db-s-2vcpu-4gb \
  --num-nodes 1

# Wait for cluster to be ready
doctl databases list

# Get connection details
doctl databases connection civicq-db

# Create database
doctl databases db create civicq-db civicq

# Create user
doctl databases user create civicq-db civicq
```

### Step 3: Create Managed Redis

```bash
# Create Redis cluster
doctl databases create civicq-redis \
  --engine redis \
  --version 7 \
  --region nyc3 \
  --size db-s-1vcpu-1gb \
  --num-nodes 1

# Get connection details
doctl databases connection civicq-redis
```

### Step 4: Create Spaces (S3-compatible storage)

```bash
# Create Space
doctl compute space create civicq-media \
  --region nyc3

# Set CORS
cat > cors.xml << 'EOF'
<CORSConfiguration>
  <CORSRule>
    <AllowedOrigin>https://civicq.com</AllowedOrigin>
    <AllowedMethod>GET</AllowedMethod>
    <AllowedMethod>PUT</AllowedMethod>
    <AllowedMethod>POST</AllowedMethod>
    <AllowedMethod>DELETE</AllowedMethod>
    <AllowedHeader>*</AllowedHeader>
    <MaxAgeSeconds>3000</MaxAgeSeconds>
  </CORSRule>
</CORSConfiguration>
EOF

# Generate Spaces access keys
doctl compute access-key create
# Save these keys!
```

### Step 5: Deploy with App Platform

```bash
# Create app spec
cat > app.yaml << 'EOF'
name: civicq-production
region: nyc

databases:
  - name: civicq-db
    engine: PG
    version: "15"
    size: db-s-2vcpu-4gb

services:
  - name: backend
    github:
      repo: your-org/civicq
      branch: main
      deploy_on_push: true
    dockerfile_path: backend/Dockerfile
    http_port: 8000
    instance_count: 2
    instance_size_slug: professional-s
    routes:
      - path: /api
    envs:
      - key: DATABASE_URL
        scope: RUN_TIME
        type: SECRET
      - key: SECRET_KEY
        scope: RUN_TIME
        type: SECRET
    health_check:
      http_path: /health

  - name: frontend
    github:
      repo: your-org/civicq
      branch: main
    dockerfile_path: nginx/Dockerfile
    http_port: 80
    instance_count: 1
    instance_size_slug: basic-s
    routes:
      - path: /
EOF

# Deploy app
doctl apps create --spec app.yaml

# Get app URL
doctl apps list
```

### Step 6: Configure CDN

```bash
# Enable CDN for Space
doctl compute cdn create \
  --origin civicq-media.nyc3.digitaloceanspaces.com \
  --certificate-id your-cert-id \
  --ttl 3600

# Get CDN endpoint
doctl compute cdn list
```

---

## VPS Deployment (Any Provider)

This section covers deploying to any VPS (Linode, Vultr, Hetzner, etc.) using Docker Compose.

### Step 1: Provision VPS

**Minimum Specs:**
- 4 vCPU
- 8 GB RAM
- 100 GB SSD
- Ubuntu 22.04 LTS

**Providers:**
- Linode: $48/month (Dedicated 8GB)
- Vultr: $48/month (8GB Memory)
- Hetzner: ~€20/month (CPX31)

### Step 2: Initial Server Setup

```bash
# SSH into server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Create non-root user
adduser civicq
usermod -aG sudo civicq
usermod -aG docker civicq

# Set up firewall
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# Switch to civicq user
su - civicq
```

### Step 3: Clone and Configure

```bash
# Clone repository
cd /opt
sudo git clone https://github.com/your-org/civicq.git
sudo chown -R civicq:civicq civicq
cd civicq

# Copy environment files
cp backend/.env.example backend/.env.production
cp frontend/.env.example frontend/.env.production

# Generate secrets
openssl rand -hex 32  # For SECRET_KEY
openssl rand -hex 32  # For POSTGRES_PASSWORD
openssl rand -hex 32  # For REDIS_PASSWORD

# Edit environment files
nano backend/.env.production
nano frontend/.env.production
```

### Step 4: Configure Environment

Edit `backend/.env.production`:

```bash
ENVIRONMENT=production
DEBUG=false

# Generate with: openssl rand -hex 32
SECRET_KEY=your-secret-key-here

# Your domain
FRONTEND_URL=https://civicq.example.com
BACKEND_URL=https://api.civicq.example.com
ALLOWED_ORIGINS=https://civicq.example.com,https://www.civicq.example.com

# Database (Docker internal)
DATABASE_URL=postgresql://civicq:YOUR_DB_PASSWORD@postgres:5432/civicq

# Redis (Docker internal)
REDIS_URL=redis://:YOUR_REDIS_PASSWORD@redis:6379/0
CELERY_BROKER_URL=redis://:YOUR_REDIS_PASSWORD@redis:6379/1
CELERY_RESULT_BACKEND=redis://:YOUR_REDIS_PASSWORD@redis:6379/1

# S3 (use DigitalOcean Spaces, Backblaze B2, or AWS)
S3_BUCKET=civicq-media
S3_REGION=nyc3
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_ENDPOINT=https://nyc3.digitaloceanspaces.com

# Email
SENDGRID_API_KEY=your-sendgrid-api-key
EMAIL_FROM=noreply@civicq.example.com

# SMS
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890

# Error tracking
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO
```

Create `.env` file for docker-compose:

```bash
# Create .env file in project root
cat > .env << 'EOF'
POSTGRES_DB=civicq
POSTGRES_USER=civicq
POSTGRES_PASSWORD=your-postgres-password-here
REDIS_PASSWORD=your-redis-password-here
SECRET_KEY=your-secret-key-here
DOMAIN=civicq.example.com
DATA_PATH=/opt/civicq/data
EOF
```

### Step 5: Initialize Data Directories

```bash
# Create data directories
mkdir -p /opt/civicq/data/postgres
mkdir -p /opt/civicq/data/redis
mkdir -p /opt/civicq/nginx/ssl

# Set permissions
sudo chown -R civicq:civicq /opt/civicq/data
```

### Step 6: Deploy with Docker Compose

```bash
# Build images
docker-compose -f docker-compose.production.yml build

# Start services
docker-compose -f docker-compose.production.yml up -d

# Check status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f backend
```

### Step 7: Initialize Database

```bash
# Run migrations
docker-compose -f docker-compose.production.yml exec backend alembic upgrade head

# Create first admin user (interactive)
docker-compose -f docker-compose.production.yml exec backend python -m app.scripts.create_admin
```

### Step 8: Set Up SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Stop nginx temporarily
docker-compose -f docker-compose.production.yml stop nginx

# Obtain certificate
sudo certbot certonly --standalone \
  -d civicq.example.com \
  -d www.civicq.example.com \
  -d api.civicq.example.com \
  --email admin@example.com \
  --agree-tos

# Copy certificates to nginx directory
sudo cp /etc/letsencrypt/live/civicq.example.com/fullchain.pem /opt/civicq/nginx/ssl/
sudo cp /etc/letsencrypt/live/civicq.example.com/privkey.pem /opt/civicq/nginx/ssl/

# Set permissions
sudo chown civicq:civicq /opt/civicq/nginx/ssl/*

# Restart nginx
docker-compose -f docker-compose.production.yml start nginx

# Set up auto-renewal
sudo certbot renew --dry-run

# Add to crontab
echo "0 0 * * * certbot renew --quiet && cp /etc/letsencrypt/live/civicq.example.com/*.pem /opt/civicq/nginx/ssl/ && docker-compose -f /opt/civicq/docker-compose.production.yml restart nginx" | sudo crontab -
```

---

## Environment Configuration

### Backend Environment Variables

See `backend/.env.example` for complete list. Critical variables:

```bash
# Security (REQUIRED)
SECRET_KEY=                    # Generate with: openssl rand -hex 32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7

# URLs (REQUIRED)
FRONTEND_URL=                  # https://civicq.example.com
BACKEND_URL=                   # https://api.civicq.example.com
ALLOWED_ORIGINS=               # Comma-separated frontend URLs

# Database (REQUIRED)
DATABASE_URL=                  # postgresql://user:pass@host:5432/dbname

# Redis (REQUIRED)
REDIS_URL=                     # redis://[:password@]host:6379/0
CELERY_BROKER_URL=             # redis://[:password@]host:6379/1

# Storage (REQUIRED for video)
S3_BUCKET=
S3_REGION=
S3_ACCESS_KEY=
S3_SECRET_KEY=
S3_ENDPOINT=                   # Optional for non-AWS S3

# Email (REQUIRED)
SENDGRID_API_KEY=              # Or use SMTP_* variables

# SMS (REQUIRED for verification)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# Optional but recommended
SENTRY_DSN=                    # Error tracking
GOOGLE_CLIENT_ID=              # OAuth login
FACEBOOK_CLIENT_ID=            # OAuth login
```

### Frontend Environment Variables

See `frontend/.env.example` for complete list. Critical variables:

```bash
# API (REQUIRED)
REACT_APP_API_URL=             # https://api.civicq.example.com/api
REACT_APP_BASE_URL=            # https://civicq.example.com

# Environment (REQUIRED)
REACT_APP_ENV=production

# Optional
REACT_APP_GOOGLE_ANALYTICS_ID=
REACT_APP_SENTRY_DSN=
REACT_APP_GOOGLE_MAPS_API_KEY=
```

---

## Database Setup

### PostgreSQL Installation

#### Option 1: Managed Database (Recommended)

Use managed PostgreSQL from your cloud provider:
- AWS RDS
- Google Cloud SQL
- DigitalOcean Managed Database
- Neon (serverless)

#### Option 2: Self-Hosted with Docker

Included in `docker-compose.production.yml`.

### Install pgvector Extension

```bash
# Connect to database
psql $DATABASE_URL

# Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

# Verify
\dx
```

### Run Migrations

```bash
# Using Alembic
cd backend
alembic upgrade head

# Or with Docker
docker-compose -f docker-compose.production.yml exec backend alembic upgrade head
```

### Database Configuration

Recommended PostgreSQL settings for production:

```sql
-- Performance tuning
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET work_mem = '1MB';

-- Restart PostgreSQL to apply
SELECT pg_reload_conf();
```

### Create Indexes

```sql
-- Key indexes for performance (included in migrations)
CREATE INDEX IF NOT EXISTS idx_questions_city_id ON questions(city_id);
CREATE INDEX IF NOT EXISTS idx_questions_contest_id ON questions(contest_id);
CREATE INDEX IF NOT EXISTS idx_questions_created_at ON questions(created_at);
CREATE INDEX IF NOT EXISTS idx_votes_question_id ON votes(question_id);
CREATE INDEX IF NOT EXISTS idx_votes_user_id ON votes(user_id);
```

---

## Redis Setup

### Redis Installation

#### Option 1: Managed Redis (Recommended)

- AWS ElastiCache
- Google Memorystore
- DigitalOcean Managed Redis
- Redis Cloud

#### Option 2: Self-Hosted with Docker

Included in `docker-compose.production.yml`.

### Redis Configuration

```bash
# Connect to Redis
redis-cli -h your-redis-host -a your-password

# Set memory limit
CONFIG SET maxmemory 512mb
CONFIG SET maxmemory-policy allkeys-lru

# Enable persistence
CONFIG SET appendonly yes
CONFIG SET save "60 1000"

# Set password
CONFIG SET requirepass your-strong-password

# Verify
INFO memory
INFO persistence
```

### Redis Monitoring

```bash
# Monitor commands
redis-cli -h your-host -a your-password MONITOR

# Get stats
redis-cli -h your-host -a your-password INFO stats

# Check memory usage
redis-cli -h your-host -a your-password INFO memory
```

---

## Storage Configuration (S3/R2)

### AWS S3

See [AWS Deployment](#aws-deployment) section.

### Cloudflare R2 (Recommended for cost savings)

```bash
# Create R2 bucket via Cloudflare dashboard
# No egress fees!

# Generate R2 API token
# Dashboard > R2 > Manage R2 API Tokens

# Configure in .env
S3_BUCKET=civicq-media
S3_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com
S3_ACCESS_KEY=your-r2-access-key
S3_SECRET_KEY=your-r2-secret-key
S3_REGION=auto
```

### DigitalOcean Spaces

```bash
# Create Space via DO control panel

# Generate access keys
# API > Spaces access keys

# Configure in .env
S3_BUCKET=civicq-media
S3_ENDPOINT=https://nyc3.digitaloceanspaces.com
S3_ACCESS_KEY=your-spaces-access-key
S3_SECRET_KEY=your-spaces-secret-key
S3_REGION=nyc3
```

### Backblaze B2

```bash
# Create bucket via B2 web UI

# Create application key
# App Keys > Add a New Application Key

# Configure in .env
S3_BUCKET=civicq-media
S3_ENDPOINT=https://s3.us-west-002.backblazeb2.com
S3_ACCESS_KEY=your-b2-key-id
S3_SECRET_KEY=your-b2-application-key
S3_REGION=us-west-002
```

### Storage Bucket CORS Configuration

All S3-compatible services need CORS configured:

```xml
<CORSConfiguration>
  <CORSRule>
    <AllowedOrigin>https://civicq.example.com</AllowedOrigin>
    <AllowedOrigin>https://www.civicq.example.com</AllowedOrigin>
    <AllowedMethod>GET</AllowedMethod>
    <AllowedMethod>PUT</AllowedMethod>
    <AllowedMethod>POST</AllowedMethod>
    <AllowedMethod>DELETE</AllowedMethod>
    <AllowedMethod>HEAD</AllowedMethod>
    <AllowedHeader>*</AllowedHeader>
    <MaxAgeSeconds>3000</MaxAgeSeconds>
  </CORSRule>
</CORSConfiguration>
```

---

## Email Service Setup

### SendGrid (Recommended)

```bash
# 1. Sign up at sendgrid.com
# 2. Verify your domain
# 3. Create API key with "Mail Send" permissions
# 4. Configure in .env

SENDGRID_API_KEY=SG.xxxxxxxxxx
EMAIL_FROM=noreply@civicq.example.com
```

**Domain Verification:**

Add these DNS records:

```
Type: CNAME
Host: em1234.civicq.example.com
Value: u1234567.wl123.sendgrid.net

Type: TXT
Host: civicq.example.com
Value: v=spf1 include:sendgrid.net ~all
```

### Alternative: SMTP (Gmail, Outlook, etc.)

```bash
# Gmail example
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Generate at google.com/settings/security
EMAIL_FROM=your-email@gmail.com
```

### Alternative: Amazon SES

```bash
# 1. Verify domain in SES console
# 2. Create SMTP credentials
# 3. Move out of sandbox

SMTP_HOST=email-smtp.us-west-2.amazonaws.com
SMTP_PORT=587
SMTP_USER=your-smtp-username
SMTP_PASSWORD=your-smtp-password
EMAIL_FROM=noreply@civicq.example.com
```

### Test Email Configuration

```bash
# Send test email
docker-compose exec backend python -m app.scripts.test_email \
  --to your-email@example.com \
  --subject "CivicQ Email Test"
```

---

## CDN Setup

### CloudFront (AWS)

See [AWS Deployment](#aws-deployment) section.

### Cloudflare CDN

```bash
# 1. Add site to Cloudflare
# 2. Update nameservers at your domain registrar
# 3. Configure DNS records

# A record for main site
Type: A
Name: @
Value: your-server-ip
Proxy: Enabled (orange cloud)

# CNAME for www
Type: CNAME
Name: www
Value: civicq.example.com
Proxy: Enabled

# CNAME for API
Type: CNAME
Name: api
Value: civicq.example.com
Proxy: Enabled

# CNAME for media CDN
Type: CNAME
Name: media
Value: your-s3-bucket-url
Proxy: Enabled
```

**Cloudflare Settings:**

- SSL/TLS: Full (strict)
- Minimum TLS Version: 1.3
- Always Use HTTPS: On
- Auto Minify: HTML, CSS, JS
- Brotli: On
- Cache Level: Standard
- Browser Cache TTL: Respect Existing Headers

### DigitalOcean CDN

```bash
# Already covered in DO Spaces section
# CDN is automatically available for Spaces
```

---

## SSL/TLS Configuration

### Let's Encrypt (Free)

#### Option 1: Certbot (Standalone)

```bash
# Install certbot
sudo apt install certbot

# Obtain certificate
sudo certbot certonly --standalone \
  -d civicq.example.com \
  -d www.civicq.example.com \
  -d api.civicq.example.com \
  --email admin@example.com \
  --agree-tos

# Certificates saved to:
# /etc/letsencrypt/live/civicq.example.com/fullchain.pem
# /etc/letsencrypt/live/civicq.example.com/privkey.pem

# Auto-renewal (runs twice daily)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

#### Option 2: Certbot with Nginx

```bash
# Install certbot nginx plugin
sudo apt install python3-certbot-nginx

# Obtain and configure automatically
sudo certbot --nginx \
  -d civicq.example.com \
  -d www.civicq.example.com \
  -d api.civicq.example.com
```

#### Option 3: DNS Challenge (for wildcards)

```bash
# Obtain wildcard certificate
sudo certbot certonly --manual \
  --preferred-challenges dns \
  -d civicq.example.com \
  -d *.civicq.example.com

# Follow prompts to add TXT records to DNS
```

### AWS Certificate Manager (ACM)

```bash
# Request certificate
aws acm request-certificate \
  --domain-name civicq.example.com \
  --subject-alternative-names www.civicq.example.com api.civicq.example.com \
  --validation-method DNS

# Get validation records
aws acm describe-certificate --certificate-arn arn:aws:acm:...

# Add CNAME records to your DNS
# ACM will automatically validate and issue certificate
```

### Cloudflare SSL

Automatic! Just enable:
- Dashboard > SSL/TLS > Overview > Full (strict)
- Edge Certificates > Always Use HTTPS: On
- Edge Certificates > Minimum TLS Version: 1.3

---

## Domain and DNS Configuration

### DNS Records

Configure these DNS records at your registrar:

```
# Main site (A record or CNAME to your server/load balancer)
Type: A
Name: @
Value: 123.456.789.0
TTL: 3600

# WWW subdomain
Type: CNAME
Name: www
Value: civicq.example.com
TTL: 3600

# API subdomain
Type: CNAME
Name: api
Value: civicq.example.com
TTL: 3600

# Media CDN (points to CloudFront/CDN)
Type: CNAME
Name: media
Value: d1234567890.cloudfront.net
TTL: 3600

# Email (SPF, DKIM for SendGrid)
Type: TXT
Name: @
Value: v=spf1 include:sendgrid.net ~all
TTL: 3600

Type: CNAME
Name: em1234
Value: u1234567.wl123.sendgrid.net
TTL: 3600
```

### Domain Verification

```bash
# Verify DNS propagation
dig civicq.example.com
dig www.civicq.example.com
dig api.civicq.example.com

# Or use online tools
# https://dnschecker.org/
```

---

## First-Time Admin Setup

### Create Admin User

```bash
# Option 1: Using management script
docker-compose exec backend python -c "
from app.services.auth import create_admin_user
create_admin_user(
    email='admin@civicq.example.com',
    password='ChangeThisPassword123!',
    full_name='System Administrator'
)
"

# Option 2: Using SQL
docker-compose exec postgres psql -U civicq -d civicq -c "
INSERT INTO users (email, hashed_password, full_name, role, is_verified, created_at)
VALUES (
  'admin@civicq.example.com',
  '\$2b\$12\$HASHED_PASSWORD_HERE',  -- Generate with bcrypt
  'System Administrator',
  'super_admin',
  true,
  NOW()
);
"
```

### Generate Password Hash

```bash
# Generate bcrypt hash
docker-compose exec backend python -c "
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
print(pwd_context.hash('YourPassword123!'))
"
```

### Access Admin Panel

1. Navigate to `https://civicq.example.com/admin`
2. Log in with admin credentials
3. Complete initial setup wizard:
   - [ ] Configure system settings
   - [ ] Set up first city
   - [ ] Import ballot data
   - [ ] Test question submission
   - [ ] Test candidate portal

---

## Smoke Testing

### Automated Tests

```bash
# Run health checks
./scripts/health-check.sh

# Test all endpoints
./scripts/test-all.sh
```

### Manual Smoke Tests

**Backend API:**

```bash
# Health check
curl https://api.civicq.example.com/health

# API documentation
open https://api.civicq.example.com/docs

# Test authentication
curl -X POST https://api.civicq.example.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "full_name": "Test User"
  }'
```

**Frontend:**

- [ ] Homepage loads
- [ ] Can select city
- [ ] Can view ballot
- [ ] Can submit question (after auth)
- [ ] Can vote on questions
- [ ] Video player works
- [ ] Mobile responsive
- [ ] No console errors

**Database:**

```bash
# Check connection
docker-compose exec postgres psql -U civicq -c "SELECT version();"

# Check tables
docker-compose exec postgres psql -U civicq -d civicq -c "\dt"

# Check data
docker-compose exec postgres psql -U civicq -d civicq -c "SELECT COUNT(*) FROM users;"
```

**Redis:**

```bash
# Check connection
docker-compose exec redis redis-cli -a $REDIS_PASSWORD ping

# Check memory
docker-compose exec redis redis-cli -a $REDIS_PASSWORD INFO memory
```

**Storage:**

```bash
# Test upload (using AWS CLI)
echo "test" > test.txt
aws s3 cp test.txt s3://civicq-media/test.txt --endpoint-url=$S3_ENDPOINT

# Test download
aws s3 cp s3://civicq-media/test.txt - --endpoint-url=$S3_ENDPOINT

# Cleanup
aws s3 rm s3://civicq-media/test.txt --endpoint-url=$S3_ENDPOINT
```

**Email:**

```bash
# Send test email
docker-compose exec backend python -m app.scripts.test_email
```

**Celery Workers:**

```bash
# Check worker status
docker-compose exec backend celery -A app.worker inspect active

# Check scheduled tasks
docker-compose exec backend celery -A app.worker inspect scheduled
```

### Performance Tests

```bash
# Load test with Apache Bench
ab -n 1000 -c 10 https://civicq.example.com/

# API load test
ab -n 1000 -c 10 https://api.civicq.example.com/api/v1/questions
```

---

## Post-Deployment

### Security Hardening

- [ ] Change all default passwords
- [ ] Enable firewall rules
- [ ] Configure fail2ban
- [ ] Set up intrusion detection
- [ ] Enable audit logging
- [ ] Review OWASP Top 10 checklist

### Monitoring Setup

- [ ] Configure Sentry for error tracking
- [ ] Set up uptime monitoring (UptimeRobot, Pingdom)
- [ ] Configure log aggregation (Papertrail, Loggly)
- [ ] Set up performance monitoring (New Relic, DataDog)
- [ ] Create monitoring dashboards

See [MONITORING_RUNBOOK.md](MONITORING_RUNBOOK.md) for details.

### Backup Configuration

- [ ] Enable automated database backups
- [ ] Configure S3 bucket versioning
- [ ] Test backup restoration
- [ ] Document backup procedures
- [ ] Set up offsite backup storage

See [BACKUP_RECOVERY.md](BACKUP_RECOVERY.md) for details.

### Documentation

- [ ] Document server IP addresses
- [ ] Record all credentials in password manager
- [ ] Create runbook for common operations
- [ ] Document emergency contacts
- [ ] Write incident response plan

### Team Training

- [ ] Train staff on admin panel
- [ ] Provide access to monitoring tools
- [ ] Review security procedures
- [ ] Establish on-call rotation
- [ ] Test disaster recovery plan

---

## Troubleshooting

### Common Issues

**"Connection refused" errors:**
```bash
# Check services are running
docker-compose ps

# Check logs
docker-compose logs backend
docker-compose logs postgres
```

**Database migrations fail:**
```bash
# Rollback and retry
alembic downgrade -1
alembic upgrade head
```

**SSL certificate errors:**
```bash
# Check certificate validity
openssl x509 -in /path/to/cert.pem -text -noout

# Renew certificate
certbot renew --force-renewal
```

For more troubleshooting, see [TROUBLESHOOTING_GUIDE.md](TROUBLESHOOTING_GUIDE.md).

---

## Next Steps

1. Complete [OPERATIONS_MANUAL.md](OPERATIONS_MANUAL.md) for day-to-day operations
2. Review [SCALING_GUIDE.md](SCALING_GUIDE.md) for growth planning
3. Set up monitoring per [MONITORING_RUNBOOK.md](MONITORING_RUNBOOK.md)
4. Configure backups per [BACKUP_RECOVERY.md](BACKUP_RECOVERY.md)
5. Train city staff using [CITY_ADMIN_GUIDE.md](CITY_ADMIN_GUIDE.md)

---

## Support

- **Documentation**: `/docs` directory
- **Issues**: GitHub Issues
- **Email**: support@civicq.org (TBD)
- **Emergency**: [On-call procedures](MONITORING_RUNBOOK.md#on-call)

---

**Document Version**: 1.0
**Last Reviewed**: 2026-02-14
**Next Review**: Quarterly or before major releases
