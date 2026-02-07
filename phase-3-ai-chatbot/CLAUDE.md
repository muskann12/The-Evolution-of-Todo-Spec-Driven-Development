# Claude Code Navigation Guide - Phase II-III Web Application

This document serves as the main navigation guide for Claude Code when working with the **Phase II-III: Full-Stack Web Application with AI Chatbot** todo manager project.

## 1. PROJECT OVERVIEW

**Name:** Todo Manager - Phase II-III Web Application with AI Chatbot
**Type:** Full-Stack Web Application (Next.js + FastAPI) + AI Chatbot
**Architecture:** Monorepo with separate frontend and backend
**Development Framework:** SpecKit Plus (Spec-Driven Development)
**Status:** Phase III - AI Chatbot Development

### Purpose
A modern, full-featured todo management web application with user authentication, real-time updates, and cloud database persistence. Phase II transitions from the CLI application (Phase I) to a production-ready web application. **Phase III adds AI-powered chatbot using OpenAI Agents SDK and MCP tools**, enabling users to manage tasks through natural language conversations.

### Technology Stack

**Frontend (Phase II):**
- Next.js 14/15 (App Router)
- TypeScript
- Tailwind CSS
- Better Auth (Authentication)
- React Query (Data fetching)

**Frontend (Phase III - AI Chatbot):**
- OpenAI ChatKit (Pre-built chat UI components)
- React 18+ (Chat components and state management)

**Backend (Phase II):**
- FastAPI (Python 3.13+)
- SQLModel (ORM)
- Neon PostgreSQL (Cloud Database)
- Pydantic (Validation)
- Alembic (Migrations)

**Backend (Phase III - AI Integration):**
- OpenAI Agents SDK (AI agent orchestration and tool calling)
- OpenAI GPT-4o / GPT-4o-mini (Language models)
- Official Model Context Protocol (MCP) SDK (Python) (Stateless tool server)
- AsyncOpenAI client (Async Python client for OpenAI API)

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
│   ├── task-crud.md              # Todo CRUD operations (Features 1-7)
│   ├── task-priorities.md        # Priority management
│   ├── task-tags.md              # Tag system
│   ├── task-recurrence.md        # Recurring tasks
│   ├── user-authentication.md    # Auth system
│   └── chatbot-features.md       # AI chatbot features (Features 8-13, Phase III)
├── api/                          # API endpoint specifications
│   ├── todos-endpoints.md        # /api/todos/* endpoints
│   ├── users-endpoints.md        # /api/users/* endpoints
│   ├── auth-endpoints.md         # /api/auth/* endpoints
│   └── chat-endpoints.md         # /api/chat/* endpoints (Phase III)
├── database/                     # Database schema specifications
│   ├── schema.md                 # Complete DB schema
│   ├── users-table.md            # Users table spec
│   ├── todos-table.md            # Todos table spec
│   ├── conversations-table.md    # Conversations table spec (Phase III)
│   └── messages-table.md         # Messages table spec (Phase III)
├── ui/                           # UI component specifications
│   ├── pages.md                  # Page specifications
│   ├── components.md             # Component library
│   ├── layouts.md                # Layout specifications
│   └── chat-ui.md                # Chat interface (Phase III)
└── mcp/                          # MCP Tools specifications (Phase III)
    ├── mcp-tools-overview.md     # MCP tools architecture
    └── tool-signatures.md        # 5 MCP tool signatures
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

5. **MCP Tools Specs** (`/specs/mcp/`): Define AI agent tools (Phase III)
   - Tool signatures
   - Tool descriptions
   - Parameter specifications
   - Return value formats

---

## 3. PHASE III: AI CHATBOT

Phase III extends the TODO application with conversational AI capabilities, allowing users to manage tasks through natural language interactions with an AI assistant.

### Architecture Overview

**Stateless Architecture:**
- ALL conversation state stored in PostgreSQL database
- NO server-side sessions or in-memory state
- Server can restart without losing conversations
- Horizontal scaling possible (multiple servers, same database)

**Key Components:**

