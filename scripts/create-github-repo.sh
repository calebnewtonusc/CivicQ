#!/bin/bash

# GitHub Repository Creation Script using GraphQL API
# This script creates a GitHub repository and pushes CivicQ

set -e

echo "🚀 Creating GitHub Repository for CivicQ..."
echo ""

# Check if GitHub token is set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Error: GITHUB_TOKEN environment variable is not set"
    echo ""
    echo "To create a GitHub token:"
    echo "1. Go to https://github.com/settings/tokens"
    echo "2. Click 'Generate new token (classic)'"
    echo "3. Name: 'CivicQ Deployment'"
    echo "4. Scopes: Select 'repo' (full control of private repositories)"
    echo "5. Click 'Generate token'"
    echo "6. Copy the token"
    echo ""
    echo "Then run:"
    echo "export GITHUB_TOKEN='your_token_here'"
    echo "./scripts/create-github-repo.sh"
    exit 1
fi

# Repository details
REPO_NAME="CivicQ"
REPO_DESCRIPTION="Civic engagement platform for local elections - turning campaigning into structured Q&A"
REPO_VISIBILITY="public"  # Change to "private" if you want a private repo

echo "📝 Repository Details:"
echo "   Name: $REPO_NAME"
echo "   Description: $REPO_DESCRIPTION"
echo "   Visibility: $REPO_VISIBILITY"
echo ""

# GraphQL mutation to create repository
read -r -d '' MUTATION <<'EOF' || true
mutation CreateRepository($name: String!, $description: String!, $visibility: RepositoryVisibility!) {
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
      defaultBranchRef {
        name
      }
    }
  }
}
EOF

# Create JSON payload
VARIABLES=$(cat <<EOF
{
  "name": "$REPO_NAME",
  "description": "$REPO_DESCRIPTION",
  "visibility": "${REPO_VISIBILITY^^}"
}
EOF
)

PAYLOAD=$(jq -n \
  --arg query "$MUTATION" \
  --argjson variables "$VARIABLES" \
  '{query: $query, variables: $variables}')

echo "📡 Creating repository on GitHub..."

# Make GraphQL API call
RESPONSE=$(curl -s -X POST \
  -H "Authorization: bearer $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  https://api.github.com/graphql)

# Check for errors
if echo "$RESPONSE" | jq -e '.errors' > /dev/null 2>&1; then
    echo "❌ Error creating repository:"
    echo "$RESPONSE" | jq '.errors'
    exit 1
fi

# Extract repository URL
REPO_URL=$(echo "$RESPONSE" | jq -r '.data.createRepository.repository.url')
SSH_URL=$(echo "$RESPONSE" | jq -r '.data.createRepository.repository.sshUrl')

echo "✅ Repository created successfully!"
echo ""
echo "🔗 Repository URL: $REPO_URL"
echo "🔗 SSH URL: $SSH_URL"
echo ""

# Add remote and push
echo "📤 Pushing code to GitHub..."

# Remove origin if it exists
git remote remove origin 2>/dev/null || true

# Add new origin (using HTTPS with token)
GITHUB_USER=$(curl -s -H "Authorization: bearer $GITHUB_TOKEN" https://api.github.com/user | jq -r '.login')
git remote add origin "https://$GITHUB_TOKEN@github.com/$GITHUB_USER/$REPO_NAME.git"

# Push to GitHub
git push -u origin main

echo ""
echo "🎉 Success! CivicQ is now on GitHub!"
echo ""
echo "📍 View your repository:"
echo "   $REPO_URL"
echo ""
echo "🚀 Next steps:"
echo "   1. Deploy frontend to Vercel: https://vercel.com/new"
echo "   2. Deploy backend to Railway: https://railway.app/new"
echo "   3. Connect both deployments!"
echo ""
