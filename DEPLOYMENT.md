# CivicQ Vercel Deployment Guide

This guide explains how to deploy CivicQ to Vercel for production hosting.

## Overview

CivicQ can be deployed to Vercel with:
- **Frontend**: Static React app served via Vercel CDN
- **Backend**: FastAPI serverless functions
- **Database**: External PostgreSQL (Vercel Postgres, Neon, Supabase, or Railway)
- **Redis**: External Redis (Upstash recommended)

## Prerequisites

1. **Vercel Account** - Sign up at https://vercel.com
2. **GitHub Account** - For connecting your repository
3. **Database** - Choose one:
   - [Vercel Postgres](https://vercel.com/docs/storage/vercel-postgres) (recommended)
   - [Neon](https://neon.tech/) (serverless PostgreSQL with pgvector)
   - [Supabase](https://supabase.com/) (PostgreSQL with many features)
   - [Railway](https://railway.app/) (easy PostgreSQL hosting)
4. **Redis** - [Upstash Redis](https://upstash.com/) (serverless, Vercel integration)

## Quick Deploy

### Option 1: Deploy Frontend Only (Fastest)

This deploys just the React frontend to Vercel:

```bash
cd /Users/joelnewton/Documents/School/Projects/CivicQ/frontend

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name: civicq-frontend
# - Directory: ./
# - Build command: npm run build
# - Output directory: build
```

**Result:** Your frontend will be live at `https://civicq-frontend.vercel.app`

### Option 2: Deploy via GitHub (Recommended)

1. **Push to GitHub**
   ```bash
   cd /Users/joelnewton/Documents/School/Projects/CivicQ
   git remote add origin https://github.com/your-username/CivicQ.git
   git push -u origin main
   ```

2. **Import to Vercel**
   - Go to https://vercel.com/new
   - Import your GitHub repository
   - Configure as shown below

3. **Configure Frontend Project**
   - Framework Preset: `Create React App`
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `build`

4. **Configure Backend Project** (Optional - for API)
   - Create separate Vercel project
   - Root Directory: `backend`
   - Framework Preset: `Other`
   - Build Command: (leave empty)
   - Output Directory: (leave empty)

## Database Setup

### Option A: Vercel Postgres (Easiest)

1. Go to your Vercel project → Storage → Create Database
2. Choose "Postgres"
3. Copy the connection string
4. Add to Vercel environment variables:
   ```
   DATABASE_URL=postgres://...
   ```

### Option B: Neon (Recommended for pgvector)

1. Sign up at https://neon.tech
2. Create a new project
3. Enable pgvector extension:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
4. Copy connection string
5. Add to Vercel environment variables

### Option C: Supabase

1. Sign up at https://supabase.com
2. Create a new project
3. Go to Project Settings → Database → Connection string
4. Enable pgvector in SQL Editor:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
5. Add to Vercel environment variables

## Redis Setup (Upstash)

1. Sign up at https://upstash.com
2. Create a Redis database
3. Copy the connection string
4. Add to Vercel environment variables:
   ```
   REDIS_URL=redis://...
   ```

## Environment Variables

### Frontend Environment Variables

In Vercel dashboard → Settings → Environment Variables:

```
REACT_APP_API_URL=https://civicq-backend.vercel.app/api
REACT_APP_ENV=production
REACT_APP_ENABLE_VIDEO_RECORDING=true
REACT_APP_ENABLE_REBUTTALS=true
```

### Backend Environment Variables

```
# Environment
ENVIRONMENT=production
DEBUG=false

# Security - GENERATE NEW SECRET KEY!
SECRET_KEY=<generate-with-openssl-rand-hex-32>

# Database (from Vercel Postgres, Neon, or Supabase)
DATABASE_URL=<your-postgres-connection-string>

# Redis (from Upstash)
REDIS_URL=<your-redis-connection-string>

# CORS - Update with your frontend domain
ALLOWED_ORIGINS=https://civicq-frontend.vercel.app

# Features
ENABLE_VIDEO_RECORDING=true
ENABLE_REBUTTALS=true
ENABLE_SOURCE_ATTACHMENTS=true
ENABLE_VIEWPOINT_CLUSTERING=true

# Video Settings
MAX_VIDEO_DURATION_SECONDS=180
VIDEO_TIME_LIMIT_COUNCIL=90
VIDEO_TIME_LIMIT_MAYOR=120
VIDEO_TIME_LIMIT_MEASURE=180

# Rate Limiting
RATE_LIMIT_QUESTIONS_PER_DAY=10
RATE_LIMIT_VOTES_PER_HOUR=100

# Question Ranking
TOP_QUESTIONS_COUNT=100
CLUSTER_MAX_QUESTIONS=5
MINORITY_CONCERN_SLOTS=10

# S3 Storage (for videos - use Vercel Blob or Cloudflare R2)
S3_BUCKET=<your-bucket-name>
S3_ACCESS_KEY=<your-access-key>
S3_SECRET_KEY=<your-secret-key>
S3_REGION=<your-region>

# Optional: Sentry for error tracking
SENTRY_DSN=<your-sentry-dsn>
```

## Generate Secret Key

```bash
# On Mac/Linux
openssl rand -hex 32

# Or in Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Storage for Videos

For video uploads, you'll need object storage:

### Option A: Vercel Blob (Easiest)
```bash
# In your Vercel project
vercel blob create civicq-videos
```

Then add to environment:
```
BLOB_READ_WRITE_TOKEN=<from-vercel>
```

### Option B: Cloudflare R2
1. Sign up at https://cloudflare.com
2. Go to R2 → Create bucket
3. Create API token
4. Add credentials to Vercel environment

### Option C: AWS S3
Standard S3 bucket with access credentials.

## Database Migrations

After deploying, run migrations:

```bash
# Install Vercel CLI
npm i -g vercel

# Link to your project
vercel link

# Run migration command
vercel env pull .env.production
cd backend
source venv/bin/activate
alembic upgrade head
```

Or use Vercel Postgres migrations in the dashboard.

## Deploy Commands

### Frontend Deployment

```bash
cd frontend
vercel --prod
```

### Backend Deployment

```bash
cd backend
vercel --prod
```

### Full Project Deployment

```bash
# From project root
vercel --prod
```

## Custom Domain

1. Go to Vercel project → Settings → Domains
2. Add your custom domain (e.g., `civicq.org`)
3. Configure DNS as instructed
4. Update environment variables with new domain

## Monitoring

### Vercel Analytics
- Automatically enabled for all deployments
- View in Vercel dashboard → Analytics

### Error Tracking (Sentry)
1. Sign up at https://sentry.io
2. Create a new project
3. Copy DSN
4. Add to Vercel environment:
   ```
   SENTRY_DSN=<your-sentry-dsn>
   ```

## Continuous Deployment

Once connected to GitHub:
- Push to `main` branch → Auto-deploys to production
- Push to other branches → Creates preview deployments
- Pull requests → Automatic preview deployments

## Vercel CLI Commands

```bash
# Install
npm i -g vercel

# Login
vercel login

# Deploy to preview
vercel

# Deploy to production
vercel --prod

# View logs
vercel logs

# List deployments
vercel ls

# View environment variables
vercel env ls

# Pull environment variables
vercel env pull
```

## Cost Estimate

### Free Tier (Hobby)
- **Vercel**: Free for personal projects
- **Neon**: 10 GB storage, 100 hours compute/month
- **Upstash Redis**: 10,000 commands/day
- **Vercel Blob**: 500 GB bandwidth

Good for: Development, small pilots (< 1,000 users)

### Pro Tier
- **Vercel Pro**: $20/month
- **Neon Scale**: ~$20-50/month
- **Upstash**: $10-30/month
- **Vercel Blob**: Pay as you go

Good for: Production pilots (1,000 - 10,000 users)

## Troubleshooting

### Build Fails

Check build logs in Vercel dashboard. Common issues:
- Missing environment variables
- TypeScript errors
- Dependency issues

Fix:
```bash
# Test build locally
cd frontend
npm run build
```

### API Not Working

1. Check environment variables are set
2. Check database connection
3. View function logs in Vercel dashboard
4. Check CORS settings match frontend domain

### Database Connection Issues

1. Check `DATABASE_URL` is correct
2. Verify IP allowlist (Neon/Supabase allow all by default)
3. Check connection pooling settings

### Rate Limiting

Vercel has built-in limits:
- 100 GB bandwidth/month (Hobby)
- 1000 serverless function invocations/day (Hobby)

Upgrade to Pro for higher limits.

## Security Checklist

Before going live:

- [ ] Change all default passwords
- [ ] Generate new `SECRET_KEY`
- [ ] Set `DEBUG=false`
- [ ] Configure CORS to specific domains
- [ ] Enable HTTPS only (automatic on Vercel)
- [ ] Set up rate limiting
- [ ] Configure CSP headers
- [ ] Enable Vercel firewall rules
- [ ] Set up monitoring (Sentry)
- [ ] Review all environment variables

## Performance Optimization

1. **Enable Edge Caching**
   - Add `Cache-Control` headers
   - Use Vercel Edge Network

2. **Optimize Images**
   - Use Next.js Image component (if upgrading)
   - Or use Vercel Image Optimization

3. **Bundle Size**
   ```bash
   # Analyze bundle
   npm run build
   npx source-map-explorer build/static/js/*.js
   ```

4. **API Response Time**
   - Use connection pooling
   - Enable database query caching
   - Use Redis for frequently accessed data

## Backup Strategy

1. **Database Backups**
   - Vercel Postgres: Automatic daily backups
   - Neon: Point-in-time restore (7 days)
   - Supabase: Automatic backups

2. **File Backups**
   - Vercel Blob: Automatic redundancy
   - S3: Enable versioning

3. **Code Backups**
   - GitHub repository (already backed up)

## Rollback

If deployment has issues:

```bash
# List deployments
vercel ls

# Promote previous deployment
vercel promote <deployment-url>
```

Or in Vercel dashboard:
1. Go to Deployments
2. Find previous working deployment
3. Click "Promote to Production"

## Next Steps

After successful deployment:

1. Test all functionality
2. Set up monitoring alerts
3. Configure custom domain
4. Enable analytics
5. Set up error tracking
6. Create staging environment
7. Document runbooks

## Getting Help

- Vercel Docs: https://vercel.com/docs
- Vercel Support: https://vercel.com/support
- CivicQ Issues: [GitHub Issues]
- Community: [Discord/Slack]

---

**You're ready to deploy CivicQ to the world! 🚀**
