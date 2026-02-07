# Deployment Guide - Phase II Web Application

This guide provides step-by-step instructions for deploying the Todo Manager backend to Railway.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Deployment (Railway)](#backend-deployment-railway)
3. [Verification & Testing](#verification--testing)
4. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts

1. **GitHub Account** - For repository hosting
2. **Neon Account** - For PostgreSQL database ([neon.tech](https://neon.tech))
3. **Railway Account** - For backend hosting ([railway.app](https://railway.app))

### Required Tools

- Git installed locally
- Node.js 18.x or higher
- Python 3.13 or higher (for local testing)

---

## Backend Deployment (Railway)

### Step 1: Set Up Database (Neon PostgreSQL)

1. **Create Neon Account**
   - Go to [neon.tech](https://neon.tech)
   - Sign up with GitHub or email

2. **Create New Project**
   - Click "Create Project"
   - Name: \`todo-app-production\`
   - Region: Choose closest to your users (e.g., US East)
   - PostgreSQL version: 16 (latest)

3. **Get Connection String**
   - Go to project dashboard
   - Copy the connection string
   - **Important**: Change the protocol from \`postgresql://\` to \`postgresql+asyncpg://\`

   **Example:**
   \`\`\`
   Original: postgresql://username:password@ep-cool-smoke-123456.us-east-2.aws.neon.tech/neondb
   Updated:  postgresql+asyncpg://username:password@ep-cool-smoke-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
   \`\`\`

4. **Save Connection String**
   - Keep this for Railway environment variables

### Step 2: Generate Secrets

Generate secure secrets for authentication:

\`\`\`bash
# Generate BETTER_AUTH_SECRET (minimum 32 characters)
openssl rand -hex 32

# Generate JWT_SECRET (minimum 32 characters)
openssl rand -hex 32
\`\`\`

**Save these secrets** - you'll need the same \`BETTER_AUTH_SECRET\` for both backend and frontend!

### Step 3: Deploy to Railway

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Authorize Railway to access your repository
   - Select your repository

3. **Configure Service**
   - Railway will detect the backend automatically
   - Service name: \`todo-backend\`
   - Root directory: \`Phase-2-Web-App/backend\`

4. **Set Environment Variables**

   Go to service → Variables → Add variables:

   \`\`\`bash
   DATABASE_URL=postgresql+asyncpg://your-connection-string-from-neon
   BETTER_AUTH_SECRET=your-generated-secret-from-step-2
   JWT_SECRET=your-generated-jwt-secret-from-step-2
   CORS_ORIGINS=http://localhost:3000
   DEBUG=False
   JWT_ALGORITHM=HS256
   \`\`\`

   **Note**: Update \`CORS_ORIGINS\` with your frontend domain when deploying frontend.

5. **Deploy**
   - Click "Deploy"
   - Railway will automatically install dependencies and run
   - Wait for deployment to complete (2-5 minutes)

6. **Get Backend URL**
   - Once deployed, Railway provides a URL
   - Click "Generate Domain" if not automatically created
   - **Save this URL** for frontend configuration

7. **Verify Deployment**
   - Open \`https://your-backend-url.railway.app/\`
   - You should see: \`{"status":"ok","message":"Todo API is running"}\`

---

## Verification & Testing

### Test Backend API

\`\`\`bash
curl https://your-backend.railway.app/
# Should return: {"status":"ok","message":"Todo API is running"}
\`\`\`

### Test API Endpoints

\`\`\`bash
# Test health endpoint
curl https://your-backend.railway.app/

# Test docs (Swagger UI)
# Visit: https://your-backend.railway.app/docs
\`\`\`

---

## Troubleshooting

### Backend Issues

**CORS errors**: Verify \`CORS_ORIGINS\` includes your frontend domain

**Database connection fails**: Check connection string uses \`postgresql+asyncpg://\` and \`?sslmode=require\`

**500 errors**: Check Railway logs in the Railway dashboard

**Environment variables**: Verify all required environment variables are set correctly

---

**Deployment Complete!** 🚀

For detailed troubleshooting and advanced configuration, see the full documentation.
