#!/bin/bash

# CivicQ Candidate Portal Demo Setup Script
# This script sets up the demo candidate account and provides instructions

set -e  # Exit on error

echo ""
echo "=========================================="
echo "  CivicQ Candidate Portal Demo Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the correct directory
if [ ! -f "CANDIDATE_PORTAL_README.md" ]; then
    echo -e "${RED}Error: This script must be run from the CivicQ project root directory${NC}"
    echo "Current directory: $(pwd)"
    exit 1
fi

echo -e "${BLUE}Step 1: Creating Demo Candidate Account${NC}"
echo "----------------------------------------"

# Check if backend exists
if [ ! -d "backend" ]; then
    echo -e "${RED}Error: backend directory not found${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo -e "${YELLOW}Warning: Virtual environment not found at backend/venv${NC}"
    echo "Please create a virtual environment first:"
    echo "  cd backend"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment and run script
cd backend
echo "Activating virtual environment..."

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    # Windows Git Bash
    source venv/Scripts/activate
else
    echo -e "${RED}Error: Could not find activation script${NC}"
    exit 1
fi

echo "Running demo account creation script..."
python scripts/create_demo_candidate.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Demo account created successfully!${NC}"
else
    echo -e "${RED}✗ Failed to create demo account${NC}"
    exit 1
fi

cd ..

echo ""
echo -e "${BLUE}Step 2: Starting the Application${NC}"
echo "----------------------------------------"
echo ""
echo "To start CivicQ, you need to run TWO commands in separate terminal windows:"
echo ""
echo -e "${YELLOW}Terminal 1 - Backend:${NC}"
echo "  cd backend"
echo "  source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "  uvicorn app.main:app --reload"
echo ""
echo -e "${YELLOW}Terminal 2 - Frontend:${NC}"
echo "  cd frontend"
echo "  npm start"
echo ""
echo -e "${BLUE}Step 3: Access the Candidate Portal${NC}"
echo "----------------------------------------"
echo ""
echo "Once both servers are running:"
echo ""
echo "1. Open your browser to: ${GREEN}http://localhost:3000${NC}"
echo "2. Click 'Sign In'"
echo "3. Log in with:"
echo "   ${YELLOW}Email:${NC}    demo.candidate@civicq.com"
echo "   ${YELLOW}Password:${NC} DemoCandidate2024!"
echo ""
echo "4. Click '${GREEN}Dashboard${NC}' in the navigation menu"
echo "5. Explore the candidate features:"
echo "   - View pending questions"
echo "   - Record video answers"
echo "   - Edit your profile"
echo "   - Track engagement metrics"
echo ""
echo -e "${BLUE}Quick Links:${NC}"
echo "----------------------------------------"
echo "Dashboard:      http://localhost:3000/candidate/dashboard"
echo "Edit Profile:   http://localhost:3000/candidate/profile/edit"
echo "Onboarding:     http://localhost:3000/candidate/onboarding"
echo ""
echo -e "${BLUE}For More Information:${NC}"
echo "----------------------------------------"
echo "Read: ${YELLOW}CANDIDATE_PORTAL_README.md${NC} for full documentation"
echo ""
echo "=========================================="
echo "  Setup Complete! Ready to Demo"
echo "=========================================="
echo ""
