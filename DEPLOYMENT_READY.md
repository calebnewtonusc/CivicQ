# 🎉 CivicQ is on GitHub!

**Repository:** https://github.com/calebnewtonusc/CivicQ

✅ 13 commits pushed
✅ All code uploaded
✅ Ready to deploy!

---

## 🚨 Security: Revoke Your Token

Since you shared your token in chat, please revoke it for security:

1. Go to: https://github.com/settings/tokens
2. Find "CivicQ" token
3. Click "Delete"
4. Create a new one if you need it later

---

## 🚀 Deploy Now (10 minutes total)

### Step 1: Frontend on Vercel (3 minutes)

**Click this link:**
https://vercel.com/new/import?s=https://github.com/calebnewtonusc/CivicQ

1. Click **Import**
2. Configure:
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `build`
3. Click **Deploy**

**Done!** Copy your Vercel URL (like `https://civicq-xxx.vercel.app`)

---

### Step 2: Backend on Railway (5 minutes)

**Go to:** https://railway.app/new

1. Choose **"Deploy from GitHub repo"**
2. Select **calebnewtonusc/CivicQ**
3. Click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
4. Click **"+ New"** → **"Database"** → **"Add Redis"**
5. Click your backend service → **Settings**
6. Set **Root Directory** to: `backend`
7. Add environment variable:
   ```
   ALLOWED_ORIGINS=https://your-vercel-url.vercel.app
   ```
   (Use your actual Vercel URL from Step 1)
8. Click **"Generate Domain"** to get your backend URL

**Done!** Copy your Railway URL (like `https://civicq.up.railway.app`)

---

### Step 3: Connect Frontend to Backend (2 minutes)

1. Go to **Vercel dashboard** → Your CivicQ project
2. **Settings** → **Environment Variables**
3. Add:
   ```
   Name: REACT_APP_API_URL
   Value: https://your-railway-url.up.railway.app/api
   ```
   (Use your Railway URL from Step 2)
4. **Deployments** → Click **"..."** → **"Redeploy"**

---

## ✅ You're Live!

Visit your Vercel URL and you'll see CivicQ running!

**Your URLs:**
- **Frontend:** https://civicq-xxx.vercel.app
- **Backend:** https://civicq.up.railway.app
- **API Docs:** https://civicq.up.railway.app/api/docs
- **GitHub:** https://github.com/calebnewtonusc/CivicQ

---

## 💡 What's Free?

- ✅ **GitHub:** Unlimited public repos
- ✅ **Vercel:** 100GB bandwidth/month
- ✅ **Railway:** $5 free credit/month (plenty for development!)

---

## 🎊 Congratulations!

You just deployed a full-stack civic tech platform!

**Next steps:**
1. Share your live URL
2. Start implementing features
3. Change the world with better local democracy! 🏛️

Need help? Check [DEPLOY_MANUAL.md](DEPLOY_MANUAL.md) for troubleshooting.