1. **OpenAI Agent** (`backend/app/ai/agent.py`)
   - Orchestrates AI conversations
   - Manages multi-turn tool calling (max 5 iterations)
   - Processes natural language requests
   - Calls MCP tools to perform actions

2. **MCP Tool Server** (`backend/app/mcp/server.py`)
   - Exposes 5 stateless tools for task management
   - Tools ALWAYS accept `user_id` as first parameter
   - ALL database queries filter by `user_id` (user isolation)
   - Returns structured JSON responses

3. **Chat API Endpoint** (`POST /api/chat/message`)
   - Receives user messages
   - Authenticates via JWT (same as Phase II)
   - Fetches conversation history from database
   - Invokes OpenAI Agent with MCP tools
   - Stores AI responses in database
   - Returns response to client

4. **Chat UI** (`frontend/src/app/chat/page.tsx`)
   - Built with OpenAI ChatKit components
   - Displays conversation history
   - Sends messages to chat API
   - Shows loading states during AI processing
   - Handles errors gracefully

5. **Database Models**
   - `conversations` table (id, user_id, title, created_at, updated_at, is_active)
   - `messages` table (id, conversation_id, role, content, created_at)
   - Indexed for fast retrieval (last 20 messages per conversation)

### Technology Stack

**AI/ML Services:**
- OpenAI Agents SDK - AI agent orchestration and tool calling
- OpenAI GPT-4o / GPT-4o-mini - Language models for natural language understanding
- Official Model Context Protocol (MCP) SDK (Python) - Stateless tool server

**Frontend:**
- OpenAI ChatKit - Pre-built chat UI components
- Next.js 15+ (App Router) - Chat page and conversation UI
- React 18+ - Chat components and state management

**Backend:**
- FastAPI (existing) - Chat API endpoints
- AsyncOpenAI client - Async Python client for OpenAI API
- SQLModel/SQLAlchemy - ORM for conversation persistence

**Database Additions:**
- PostgreSQL (existing) - Add conversations and messages tables
- Async database drivers - asyncpg for async operations

**Security & Authentication:**
- JWT cookies (existing Phase II) - Same auth for chat endpoints
- User isolation - All conversations filtered by user_id

### Conversation Flow

**Stateless Request/Response Cycle:**

```
User types message in chat UI
    ↓
POST /api/chat/message
    ↓
1. Authenticate user (JWT → user_id)
2. Get/create conversation (from DB)
3. Fetch last 20 messages (from DB)
4. Store user message (to DB)
5. Build message array for AI
6. Run OpenAI Agent with MCP tools
    ↓
    Agent analyzes message
        ↓
        Agent calls MCP tools (e.g., add_task)
            ↓
            Tool executes (filtered by user_id)
            ↓
            Tool returns result
        ↓
        Agent generates response
    ↓
7. Store assistant response (to DB)
8. Return response to client
    ↓
Chat UI displays response
```

**Context Window Management:**
- Default: Last 20 messages sent to AI
- Token limits: GPT-4o (128K tokens), GPT-4o-mini (128K tokens)
- Automatic summarization for very long conversations

### System Prompt

The AI agent behavior is defined by `TODO_ASSISTANT_SYSTEM_PROMPT`:

```python
TODO_ASSISTANT_SYSTEM_PROMPT = """
You are a helpful TODO task assistant. You help users manage their tasks through natural language conversations.

Available MCP Tools:
1. add_task(user_id, title, description, priority, tags, due_date) - Create new task
2. list_tasks(user_id, status, priority, tags, limit) - Retrieve tasks with filters
3. update_task(user_id, task_id, title, description, status, priority) - Update existing task
4. complete_task(user_id, task_id) - Mark task as completed
5. delete_task(user_id, task_id) - Delete task permanently

Personality:
- Friendly and helpful
- Concise and action-oriented
- Professional but not robotic
- Encouraging for task completion

Response Format:
- Confirm what was done
- Show relevant details
- Offer next steps (optional)
- Use emojis sparingly (✅ ❌ 🎯 📅)
"""
```

---

## 4. MCP TOOLS

Phase III implements 5 MCP (Model Context Protocol) tools that the AI agent uses to manage tasks. All tools are stateless and ALWAYS filter by `user_id` for security.

### Tool 1: add_task

