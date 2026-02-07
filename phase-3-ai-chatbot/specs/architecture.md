# System Architecture - Phase II Web Application

**Project:** Todo Manager - Full-Stack Web Application
**Document:** System Architecture (HOW - Structure)
**Last Updated:** 2025-12-31

---

## 1. Architecture Overview

### System Design Philosophy

This application follows a **three-tier architecture**:
1. **Presentation Layer** - Next.js Frontend (UI/UX)
2. **Application Layer** - FastAPI Backend (Business Logic & API)
3. **Data Layer** - PostgreSQL Database (Data Persistence)

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         CLIENT BROWSER                            │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              Next.js Frontend (Port 3000)                   │  │
│  │                                                              │  │
│  │  ├─ App Router (pages, layouts, routing)                   │  │
│  │  ├─ React Components (UI)                                  │  │
│  │  ├─ Better Auth Client (authentication)                    │  │
│  │  ├─ API Client (backend communication)                     │  │
│  │  └─ Tailwind CSS (styling)                                 │  │
│  └────────────────────────────────────────────────────────────┘  │
│                              ↕ HTTPS                              │
└──────────────────────────────────────────────────────────────────┘
                               ↕
┌──────────────────────────────────────────────────────────────────┐
│                      API SERVER (Backend)                         │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              FastAPI Backend (Port 8000)                    │  │
│  │                                                              │  │
│  │  ├─ API Routers (endpoints)                                │  │
│  │  ├─ Auth Middleware (JWT verification)                     │  │
│  │  ├─ Pydantic Schemas (validation)                          │  │
│  │  ├─ SQLModel ORM (database abstraction)                    │  │
│  │  └─ Business Logic (task operations)                       │  │
│  └────────────────────────────────────────────────────────────┘  │
│                           ↕ SQL (asyncpg)                         │
└──────────────────────────────────────────────────────────────────┘
                               ↕
┌──────────────────────────────────────────────────────────────────┐
│                      DATABASE (Neon Cloud)                        │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │            PostgreSQL Database (Serverless)                 │  │
│  │                                                              │  │
│  │  ├─ users table (authentication)                           │  │
│  │  ├─ tasks table (todo items)                               │  │
│  │  ├─ Indexes (performance)                                  │  │
│  │  └─ Constraints (data integrity)                           │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Architecture

### 2.1 Frontend Architecture (Next.js)

#### Component Hierarchy

```
app/ (App Router)
├── layout.tsx                    # Root layout (global)
├── page.tsx                      # Home/landing page
│
├── (auth)/                       # Auth route group
│   ├── login/page.tsx           # Login page
│   └── signup/page.tsx          # Signup page
│
└── (dashboard)/                  # Protected route group
    ├── layout.tsx               # Dashboard layout
    ├── tasks/
    │   ├── page.tsx            # Task list page
    │   ├── [id]/page.tsx       # Task detail page
    │   └── new/page.tsx        # Create task page
    └── profile/page.tsx        # User profile

components/
├── ui/                          # Generic UI components
│   ├── Button.tsx
│   ├── Input.tsx
│   ├── Card.tsx
│   └── Modal.tsx
│
├── features/                    # Feature-specific components
│   ├── tasks/
│   │   ├── TaskList.tsx        # Server component
│   │   ├── TaskItem.tsx        # Client component
│   │   ├── TaskForm.tsx        # Client component
│   │   └── TaskFilters.tsx     # Client component
│   └── auth/
│       ├── LoginForm.tsx       # Client component
│       └── SignupForm.tsx      # Client component
│
└── layout/                      # Layout components
    ├── Header.tsx              # Client component
    ├── Sidebar.tsx             # Client component
    └── Footer.tsx              # Server component

lib/
├── api.ts                       # API client (backend communication)
├── auth.ts                      # Better Auth configuration
├── types.ts                     # TypeScript types
├── validation.ts                # Zod schemas
└── utils.ts                     # Helper functions
```

#### Data Flow (Frontend)

```
User Action → Component Event Handler → API Client → Backend API
                                                            ↓
User sees result ← Component Re-render ← State Update ← API Response
```

