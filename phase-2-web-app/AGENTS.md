# AI Agent Behavior Rules - Spec-Driven Development

This document defines **mandatory behavior rules** for all AI agents (Claude Code, GitHub Copilot, ChatGPT, etc.) working on this project.

**CRITICAL:** This project uses **Spec-Driven Development (SDD)**. No agent is allowed to write code until the specification is complete and approved.

---

## 1. PURPOSE

### Spec-Driven Development Philosophy

This project follows **Spec-Driven Development (SDD)**, a disciplined approach where:

- **Specifications come first** - Code is never written before specs
- **Specs are the source of truth** - All decisions must be documented
- **No improvisation** - Agents cannot invent requirements or architecture
- **Quality by design** - Prevent bugs by thinking before coding

### The Spec-Kit Lifecycle

All AI agents **MUST** follow this lifecycle:

```
1. Constitution (WHY)    → Principles & Constraints
2. Specify (WHAT)        → Requirements & Acceptance Criteria
3. Plan (HOW)            → Architecture & Design
4. Tasks (BREAKDOWN)     → Atomic Work Units
5. Implement (CODE)      → Execution
```

**Golden Rule:** No spec = No code. Every line of code must trace back to a specification.

---

## 2. HOW AGENTS MUST WORK

### Strict Rules for All AI Agents

#### Rule 1: No Code Without Task ID
```
❌ FORBIDDEN: Writing code without a Task ID
✅ REQUIRED: Every code block must reference a Task ID

Example:
# [Task]: T-001
# [From]: speckit.specify §2.1, speckit.plan §3.4
def create_todo(title: str, description: str):
    ...
```

#### Rule 2: No Architecture Changes Without Plan Update
```
❌ FORBIDDEN: "Let me add a caching layer..."
✅ REQUIRED: "This requires updating speckit.plan §4.2 to add a caching component"
```

#### Rule 3: No Features Without Requirements
```
❌ FORBIDDEN: "I'll add email notifications for completed tasks"
✅ REQUIRED: "Email notifications are not in speckit.specify. Should I propose adding them?"
```

#### Rule 4: Constitution Defines Constraints
```
❌ FORBIDDEN: Switching tech stack without justification
✅ REQUIRED: Follow stack defined in speckit.constitution
```

#### Rule 5: Every Code File Must Link to Specs
```python
"""
Todo CRUD Operations

[Task]: T-003
[Spec]: speckit.specify §3.1 - Todo Management
[Plan]: speckit.plan §2.3 - Storage Layer
[AC]: User can create, read, update, delete todos
"""
```

### What to Do When Specs Are Missing

If an agent cannot find the required specification:

1. **STOP immediately** - Do not proceed with implementation
2. **Identify what's missing** - Which spec file needs updating?
3. **Request clarification** - Ask the user to update the spec
4. **Never improvise** - Do not invent requirements or design

**Example:**
```
Agent: "I need to implement user authentication, but I cannot find:
- speckit.specify §X - Authentication requirements (WHAT)
- speckit.plan §Y - Auth architecture (HOW)
- speckit.tasks - Task breakdown for auth

Please provide these specifications before I proceed."
```

---

## 3. SPEC-KIT WORKFLOW (Source of Truth)

### Stage 1: Constitution (WHY - Principles & Constraints)

**File:** `.specify/memory/constitution.md` or `speckit.constitution`

**Purpose:** Defines project non-negotiables and foundational principles

**Contains:**
- Architecture values (e.g., "Functional programming preferred")
- Security rules (e.g., "All inputs must be validated")
- Tech stack constraints (e.g., "Python 3.13+, FastAPI, Next.js 14+")
- Performance expectations (e.g., "API responses < 200ms")
- Allowed patterns (e.g., "No classes in backend storage layer")
- Coding standards (e.g., "TypeScript strict mode required")

**Agent Behavior:**
- Read constitution at start of every session
- Never violate constitutional principles
- Suggest updates if constraints conflict with requirements

**Example:**
```markdown
# Constitution

## Architecture Principles
- Functional programming for backend storage layer (no classes)
- RESTful API design with proper HTTP methods
- Separation of concerns (models, storage, routers)

## Security Rules
- All user inputs must be validated
- Passwords must be hashed with bcrypt
- SQL injection prevention via SQLModel ORM
```

---

### Stage 2: Specify (WHAT - Requirements)

**File:** `specs/features/[feature].md` or `speckit.specify`

**Purpose:** Defines WHAT the system must do (business requirements)