```python
@mcp_server.tool()
async def add_task(
    user_id: int,        # ALWAYS first parameter
    title: str,          # Required
    description: str = None,
    priority: str = "medium",  # "low", "medium", "high"
    tags: List[str] = None,
    due_date: str = None  # ISO 8601 format
) -> Dict[str, Any]:
    """
    Create a new TODO task. Use when user wants to add a task.

    Returns: {"success": True, "data": {"id": int, "title": str, ...}}
    """
```

**Usage Example:**
- User: "Create a high priority task for client presentation tomorrow"
- Agent calls: `add_task(user_id=123, title="Client presentation", priority="high", due_date="2026-01-13")`

### Tool 2: list_tasks

```python
@mcp_server.tool()
async def list_tasks(
    user_id: int,
    status: str = None,    # Filter by status: "pending", "completed"
    priority: str = None,  # Filter by priority: "low", "medium", "high"
    tags: List[str] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Retrieve tasks with optional filters.

    Returns: {"success": True, "data": [{"id": int, "title": str, ...}, ...]}
    """
```

**Usage Example:**
- User: "Show me my high priority tasks"
- Agent calls: `list_tasks(user_id=123, priority="high")`

### Tool 3: update_task

```python
@mcp_server.tool()
async def update_task(
    user_id: int,
    task_id: int,
    title: str = None,
    description: str = None,
    status: str = None,
    priority: str = None
) -> Dict[str, Any]:
    """
    Update an existing task. Only provided fields are updated.

    Returns: {"success": True, "data": {"id": int, "title": str, ...}}
    """
```

**Usage Example:**
- User: "Change the priority of task 5 to high"
- Agent calls: `update_task(user_id=123, task_id=5, priority="high")`

### Tool 4: complete_task

```python
@mcp_server.tool()
async def complete_task(
    user_id: int,
    task_id: int
) -> Dict[str, Any]:
    """
    Mark a task as completed.

    Returns: {"success": True, "data": {"id": int, "status": "completed", ...}}
    """
```

**Usage Example:**
- User: "Mark task 3 as done"
- Agent calls: `complete_task(user_id=123, task_id=3)`

### Tool 5: delete_task

```python
@mcp_server.tool()
async def delete_task(
    user_id: int,
    task_id: int
) -> Dict[str, Any]:
    """
    Delete a task permanently. Use with caution.

    Returns: {"success": True, "data": {"id": int, "deleted": True}}
    """
```

**Usage Example:**
- User: "Delete task 7"
- Agent calls: `delete_task(user_id=123, task_id=7)`

### MCP Tool Design Principles

**CRITICAL Requirements:**
1. **Stateless**: Tools MUST NOT maintain state between calls
2. **user_id First**: EVERY tool MUST accept user_id as first parameter
3. **Database Filter**: EVERY database query MUST filter by user_id
4. **Return JSON**: Tools MUST return Dict[str, Any], never arbitrary objects
5. **Type Hints**: All parameters MUST have type hints
6. **Clear Descriptions**: Docstrings MUST explain WHEN to use the tool
7. **Error Handling**: Tools MUST handle errors gracefully and return structured errors

---

## 5. HOW TO USE SPECS

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

## 6. DEVELOPMENT WORKFLOW

Follow this step-by-step process for implementing features:

### Phase II Features (Traditional Web Features)

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

### Phase III Features (AI Chatbot Features)

For implementing AI chatbot features, follow this extended workflow:

### Step 1: Read Phase III Specifications
```bash
# Read the chatbot feature spec
@speckit.specify (Section 5 - Features 8-13)

# Read MCP tools specification
@speckit.specify (Section 6 - MCP Tools)

# Read implementation plan
@speckit.plan (Phases 5-7)

# Read agent behavior rules
@AGENTS.md (Section 11 - Phase III Rules)
```

### Step 2: Implement MCP Tools (Backend)
```bash
# Navigate to backend
cd backend

# Create/update MCP tool server
@backend/app/mcp/server.py

# CRITICAL Requirements:
# - user_id ALWAYS first parameter
# - ALL queries filter by user_id
# - Return Dict[str, Any]
# - Include type hints
# - Stateless (no global state)

# Test MCP tools
uv run pytest tests/test_mcp_tools.py -v
```

