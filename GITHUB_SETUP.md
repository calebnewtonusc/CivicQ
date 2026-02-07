# Push CivicQ to GitHub

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: **CivicQ**
3. Description: **Civic engagement platform for local elections**
4. Visibility: **Public** (or Private if you prefer)
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click **Create repository**

## Step 2: Push to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
cd /Users/joelnewton/Documents/School/Projects/CivicQ

# Add GitHub as remote origin
git remote add origin https://github.com/YOUR-USERNAME/CivicQ.git

# Push all commits to GitHub
git push -u origin main
```

Replace `YOUR-USERNAME` with your actual GitHub username.

## Step 3: Verify

Visit your repository at: `https://github.com/YOUR-USERNAME/CivicQ`

You should see:
- All your code files
- 5 commits
- Complete documentation
- Ready for Vercel deployment!

## Step 4: Connect to Vercel

1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Select your GitHub account
4. Find and import **CivicQ**
5. Configure:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
6. Add environment variables (optional for now)
7. Click **Deploy**

Done! Your CivicQ will be live in ~2 minutes!

## What Happens Next

- Every push to `main` → Automatic production deployment
- Every PR → Automatic preview deployment
- One-click rollbacks from Vercel dashboard

## If You Get "Remote Already Exists" Error

```bash
# Remove old remote
git remote remove origin

# Add new remote
git remote add origin https://github.com/YOUR-USERNAME/CivicQ.git

# Push
git push -u origin main
```

## Repository Stats

Once pushed, your repo will show:
- **5 commits**
- **80+ files**
- **~5,000+ lines of code**
- **8 documentation files**
- Complete fullstack app ready to deploy!

---

**Ready to become a civic tech legend? Let's go! 🚀**