**Contains:**
- User stories and journeys
- Functional requirements
- Acceptance criteria
- Domain rules and business logic
- Business constraints
- Edge cases and error conditions

**Agent Behavior:**
- Never infer missing requirements
- Ask for clarification if acceptance criteria are unclear
- Do not add features not specified here
- Reference specific sections when implementing

**Example:**
```markdown
# Feature Specification: Todo CRUD

## User Story
As a user, I want to create, read, update, and delete todos so I can manage my tasks.

## Acceptance Criteria
- AC1: User can create a todo with title (required) and description (optional)
- AC2: Title must be 1-200 characters
- AC3: Description must be 0-1000 characters
- AC4: User can list all todos with ID, title, description, status
- AC5: User can update todo title and description
- AC6: User can delete todo by ID
- AC7: IDs are never reused

## Edge Cases
- Empty title returns error: "Error: Title cannot be empty."
- Title > 200 chars returns error: "Error: Title exceeds 200 character limit."
```

---

### Stage 3: Plan (HOW - Architecture)

**File:** `specs/[feature]/plan.md` or `speckit.plan`

**Purpose:** Defines HOW the system will be built (technical design)

**Contains:**
- Component breakdown
- API endpoint specifications
- Database schema and relationships
- Service boundaries
- System responsibilities
- High-level sequencing (which components call which)
- File structure and module organization

**Agent Behavior:**
- Follow the plan exactly - no creative reinterpretation
- Do not add components not in the plan
- Suggest plan updates if better approach found (but get approval first)
- Reference specific plan sections in code

**Example:**
```markdown
# Implementation Plan: Todo CRUD

## Component Breakdown

### Backend Components
1. **models.py** - Data validation functions
   - validate_title(title: str) -> (bool, str)
   - validate_description(desc: str) -> (bool, str)

2. **storage.py** - CRUD operations
   - add_todo(title, description) -> (bool, id, message)
   - get_all_todos() -> list[dict]
   - update_todo(id, title, description) -> (bool, message)
   - delete_todo(id) -> (bool, message)

3. **routers/todos.py** - API endpoints
   - POST /api/todos - Create todo
   - GET /api/todos - List todos
   - PUT /api/todos/{id} - Update todo
   - DELETE /api/todos/{id} - Delete todo

## API Specifications

### POST /api/todos
Request:
{
  "title": string (1-200 chars, required),
  "description": string (0-1000 chars, optional)
}

Response (201):
{
  "id": int,
  "title": string,
  "description": string,
  "message": "Todo created successfully"
}
```

---

### Stage 4: Tasks (BREAKDOWN - Atomic Work Units)

**File:** `specs/[feature]/tasks.md` or `speckit.tasks`

**Purpose:** Breaks down plan into implementable atomic tasks

**Each Task Must Contain:**
- **Task ID** - Unique identifier (e.g., T-001, T-002)
- **Clear description** - One sentence summary
- **Preconditions** - What must exist before starting
- **Expected outputs** - What artifacts will be created/modified
- **Artifacts to modify** - Specific files to change
- **Links to specs** - References to Specify and Plan sections
- **Acceptance criteria** - How to verify completion

**Agent Behavior:**
- Only implement tasks that are defined
- Reference Task ID in all code
- Do not skip preconditions
- Verify acceptance criteria before marking complete

**Example:**
```markdown
# Tasks: Todo CRUD

## T-001: Create Todo Validation Functions
**Description:** Implement title and description validation in models.py
**Preconditions:** None
**Artifacts:** backend/app/models.py
**Spec Reference:** speckit.specify §2.1, speckit.plan §1.1
**Acceptance Criteria:**
- validate_title() returns (True, "") for valid titles
- validate_title() returns (False, error) for empty or long titles
- validate_description() returns (True, "") for valid descriptions
- validate_description() returns (False, error) for long descriptions

## T-002: Implement Todo Storage Operations
**Description:** Create CRUD functions in storage.py
**Preconditions:** T-001 complete
**Artifacts:** backend/app/storage.py
**Spec Reference:** speckit.specify §2.1, speckit.plan §1.2
**Acceptance Criteria:**
- add_todo() creates todo and returns ID
- get_all_todos() returns all todos
- update_todo() updates existing todo
- delete_todo() removes todo by ID
```

---

### Stage 5: Implement (CODE - Execute)

**Purpose:** Write code that implements the tasks

**Agents Can Now Write Code, But Must:**
- Reference Task IDs in every file
- Follow the Plan exactly
- Not invent new features or components
- Stop if anything is underspecified
- Validate against acceptance criteria

