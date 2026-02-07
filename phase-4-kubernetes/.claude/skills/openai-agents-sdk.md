# Skill: OpenAI Agents SDK with MCP Tools

## Description
Implement OpenAI Agents using the Agents SDK with Model Context Protocol (MCP) tools for building AI-powered conversational interfaces that can interact with TODO management features.

## When to Use
- Building AI agents that need to call external tools/functions
- Implementing conversational AI with access to backend APIs
- Creating chatbots that can perform actions (CRUD operations)
- Integrating OpenAI models with MCP tool ecosystem
- Managing multi-turn conversations with tool execution

## Prerequisites
- OpenAI API key configured in environment
- AsyncOpenAI client installed (`openai` package)
- MCP tools registered and available
- PostgreSQL database for conversation history
- Understanding of async/await patterns in Python

---

## Core Concepts

### OpenAI Agents SDK
The OpenAI Agents SDK allows you to create AI agents that can:
- Understand natural language requests
- Decide when to use tools/functions
- Execute tools and process results
- Maintain conversation context
- Generate responses based on tool outputs

### Model Context Protocol (MCP)
MCP tools are standardized functions that the agent can call:
- Todo management (create, read, update, delete)
- Search and filtering
- Priority and tag management
- User preferences
- Analytics and insights

---

## Setup

### 1. Install Dependencies

```python
# requirements.txt
openai>=1.50.0
pydantic>=2.0.0
sqlalchemy>=2.0.0
asyncpg>=0.29.0  # For async PostgreSQL
python-dotenv>=1.0.0
```

```bash
# Install with UV
uv add openai pydantic sqlalchemy asyncpg python-dotenv

# Or with pip
pip install openai pydantic sqlalchemy asyncpg python-dotenv
```

### 2. Environment Configuration

```python
# .env
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-2024-08-06  # or gpt-4o-mini for lower cost
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0.7
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
```

### 3. Project Structure

```
backend/
├── agents/
│   ├── __init__.py
│   ├── openai_agent.py      # Main agent implementation
│   ├── tools.py              # MCP tool definitions
│   ├── prompts.py            # System prompts
│   └── context.py            # Conversation context management
├── routes/
│   └── chat.py               # Chat API endpoints
└── models/
    └── conversation.py       # DB models for chat history
```

---

## Implementation

### 1. Agent Initialization

```python
# agents/openai_agent.py
import os
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class AgentConfig(BaseModel):
    """Configuration for OpenAI Agent"""
    model: str = "gpt-4o-2024-08-06"
    max_tokens: int = 4096
    temperature: float = 0.7
    max_history: int = 20  # Limit conversation history
    max_retries: int = 3
    timeout: int = 60

class OpenAIAgent:
    """
    OpenAI Agent with MCP tools integration.

    Features:
    - Async/await for all operations
    - Tool calling with automatic execution
    - Conversation history management
    - Error handling and retries
    - Cost tracking
    """

    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        system_prompt: Optional[str] = None
    ):
        """
        Initialize OpenAI Agent.

        Args:
            config: Agent configuration
            system_prompt: System prompt for agent behavior
        """
        self.config = config or AgentConfig()
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.tools = []  # MCP tools will be registered here

    def _default_system_prompt(self) -> str:
        """Default system prompt for TODO assistant"""
        return """You are an AI assistant for a TODO management application.

Your capabilities:
- Create, read, update, and delete TODO tasks
- Search and filter tasks by various criteria
- Manage task priorities (high, medium, low)
- Add and manage tags
- Set due dates and recurring tasks
- Provide task analytics and insights

Your behavior:
- Be concise and helpful
- Confirm actions before executing them
- Ask for clarification when needed
- Provide clear feedback on task operations
- Suggest optimizations for task management
- Handle errors gracefully and explain issues

When a user asks to create/update/delete tasks:
1. Extract all relevant information
2. Use the appropriate tool to perform the action
3. Confirm the action was successful
4. Provide a summary of what was done

Always prioritize user intent and provide actionable responses."""

    async def register_tools(self, tools: List[Dict[str, Any]]):
        """
        Register MCP tools with the agent.

        Args:
            tools: List of OpenAI function tool definitions
        """
        self.tools = tools
        logger.info(f"Registered {len(tools)} tools with agent")
```

