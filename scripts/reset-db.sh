#!/bin/bash

# CivicQ Database Reset Script
# WARNING: This will destroy all data!

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}⚠️  WARNING: This will destroy all database data!${NC}"
read -p "Are you sure you want to continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo -e "${RED}🗑️  Dropping database...${NC}"
dropdb --if-exists civicq
createdb civicq

echo -e "${GREEN}✅ Database recreated!${NC}"

echo -e "${BLUE}📊 Setting up pgvector extension...${NC}"
psql civicq -c "CREATE EXTENSION IF NOT EXISTS vector;"

echo -e "${GREEN}✅ pgvector extension installed!${NC}"

echo ""
echo "Database has been reset. Run migrations to create tables:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  alembic upgrade head"
