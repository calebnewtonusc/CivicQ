#!/bin/bash

# GitHub GraphQL API - Complete Setup
# Creates repository and pushes CivicQ

set -e

echo "🚀 CivicQ GitHub Setup via GraphQL API"
echo "======================================="
echo ""

# Get token
if [ -z "$GITHUB_TOKEN" ]; then
    echo "📝 Enter your GitHub Personal Access Token"
    echo "   Get one here: https://github.com/settings/tokens/new"
    echo "   Scopes needed: repo"
    echo ""
    read -sp "Token (input hidden): " GITHUB_TOKEN
    echo ""
    export GITHUB_TOKEN
fi

# Validate token and get user info using GraphQL
echo ""
echo "🔍 Validating token..."

USER_QUERY='query {
  viewer {
    login
    name
    email
  }
}'

USER_RESPONSE=$(curl -s -H "Authorization: bearer $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"$USER_QUERY\"}" \
  https://api.github.com/graphql)

# Check for errors
if echo "$USER_RESPONSE" | jq -e '.errors' > /dev/null 2>&1; then
    echo "❌ Invalid token or API error:"
    echo "$USER_RESPONSE" | jq '.errors'
    exit 1
fi

GITHUB_USER=$(echo "$USER_RESPONSE" | jq -r '.data.viewer.login')
GITHUB_NAME=$(echo "$USER_RESPONSE" | jq -r '.data.viewer.name')

echo "✅ Authenticated as: $GITHUB_USER ($GITHUB_NAME)"
echo ""

# Create repository using GraphQL mutation
echo "📝 Creating repository 'CivicQ'..."

CREATE_REPO_MUTATION='mutation($name: String!, $description: String!, $visibility: RepositoryVisibility!) {
  createRepository(input: {
    name: $name
    description: $description
    visibility: $visibility
    hasIssuesEnabled: true
    hasWikiEnabled: false
  }) {
    repository {
      name
      url
      sshUrl
      owner {
        login
      }
    }
  }
}'

VARIABLES='{
  "name": "CivicQ",
  "description": "Civic engagement platform for local elections - turning campaigning into structured Q&A",
  "visibility": "PUBLIC"
}'

REPO_RESPONSE=$(curl -s -H "Authorization: bearer $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"$(echo $CREATE_REPO_MUTATION | tr '\n' ' ')\",\"variables\":$VARIABLES}" \
  https://api.github.com/graphql)

# Check for errors
if echo "$REPO_RESPONSE" | jq -e '.errors' > /dev/null 2>&1; then
    ERROR_MSG=$(echo "$REPO_RESPONSE" | jq -r '.errors[0].message')

    # Check if repo already exists
    if [[ "$ERROR_MSG" == *"already exists"* ]]; then
        echo "ℹ️  Repository already exists, will use existing repo"
        REPO_URL="https://github.com/$GITHUB_USER/CivicQ"
    else
        echo "❌ Error creating repository:"
        echo "$REPO_RESPONSE" | jq '.errors'
        exit 1
    fi
else
    REPO_URL=$(echo "$REPO_RESPONSE" | jq -r '.data.createRepository.repository.url')
    echo "✅ Repository created successfully!"
fi

echo ""
echo "🔗 Repository URL: $REPO_URL"
echo ""

# Configure git
echo "⚙️  Configuring git remote..."

# Remove existing origin if present
git remote remove origin 2>/dev/null || true

# Add new origin with token authentication
git remote add origin "https://$GITHUB_TOKEN@github.com/$GITHUB_USER/CivicQ.git"

# Push to GitHub
echo "📤 Pushing code to GitHub..."
git push -u origin main

echo ""
echo "🎉 SUCCESS! CivicQ is now on GitHub!"
echo ""
echo "📍 View your repository:"
echo "   $REPO_URL"
echo ""
echo "📊 Repository Stats:"

# Get repository info using GraphQL
REPO_INFO_QUERY='query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    diskUsage
    object(expression: "main") {
      ... on Commit {
        history {
          totalCount
        }
      }
    }
    languages(first: 5, orderBy: {field: SIZE, direction: DESC}) {
      edges {
        node {
          name
        }
        size
      }
    }
  }
}'

REPO_INFO_VARIABLES="{
  \"owner\": \"$GITHUB_USER\",
  \"name\": \"CivicQ\"
}"

REPO_INFO=$(curl -s -H "Authorization: bearer $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"$(echo $REPO_INFO_QUERY | tr '\n' ' ')\",\"variables\":$REPO_INFO_VARIABLES}" \
  https://api.github.com/graphql)

COMMIT_COUNT=$(echo "$REPO_INFO" | jq -r '.data.repository.object.history.totalCount')
REPO_SIZE=$(echo "$REPO_INFO" | jq -r '.data.repository.diskUsage')

echo "   📦 Total commits: $COMMIT_COUNT"
echo "   💾 Repository size: ${REPO_SIZE}KB"
echo ""

# Get top languages
echo "🔤 Top languages:"
echo "$REPO_INFO" | jq -r '.data.repository.languages.edges[] | "   - \(.node.name): \(.size) bytes"'

echo ""
echo "🚀 Next Steps:"
echo ""
echo "1. Deploy Frontend to Vercel:"
echo "   https://vercel.com/new/import?s=$REPO_URL"
echo ""
echo "2. Deploy Backend to Railway:"
echo "   https://railway.app/new"
echo ""
echo "3. Connect both services and go live!"
echo ""