### 2.2 Backend Architecture (FastAPI)

#### Module Organization

```
app/
├── main.py                      # FastAPI app entry point
├── config.py                    # Configuration settings
├── database.py                  # Database connection
├── models.py                    # SQLModel database models
├── schemas.py                   # Pydantic request/response schemas
│
├── routers/                     # API route handlers
│   ├── __init__.py
│   ├── tasks.py                # Task CRUD endpoints
│   └── auth.py                 # Authentication endpoints
│
├── middleware/                  # Middleware components
│   ├── __init__.py
│   ├── auth.py                 # JWT verification
│   └── cors.py                 # CORS configuration
│
├── dependencies/                # FastAPI dependencies
│   ├── __init__.py
│   ├── database.py             # DB session dependency
│   └── auth.py                 # Auth dependencies
│
└── utils/                       # Utility functions
    ├── __init__.py
    ├── logging.py              # Logging setup
    └── exceptions.py           # Custom exceptions
```

#### Request Flow (Backend)

```
HTTP Request → FastAPI Router → Middleware (CORS, Auth)
                                        ↓
                            Dependency Injection (DB Session, User ID)
                                        ↓
                            Route Handler Function
                                        ↓
                            Pydantic Validation
                                        ↓
                            Business Logic
                                        ↓
                            SQLModel ORM Query
                                        ↓
                            Database Operation
                                        ↓
HTTP Response ← JSON Serialization ← Pydantic Schema ← Database Result
```

### 2.3 Database Architecture (PostgreSQL)

#### Database Schema

```sql
-- Users table
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- Tasks table
CREATE TABLE tasks (
    id VARCHAR PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(1000),
    completed BOOLEAN DEFAULT FALSE,
    priority VARCHAR(10) DEFAULT 'Medium',  -- High, Medium, Low
    tags TEXT DEFAULT '',                    -- Comma-separated
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_priority ON tasks(priority);
```

#### Data Relationships

```
users (1) ──────< (many) tasks
  │                      │
  └─ One user has many tasks
                         └─ Each task belongs to one user
```

---

## 3. Authentication & Authorization

### Authentication Flow

```
┌─────────────┐                 ┌─────────────┐                 ┌─────────────┐
│   Frontend  │                 │   Backend   │                 │  Database   │
└──────┬──────┘                 └──────┬──────┘                 └──────┬──────┘
       │                                │                                │
       │ 1. POST /api/auth/signup      │                                │
       │  { email, password, name }     │                                │
       ├───────────────────────────────>│                                │
       │                                │ 2. Hash password               │
       │                                ├──────────────┐                 │
       │                                │<─────────────┘                 │
       │                                │ 3. INSERT user                 │
       │                                ├───────────────────────────────>│
       │                                │                                │
       │                                │<───────────────────────────────┤
       │ 4. { user, token }            │ 4. Create JWT token            │
       │<───────────────────────────────┤                                │
       │ 5. Store token in cookie      │                                │
       ├──────────────┐                 │                                │
       │<─────────────┘                 │                                │
       │                                │                                │
       │ 6. GET /api/{user_id}/tasks   │                                │
       │    Authorization: Bearer <JWT> │                                │
       ├───────────────────────────────>│                                │
       │                                │ 7. Verify JWT                  │
       │                                ├──────────────┐                 │
       │                                │<─────────────┘                 │
       │                                │ 8. Extract user_id             │
       │                                │ 9. Query tasks WHERE user_id   │
       │                                ├───────────────────────────────>│
       │                                │<───────────────────────────────┤
       │ 10. { tasks }                 │                                │
       │<───────────────────────────────┤                                │
       │                                │                                │
```

### Authorization Rules

**CRITICAL:** Every API endpoint MUST:
1. ✅ Verify JWT token in `Authorization: Bearer <token>` header
2. ✅ Extract `user_id` from token payload (`sub` claim)
3. ✅ Compare token `user_id` with URL `user_id` parameter
4. ✅ Return `403 Forbidden` if mismatch
5. ✅ Filter all database queries by `user_id`

