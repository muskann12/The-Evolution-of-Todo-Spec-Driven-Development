# Environment Variables Setup Guide

This guide explains all environment variables needed for local development and production deployment.

---

## 📋 Summary of Changes

### ✅ Backend `.env` Updated
- ✅ Added `?sslmode=require` to DATABASE_URL (required for Neon production)
- ✅ Added `JWT_ALGORITHM=HS256`
- ✅ Added production configuration examples (commented)
- ✅ Organized with clear LOCAL vs PRODUCTION sections

### ✅ Frontend `.env.local` Updated
- ✅ Added `BETTER_AUTH_SECRET` (matching backend)
- ✅ Added `BETTER_AUTH_URL`
- ✅ Added production configuration examples (commented)
- ✅ Organized with clear LOCAL vs PRODUCTION sections

---

## 🔧 Local Development (Current Setup)

### Backend `.env` - LOCAL CONFIGURATION
```bash
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_HvxfMqG5Fb7Y@ep-withered-sunset-a1kv12v0-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
JWT_SECRET=b0e3cc396c2f15582a8f6ca6d0a2cb5f32e227cdd6e1d02d5517e215721f225c
BETTER_AUTH_SECRET=b0e3cc396c2f15582a8f6ca6d0a2cb5f32e227cdd6e1d02d5517e215721f225c
JWT_ALGORITHM=HS256
CORS_ORIGINS=http://localhost:3000
DEBUG=True
```

**Status**: ✅ Ready for local development

### Frontend `.env.local` - LOCAL CONFIGURATION
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=b0e3cc396c2f15582a8f6ca6d0a2cb5f32e227cdd6e1d02d5517e215721f225c
BETTER_AUTH_URL=http://localhost:3000
NODE_ENV=development
```

**Status**: ✅ Ready for local development

---

## 🚀 Production Deployment

### Step 1: Set Up Neon Database (If using new database)

**Option A: Use Existing Database (Recommended)**
Your current DATABASE_URL is already configured with Neon. You can use this for production or create a new production database.

**Option B: Create New Production Database**
1. Go to [neon.tech](https://neon.tech)
2. Create a new project for production
3. Copy the connection string
4. Add `?sslmode=require` at the end

### Step 2: Railway Environment Variables (Backend)

Set these in Railway Dashboard → Service → Variables:

```bash
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_HvxfMqG5Fb7Y@ep-withered-sunset-a1kv12v0-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require

JWT_SECRET=b0e3cc396c2f15582a8f6ca6d0a2cb5f32e227cdd6e1d02d5517e215721f225c

BETTER_AUTH_SECRET=b0e3cc396c2f15582a8f6ca6d0a2cb5f32e227cdd6e1d02d5517e215721f225c

JWT_ALGORITHM=HS256

CORS_ORIGINS=http://localhost:3000

DEBUG=False
```

**⚠️ IMPORTANT**: After deploying frontend to Vercel, update `CORS_ORIGINS` with your actual Vercel URL!

### Step 3: Vercel Environment Variables (Frontend)

Set these in Vercel Dashboard → Project → Settings → Environment Variables:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000

BETTER_AUTH_SECRET=b0e3cc396c2f15582a8f6ca6d0a2cb5f32e227cdd6e1d02d5517e215721f225c

BETTER_AUTH_URL=http://localhost:3000

NODE_ENV=production
```

**⚠️ IMPORTANT**: After deploying backend to Railway, update `NEXT_PUBLIC_API_URL` with your actual Railway URL!

### Step 4: Update After First Deployment

#### Railway (Backend) - UPDATE CORS
After frontend is deployed to Vercel:
```bash
CORS_ORIGINS=https://your-app.vercel.app
```

#### Vercel (Frontend) - UPDATE API URL
After backend is deployed to Railway:
```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
BETTER_AUTH_URL=https://your-app.vercel.app
```

---

## 🔐 Security Notes

### Current Secrets Analysis

✅ **JWT_SECRET**: `b0e3cc396c2f15582a8f6ca6d0a2cb5f32e227cdd6e1d02d5517e215721f225c`
- Length: 64 characters ✅
- Format: Hexadecimal ✅
- Status: **Secure for production**

✅ **BETTER_AUTH_SECRET**: Same as JWT_SECRET
- Length: 64 characters ✅
- Format: Hexadecimal ✅
- Status: **Secure for production**
- ⚠️ **CRITICAL**: Must be identical on both backend and frontend!

### Security Checklist

- [x] Secrets are minimum 32 characters
- [x] BETTER_AUTH_SECRET matches between backend and frontend
- [x] Database URL uses SSL (`?sslmode=require`)
- [ ] Update CORS_ORIGINS after frontend deployment
- [ ] Set DEBUG=False in Railway production
- [ ] Never commit production secrets to git

---

## 📝 Environment Variable Reference

