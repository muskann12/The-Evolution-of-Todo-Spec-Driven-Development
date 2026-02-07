# Todo Manager - Phase III: AI-Powered Chatbot

> A full-stack todo management web application with an AI-powered chatbot for natural language task management.

[![Next.js](https://img.shields.io/badge/Next.js-16%2B-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Python_3.13%2B-009688)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon_Serverless-316192)](https://neon.tech/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9%2B-blue)](https://www.typescriptlang.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991)](https://openai.com/)
[![MCP](https://img.shields.io/badge/MCP-Tools-orange)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/license-Educational-orange)](./LICENSE)

---

## Overview

**Phase III** extends the Phase II web application with an AI-powered chatbot that allows users to manage their tasks through natural language conversations. The chatbot uses OpenAI's GPT-4o model with Model Context Protocol (MCP) tools to create, read, update, and delete tasks.

### What's New in Phase III

- **AI Chatbot Interface** - Conversational task management
- **Natural Language Processing** - Create tasks by simply describing them
- **5 MCP Tools** - add_task, list_tasks, update_task, complete_task, delete_task
- **Stateless Architecture** - All conversation state persisted to database
- **Multi-turn Conversations** - Context-aware AI responses
- **Tool Call Visualization** - See what the AI is doing in real-time

---

## Architecture

### System Overview

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│  Next.js        │ ←──────→│  FastAPI        │ ←──────→│  PostgreSQL     │
│  Frontend       │  HTTPS  │  Backend        │   SQL   │  Database       │
│  + ChatKit      │         │  + OpenAI       │         │  (Neon Cloud)   │
│  (Port 3000)    │         │  (Port 8000)    │         │                 │
│                 │         │                 │         │                 │
└─────────────────┘         └────────┬────────┘         └─────────────────┘
                                     │
                                     │ API Calls
                                     ↓
                            ┌─────────────────┐
                            │                 │
                            │  OpenAI API     │
                            │  (GPT-4o)       │
                            │                 │
                            └─────────────────┘
```

### Stateless Chat Flow

```
1. User types message in chat UI
   ↓
2. POST /api/chat/message (with JWT cookie)
   ↓
3. Backend authenticates user (JWT → user_id)
   ↓
4. Get/create conversation (from database)
   ↓
5. Fetch last 20 messages (from database)
   ↓
6. Store user message (to database)
   ↓
7. Build message array for OpenAI
   ↓
8. Run OpenAI Agent with MCP tools
   ├── Agent analyzes message
   ├── Agent calls MCP tools (e.g., add_task)
   │   └── Tool executes (filtered by user_id)
   └── Agent generates response
   ↓
9. Store assistant response (to database)
   ↓
10. Return response to client
   ↓
11. Chat UI displays response
```

---

## Tech Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 16+ | React framework with App Router |
| TypeScript | 5.9+ | Type-safe JavaScript |
| Tailwind CSS | 3.4+ | Utility-first CSS |
| React | 19+ | UI library |
| OpenAI ChatKit | Latest | Pre-built chat UI components |
| React Query | 5+ | Server state management |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| FastAPI | 0.109+ | High-performance async API |
| Python | 3.13+ | Backend language |
| SQLModel | 0.0.14+ | ORM (SQLAlchemy + Pydantic) |
| PostgreSQL | 15+ | Database (Neon Serverless) |
| OpenAI SDK | Latest | AI model integration |
| MCP SDK | Latest | Tool protocol implementation |
| PyJWT | 2.8+ | JWT authentication |

### AI & ML
| Technology | Purpose |
|------------|---------|
| OpenAI GPT-4o | Language model for chat |
| MCP (Model Context Protocol) | Standardized tool calling |
| Function Calling | AI-to-tool communication |

---

## Quick Start

### Prerequisites

- **Node.js** 18.x or higher
- **Python** 3.13 or higher
- **UV** Package Manager ([Install](https://docs.astral.sh/uv/))
- **PostgreSQL** (Neon Serverless recommended)
- **OpenAI API Key** ([Get one](https://platform.openai.com/))

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/Roofan-Jlove/Hackathon-II-TODO-APP.git
cd Hackathon-II-TODO-APP/phase-3-ai-chatbot
```

#### 2. Set Up Backend

```bash
cd backend

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your credentials:
# - DATABASE_URL (Neon PostgreSQL)
# - BETTER_AUTH_SECRET (JWT secret)
# - OPENAI_API_KEY (OpenAI API key)
# - CORS_ORIGINS (frontend URL)

# Run the backend server
uv run uvicorn app.main:app --reload
```

Backend: **http://localhost:8000**
API Docs: **http://localhost:8000/docs**

#### 3. Set Up Frontend

```bash
cd ../frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with backend URL

# Run the frontend server
npm run dev
```

Frontend: **http://localhost:3000**

#### 4. Access the Application

1. Open **http://localhost:3000** in your browser
2. Sign up or log in
3. Navigate to the **Chat** page
4. Start chatting with the AI assistant!

---

## Features

### AI Chat Commands

The AI assistant understands natural language. Here are some example commands:

#### Creating Tasks
```
"Create a task to buy groceries"
"Add a high priority task for the client meeting tomorrow"
"I need to remember to call mom this weekend"
"Make a task: Review Q4 reports, priority high, tags: work, urgent"
```

#### Listing Tasks
```
"Show me my tasks"
"List all high priority tasks"
"What tasks do I have due this week?"
"Show completed tasks"
```

#### Updating Tasks
```
"Change the priority of task 5 to high"
"Update the client meeting task to include agenda prep"
"Mark task 3 as in progress"
```

#### Completing Tasks
```
"Mark task 3 as done"
"Complete the groceries task"
"I finished the code review"
```

#### Deleting Tasks
```
"Delete task 7"
"Remove the groceries task"
"Cancel the old meeting task"
```

### MCP Tools

The AI uses these 5 tools to manage tasks:

| Tool | Description | Parameters |
|------|-------------|------------|
| `add_task` | Create a new task | title, description, priority, tags, due_date |
| `list_tasks` | Retrieve tasks with filters | status, priority, tags, limit |
| `update_task` | Update an existing task | task_id, title, description, status, priority |
| `complete_task` | Mark a task as completed | task_id |
| `delete_task` | Delete a task permanently | task_id |

**Security Note:** All tools automatically receive the `user_id` from JWT authentication and filter database queries accordingly.

---

## Project Structure

```
phase-3-ai-chatbot/
├── frontend/                        # Next.js Frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── chat/               # AI Chat page
│   │   │   │   └── page.tsx        # Chat interface
│   │   │   ├── tasks/              # Task management pages
│   │   │   └── ...
│   │   ├── components/
│   │   │   ├── features/
│   │   │   │   ├── chat/           # Chat components
│   │   │   │   └── tasks/          # Task components
│   │   │   └── ...
│   │   └── lib/
│   │       ├── api.ts              # API client (includes chat methods)
│   │       └── types.ts            # TypeScript types
│   ├── package.json
│   └── README.md
│
├── backend/                         # FastAPI Backend
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── routers/
│   │   │   ├── chat.py             # Chat endpoints
│   │   │   ├── tasks.py            # Task CRUD endpoints
│   │   │   └── auth.py             # Auth endpoints
│   │   ├── mcp/
│   │   │   └── server.py           # 5 MCP tools
│   │   ├── ai/
│   │   │   ├── agent.py            # OpenAI Agent
│   │   │   └── prompts.py          # System prompts
│   │   ├── models.py               # SQLModel models
│   │   └── ...
│   ├── pyproject.toml
│   └── README.md
│
├── specs/                           # Specifications
│   ├── features/
│   │   └── chatbot-features.md     # Chatbot feature specs
│   ├── api/
│   │   └── chat-endpoints.md       # Chat API specs
│   └── mcp/
│       └── mcp-tools-overview.md   # MCP tools specs
│
├── CLAUDE.md                        # Claude Code navigation guide
└── README.md                        # This file
```

---

## API Endpoints

### Chat Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat/message` | Send a message to AI assistant |
| `GET` | `/api/chat/conversations` | List user's conversations |
| `GET` | `/api/chat/conversations/{id}` | Get conversation with messages |
| `DELETE` | `/api/chat/conversations/{id}` | Delete a conversation |

### Example: Send Chat Message

**Request:**
```bash
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -H "Cookie: auth-token=<jwt-token>" \
  -d '{
    "message": "Create a task to buy groceries",
    "conversation_id": 123
  }'
```

**Response:**
```json
{
  "conversation_id": 123,
  "response": "✅ I've created a task titled 'Buy groceries'. Would you like to set a due date or priority?",
  "tool_calls": [
    {
      "tool": "add_task",
      "result": {
        "success": true,
        "data": {
          "id": "task-uuid",
          "title": "Buy groceries",
          "priority": "medium"
        }
      }
    }
  ]
}
```

---

## Environment Variables

### Backend (.env)

```bash
# Database - Neon Serverless PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# Authentication
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters

# CORS
CORS_ORIGINS=http://localhost:3000

# OpenAI (Phase III)
OPENAI_API_KEY=sk-your-openai-api-key

# Optional
DEBUG=false
```

### Frontend (.env.local)

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters
BETTER_AUTH_URL=http://localhost:3000
```

---

## Security

### User Isolation

**All MCP tools filter by user_id:**
- `user_id` is extracted from JWT token
- Every database query includes `WHERE user_id = ?`
- Users can only access their own tasks and conversations

### Authentication Flow

1. User logs in → receives JWT token in httpOnly cookie
2. Chat requests include cookie automatically
3. Backend verifies JWT, extracts user_id
4. MCP tools receive user_id for filtering

### Data Privacy

- Conversations stored only in your database
- Messages sent to OpenAI for processing
- No conversation data shared between users

---

## Development

### Running Both Servers

**Terminal 1 - Backend:**
```bash
cd backend
uv run uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Testing

**Backend Tests:**
```bash
cd backend
uv run pytest -v
uv run pytest tests/test_mcp_tools.py -v
uv run pytest tests/test_chat_endpoints.py -v
```

**Frontend Tests:**
```bash
cd frontend
npm test
npm run test:run
```

### Database Migrations

```bash
cd backend
alembic revision --autogenerate -m "Add conversations and messages tables"
alembic upgrade head
```

---

## Troubleshooting

### Common Issues

**1. OpenAI API Key Error:**
```bash
# Check if key is set
echo $OPENAI_API_KEY

# Ensure key is in backend/.env
OPENAI_API_KEY=sk-your-key-here
```

**2. Chat Not Working:**
- Check backend logs for errors
- Verify JWT cookie is being sent
- Ensure CORS_ORIGINS includes frontend URL

**3. Database Connection:**
```bash
# Verify DATABASE_URL format
postgresql+asyncpg://user:password@host:5432/dbname
```

**4. MCP Tool Errors:**
- Check that user_id is being passed correctly
- Verify database tables exist (run migrations)

---

## Documentation

- **Main Guide:** [CLAUDE.md](./CLAUDE.md) - Navigation for Claude Code
- **Backend Docs:** [backend/README.md](./backend/README.md) - Backend guide
- **Frontend Docs:** [frontend/README.md](./frontend/README.md) - Frontend guide
- **Specifications:** [specs/](./specs/) - Feature and API specifications
- **API Docs:** http://localhost:8000/docs (when backend is running)

---

## Contributing

This is an educational hackathon project. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Read the relevant specifications
4. Write tests for your feature
5. Implement according to specs
6. Submit a Pull Request

---

## Acknowledgments

- **Claude Code** - AI-powered development assistant
- **OpenAI** - GPT-4o language model
- **SpecKit Plus** - Specification-driven development framework
- **Anthropic MCP** - Model Context Protocol

---

## License

Educational project for learning purposes.

---

<div align="center">

**Built with Next.js, FastAPI, OpenAI, and Claude Code**

**Phase III - AI-Powered Chatbot**

**Status:** Development Complete ✅

**Last Updated:** January 16, 2026

[⬆ Back to Top](#todo-manager---phase-iii-ai-powered-chatbot)

</div>
