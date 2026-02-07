# Claude Code Navigation Guide - Phase II Web Application

This document serves as the main navigation guide for Claude Code when working with the **Phase II: Full-Stack Web Application** todo manager project.

## 1. PROJECT OVERVIEW

**Name:** Todo Manager - Phase II Web Application
**Type:** Full-Stack Web Application (Next.js + FastAPI)
**Architecture:** Monorepo with separate frontend and backend
**Development Framework:** SpecKit Plus (Spec-Driven Development)
**Status:** Phase II - Ready for Development

### Purpose
A modern, full-featured todo management web application with user authentication, real-time updates, and cloud database persistence. This phase transitions from the CLI application (Phase I) to a production-ready web application.

### Technology Stack

**Frontend:**
- Next.js 14/15 (App Router)
- TypeScript
- Tailwind CSS
- Better Auth (Authentication)
- React Query (Data fetching)

**Backend:**
- FastAPI (Python 3.13+)
- SQLModel (ORM)
- Neon PostgreSQL (Cloud Database)
- Pydantic (Validation)
- Alembic (Migrations)

**Development:**
- SpecKit Plus (Specification framework)
- UV (Python package manager)
- Claude Code (AI-powered development)

---

## 2. SPEC-KIT STRUCTURE

The project uses **SpecKit Plus** for spec-driven development. All specifications are located in the `/specs` directory with the following organization:

```
specs/
├── overview.md                    # High-level project overview
├── features/                      # Feature specifications
│   ├── task-crud.md              # Todo CRUD operations
│   ├── task-priorities.md        # Priority management
│   ├── task-tags.md              # Tag system
│   ├── task-recurrence.md        # Recurring tasks
│   └── user-authentication.md    # Auth system
├── api/                          # API endpoint specifications
│   ├── todos-endpoints.md        # /api/todos/* endpoints
│   ├── users-endpoints.md        # /api/users/* endpoints
│   └── auth-endpoints.md         # /api/auth/* endpoints
├── database/                     # Database schema specifications
│   ├── schema.md                 # Complete DB schema
│   ├── users-table.md            # Users table spec
│   └── todos-table.md            # Todos table spec
└── ui/                           # UI component specifications
    ├── pages.md                  # Page specifications
    ├── components.md             # Component library
    └── layouts.md                # Layout specifications
```

### Spec Types

1. **Feature Specs** (`/specs/features/`): Define WHAT to build
   - User stories
   - Acceptance criteria
   - Business logic
   - Edge cases

2. **API Specs** (`/specs/api/`): Define backend endpoints
   - Request/response formats
   - Status codes
   - Error handling
   - Authentication requirements

3. **Database Specs** (`/specs/database/`): Define data models
   - Table schemas
   - Relationships
   - Indexes
   - Constraints

4. **UI Specs** (`/specs/ui/`): Define frontend components
   - Component behavior
   - Props/API
   - Styling requirements
   - Accessibility

---

## 3. HOW TO USE SPECS

### Reading Specs

**ALWAYS read the relevant spec BEFORE implementing any feature:**

```bash
# Reference specs using @ notation
@specs/features/task-crud.md
@specs/api/todos-endpoints.md
@specs/database/schema.md
@specs/ui/components.md
```

### Spec-Driven Workflow

1. **Before Implementation:**
   - Read the feature spec in `@specs/features/[feature].md`
   - Review related API spec in `@specs/api/[endpoints].md`
   - Check database spec in `@specs/database/[table].md`
   - Review UI spec in `@specs/ui/[component].md`

2. **During Implementation:**
   - Follow spec requirements exactly
   - Reference spec for acceptance criteria
   - Validate against spec edge cases

3. **After Implementation:**
   - Verify all acceptance criteria met
   - Test edge cases from spec
   - Update spec if requirements changed (with approval)

### Updating Specs

If requirements change during implementation:
1. **Document the change** in spec file
2. **Get user approval** before proceeding
3. **Update related specs** for consistency
4. **Note changes** in commit message

---

## 4. PROJECT STRUCTURE

```
phase-2-web-app/
├── frontend/                      # Next.js Frontend
│   ├── src/
│   │   ├── app/                  # App Router (pages, layouts, API routes)
│   │   ├── components/           # Reusable React components
│   │   ├── lib/                  # Utilities and helpers
│   │   └── styles/               # Global styles
│   ├── public/                   # Static assets
│   ├── tests/                    # Frontend tests
│   ├── package.json
│   ├── next.config.js
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── CLAUDE.md                 # Frontend-specific guide
│
├── backend/                      # FastAPI Backend
│   ├── app/                      # Application code
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── models.py            # SQLModel models
│   │   ├── routers/             # API route handlers
│   │   ├── database.py          # Database connection
│   │   ├── auth.py              # Authentication logic
│   │   └── config.py            # Configuration
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # Backend tests
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── CLAUDE.md                # Backend-specific guide
│
├── specs/                        # SpecKit Plus specifications
│   ├── overview.md
│   ├── features/
│   ├── api/
│   ├── database/
│   └── ui/
│
├── .claude/                      # Claude Code configuration
│   ├── agents/                  # Specialized agents
│   ├── commands/                # Custom commands
│   └── skills/                  # Development skills
│
├── .specify/                     # SpecKit Plus framework
│   ├── memory/
│   ├── scripts/
│   └── templates/
│
├── history/                      # Development history
│   └── prompts/
│
├── CLAUDE.md                     # This file (main guide)
├── AGENTS.md                     # Agent behavior rules
├── PROCEDURES.md                 # Development procedures
└── README.md                     # Project documentation
```

---

