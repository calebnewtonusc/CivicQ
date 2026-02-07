# CivicQ Quick Start Guide

Get CivicQ running in less than 5 minutes!

## Prerequisites

Ensure you have these installed:
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (or use Docker)
- Redis (or use Docker)

## Fastest Start: Docker Compose (Recommended)

```bash
# Clone and navigate to project
cd /Users/joelnewton/Documents/School/Projects/CivicQ

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

Access:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs

## Alternative: Manual Setup

### 1. Database Setup

```bash
# Using Docker (easiest)
docker-compose up -d db redis

# OR using local PostgreSQL
createdb civicq
psql civicq -c "CREATE EXTENSION vector;"
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn app.main:app --reload
```

Backend will run on http://localhost:8000

### 3. Frontend Setup

```bash
# In a new terminal
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will run on http://localhost:3000

## Using Make Commands

We provide helpful Make commands:

```bash
# See all available commands
make help

# Set up everything
make setup

# Start development servers
make dev

# Check health
make health

# Run tests
make test

# Format code
make format
```

## Verify Installation

### Check Backend
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

### Check Frontend
Open http://localhost:3000 in your browser. You should see the CivicQ homepage.

### Check API Documentation
Visit http://localhost:8000/api/docs for interactive API documentation.

## Common Issues

### Port Already in Use

**Backend (8000):**
```bash
# Use different port
uvicorn app.main:app --reload --port 8001
```

**Frontend (3000):**
```bash
# Use different port
PORT=3001 npm start
```

### Database Connection Error

```bash
# Check if PostgreSQL is running
pg_isready

# Check Docker services
docker-compose ps
```

### Redis Connection Error

```bash
# Check if Redis is running
redis-cli ping

# Should return: PONG
```

## Next Steps

1. **Read the Documentation**
   - [Architecture Overview](docs/architecture/overview.md)
   - [Database Schema](docs/architecture/database-schema.md)
   - [Full Setup Guide](SETUP.md)

2. **Explore the API**
   - Visit http://localhost:8000/api/docs
   - Try the health check endpoint
   - Review available endpoints

3. **Start Developing**
   - Check [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines
   - Review the original [PRD](../Downloads/CivicQ.md)
   - Pick a feature to implement!

## Stopping Services

### Docker Compose
```bash
docker-compose down
```

### Manual
Press `Ctrl+C` in each terminal running a service.

## Getting Help

- Review [SETUP.md](SETUP.md) for detailed instructions
- Check logs: `docker-compose logs -f`
- Run health check: `make health` or `./scripts/health-check.sh`

## Development Workflow

1. **Make changes** to backend (`backend/app/`) or frontend (`frontend/src/`)
2. **Changes auto-reload** in development mode
3. **Test your changes** with `make test`
4. **Format code** with `make format`
5. **Commit** following the guidelines in CONTRIBUTING.md

Happy coding! 🚀