### Backend Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | ✅ Yes | PostgreSQL connection string with asyncpg driver | `postgresql+asyncpg://user:pass@host/db?sslmode=require` |
| `JWT_SECRET` | ✅ Yes | Secret for JWT token signing (32+ chars) | Generated with `openssl rand -hex 32` |
| `BETTER_AUTH_SECRET` | ✅ Yes | Better Auth secret (32+ chars, must match frontend) | Same as JWT_SECRET |
| `JWT_ALGORITHM` | ✅ Yes | JWT signing algorithm | `HS256` |
| `CORS_ORIGINS` | ✅ Yes | Allowed frontend origins (comma-separated) | `https://your-app.vercel.app` |
| `DEBUG` | ✅ Yes | Debug mode (True for dev, False for prod) | `True` / `False` |

### Frontend Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | ✅ Yes | Backend API base URL | `https://your-backend.railway.app` |
| `BETTER_AUTH_SECRET` | ✅ Yes | Better Auth secret (must match backend!) | Same as backend BETTER_AUTH_SECRET |
| `BETTER_AUTH_URL` | ✅ Yes | Frontend base URL | `https://your-app.vercel.app` |
| `NODE_ENV` | ✅ Yes | Node environment | `development` / `production` |

---

## 🔄 Deployment Workflow

### 1. Initial Deployment

```bash
# Step 1: Deploy Backend to Railway
# - Use current backend/.env values
# - Set DEBUG=False
# - Keep CORS_ORIGINS=http://localhost:3000 (temporary)

# Step 2: Get Railway URL
# Example: https://todo-backend-production.up.railway.app

# Step 3: Deploy Frontend to Vercel
# - Update NEXT_PUBLIC_API_URL with Railway URL
# - Keep other values from frontend/.env.local

# Step 4: Get Vercel URL
# Example: https://your-app.vercel.app

# Step 5: Update Railway CORS_ORIGINS
# Change from: http://localhost:3000
# Change to: https://your-app.vercel.app

# Step 6: Update Vercel BETTER_AUTH_URL
# Change from: http://localhost:3000
# Change to: https://your-app.vercel.app
```

### 2. Post-Deployment Testing

```bash
# Test backend health
curl https://your-backend.railway.app/
# Expected: {"status":"ok","message":"Todo API is running"}

# Test frontend
# Open: https://your-app.vercel.app
# - Sign up for account
# - Create a task
# - Verify task appears
```

---

## ⚠️ Common Issues & Solutions

### Issue 1: CORS Errors

**Symptom**: Frontend can't connect to backend, CORS errors in browser console

**Solution**:
- Verify `CORS_ORIGINS` in Railway includes your Vercel URL
- Ensure no trailing slash in URLs
- Check Railway logs for CORS-related errors

### Issue 2: Authentication Fails

**Symptom**: Can't log in, JWT verification fails

**Solution**:
- Verify `BETTER_AUTH_SECRET` is **identical** on backend and frontend
- Check secret is minimum 32 characters
- Clear browser cookies and try again

### Issue 3: Database Connection Fails

**Symptom**: 500 errors, can't connect to database

**Solution**:
- Verify `DATABASE_URL` includes `?sslmode=require`
- Check protocol is `postgresql+asyncpg://` (not `postgresql://`)
- Verify Neon database is running
- Test connection in Railway shell

### Issue 4: Frontend Can't Reach Backend

**Symptom**: API calls return 404 or timeout

**Solution**:
- Verify `NEXT_PUBLIC_API_URL` is correct in Vercel
- Check Railway backend is deployed and running
- Ensure no trailing slash in API URL
- Test backend directly: `curl https://your-backend.railway.app/`

---

## 🎯 Quick Copy-Paste Templates

### Railway Environment Variables (Copy All)

```env
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_HvxfMqG5Fb7Y@ep-withered-sunset-a1kv12v0-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
JWT_SECRET=b0e3cc396c2f15582a8f6ca6d0a2cb5f32e227cdd6e1d02d5517e215721f225c
BETTER_AUTH_SECRET=b0e3cc396c2f15582a8f6ca6d0a2cb5f32e227cdd6e1d02d5517e215721f225c
JWT_ALGORITHM=HS256
CORS_ORIGINS=http://localhost:3000
DEBUG=False
```

**⚠️ Remember to update `CORS_ORIGINS` after frontend deployment!**

### Vercel Environment Variables (Copy All)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=b0e3cc396c2f15582a8f6ca6d0a2cb5f32e227cdd6e1d02d5517e215721f225c
BETTER_AUTH_URL=http://localhost:3000
NODE_ENV=production
```

**⚠️ Remember to update URLs after backend deployment!**

---

## 📚 Additional Resources

- **DEPLOYMENT.md** - Complete deployment guide with detailed steps
- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Vercel Docs**: [vercel.com/docs](https://vercel.com/docs)
- **Neon Docs**: [neon.tech/docs](https://neon.tech/docs)

---

**Last Updated**: January 2026
**Status**: ✅ Environment files configured and ready for deployment

---

<div align="center">

**🔐 Keep your secrets safe! Never commit production credentials to git.**

[⬆ Back to Top](#environment-variables-setup-guide)

</div>
