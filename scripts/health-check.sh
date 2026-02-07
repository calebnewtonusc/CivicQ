#!/bin/bash

# CivicQ Health Check Script

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🏥 CivicQ Health Check"
echo "===================="
echo ""

# Check PostgreSQL
echo -n "PostgreSQL... "
if pg_isready -h localhost -p 5432 -U civicq &> /dev/null; then
    echo -e "${GREEN}✅ Running${NC}"
else
    echo -e "${RED}❌ Not running${NC}"
fi

# Check Redis
echo -n "Redis... "
if redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✅ Running${NC}"
else
    echo -e "${RED}❌ Not running${NC}"
fi

# Check Backend API
echo -n "Backend API... "
if curl -s http://localhost:8000/health &> /dev/null; then
    echo -e "${GREEN}✅ Running${NC}"
    RESPONSE=$(curl -s http://localhost:8000/health)
    echo "   Response: $RESPONSE"
else
    echo -e "${RED}❌ Not running${NC}"
fi

# Check Frontend
echo -n "Frontend... "
if curl -s http://localhost:3000 &> /dev/null; then
    echo -e "${GREEN}✅ Running${NC}"
else
    echo -e "${RED}❌ Not running${NC}"
fi

echo ""
echo "Health check complete!"
