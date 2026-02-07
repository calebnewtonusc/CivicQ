# Push CivicQ to GitHub - Complete Guide

## Method 1: Automated Script (Recommended) ⚡

### Step 1: Get GitHub Token

1. Go to: https://github.com/settings/tokens/new
2. **Token name:** `CivicQ`
3. **Expiration:** 90 days (or your preference)
4. **Scopes:** Check ✓ **repo** (Full control of private repositories)
5. Click **Generate token**
6. Copy the token (starts with `ghp_...`)

### Step 2: Run the Script

```bash
cd /Users/joelnewton/Documents/School/Projects/CivicQ

# Set your token
export GITHUB_TOKEN='paste_your_token_here'

# Run the automated script
./scripts/quick-github-push.sh
```

**That's it!** The script will:
- ✅ Create the GitHub repository
- ✅ Push all your code
- ✅ Give you the repository URL

---

## Method 2: Manual GitHub CLI 🔧

```bash
cd /Users/joelnewton/Documents/School/Projects/CivicQ

# Login to GitHub
gh auth login

# Create repo and push
gh repo create CivicQ --public --source=. --remote=origin --push

# Done!
```

---

## Method 3: Manual via GitHub Website 🌐

### Step 1: Create Repository
1. Go to https://github.com/new
2. Repository name: **CivicQ**
3. Description: **Civic engagement platform for local elections**
4. Visibility: **Public** (or Private)
5. **DON'T** check "Initialize with README"
6. Click **Create repository**

### Step 2: Push Code
```bash
cd /Users/joelnewton/Documents/School/Projects/CivicQ

# Add GitHub as remote
git remote add origin https://github.com/YOUR-USERNAME/CivicQ.git

# Push code
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username.

---

## After Pushing to GitHub

Your repository will be at: `https://github.com/YOUR-USERNAME/CivicQ`

You'll see:
- ✅ 6 commits
- ✅ 80+ files
- ✅ Complete documentation
- ✅ Ready for deployment!

---

## Next: Deploy to Production 🚀

### Deploy Frontend (Vercel)
1. Go to https://vercel.com/new
2. Import your CivicQ repository
3. Configure:
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `build`
4. Click **Deploy**

**Live in 2 minutes!** ⚡

### Deploy Backend (Railway)
1. Go to https://railway.app/new
2. Select your CivicQ repository
3. Select the backend directory
4. Railway auto-detects Python/FastAPI
5. Add PostgreSQL + Redis databases
6. Click **Deploy**

**Live in 3 minutes!** 🚂

---

## Troubleshooting

### "Repository already exists"
```bash
# Use existing repo
git remote add origin https://github.com/YOUR-USERNAME/CivicQ.git
git push -u origin main
```

### "Authentication failed"
Make sure your token has **repo** permissions.

### "Permission denied"
```bash
# Use HTTPS with token
git remote set-url origin https://YOUR-TOKEN@github.com/YOUR-USERNAME/CivicQ.git
git push -u origin main
```

---

## What Gets Pushed

```
✅ All source code (frontend + backend)
✅ Complete documentation (8 markdown files)
✅ Configuration files (Docker, Vercel, Railway)
✅ Git history (6 commits)
✅ Everything you need to deploy!
```

---

**Choose your method and let's get CivicQ on GitHub! 🎉**