### Step 3: Implement Database Models (Backend)
```bash
# Create conversation and message models
@backend/app/models.py

# Create Alembic migration
alembic revision --autogenerate -m "Add conversations and messages tables"

# Run migration
alembic upgrade head

# Verify schema
# Check conversations table (user_id, title, created_at, updated_at, is_active)
# Check messages table (conversation_id, role, content, created_at)
# Verify indexes on user_id and conversation_id
```

### Step 4: Implement OpenAI Agent (Backend)
```bash
# Create AI agent class
@backend/app/ai/agent.py

# Requirements:
# - Use AsyncOpenAI client
# - Integrate with MCP tools
# - Handle multi-turn conversations (max 5 iterations)
# - Include TODO_ASSISTANT_SYSTEM_PROMPT
# - Error handling for API failures

# Test agent
uv run pytest tests/test_ai_agent.py -v
```

### Step 5: Implement Chat API Endpoint (Backend)
```bash
# Create chat router
@backend/app/routers/chat.py

# POST /api/chat/message endpoint:
# 1. Authenticate user (JWT)
# 2. Get/create conversation
# 3. Fetch last 20 messages
# 4. Store user message
# 5. Run OpenAI Agent
# 6. Store assistant response
# 7. Return response

# Test endpoint
uv run pytest tests/test_chat_endpoints.py -v
```

### Step 6: Implement Chat UI (Frontend)
```bash
# Navigate to frontend
cd frontend

# Install OpenAI ChatKit
npm install @openai/chatkit

# Create chat page
@frontend/src/app/chat/page.tsx

# Requirements:
# - Use ChatKit components
# - Fetch conversation history
# - Send messages to /api/chat/message
# - Show loading states
# - Handle errors (401, 500)
# - credentials: 'include' for cookies

# Test UI
npm test
```

### Step 7: End-to-End Testing (Phase III)
```bash
# Run both servers
# Terminal 1: Backend
cd backend && uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev

# Test stateless architecture:
# 1. Start conversation
# 2. Send messages
# 3. Restart backend server
# 4. Reload frontend
# 5. Verify conversation persists

# Test user isolation:
# 1. Create tasks as User A
# 2. Login as User B
# 3. Try to access User A's tasks
# 4. Verify 403/404 response

# Test multi-turn conversations:
# 1. Send complex request
# 2. Verify agent calls multiple tools
# 3. Check conversation history

# Test error handling:
# 1. Send message without auth
# 2. Verify 401 response
# 3. Send invalid request
# 4. Verify error message displayed
```

---

## 7. COMMANDS

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

### Phase III Commands

