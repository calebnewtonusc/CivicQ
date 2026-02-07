# Push CivicQ to GitHub - Token Method

## Step 1: Get Your Token (30 seconds)

Click this link (auto-configured):
**https://github.com/settings/tokens/new?description=CivicQ&scopes=repo**

1. Click **"Generate token"**
2. Copy the token (starts with `ghp_...`)

## Step 2: Run This Command

```bash
cd /Users/joelnewton/Documents/School/Projects/CivicQ

# Set your token (paste your actual token)
export GITHUB_TOKEN='paste_your_token_here'

# Run the push
./scripts/github-api-push.sh
```

## Or All-in-One Command

```bash
cd /Users/joelnewton/Documents/School/Projects/CivicQ
export GITHUB_TOKEN='paste_your_ghp_token' && ./scripts/github-api-push.sh
```

Replace `paste_your_ghp_token` with your actual token!

---

## What Happens

The script will:
1. ✅ Validate your token via GraphQL
2. ✅ Create repository **github.com/calebnewtonusc/CivicQ**
3. ✅ Push all 11 commits
4. ✅ Show repository stats
5. ✅ Give you deployment URLs

---

## After GitHub Push

Your repository: **https://github.com/calebnewtonusc/CivicQ**

Then deploy:
- **Frontend**: https://vercel.com/new
- **Backend**: https://railway.app/new

See [DEPLOY_MANUAL.md](DEPLOY_MANUAL.md) for full instructions!