## 5. DEVELOPMENT WORKFLOW

Follow this step-by-step process for implementing features:

### Step 1: Read the Specification
```bash
# Read the feature spec
@specs/features/[feature-name].md

# Example: Implementing task CRUD
@specs/features/task-crud.md
```

### Step 2: Implement Backend
```bash
# Navigate to backend
cd backend

# Read backend-specific guide
@backend/CLAUDE.md

# Implement according to:
@specs/api/[endpoints].md
@specs/database/[table].md

# Run backend tests
uv run pytest
```

### Step 3: Implement Frontend
```bash
# Navigate to frontend
cd frontend

# Read frontend-specific guide
@frontend/CLAUDE.md

# Implement according to:
@specs/ui/[component].md

# Run frontend tests
npm test
```

### Step 4: Test and Iterate
```bash
# Run both servers
# Terminal 1: Backend
cd backend && uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev

# Test the feature end-to-end
# Verify against acceptance criteria in spec
```

### Step 5: Integration Testing
```bash
# Test full user flow
# Verify authentication
# Check error handling
# Test edge cases from spec
```

---

## 6. COMMANDS

### Frontend Commands
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server (http://localhost:3000)
npm run dev

# Run tests
npm test
npm run test:watch

# Build for production
npm run build

# Start production server
npm start

# Lint and format
npm run lint
npm run format
```

### Backend Commands
```bash
# Navigate to backend
cd backend

# Install dependencies (using UV)
uv sync

# Run development server (http://localhost:8000)
uvicorn app.main:app --reload

# Alternative: Using UV
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest
uv run pytest -v  # Verbose
uv run pytest tests/unit  # Unit tests only

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1

# API documentation (auto-generated)
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

### Docker Commands (if using Docker)
```bash
# Start both frontend and backend
docker-compose up

# Start in detached mode
docker-compose up -d

# Stop containers
docker-compose down

# Rebuild containers
docker-compose up --build

# View logs
docker-compose logs -f
```

### Full Stack Development
```bash
# Terminal 1: Backend
cd backend && uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev

# Terminal 3: Database (if running locally)
# postgres or docker-compose up postgres
```

---

## 7. IMPORTANT NOTES

### Spec-Driven Development Philosophy

This project follows **strict spec-driven development**:

- **NO implementation without specs**: Always read the spec first
- **Specs are the source of truth**: If unclear, refer to the spec
- **Changes require spec updates**: Update specs when requirements change
- **Test against specs**: Acceptance criteria define success

### Agent-Assisted Development

This project uses **Claude Code for all development**:

- **No manual coding**: All code generated via Claude Code
- **Agent specialization**: Use specialized agents (see `@AGENTS.md`)
- **Skill-based tasks**: Leverage skills in `.claude/skills/`
- **Quality checks**: Agents follow constitution in `.specify/memory/constitution.md`

### Agent Behavior Rules

Refer to `@AGENTS.md` for detailed agent behavior rules including:
- When to use which agent (nextjs-developer, fastapi-developer, auth-specialist, etc.)
- Agent responsibilities and constraints
- Communication patterns between agents
- Quality standards and testing requirements

### Development Principles

1. **Read specs first**: Never implement without reading the spec
2. **Follow the architecture**: Backend = API, Frontend = UI, separate concerns
3. **Test everything**: Write tests for all features
4. **Use TypeScript**: Frontend must be strongly typed
5. **Validate inputs**: Backend must validate all inputs
6. **Handle errors**: Proper error handling on both sides
7. **Security first**: Authentication, authorization, input sanitization
8. **Document as you go**: Update docs when changing behavior

### File References

When referencing files in this project, use the `@` notation:

```bash
# Main guides
@CLAUDE.md                    # This file (main navigation)
@AGENTS.md                    # Agent behavior rules
@PROCEDURES.md                # Development procedures
@README.md                    # Project documentation

# Specs
@specs/overview.md
@specs/features/[feature].md
@specs/api/[endpoints].md
@specs/database/[table].md
@specs/ui/[component].md

# Code
@frontend/CLAUDE.md           # Frontend guide
@backend/CLAUDE.md            # Backend guide
@backend/app/main.py
@frontend/src/app/page.tsx
```

### Quick Reference

| Task | Guide to Read |
|------|---------------|
| Understand project | `@CLAUDE.md` (this file) |
| Implement backend | `@backend/CLAUDE.md` |
| Implement frontend | `@frontend/CLAUDE.md` |
| Check agent rules | `@AGENTS.md` |
| Review procedures | `@PROCEDURES.md` |
| Find feature spec | `@specs/features/` |
| Find API spec | `@specs/api/` |
| Find DB spec | `@specs/database/` |
| Find UI spec | `@specs/ui/` |

---

## Getting Started

**For Claude Code:**

1. Read this file (`@CLAUDE.md`) to understand the project structure
2. Read `@AGENTS.md` to understand agent roles and behavior
3. Read `@specs/overview.md` for project requirements
4. Read relevant specs before implementing features
5. Follow the development workflow outlined in Section 5

**For New Features:**

1. Check if spec exists in `@specs/features/[feature].md`
2. If no spec, ask user to create one using SpecKit Plus
3. Read spec thoroughly
4. Implement backend (see `@backend/CLAUDE.md`)
5. Implement frontend (see `@frontend/CLAUDE.md`)
6. Test end-to-end
7. Verify against spec acceptance criteria

---

**Project Phase:** II - Full-Stack Web Application
**Status:** Ready for Development
**Last Updated:** 2025-12-31
**Development Framework:** SpecKit Plus
**AI Assistant:** Claude Code