```bash
# Navigate to backend
cd backend

# Test MCP tools
uv run pytest tests/test_mcp_tools.py -v

# Test specific MCP tool
uv run pytest tests/test_mcp_tools.py::test_add_task -v

# Test AI agent
uv run pytest tests/test_ai_agent.py -v

# Test chat endpoints
uv run pytest tests/test_chat_endpoints.py -v

# Test user isolation (CRITICAL)
uv run pytest tests/test_user_isolation.py -v

# Test stateless architecture
uv run pytest tests/test_stateless.py -v

# Run all Phase III tests
uv run pytest tests/test_mcp*.py tests/test_ai*.py tests/test_chat*.py -v

# Check OpenAI API key configuration
echo $OPENAI_API_KEY  # Should be set

# Monitor token usage (if implemented)
# Check logs for token consumption per request
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

## 8. IMPORTANT NOTES

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
| Find feature spec | `@specs/features/` or `@speckit.specify` |
| Find API spec | `@specs/api/` or `@speckit.specify` |
| Find DB spec | `@specs/database/` or `@speckit.specify` |
| Find UI spec | `@specs/ui/` or `@speckit.specify` |
| Find MCP tools spec | `@speckit.specify` (Section 6) |
| Find implementation plan | `@speckit.plan` |
| Find Phase III rules | `@AGENTS.md` (Section 11) |

---

## 9. PHASE III IMPORTANT NOTES

### Stateless Architecture (CRITICAL)

**Phase III MUST follow stateless architecture:**

❌ **FORBIDDEN:**
- Server-side sessions for conversations
- In-memory conversation storage
- Global variables tracking chat state
- Caching conversation state in memory
- Any state that doesn't survive server restart

✅ **REQUIRED:**
- ALL conversation state in PostgreSQL database
- Every request fetches fresh conversation history from database
- Server can restart without losing conversations
- Horizontal scaling possible (multiple servers, same database)

**Why This Matters:**
- Cloud-native deployment requires stateless architecture
- Load balancers can route requests to any server
- Server crashes don't lose conversation data
- Easy to scale horizontally by adding more servers

### Database Persistence

**ALL chat data MUST be persisted:**

1. **conversations table:**
   - Track every conversation (id, user_id, title, created_at, updated_at, is_active)
   - Index on (user_id, updated_at DESC) for fast listing
   - Foreign key to users table with CASCADE delete

2. **messages table:**
   - Store EVERY message (user, assistant, system, tool)
   - Track conversation_id, role, content, created_at
   - Index on (conversation_id, created_at DESC) for fast retrieval
   - Foreign key to conversations table with CASCADE delete

3. **Context Window:**
   - Fetch last 20 messages per request (default)
   - Configurable limit for different models
   - Efficient query with LIMIT and ORDER BY

### User Isolation (SECURITY CRITICAL)

**EVERY database query MUST filter by user_id:**

```python
# ✅ CORRECT - Filters by user_id
tasks = await db.execute(
    select(Task).where(Task.user_id == user_id).where(Task.id == task_id)
)

# ❌ WRONG - No user_id filter (SECURITY VULNERABILITY!)
tasks = await db.execute(
    select(Task).where(Task.id == task_id)
)
```

**Why This Matters:**
- Prevents users from accessing other users' data
- MCP tools receive user_id from JWT authentication
- Database layer enforces isolation (defense in depth)
- Audit trail shows which user accessed what data

### JWT Authentication

**Phase III uses existing Phase II JWT authentication:**

1. **Same endpoints:**
   - POST /api/auth/login (get JWT cookie)
   - POST /api/auth/register (create account)
   - GET /api/auth/me (verify token)

2. **Same cookie mechanism:**
   - httpOnly cookies for security
   - SameSite=Lax to prevent CSRF
   - Secure flag in production

3. **Frontend requirements:**
   - Use `credentials: 'include'` in fetch requests
   - Handle 401 responses (redirect to login)
   - Refresh token if needed

4. **Backend requirements:**
   - Use `Depends(get_current_user)` in chat endpoints
   - Extract user_id from JWT
   - Pass user_id to MCP tools

### OpenAI API Integration

**Critical considerations:**

1. **API Key Management:**
   - Store in environment variable: `OPENAI_API_KEY`
   - NEVER commit to git
   - Use different keys for dev/staging/production
   - Rotate keys periodically

2. **Cost Control:**
   - GPT-4o: ~$5 per 1M input tokens, ~$15 per 1M output tokens
   - GPT-4o-mini: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
   - Use GPT-4o-mini for cost-sensitive operations
   - Limit context window (default: 20 messages)
   - Monitor token usage per user/conversation

3. **Rate Limiting:**
   - OpenAI has rate limits (requests per minute, tokens per minute)
   - Implement exponential backoff for rate limit errors
   - Consider user-level rate limiting (prevent abuse)

4. **Error Handling:**
   - Handle OpenAI API failures gracefully
   - Show user-friendly error messages
   - Log errors for debugging
   - Fallback to "AI is unavailable" message

### MCP Tools Implementation

**Every MCP tool MUST:**

1. Accept `user_id` as FIRST parameter
2. Filter ALL database queries by `user_id`
3. Return `Dict[str, Any]` (structured JSON)
4. Include complete type hints
5. Have clear docstring explaining WHEN to use it
6. Handle errors gracefully and return structured errors
7. Be completely stateless (no global variables)

**Example:**
```python
@mcp_server.tool()
async def add_task(
    user_id: int,        # ✅ ALWAYS first
    title: str,
    description: str = None,
    priority: str = "medium"
) -> Dict[str, Any]:
    """Create a new task. Use when user wants to add a task."""
    async with get_db_session() as db:
        task = Task(
            user_id=user_id,  # ✅ CRITICAL
            title=title,
            description=description,
            priority=priority
        )
        db.add(task)
        await db.commit()

        return {
            "success": True,
            "data": {"id": task.id, "title": task.title}
        }
