# CivicQ Environment Configuration Guide

This guide explains how to properly configure CivicQ for development and production environments.

## Table of Contents

- [Quick Start](#quick-start)
- [Backend Configuration](#backend-configuration)
- [Frontend Configuration](#frontend-configuration)
- [Docker Configuration](#docker-configuration)
- [Environment Validation](#environment-validation)
- [Production Deployment](#production-deployment)
- [Common Issues](#common-issues)

## Quick Start

### 1. Backend Setup

```bash
cd backend
cp .env.example .env
```

Edit `.env` and configure:

```bash
# Generate a secure secret key
SECRET_KEY=$(openssl rand -hex 32)

# Set your URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 2. Frontend Setup

```bash
cd frontend
cp .env.example .env.local
```

Edit `.env.local`:

```bash
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_BASE_URL=http://localhost:3000
```

### 3. Validate Configuration

```bash
cd backend
python app/core/startup_checks.py
```

## Backend Configuration

### Required Variables

These MUST be set before running the backend:

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key (32+ chars) | Generated with `openssl rand -hex 32` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/civicq` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `FRONTEND_URL` | Frontend URL for OAuth callbacks | `http://localhost:3000` |
| `BACKEND_URL` | Backend URL for OAuth redirects | `http://localhost:8000` |
| `ALLOWED_ORIGINS` | Comma-separated allowed origins | `http://localhost:3000,http://localhost:8000` |

### Feature-Specific Variables

#### Video Recording (Required if `ENABLE_VIDEO_RECORDING=true`)

```bash
S3_BUCKET=civicq-media
S3_REGION=us-west-2
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
```

#### SMS Verification (Required if `VERIFICATION_METHOD=sms`)

```bash
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890
```

#### Email Service (Required for email verification)

Option 1 - SMTP:
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-app-password
```

Option 2 - SendGrid (Recommended):
```bash
SENDGRID_API_KEY=your-sendgrid-api-key
```

#### OAuth Authentication (Optional)

Google OAuth:
```bash
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

Facebook OAuth:
```bash
FACEBOOK_CLIENT_ID=your-app-id
FACEBOOK_CLIENT_SECRET=your-app-secret
```

#### AI Features (Optional)

```bash
ANTHROPIC_API_KEY=your-api-key
ENABLE_AI_FEATURES=true
```

## Frontend Configuration

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API endpoint | `http://localhost:8000/api` |
| `REACT_APP_BASE_URL` | Frontend base URL | `http://localhost:3000` |

### Optional Variables

```bash
# Analytics
REACT_APP_GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX

# Error Tracking
REACT_APP_SENTRY_DSN=https://...@sentry.io/...

# Feature Flags
REACT_APP_ENABLE_VIDEO_RECORDING=true
REACT_APP_ENABLE_REBUTTALS=true
```

## Docker Configuration

### Development with Docker Compose

1. Create environment files:
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

2. Start services:
```bash
docker-compose up -d
```

The docker-compose.yml automatically overrides URLs for the Docker network:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Database: `postgresql://civicq:civicq@db:5432/civicq`

### Production with Docker

1. Create production environment file:
```bash
cp backend/.env.example backend/.env.production
```

2. Edit `.env.production` with production values:
```bash
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<generate-new-key>
FRONTEND_URL=https://app.civicq.com
BACKEND_URL=https://api.civicq.com
ALLOWED_ORIGINS=https://civicq.com,https://app.civicq.com
```

3. Create root `.env` for docker-compose:
```bash
# Database
POSTGRES_PASSWORD=<strong-password>
REDIS_PASSWORD=<strong-password>

# Application
SECRET_KEY=<your-secret-key>
ALLOWED_ORIGINS=https://civicq.com,https://app.civicq.com

# URLs
FRONTEND_URL=https://app.civicq.com
BACKEND_URL=https://api.civicq.com
REACT_APP_API_URL=https://api.civicq.com/api
REACT_APP_BASE_URL=https://app.civicq.com

# S3
S3_BUCKET=civicq-media-prod
S3_REGION=us-west-2
S3_ACCESS_KEY=<your-access-key>
S3_SECRET_KEY=<your-secret-key>

# Error Tracking
SENTRY_DSN=<your-sentry-dsn>
```

4. Deploy:
```bash
docker-compose -f docker-compose.production.yml up -d
```

## Environment Validation

### Automatic Validation on Startup

The backend automatically validates environment variables on startup. It will:

1. Check all required variables are set
2. Validate SECRET_KEY is secure (32+ characters)
3. Ensure URLs are properly configured
4. Verify feature dependencies (S3 for videos, Twilio for SMS, etc.)
5. Validate production security settings (HTTPS, no wildcards in CORS)

### Manual Validation

Run validation checks manually:

```bash
cd backend
python app/core/startup_checks.py
```

This will output detailed error messages for any configuration issues.

## Production Deployment

### Security Checklist

Before deploying to production, ensure:

- [ ] `SECRET_KEY` is unique and generated securely (never use example value)
- [ ] `DEBUG=false`
- [ ] `ENVIRONMENT=production`
- [ ] All URLs use HTTPS (not HTTP)
- [ ] `ALLOWED_ORIGINS` contains exact domains (no wildcards `*`)
- [ ] Database uses strong credentials
- [ ] Redis has password authentication
- [ ] S3 bucket has proper IAM permissions
- [ ] Sentry DSN is configured for error tracking
- [ ] OAuth redirect URIs updated in Google/Facebook consoles
- [ ] SSL/TLS certificates configured
- [ ] Environment variables stored securely (not in version control)

### URL Configuration

Production URLs must be consistent across all services:

**Backend `.env`:**
```bash
FRONTEND_URL=https://app.civicq.com
BACKEND_URL=https://api.civicq.com
ALLOWED_ORIGINS=https://civicq.com,https://app.civicq.com
```

**Frontend build args:**
```bash
REACT_APP_API_URL=https://api.civicq.com/api
REACT_APP_BASE_URL=https://app.civicq.com
```

**OAuth Redirect URIs:**
- Google: `https://api.civicq.com/api/v1/auth/oauth/google/callback`
- Facebook: `https://api.civicq.com/api/v1/auth/oauth/facebook/callback`

### Environment Variables Priority

1. **Docker environment** (in docker-compose.yml) - highest priority
2. **Shell environment** - overrides .env file
3. **`.env` file** - default values

## Common Issues

### Issue: "ALLOWED_ORIGINS cannot contain wildcards in production"

**Solution:** Set exact frontend origins:
```bash
ALLOWED_ORIGINS=https://civicq.com,https://app.civicq.com
```

### Issue: "SECRET_KEY is not set or using default value"

**Solution:** Generate and set a secure key:
```bash
SECRET_KEY=$(openssl rand -hex 32)
```

### Issue: OAuth callback fails with "redirect_uri mismatch"

**Solution:** Ensure URLs match exactly:
1. Check `BACKEND_URL` in backend `.env`
2. Update OAuth console with exact callback URL
3. URLs must include protocol (https://) and NO trailing slash

### Issue: Video upload fails

**Solution:** Verify S3 configuration:
```bash
# Check all S3 variables are set
S3_BUCKET=civicq-media
S3_REGION=us-west-2
S3_ACCESS_KEY=<valid-key>
S3_SECRET_KEY=<valid-key>

# Verify IAM permissions: s3:PutObject, s3:GetObject
```

### Issue: CORS errors in browser

**Solution:**
1. Verify `FRONTEND_URL` is in `ALLOWED_ORIGINS`
2. Check URLs match exactly (including protocol and port)
3. Ensure no trailing slashes
4. Restart backend after changing CORS settings

### Issue: "Cannot connect to database"

**Solution:**
1. For local development: Ensure PostgreSQL is running
2. For Docker: Use service name as host (`db` not `localhost`)
3. Verify credentials in `DATABASE_URL`

## Testing Configuration

### Test Backend Configuration

```bash
# Check startup validation
python backend/app/core/startup_checks.py

# Test database connection
python backend/scripts/test_db_connection.py

# Verify API is accessible
curl http://localhost:8000/health
```

### Test Frontend Configuration

```bash
# Print environment variables
npm run env

# Build production bundle
npm run build

# Test production build locally
npx serve -s build
```

### Test OAuth Flow

1. Ensure OAuth credentials are configured
2. Start both backend and frontend
3. Visit frontend login page
4. Click "Sign in with Google/Facebook"
5. Verify redirect back to frontend after authentication

## Additional Resources

- Backend .env.example: See all available configuration options
- Frontend .env.example: See all frontend environment variables
- OAuth Setup Guide: See `docs/oauth-setup.md`
- Deployment Guide: See `docs/deployment.md`

## Support

If you encounter configuration issues:

1. Run validation: `python backend/app/core/startup_checks.py`
2. Check logs for detailed error messages
3. Verify all required variables are set
4. Compare with `.env.example` files
5. Review this guide for common issues
