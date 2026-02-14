# CivicQ Quick Start Guide

Get CivicQ running on your machine in **less than 5 minutes**!

---

## Prerequisites

Before you begin, ensure you have:

- **Docker & Docker Compose** (recommended) OR
- **Python 3.11+** and **Node.js 18+**
- **PostgreSQL 15+** (if not using Docker)
- **Redis** (if not using Docker)

---

## Option 1: Docker Compose (Recommended)

The fastest way to get everything running.

### 1. Clone the Repository

```bash
git clone <repository-url>
cd CivicQ
```

### 2. Start All Services

```bash
docker-compose up -d
```

This starts:
- PostgreSQL database with pgvector
- Redis cache
- Backend API (FastAPI)
- Frontend (React)

### 3. Verify It's Running

```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Or check health
curl http://localhost:8000/health
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### 5. Stop Services

```bash
docker-compose down
```

**Done! You're ready to develop.**

---

## Option 2: Make Commands

If you prefer using Make:

### 1. Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd CivicQ

# Run setup (first time only)
make setup
```

This will:
- Create Python virtual environment
- Install backend dependencies
- Install frontend dependencies
- Set up database

### 2. Start Development Servers

```bash
make dev
```

This starts both backend and frontend in development mode.

### 3. Other Useful Commands

```bash
make help          # See all available commands
make test          # Run all tests
make format        # Format code
make lint          # Lint code
make health        # Check system health
make clean         # Clean up temporary files
```

---

## Option 3: Manual Setup

For more control over each component.

### Step 1: Database Setup

**Using Docker (easiest):**

```bash
docker-compose up -d db redis
```

**Using Local PostgreSQL:**

```bash
# Create database
createdb civicq

# Enable pgvector extension
psql civicq -c "CREATE EXTENSION vector;"
```

### Step 2: Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional for development)
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload
```

Backend will run on **http://localhost:8000**

### Step 3: Frontend Setup

Open a **new terminal window**:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will run on **http://localhost:3000**

---

## Verify Installation

### 1. Check Backend Health

```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "1.0.0"
}
```

### 2. Check Frontend

Open **http://localhost:3000** in your browser. You should see the CivicQ homepage.

### 3. Check API Documentation

Visit **http://localhost:8000/docs** for interactive API documentation (Swagger UI).

### 4. Test an API Endpoint

```bash
# Get all cities (should return empty list initially)
curl http://localhost:8000/api/v1/cities
```

---

## Common Issues & Solutions

### Port Already in Use

**Backend (port 8000):**
```bash
# Use different port
uvicorn app.main:app --reload --port 8001

# Update frontend API URL in frontend/src/services/api.ts
```

**Frontend (port 3000):**
```bash
# Use different port
PORT=3001 npm start
```

### Database Connection Error

```bash
# Check if PostgreSQL is running
pg_isready

# If using Docker, check services
docker-compose ps

# View logs
docker-compose logs db
```

### Redis Connection Error

```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# If using Docker
docker-compose ps
docker-compose logs redis
```

### Python Virtual Environment Issues

```bash
# Deactivate and recreate
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Node Modules Issues

```bash
# Clean install
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Migration Errors

```bash
# Reset database (WARNING: Deletes all data)
cd backend
alembic downgrade base
alembic upgrade head

# Or use the script
../scripts/reset-db.sh
```

---

## Next Steps

### 1. Explore the Application

**As a Voter:**
- Browse available ballots
- View contests and candidates
- Submit and vote on questions
- Watch candidate video answers

**As a Candidate:**
- Register and verify identity
- View top questions
- Record video answers
- Track analytics

**As an Admin:**
- Access moderation console
- Review flagged content
- Manage users and verification
- View analytics

### 2. Read Documentation

Start with these docs based on your role:

**Developers:**
- [Architecture Overview](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Database Schema](docs/architecture/database-schema.md)
- [Frontend Guide](frontend/FRONTEND_GUIDE.md)

**Product/Design:**
- [CivicQ PRD](CivicQ.md)
- [MVP Scope](docs/MVP-SCOPE.md)
- [UX Best Practices](docs/UX-BEST-PRACTICES.md)
- [Product Vision](docs/product/product-vision.md)

**Operations:**
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Security Policy](SECURITY.md)
- [Testing Guide](TESTING.md)

### 3. Start Developing

**Backend Development:**

```bash
# Create a new API endpoint
cd backend/app/api/v1/endpoints
# Edit or create endpoint file