### 2. System Prompts

```python
# agents/prompts.py

TODO_ASSISTANT_PROMPT = """You are an intelligent TODO management assistant.

## Your Role
Help users manage their tasks efficiently through natural conversation.

## Available Tools
You have access to these tools (use them wisely):
- create_task: Create a new TODO task
- get_tasks: Retrieve tasks with optional filters
- update_task: Update an existing task
- delete_task: Delete a task
- search_tasks: Search tasks by keyword
- get_task_analytics: Get insights about tasks

## Guidelines

### When Creating Tasks:
- Extract title, description, priority, tags, and due date from user input
- If information is missing, ask for clarification
- Set reasonable defaults (priority: medium, no due date unless specified)
- Confirm creation with a summary

### When Searching/Filtering:
- Use appropriate filters (status, priority, tags, date range)
- Present results in a clear, organized format
- Offer to perform actions on the results

### When Updating Tasks:
- Confirm which task to update
- Ask what to change if not clear
- Validate the changes make sense
- Provide before/after summary

### When Deleting Tasks:
- Always confirm before deletion
- Be extra careful with bulk deletions
- Explain what will be deleted

### Error Handling:
- If a tool fails, explain the error in user-friendly terms
- Suggest alternatives or next steps
- Never expose technical error details

### Conversation:
- Be friendly but professional
- Keep responses concise
- Use bullet points for lists
- Use emojis sparingly (✅ ❌ 🎯 📅)

## Response Format
Always structure your responses:
1. Acknowledge the request
2. Execute the action (using tools)
3. Confirm the result
4. Offer next steps (optional)

Example:
User: "Create a task to finish the report by Friday"
You: "I'll create that task for you. ✅

Created: "Finish the report"
- Due: Friday, Jan 12, 2026
- Priority: Medium
- Status: Ready

Would you like me to set a reminder or add any tags?"
"""

MULTI_TURN_SYSTEM_PROMPT = """You are a TODO assistant maintaining context across conversation.

## Context Awareness
- Remember previous messages in this conversation
- Reference earlier tasks and actions
- Build on previous clarifications
- Don't ask for information already provided

## Context Management
- Summarize long conversations periodically
- Track tasks mentioned in the conversation
- Remember user preferences (default priority, tags, etc.)
- Note recurring patterns in user requests

## Examples

Turn 1:
User: "I need to prepare for the meeting"
You: "I'll help you prepare. What meeting is this for, and when is it?"

Turn 2:
User: "The client presentation next Tuesday"
You: [Use context from turn 1] "Got it! I'll create a task for the client presentation next Tuesday.
Should I set the priority to high since it's a client meeting?"

Turn 3:
User: "Yes, and add a tag for 'client-work'"
You: [Use context from turns 1-2] "Perfect! ✅

Created: "Prepare for client presentation"
- Due: Tuesday, Jan 16, 2026
- Priority: High
- Tags: client-work
- Status: Ready

Would you like me to create any sub-tasks to help you prepare?"
"""
```

### 3. MCP Tool Definitions

