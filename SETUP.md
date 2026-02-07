# CivicQ Setup Guide

This guide will help you get CivicQ running on your local machine for development.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **PostgreSQL 15+** - [Download](https://www.postgresql.org/download/)
- **Redis** - [Download](https://redis.io/download)
- **Git** - [Download](https://git-scm.com/downloads)
- **Docker** (optional) - [Download](https://www.docker.com/products/docker-desktop)

## Quick Start with Docker (Recommended)

The easiest way to get started is using Docker Compose:

```bash
# Clone the repository
cd /Users/joelnewton/Documents/School/Projects/CivicQ

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

Services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

To stop:
```bash
docker-compose down
```

## Manual Setup (Without Docker)

### 1. Database Setup

```bash
# Create PostgreSQL database
createdb civicq

# Create user (if needed)
psql -c "CREATE USER civicq WITH PASSWORD 'civicq';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE civicq TO civicq;"

# Enable pgvector extension
psql civicq -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and update configuration
# At minimum, set DATABASE_URL and SECRET_KEY

# Run database migrations (once implemented)
# alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload
```

Backend will be available at http://localhost:8000

### 3. Frontend Setup

```bash
# Open a new terminal
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env if needed (default should work for local dev)

# Start the development server
npm start
```

Frontend will be available at http://localhost:3000

### 4. Redis Setup

```bash
# Start Redis (if not already running)
redis-server

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

### 5. Celery Worker (Optional - for background tasks)

```bash
# In backend directory with venv activated
celery -A app.tasks worker --loglevel=info
```

## Environment Variables

### Backend (.env)

Key variables to configure:

```bash
# Security - IMPORTANT: Change in production!
SECRET_KEY=generate-a-secure-key-here

# Database
DATABASE_URL=postgresql://civicq:civicq@localhost:5432/civicq

# Redis
REDIS_URL=redis://localhost:6379/0

# Feature toggles
ENABLE_VIDEO_RECORDING=true
ENABLE_REBUTTALS=true
```

Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Frontend (.env)

```bash
# API URL
REACT_APP_API_URL=http://localhost:8000/api
```

## Verification

After setup, verify everything is working:

### 1. Check Backend Health
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

### 2. Check API Documentation
Visit http://localhost:8000/api/docs in your browser. You should see the interactive API documentation.

### 3. Check Frontend
Visit http://localhost:3000 in your browser. You should see the CivicQ homepage.

### 4. Check Database Connection
```bash
psql civicq -c "\dt"
```

Should show database tables (once migrations are run).

## Database Migrations (Coming Soon)

Migrations will be managed with Alembic:

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Development Workflow

### Backend Development

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

Changes to Python files will automatically reload the server.

### Frontend Development

```bash
cd frontend
npm start
```

Changes to React files will automatically reload the browser.

### Database Changes

1. Modify models in `backend/app/models/`
2. Create migration: `alembic revision --autogenerate -m "description"`
3. Review migration in `database/migrations/`
4. Apply migration: `alembic upgrade head`

## Common Issues

### Port Already in Use

If ports are already in use, you can change them:

**Backend:**
```bash
uvicorn app.main:app --reload --port 8001
```

**Frontend:**
Edit `package.json` and change the start script to use `PORT=3001`

### Database Connection Error

Ensure PostgreSQL is running:
```bash
pg_isready
```

Check your DATABASE_URL in `.env`

### Module Not Found Errors (Backend)

Ensure virtual environment is activated:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Module Not Found Errors (Frontend)

Delete node_modules and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

### pgvector Extension Error

Install pgvector extension:
```bash
psql civicq -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

## Next Steps

1. Review the [Architecture Documentation](docs/architecture/overview.md)
2. Read the [Database Schema](docs/architecture/database-schema.md)
3. Explore the [API Documentation](http://localhost:8000/api/docs)
4. Start implementing features!

## Getting Help

- Check existing issues: [GitHub Issues](TBD)
- Read the original PRD: `/Users/joelnewton/Downloads/CivicQ.md`
- Review documentation in `docs/`

## Contributing

Contribution guidelines coming soon!
