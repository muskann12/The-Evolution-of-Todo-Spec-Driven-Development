<!--
Sync Impact Report:
- Version change: [NEW CONSTITUTION] → 1.0.0
- This is the initial constitution for The Evolution of Todo — Phase I
- Added sections: All sections are new (Vision, Role, SDD Mandate, Principles, Scope, Forward-Compatibility, Success Criteria)
- Templates requiring updates:
  ✅ .specify/templates/spec-template.md (aligned with testability and explicit requirements)
  ✅ .specify/templates/plan-template.md (aligned with constitution check and Phase I constraints)
  ⚠ .specify/templates/tasks-template.md (should verify task acceptance criteria align)
- Deferred TODOs: None
-->

# The Evolution of Todo — Phase I-III Constitution

## Vision & Educational Goal

This project simulates the real-world evolution of software systems from simple beginnings to distributed, cloud-native, AI-powered architectures. Phase I establishes foundational discipline in specification-driven development and architectural thinking. Students learn to articulate requirements, make explicit architectural decisions, and understand that code quality begins with clarity of thought before implementation. The purpose is to develop Product Architects who can specify systems, not just implement them.

## Phase III: AI-Powered Chatbot Extension

Phase III adds conversational AI capabilities to the TODO application while maintaining all Phase II web application features. Users can manage tasks through natural language conversations with an AI assistant powered by OpenAI's GPT models.

**Phase III Educational Goals**:
- Integrate AI/ML services (OpenAI Agents SDK) into applications
- Implement stateless, scalable chatbot architectures
- Design and build Model Context Protocol (MCP) tools
- Manage conversation state with database persistence
- Apply prompt engineering for effective AI behavior
- Ensure AI systems follow security and privacy principles

## Role of the Product Architect (Student)

Students act exclusively as Product Architects in Phase I. The Product Architect defines requirements, specifies behavior, establishes quality criteria, and validates outcomes. The Product Architect does NOT implement boilerplate code manually.

**Responsibilities**:
- Write specifications that are complete, testable, and unambiguous
- Make architectural decisions with explicit rationale
- Define acceptance criteria for all features
- Validate implementations against specifications
- Document decisions in ADRs when architecturally significant

**Prohibited Activities**:
- Manual implementation of repetitive boilerplate code
- Writing code before specifications exist
- Leaving requirements implicit or assumed

## Spec-Driven Development Mandate

All functionality MUST originate from written specifications before any code exists.

**Requirements for Specifications**:
- Define feature scope and boundaries explicitly
- Specify user interaction models with concrete examples
- Document data structures and their invariants
- Enumerate error conditions and handling requirements
- Establish testable acceptance criteria

**Non-Negotiable Rules**:
- No code SHALL be written without a corresponding specification artifact
- No specification SHALL remain abstract; every requirement MUST be testable and verifiable
- Specifications MUST be updated if implementation reveals ambiguities

## Core Principles

### I. Explicitness Over Implicitness

Every behavior MUST be explicitly specified. Default behaviors, error paths, and edge cases SHALL NOT be left to implementation discretion. If a behavior is not specified, it does not exist.

**Rationale**: Implicit assumptions lead to divergent implementations and untestable systems. Architectural clarity requires explicit contracts.

### II. Separation of Concerns

The application MUST maintain clear boundaries between user interface (CLI interaction), business logic (todo operations), and data management (in-memory storage). Each layer MUST be independently testable.

**Rationale**: Clean separation enables evolution—persistence can be added in Phase II without rewriting business logic. This principle ensures forward compatibility.

### III. Testability as First-Class Requirement (NON-NEGOTIABLE)

Every feature MUST include acceptance criteria that can be validated through automated or manual testing. Specifications SHALL include both positive test cases and negative/edge case scenarios. Code without tests is considered incomplete.

**Rationale**: Testability validates that specifications are implementable and complete. Untestable requirements are ambiguous requirements.

### IV. Minimal Viable Scope