```

### Testing Requirements

**Phase III requires these additional tests:**

1. **MCP Tools Tests:**
   - Test each tool with valid inputs
   - Test user isolation (User A can't access User B's data)
   - Test error handling (invalid inputs, database errors)

2. **AI Agent Tests:**
   - Test agent can call tools correctly
   - Test multi-turn conversations
   - Test error recovery

3. **Chat Endpoint Tests:**
   - Test stateless architecture (restart server, verify data persists)
   - Test authentication (401 without JWT)
   - Test conversation history retrieval
   - Test message persistence

4. **Integration Tests:**
   - End-to-end conversation flow
   - User isolation across conversations
   - Error handling and recovery

### Development Best Practices

1. **Always read specs first:**
   - `@speckit.specify` for features and requirements
   - `@speckit.plan` for implementation details
   - `@AGENTS.md` (Section 11) for behavior rules

2. **Test stateless architecture:**
   - Restart server between tests
   - Verify data persists in database
   - Check no global state remains

3. **Verify user isolation:**
   - Create test users
   - Attempt cross-user access
   - Confirm 403/404 responses

4. **Monitor costs:**
   - Log token usage per request
   - Track OpenAI API costs
   - Optimize context window size

---

## 10. Getting Started

**For Claude Code:**

1. Read this file (`@CLAUDE.md`) to understand the project structure
2. Read `@AGENTS.md` to understand agent roles and behavior (especially Section 11 for Phase III)
3. Read `@speckit.specify` for Phase III features and requirements
4. Read `@speckit.plan` for Phase III implementation details
5. Read relevant specs before implementing features
6. Follow the development workflow outlined in Section 6

**For Phase II Features (Traditional Web Features):**

1. Check if spec exists in `@specs/features/[feature].md` or `@speckit.specify`
2. If no spec, ask user to create one using SpecKit Plus
3. Read spec thoroughly
4. Implement backend (see `@backend/CLAUDE.md`)
5. Implement frontend (see `@frontend/CLAUDE.md`)
6. Test end-to-end
7. Verify against spec acceptance criteria

**For Phase III Features (AI Chatbot Features):**

1. Read `@speckit.specify` (Section 5: Features 8-13, Section 6: MCP Tools)
2. Read `@speckit.plan` (Phases 5-7: AI Implementation)
3. Read `@AGENTS.md` (Section 11: Phase III Rules)
4. **Implement MCP Tools** (backend/app/mcp/server.py)
   - user_id ALWAYS first parameter
   - ALL queries filter by user_id
   - Return Dict[str, Any]
   - Test user isolation
5. **Implement Database Models** (conversations, messages tables)
   - Create Alembic migration
   - Add indexes for performance
6. **Implement OpenAI Agent** (backend/app/ai/agent.py)
   - Use AsyncOpenAI client
   - Integrate MCP tools
   - Handle multi-turn conversations
7. **Implement Chat Endpoint** (backend/app/routers/chat.py)
   - POST /api/chat/message
   - JWT authentication
   - Stateless architecture (fetch from DB)
8. **Implement Chat UI** (frontend/src/app/chat/page.tsx)
   - Use OpenAI ChatKit
   - credentials: 'include' for cookies
   - Handle loading and errors
9. **Test End-to-End**
   - Verify stateless architecture (restart server)
   - Verify user isolation
   - Verify multi-turn conversations
10. **Verify Against Specs**
    - Check acceptance criteria in speckit.specify
    - Test all edge cases
    - Verify security (user isolation, JWT auth)

---

**Project Phase:** III - AI-Powered Chatbot
**Status:** Phase III Specification Complete, Implementation In Progress
**Last Updated:** 2026-01-12
**Development Framework:** SpecKit Plus
**AI Assistant:** Claude Code
