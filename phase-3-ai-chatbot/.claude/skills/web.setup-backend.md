# Skill: Setup FastAPI Backend

## Description
Initialize a FastAPI backend project with proper structure, dependencies, database configuration, and CORS settings for the TODO web app.

## When to Use
- Starting Phase 2 (Web App) development
- Setting up FastAPI backend for the first time
- Need to establish backend project structure

## Prerequisites
- Python 3.11+ installed
- UV package manager installed
- Phase 2 workspace ready

## Workflow

### 1. Initialize Backend Directory Structure
```
phase-2-web-app/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # Database configuration
│   ├── config.py            # App configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── database.py      # SQLAlchemy models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── todo.py          # Pydantic schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   └── todos.py         # Todo endpoints
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── todo_repository.py
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       └── test_todos_api.py
├── pyproject.toml
└── .env
```

### 2. Install Dependencies
```bash
cd phase-2-web-app
uv init
uv add fastapi uvicorn sqlalchemy pydantic pydantic-settings python-dotenv
uv add --dev pytest pytest-cov pytest-asyncio httpx
```

### 3. Create Main FastAPI App
```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import todos
from database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TODO API",
    description="FastAPI backend for TODO web application",
    version="1.0.0"
)

# CORS configuration for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(todos.router)

@app.get("/")
def read_root():
    return {"message": "TODO API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

### 4. Configure Database
```python
# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

```python
# backend/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./todos.db"
    API_V1_STR: str = "/api"

    class Config:
        env_file = ".env"

settings = Settings()
```

### 5. Create Environment File
```bash
# .env
DATABASE_URL=sqlite:///./todos.db
# For PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/todos_db
```

### 6. Run Development Server
```bash
# From phase-2-web-app directory
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Access API:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc

## Checklist
- [ ] Backend directory structure created
- [ ] Dependencies installed (FastAPI, SQLAlchemy, etc.)
- [ ] main.py with FastAPI app created
- [ ] Database configuration set up
- [ ] CORS middleware configured for Next.js
- [ ] Environment variables configured
- [ ] Development server runs successfully
- [ ] API docs accessible at /docs
- [ ] Health check endpoint works

## Project Files

**pyproject.toml**
```toml
[project]
name = "todo-api"
version = "1.0.0"
description = "FastAPI backend for TODO web application"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "sqlalchemy>=2.0.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.21.0",
    "httpx>=0.25.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## Quick Start Commands
```bash
# Install all dependencies
uv sync

# Run development server
uv run uvicorn backend.main:app --reload

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=backend

# Generate OpenAPI schema
uv run python -c "import json; from backend.main import app; print(json.dumps(app.openapi()))" > openapi.json
```

## Next Steps
After setup:
1. Use `web.add-model.md` to create data models
2. Use `web.add-api-endpoint.md` to add API endpoints
3. Use `web.test-api.md` to write tests
4. Use `web.integrate-api.md` to connect with frontend

## Related Skills
- `web.add-model.md` - Create Pydantic/SQLAlchemy models
- `web.add-api-endpoint.md` - Add API endpoints
- `web.setup-frontend.md` - Setup Next.js frontend

## References
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [UV Package Manager](https://docs.astral.sh/uv/)
