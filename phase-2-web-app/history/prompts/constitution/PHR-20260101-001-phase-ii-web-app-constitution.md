---
id: PHR-20260101-001
title: Phase II Web App Constitution
stage: constitution
date: 2026-01-01T04:58:00Z
surface: claude-code-cli
model: claude-sonnet-4.5
feature: phase-ii-constitution
branch: main
user: kenneth
command: sp.constitution
labels: [constitution, phase-ii, architecture, principles]
links:
  spec: speckit.constitution
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - path: phase-2-web-app/speckit.constitution
    action: created
    lines: 1200+
tests:
  - N/A (Constitution document - no tests required)
---

## Prompt

Create a file called "speckit.constitution" in the project root that defines the
architectural principles, constraints, and quality standards for Phase II of the
todo application.

This is a Next.js 16+ frontend with FastAPI backend, SQLModel ORM, and Neon
PostgreSQL database.

Include these sections:

1. PROJECT OVERVIEW
- Multi-user web-based todo application
- Phase II: Full-Stack Web Application
- Authentication with Better Auth and JWT tokens
- Persistent storage with Neon PostgreSQL

2. ARCHITECTURAL PRINCIPLES

Separation of Concerns:
- Frontend (Next.js) handles UI and user interactions only
- Backend (FastAPI) handles business logic and data operations
- Database (Neon) stores persistent data
- Authentication (Better Auth + JWT) handles security

Monorepo Organization:
- Single repository with frontend/ and backend/ folders
- Shared specifications in specs/ folder
- Environment-specific configurations

Security First:
- All API endpoints require JWT authentication
- User data isolation (users only see their own tasks)
- Secure password hashing (Better Auth handles this)
- HttpOnly cookies for token storage (NOT localStorage)
- CORS properly configured

Spec-Driven Development:
- NO manual coding allowed
- All features start with specification
- Workflow: Specify → Plan → Tasks → Implement
- Every code change maps to a task
- Use SpecKit Plus for all development

3. TECHNOLOGY STACK

Frontend:
- Next.js 16+ (App Router)
- TypeScript (strict mode)
- Tailwind CSS
- Better Auth with JWT plugin

Backend:
- Python 3.13+
- FastAPI with async/await
- SQLModel ORM
- Pydantic validation
- asyncpg for PostgreSQL

Database:
- Neon Serverless PostgreSQL

Development Tools:
- UV for Python package management
- Claude Code for implementation
- SpecKit Plus for specifications

4. CODING STANDARDS

Frontend (TypeScript):
- Use TypeScript strict mode
- ESLint configuration enforced
- Prettier for code formatting
- Server components by default
- Client components only when needed ('use client')
- All API calls through /lib/api.ts
- Tailwind CSS only (no inline styles)

Backend (Python):
- Python 3.13+ features
- Full type hints (mypy --strict)
- Google-style docstrings
- Async/await for all I/O operations
- Pydantic models for validation
- Custom exceptions for errors
- No print statements (use logging)

API Design:
- RESTful conventions
- Consistent error responses: {"detail": "Error message"}
- HTTP status codes used correctly (200, 201, 400, 401, 403, 404)
- Request/response validation with Pydantic
- OpenAPI documentation auto-generated

5. DATA MODEL STANDARDS

User Model (Better Auth managed):
- id: UUID string (primary key)
- email: unique, validated
- name: string
- created_at: timestamp

Task Model:
- id: auto-increment integer (primary key)
- user_id: foreign key to users (NOT NULL)
- title: required, max 200 characters
- description: optional, max 1000 characters
- completed: boolean, default false
- created_at: auto-timestamp
- updated_at: auto-timestamp

Relationships:
- One user has many tasks (one-to-many)
- Tasks cannot exist without user
- Cascade delete on user deletion

6. QUALITY GATES

Backend:
- 90%+ test coverage (pytest)
- All tests passing
- mypy --strict passing
- ruff linting passing
- No security vulnerabilities

Frontend:
- 80%+ component test coverage (Jest)
- All tests passing
- ESLint passing
- TypeScript strict mode
- No console errors in production

Integration:
- All API endpoints tested
- Authentication flow tested end-to-end
- Full user journey tested (signup → login → CRUD)

7. ERROR HANDLING POLICY

Frontend:
- User-friendly error messages
- Loading states for async operations
- Form validation with clear feedback
- Graceful handling of API errors
- Logout on 401 Unauthorized

