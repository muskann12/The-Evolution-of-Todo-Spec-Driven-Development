# Todo Manager Backend - FastAPI

> RESTful API backend for the Todo Manager application built with FastAPI, SQLModel, and PostgreSQL.

[![FastAPI](https://img.shields.io/badge/FastAPI-Python_3.13%2B-009688)](https://fastapi.tiangolo.com/)
[![SQLModel](https://img.shields.io/badge/SQLModel-ORM-blueviolet)](https://sqlmodel.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon_Serverless-316192)](https://neon.tech/)
[![Python](https://img.shields.io/badge/Python-3.13%2B-blue)](https://www.python.org/)

---

## Overview

The **Todo Manager Backend** is a high-performance RESTful API built with FastAPI and Python 3.13+. It provides authentication, task management, and data persistence with a cloud PostgreSQL database. The API follows modern best practices with async/await, type safety, and comprehensive validation.

### Key Features

- **FastAPI Framework** - High-performance async web framework
- **SQLModel ORM** - Type-safe database operations combining SQLAlchemy + Pydantic
- **JWT Authentication** - Secure token-based authentication
- **PostgreSQL Database** - Neon Serverless with asyncpg driver
- **Automatic API Docs** - Swagger UI and ReDoc auto-generated
- **Type Safety** - Full Python 3.13+ type hints
- **Pydantic Validation** - Request/response validation
- **CORS Support** - Configured for frontend integration
- **Database Migrations** - Alembic for schema management

---

## Quick Start

### Prerequisites

- **Python** 3.13 or higher
- **UV** Package Manager ([Installation Guide](https://docs.astral.sh/uv/))
- **PostgreSQL** Database (Neon Serverless recommended)

### Installation

1. **Install UV (if not already installed)**

   **Windows:**
   ```powershell
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

   **macOS/Linux:**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install dependencies:**
   ```bash
   cd backend
   uv sync
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and secrets
   ```

4. **Set up database:**
   - Create a Neon PostgreSQL database (or use local PostgreSQL)
   - Update `DATABASE_URL` in `.env`
   - Tables will be created automatically on first run

5. **Run the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

   Or using UV:
   ```bash
   uv run uvicorn app.main:app --reload
   ```

6. **Access API documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - OpenAPI JSON: http://localhost:8000/openapi.json

---

## Environment Variables

Required environment variables (see `.env.example`):

```bash
# Database - Neon Serverless PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# Example Neon URL:
# DATABASE_URL=postgresql+asyncpg://user:password@ep-cool-smoke-123456.us-east-2.aws.neon.tech/neondb?sslmode=require

# Authentication - Must match frontend Better Auth secret
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters

# CORS - Allowed frontend origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,https://yourfrontend.com

# Optional - Debug mode
DEBUG=false
```

### Environment File Template

Create `.env` file:

```bash
# .env.example

# Database - Neon Serverless PostgreSQL
DATABASE_URL=postgresql+asyncpg://username:password@hostname:5432/database

# Authentication - Must match frontend Better Auth secret
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters

# CORS - Allowed frontend origins (comma-separated)
CORS_ORIGINS=http://localhost:3000

# Debug mode (development only)
DEBUG=true
```

---

## API Endpoints

### Authentication Endpoints

All authentication endpoints are under `/api/auth`:

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/auth/signup` | Create new user account | No |
| `POST` | `/api/auth/login` | Login and get JWT token | No |
| `POST` | `/api/auth/logout` | Logout (client-side token removal) | No |
| `GET` | `/api/auth/session` | Get current user session | Yes |

### Task Endpoints (Authenticated)

All task endpoints require a valid JWT token in the `Authorization: Bearer <token>` header.

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/{user_id}/tasks` | List all user's tasks | Yes |
| `POST` | `/api/{user_id}/tasks` | Create new task | Yes |
| `GET` | `/api/{user_id}/tasks/{id}` | Get single task by ID | Yes |
| `PUT` | `/api/{user_id}/tasks/{id}` | Update task (full update) | Yes |
| `DELETE` | `/api/{user_id}/tasks/{id}` | Delete task | Yes |
| `PATCH` | `/api/{user_id}/tasks/{id}/complete` | Toggle completion status | Yes |

### Request/Response Examples

#### Create Task

**Request:**
```http
POST /api/user123/tasks HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for Phase II",
  "priority": "High",
  "tags": ["documentation", "urgent"]
}
```

**Response (201 Created):**
```json
{
  "id": "task-uuid-here",
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for Phase II",
  "completed": false,
  "priority": "High",
  "tags": ["documentation", "urgent"],
  "user_id": "user123",
  "created_at": "2026-01-07T12:00:00Z",
  "updated_at": "2026-01-07T12:00:00Z"
}
```

#### Get All Tasks

**Request:**
```http
GET /api/user123/tasks HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
[
  {
    "id": "task1",
    "title": "Task 1",
    "description": "Description 1",
    "completed": false,
    "priority": "High",
    "tags": ["work"],
    "user_id": "user123",
    "created_at": "2026-01-07T12:00:00Z",
    "updated_at": "2026-01-07T12:00:00Z"
  },
  {
    "id": "task2",
    "title": "Task 2",
    "description": "Description 2",
    "completed": true,
    "priority": "Medium",
    "tags": ["personal"],
    "user_id": "user123",
    "created_at": "2026-01-07T11:00:00Z",
    "updated_at": "2026-01-07T12:30:00Z"
  }
]
```

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Configuration settings
│   ├── database.py                # Database connection
│   ├── models.py                  # SQLModel database models
│   ├── schemas.py                 # Pydantic validation schemas
│   ├── auth.py                    # Authentication utilities
│   │
│   ├── routers/                   # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py               # Authentication endpoints
│   │   └── tasks.py              # Task CRUD endpoints
│   │
│   ├── dependencies/              # FastAPI dependencies
│   │   ├── __init__.py
│   │   ├── database.py           # Database session dependency
│   │   └── auth.py               # Auth dependencies
│   │
│   ├── middleware/                # Middleware components
│   │   ├── __init__.py
│   │   ├── auth.py               # JWT verification
│   │   └── cors.py               # CORS configuration
│   │
│   └── utils/                     # Utility functions
│       ├── __init__.py
│       ├── logging.py            # Logging setup
│       └── exceptions.py         # Custom exceptions
│
├── alembic/                       # Database migrations
│   ├── versions/                 # Migration files
│   ├── env.py                    # Alembic environment
│   └── script.py.mako            # Migration template
│
├── tests/                         # Backend tests
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── conftest.py               # Pytest configuration
│
├── .env                           # Environment variables (gitignored)
├── .env.example                   # Example environment file
├── alembic.ini                    # Alembic configuration
├── pyproject.toml                 # UV project configuration
├── requirements.txt               # Python dependencies
├── CLAUDE.md                      # Backend-specific guide
└── README.md                      # This file
```

---

## Development

### Running the Server

**Development Mode:**
```bash
# Using uvicorn directly
uvicorn app.main:app --reload --port 8000

# Using UV (recommended)
uv run uvicorn app.main:app --reload --port 8000

# With specific host
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production Mode:**
```bash
# Production server (no reload, optimized)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Using UV
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Running Tests

**Test Status:** ✅ **28/28 tests passing** (100%)

```bash
# Run all tests
uv run pytest

# Verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_auth.py

# Run tests with coverage
uv run pytest --cov=app --cov-report=html
```

**Test Suite Breakdown:**
- **Authentication Tests:** 10/10 passing ✅
  - User signup, login, password hashing
  - JWT token generation and validation
  - Timestamp creation

- **Task Management Tests:** 18/18 passing ✅
  - CRUD operations (Create, Read, Update, Delete)
  - Authentication and authorization
  - User isolation (users can only access their own tasks)
  - Input validation
  - Tag and recurrence support

**Example Output:**
```
============================= test session starts =============================
collected 28 items

tests/test_auth.py::test_signup_success PASSED                     [  3%]
tests/test_auth.py::test_signup_duplicate_email PASSED             [  7%]
...
tests/test_tasks.py::test_task_timestamps_updated PASSED          [100%]

============================= 28 passed in 12.66s =============================
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Add new column to tasks table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show migration history
alembic history

# Show current revision
alembic current
```

### Code Quality

```bash
# Type checking with mypy
uv run mypy app/

# Linting with ruff
uv run ruff check app/

# Format code with ruff
uv run ruff format app/

# Check for security issues
uv run bandit -r app/
```

---

## Database

### Database Schema

#### Users Table

```sql
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

#### Tasks Table

```sql
CREATE TABLE tasks (
    id VARCHAR PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(1000),
    completed BOOLEAN DEFAULT FALSE,
    priority VARCHAR(10) DEFAULT 'Medium',  -- High, Medium, Low
    tags TEXT DEFAULT '',                    -- Comma-separated
    recurrence_pattern VARCHAR(10),          -- Daily, Weekly, Monthly
    recurrence_interval INTEGER DEFAULT 1,
    due_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Ready',      -- Ready, In Progress, Review, Done
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_status ON tasks(status);
```

### Data Relationships

```
users (1) ──────< (many) tasks
  │                      │
  └─ One user has many tasks
                         └─ Each task belongs to one user
```

### Connection Pooling

The backend uses SQLAlchemy's async engine with connection pooling:

```python
engine = create_async_engine(
    DATABASE_URL,
    echo=DEBUG,
    pool_size=5,          # Default: 5 connections
    max_overflow=10,      # Allow up to 10 extra connections
    pool_pre_ping=True,   # Verify connections before using
)
```

---

## Authentication & Authorization

### JWT Token Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user-id-here",
    "email": "user@example.com",
    "exp": 1735689600
  },
  "signature": "..."
}
```

### Authorization Flow

1. User logs in with email/password
2. Backend verifies credentials against database
3. Backend generates JWT token signed with `BETTER_AUTH_SECRET`
4. Token sent to frontend in response
5. Frontend stores token in httpOnly cookie
6. All subsequent requests include `Authorization: Bearer <token>` header
7. Backend verifies token on each request
8. Backend extracts `user_id` from token's `sub` claim
9. Backend verifies `user_id` in URL matches token's `user_id`
10. Backend filters all database queries by `user_id`

### Security Rules

**CRITICAL:** Every API endpoint MUST:
1. ✅ Verify JWT token in `Authorization: Bearer <token>` header
2. ✅ Extract `user_id` from token payload (`sub` claim)
3. ✅ Compare token `user_id` with URL `user_id` parameter
4. ✅ Return `403 Forbidden` if mismatch
5. ✅ Filter all database queries by `user_id`

**Security Principle:** Users can ONLY access their own data.

---

## Code Quality Standards

### Python 3.13+ with Type Hints

All code must use full type hints:

```python
# ✅ GOOD - Full type hints
async def get_tasks(
    session: AsyncSession,
    user_id: str
) -> list[Task]:
    """Get all tasks for a user."""
    statement = select(Task).where(Task.user_id == user_id)
    result = await session.execute(statement)
    return result.scalars().all()

# ❌ BAD - No type hints
async def get_tasks(session, user_id):
    statement = select(Task).where(Task.user_id == user_id)
    result = await session.execute(statement)
    return result.scalars().all()
```

### Google-Style Docstrings

```python
def create_task(session: AsyncSession, task_data: TaskCreate, user_id: str) -> Task:
    """
    Create a new task for a user.

    Args:
        session: Database session
        task_data: Task data to create
        user_id: User ID who owns the task

    Returns:
        Task: Created task object

    Raises:
        HTTPException: 400 if validation fails

    Example:
        >>> task = await create_task(session, task_data, "user123")
        >>> print(task.id)
        "task-uuid-here"
    """
    ...
```

### Async/Await for All I/O

```python
# ✅ GOOD - Async I/O operations
async def get_task(session: AsyncSession, task_id: str) -> Task | None:
    statement = select(Task).where(Task.id == task_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()

# ❌ BAD - Blocking I/O
def get_task(session: Session, task_id: str) -> Task | None:
    return session.query(Task).filter(Task.id == task_id).first()
```

### No Print Statements - Use Logging

```python
import logging

logger = logging.getLogger(__name__)

# ✅ GOOD - Use logging
logger.info(f"Task created: {task.id}")
logger.error(f"Failed to create task: {error}")
logger.debug(f"Processing task data: {task_data}")

# ❌ BAD - Print statements
print(f"Task created: {task.id}")
```

---

## API Documentation

FastAPI automatically generates interactive API documentation:

### Swagger UI
- **URL:** http://localhost:8000/docs
- Interactive API testing
- Request/response examples
- Schema documentation

### ReDoc
- **URL:** http://localhost:8000/redoc
- Alternative documentation UI
- Better for reading/reference
- Export to PDF/HTML

### OpenAPI JSON
- **URL:** http://localhost:8000/openapi.json
- Raw OpenAPI 3.0 specification
- For API clients and code generation

---

## Security

### Password Security
- **Hashing:** bcrypt with automatic salt
- **Minimum Length:** 8 characters (configurable)
- **Storage:** Only hashed passwords stored in database
- **Verification:** Constant-time comparison

### JWT Security
- **Algorithm:** HS256 (HMAC with SHA-256)
- **Secret:** Minimum 32 characters, loaded from environment
- **Expiry:** 7 days (configurable)
- **Claims:** `sub` (user_id), `email`, `exp` (expiration)

### SQL Injection Prevention
- **ORM:** SQLModel with parameterized queries
- **No Raw SQL:** All queries use SQLModel/SQLAlchemy
- **Validation:** Pydantic schemas validate all inputs

### CORS Configuration
- **Allowed Origins:** Configured in environment variable
- **Credentials:** `allow_credentials=True` for cookies
- **Methods:** All HTTP methods allowed
- **Headers:** All headers allowed

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Use Case |
|------|---------|----------|
| `200` | OK | Successful GET, PUT, PATCH |
| `201` | Created | Successful POST (resource created) |
| `204` | No Content | Successful DELETE |
| `400` | Bad Request | Invalid input/validation error |
| `401` | Unauthorized | Missing or invalid token |
| `403` | Forbidden | User not allowed to access resource |
| `404` | Not Found | Resource doesn't exist |
| `500` | Internal Server Error | Unexpected server error |

### Error Response Format

```json
{
  "detail": "Error message here"
}
```

### Common Errors

**401 Unauthorized:**
```json
{
  "detail": "Invalid or missing token"
}
```

**403 Forbidden:**
```json
{
  "detail": "Forbidden: Cannot access other users' tasks"
}
```

**404 Not Found:**
```json
{
  "detail": "Task with ID task123 not found"
}
```

**400 Bad Request:**
```json
{
  "detail": "Validation error: title is required"
}
```

---

## Performance

### Async/Await Benefits
- Non-blocking I/O operations
- High concurrency with low overhead
- Efficient database connection usage
- Scalable to many concurrent users

### Database Optimization
- **Indexes:** On `user_id`, `email`, `completed`, `priority`, `status`
- **Connection Pooling:** Reuses database connections
- **Async Driver:** `asyncpg` for PostgreSQL (fastest Python driver)
- **Query Optimization:** Select only needed columns, use WHERE clauses

### Response Optimization
- **Pydantic Models:** Fast serialization/deserialization
- **Gzip Compression:** Automatic compression for large responses
- **Caching Headers:** ETags and Last-Modified for client-side caching

---

## Deployment

### Production Configuration

**Environment Variables:**
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@prod-host:5432/dbname
BETTER_AUTH_SECRET=production-secret-very-long-and-random
CORS_ORIGINS=https://yourdomain.com
DEBUG=false
```

**Server Configuration:**
```bash
# Use gunicorn with uvicorn workers for production
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Deployment Platforms

**Railway:**
- Automatic deployment from GitHub
- PostgreSQL addon available
- Environment variable management
- Automatic HTTPS

**Render:**
- Free tier available
- PostgreSQL database included
- Automatic deployments
- Custom domains

**AWS/GCP/Azure:**
- Full control over infrastructure
- Kubernetes deployment
- Load balancing
- Auto-scaling

---

## Troubleshooting

### Common Issues

**1. Database connection errors:**
```bash
# Check DATABASE_URL format
postgresql+asyncpg://user:password@host:5432/database

# For Neon PostgreSQL, remove ?sslmode=require from URL
# The application handles SSL automatically with ssl='require' parameter

# Ensure asyncpg driver is installed
uv add asyncpg
```

**Fixed Issue (January 2026):**
- **SSL Connection Error:** Fixed asyncpg `sslmode` parameter issue
- The database.py file now properly handles SSL connections
- Use `ssl='require'` in connect_args instead of URL parameter

**2. JWT token verification fails:**
```bash
# Ensure BETTER_AUTH_SECRET matches frontend
# Check token is included in Authorization header
# Verify token hasn't expired
```

**3. CORS errors:**
```bash
# Add frontend URL to CORS_ORIGINS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

**4. Import errors:**
```bash
# Sync dependencies
uv sync

# Check Python version (3.13+ required)
python --version
```

---

## Spec Reference

See project specifications:
- [`@../specs/overview.md`](../specs/overview.md) - Project overview
- [`@../specs/architecture.md`](../specs/architecture.md) - System architecture
- [`@../specs/api/`](../specs/api/) - API endpoint specifications
- [`@../specs/database/`](../specs/database/) - Database schema
- [`@../specs/features/`](../specs/features/) - Feature specifications

---

## Support

For issues and questions, refer to:
- [`@../CLAUDE.md`](../CLAUDE.md) - Main navigation guide
- [`@CLAUDE.md`](./CLAUDE.md) - Backend-specific guide
- API docs: http://localhost:8000/docs (when server is running)
- [GitHub Issues](https://github.com/Roofan-Jlove/Hackathon-II-TODO-APP/issues)

---

## License

Educational project for learning purposes.

---

<div align="center">

**Built with FastAPI, SQLModel, and UV**

**Python 3.13+ | PostgreSQL | JWT Authentication**

**Status:** Production Ready ✅ - 28/28 Tests Passing

**Last Updated:** January 10, 2026

[⬆ Back to Top](#todo-manager-backend---fastapi)

</div>
