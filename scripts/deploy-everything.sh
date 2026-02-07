#!/bin/bash

# CivicQ Complete Automated Deployment
# This script does EVERYTHING - GitHub, Vercel, Railway

set -e

echo "🚀 CivicQ Complete Deployment Automation"
echo "========================================="
echo ""
echo "This script will:"
echo "  1. Push to GitHub"
echo "  2. Deploy frontend to Vercel"
echo "  3. Deploy backend to Railway"
echo "  4. Give you live URLs"
echo ""
echo "Let's go! 🎉"
echo ""

# Check for required tools
command -v jq >/dev/null 2>&1 || { echo "Installing jq..."; brew install jq; }
command -v gh >/dev/null 2>&1 || { echo "Installing GitHub CLI..."; brew install gh; }

# Step 1: GitHub
echo "📦 STEP 1: Pushing to GitHub"
echo "=============================="
echo ""

# Try GitHub CLI first
if gh auth status 2>/dev/null; then
    echo "✅ Already authenticated with GitHub CLI"
else
    echo "🔐 Logging into GitHub..."
    gh auth login -p https -w
fi

echo ""
echo "Creating repository and pushing..."

# Create repo and push
gh repo create CivicQ \
    --public \
    --description "Civic engagement platform for local elections - turning campaigning into structured Q&A" \
    --source=. \
    --remote=origin \
    --push 2>/dev/null || {
        echo "Repository might already exist, pushing anyway..."
        git remote set-url origin https://github.com/$(gh api user -q .login)/CivicQ.git 2>/dev/null || \
        git remote add origin https://github.com/$(gh api user -q .login)/CivicQ.git
        git push -u origin main
    }

GITHUB_USER=$(gh api user -q .login)
REPO_URL="https://github.com/$GITHUB_USER/CivicQ"

echo ""
echo "✅ Code pushed to GitHub!"
echo "🔗 Repository: $REPO_URL"
echo ""

# Step 2: Vercel
echo "📦 STEP 2: Deploying Frontend to Vercel"
echo "========================================"
echo ""

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "Installing Vercel CLI..."
    npm install -g vercel
fi

# Deploy frontend
echo "Deploying frontend..."
cd frontend

# Login to Vercel if needed
vercel login || true

# Deploy
echo ""
echo "Deploying to production..."
FRONTEND_URL=$(vercel --prod --yes 2>&1 | grep -o 'https://[^ ]*' | tail -1)

cd ..

echo ""
echo "✅ Frontend deployed!"
echo "🔗 Live URL: $FRONTEND_URL"
echo ""

# Step 3: Railway
echo "📦 STEP 3: Deploying Backend to Railway"
echo "========================================"
echo ""

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "Installing Railway CLI..."
    brew install railway
fi

# Login to Railway
echo "Logging into Railway..."
railway login || true

# Create project and deploy
echo "Creating Railway project..."
cd backend

railway init 2>/dev/null || echo "Project might already exist"

# Add PostgreSQL
echo "Adding PostgreSQL database..."
railway add --plugin postgresql 2>/dev/null || echo "PostgreSQL might already exist"

# Add Redis
echo "Adding Redis..."
railway add --plugin redis 2>/dev/null || echo "Redis might already exist"

# Deploy
echo "Deploying backend..."
railway up

# Get backend URL
BACKEND_URL=$(railway domain 2>/dev/null || echo "Will be available in Railway dashboard")

cd ..

echo ""
echo "✅ Backend deployed!"
echo "🔗 Backend URL: $BACKEND_URL"
echo ""

# Step 4: Connect Everything
echo "📦 STEP 4: Connecting Services"
echo "==============================="
echo ""

echo "Updating Vercel environment variables..."
vercel env add REACT_APP_API_URL production --yes <<< "$BACKEND_URL/api" 2>/dev/null || true

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================="
echo ""
echo "Your CivicQ is now LIVE! 🚀"
echo ""
echo "📍 URLs:"
echo "   GitHub:   $REPO_URL"
echo "   Frontend: $FRONTEND_URL"
echo "   Backend:  $BACKEND_URL"
echo ""
echo "📋 Next Steps:"
echo "   1. Visit your frontend: $FRONTEND_URL"
echo "   2. Check Railway dashboard for backend URL if not shown above"
echo "   3. Configure database in Railway dashboard"
echo "   4. Run migrations (see Railway logs)"
echo ""
echo "🎊 You did it! CivicQ is live on the internet!"
echo ""
