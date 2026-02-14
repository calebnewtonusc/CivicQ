#!/bin/bash
#
# Start Celery Worker for CivicQ
#
# This script starts the Celery worker for processing background tasks
# like ballot data refresh, video transcription, etc.
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}CivicQ Celery Worker Startup${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""

# Change to backend directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/../backend"

cd "$BACKEND_DIR"
echo -e "${YELLOW}Working directory: $BACKEND_DIR${NC}"
echo ""

# Check if Redis is running
echo -e "${YELLOW}Checking Redis connection...${NC}"
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${RED}ERROR: Redis is not running!${NC}"
    echo -e "${YELLOW}Please start Redis first:${NC}"
    echo -e "  redis-server"
    echo ""
    exit 1
fi
echo -e "${GREEN}Redis is running${NC}"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}ERROR: .env file not found!${NC}"
    echo -e "${YELLOW}Please copy .env.example to .env and configure it:${NC}"
    echo -e "  cp .env.example .env"
    echo ""
    exit 1
fi

# Check if Python environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}WARNING: No virtual environment detected${NC}"
    echo -e "${YELLOW}Consider activating your virtualenv first:${NC}"
    echo -e "  source venv/bin/activate"
    echo ""
fi

# Start Celery worker
echo -e "${GREEN}Starting Celery worker...${NC}"
echo ""

celery -A app.tasks worker \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=100 \
    --pool=solo

# Note: --pool=solo is for development on macOS
# For production on Linux, remove --pool=solo to use prefork
