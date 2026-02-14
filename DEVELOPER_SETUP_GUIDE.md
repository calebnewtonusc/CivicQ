# CivicQ Developer Setup Guide

**Complete onboarding guide for new developers joining the CivicQ project.**

Welcome to CivicQ! This guide will walk you through everything you need to get your development environment set up and start contributing to the project.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Initial Setup](#2-initial-setup)
3. [Project Structure](#3-project-structure)
4. [Development Workflow](#4-development-workflow)
5. [Common Development Tasks](#5-common-development-tasks)
6. [Troubleshooting](#6-troubleshooting)
7. [Code Standards](#7-code-standards)
8. [Useful Commands](#8-useful-commands)

---

## 1. Prerequisites

### Required Software

Before you begin, ensure you have the following installed on your machine:

#### Core Requirements

| Software | Minimum Version | Purpose |
|----------|----------------|---------|
| **Python** | 3.11+ | Backend API |
| **Node.js** | 18+ | Frontend development |
| **PostgreSQL** | 15+ | Primary database with pgvector |
| **Redis** | 7+ | Caching and task queue |
| **Docker** | 20+ | Containerization (recommended) |
| **Docker Compose** | 2.0+ | Multi-container orchestration |
| **Git** | 2.30+ | Version control |

#### Optional (But Recommended)

- **FFmpeg** - Video processing (required for video features)
- **Make** - Build automation
- **curl** - API testing
- **jq** - JSON processing for CLI testing

---

### Installation Instructions

#### macOS

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install core dependencies
brew install python@3.11 node postgresql@15 redis docker docker-compose git ffmpeg

# Start PostgreSQL and Redis as services
brew services start postgresql@15
brew services start redis

# Verify installations
python3 --version  # Should be 3.11+
node --version     # Should be v18+
psql --version     # Should be 15+
redis-cli --version
docker --version
docker-compose --version
```

#### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# Install Node.js 18+ (via NodeSource)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install PostgreSQL 15
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt update
sudo apt install -y postgresql-15 postgresql-contrib-15

# Install Redis
sudo apt install -y redis-server

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install -y docker-compose

# Install FFmpeg
sudo apt install -y ffmpeg

# Install development tools
sudo apt install -y git curl jq make

# Start services
sudo systemctl start postgresql
sudo systemctl start redis-server
sudo systemctl enable postgresql
sudo systemctl enable redis-server

# Verify installations
python3.11 --version
node --version
psql --version
redis-cli --version
docker --version
```

#### Windows

```powershell
# Install Chocolatey (if not already installed)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install dependencies
choco install python311 nodejs postgresql15 redis docker-desktop git ffmpeg -y

# Verify installations
python --version
node --version
psql --version
redis-cli --version
docker --version

# Note: You'll need to start Docker Desktop manually
# PostgreSQL and Redis will start as Windows services
```

---

## 2. Initial Setup

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/your-org/CivicQ.git
cd CivicQ

# Verify you're in the correct directory
pwd  # Should end with /CivicQ
ls   # Should see backend/, frontend/, docs/, etc.
```

### Step 2: Quick Start with Docker (Recommended)

This is the fastest way to get everything running:

```bash
# Start all services with Docker Compose
docker-compose up -d

# Wait for services to initialize (about 30 seconds)
sleep 30

# Check that all services are running
docker-compose ps

# You should see:
# - civicq_db (PostgreSQL)
# - civicq_redis
# - civicq_backend (FastAPI)
# - civicq_frontend (React)
# - civicq_celery_worker (background tasks)
```

**Verify it worked:**

```bash
# Backend health check
curl http://localhost:8000/health
# Expected: {"status":"healthy","environment":"development","version":"1.0.0"}

# Frontend check (open in browser)
open http://localhost:3000  # macOS
# or
xdg-open http://localhost:3000  # Linux
# or visit http://localhost:3000 in your browser
```

**Access points:**
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **API Docs (ReDoc):** http://localhost:8000/redoc

---

### Step 3: Manual Setup (Alternative to Docker)

If you prefer to run services locally without Docker:

#### A. Set Up PostgreSQL Database

```bash
# Create database and user
psql postgres

# In psql shell:
CREATE DATABASE civicq;
CREATE USER civicq WITH PASSWORD 'civicq';
GRANT ALL PRIVILEGES ON DATABASE civicq TO civicq;
\c civicq
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

#### B. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Create environment file from template
cp .env.example .env

# Generate a secure SECRET_KEY
openssl rand -hex 32

# Edit .env and update at minimum:
# - SECRET_KEY (paste the generated key from above)
# - DATABASE_URL=postgresql://civicq:civicq@localhost:5432/civicq
# - REDIS_URL=redis://localhost:6379/0
# - ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
# - FRONTEND_URL=http://localhost:3000
# - BACKEND_URL=http://localhost:8000

# Run database migrations
alembic upgrade head

# Verify migration worked
psql civicq -c "\dt"  # Should show tables like users, questions, etc.
```

#### C. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install

# Create environment file from template
cp .env.example .env.local

# Edit .env.local and update:
# - REACT_APP_API_URL=http://localhost:8000/api
# - REACT_APP_BASE_URL=http://localhost:3000
# - REACT_APP_ENV=development
```

#### D. Start Development Servers

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # Skip on Windows
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

**Terminal 3 - Celery Worker (optional, for background tasks):**
```bash
cd backend
source venv/bin/activate
celery -A app.tasks worker --loglevel=info
```

---

### Step 4: Seed Development Data (Optional)

To populate your local database with sample data for testing:

```bash
# Make sure backend virtual environment is activated
cd backend
source venv/bin/activate

# Run seed script (if available)
python scripts/seed_data.py

# Or use the Makefile
make seed-dev-data
```

---

### Step 5: Verify Everything Works

Run the health check script:

```bash
# From project root
make health

# Or manually:
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

---

## 3. Project Structure

### Directory Layout

```
CivicQ/
├── backend/                    # FastAPI backend application
│   ├── app/                    # Main application code
│   │   ├── api/               # API route handlers
│   │   │   ├── v1/            # API version 1 endpoints
│   │   │   │   ├── auth.py           # Authentication endpoints
│   │   │   │   ├── users.py          # User management
│   │   │   │   ├── questions.py      # Question submission/voting
│   │   │   │   ├── candidates.py     # Candidate profiles
│   │   │   │   ├── contests.py       # Elections/contests
│   │   │   │   ├── videos.py         # Video management
│   │   │   │   └── admin.py          # Admin operations
│   │   ├── core/              # Core functionality
│   │   │   ├── config.py             # Configuration management
│   │   │   ├── security.py           # Security utilities (JWT, hashing)
│   │   │   ├── database.py           # Database connection
│   │   │   └── auth.py               # Authentication logic
│   │   ├── models/            # SQLAlchemy ORM models
│   │   │   ├── user.py               # User model
│   │   │   ├── question.py           # Question model
│   │   │   ├── candidate.py          # Candidate model
│   │   │   ├── contest.py            # Contest/election model
│   │   │   ├── video.py              # Video model
│   │   │   └── vote.py               # Vote/ranking model
│   │   ├── schemas/           # Pydantic schemas (validation)
│   │   │   ├── user.py               # User DTOs
│   │   │   ├── question.py           # Question DTOs
│   │   │   ├── auth.py               # Auth DTOs
│   │   │   └── ...
│   │   ├── services/          # Business logic layer
│   │   │   ├── llm_service.py        # Claude AI integration
│   │   │   ├── auth_service.py       # Authentication logic
│   │   │   ├── question_service.py   # Question management
│   │   │   ├── ranking_service.py    # Question ranking algorithms
│   │   │   ├── video_service.py      # Video processing
│   │   │   └── email_service.py      # Email notifications
│   │   ├── tasks/             # Celery background tasks
│   │   │   ├── video.py              # Video transcoding
│   │   │   ├── email.py              # Email sending
│   │   │   └── ranking.py            # Ranking recalculation
│   │   ├── utils/             # Utility functions
│   │   │   ├── validators.py         # Custom validators
│   │   │   ├── helpers.py            # Helper functions
│   │   │   └── constants.py          # Application constants
│   │   ├── middleware/        # Custom middleware
│   │   │   ├── rate_limit.py         # Rate limiting
│   │   │   └── cors.py               # CORS handling
│   │   └── main.py            # FastAPI application entry point
│   ├── tests/                 # Backend tests
│   │   ├── api/               # API endpoint tests
│   │   ├── services/          # Service layer tests
│   │   ├── models/            # Model tests
│   │   └── conftest.py        # Pytest configuration
│   ├── database/              # Database-related files
│   │   └── migrations/        # Alembic migration files
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment template
│   ├── alembic.ini           # Alembic configuration
│   ├── Dockerfile            # Docker image definition
│   └── pytest.ini            # Pytest configuration
│
├── frontend/                  # React frontend application
│   ├── public/               # Static assets
│   │   ├── index.html        # HTML template
│   │   └── favicon.ico       # Favicon
│   ├── src/                  # Source code
│   │   ├── components/       # Reusable UI components
│   │   │   ├── common/              # Generic components (Button, Card, Modal)
│   │   │   ├── layout/              # Layout components (Header, Footer, Sidebar)
│   │   │   ├── questions/           # Question-related components
│   │   │   ├── candidates/          # Candidate-related components
│   │   │   └── video/               # Video player/recorder
│   │   ├── pages/            # Page components (routes)
│   │   │   ├── Home.tsx             # Landing page
│   │   │   ├── Questions.tsx        # Question feed
│   │   │   ├── CandidatePortal.tsx  # Candidate dashboard
│   │   │   ├── AdminDashboard.tsx   # Admin panel
│   │   │   └── ...
│   │   ├── services/         # API client services
│   │   │   ├── api.ts               # Axios configuration
│   │   │   ├── authService.ts       # Auth API calls
│   │   │   ├── questionService.ts   # Question API calls
│   │   │   └── ...
│   │   ├── hooks/            # Custom React hooks
│   │   │   ├── useAuth.ts           # Authentication hook
│   │   │   ├── useQuestions.ts      # Question data hook
│   │   │   └── ...
│   │   ├── contexts/         # React Context providers
│   │   │   └── AuthContext.tsx      # Auth state management
│   │   ├── types/            # TypeScript type definitions
│   │   │   ├── user.ts              # User types
│   │   │   ├── question.ts          # Question types
│   │   │   └── ...
│   │   ├── utils/            # Utility functions
│   │   │   ├── validators.ts        # Form validators
│   │   │   ├── formatters.ts        # Data formatters
│   │   │   └── constants.ts         # Constants
│   │   ├── App.tsx           # Root component
│   │   ├── index.tsx         # Application entry point
│   │   └── index.css         # Global styles (Tailwind)
│   ├── package.json          # Node dependencies
│   ├── .env.example         # Environment template
│   ├── tsconfig.json        # TypeScript configuration
│   └── tailwind.config.js   # Tailwind CSS configuration
│
├── database/                 # Database schemas and migrations
│   ├── migrations/          # Alembic migration files
│   └── schemas/             # SQL schema documentation
│
├── docs/                    # Project documentation
│   ├── architecture/        # Technical architecture docs
│   ├── business/            # Business documentation
│   ├── legal/               # Legal compliance
│   └── product/             # Product vision
│
├── scripts/                 # Utility scripts
│   ├── setup-dev.sh        # Development setup
│   ├── health-check.sh     # System health check
│   ├── deploy.sh           # Deployment script
│   └── seed_data.py        # Database seeding
│
├── infrastructure/          # Infrastructure as code
│   ├── docker/             # Docker configurations
│   └── terraform/          # Cloud infrastructure (if using)
│
├── e2e/                    # End-to-end tests
│   └── tests/              # Playwright/Cypress tests
│
├── docker-compose.yml      # Docker Compose configuration
├── Makefile               # Build automation
├── README.md              # Project overview
└── .gitignore             # Git ignore rules
```

### Key Files and Their Purpose

| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI application entry point, app configuration |
| `backend/app/core/config.py` | Environment variables and application settings |
| `backend/app/core/database.py` | Database connection and session management |
| `backend/alembic.ini` | Database migration configuration |
| `frontend/src/App.tsx` | React root component, routing configuration |
| `frontend/src/services/api.ts` | Axios HTTP client configuration |
| `docker-compose.yml` | Multi-container Docker configuration |
| `.env.example` | Template for environment variables |

---

## 4. Development Workflow

### Starting Development Servers

#### Option 1: Docker Compose (Recommended)

```bash
# Start all services
docker-compose up

# Or start in detached mode (background)
docker-compose up -d

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
```

#### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

**Terminal 3 - Celery (if needed):**
```bash
cd backend
source venv/bin/activate
celery -A app.tasks worker --loglevel=info
```

#### Option 3: Using Makefile

```bash
# Set up environment (first time only)
make setup

# Start development servers
make dev

# Or with Docker
make docker-up
```

---

### Running Tests

#### Backend Tests

```bash
cd backend
source venv/bin/activate

# Run all tests
pytest

# Run with coverage report
pytest --cov=app tests/

# Run specific test file
pytest tests/api/test_auth.py

# Run specific test
pytest tests/api/test_auth.py::test_register_user

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

#### Frontend Tests

```bash
cd frontend

# Run all tests (watch mode)
npm test

# Run tests once (CI mode)
npm test -- --watchAll=false

# Run with coverage
npm test -- --coverage --watchAll=false

# Run specific test file
npm test -- QuestionCard.test.tsx
```

#### End-to-End Tests

```bash
cd e2e
npm install  # First time only

# Run E2E tests
npm test

# Run in headed mode (see browser)
npm run test:headed
```

---

### Making Changes

#### 1. Create a Feature Branch

```bash
# Pull latest changes
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name

# Or bug fix branch
git checkout -b fix/bug-description
```

#### 2. Make Your Changes

- Edit files in `backend/app/` or `frontend/src/`
- Follow code standards (see section 7)
- Write tests for new functionality
- Update documentation if needed

#### 3. Test Your Changes

```bash
# Backend: Run tests
cd backend
pytest

# Frontend: Run tests
cd frontend
npm test -- --watchAll=false

# Lint your code
make lint

# Format your code
make format
```

#### 4. Commit Your Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: Add question filtering by category"

# Push to remote
git push origin feature/your-feature-name
```

#### 5. Create Pull Request

- Go to GitHub repository
- Click "New Pull Request"
- Select your feature branch
- Fill in PR template
- Request review from team members

---

### Debugging

#### Backend Debugging

**Using print statements:**
```python
# In any Python file
print(f"Debug: {variable_name}")
```

**Using Python debugger:**
```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use ipdb for better experience
import ipdb; ipdb.set_trace()
```

**View logs:**
```bash
# Docker
docker-compose logs -f backend

# Manual
# Logs appear in terminal where uvicorn is running
```

**Interactive API testing:**
- Open http://localhost:8000/docs
- Use Swagger UI to test endpoints
- Check request/response in Network tab

#### Frontend Debugging

**Browser DevTools:**
- Open DevTools (F12 or Cmd+Option+I)
- Console: View console.log output
- Network: Monitor API requests
- React DevTools: Inspect component state

**React Query Devtools:**
```typescript
// Already included in development mode
// Toggle devtools panel in bottom-left corner
```

**Add console logs:**
```typescript
console.log('Debug:', someVariable);
console.table(arrayData);
console.dir(objectData);
```

---

### Code Formatting & Linting

#### Backend (Python)

```bash
cd backend
source venv/bin/activate

# Format code with Black
black app/

# Lint code with Flake8
flake8 app/

# Type checking with MyPy
mypy app/

# Or use Makefile
make format  # Formats both backend and frontend
make lint    # Lints both backend and frontend
```

#### Frontend (TypeScript/React)

```bash
cd frontend

# Format code with Prettier
npm run format

# Lint code with ESLint
npm run lint

# Fix auto-fixable issues
npm run lint -- --fix
```

---

## 5. Common Development Tasks

### Creating New API Endpoints

**Step 1: Define Pydantic Schema**

Create/update schema in `backend/app/schemas/`:

```python
# backend/app/schemas/my_resource.py
from pydantic import BaseModel
from datetime import datetime

class MyResourceCreate(BaseModel):
    name: str
    description: str

class MyResourceResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True
```

**Step 2: Create Database Model**

Create/update model in `backend/app/models/`:

```python
# backend/app/models/my_resource.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class MyResource(Base):
    __tablename__ = "my_resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Step 3: Create Migration**

```bash
cd backend
source venv/bin/activate

# Auto-generate migration
alembic revision --autogenerate -m "Add my_resource table"

# Review the generated migration file in database/migrations/versions/

# Apply migration
alembic upgrade head
```

**Step 4: Create API Route**

Create/update route in `backend/app/api/v1/`:

```python
# backend/app/api/v1/my_resources.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.my_resource import MyResourceCreate, MyResourceResponse
from app.models.my_resource import MyResource

router = APIRouter()

@router.post("/", response_model=MyResourceResponse)
def create_resource(
    resource: MyResourceCreate,
    db: Session = Depends(get_db)
):
    db_resource = MyResource(**resource.dict())
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource

@router.get("/{resource_id}", response_model=MyResourceResponse)
def get_resource(resource_id: int, db: Session = Depends(get_db)):
    resource = db.query(MyResource).filter(MyResource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource
```

**Step 5: Register Router**

Update `backend/app/main.py`:

```python
from app.api.v1 import my_resources

# Add to router includes
app.include_router(
    my_resources.router,
    prefix="/api/v1/my-resources",
    tags=["my-resources"]
)
```

**Step 6: Test the Endpoint**

```bash
# Start backend if not running
uvicorn app.main:app --reload

# Visit http://localhost:8000/docs
# Test your new endpoints in Swagger UI
```

---

### Adding New Frontend Pages

**Step 1: Create Page Component**

```typescript
// frontend/src/pages/MyNewPage.tsx
import React from 'react';

const MyNewPage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">My New Page</h1>
      <p>Content goes here...</p>
    </div>
  );
};

export default MyNewPage;
```

**Step 2: Add Route**

Update `frontend/src/App.tsx`:

```typescript
import MyNewPage from './pages/MyNewPage';

// In the Routes section
<Route path="/my-new-page" element={<MyNewPage />} />
```

**Step 3: Add Navigation Link (Optional)**

Update header/navigation component:

```typescript
<Link to="/my-new-page" className="nav-link">
  My New Page
</Link>
```

---

### Creating Database Migrations

```bash
cd backend
source venv/bin/activate

# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of change"

# Review generated migration file
# Located in: database/migrations/versions/

# Apply migration
alembic upgrade head

# Rollback last migration (if needed)
alembic downgrade -1

# View migration history
alembic history

# View current version
alembic current
```

**Manual Migration Example:**

```python
# database/migrations/versions/xxxx_add_field.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('questions',
        sa.Column('category', sa.String(50), nullable=True)
    )

def downgrade():
    op.drop_column('questions', 'category')
```

---

### Adding Tests

#### Backend Test Example

```python
# backend/tests/api/test_my_resource.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_resource():
    response = client.post(
        "/api/v1/my-resources/",
        json={"name": "Test", "description": "Test description"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test"
    assert "id" in data

def test_get_resource():
    # Create resource first
    create_response = client.post(
        "/api/v1/my-resources/",
        json={"name": "Test", "description": "Test"}
    )
    resource_id = create_response.json()["id"]

    # Get resource
    response = client.get(f"/api/v1/my-resources/{resource_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test"
```

#### Frontend Test Example

```typescript
// frontend/src/components/__tests__/MyComponent.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import MyComponent from '../MyComponent';

describe('MyComponent', () => {
  test('renders component', () => {
    render(<MyComponent />);
    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });

  test('handles button click', () => {
    const handleClick = jest.fn();
    render(<MyComponent onClick={handleClick} />);

    const button = screen.getByRole('button');
    fireEvent.click(button);

    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

---

### Working with Celery Background Tasks

**Define Task:**

```python
# backend/app/tasks/my_task.py
from celery import shared_task
import time

@shared_task
def process_something(item_id: int):
    """Process something in the background"""
    # Simulate long-running task
    time.sleep(5)

    # Do actual work here
    print(f"Processed item {item_id}")

    return {"status": "completed", "item_id": item_id}
```

**Trigger Task from API:**

```python
# backend/app/api/v1/my_endpoint.py
from app.tasks.my_task import process_something

@router.post("/process/{item_id}")
def trigger_processing(item_id: int):
    # Queue task asynchronously
    task = process_something.delay(item_id)

    return {
        "message": "Processing started",
        "task_id": task.id
    }
```

**Check Task Status:**

```python
from celery.result import AsyncResult

@router.get("/status/{task_id}")
def get_task_status(task_id: str):
    task = AsyncResult(task_id)

    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    }
```

**Run Celery Worker:**

```bash
cd backend
source venv/bin/activate

# Start worker
celery -A app.tasks worker --loglevel=info

# Start with auto-reload (development)
watchmedo auto-restart --directory=./app --pattern=*.py --recursive -- \
  celery -A app.tasks worker --loglevel=info
```

---

## 6. Troubleshooting

### Common Setup Issues

#### Issue: "Module not found" errors in backend

**Symptom:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
cd backend
source venv/bin/activate  # Make sure venv is activated
pip install -r requirements.txt
```

---

#### Issue: Frontend dependencies not installing

**Symptom:**
```
npm ERR! code ERESOLVE
```

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

---

#### Issue: Port conflicts (8000 or 3000 already in use)

**Symptom:**
```
Error: Address already in use
```

**Solution:**

```bash
# Find what's using the port
lsof -i :8000  # Backend port
lsof -i :3000  # Frontend port

# Kill the process
kill -9 <PID>

# Or use different ports
# Backend:
uvicorn app.main:app --reload --port 8001

# Frontend:
PORT=3001 npm start
```

---

#### Issue: Database connection failed

**Symptom:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**

```bash
# Check if PostgreSQL is running
# Docker:
docker-compose ps db

# Local:
pg_isready -h localhost -p 5432

# Start PostgreSQL
# Docker:
docker-compose up -d db

# macOS:
brew services start postgresql@15

# Linux:
sudo systemctl start postgresql

# Verify connection
psql -h localhost -U civicq -d civicq
```

---

#### Issue: Redis connection failed

**Symptom:**
```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Solution:**

```bash
# Check if Redis is running
redis-cli ping  # Should return PONG

# Start Redis
# Docker:
docker-compose up -d redis

# macOS:
brew services start redis

# Linux:
sudo systemctl start redis-server

# Test connection
redis-cli
> ping
> PONG
```

---

#### Issue: Database migration errors

**Symptom:**
```
alembic.util.exc.CommandError: Can't locate revision identified by 'xxxxx'
```

**Solution:**

```bash
cd backend
source venv/bin/activate

# Check current state
alembic current

# View migration history
alembic history

# Reset to base (WARNING: Destroys data)
alembic downgrade base
alembic upgrade head

# Or use database reset script
../scripts/reset-db.sh
```

---

#### Issue: Docker container won't start

**Symptom:**
```
Container exited with code 1
```

**Solution:**

```bash
# View container logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up

# Check environment variables
docker-compose exec backend env | grep DATABASE_URL
```

---

#### Issue: Frontend build errors

**Symptom:**
```
Module build failed: Error: ENOENT
```

**Solution:**

```bash
cd frontend

# Clear cache
rm -rf node_modules/.cache

# Reinstall
rm -rf node_modules package-lock.json
npm install

# Clear all caches
npm cache clean --force
npm install
```

---

#### Issue: Celery worker not processing tasks

**Symptom:**
Tasks remain in "PENDING" state

**Solution:**

```bash
# Check Redis connection (Celery uses Redis as broker)
redis-cli ping

# Check worker is running
ps aux | grep celery

# Restart worker
pkill -f celery
cd backend
source venv/bin/activate
celery -A app.tasks worker --loglevel=debug

# Check task in Redis
redis-cli
> KEYS *
> TYPE celery
```

---

### Performance Issues

#### Slow API responses

**Diagnosis:**
```bash
# Enable SQL query logging
# In backend/.env:
DATABASE_ECHO=true

# Restart backend and watch logs for slow queries
```

**Common fixes:**
- Add database indexes
- Use eager loading for relationships
- Implement caching with Redis
- Use pagination for large result sets

---

#### High memory usage

**Check:**
```bash
# Docker containers
docker stats

# Local processes
top -o mem
```

**Solutions:**
- Limit Celery concurrency: `celery worker --concurrency=2`
- Adjust Docker memory limits in `docker-compose.yml`
- Clear Redis cache: `redis-cli FLUSHDB`

---

## 7. Code Standards

### Python Style Guide (Backend)

CivicQ follows **PEP 8** with **Black** formatting.

**Key conventions:**
- **Line length:** 88 characters (Black default)
- **Indentation:** 4 spaces
- **Imports:** Grouped (standard library, third-party, local)
- **Naming:**
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
- **Type hints:** Always use type hints for function parameters and returns
- **Docstrings:** Google-style docstrings

**Example:**

```python
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user import User

def get_active_users(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[User]:
    """
    Retrieve active users from the database.

    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return

    Returns:
        List of active User objects

    Raises:
        ValueError: If limit exceeds maximum allowed
    """
    if limit > 1000:
        raise ValueError("Limit cannot exceed 1000")

    return db.query(User)\
        .filter(User.is_active == True)\
        .offset(skip)\
        .limit(limit)\
        .all()
```

**Linting & Formatting:**

```bash
cd backend

# Auto-format code
black app/

# Check code style
flake8 app/

# Type checking
mypy app/
```

**Configuration files:**
- `.flake8` - Flake8 settings
- `pyproject.toml` - Black settings
- `mypy.ini` - MyPy settings

---

### TypeScript Style Guide (Frontend)

CivicQ uses **ESLint** + **Prettier** for TypeScript/React.

**Key conventions:**
- **Line length:** 100 characters
- **Indentation:** 2 spaces
- **Semicolons:** Required
- **Quotes:** Single quotes for strings, double for JSX attributes
- **Naming:**
  - Components: `PascalCase`
  - Functions/variables: `camelCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Interfaces: `PascalCase` (prefix `I` optional)
  - Types: `PascalCase`
- **Imports:** Auto-sorted by Prettier
- **React:** Functional components with hooks (no class components)

**Example:**

```typescript
import React, { useState, useEffect } from 'react';
import { Question } from '../types/question';
import { questionService } from '../services/questionService';

interface QuestionListProps {
  contestId: number;
  maxItems?: number;
}

const QuestionList: React.FC<QuestionListProps> = ({
  contestId,
  maxItems = 10
}) => {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        const data = await questionService.getByContest(contestId);
        setQuestions(data.slice(0, maxItems));
      } catch (error) {
        console.error('Failed to fetch questions:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchQuestions();
  }, [contestId, maxItems]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="question-list">
      {questions.map((question) => (
        <QuestionCard key={question.id} question={question} />
      ))}
    </div>
  );
};

export default QuestionList;
```

**Linting & Formatting:**

```bash
cd frontend

# Auto-format code
npm run format

# Lint code
npm run lint

# Fix auto-fixable issues
npm run lint -- --fix
```

---

### Git Commit Message Format

CivicQ follows **Conventional Commits** specification.

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, no logic change)
- `refactor:` Code refactoring (no feature/bug change)
- `perf:` Performance improvements
- `test:` Adding/updating tests
- `chore:` Build process, dependencies, tooling

**Examples:**

```bash
# Simple feature
git commit -m "feat: Add question filtering by category"

# Bug fix with scope
git commit -m "fix(auth): Resolve token expiration issue"

# Breaking change
git commit -m "feat!: Change API response format

BREAKING CHANGE: Question API now returns nested objects instead of flat structure"

# With ticket reference
git commit -m "fix(video): Resolve upload timeout issue

Increases upload timeout from 30s to 120s for large files.

Closes #123"
```

---

### Pull Request Process

**Before submitting:**
1. Create feature branch from `main`
2. Make your changes
3. Write/update tests
4. Run tests: `make test`
5. Run linters: `make lint`
6. Format code: `make format`
7. Update documentation if needed
8. Commit with conventional commit messages
9. Push to your branch

**PR Checklist:**
- [ ] Tests pass locally
- [ ] Code is formatted and linted
- [ ] Documentation updated
- [ ] No merge conflicts with `main`
- [ ] PR title follows conventional commit format
- [ ] Description explains what and why (not how)
- [ ] Screenshots included (for UI changes)
- [ ] Breaking changes documented

**PR Template:**

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How to test these changes

## Screenshots (if applicable)
Add screenshots here

## Checklist
- [ ] Tests pass
- [ ] Code is linted and formatted
- [ ] Documentation updated
```

---

## 8. Useful Commands

### Development Shortcuts

```bash
# Quick start everything
make dev

# Run all tests
make test

# Lint and format
make lint
make format

# Database migrations
make migrate

# Health check
make health

# Clean build artifacts
make clean
```

---

### Testing Commands

```bash
# Backend tests
cd backend
source venv/bin/activate
pytest                              # Run all tests
pytest -v                           # Verbose output
pytest -x                           # Stop on first failure
pytest --cov=app                    # With coverage
pytest -k "test_auth"               # Run tests matching pattern
pytest tests/api/test_auth.py       # Specific file
pytest --lf                         # Run last failed tests

# Frontend tests
cd frontend
npm test                            # Watch mode
npm test -- --watchAll=false        # Run once
npm test -- --coverage              # With coverage
npm test -- QuestionCard            # Specific test
```

---

### Database Commands

```bash
# Migrations
cd backend
source venv/bin/activate
alembic upgrade head                # Apply all migrations
alembic downgrade -1                # Rollback one migration
alembic current                     # Show current version
alembic history                     # Show migration history
alembic revision --autogenerate -m "Description"  # Create migration

# Database access
psql civicq                         # Connect to database
psql civicq -c "\dt"                # List tables
psql civicq -c "\d users"           # Describe table

# Database reset (WARNING: Destroys data)
./scripts/reset-db.sh
```

---

### Docker Commands

```bash
# Start services
docker-compose up                   # Start with logs
docker-compose up -d                # Start detached
docker-compose up --build           # Rebuild and start

# Stop services
docker-compose down                 # Stop containers
docker-compose down -v              # Stop and remove volumes

# View logs
docker-compose logs                 # All services
docker-compose logs -f backend      # Follow backend logs
docker-compose logs --tail=100 frontend  # Last 100 lines

# Execute commands in containers
docker-compose exec backend bash    # Shell into backend
docker-compose exec db psql -U civicq  # Connect to DB
docker-compose exec redis redis-cli # Connect to Redis

# Rebuild specific service
docker-compose build backend
docker-compose up -d backend

# View running containers
docker-compose ps

# View resource usage
docker stats
```

---

### API Testing Commands

```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Get questions (with auth)
curl http://localhost:8000/api/v1/questions \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Pretty print JSON with jq
curl http://localhost:8000/api/v1/questions | jq
```

---

### Code Quality Commands

```bash
# Backend
cd backend
black app/                          # Format code
flake8 app/                         # Lint code
mypy app/                           # Type check
pytest --cov=app --cov-report=html  # Coverage report

# Frontend
cd frontend
npm run format                      # Format code
npm run lint                        # Lint code
npm run lint -- --fix               # Auto-fix issues
npm test -- --coverage --watchAll=false  # Coverage report
```

---

### Git Commands Reference

```bash
# Branch management
git checkout main                   # Switch to main
git pull origin main                # Update main
git checkout -b feature/my-feature  # Create feature branch
git branch -d feature/old-feature   # Delete local branch

# Stashing changes
git stash                           # Stash current changes
git stash pop                       # Apply and remove stash
git stash list                      # List stashes

# Viewing changes
git status                          # Working directory status
git diff                            # Unstaged changes
git diff --staged                   # Staged changes
git log --oneline                   # Commit history

# Undoing changes
git checkout -- file.txt            # Discard changes to file
git reset HEAD file.txt             # Unstage file
git reset --soft HEAD~1             # Undo last commit (keep changes)
git reset --hard HEAD~1             # Undo last commit (discard changes)
```

---

### Environment Management

```bash
# Backend virtual environment
cd backend
python3 -m venv venv                # Create venv
source venv/bin/activate            # Activate (macOS/Linux)
venv\Scripts\activate               # Activate (Windows)
deactivate                          # Deactivate

# Install/update dependencies
pip install -r requirements.txt
pip freeze > requirements.txt       # Update requirements

# Frontend dependencies
cd frontend
npm install                         # Install dependencies
npm install <package>               # Add new package
npm uninstall <package>             # Remove package
npm update                          # Update all packages
npm outdated                        # Check for updates
```

---

## Additional Resources

### Documentation

- **Project README:** [README.md](README.md)
- **API Documentation:** http://localhost:8000/docs (when backend is running)
- **Architecture Docs:** [docs/architecture/](docs/architecture/)
- **Testing Guide:** [TESTING.md](TESTING.md)
- **Deployment Guide:** [DEPLOYMENT.md](DEPLOYMENT.md)

### External Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **React Docs:** https://react.dev/
- **SQLAlchemy Docs:** https://docs.sqlalchemy.org/
- **Alembic Docs:** https://alembic.sqlalchemy.org/
- **Tailwind CSS Docs:** https://tailwindcss.com/docs

### Getting Help

- **GitHub Issues:** Report bugs and request features
- **Team Chat:** [Your team communication platform]
- **Code Review:** Request reviews on pull requests
- **Documentation:** Check docs/ folder first

---

## Quick Reference Card

**Essential Commands:**

```bash
# First-time setup
make setup

# Start development
make dev                           # or: docker-compose up

# Run tests
make test

# Code quality
make lint && make format

# Database migration
cd backend && alembic upgrade head

# Health check
make health
```

**Common URLs:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Database: postgresql://civicq:civicq@localhost:5432/civicq
- Redis: redis://localhost:6379/0

**Emergency Commands:**
```bash
# Reset everything
docker-compose down -v
make clean
make setup

# View logs
docker-compose logs -f

# Rebuild containers
docker-compose build --no-cache
```

---

## Welcome to CivicQ!

You're now ready to start developing on CivicQ. Remember:

1. Always create feature branches
2. Write tests for new code
3. Run linters before committing
4. Follow code style guides
5. Ask questions when stuck

**Happy coding!** Let's build tools that strengthen democracy.

---

**Document Version:** 1.0
**Last Updated:** 2026-02-14
**Maintainers:** CivicQ Development Team
