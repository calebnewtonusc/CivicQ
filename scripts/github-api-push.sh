#!/bin/bash

# GitHub GraphQL API - Automated Push for calebnewtonusc

set -e

echo "🚀 Pushing CivicQ to GitHub via GraphQL API"
echo "==========================================="
echo ""
echo "GitHub User: calebnewtonusc"
echo "Repository: CivicQ"
echo ""

# Get GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
    echo "📝 I need your GitHub Personal Access Token"
    echo ""
    echo "Get it here (auto-configured):"
    echo "👉 https://github.com/settings/tokens/new?description=CivicQ&scopes=repo"
    echo ""
    echo "Just click 'Generate token' and paste it here:"
    read -sp "Token: " GITHUB_TOKEN
    echo ""
    export GITHUB_TOKEN
fi

# Validate token with GraphQL
echo ""
echo "🔍 Validating token..."

USER_QUERY='{"query":"query { viewer { login } }"}'

USER_RESPONSE=$(curl -s -H "Authorization: bearer $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$USER_QUERY" \
  https://api.github.com/graphql)

# Check for errors
if echo "$USER_RESPONSE" | jq -e '.errors' > /dev/null 2>&1; then
    echo "❌ Token validation failed:"
    echo "$USER_RESPONSE" | jq -r '.errors[].message'
    exit 1
fi

GITHUB_USER=$(echo "$USER_RESPONSE" | jq -r '.data.viewer.login')

if [ "$GITHUB_USER" != "calebnewtonusc" ]; then
    echo "⚠️  Warning: Token is for user '$GITHUB_USER', not 'calebnewtonusc'"
    echo "   Continuing anyway..."
fi

echo "✅ Authenticated as: $GITHUB_USER"
echo ""

# Create repository using GraphQL mutation
echo "📦 Creating repository via GraphQL..."

CREATE_MUTATION='mutation {
  createRepository(input: {
    name: "CivicQ"
    description: "Civic engagement platform for local elections - turning campaigning into structured Q&A"
    visibility: PUBLIC
    hasIssuesEnabled: true
    hasWikiEnabled: false
  }) {
    repository {
      name
      url
      sshUrl
      createdAt
    }
  }
}'

CREATE_RESPONSE=$(curl -s -H "Authorization: bearer $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"$(echo $CREATE_MUTATION | tr '\n' ' ')\"}" \
  https://api.github.com/graphql)

# Check for errors
if echo "$CREATE_RESPONSE" | jq -e '.errors' > /dev/null 2>&1; then
    ERROR_MSG=$(echo "$CREATE_RESPONSE" | jq -r '.errors[0].message')

    if [[ "$ERROR_MSG" == *"already exists"* ]]; then
        echo "ℹ️  Repository already exists, using existing repo"
        REPO_URL="https://github.com/$GITHUB_USER/CivicQ"
    else
        echo "❌ Error creating repository:"
        echo "$CREATE_RESPONSE" | jq -r '.errors[].message'
        exit 1
    fi
else
    REPO_URL=$(echo "$CREATE_RESPONSE" | jq -r '.data.createRepository.repository.url')
    echo "✅ Repository created!"
fi

echo ""
echo "🔗 Repository: $REPO_URL"
echo ""

# Configure git remote
echo "⚙️  Configuring git remote..."

# Remove existing origin
git remote remove origin 2>/dev/null || true

# Add new origin with token
git remote add origin "https://$GITHUB_TOKEN@github.com/$GITHUB_USER/CivicQ.git"

# Push to GitHub
echo "📤 Pushing all commits to GitHub..."
git push -u origin main

echo ""
echo "🎉 SUCCESS! CivicQ is now on GitHub!"
echo ""

# Get repository stats via GraphQL
echo "📊 Repository Stats (via GraphQL):"

STATS_QUERY='query {
  repository(owner: "'$GITHUB_USER'", name: "CivicQ") {
    diskUsage
    pushedAt
    object(expression: "main") {
      ... on Commit {
        history {
          totalCount
        }
      }
    }
    languages(first: 3, orderBy: {field: SIZE, direction: DESC}) {
      edges {
        node {
          name
        }
        size
      }
    }
  }
}'

STATS_RESPONSE=$(curl -s -H "Authorization: bearer $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"$(echo $STATS_QUERY | tr '\n' ' ')\"}" \
  https://api.github.com/graphql)

COMMIT_COUNT=$(echo "$STATS_RESPONSE" | jq -r '.data.repository.object.history.totalCount')
REPO_SIZE=$(echo "$STATS_RESPONSE" | jq -r '.data.repository.diskUsage')
PUSHED_AT=$(echo "$STATS_RESPONSE" | jq -r '.data.repository.pushedAt')

echo "   📦 Commits pushed: $COMMIT_COUNT"
echo "   💾 Repository size: ${REPO_SIZE}KB"
echo "   🕐 Last push: $PUSHED_AT"
echo ""
echo "🔤 Top languages:"
echo "$STATS_RESPONSE" | jq -r '.data.repository.languages.edges[] | "   - \(.node.name): \(.size) bytes"'

echo ""
echo "✅ All done!"
echo ""
echo "🔗 View your repository:"
echo "   $REPO_URL"
echo ""
echo "🚀 Next: Deploy to production!"
echo "   Frontend (Vercel): https://vercel.com/new/import?s=$REPO_URL"
echo "   Backend (Railway): https://railway.app/new"
echo ""
