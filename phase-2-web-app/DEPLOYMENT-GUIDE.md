# 🚀 Complete Deployment Guide - Railway vs Hugging Face

**Project**: Todo Manager Full-Stack App
**Backend**: FastAPI (Python)
**Frontend**: Next.js (React)
**Database**: Neon PostgreSQL (Already configured)

---

## 📊 Platform Comparison: Railway vs Hugging Face

| Feature | Railway | Hugging Face Spaces |
|---------|---------|-------------------|
| **Best For** | Production APIs | ML Models & Demos |
| **FastAPI Support** | ✅ Excellent | ⚠️ Limited (Gradio/Streamlit focused) |
| **Cost** | $5-10/month | FREE |
| **Performance** | ⭐⭐⭐⭐⭐ Fast | ⭐⭐⭐ Moderate |
| **Cold Starts** | ❌ None | ✅ Minimal |
| **Custom Domains** | ✅ Yes | ❌ No |
| **Environment Variables** | ✅ Easy | ✅ Secrets support |
| **Database Support** | ✅ Direct connection | ✅ External DB only |
| **Deployment** | Git push auto-deploy | Git push auto-deploy |
| **HTTPS/SSL** | ✅ Automatic | ✅ Automatic |
| **CI/CD** | ✅ Built-in | ✅ Built-in |
| **Logs & Monitoring** | ✅ Excellent | ⚠️ Basic |
| **Scaling** | ✅ Easy | ❌ Limited |

---

## 🎯 My Recommendation

### ✅ **Use Railway** if:
- You need a production-ready API
- You want zero cold starts
- You need better performance
- You can afford $5-10/month
- You want custom domains
- You need detailed monitoring

### ⚠️ **Use Hugging Face** if:
- You want completely FREE hosting
- Your API has low traffic
- You're okay with slower response times
- You're building an ML/AI app
- You don't mind cold starts

---

## 🚂 Option 1: Deploy Backend to Railway (RECOMMENDED)

### Why Railway?
- ✅ Built specifically for production APIs
- ✅ Excellent FastAPI support
- ✅ No cold starts (instant response)
- ✅ Great developer experience
- ✅ Built-in monitoring & logs
- ✅ Easy to scale

### Cost: ~$5-10/month

---

### Step-by-Step: Railway Deployment

#### 1. Prepare Your Backend

**1.1 Ensure you have these files in `/phase-2-web-app/backend/`:**