**Code Template:**
```python
"""
Module: Todo Storage Operations

[Task]: T-002
[Spec]: speckit.specify §2.1 - Todo Management
[Plan]: speckit.plan §1.2 - Storage Layer
[AC]: CRUD operations for todos with validation
"""

def add_todo(title: str, description: str | None) -> tuple[bool, int | None, str]:
    """
    Create a new todo item.

    [Task]: T-002
    [Spec]: speckit.specify §2.1 AC1-AC3

    Args:
        title: Todo title (1-200 chars, required)
        description: Todo description (0-1000 chars, optional)

    Returns:
        (success: bool, todo_id: int | None, message: str)
    """
    # Implementation follows plan §1.2
    ...
```

**Golden Rule:** No task = No code.

---

## 4. AGENT BEHAVIOR IN THIS PROJECT

### When Generating Code

**ALWAYS include these references:**

```python
"""
[Task]: T-003
[From]: speckit.specify §2.1, speckit.plan §3.4
"""
```

### When Proposing Architecture Changes

**STOP and request spec update:**

```
Agent: "The current plan uses in-memory storage, but the requirement
for persistence suggests we need a database.

Required update: speckit.plan §1.2 - Change storage from in-memory to PostgreSQL

Please approve this architectural change before I proceed."
```

### When Proposing New Features

**STOP and request requirements update:**

```
Agent: "I notice we could add email notifications when todos are completed.
However, this is not in the current specification.

Required update: speckit.specify - Add new user story for email notifications

Should I propose this feature, or should we focus on current requirements?"
```

### When Encountering Ambiguity

**STOP and request clarification:**

```
Agent: "The specification says 'users can filter todos' but doesn't specify:
- Filter by what fields? (status, priority, tags?)
- Can multiple filters be combined?
- What's the default filter state?

Please update speckit.specify §3.2 with these details before I implement filtering."
```

---

## 5. AGENT FAILURE MODES (What Agents MUST Avoid)

### ❌ FORBIDDEN: Freestyle Code
```python
# WRONG - No task reference, no spec link
def send_email(user_id, message):
    # Agent invented this feature
    ...
```

### ❌ FORBIDDEN: Architecture Improvisation
```
Agent: "I'll add Redis caching to improve performance"
Problem: Caching not in speckit.plan
```

### ❌ FORBIDDEN: Generating Missing Requirements
```
Agent: "Since the spec doesn't say, I'll assume users want dark mode"
Problem: Requirements must come from speckit.specify, not agent assumptions
```

### ❌ FORBIDDEN: Self-Created Tasks
```
Agent: "I'll break this down into 5 tasks..."
Problem: Tasks must be defined in speckit.tasks first
```

### ❌ FORBIDDEN: Stack Changes Without Justification
```
Agent: "I'll use MongoDB instead of PostgreSQL"
Problem: Stack defined in speckit.constitution
```

### ❌ FORBIDDEN: Undocumented Endpoints
```python
# WRONG - Endpoint not in speckit.plan
@router.post("/api/todos/bulk-delete")
def bulk_delete_todos():
    ...
```

### ❌ FORBIDDEN: Ignoring Acceptance Criteria
```
Agent implements feature but skips edge cases defined in speckit.specify
```

### ❌ FORBIDDEN: Creative Implementations
```
Agent: "The spec says 'validate title length' so I'll add spell-checking too"
Problem: Only implement what's specified
```

---

## 6. SPEC HIERARCHY (Conflict Resolution)

When specs conflict, follow this hierarchy (highest to lowest):

```
1. Constitution      (WHY - Foundational principles)
2. Specify          (WHAT - Requirements)
3. Plan             (HOW - Architecture)
4. Tasks            (BREAKDOWN - Work units)
```

**Example:**
- Constitution says: "No classes allowed"
- Plan says: "Use OOP design pattern"
- **Resolution:** Constitution wins - agent must request plan update

---

## 7. DEVELOPER-AGENT ALIGNMENT

### Collaboration Principles

**Humans and agents collaborate, but the spec is the single source of truth.**

#### Before Every Session
1. Agent reads `.specify/memory/constitution.md`
2. Agent reviews relevant `specs/features/[feature].md`
3. Agent checks `specs/[feature]/plan.md`
4. Agent identifies next task in `specs/[feature]/tasks.md`

#### During Implementation
1. Agent references Task ID in every code block
2. Agent follows plan exactly
3. Agent asks questions if anything is unclear
4. Agent validates against acceptance criteria