Backend:
- Custom exception classes
- Consistent error response format
- Detailed logging (not exposed to client)
- Proper HTTP status codes
- Validation errors with field details

8. SECURITY GUIDELINES

Authentication:
- JWT tokens with 7-day expiry
- Shared BETTER_AUTH_SECRET between frontend/backend
- HttpOnly cookies (NOT localStorage)
- Automatic token refresh
- Logout clears all client state

Authorization:
- Every endpoint verifies JWT token
- User ID extracted from token
- URL user_id must match token user_id
- Users can only access their own data
- Return 403 Forbidden if user_id mismatch

Input Validation:
- All inputs validated on backend
- SQL injection prevention (SQLModel ORM handles this)
- XSS prevention (React auto-escaping)
- CSRF protection via SameSite cookies

9. PERFORMANCE REQUIREMENTS

Frontend:
- First Contentful Paint < 1.5s
- Time to Interactive < 3s
- Lighthouse score > 90

Backend:
- API response time < 200ms (95th percentile)
- Database queries optimized with indexes
- Connection pooling enabled

Database:
- Indexes on: user_id, completed, created_at
- Query optimization for list endpoints
- Efficient filtering and sorting

10. API ENDPOINTS (Required)
All 6 endpoints must be implemented:
- GET    /api/{user_id}/tasks - List user's tasks
- POST   /api/{user_id}/tasks - Create task
- GET    /api/{user_id}/tasks/{id} - Get single task
- PUT    /api/{user_id}/tasks/{id} - Update task
- DELETE /api/{user_id}/tasks/{id} - Delete task
- PATCH  /api/{user_id}/tasks/{id}/complete - Toggle completion

## Response snapshot

Created comprehensive Phase II constitution document (speckit.constitution) with 12 major sections:

1. **Project Overview**: Defined multi-user web application with Next.js 16+, FastAPI, SQLModel, and Neon PostgreSQL
2. **Architectural Principles**: Established separation of concerns, monorepo organization, security-first approach, and spec-driven development
3. **Technology Stack**: Detailed frontend (Next.js, TypeScript, Tailwind), backend (FastAPI, SQLModel, Pydantic), and database (Neon) technologies
4. **Coding Standards**: Set strict TypeScript and Python standards, API design conventions
5. **Data Model Standards**: Defined User and Task models with relationships and constraints
6. **Quality Gates**: Established 90% backend and 80% frontend test coverage requirements
7. **Error Handling Policy**: Created consistent error handling for frontend and backend
8. **Security Guidelines**: Implemented JWT authentication, authorization, and input validation policies
9. **Performance Requirements**: Set response time, Lighthouse score, and database optimization targets
10. **API Endpoints**: Specified all 6 required RESTful endpoints with full documentation
11. **Development Workflow**: Integrated SpecKit Plus workflow (Specify → Plan → Tasks → Implement)
12. **Deployment**: Defined environment variables, production checklist, and governance

**Key Decisions:**
- HttpOnly cookies for JWT storage (not localStorage) to prevent XSS attacks
- User ID from token only (never from client) for authorization
- Cascade delete on user removal
- Async/await for all backend I/O operations
- Server components by default in Next.js
- 7-day JWT token expiry
- Strict type checking (TypeScript strict mode, mypy --strict)

## Outcome

- ✅ Impact: Created foundational governance document for Phase II development. Defines all architectural principles, technology choices, coding standards, and quality requirements.
- 🧪 Tests: N/A (Constitution document - no code tests required)
- 📁 Files: 1 file created (speckit.constitution, 1200+ lines)
- 🔁 Next prompts:
  - Create authentication feature specification (sp.specify)
  - Create implementation plan for authentication (sp.plan)
  - Begin backend setup with constitution compliance
- 🧠 Reflection: Constitution establishes security-first architecture with clear separation of concerns. Spec-driven development workflow enforced. All 6 API endpoints documented with authorization requirements. Quality gates ensure maintainability.

## Evaluation notes (flywheel)

- Failure modes observed: None - constitution creation successful
- Graders run and results (PASS/FAIL): N/A (manual review required)
- Prompt variant (if applicable): N/A (initial constitution)
- Next experiment (smallest change to try): Validate constitution against existing Phase II specifications in specs/ folder for consistency
