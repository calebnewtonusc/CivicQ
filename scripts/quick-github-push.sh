#!/bin/bash

# Quick GitHub Push Script
# Alternative method using GitHub REST API

set -e

echo "🚀 Quick GitHub Setup for CivicQ"
echo ""

# Get GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
    echo "📝 You need a GitHub Personal Access Token"
    echo ""
    echo "Quick steps:"
    echo "1. Visit: https://github.com/settings/tokens/new"
    echo "2. Token name: CivicQ"
    echo "3. Expiration: 90 days (or your preference)"
    echo "4. Scopes: Check 'repo' (all repo permissions)"
    echo "5. Click 'Generate token'"
    echo "6. Copy the token (starts with ghp_)"
    echo ""
    read -p "Paste your GitHub token here: " GITHUB_TOKEN
    export GITHUB_TOKEN
fi

# Get GitHub username
echo ""
echo "🔍 Getting your GitHub info..."
GITHUB_USER=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user | jq -r '.login')

if [ "$GITHUB_USER" = "null" ] || [ -z "$GITHUB_USER" ]; then
    echo "❌ Invalid token. Please check your token and try again."
    exit 1
fi

echo "✅ Authenticated as: $GITHUB_USER"
echo ""

# Create repository using REST API
echo "📝 Creating repository 'CivicQ'..."

RESPONSE=$(curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{
    "name": "CivicQ",
    "description": "Civic engagement platform for local elections - turning campaigning into structured Q&A",
    "private": false,
    "has_issues": true,
    "has_wiki": false,
    "has_downloads": true
  }')

# Check if repo was created
REPO_URL=$(echo "$RESPONSE" | jq -r '.html_url')

if [ "$REPO_URL" = "null" ]; then
    # Check if repo already exists
    if echo "$RESPONSE" | jq -e '.errors[] | select(.message | contains("already exists"))' > /dev/null; then
        echo "ℹ️  Repository already exists"
        REPO_URL="https://github.com/$GITHUB_USER/CivicQ"
    else
        echo "❌ Error creating repository:"
        echo "$RESPONSE" | jq '.'
        exit 1
    fi
else
    echo "✅ Repository created!"
fi

echo ""
echo "🔗 Repository: $REPO_URL"
echo ""

# Push to GitHub
echo "📤 Pushing code to GitHub..."

# Remove existing origin
git remote remove origin 2>/dev/null || true

# Add remote with token authentication
git remote add origin "https://$GITHUB_TOKEN@github.com/$GITHUB_USER/CivicQ.git"

# Push
git push -u origin main

echo ""
echo "🎉 Success! CivicQ is live on GitHub!"
echo ""
echo "📍 Repository: $REPO_URL"
echo ""
echo "🚀 Next: Deploy to Vercel and Railway"
echo "   Frontend (Vercel): https://vercel.com/import/git?s=$REPO_URL"
echo "   Backend (Railway): https://railway.app/new"
echo ""

# Save token for later (optional)
read -p "Save token to .env for future use? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "GITHUB_TOKEN=$GITHUB_TOKEN" >> .env.local
    echo "✅ Token saved to .env.local (this file is gitignored)"
fi