**Security Principle:** Users can ONLY access their own data.

---

## 4. API Design

### API Conventions

#### Base URL
```
Development:  http://localhost:8000
Production:   https://api.yourdomain.com
```

#### URL Structure
```
/api/{user_id}/tasks           # User's task collection
/api/{user_id}/tasks/{id}      # Specific task
/api/auth/*                     # Authentication endpoints
```

#### HTTP Methods
- `GET` - Retrieve resource(s)
- `POST` - Create new resource
- `PUT` - Update entire resource
- `PATCH` - Partial update
- `DELETE` - Remove resource

### API Endpoints

#### Authentication Endpoints

```
POST   /api/auth/signup        # Create new user account
POST   /api/auth/login         # Login and get JWT token
POST   /api/auth/logout        # Logout (clear session)
GET    /api/auth/session       # Get current user session
```

#### Task Endpoints (Authenticated)

```
GET    /api/{user_id}/tasks              # List all user's tasks
POST   /api/{user_id}/tasks              # Create new task
GET    /api/{user_id}/tasks/{id}         # Get single task
PUT    /api/{user_id}/tasks/{id}         # Update task
DELETE /api/{user_id}/tasks/{id}         # Delete task
PATCH  /api/{user_id}/tasks/{id}/complete # Toggle completion
```

### Request/Response Format

#### Example: Create Task

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
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": "task-uuid-here",
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for Phase II",
  "completed": false,
  "priority": "High",
  "tags": ["documentation", "urgent"],
  "user_id": "user123",
  "created_at": "2025-12-31T12:00:00Z",
  "updated_at": "2025-12-31T12:00:00Z"
}
```

---

## 5. Data Flow Patterns

### 5.1 Create Task Flow

```
┌──────────────────────────────────────────────────────────────────┐
│ 1. User fills out TaskForm and clicks "Create"                   │
└──────────────────────────┬───────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────────┐
│ 2. Frontend validates with Zod schema                            │
│    - Title: 1-200 chars                                          │
│    - Description: max 1000 chars                                 │
│    - Priority: High/Medium/Low                                   │
└──────────────────────────┬───────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────────┐
│ 3. API Client sends POST /api/{user_id}/tasks                   │
│    - Includes JWT token from cookie                              │
│    - Sends JSON payload                                          │
└──────────────────────────┬───────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────────┐
│ 4. Backend verifies JWT token                                    │
│    - Decodes token with BETTER_AUTH_SECRET                       │
│    - Extracts user_id from 'sub' claim                          │
│    - Verifies user_id matches URL parameter                      │
└──────────────────────────┬───────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────────┐
│ 5. Backend validates with Pydantic schema                        │
│    - TaskCreate model validation                                 │
│    - Field constraints checked                                   │
└──────────────────────────┬───────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────────┐
│ 6. Backend creates Task object with SQLModel                     │
│    - Generates UUID for task ID                                  │
│    - Sets user_id, timestamps                                    │
│    - Adds to database session                                    │
└──────────────────────────┬───────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────────┐
│ 7. Database INSERT operation                                     │
│    - Transaction committed                                       │
│    - Task persisted                                              │
└──────────────────────────┬───────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────────┐
│ 8. Backend returns 201 Created with task data                    │
│    - TaskResponse Pydantic model                                 │
│    - JSON serialization                                          │
└──────────────────────────┬───────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────────┐
│ 9. Frontend receives response                                    │
│    - Updates local state                                         │
│    - Shows success message                                       │
│    - Redirects to task list                                      │
└──────────────────────────────────────────────────────────────────┘
```

### 5.2 List Tasks Flow

```
User visits /tasks page
        ↓
Next.js Server Component fetches data
        ↓
API Client: GET /api/{user_id}/tasks (with JWT)
        ↓
Backend verifies JWT and user_id
        ↓
Database: SELECT * FROM tasks WHERE user_id = ?
        ↓
Backend returns array of TaskResponse
        ↓
Frontend renders TaskList component
        ↓
