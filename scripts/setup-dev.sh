#!/bin/bash

# CivicQ Development Environment Setup Script

set -e

echo "🚀 Setting up CivicQ development environment..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${BLUE}📦 Starting Docker services...${NC}"
docker-compose up -d db redis

# Wait for PostgreSQL to be ready
echo -e "${BLUE}⏳ Waiting for PostgreSQL to be ready...${NC}"
sleep 5

# Check if PostgreSQL is ready
until docker-compose exec -T db pg_isready -U civicq &> /dev/null; do
    echo -e "${BLUE}⏳ Waiting for PostgreSQL...${NC}"
    sleep 2
done

echo -e "${GREEN}✅ PostgreSQL is ready!${NC}"

# Create pgvector extension
echo -e "${BLUE}📊 Setting up pgvector extension...${NC}"
docker-compose exec -T db psql -U civicq -d civicq -c "CREATE EXTENSION IF NOT EXISTS vector;" || true

echo -e "${GREEN}✅ Database setup complete!${NC}"

# Backend setup
echo -e "${BLUE}🐍 Setting up Python backend...${NC}"
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo -e "${BLUE}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}✅ Backend setup complete!${NC}"

# Frontend setup
echo -e "${BLUE}📱 Setting up React frontend...${NC}"
cd ../frontend

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}Installing npm dependencies...${NC}"
    npm install
fi

echo -e "${GREEN}✅ Frontend setup complete!${NC}"

cd ..

echo ""
echo -e "${GREEN}🎉 Development environment setup complete!${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Start the backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload"
echo ""
echo "2. In a new terminal, start the frontend:"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "3. Or use Docker Compose to start everything:"
echo "   docker-compose up"
echo ""
echo "📚 See SETUP.md for more details!"