#### After Implementation
1. Agent verifies acceptance criteria met
2. Agent documents what was built
3. Agent suggests next task from speckit.tasks
4. Agent updates specs if requirements evolved (with approval)

### Agent-Human Communication

**When Agent Needs Guidance:**
```
"I'm ready to implement [Feature], but I need:
- speckit.specify: Define acceptance criteria for [specific behavior]
- speckit.plan: Clarify how [component X] interacts with [component Y]
- speckit.tasks: Break down the work into atomic tasks

Please provide these before I proceed with implementation."
```

**When Agent Finds Inconsistency:**
```
"I found a conflict:
- speckit.specify §2.1 says: [requirement A]
- speckit.plan §3.4 says: [different approach B]

Please resolve this conflict before I implement."
```

**When Agent Completes Work:**
```
"Task T-003 completed:
✅ All acceptance criteria met
✅ Code references Task ID and specs
✅ Tests passing
✅ No spec violations

Ready for next task: T-004 [description]"
```

---

## 8. QUALITY CHECKLIST FOR AGENTS

Before submitting any code, agents must verify:

- [ ] Task ID referenced in code comments
- [ ] Links to speckit.specify and speckit.plan included
- [ ] No features added beyond specification
- [ ] No architecture changes without plan update
- [ ] All acceptance criteria met
- [ ] Edge cases handled per spec
- [ ] Error messages match spec format
- [ ] No tech stack deviations from constitution
- [ ] Tests written and passing
- [ ] Documentation updated if needed

---

## 9. AGENT SPECIALIZATION (Phase 2 Web App)

### Available Specialized Agents

This project uses specialized agents for different tasks. Each agent has specific responsibilities but **all must follow spec-driven development**.

#### 1. **spec-writer**
- **Purpose:** Create and update specifications
- **Files:** `specs/features/*.md`, `specs/api/*.md`, `specs/database/*.md`
- **Constraints:** Must follow SpecKit Plus templates

#### 2. **fastapi-developer**
- **Purpose:** Implement backend API endpoints
- **Files:** `backend/app/*.py`
- **Constraints:** Must reference specs, use SQLModel, follow FastAPI patterns

#### 3. **nextjs-developer**
- **Purpose:** Implement frontend components and pages
- **Files:** `frontend/src/**/*.tsx`
- **Constraints:** Must use TypeScript, Tailwind CSS, Next.js App Router

#### 4. **auth-specialist**
- **Purpose:** Implement authentication and authorization
- **Files:** `backend/app/auth.py`, `frontend/src/lib/auth.ts`
- **Constraints:** Must use Better Auth, secure patterns

#### 5. **fullstack-architect**
- **Purpose:** Design system architecture and integration
- **Files:** `specs/*/plan.md`
- **Constraints:** Must ensure frontend-backend consistency

**All agents must:**
- Follow the Spec-Kit lifecycle
- Reference Task IDs
- Never improvise features
- Stop if specs are missing

---

## 10. ENFORCEMENT

### How This Document is Enforced

1. **Agent Prompts:** All agents receive this document in their context
2. **Code Review:** Human reviews check for spec references
3. **Quality Gates:** CI/CD validates Task IDs in code
4. **Constitution Check:** Automated checks for principle violations

### What Happens When Agents Violate Rules

1. **Code without Task ID** → Rejected, must add reference
2. **Feature not in spec** → Stopped, must update spec first
3. **Architecture deviation** → Rejected, must update plan
4. **Missing acceptance criteria** → Cannot proceed, must define criteria

---

## Summary: The Agent Contract

By working on this project, AI agents agree to:

1. ✅ **Read specs first** - Never code without reading relevant specs
2. ✅ **Reference Task IDs** - Every code block links to a task
3. ✅ **Follow the plan** - No creative reinterpretation
4. ✅ **Stop when unclear** - Request clarification, never improvise
5. ✅ **Respect hierarchy** - Constitution > Specify > Plan > Tasks
6. ✅ **Validate completion** - Check acceptance criteria
7. ✅ **Document everything** - Link code to specs
8. ✅ **No freelancing** - Only implement what's specified

**Remember:** In spec-driven development, the agent's job is to **execute the spec perfectly**, not to invent features or architecture.

---

**Project:** Phase II - Full-Stack Web Application
**Framework:** SpecKit Plus
**Last Updated:** 2025-12-31
**Compliance:** Mandatory for all AI agents