```python
# agents/tools.py
from typing import List, Dict, Any

def get_mcp_tools() -> List[Dict[str, Any]]:
    """
    Define MCP tools in OpenAI function calling format.

    Returns:
        List of tool definitions
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "create_task",
                "description": "Create a new TODO task. Use this when the user wants to add a task to their list.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The task title (required, concise)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed description of the task (optional)"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                            "description": "Task priority level (default: medium)"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tags for categorizing the task (optional)"
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Due date in ISO format YYYY-MM-DD (optional)"
                        },
                        "recurrence": {
                            "type": "string",
                            "enum": ["none", "daily", "weekly", "monthly"],
                            "description": "Recurrence pattern (default: none)"
                        }
                    },
                    "required": ["title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_tasks",
                "description": "Retrieve TODO tasks with optional filters. Use this to list, view, or filter tasks.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["ready", "in_progress", "review", "done"],
                            "description": "Filter by task status"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                            "description": "Filter by priority"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by tags (any match)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of tasks to return (default: 20)"
                        },
                        "sort_by": {
                            "type": "string",
                            "enum": ["created", "updated", "due_date", "priority", "title"],
                            "description": "Sort field (default: created)"
                        },
                        "sort_order": {
                            "type": "string",
                            "enum": ["asc", "desc"],
                            "description": "Sort order (default: desc)"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update an existing TODO task. Use this to modify task properties.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "New title for the task"
                        },
                        "description": {
                            "type": "string",
                            "description": "New description"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["ready", "in_progress", "review", "done"]
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high"]
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Due date in ISO format YYYY-MM-DD"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Delete a TODO task permanently. Use with caution and confirm with user.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to delete"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_tasks",
                "description": "Search tasks by keyword in title or description. Use for flexible text search.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (matches title and description)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum results (default: 20)"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_task_analytics",
                "description": "Get analytics and insights about tasks. Use for reporting and statistics.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date_from": {
                            "type": "string",
                            "description": "Start date in ISO format (optional)"
                        },
                        "date_to": {
                            "type": "string",
                            "description": "End date in ISO format (optional)"
                        }
                    },
                    "required": []
                }
            }
        }
    ]
```

### 4. Running Agent with Tool Calls

```python
# agents/openai_agent.py (continued)

import json
from typing import List, Dict, Any, Optional, Tuple

class OpenAIAgent:
    # ... (previous code)

    async def run(
        self,
        messages: List[Dict[str, str]],
        user_id: int,
        max_iterations: int = 5
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Run the agent with conversation messages and handle tool calls.

        Args:
            messages: Conversation history [{"role": "user", "content": "..."}]
            user_id: User ID for tool execution context
            max_iterations: Maximum tool call iterations (prevent infinite loops)

        Returns:
            Tuple of (final_response, tool_calls_executed)
        """
        # Prepare messages with system prompt
        full_messages = [
            {"role": "system", "content": self.system_prompt}
        ] + messages[-self.config.max_history:]  # Limit history

        tool_calls_log = []
        iteration = 0

        try:
            while iteration < max_iterations:
                iteration += 1
                logger.info(f"Agent iteration {iteration}/{max_iterations}")

                # Call OpenAI API
                response = await self.client.chat.completions.create(
                    model=self.config.model,
                    messages=full_messages,
                    tools=self.tools if self.tools else None,
                    tool_choice="auto",  # Let model decide when to use tools
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens
                )

                message = response.choices[0].message

                # Check if model wants to call tools
                if message.tool_calls:
                    logger.info(f"Agent requested {len(message.tool_calls)} tool calls")

                    # Add assistant message with tool calls to history
                    full_messages.append({
                        "role": "assistant",
                        "content": message.content or "",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            }
                            for tc in message.tool_calls
                        ]
                    })

                    # Execute tool calls
                    for tool_call in message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)

                        logger.info(f"Executing tool: {tool_name} with args: {tool_args}")

                        try:
                            # Execute the tool
                            tool_result = await self._execute_tool(
                                tool_name,
                                tool_args,
                                user_id
                            )

                            # Log tool execution
                            tool_calls_log.append({
                                "tool": tool_name,
                                "args": tool_args,
                                "result": tool_result,
                                "success": True
                            })

                            # Add tool result to messages
                            full_messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps(tool_result)
                            })

                        except Exception as e:
                            logger.error(f"Tool execution failed: {tool_name} - {e}")

                            # Log failure
                            tool_calls_log.append({
                                "tool": tool_name,
                                "args": tool_args,
                                "error": str(e),
                                "success": False
                            })

                            # Add error to messages
                            full_messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps({
                                    "error": str(e),
                                    "message": "Tool execution failed"
                                })
                            })

                    # Continue loop to get final response after tool execution
                    continue

                else:
                    # No more tool calls, return final response
                    final_response = message.content or "I couldn't generate a response."
                    logger.info(f"Agent completed in {iteration} iterations")
                    return final_response, tool_calls_log

            # Max iterations reached
            logger.warning(f"Max iterations ({max_iterations}) reached")
            return (
                "I've completed the maximum number of steps. Please try breaking down your request.",
                tool_calls_log
            )

        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            raise

    async def _execute_tool(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        user_id: int
    ) -> Dict[str, Any]:
        """
        Execute a tool and return results.

        Args:
            tool_name: Name of the tool to execute
            tool_args: Tool arguments
            user_id: User ID for context

        Returns:
            Tool execution result
        """
        # Import tool executors
        from .tool_executors import execute_tool

        # Add user_id to tool context
        tool_context = {"user_id": user_id}

        # Execute tool
        result = await execute_tool(tool_name, tool_args, tool_context)

        return result
```

