#!/bin/bash

# Simple GitHub Push - Just handles GitHub, you do the rest!

set -e

echo "🚀 Pushing CivicQ to GitHub"
echo "==========================="
echo ""

# Use GitHub CLI (simplest method)
if ! command -v gh &> /dev/null; then
    echo "Installing GitHub CLI..."
    brew install gh
fi

echo "🔐 Authenticating with GitHub..."
gh auth login -p https -w

echo ""
echo "📤 Creating repository and pushing code..."

# Create repo and push in one command
gh repo create CivicQ \
    --public \
    --description "Civic engagement platform for local elections" \
    --source=. \
    --remote=origin \
    --push || {
        echo "Repository might already exist, pushing to it..."
        GITHUB_USER=$(gh api user -q .login)
        git remote set-url origin "https://github.com/$GITHUB_USER/CivicQ.git" 2>/dev/null || \
        git remote add origin "https://github.com/$GITHUB_USER/CivicQ.git"
        git push -u origin main
    }

# Get repo URL
GITHUB_USER=$(gh api user -q .login)
REPO_URL="https://github.com/$GITHUB_USER/CivicQ"

echo ""
echo "🎉 SUCCESS! Code is on GitHub!"
echo ""
echo "🔗 Repository: $REPO_URL"
echo ""
echo "📊 Stats:"
gh repo view --json name,description,diskUsage,pushedAt,url --jq '. | "   Name: \(.name)\n   Size: \(.diskUsage)KB\n   Last push: \(.pushedAt)\n   URL: \(.url)"'

echo ""
echo "✅ Done! Now deploy manually:"
echo ""
echo "   Frontend (Vercel): https://vercel.com/new/import?s=$REPO_URL"
echo "   Backend (Railway): https://railway.app/new"
echo ""