**`requirements.txt`** (already exists):
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlmodel==0.0.14
asyncpg==0.29.0
alembic==1.13.1
pydantic==2.5.3
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```

**`Procfile`** (create this):
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**`railway.json`** (create this):
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**`runtime.txt`** (create this):
```
python-3.12
```

#### 2. Sign Up for Railway

1. Go to: https://railway.app
2. Click **"Login"** → Sign in with **GitHub**
3. Authorize Railway to access your repositories
4. **Add a payment method** (required, even for free trial - you get $5 free credit)

#### 3. Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository: `HackathonII-TODO-APP`
4. Railway will detect it's a Python project

#### 4. Configure the Service

After deployment starts:

1. Click on your service in Railway dashboard
2. Go to **Settings** tab
3. Update these settings:
   - **Root Directory**: `phase-2-web-app/backend`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Watch Paths**: `phase-2-web-app/backend/**`

#### 5. Add Environment Variables

Click on **Variables** tab and add these:

```bash
# Database (your existing Neon PostgreSQL)
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_HvxfMqG5Fb7Y@ep-withered-sunset-a1kv12v0-pooler.ap-southeast-1.aws.neon.tech/neondb

# Authentication Secret
BETTER_AUTH_SECRET=b0e3cc396c2f15582a8f6ca6d0a2cb5f32e227cdd6e1d02d5517e215721f225c

# CORS - Update after Vercel deployment
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000

# Debug mode
DEBUG=False
```

**Important**:
- Don't use quotes around values in Railway
- Update `CORS_ORIGINS` with your actual Vercel URL after frontend deployment

#### 6. Generate Public Domain

1. Go to **Settings** → **Networking** tab
2. Click **"Generate Domain"**
3. Railway will give you a URL like: `https://your-app.railway.app`
4. **Save this URL** - you'll need it for frontend configuration

#### 7. Deploy

1. Railway will automatically deploy your backend
2. Wait 2-3 minutes for build to complete
3. Check **Deployments** tab for logs
4. Once deployed, test your API:
   - Visit: `https://your-app.railway.app` (should show `{"status":"ok"}`)
   - Visit: `https://your-app.railway.app/docs` (Swagger UI)

#### 8. Test Authentication Endpoint

```bash
# Test signup
curl -X POST https://your-app.railway.app/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"test123"}'

# Test login
curl -X POST https://your-app.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"admin123"}'
```

---

## 🤗 Option 2: Deploy Backend to Hugging Face Spaces

### Why Hugging Face?
- ✅ Completely FREE
- ✅ Good for demos and low-traffic apps
- ✅ Easy deployment
- ⚠️ Not optimized for REST APIs (designed for ML models)
- ⚠️ May have cold starts
- ⚠️ Limited to 2 vCPU & 16GB RAM

### Cost: FREE

---

### Step-by-Step: Hugging Face Deployment

#### 1. Prepare Your Backend

**1.1 Create `app.py` in `/phase-2-web-app/backend/`:**

Hugging Face Spaces expects an `app.py` file in the root. Create this:

```python
"""
Hugging Face Space entry point for FastAPI backend.
"""
from app.main import app

# Hugging Face Spaces will run this file
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
```

**1.2 Create `requirements.txt`** (already exists, ensure it has all dependencies)

**1.3 Create `.env.example`** (for documentation):
```env
DATABASE_URL=your_neon_postgresql_url_here
BETTER_AUTH_SECRET=your_secret_here
CORS_ORIGINS=https://your-frontend.vercel.app
DEBUG=False
```

#### 2. Sign Up for Hugging Face

1. Go to: https://huggingface.co
2. Click **"Sign Up"** → Create account or sign in with GitHub
3. Verify your email

#### 3. Create a New Space

1. Click your profile → **"New Space"**
2. Configure:
   - **Owner**: Your username
   - **Space name**: `todo-api` (or your choice)
   - **License**: Choose a license (e.g., MIT)
   - **Select SDK**: Choose **"Gradio"** (we'll modify this)
   - **Space hardware**: **CPU basic (free)**
   - **Visibility**: Public or Private

3. Click **"Create Space"**

#### 4. Configure Space

After space is created:

1. Go to **Files** tab
2. Click **"Add file"** → **"Upload files"**
3. Upload these files from your backend:
   - `app.py` (the entry point we created)
   - `requirements.txt`
   - All files from `/app` directory
   - `alembic/` folder (if you use migrations)

**Alternative (Git):**
```bash
# Clone the space repository
git clone https://huggingface.co/spaces/YOUR_USERNAME/todo-api
cd todo-api

# Copy your backend files
cp -r /path/to/phase-2-web-app/backend/* .

# Commit and push
git add .
git commit -m "Initial deployment"
git push
```

#### 5. Add Secrets (Environment Variables)

1. Go to **Settings** tab in your Space
2. Scroll down to **"Repository secrets"**
3. Click **"New secret"** and add:

```
DATABASE_URL
Value: postgresql+asyncpg://neondb_owner:npg_HvxfMqG5Fb7Y@ep-withered-sunset-a1kv12v0-pooler.ap-southeast-1.aws.neon.tech/neondb

BETTER_AUTH_SECRET
Value: b0e3cc396c2f15582a8f6ca6d0a2cb5f32e227cdd6e1d02d5517e215721f225c

CORS_ORIGINS
Value: https://your-frontend.vercel.app,http://localhost:3000

DEBUG
Value: False
```

#### 6. Update App to Read Secrets

Modify `app.py` to load secrets:

```python
"""
Hugging Face Space entry point for FastAPI backend.
"""
import os
from app.main import app

# Hugging Face Spaces sets port to 7860
PORT = int(os.getenv("PORT", 7860))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )
```

#### 7. Wait for Build

1. Hugging Face will automatically build your Space
2. Check **Logs** tab to see build progress
3. Once built, your API will be available at:
   - `https://huggingface.co/spaces/YOUR_USERNAME/todo-api`

#### 8. Access Your API

Your API endpoints will be at:
```
https://YOUR_USERNAME-todo-api.hf.space/
https://YOUR_USERNAME-todo-api.hf.space/docs
https://YOUR_USERNAME-todo-api.hf.space/api/auth/login
```

#### ⚠️ Limitations of Hugging Face for FastAPI:

1. **Not optimized for REST APIs** - Hugging Face Spaces is designed for ML models
2. **Cold starts** - If unused for 48 hours, space may sleep
3. **No custom domains** - You're stuck with `.hf.space` domain
4. **Limited resources** - 2 vCPU, 16GB RAM on free tier
5. **Slower performance** - Compared to Railway/Render

---

## 🎨 Frontend Deployment (Vercel) - For Both Options

This section is the same regardless of whether you chose Railway or Hugging Face for backend.

### Step 1: Prepare Frontend

**1.1 Create `.env.production` in `/phase-2-web-app/frontend/`:**

```env
# Backend API URL - Update with your actual backend URL
NEXT_PUBLIC_API_URL=https://your-app.railway.app

# OR if using Hugging Face:
# NEXT_PUBLIC_API_URL=https://YOUR_USERNAME-todo-api.hf.space

NODE_ENV=production
```

**1.2 Verify `next.config.js`:**

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  swcMinify: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
}

module.exports = nextConfig
```

**1.3 Test build locally:**

```bash
cd phase-2-web-app/frontend
npm run build
```

If build succeeds, you're ready to deploy!

### Step 2: Deploy to Vercel

#### 2.1 Sign Up for Vercel

1. Go to: https://vercel.com
2. Click **"Sign Up"**
3. Choose **"Continue with GitHub"**
4. Authorize Vercel

#### 2.2 Import Project

1. Click **"Add New..."** → **"Project"**
2. Click **"Import"** next to your repository
3. Configure project:
   - **Framework Preset**: `Next.js` (auto-detected)
   - **Root Directory**: `phase-2-web-app/frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Install Command**: `npm install`

#### 2.3 Add Environment Variables

Before deploying, click **"Environment Variables"**:

Add this variable:
```
Name: NEXT_PUBLIC_API_URL
Value: https://your-app.railway.app
```

(Or your Hugging Face URL: `https://YOUR_USERNAME-todo-api.hf.space`)

**Important**: Make sure it starts with `NEXT_PUBLIC_` - this makes it available in the browser.

#### 2.4 Deploy

1. Click **"Deploy"**
2. Wait 2-3 minutes for deployment
3. Vercel will show you the URL: `https://your-app.vercel.app`

#### 2.5 Update Backend CORS

Now that you have your Vercel URL, update your backend:

**For Railway:**
1. Go to Railway dashboard
2. Click your service → **Variables**
3. Update `CORS_ORIGINS`:
   ```
   CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
   ```
4. Service will auto-redeploy

**For Hugging Face:**
1. Go to your Space → **Settings** → **Repository secrets**
2. Edit `CORS_ORIGINS`:
   ```
   https://your-app.vercel.app,http://localhost:3000
   ```
3. Space will rebuild

---

## ✅ Deployment Verification Checklist

### Backend Checklist
- [ ] Backend is accessible at your URL
- [ ] `/docs` endpoint shows Swagger UI
- [ ] Health check works: `GET /` returns `{"status":"ok"}`
- [ ] Database connection successful
- [ ] Environment variables loaded correctly
- [ ] CORS includes your Vercel URL

### Frontend Checklist
- [ ] Frontend loads at Vercel URL
- [ ] Can access login/signup pages
- [ ] API calls are sent to correct backend URL
- [ ] No CORS errors in browser console
- [ ] Can successfully login with test credentials

### Integration Checklist
- [ ] Login works end-to-end
- [ ] Can create tasks
- [ ] Can view tasks
- [ ] Can update tasks
- [ ] Can delete tasks
- [ ] Authentication persists on refresh

---

## 🐛 Common Issues & Solutions

### Issue 1: CORS Errors

**Error:**
```
Access to fetch at 'https://backend...' from origin 'https://frontend...'
has been blocked by CORS policy
```

**Solution:**
1. Check backend `CORS_ORIGINS` includes your Vercel URL
2. Make sure CORS_ORIGINS has no trailing slash
3. Restart backend after updating environment variables

### Issue 2: Backend Not Responding

**For Railway:**
- Check **Deployments** tab for errors
- View **Logs** for runtime errors
- Verify all environment variables are set

**For Hugging Face:**
- Check **Logs** tab in Space
- Space may be sleeping - try visiting the URL to wake it
- Verify secrets are set correctly

### Issue 3: Frontend API Calls Fail

**Error:** `Failed to fetch` or `Network Error`

**Solution:**
1. Verify `NEXT_PUBLIC_API_URL` is set in Vercel
2. Check backend is actually running (visit /docs)
3. Open browser DevTools → Network tab to see actual error
4. Ensure backend URL doesn't have trailing slash

### Issue 4: Database Connection Fails

**Error:** `could not connect to server` or `asyncpg connection failed`

**Solution:**
1. Verify `DATABASE_URL` starts with `postgresql+asyncpg://`
2. Check Neon database is active (login to Neon dashboard)
3. Ensure `asyncpg` is in requirements.txt
4. Test connection string locally first

### Issue 5: Authentication Fails

**Error:** `Invalid credentials` or `Token verification failed`

**Solution:**
1. Check `BETTER_AUTH_SECRET` is set correctly on backend
2. Verify JWT secret is the same everywhere (64 character hex string)
3. Create test user with known credentials
4. Check backend logs for authentication errors

---

## 💰 Cost Summary

### Option 1: Railway (Recommended)
```
Backend (Railway):     $5-10/month
Frontend (Vercel):     $0/month (Hobby tier)
Database (Neon):       $0/month (Free tier, 0.5GB)
─────────────────────────────────
Total:                 ~$5-10/month
```

### Option 2: Hugging Face (Free)
```
Backend (HF Spaces):   $0/month
Frontend (Vercel):     $0/month (Hobby tier)
Database (Neon):       $0/month (Free tier, 0.5GB)
─────────────────────────────────
Total:                 $0/month
```

---

## 🚀 Quick Deploy Commands

### For Railway:

```bash
# 1. Create deployment files
cd phase-2-web-app/backend

# Create Procfile
echo "web: uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Create railway.json
cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF

# Commit and push
git add .
git commit -m "chore: add Railway deployment config"
git push

# Then deploy via Railway dashboard (connect GitHub repo)
```

### For Hugging Face:

```bash
# 1. Create app.py entry point
cd phase-2-web-app/backend

cat > app.py << 'EOF'
"""Hugging Face Space entry point."""
import os
from app.main import app

PORT = int(os.getenv("PORT", 7860))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
EOF

# 2. Commit and push to HF Space
git add .
git commit -m "chore: add Hugging Face Space config"
# Push to your HF Space repo
```

### For Frontend (Vercel):

```bash
cd phase-2-web-app/frontend

# Create production environment file
echo "NEXT_PUBLIC_API_URL=https://your-backend-url" > .env.production

# Test build
npm run build

# Commit and push
git add .
git commit -m "chore: configure for Vercel deployment"
git push

# Then deploy via Vercel dashboard (connect GitHub repo)
```

---

## 📚 Additional Resources

### Railway
- Documentation: https://docs.railway.app
- FastAPI Template: https://docs.railway.app/guides/fastapi
- Environment Variables: https://docs.railway.app/develop/variables

### Hugging Face Spaces
- Documentation: https://huggingface.co/docs/hub/spaces
- Spaces Secrets: https://huggingface.co/docs/hub/spaces-overview#managing-secrets
- FastAPI on Spaces: https://huggingface.co/docs/hub/spaces-sdks-docker-fastapi

### Vercel
- Next.js Deployment: https://vercel.com/docs/frameworks/nextjs
- Environment Variables: https://vercel.com/docs/projects/environment-variables
- Custom Domains: https://vercel.com/docs/projects/domains

### Neon PostgreSQL
- Documentation: https://neon.tech/docs
- Connection Pooling: https://neon.tech/docs/connect/connection-pooling
- Branching: https://neon.tech/docs/introduction/branching

---

## 🎯 Final Recommendation

### For Production / Serious Projects:
→ **Use Railway** ($5-10/month)
- Better performance
- Zero cold starts
- Production-ready
- Great monitoring
- Easy to scale

### For Learning / Demos / Low Traffic:
→ **Use Hugging Face** (FREE)
- Completely free
- Good enough for demos
- Easy to set up
- Works for low-traffic apps

### Frontend:
→ **Use Vercel** (FREE)
- Perfect for Next.js
- Automatic deployments
- Great performance
- Free SSL/HTTPS
- Global CDN

---

**Created**: 2026-01-08
**Project**: Todo Manager - Phase II Web Application
**Stack**: FastAPI + Next.js + Neon PostgreSQL