Features MUST be scoped to the minimum necessary for Phase I objectives. No feature shall anticipate future phases unless explicitly required for forward compatibility. YAGNI (You Aren't Gonna Need It) is law.

**Rationale**: Over-engineering wastes time and introduces complexity. Simple solutions are easier to test, understand, and evolve.

### V. Error Transparency

All error conditions MUST be identified, classified, and handled with user-appropriate messaging. Silent failures are prohibited. Every error path MUST be specified and tested.

**Rationale**: Robust systems fail gracefully with clear diagnostics. Error handling is part of the specification, not an implementation detail.

### VI. Documentation as Contract

Code MUST reflect specifications exactly. Deviations require specification amendments. Documentation is not commentary; it is contractual definition of system behavior. All architectural decisions with long-term impact MUST be captured in ADRs.

**Rationale**: Specifications serve as the source of truth. Implementation-specification drift creates technical debt and ambiguity.

## Prohibition of Manual Boilerplate Coding

Students SHALL NOT write repetitive implementation code manually. Boilerplate code—including but not limited to data models, CRUD operations, CLI parsing, input validation, and standard error handling—MUST be generated through:

- AI-assisted code generation from specifications
- Template-based code generation tools
- Automated scaffolding systems

**Permitted Manual Work**:
- Writing specifications, architectural decision records, test cases
- Reviewing and refining generated code
- Writing unique business logic not covered by patterns

**Rationale**: Product Architects focus on what to build and why, not typing implementation details. Code generation from specs reinforces the discipline that specifications must be complete and precise.

## Scope Boundaries (CLI-only, in-memory only)

### Phase I Constraints

**In Scope**:
- Command-line interface interaction exclusively
- In-memory data storage with no persistence between sessions
- Single-user, single-process execution model
- Standard input/output for all user communication
- Python 3.x standard library plus explicitly approved dependencies

**Explicitly Out of Scope**:
- Graphical user interfaces
- File-based or database persistence
- Network communication
- Multi-user or concurrent access
- Web servers or APIs
- External service integrations

**Rationale**: Phase I is intentionally constrained to focus on specification quality and architectural thinking without the complexity of persistence, concurrency, or distribution.

## Phase III: AI Chatbot Technology Stack

### Required Technologies

**AI/ML Services**:
- OpenAI Agents SDK - AI agent orchestration and tool calling
- OpenAI GPT-4o / GPT-4o-mini - Language models for natural language understanding
- Official Model Context Protocol (MCP) SDK (Python) - Stateless tool server

**Frontend**:
- OpenAI ChatKit - Pre-built chat UI components
- Next.js 15+ (App Router) - Chat page and conversation UI
- React 18+ - Chat components and state management

**Backend**:
- FastAPI (existing) - Chat API endpoints
- AsyncOpenAI client - Async Python client for OpenAI API
- SQLModel/SQLAlchemy - ORM for conversation persistence

**Database Additions**:
- PostgreSQL (existing) - Add conversations and messages tables
- Async database drivers - asyncpg for async operations

**Security & Authentication**:
- JWT cookies (existing Phase II) - Same auth for chat endpoints
- User isolation - All conversations filtered by user_id

## Phase III: Stateless Architecture Principles

### Stateless Request/Response Model

The chatbot MUST follow stateless architecture where the server maintains NO conversation state in memory:

**Requirements**:
- ❌ NO server-side sessions for conversations
- ❌ NO in-memory conversation storage
- ❌ NO global variables tracking chat state
- ✅ ALL conversation state stored in database
- ✅ Every request fetches fresh conversation history from database
- ✅ Server can restart without losing conversations
- ✅ Horizontal scaling possible (multiple servers, same database)

**Rationale**: Stateless architecture enables cloud-native deployment, horizontal scaling, and resilience to server failures. Conversations persist across server restarts and load balancer routing.

### Database-Backed Persistence

**Conversation State**:
- Store ALL messages in `messages` table
- Track conversation metadata in `conversations` table
- Fetch last N messages (default: 20) on each request
- User sees full conversation history even after server restart

**Implementation Pattern**:
```python
# Every request:
1. Authenticate user (get user_id from JWT)
2. Fetch conversation from database (by conversation_id + user_id)
3. Load last 20 messages from database
4. Process user message
5. Call AI agent with message history
6. Store AI response in database
7. Return response
```

### Context Window Management

**Token Limits**:
- GPT-4o: 128K tokens (~96K words)
- Default conversation window: 20 messages
- Implement automatic summarization for long conversations
- Monitor token usage to optimize costs

**Rationale**: Limiting context window prevents token overflow, reduces API costs, and maintains response speed.

## Phase III: Model Context Protocol (MCP) Server

### MCP Tool Server Design

The application MUST expose a Model Context Protocol server that provides 5 stateless tools for task management:

**Tool 1: add_task**
```python
@mcp_server.tool()
async def add_task(
    user_id: int,        # ALWAYS first parameter
    title: str,          # Required
    description: str = None,
    priority: str = "medium",
    tags: List[str] = None,
    due_date: str = None
) -> Dict[str, Any]:
    """Create a new TODO task. Use when user wants to add a task."""
```

**Tool 2: list_tasks**
```python
@mcp_server.tool()
async def list_tasks(
    user_id: int,
    status: str = None,    # Filter by status
    priority: str = None,  # Filter by priority
    tags: List[str] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """Retrieve tasks with optional filters."""
```

**Tool 3: update_task**
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
    """Update an existing task."""
```

**Tool 4: complete_task**
```python
@mcp_server.tool()
async def complete_task(
    user_id: int,
    task_id: int
) -> Dict[str, Any]:
    """Mark a task as completed."""
```

**Tool 5: delete_task**
```python
@mcp_server.tool()
async def delete_task(
    user_id: int,
    task_id: int
) -> Dict[str, Any]:
    """Delete a task permanently."""
```

### MCP Tool Design Principles

**CRITICAL Requirements**:
1. **Stateless**: Tools MUST NOT maintain state between calls
2. **user_id First**: EVERY tool MUST accept user_id as first parameter
3. **Database Filter**: EVERY database query MUST filter by user_id
4. **Return JSON**: Tools MUST return Dict[str, Any], never arbitrary objects
5. **Type Hints**: All parameters MUST have type hints
6. **Clear Descriptions**: Docstrings MUST explain WHEN to use the tool
7. **Error Handling**: Tools MUST handle errors gracefully and return structured errors

**Rationale**: Stateless tools enable reliable, scalable AI agent operation. User isolation prevents data leakage. Type hints enable validation.

## Phase III: AI Agent Behavior Standards

### Natural Language Understanding

The AI agent MUST:
- Understand natural language task creation requests
- Extract task details (title, priority, due date, tags) from conversational input
- Handle ambiguous requests by asking clarifying questions
- Confirm actions clearly before executing them

**Examples**:
- Input: "Create a task to finish the report by Friday"
- Agent: Extracts title="Finish the report", due_date=Friday, priority=medium
- Agent: Uses add_task tool, then confirms "✅ Created 'Finish the report' due Friday"

### Tool Usage Guidelines

**When to Use Tools**:
- Task creation: Use `add_task` tool
- Listing tasks: Use `list_tasks` tool with appropriate filters
- Task updates: Use `update_task` tool with specific fields
- Task completion: Use `complete_task` tool
- Task deletion: Confirm first, then use `delete_task` tool

**Multi-Turn Conversations**:
- Agent MAY call multiple tools in sequence (max 5 iterations)
- Agent MUST provide conversational responses explaining actions
- Agent MUST handle tool failures gracefully

### Conversational Response Style

**Personality**:
- Friendly and helpful
- Concise and action-oriented
- Professional but not robotic
- Encouraging for task completion

**Response Format**:
- Confirm what was done
- Show relevant details
- Offer next steps (optional)
- Use emojis sparingly (✅ ❌ 🎯 📅)

**Example**:
```
User: "Create a high priority task for the client presentation"
AI: "I'll create that for you. ✅

Created: "Client presentation"
- Priority: High
- Status: Ready
- Created: Today

Would you like to set a due date or add any notes?"
```

### System Prompt Requirements

**System prompts MUST**:
1. Define agent identity and capabilities
2. List available tools with usage guidelines
3. Specify personality and tone
4. Provide behavioral guidelines for common scenarios
5. Include error handling templates
6. Show example interactions

**Rationale**: Clear system prompts ensure consistent, helpful AI behavior. Examples guide the model toward desired interaction patterns.

## Phase III: Database Schema Additions

### New Tables

**conversations**
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR(200),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_conversations_user_updated ON conversations(user_id, updated_at DESC);
```

**messages**
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    role VARCHAR(20) NOT NULL,  -- 'user', 'assistant', 'system', 'tool'
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_conversation FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at DESC);
```

### Data Model Principles

**User Isolation**:
- Every conversation MUST be associated with a user_id
- All queries MUST filter by user_id
- Users MUST NOT access other users' conversations

**Message Storage**:
- Store EVERY message (user, assistant, system, tool)
- Include timestamps for all messages
- Preserve complete conversation history
- Support fetching last N messages efficiently

**Conversation Metadata**:
- Track conversation title (auto-generated or user-set)
- Track creation and update timestamps
- Support soft delete (is_active flag)
- Enable conversation listing ordered by recency

## Phase III: Security and Privacy

### Authentication and Authorization

**Same JWT Authentication**:
- AI chat endpoints use existing Phase II JWT cookie authentication
- Same `/api/auth/login` and `/api/auth/register` endpoints
- JWT tokens in httpOnly cookies for security

**Authorization Rules**:
- Users can ONLY access their own conversations (filter by user_id)
- Users can ONLY create/read/update/delete their own messages
- MCP tools ALWAYS receive authenticated user_id
- 401 response if JWT token invalid/missing

### Conversation Privacy

**Privacy Principles**:
- User conversations are PRIVATE and ISOLATED
- AI responses are EPHEMERAL (not stored globally, only per-conversation)
- No conversation data shared between users
- Conversation history deleted when user deletes account

**Data Retention**:
- Conversations stored indefinitely unless user deletes
- Users can delete individual conversations
- Soft delete preserves audit trail (is_active = false)

### OpenAI API Security

**API Key Management**:
- OpenAI API key stored in environment variable ONLY
- NEVER expose API key in logs, errors, or responses
- Use separate API keys for dev/staging/production

**Cost Controls**:
- Limit conversation context window (default: 20 messages)
- Use GPT-4o-mini for cost-sensitive operations
- Monitor token usage per user/conversation
- Implement rate limiting on chat endpoints

**Rationale**: Security and privacy are non-negotiable. Users must trust that their conversations are private and their data is protected.

## Forward-Compatibility Expectations for Future Phases

Architectural decisions in Phase I MUST NOT preclude evolution toward:

- Persistent storage backends (Phase II: file, database)
- Multi-user capabilities (Phase III: authentication, authorization)
- API-based architectures (Phase IV: REST, GraphQL)
- Distributed systems (Phase V: microservices, message queues)
- AI/ML enhancements (Phase VI: recommendations, NLP)

**Design Requirements**:
- Specifications SHALL identify extension points where future capabilities will integrate
- Data models MUST be designed with schema evolution in mind
- Interfaces MUST separate concerns to enable component replacement in subsequent phases
- Business logic MUST be decoupled from storage implementation

**Rationale**: The evolution of the system is the pedagogical goal. Phase I architecture must enable, not hinder, future phases.

## Phase I Success Criteria

Phase I is complete when ALL of the following are satisfied:

1. **Specification Completeness**: A complete specification exists for all todo application features in `specs/<feature>/spec.md`
2. **Generated Implementation**: All features are implemented through generated code from specifications; zero manually-written boilerplate code exists
3. **Test Validation**: All acceptance criteria defined in specifications are validated and passing
4. **Architectural Documentation**: Architectural Decision Records exist for all significant design choices in `history/adr/`
5. **Functional CLI**: The application runs as a functional CLI todo manager with in-memory storage
6. **Documentation Quality**: Documentation fully describes system behavior, constraints, and extension points
7. **Architectural Articulation**: Students can articulate the rationale behind every architectural decision

**Measurement**:
- Success is measured by clarity of specifications, quality of architectural thinking, and completeness of validation against requirements
- Success is NOT measured by lines of code written, number of features, or implementation complexity

## Phase III Additional Success Criteria

Phase III is complete when ALL of the following Phase III criteria are satisfied:

**AI Integration**:
1. OpenAI agent successfully integrated with AsyncOpenAI client
2. Agent can make multi-turn tool calls (up to 5 iterations)
3. Agent handles tool failures gracefully
4. System prompt produces consistent, helpful behavior

**MCP Server**:
5. MCP server running with 5 tools (add, list, update, complete, delete)
6. All tools are stateless and accept user_id first parameter
7. All tools filter database queries by user_id
8. All tools return structured JSON responses

**Conversation Management**:
9. Conversations and messages tables created with proper indexes
10. Conversation state persists across server restarts
11. Users can only access their own conversations
12. Context window limited to 20 messages by default

**Chat UI**:
13. Chat page accessible at `/chat` route
14. Chat interface displays message history
15. Loading states shown during AI processing
16. Error messages displayed gracefully
17. JWT authentication working with credentials: 'include'

**Testing**:
18. Unit tests for MCP tools (user isolation, error handling)
19. Integration tests for chat API endpoints
20. Manual testing of full conversation flow
21. Testing of 401 error handling (session expiry)

**Documentation**:
22. System prompt documented with examples
23. MCP tool descriptions clear and helpful
24. API endpoints documented
25. Architecture diagrams for AI/MCP integration

## Governance

This constitution supersedes all other development practices for Phase I. All work MUST comply with the principles and constraints defined herein.

**Amendment Process**:
- Amendments require explicit documentation of rationale
- Version bump follows semantic versioning (MAJOR.MINOR.PATCH)
- All dependent templates and artifacts MUST be updated for consistency

**Compliance Review**:
- All specifications MUST verify compliance with constitution principles
- All implementations MUST be validated against specifications
- Violations require explicit justification in the Complexity Tracking section of plans

**Enforcement**:
- Pull requests and reviews MUST verify constitution compliance
- Unjustified complexity is rejected
- Runtime development guidance is provided in `.claude/agents/` and CLAUDE.md

### Phase III Amendments (Version 2.0.0)

**Changes in Phase III**:
- Added AI/ML technology stack (OpenAI Agents SDK, MCP SDK, ChatKit)
- Introduced stateless architecture principles
- Specified MCP server with 5 tools
- Defined AI agent behavior standards
- Added database schema for conversations and messages
- Established security and privacy guidelines for AI features

**Rationale**: Phase III extends the TODO application with conversational AI capabilities while maintaining all Phase II web application features. Stateless architecture ensures scalability and reliability.

**Version**: 2.0.0 | **Phase III Ratified**: 2026-01-12 | **Last Amended**: 2026-01-12
