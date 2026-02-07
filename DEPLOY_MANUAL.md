# CivicQ Manual Deployment Guide

Simple 3-step deployment. Each step takes ~2 minutes.

---

## Step 1: Push to GitHub (2 minutes)

### Option A: Using GitHub CLI (Easiest)

```bash
cd /Users/joelnewton/Documents/School/Projects/CivicQ

# Login to GitHub
gh auth login

# Create repo and push
gh repo create CivicQ --public --source=. --push
```

### Option B: Manual Method

1. Go to https://github.com/new
2. Repository name: **CivicQ**
3. Make it **Public**
4. DON'T initialize with anything
5. Click **Create repository**

Then:
```bash
cd /Users/joelnewton/Documents/School/Projects/CivicQ
git remote add origin https://github.com/YOUR-USERNAME/CivicQ.git
git push -u origin main
```

✅ **Your code is now on GitHub!**

---

## Step 2: Deploy Frontend to Vercel (2 minutes)

1. Go to: https://vercel.com/new

2. Click **"Import Git Repository"**

3. Find and select your **CivicQ** repository

4. Configure the project:
   - **Project Name**: `civicq` (or whatever you want)
   - **Framework Preset**: `Create React App`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`

5. Click **Deploy**

6. Wait 2 minutes... Done! ✅

7. **Copy your live URL** (looks like `https://civicq-xxxx.vercel.app`)

---

## Step 3: Deploy Backend to Railway (3 minutes)

1. Go to: https://railway.app

2. Click **"Start a New Project"**

3. Choose **"Deploy from GitHub repo"**

4. Select your **CivicQ** repository

5. Railway will auto-detect it's a Python app

6. **Add a PostgreSQL database**:
   - Click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
   - Railway automatically connects it to your backend

7. **Add Redis**:
   - Click **"+ New"** → **"Database"** → **"Add Redis"**
   - Automatically connected!

8. **Configure the backend service**:
   - Click on your backend service
   - Go to **Settings** → **Root Directory**
   - Set to: `backend`
   - Click **"Deploy"**

9. **Add environment variables** (in Railway dashboard):
   ```
   ALLOWED_ORIGINS=https://your-vercel-url.vercel.app
   ```

10. **Get your backend URL**:
    - Click **Settings** → **Generate Domain**
    - Copy the URL (looks like `https://civicq-production.up.railway.app`)

✅ **Backend is live!**

---

## Step 4: Connect Frontend to Backend (1 minute)

1. Go back to **Vercel dashboard**

2. Go to your CivicQ project → **Settings** → **Environment Variables**

3. Add this variable:
   ```
   Name: REACT_APP_API_URL
   Value: https://your-railway-url.up.railway.app/api
   ```
   (Use your Railway URL from Step 3)

4. Go to **Deployments** → **Redeploy** (to apply the new env variable)

✅ **Frontend and backend are connected!**

---

## Step 5: Test It Works

Visit your Vercel URL: `https://civicq-xxxx.vercel.app`

You should see the CivicQ homepage! 🎉

---

## Summary URLs

After deployment, you'll have:

- **GitHub**: `https://github.com/YOUR-USERNAME/CivicQ`
- **Frontend**: `https://civicq-xxxx.vercel.app`
- **Backend**: `https://civicq-production.up.railway.app`
- **API Docs**: `https://civicq-production.up.railway.app/api/docs`

---

## What's Free?

- ✅ **GitHub**: Unlimited public repos
- ✅ **Vercel**: Free hosting, 100GB bandwidth/month
- ✅ **Railway**: $5 free credit/month (plenty for development)

---

## Troubleshooting

### Frontend shows error connecting to backend?
- Check REACT_APP_API_URL in Vercel environment variables
- Make sure it ends with `/api`
- Redeploy frontend after changing env variables

### Backend not starting on Railway?
- Check it detected `backend` as root directory
- Check build logs in Railway dashboard
- Make sure PostgreSQL and Redis are connected

### Need to run database migrations?
In Railway dashboard:
1. Click on your backend service
2. Go to **Settings** → **Deploy Triggers**
3. Add a deploy command: `alembic upgrade head`

---

## Cost Breakdown

**Free Tier:**
- Vercel: Free
- Railway: $5/month credit (enough for small projects)
- Total: **FREE** for development!

**When you grow:**
- Vercel Pro: $20/month (100+ users)
- Railway: ~$20-30/month (active production use)
- Total: **~$40-50/month** for real production

---

## Next Steps After Deployment

1. ✅ Test your live site
2. ✅ Share the URL with friends
3. ✅ Start implementing features:
   - Authentication
   - Question submission
   - Video recording
   - Admin dashboard

---

**You're live on the internet! 🚀**

Any issues? Check the logs:
- Vercel: Dashboard → Your Project → Deployments → Logs
- Railway: Dashboard → Your Service → Logs