### 5. Tool Executors

```python
# agents/tool_executors.py
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.crud import (
    create_todo,
    get_todos,
    update_todo,
    delete_todo,
    search_todos,
    get_analytics
)

async def execute_tool(
    tool_name: str,
    tool_args: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a tool with given arguments.

    Args:
        tool_name: Name of tool to execute
        tool_args: Tool arguments
        context: Execution context (user_id, etc.)

    Returns:
        Tool execution result
    """
    user_id = context["user_id"]

    # Get database session
    async for db in get_db():
        try:
            if tool_name == "create_task":
                result = await create_todo(
                    db,
                    user_id=user_id,
                    title=tool_args["title"],
                    description=tool_args.get("description"),
                    priority=tool_args.get("priority", "medium"),
                    tags=tool_args.get("tags", []),
                    due_date=tool_args.get("due_date"),
                    recurrence=tool_args.get("recurrence", "none")
                )
                return {
                    "success": True,
                    "task_id": result.id,
                    "message": f"Created task: {result.title}"
                }

            elif tool_name == "get_tasks":
                tasks = await get_todos(
                    db,
                    user_id=user_id,
                    status=tool_args.get("status"),
                    priority=tool_args.get("priority"),
                    tags=tool_args.get("tags"),
                    limit=tool_args.get("limit", 20),
                    sort_by=tool_args.get("sort_by", "created"),
                    sort_order=tool_args.get("sort_order", "desc")
                )
                return {
                    "success": True,
                    "count": len(tasks),
                    "tasks": [
                        {
                            "id": t.id,
                            "title": t.title,
                            "status": t.status,
                            "priority": t.priority,
                            "tags": t.tags,
                            "due_date": str(t.due_date) if t.due_date else None
                        }
                        for t in tasks
                    ]
                }

            elif tool_name == "update_task":
                task_id = tool_args.pop("task_id")
                result = await update_todo(db, task_id, user_id, **tool_args)
                return {
                    "success": True,
                    "task_id": result.id,
                    "message": f"Updated task: {result.title}"
                }

            elif tool_name == "delete_task":
                await delete_todo(db, tool_args["task_id"], user_id)
                return {
                    "success": True,
                    "message": "Task deleted successfully"
                }

            elif tool_name == "search_tasks":
                tasks = await search_todos(
                    db,
                    user_id=user_id,
                    query=tool_args["query"],
                    limit=tool_args.get("limit", 20)
                )
                return {
                    "success": True,
                    "count": len(tasks),
                    "tasks": [
                        {
                            "id": t.id,
                            "title": t.title,
                            "description": t.description,
                            "priority": t.priority
                        }
                        for t in tasks
                    ]
                }

            elif tool_name == "get_task_analytics":
                analytics = await get_analytics(
                    db,
                    user_id=user_id,
                    date_from=tool_args.get("date_from"),
                    date_to=tool_args.get("date_to")
                )
                return {
                    "success": True,
                    "analytics": analytics
                }

            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            await db.close()
```

