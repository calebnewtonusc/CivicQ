# CivicQ Testing Guide

This document explains how to test the CivicQ application.

## Pre-Test Checklist

Before testing, ensure you have:

- [ ] Docker and Docker Compose installed
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] PostgreSQL 15+ (or Docker)
- [ ] Redis (or Docker)

## Quick Test: Docker Compose

This is the fastest way to verify everything works:

```bash
cd /Users/joelnewton/Documents/School/Projects/CivicQ

# Start all services
docker-compose up -d

# Wait 30 seconds for services to start
sleep 30

# Check service status
docker-compose ps

# All services should show "Up" status
```

Expected output:
```
NAME                  STATUS
civicq_backend        Up
civicq_frontend       Up
civicq_db             Up (healthy)
civicq_redis          Up (healthy)
civicq_celery_worker  Up
```

## Test Endpoints

### 1. Backend Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "1.0.0"
}
```

### 2. Backend Root

```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "message": "CivicQ API",
  "version": "1.0.0",
  "docs": "/api/docs"
}
```

### 3. API Documentation

Visit in browser: http://localhost:8000/api/docs

You should see Swagger UI with all API endpoints.

### 4. Frontend

Visit in browser: http://localhost:3000

You should see the CivicQ homepage.

## Manual Testing (Without Docker)

### Backend Test

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run tests
pytest

# Expected: All tests pass
```

### Frontend Test

```bash
cd frontend

# Run tests
npm test -- --watchAll=false

# Expected: All tests pass
```

## Database Test

### Check PostgreSQL Connection

```bash
# Using Docker
docker-compose exec db psql -U civicq -c "SELECT version();"

# Using local PostgreSQL
psql civicq -c "SELECT version();"
```

### Check pgvector Extension

```bash
# Using Docker
docker-compose exec db psql -U civicq -d civicq -c "\dx vector"

# Using local PostgreSQL
psql civicq -c "\dx vector"
```

Expected: You should see the vector extension listed.

## Redis Test

```bash
# Using Docker
docker-compose exec redis redis-cli ping

# Using local Redis
redis-cli ping
```

Expected response: `PONG`

## System Health Check

Use the provided health check script:

```bash
make health
# OR
./scripts/health-check.sh
```

Expected output:
```
🏥 CivicQ Health Check
====================

PostgreSQL... ✅ Running
Redis... ✅ Running
Backend API... ✅ Running
   Response: {"status":"healthy",...}
Frontend... ✅ Running

Health check complete!
```

## Common Test Failures

### Backend Won't Start

**Symptom:** `ModuleNotFoundError` or import errors

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend Won't Start

**Symptom:** Missing dependencies or build errors

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Database Connection Error

**Symptom:** `could not connect to server`

**Solution:**
```bash
# Check if PostgreSQL is running
docker-compose ps db

# Restart database
docker-compose restart db
```

### Port Already in Use

**Symptom:** `Address already in use` error

**Solution:**
```bash
# Find what's using the port
lsof -i :8000  # For backend
lsof -i :3000  # For frontend

# Kill the process or use different ports
```

## Performance Tests

### Backend Response Time

```bash
time curl http://localhost:8000/health
```

Should respond in < 100ms.

### Frontend Load Time

Open browser DevTools → Network tab → Load http://localhost:3000

Initial load should be < 2 seconds.

## Integration Tests

Coming soon:
- User registration and verification flow
- Question submission and ranking
- Video recording and playback
- Moderation workflow

## Load Tests

Coming soon:
- Concurrent user simulation
- Database query performance
- API rate limiting validation

## Security Tests

Before production:
- [ ] SQL injection testing
- [ ] XSS vulnerability testing
- [ ] CSRF protection validation
- [ ] Authentication flow testing
- [ ] Rate limiting verification

## Automated Testing

### Run All Tests

```bash
make test
```

This runs:
- Backend unit tests (pytest)
- Frontend unit tests (Jest)
- Linting (flake8, ESLint)

### Continuous Testing

```bash
# Backend (watches for changes)
cd backend
source venv/bin/activate
pytest-watch

# Frontend (watches for changes)
cd frontend
npm test
```

## Test Coverage

### Backend Coverage

```bash
cd backend
source venv/bin/activate
pytest --cov=app tests/
```

Target: > 80% coverage

### Frontend Coverage

```bash
cd frontend
npm test -- --coverage --watchAll=false
```

Target: > 80% coverage

## Troubleshooting Tests

### Clear All Data and Reset

```bash
# Stop all services
docker-compose down -v

# Remove virtual environment
rm -rf backend/venv

# Remove node_modules
rm -rf frontend/node_modules

# Start fresh
make setup
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

## Test Reporting

After testing, you should be able to confirm:

✅ All services start without errors
✅ Health check passes
✅ API documentation is accessible
✅ Frontend loads successfully
✅ Database connection works
✅ Redis connection works
✅ Tests pass (backend and frontend)

## Next Steps

After successful testing:

1. Read the [Architecture Documentation](docs/architecture/overview.md)
2. Review the [API Documentation](http://localhost:8000/api/docs)
3. Start implementing features!

## Getting Help

If tests fail:

1. Check [SETUP.md](SETUP.md) for detailed setup instructions
2. Review [QUICKSTART.md](QUICKSTART.md) for common issues
3. Check Docker logs: `docker-compose logs -f`
4. Run health check: `make health`

## Test Environment Variables

For testing, these are the default values (configured in `.env` files):

**Backend:**
- `DATABASE_URL`: `postgresql://civicq:civicq@localhost:5432/civicq`
- `REDIS_URL`: `redis://localhost:6379/0`
- `ENVIRONMENT`: `development`
- `DEBUG`: `true`

**Frontend:**
- `REACT_APP_API_URL`: `http://localhost:8000/api`
- `REACT_APP_ENV`: `development`

Happy testing! 🧪
