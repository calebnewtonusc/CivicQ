# Deploy CivicQ to Vercel in 5 Minutes

The fastest way to get CivicQ live on the internet.

## Step 1: Install Vercel CLI

```bash
npm i -g vercel
```

## Step 2: Deploy Frontend

```bash
cd /Users/joelnewton/Documents/School/Projects/CivicQ/frontend

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

Follow the prompts:
- **Set up and deploy?** Yes
- **Which scope?** Your account
- **Link to existing project?** No
- **Project name:** civicq (or your choice)
- **Directory:** ./
- **Override settings?** No

**Done!** Your frontend is live at: `https://civicq-xxxx.vercel.app`

## Step 3: Set Up Database (Choose One)

### Option A: Neon (Recommended - Free tier with pgvector)

1. Go to https://neon.tech and sign up
2. Create a new project: **CivicQ**
3. Copy the connection string
4. In Neon SQL Editor, run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

### Option B: Vercel Postgres

1. In Vercel dashboard → Your Project → Storage
2. Create Database → Postgres
3. Connection string is auto-added to environment

### Option C: Supabase

1. Go to https://supabase.com and sign up
2. Create new project: **CivicQ**
3. Copy the connection string (direct connection, not pooler)
4. In SQL Editor, run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

## Step 4: Set Up Redis

1. Go to https://upstash.com and sign up
2. Create Redis database: **civicq-redis**
3. Copy the Redis URL

## Step 5: Configure Environment Variables

In Vercel dashboard → Your Project → Settings → Environment Variables:

Add these variables:

```bash
# Frontend (if deploying separately)
REACT_APP_API_URL=https://your-backend.vercel.app/api

# Backend
DATABASE_URL=<paste-your-postgres-url>
REDIS_URL=<paste-your-redis-url>
SECRET_KEY=<generate-new-secret>
ENVIRONMENT=production
DEBUG=false
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

Generate secret key:
```bash
openssl rand -hex 32
```

## Step 6: Deploy Backend (Optional)

```bash
cd /Users/joelnewton/Documents/School/Projects/CivicQ/backend
vercel --prod
```

## Step 7: Update Frontend Environment

Update `REACT_APP_API_URL` in frontend Vercel environment variables:
```
REACT_APP_API_URL=https://your-backend-url.vercel.app/api
```

Then redeploy frontend:
```bash
cd frontend
vercel --prod
```

## Step 8: Run Database Migrations

```bash
cd backend
vercel env pull .env.production
source venv/bin/activate
alembic upgrade head
```

## Step 9: Test Your Deployment

Visit your frontend URL: `https://civicq-xxxx.vercel.app`

You should see the CivicQ homepage!

## That's It! 🎉

Your CivicQ is now live on the internet!

## What You Get Free

- **Vercel**: Free hosting, automatic HTTPS, CDN
- **Neon**: 10 GB database, 100 hours compute/month
- **Upstash**: 10,000 Redis commands/day

Perfect for development and small pilots!

## Next Steps

1. **Custom Domain**: Add in Vercel dashboard → Settings → Domains
2. **Monitoring**: Enable Vercel Analytics
3. **Security**: Review [DEPLOYMENT.md](DEPLOYMENT.md) security checklist
4. **Features**: Start implementing authentication, questions, etc.

## Quick Commands

```bash
# View deployment
vercel ls

# View logs
vercel logs

# Redeploy
vercel --prod

# Rollback
vercel promote <previous-deployment-url>
```

## Troubleshooting

### Build fails?
- Check environment variables are set
- View build logs in Vercel dashboard

### API not working?
- Check `DATABASE_URL` is set correctly
- Check `ALLOWED_ORIGINS` matches frontend URL
- View function logs in Vercel dashboard

### Database connection fails?
- Verify connection string is correct
- Check database is not paused (Neon auto-pauses after inactivity)

## Getting Help

- Full guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- Vercel docs: https://vercel.com/docs
- Neon docs: https://neon.tech/docs
- Upstash docs: https://upstash.com/docs

---

**Your CivicQ is live! Now go change local democracy! 🏛️**