### 6. Conversation Context Management

```python
# agents/context.py
from typing import List, Dict, Any, Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.database import Base

class Conversation(Base):
    """Database model for storing conversations"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Message(Base):
    """Database model for storing messages"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system, tool
    content = Column(Text)
    tool_calls = Column(JSONB)  # Store tool calls if any
    metadata = Column(JSONB)  # Additional metadata
    created_at = Column(DateTime, default=datetime.utcnow)

class ConversationManager:
    """Manage conversation history in database"""

    @staticmethod
    async def create_conversation(
        db: AsyncSession,
        user_id: int,
        title: Optional[str] = None
    ) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(
            user_id=user_id,
            title=title or f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        return conversation

    @staticmethod
    async def add_message(
        db: AsyncSession,
        conversation_id: int,
        role: str,
        content: str,
        tool_calls: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None
    ) -> Message:
        """Add a message to conversation"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            metadata=metadata
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message

    @staticmethod
    async def get_conversation_messages(
        db: AsyncSession,
        conversation_id: int,
        limit: int = 50
    ) -> List[Message]:
        """Get conversation messages"""
        from sqlalchemy import select

        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        messages = result.scalars().all()
        return list(reversed(messages))  # Oldest first

    @staticmethod
    def messages_to_openai_format(messages: List[Message]) -> List[Dict[str, Any]]:
        """Convert DB messages to OpenAI format"""
        return [
            {
                "role": msg.role,
                "content": msg.content or "",
                **({"tool_calls": msg.tool_calls} if msg.tool_calls else {})
            }
            for msg in messages
        ]
```

### 7. Error Handling

```python
# agents/errors.py
import asyncio
from typing import Callable, Any
from openai import (
    RateLimitError,
    APIError,
    APITimeoutError,
    APIConnectionError
)
import logging

logger = logging.getLogger(__name__)

class AgentError(Exception):
    """Base exception for agent errors"""
    pass

class ToolExecutionError(AgentError):
    """Tool execution failed"""
    pass

class RateLimitExceeded(AgentError):
    """OpenAI rate limit exceeded"""
    pass

async def retry_with_exponential_backoff(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0
) -> Any:
    """
    Retry a function with exponential backoff.

    Args:
        func: Async function to retry
        max_retries: Maximum number of retries
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Exponential base for backoff

    Returns:
        Function result

    Raises:
        Last exception if all retries fail
    """
    delay = initial_delay

    for attempt in range(max_retries):
        try:
            return await func()
        except RateLimitError as e:
            if attempt == max_retries - 1:
                logger.error(f"Rate limit exceeded after {max_retries} attempts")
                raise RateLimitExceeded("OpenAI rate limit exceeded") from e

            logger.warning(f"Rate limit hit, retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
            await asyncio.sleep(delay)
            delay = min(delay * exponential_base, max_delay)

        except (APITimeoutError, APIConnectionError) as e:
            if attempt == max_retries - 1:
                logger.error(f"Connection failed after {max_retries} attempts")
                raise AgentError("Failed to connect to OpenAI") from e

            logger.warning(f"Connection error, retrying in {delay}s...")
            await asyncio.sleep(delay)
            delay = min(delay * exponential_base, max_delay)

        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise AgentError(f"OpenAI API error: {str(e)}") from e

    raise AgentError("Max retries exceeded")

def handle_agent_errors(func: Callable) -> Callable:
    """Decorator for handling agent errors"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except RateLimitExceeded:
            return {
                "error": "rate_limit",
                "message": "Too many requests. Please try again in a moment."
            }
        except ToolExecutionError as e:
            return {
                "error": "tool_error",
                "message": f"Failed to execute action: {str(e)}"
            }
        except AgentError as e:
            return {
                "error": "agent_error",
                "message": str(e)
            }
        except Exception as e:
            logger.exception("Unexpected error in agent")
            return {
                "error": "internal_error",
                "message": "An unexpected error occurred. Please try again."
            }

    return wrapper
```