# Run tests
pytest

# Check code quality
black .
flake8
mypy .
```

**Frontend Development:**

```bash
# Create a new component
cd frontend/src/components
# Create component file

# Run tests
npm test

# Check code quality
npm run lint
npm run format
```

### 4. Make Your First Contribution

1. Create a new branch
   ```bash
   git checkout -b feature/my-feature
   ```

2. Make your changes

3. Run tests
   ```bash
   make test
   ```

4. Format code
   ```bash
   make format
   ```

5. Commit and push
   ```bash
   git add .
   git commit -m "Add my feature"
   git push origin feature/my-feature
   ```

6. Create a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## Development Workflow

### Typical Development Session

```bash
# 1. Pull latest changes
git pull origin main

# 2. Start services
make dev
# OR
docker-compose up -d

# 3. Make changes to code
# Backend: backend/app/
# Frontend: frontend/src/

# 4. Changes auto-reload in development mode
# Backend: uvicorn with --reload
# Frontend: react-scripts with hot module replacement

# 5. Test your changes
make test

# 6. Format code
make format

# 7. Commit and push
git add .
git commit -m "Description of changes"
git push
```

### Running Specific Tests

```bash
# Backend tests only
cd backend
pytest

# Specific test file
pytest tests/test_auth.py

# With coverage
pytest --cov=app --cov-report=html

# Frontend tests only
cd frontend
npm test

# Specific test file
npm test -- QuestionCard.test.tsx

# With coverage
npm test -- --coverage
```

---

## Environment Configuration

### Backend (.env)

Create `backend/.env` for custom configuration:

```env
# Database
DATABASE_URL=postgresql://civicq:civicq@localhost:5432/civicq

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Secret (generate a secure random string)
SECRET_KEY=your-secret-key-here

# Environment
ENVIRONMENT=development

# AI Features
ANTHROPIC_API_KEY=sk-ant-api03-...
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
ENABLE_AI_FEATURES=true

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Frontend (.env)

Create `frontend/.env` for custom configuration:

```env
# API URL
REACT_APP_API_URL=http://localhost:8000

# Environment
REACT_APP_ENV=development
```

---

## Stopping Services

### Docker Compose

```bash
# Stop services
docker-compose down

# Stop and remove volumes (deletes data)
docker-compose down -v

# View logs before stopping
docker-compose logs -f
```

### Manual

Press `Ctrl+C` in each terminal running a service.

---

## Getting Help

### Documentation

- **Main README**: [README.md](README.md)
- **Full Setup Guide**: [SETUP.md](SETUP.md)
- **Documentation Index**: [docs/INDEX.md](docs/INDEX.md)
- **Project Status**: [STATUS.md](STATUS.md)

### Debugging

```bash
# Check system health
make health
# OR
./scripts/health-check.sh

# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db

# Check running processes
docker-compose ps

# Restart a service
docker-compose restart backend
```

### Common Commands Reference

```bash
# Start everything
docker-compose up -d
make dev

# Stop everything
docker-compose down
Ctrl+C (if using make dev)

# View logs
docker-compose logs -f
make logs

# Run tests
make test
pytest (backend)
npm test (frontend)

# Format code
make format
black . (backend)
npm run format (frontend)

# Check health
make health
curl http://localhost:8000/health

# Reset database
./scripts/reset-db.sh
```

---

## What's Next?

You're all set! Here are some suggested next steps:

1. **Explore the Code**
   - Browse `backend/app/` for API code
   - Browse `frontend/src/` for React components
   - Check `docs/` for detailed documentation

2. **Run the Tests**
   ```bash
   make test
   ```

3. **Try the AI Features**
   - Set up Anthropic API key in `.env`
   - Submit a question and see AI analysis
   - Check [AI_FEATURES.md](AI_FEATURES.md) for details

4. **Read the Architecture**
   - [Architecture Overview](docs/ARCHITECTURE.md)
   - [Database Schema](docs/architecture/database-schema.md)
   - [API Documentation](docs/API.md)

5. **Pick a Feature to Implement**
   - Check [STATUS.md](STATUS.md) for what's next
   - Review [ROADMAP.md](docs/ROADMAP.md) for upcoming features
   - See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines

---

**Happy coding!**

Built to make local democracy more transparent, accessible, and focused on what voters actually care about.

**CivicQ: Democracy through clarity, not chaos.**
