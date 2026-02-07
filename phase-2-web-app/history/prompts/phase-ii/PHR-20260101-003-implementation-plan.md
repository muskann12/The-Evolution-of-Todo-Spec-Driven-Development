---
id: PHR-20260101-003
title: Phase II Implementation Plan
stage: plan
date: 2026-01-01T05:45:00Z
surface: claude-code-cli
model: claude-sonnet-4.5
feature: phase-ii
branch: main
user: kenneth
command: sp.plan
labels: [plan, implementation, architecture, authentication, phase-ii]
links:
  spec: speckit.specify
  plan: speckit.plan
  ticket: N/A
  adr: N/A
files:
  - path: phase-2-web-app/speckit.plan
    action: created
    lines: 1800+
tests:
  - N/A (Plan document - no code tests)
---

## Prompt

sp/plan for authentication implementation

Create a file called "speckit.plan" that defines HOW to build Phase II of the
todo application.

This file provides the technical architecture, component breakdown, and
implementation approach.

Include these sections:

1. SYSTEM ARCHITECTURE
2. COMPONENT BREAKDOWN
3. DATABASE MODELS
4. API ENDPOINTS
5. AUTHENTICATION FLOW
6. FRONTEND IMPLEMENTATION
7. BACKEND IMPLEMENTATION
8. DATABASE CONNECTION
9. DEPLOYMENT ARCHITECTURE
10. DEVELOPMENT WORKFLOW
11. SECURITY IMPLEMENTATION

## Response snapshot

Created comprehensive Phase II implementation plan (speckit.plan) defining HOW to build the full-stack application:

**12 Major Sections:**

1. **System Architecture**: Complete system diagram with data flow
   - Browser → Next.js Frontend → FastAPI Backend → Neon PostgreSQL
   - JWT authentication flow
   - Component interaction patterns

2. **Component Breakdown**: Detailed file structure
   - Frontend: 10+ components (Header, TaskList, TaskItem, TaskForm, LoginForm, SignupForm)
   - Backend: 8+ modules (main.py, models.py, schemas.py, db.py, routes/tasks.py, middleware/auth.py)
   - Library code: api.ts, auth.ts, types.ts

3. **Database Models**: SQLModel schemas with relationships
   - User model (Better Auth managed)
   - Task model with foreign key to users
   - Indexes for performance (user_id, completed, created_at)

4. **API Endpoints**: Complete implementation code for all 6 endpoints
   - GET /api/{user_id}/tasks (with filtering)
   - POST /api/{user_id}/tasks
   - GET /api/{user_id}/tasks/{id}
   - PUT /api/{user_id}/tasks/{id}
   - DELETE /api/{user_id}/tasks/{id}
   - PATCH /api/{user_id}/tasks/{id}/complete

5. **Authentication Flow**: JWT token lifecycle
   - Signup/Login → JWT generation → httpOnly cookie storage
   - Request flow → JWT verification → user_id extraction
   - Authorization check (token user_id vs URL user_id)

6. **Frontend Implementation**: Next.js patterns
   - Better Auth setup with JWT plugin
   - API client with automatic token injection
   - Server Components for SSR
   - Client Components for interactivity
   - TypeScript types for all data

7. **Backend Implementation**: FastAPI patterns
   - JWT verification middleware (verify_jwt dependency)
   - Database session management (get_db dependency)
   - Endpoint authorization checks
   - Error handling with proper status codes

8. **Database Connection**: Neon PostgreSQL setup
   - Connection string configuration
   - Async engine with connection pooling
   - Pool size: 10, max overflow: 20
   - Session management with commit/rollback

9. **Deployment Architecture**: Production deployment
   - Frontend: Vercel (auto-deploy from GitHub)
   - Backend: Railway/Render (auto-deploy from GitHub)
   - Database: Neon (serverless, already deployed)
   - Environment variables for each service

10. **Development Workflow**: Local setup instructions
    - Frontend: npm install → npm run dev (localhost:3000)
    - Backend: uv pip install → uvicorn --reload (localhost:8000)
    - Testing: pytest (backend 90%+), Jest (frontend 80%+)

11. **Security Implementation**: Defense in depth
    - CORS configuration (allow credentials for cookies)
    - Environment variables (BETTER_AUTH_SECRET shared)
    - User isolation enforcement (every endpoint)
    - Input validation (frontend + backend)

12. **Implementation Checklist**: 4-phase rollout
    - Phase 1: Backend Setup (10 tasks)
    - Phase 2: Frontend Setup (8 tasks)
    - Phase 3: Integration (6 tasks)
    - Phase 4: Production (6 tasks)

**Key Architecture Decisions:**

1. **JWT in httpOnly Cookies** (not localStorage)
   - Prevents XSS attacks
   - Automatic cookie sending
   - SameSite=Strict for CSRF protection

2. **User Isolation via Token user_id**
   - User ID extracted from JWT (never from client)
   - Authorization check on every endpoint
   - Database queries filtered by user_id

3. **Async/Await Throughout**
   - FastAPI async endpoints
   - SQLModel async queries
   - Next.js Server Components (async)

4. **Connection Pooling**
   - Pool size: 10 connections
   - Max overflow: 20 connections
   - Pool timeout: 30 seconds

5. **Serverless Database**
   - Neon PostgreSQL (auto-scaling)
   - No manual infrastructure management
   - Built-in connection pooling

**Technology Stack Summary:**
- Frontend: Next.js 16+, TypeScript, Tailwind CSS, Better Auth
- Backend: FastAPI, SQLModel, Pydantic, asyncpg
- Database: Neon Serverless PostgreSQL
- Deployment: Vercel (frontend), Railway (backend), Neon (database)

**Code Patterns Provided:**
- 6 complete endpoint implementations with authorization
- JWT verification middleware
- Database session management
- API client with error handling
- React component patterns (Server + Client)
- Better Auth configuration
- CORS configuration
- Environment variable setup

## Outcome

- ✅ Impact: Created detailed implementation guide for Phase II development. Provides complete code patterns, architecture diagrams, and deployment instructions.
- 🧪 Tests: Testing strategy defined (pytest 90%+, Jest 80%+, integration tests, E2E tests)
- 📁 Files: 1 file created (speckit.plan, 1800+ lines)
- 🔁 Next prompts:
  - Create task breakdown (sp.tasks) - Step-by-step implementation tasks
  - Begin backend implementation following plan
  - Set up Neon database and get connection string
- 🧠 Reflection: Plan is comprehensive and actionable. All code patterns provided with complete implementations. Security enforced at multiple layers. Architecture follows constitution principles (separation of concerns, security first). Ready for task breakdown and implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None - plan creation successful
- Graders run and results (PASS/FAIL): N/A (manual review required)
- Prompt variant (if applicable): N/A (initial plan)
- Next experiment (smallest change to try): Validate plan against specification to ensure all requirements are addressed (8 features, 6 endpoints, 3 user journeys)