### 8. API Endpoints

```python
# routes/chat.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth import get_current_user
from agents.openai_agent import OpenAIAgent, AgentConfig
from agents.tools import get_mcp_tools
from agents.prompts import TODO_ASSISTANT_PROMPT
from agents.context import ConversationManager
from agents.errors import handle_agent_errors

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: int
    tool_calls: List[dict] = []

@router.post("/", response_model=ChatResponse)
@handle_agent_errors
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Chat with AI agent.

    - Creates new conversation if conversation_id not provided
    - Retrieves conversation history from database
    - Runs agent with tools
    - Stores messages in database
    """
    # Get or create conversation
    if request.conversation_id:
        conversation_id = request.conversation_id
        # Verify user owns this conversation
        # ... (add verification logic)
    else:
        conversation = await ConversationManager.create_conversation(
            db,
            user_id=current_user.id
        )
        conversation_id = conversation.id

    # Store user message
    await ConversationManager.add_message(
        db,
        conversation_id=conversation_id,
        role="user",
        content=request.message
    )

    # Get conversation history
    messages_db = await ConversationManager.get_conversation_messages(
        db,
        conversation_id=conversation_id,
        limit=20  # Limit history
    )
    messages = ConversationManager.messages_to_openai_format(messages_db)

    # Initialize agent
    config = AgentConfig(
        model="gpt-4o-2024-08-06",
        temperature=0.7,
        max_tokens=4096
    )
    agent = OpenAIAgent(config=config, system_prompt=TODO_ASSISTANT_PROMPT)

    # Register tools
    tools = get_mcp_tools()
    await agent.register_tools(tools)

    # Run agent
    response, tool_calls = await agent.run(
        messages=messages,
        user_id=current_user.id,
        max_iterations=5
    )

    # Store assistant response
    await ConversationManager.add_message(
        db,
        conversation_id=conversation_id,
        role="assistant",
        content=response,
        tool_calls=tool_calls if tool_calls else None
    )

    return ChatResponse(
        response=response,
        conversation_id=conversation_id,
        tool_calls=tool_calls
    )

@router.get("/conversations")
async def get_conversations(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get user's conversations"""
    from sqlalchemy import select
    from agents.context import Conversation

    query = (
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
    )
    result = await db.execute(query)
    conversations = result.scalars().all()

    return [
        {
            "id": conv.id,
            "title": conv.title,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at
        }
        for conv in conversations
    ]

@router.get("/conversations/{conversation_id}/messages")
async def get_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get conversation messages"""
    messages = await ConversationManager.get_conversation_messages(
        db,
        conversation_id=conversation_id
    )

    return [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "tool_calls": msg.tool_calls,
            "created_at": msg.created_at
        }
        for msg in messages
    ]
```

---

## Best Practices

### 1. System Prompts
```python
# ✅ Good: Clear, specific, actionable
"""You are a TODO assistant. Create tasks when requested.
Ask for clarification if details are missing. Confirm actions."""

# ❌ Bad: Vague, generic
"""You are a helpful assistant. Help the user."""
```

### 2. Tool Descriptions
```python
# ✅ Good: Clear when to use
"Create a new TODO task. Use this when the user wants to add a task."

# ❌ Bad: Unclear usage
"Manages tasks in the system"
```

### 3. Conversation History
```python
# ✅ Good: Limit history to avoid token limits
messages = messages[-20:]  # Last 20 messages

# ❌ Bad: Unlimited history (can exceed context window)
messages = all_messages
```