User sees their tasks
```

---

## 6. Security Architecture

### 6.1 Authentication Security

**JWT Token Structure:**
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

**Token Storage:**
- Frontend: httpOnly cookies (prevents XSS attacks)
- Backend: Verified on every request
- Expiry: 7 days (configurable)

### 6.2 Authorization Security

**Every API Endpoint:**
```python
@router.get("/api/{user_id}/tasks")
async def get_tasks(
    user_id: str,  # From URL
    current_user_id: str = Depends(get_current_user_id),  # From JWT
    session: AsyncSession = Depends(get_session),
):
    # CRITICAL: Verify user_id matches token
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # CRITICAL: Filter by user_id
    statement = select(Task).where(Task.user_id == user_id)
    ...
```

### 6.3 Data Security

**Principles:**
- ✅ All passwords hashed with bcrypt
- ✅ SQL injection prevented by ORM (SQLModel)
- ✅ XSS prevented by httpOnly cookies
- ✅ CSRF protection via SameSite cookies
- ✅ CORS restricted to frontend origin
- ✅ Input validation on frontend AND backend

---

## 7. Performance & Scalability

### 7.1 Frontend Performance

**Optimizations:**
- Server components for static content
- Client components only when needed
- Code splitting (Next.js automatic)
- Image optimization (next/image)
- Lazy loading for heavy components

### 7.2 Backend Performance

**Optimizations:**
- Async/await for all I/O operations
- Database connection pooling
- Indexed database queries
- Efficient SQLModel queries
- Response caching (future)

### 7.3 Database Performance

**Optimizations:**
- Indexes on user_id, email
- Foreign key constraints
- Serverless auto-scaling (Neon)
- Connection pooling (asyncpg)

---

## 8. Error Handling

### 8.1 Frontend Errors

```typescript
try {
  const task = await api.createTask(data)
  // Success handling
} catch (error) {
  if (error.status === 401) {
    // Redirect to login
  } else if (error.status === 403) {
    // Show permission error
  } else {
    // Show generic error
  }
}
```

### 8.2 Backend Errors

```python
# 400 Bad Request
if invalid_input:
    raise HTTPException(status_code=400, detail="Invalid data")

# 401 Unauthorized
if not token_valid:
    raise HTTPException(status_code=401, detail="Unauthorized")

# 403 Forbidden
if user_id != current_user_id:
    raise HTTPException(status_code=403, detail="Forbidden")

# 404 Not Found
if not task:
    raise HTTPException(status_code=404, detail="Task not found")
```

---

## 9. Deployment Architecture

### 9.1 Development Environment

```
Frontend:  http://localhost:3000   (npm run dev)
Backend:   http://localhost:8000   (uvicorn --reload)
Database:  Neon Cloud (development branch)
```

### 9.2 Production Environment

```
Frontend:  Vercel (auto-deploy from main branch)
Backend:   Cloud provider (Railway, Render, AWS)
Database:  Neon Cloud (production branch)
```

---

## 10. Technology Decisions

### Why This Architecture?

**Three-Tier Benefits:**
- Clear separation of concerns
- Independent scaling
- Easy to test and maintain
- Technology flexibility

**RESTful API Benefits:**
- Standard HTTP methods
- Stateless communication
- Cacheable responses
- Well-understood patterns

**Async Architecture Benefits:**
- High concurrency
- Better performance
- Non-blocking I/O
- Scalable to many users

---

## 11. Future Enhancements

### Planned Improvements

1. **Caching Layer**
   - Redis for session storage
   - API response caching

2. **Real-time Updates**
   - WebSocket connections
   - Live task updates

3. **Microservices**
   - Separate auth service
   - Notification service

4. **CDN Integration**
   - Static asset delivery
   - Global distribution

---

## References

- `@specs/overview.md` - Project overview
- `@specs/api/` - API specifications
- `@specs/database/` - Database schemas
- `@specs/ui/` - UI specifications
- `@CLAUDE.md` - Main navigation
- `@AGENTS.md` - Agent rules

---

**Document Type:** Architecture Specification
**Lifecycle Stage:** Plan (HOW)
**Status:** Complete
**Last Updated:** 2025-12-31
