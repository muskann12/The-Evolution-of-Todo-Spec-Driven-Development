# Skill: Deploy Web App

## Description
Deploy Next.js frontend and FastAPI backend to production environments.

## When to Use
- Ready for production deployment
- Setting up staging environment
- Continuous deployment

## Workflow

### 1. Frontend Deployment (Vercel - Recommended for Next.js)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from frontend directory
cd frontend
vercel

# Production deployment
vercel --prod
```

**Environment Variables:**
- Add `NEXT_PUBLIC_API_URL` in Vercel dashboard
- Point to production API URL

### 2. Backend Deployment Options

**Option A: Railway**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Deploy from backend directory
cd backend
railway login
railway init
railway up
```

**Option B: Docker + Cloud Platform**
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and push
docker build -t todo-api .
docker push your-registry/todo-api:latest

# Deploy to cloud (AWS, GCP, Azure)
```

### 3. Database Setup
```bash
# For production, use PostgreSQL
DATABASE_URL=postgresql://user:pass@host:5432/todos_prod
```

### 4. CORS Configuration
```python
# Update main.py for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",
        "http://localhost:3000"  # for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Checklist
- [ ] Frontend deployed (Vercel/Netlify)
- [ ] Backend deployed (Railway/Docker)
- [ ] Database configured (PostgreSQL)
- [ ] Environment variables set
- [ ] CORS configured for production
- [ ] SSL/HTTPS enabled
- [ ] Domain configured (optional)
- [ ] Monitoring set up
- [ ] Backup strategy in place

## Quick Deploy Commands
```bash
# Frontend (Vercel)
cd frontend && vercel --prod

# Backend (Railway)
cd backend && railway up

# Docker
docker-compose up -d
```

## References
- [Vercel Documentation](https://vercel.com/docs)
- [Railway Documentation](https://docs.railway.app/)
- [Docker Documentation](https://docs.docker.com/)