### 4. Error Messages
```python
# ✅ Good: User-friendly
"I couldn't create that task because the title is too long. Please use fewer than 200 characters."

# ❌ Bad: Technical
"ValidationError: title exceeds max_length constraint"
```

### 5. Cost Management
```python
# Monitor token usage
response = await client.chat.completions.create(...)
tokens_used = response.usage.total_tokens
cost = tokens_used * COST_PER_TOKEN

# Use cheaper model for simple tasks
if is_simple_query:
    model = "gpt-4o-mini"  # Lower cost
else:
    model = "gpt-4o"  # More capable
```

### 6. Rate Limit Handling
```python
# ✅ Good: Exponential backoff with retries
result = await retry_with_exponential_backoff(
    lambda: agent.run(messages),
    max_retries=3
)

# ❌ Bad: No retry logic
result = await agent.run(messages)  # Fails on rate limit
```

---

## Testing

### Unit Tests

```python
# tests/test_agent.py
import pytest
from agents.openai_agent import OpenAIAgent, AgentConfig
from agents.tools import get_mcp_tools

@pytest.mark.asyncio
async def test_agent_initialization():
    """Test agent initialization"""
    config = AgentConfig(model="gpt-4o-mini")
    agent = OpenAIAgent(config=config)

    assert agent.config.model == "gpt-4o-mini"
    assert agent.client is not None
    assert agent.system_prompt is not None

@pytest.mark.asyncio
async def test_tool_registration():
    """Test tool registration"""
    agent = OpenAIAgent()
    tools = get_mcp_tools()

    await agent.register_tools(tools)

    assert len(agent.tools) == 6
    assert agent.tools[0]["function"]["name"] == "create_task"

@pytest.mark.asyncio
async def test_agent_simple_response():
    """Test agent response without tool calls"""
    agent = OpenAIAgent()

    messages = [
        {"role": "user", "content": "Hello!"}
    ]

    response, tool_calls = await agent.run(messages, user_id=1)

    assert isinstance(response, str)
    assert len(response) > 0
    assert len(tool_calls) == 0

@pytest.mark.asyncio
async def test_agent_with_tool_call(mock_tool_executor):
    """Test agent with tool execution"""
    agent = OpenAIAgent()
    tools = get_mcp_tools()
    await agent.register_tools(tools)

    messages = [
        {"role": "user", "content": "Create a task to write tests"}
    ]

    response, tool_calls = await agent.run(messages, user_id=1)

    assert isinstance(response, str)
    assert len(tool_calls) > 0
    assert tool_calls[0]["tool"] == "create_task"
    assert tool_calls[0]["success"] is True
```

---

## Deployment Checklist

- [ ] Environment variables configured (OPENAI_API_KEY)
- [ ] Database migrations applied (conversations, messages tables)
- [ ] Rate limit handling implemented
- [ ] Error handling and retries configured
- [ ] Cost monitoring enabled
- [ ] Conversation history limits set
- [ ] Tool execution permissions verified
- [ ] API endpoints secured with authentication
- [ ] Logging configured for debugging
- [ ] Testing completed (unit + integration)

---

## Common Issues

### Issue: "Rate limit exceeded"
**Solution:** Implement exponential backoff with retries (see Error Handling section)

### Issue: "Context length exceeded"
**Solution:** Limit conversation history to last 20-30 messages

### Issue: "Tool execution failed"
**Solution:** Add proper error handling in tool executors and return descriptive errors

### Issue: "Agent makes too many tool calls"
**Solution:** Set `max_iterations` parameter to limit loops (default: 5)

### Issue: "Responses are slow"
**Solution:** Use `gpt-4o-mini` for simpler queries, implement streaming responses

---

## Resources

- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Best Practices for Agents](https://platform.openai.com/docs/guides/best-practices)
- [OpenAI Rate Limits](https://platform.openai.com/docs/guides/rate-limits)

---

**Last Updated:** 2026-01-12
**Skill Version:** 1.0.0
**Recommended For:** Phase 3 AI Chatbot Development
