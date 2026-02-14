# CivicQ Production Deployment Guide

**Version:** 1.0
**Last Updated:** 2026-02-14
**Target:** Production deployment for pilot city

---

## Overview

This guide covers deploying CivicQ to production for a pilot city. The recommended stack uses Vercel (frontend), Railway (backend + workers), Neon (PostgreSQL), and Upstash (Redis).

**Architecture:**
```
Internet → Cloudflare (CDN/DDoS) → Vercel (Frontend) → Railway (API) → Neon (DB)
                                                     ↓
                                        Railway (Celery Workers) → S3 (Videos)
                                                     ↓
                                                Upstash (Redis)
```

---

## Prerequisites

- GitHub account (for code hosting and CI/CD)
- Vercel account (free tier sufficient for pilot)
- Railway account (hobby plan: $5/month)
- Neon account (free tier with pgvector)
- Upstash account (free tier: 10K commands/day)
- AWS account (S3 for video storage) OR Cloudflare R2
- Domain name (e.g., `civicq.org`)

---

## Part 1: Database Setup (Neon PostgreSQL)

### 1.1 Create Neon Project

1. Go to [neon.tech](https://neon.tech)
2. Create new project: `civicq-production`
3. Select region closest to your users
4. Enable pgvector extension:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
5. Copy connection string (will be used in backend)

### 1.2 Run Migrations

```bash
# Set DATABASE_URL environment variable
export DATABASE_URL="postgresql://user:pass@host/db"

# Run migrations
cd backend
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
```

### 1.3 Create Admin User (Optional)

```bash
cd backend
python scripts/create_admin.py \
  --email admin@pilot-city.gov \
  --password <secure-password>
```

---

## Part 2: Redis Setup (Upstash)

### 2.1 Create Redis Database

1. Go to [upstash.com](https://upstash.com)
2. Create new database: `civicq-production`
3. Select region closest to backend
4. Enable TLS
5. Copy connection URLs (REST and regular)

---

## Part 3: Backend Deployment (Railway)

### 3.1 Deploy API Service

1. Go to [railway.app](https://railway.app)
2. Create new project: `civicq-production`
3. Add service from GitHub repo
4. Select `backend` directory as root
5. Set build command: `pip install -r requirements.txt`
6. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3.2 Configure Environment Variables

Add in Railway dashboard:

```bash
# Database
DATABASE_URL=<neon-connection-string>

# Redis
REDIS_URL=<upstash-redis-url>

# Security
JWT_SECRET_KEY=<generate-with-openssl-rand-hex-64>
ALLOWED_ORIGINS=https://civicq.org,https://www.civicq.org

# Video Storage
AWS_ACCESS_KEY_ID=<aws-key>
AWS_SECRET_ACCESS_KEY=<aws-secret>
S3_BUCKET=civicq-videos-production
S3_REGION=us-west-2

# Transcription (choose one)
OPENAI_API_KEY=<openai-key>  # For Whisper
# OR
DEEPGRAM_API_KEY=<deepgram-key>  # For Deepgram

# Email (optional for V1)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<sendgrid-api-key>
FROM_EMAIL=noreply@civicq.org

# SMS (optional for V1)
TWILIO_ACCOUNT_SID=<twilio-sid>
TWILIO_AUTH_TOKEN=<twilio-token>
TWILIO_PHONE_NUMBER=+1234567890

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ALLOW_CREDENTIALS=true
```

### 3.3 Deploy Celery Workers

1. Add another service in same Railway project
2. Same GitHub repo, same `backend` directory
3. Set start command:
   ```bash
   celery -A app.celery_app worker --loglevel=info
   ```
4. Use same environment variables as API service
5. Scale to 2 workers for redundancy

---

## Part 4: Frontend Deployment (Vercel)

### 4.1 Deploy to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Import GitHub repository
3. Set root directory: `frontend`
4. Framework preset: Create React App
5. Build command: `npm run build`
6. Output directory: `build`

### 4.2 Configure Environment Variables

Add in Vercel dashboard:

```bash
REACT_APP_API_URL=https://api.civicq.org
REACT_APP_ENVIRONMENT=production
REACT_APP_SENTRY_DSN=<sentry-dsn>  # Optional
```

### 4.3 Custom Domain

1. Add custom domain: `civicq.org` and `www.civicq.org`
2. Update DNS records as instructed by Vercel
3. SSL certificate auto-provisioned

---

## Part 5: Video Storage (AWS S3)

### 5.1 Create S3 Bucket

```bash
aws s3 mb s3://civicq-videos-production --region us-west-2

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket civicq-videos-production \
  --versioning-configuration Status=Enabled

# Set lifecycle policy (archive to Glacier after 90 days)
aws s3api put-bucket-lifecycle-configuration \
  --bucket civicq-videos-production \
  --lifecycle-configuration file://s3-lifecycle.json
```

### 5.2 Configure CORS

`s3-cors.json`:
```json
{
  "CORSRules": [
    {
      "AllowedOrigins": ["https://civicq.org"],
      "AllowedMethods": ["GET", "PUT", "POST"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 3000
    }
  ]
}
```

```bash
aws s3api put-bucket-cors \
  --bucket civicq-videos-production \
  --cors-configuration file://s3-cors.json
```

### 5.3 CloudFront CDN (Optional but Recommended)

1. Create CloudFront distribution
2. Origin: `civicq-videos-production.s3.amazonaws.com`
3. Viewer Protocol Policy: Redirect HTTP to HTTPS
4. Allowed HTTP Methods: GET, HEAD, OPTIONS
5. Cache Policy: CachingOptimized
6. Update backend `CDN_BASE_URL` environment variable

---

## Part 6: Domain and DNS

### 6.1 DNS Configuration

Add these DNS records:

```
A     @               76.76.21.21 (Vercel)
A     www             76.76.21.21 (Vercel)
CNAME api           <railway-api-url>
CNAME cdn           <cloudfront-url>
TXT   @             "v=spf1 include:sendgrid.net ~all"
```

### 6.2 SSL Certificates

- Vercel: Auto-provisioned via Let's Encrypt
- Railway: Auto-provisioned
- CloudFront: Use AWS Certificate Manager (ACM)

---

## Part 7: Monitoring and Logging

### 7.1 Error Tracking (Sentry)

1. Create Sentry project: `civicq-production`
2. Get DSN
3. Add to backend and frontend environment variables
4. Configure alerts for critical errors

### 7.2 Uptime Monitoring

Use one of:
- UptimeRobot (free, 5-minute checks)
- Pingdom (paid, 1-minute checks)
- Better Uptime (paid, nice status page)

Monitor:
- Frontend: `https://civicq.org`
- API health: `https://api.civicq.org/health`
- Database: Connection from Railway dashboard

### 7.3 Log Aggregation (Optional)

For production:
- Railway: Built-in logging (7 days retention)
- Papertrail: Log aggregation and search
- Datadog: Full observability (expensive)

---

## Part 8: Security Hardening

### 8.1 API Security

In Railway backend environment:

```bash
# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_ANONYMOUS=100
RATE_LIMIT_AUTHENTICATED=1000

# Security headers
ENABLE_HSTS=true
ENABLE_CSP=true
```

### 8.2 Database Security

- Enable Neon IP allowlist (Railway IPs only)
- Rotate database password quarterly
- Enable query logging for audit

### 8.3 Secrets Management

- Use Railway's built-in secret management
- Rotate JWT secret annually
- Store AWS keys in Railway, not in code

---

## Part 9: Backup and Disaster Recovery

### 9.1 Database Backups

Neon provides:
- Automated daily backups (retained 7 days)
- Point-in-time recovery (7 days)

Additional backups:
```bash
# Manual backup to S3
pg_dump $DATABASE_URL | gzip | aws s3 cp - s3://civicq-backups/db-$(date +%Y%m%d).sql.gz
```

### 9.2 Video Backups

S3 versioning enabled, so deleted videos are recoverable for 90 days.

Archive policy:
- Videos moved to Glacier after election + 90 days
- Retained for 7 years (election record retention)

### 9.3 Disaster Recovery Plan

**RTO (Recovery Time Objective):** 4 hours
**RPO (Recovery Point Objective):** 24 hours

**Recovery Steps:**
1. Restore database from latest Neon backup
2. Redeploy backend/frontend from GitHub main branch
3. Verify all services operational
4. Notify city admin and users of incident

---

## Part 10: Performance Optimization

### 10.1 Database Optimization

```sql
-- Create indexes for common queries
CREATE INDEX idx_questions_contest_ranking ON questions(contest_id, ranking_score DESC);
CREATE INDEX idx_answers_question ON answers(question_id);
CREATE INDEX idx_votes_question ON question_votes(question_id);

-- Analyze query performance
EXPLAIN ANALYZE SELECT ...;
```

### 10.2 Redis Caching

Cache these for 15 minutes:
- Top 100 questions per contest
- Candidate profiles
- Contest metadata

### 10.3 CDN Configuration

- Set Cache-Control headers for videos (1 year)
- Set Cache-Control for images (1 month)
- Dynamic content (API responses): no-cache

---

## Part 11: Deployment Checklist

**Pre-Launch:**
- [ ] Database migrations run successfully
- [ ] All environment variables configured
- [ ] Frontend connected to backend API
- [ ] Video upload and playback working
- [ ] Email/SMS verification working
- [ ] Admin console accessible
- [ ] SSL certificates valid
- [ ] DNS records propagated
- [ ] Monitoring and alerts configured
- [ ] Backup strategy tested
- [ ] Security audit completed
- [ ] Load testing passed (100 concurrent users)

**Launch Day:**
- [ ] Announcement to city and press
- [ ] Monitor error rates and performance
- [ ] Have team on standby for issues
- [ ] Collect feedback from early users

**Post-Launch:**
- [ ] Daily check of error logs
- [ ] Weekly review of analytics
- [ ] Monthly security review
- [ ] Quarterly disaster recovery test

---

## Part 12: Scaling Strategy

**Phase 1: Single City (0-10K voters)**
- Current stack is sufficient
- 1 API instance, 2 workers, 1 DB

**Phase 2: Growing (10K-50K voters)**
- Scale API to 2-3 instances
- Scale workers to 3-5
- Add database read replica
- Enable Redis cluster mode

**Phase 3: Multi-City (50K+ voters)**
- Database sharding by city
- Separate worker pools per city
- Multi-region deployment
- Load balancer with auto-scaling

---

## Part 13: Cost Estimate

**Pilot City (10K voters, 3-month election cycle):**

| Service | Cost/Month | Notes |
|---------|-----------|-------|
| Vercel (Frontend) | $0 | Free tier |
| Railway (API + Workers) | $20 | Hobby plan |
| Neon (PostgreSQL) | $0 | Free tier |
| Upstash (Redis) | $0 | Free tier |
| AWS S3 | $10 | ~100 GB videos |
| CloudFront (CDN) | $5 | ~500 GB transfer |
| Deepgram (Transcription) | $30 | ~50 hours |
| Domain | $12/year | |
| **Total** | **$65/month** | |

**Production (Multiple Cities):**
- Scale costs linearly with usage
- Neon Pro: $69/month
- Railway Pro: $100/month
- Larger video storage: ~$50/month

---

## Part 14: Troubleshooting

**API not responding:**
- Check Railway deployment logs
- Verify DATABASE_URL is correct
- Check database connection limits

**Videos not uploading:**
- Check S3 bucket permissions
- Verify AWS credentials in Railway
- Check Celery worker logs

**Ranking not updating:**
- Check Celery worker is running
- Verify Redis connection
- Check ranking job schedule

**Verification emails not sending:**
- Check SMTP credentials
- Verify SendGrid API key
- Check spam folder

---

**For architecture details, see [ARCHITECTURE.md](ARCHITECTURE.md)**

**For API documentation, see [API.md](API.md)**

---

**Last Updated:** 2026-02-14
**Questions?** Open a GitHub issue or contact the development team.
