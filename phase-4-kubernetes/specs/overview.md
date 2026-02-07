# Project Overview - Phase II Web Application

**Project:** Todo Manager - Full-Stack Web Application
**Phase:** Phase II - Web Application Development
**Status:** 🚀 MVP Complete - Ready for Testing
**Last Updated:** 2026-01-07

---

## 1. Project Vision

### What We're Building
A modern, full-featured todo management web application that allows users to create, organize, and manage their tasks with authentication, persistence, and a beautiful user interface.

### Why This Project
This is Phase II of our todo application evolution:
- **Phase I:** CLI application with in-memory storage (✅ Complete)
- **Phase II:** Full-stack web application with database persistence (✅ Complete)
- **Future Phases:** Mobile apps, real-time collaboration, advanced features

### Target Users
- Individuals who need to manage personal tasks
- Users who want a simple, fast, and reliable todo app
- People who value data persistence and security

---

## 2. Project Goals

### Primary Goals
1. **User Authentication** - Secure signup/login with Better Auth
2. **Task Management** - Full CRUD operations for todos
3. **Data Persistence** - Cloud database storage with Neon PostgreSQL
4. **Modern UI** - Responsive Next.js frontend with Tailwind CSS
5. **API Backend** - RESTful FastAPI server with proper authentication

### Success Criteria
- [x] Users can create accounts and log in securely
- [x] Users can create, read, update, and delete tasks
- [x] Tasks persist across sessions (stored in database)
- [x] Each user can only access their own tasks
- [x] Responsive UI works on desktop and mobile
- [x] API follows RESTful conventions
- [x] All endpoints require authentication
- [x] Tests cover critical functionality

---

## 3. Tech Stack

### Frontend
- **Framework:** Next.js 16+ (App Router)
- **Language:** TypeScript (strict mode)
- **Styling:** Tailwind CSS
- **Authentication:** Better Auth (client-side)
- **Data Fetching:** React Query
- **Validation:** Zod schemas

### Backend
- **Framework:** FastAPI (Python 3.13+)
- **ORM:** SQLModel
- **Database:** Neon Serverless PostgreSQL
- **Authentication:** PyJWT (JWT token verification)
- **Validation:** Pydantic models
- **Migrations:** Alembic

### Development Tools
- **Package Manager:** npm (frontend), UV (backend)
- **Spec Framework:** SpecKit Plus
- **AI Assistant:** Claude Code
- **Version Control:** Git

---

## 4. High-Level Features

### Core Features (MVP)
1. **User Authentication**
   - Email/password signup
   - Login with JWT tokens
   - Logout functionality
   - Protected routes

2. **Task Management**
   - Create new tasks
   - View all user's tasks
   - Update task details
   - Delete tasks
   - Mark tasks as complete/incomplete

3. **Task Properties**
   - Title (required, 1-200 chars)
   - Description (optional, max 1000 chars)
   - Completion status (boolean)
   - Priority (High, Medium, Low)
   - Tags (comma-separated list)
   - Recurring tasks (Daily, Weekly, Monthly)
   - Due dates (ISO 8601 datetime)
   - Timestamps (created_at, updated_at)

4. **Kanban Board View**
   - Drag-and-drop task management
   - Status columns (Ready, In Progress, Review, Done)
   - Visual task organization
   - Status update on drop

5. **Task Search & Filtering**
   - Real-time search across tasks
   - Filter by priority, tags, status
   - Search by title and description

6. **Task Sorting**
   - Sort by date (newest/oldest)
   - Sort by priority (high/low)
   - Sort by title (A-Z, Z-A)
   - Sort by completion status

### Future Enhancements (Post-MVP)
- Advanced filtering (date ranges, multiple criteria)
- Task categories/projects
- Collaboration features
- Mobile applications
- Task templates
- Bulk operations

---

## 5. Architecture Overview

### System Components

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│  Next.js        │ ←──────→│  FastAPI        │ ←──────→│  PostgreSQL     │
│  Frontend       │  HTTPS  │  Backend        │   SQL   │  Database       │
│  (Port 3000)    │         │  (Port 8000)    │         │  (Neon Cloud)   │
│                 │         │                 │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
       │                           │                           │
       │                           │                           │
   TypeScript                  Python 3.13+               PostgreSQL 14+
   Tailwind CSS                 SQLModel                  Async Driver
   Better Auth                  PyJWT                     Connection Pool
```

### Data Flow

1. **User Authentication:**
   - User submits email/password → Frontend
   - Frontend sends to `/api/auth/login` → Backend
   - Backend verifies credentials → Database
   - Backend returns JWT token → Frontend
   - Frontend stores token in httpOnly cookie

2. **Task Operations:**
   - User performs action → Frontend
   - Frontend sends authenticated request → Backend
   - Backend verifies JWT token
   - Backend queries/updates database
   - Backend returns response → Frontend
   - Frontend updates UI

---

## 6. Development Approach

### Spec-Driven Development
This project follows **strict spec-driven development**:
- ✅ Specifications written BEFORE code
- ✅ All code references Task IDs and specs
- ✅ No improvisation or feature invention
- ✅ Acceptance criteria define success

See: `@AGENTS.md` for agent behavior rules

### Development Workflow

```
1. Constitution (WHY)     → Principles defined in .specify/memory/constitution.md
2. Specify (WHAT)         → Feature specs in specs/features/
3. Plan (HOW)             → Architecture in specs/architecture.md
4. Tasks (BREAKDOWN)      → Task lists in spec files
5. Implement (CODE)       → Backend + Frontend implementation
```

### Quality Standards
- All code has type hints (Python) or types (TypeScript)
- All API endpoints require authentication
- All database queries filter by user_id
- All forms have validation
- All features have tests
- No security vulnerabilities

---

## 7. Project Structure

```
phase-2-web-app/
├── .spec-kit/              # SpecKit Plus configuration
├── specs/                  # All specifications
│   ├── overview.md         # This file
│   ├── architecture.md     # System architecture
│   ├── features/           # Feature specifications
│   ├── api/                # API specifications
│   ├── database/           # Database schemas
│   └── ui/                 # UI specifications
├── frontend/               # Next.js application
├── backend/                # FastAPI application
├── .claude/                # Claude Code configuration
├── .specify/               # SpecKit Plus framework
└── CLAUDE.md              # Main navigation guide
```

---

## 8. Getting Started

### For Developers
1. Read `@CLAUDE.md` - Main navigation guide
2. Read `@AGENTS.md` - Agent behavior rules
3. Read `@specs/architecture.md` - System architecture
4. Read feature specs in `@specs/features/`
5. Follow the spec-driven workflow

### For AI Agents
1. **NEVER** write code without reading specs first
2. **ALWAYS** reference Task IDs in code
3. **STOP** if specifications are missing or unclear
4. **ASK** for clarification when requirements are ambiguous
5. **FOLLOW** the lifecycle: Constitution → Specify → Plan → Tasks → Implement

---

## 9. Project Timeline

### Phase II Milestones

**Milestone 1: Specifications** ✅ Complete (Dec 30, 2025)
- [x] Write all feature specifications
- [x] Define API contracts
- [x] Design database schema
- [x] Plan UI components

**Milestone 2: Backend Foundation** ✅ Complete (Jan 1, 2026)
- [x] Setup FastAPI project structure
- [x] Implement database models
- [x] Create authentication system
- [x] Build CRUD API endpoints

**Milestone 3: Frontend Foundation** ✅ Complete (Jan 2, 2026)
- [x] Setup Next.js project structure
- [x] Implement authentication UI
- [x] Create core components
- [x] Build API client

**Milestone 4: Feature Implementation** ✅ Complete (Jan 6, 2026)
- [x] Task priorities system
- [x] Task tags system
- [x] Recurring tasks feature
- [x] Due dates functionality
- [x] Kanban board view
- [x] Search and sorting

**Milestone 5: Testing & Polish** 🚧 In Progress (Jan 7, 2026)
- [x] Connect frontend to backend
- [x] End-to-end testing
- [ ] Comprehensive bug fixes
- [ ] Documentation completion
- [ ] Performance optimization

**Milestone 6: Deployment** ⏳ Planned
- [ ] Deploy backend to cloud
- [ ] Deploy frontend to Vercel
- [ ] Configure production database
- [ ] Final testing and launch

---

## 10. Key Decisions

### Why Next.js 16+ (App Router)?
- Server components for better performance
- Built-in routing and layouts
- TypeScript support
- Excellent developer experience

### Why FastAPI?
- High performance (async/await)
- Automatic API documentation
- Type safety with Pydantic
- Easy to test and maintain

### Why Neon PostgreSQL?
- Serverless architecture (auto-scaling)
- Generous free tier
- Excellent performance
- Easy integration with asyncpg

### Why Better Auth?
- Modern authentication solution
- Built for Next.js
- Supports various auth methods
- Easy to configure

---

## 11. Success Metrics

### Technical Metrics
- API response time < 200ms
- Frontend load time < 2 seconds
- Zero security vulnerabilities
- 90%+ test coverage
- 100% type safety

### User Experience Metrics
- Simple, intuitive UI
- Fast task creation (< 1 second)
- Responsive on all devices
- Clear error messages
- Reliable data persistence

---

## 12. Constraints & Assumptions

### Constraints
- Must use specified tech stack
- Must follow spec-driven development
- Must implement authentication on all endpoints
- Must ensure users can only access their own data
- Must be deployable to cloud platforms

### Assumptions
- Users have modern browsers (Chrome, Firefox, Safari, Edge)
- Users have stable internet connection
- Database connection is reliable
- JWT tokens are stored securely in httpOnly cookies

---

## 13. References

### Documentation
- `@CLAUDE.md` - Main navigation guide
- `@AGENTS.md` - Agent behavior rules
- `@specs/architecture.md` - System architecture
- `@frontend/CLAUDE.md` - Frontend-specific guide
- `@backend/CLAUDE.md` - Backend-specific guide

### Specifications
- `@specs/features/` - Feature specifications
- `@specs/api/` - API specifications
- `@specs/database/` - Database schemas
- `@specs/ui/` - UI specifications

---

**Status:** MVP Complete - Testing Phase
**Next Step:** Comprehensive testing and bug fixes
**Framework:** SpecKit Plus v2.0
**Managed By:** Claude Code
**Implementation Period:** December 30, 2025 - January 7, 2026
