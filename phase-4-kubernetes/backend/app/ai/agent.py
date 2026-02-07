"""
Phase III: OpenAI Agent Integration

This module implements the TodoAgent class for AI-powered task management through natural
language conversations.

ARCHITECTURE:
- Uses AsyncOpenAI client for async API calls
- Integrates with MCP tools for task operations
- Supports multi-turn conversations (max 5 iterations)
- Stateless: All conversation state stored in database
- User isolation: user_id passed to all MCP tools

WORKFLOW:
1. Receive conversation messages from chat endpoint
2. Add system prompt to message array
3. Call OpenAI API with tools (MCP tools)
4. Process tool calls (if any)
5. Execute MCP tools with user_id
6. Add tool results to message array
7. Continue until final response or max iterations
8. Return final assistant response

Author: Claude Code
Date: 2026-01-13
Version: 1.0.0
"""

from typing import List, Dict, Any, Optional
import os
import json
import logging

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageToolCall

from app.mcp.server import (
    add_task,
    list_tasks,
    update_task,
    complete_task,
    delete_task,
)

# Setup logging
logger = logging.getLogger(__name__)


# System prompt for TODO assistant
TODO_ASSISTANT_SYSTEM_PROMPT = """
You are a helpful TODO task assistant. You help users manage their tasks through natural language conversations.

Available MCP Tools:
1. add_task(user_id, title, description, priority, tags, due_date) - Create new task
   - Use when user wants to add/create a task
   - Extract details from user's message (title, priority, due date, tags)

2. list_tasks(user_id, status, priority, tags, limit) - Retrieve tasks with filters
   - Use when user wants to see/view/list their tasks
   - Apply filters based on user's request (completed, pending, high priority, etc.)

3. update_task(user_id, task_id, title, description, status, priority) - Update existing task
   - Use when user wants to change/modify a task
   - Only update fields mentioned by user

4. complete_task(user_id, task_id) - Mark task as completed
   - Use when user wants to finish/complete/mark done a task

5. delete_task(user_id, task_id) - Delete task permanently
   - Use when user wants to remove/delete a task
   - Confirm before deleting

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

Example Interactions:
User: "Create a task for client presentation tomorrow"
You: "I'll create that for you. ✅

Created: "Client presentation"
- Priority: Medium
- Due: Tomorrow
- Status: Ready

Would you like to set this as high priority or add any notes?"

User: "Show me my high priority tasks"
You: "Here are your high priority tasks: 🎯

1. Client presentation - Due tomorrow
2. Finish Q4 report - Due in 3 days

Both are pending. Want to complete any of these?"
"""


class TodoAgent:
    """
    OpenAI agent for todo task management.

    Features:
    - Async OpenAI API integration
    - Multi-turn tool calling (max 5 iterations)
    - MCP tool integration with all 5 tools
    - Error handling for API failures
    - User isolation (user_id passed to all tools)
    - Stateless architecture
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize TodoAgent with OpenAI API key.

        Args:
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)

        Raises:
            ValueError: If API key not provided and not in environment
        """
        # Import settings here to avoid circular imports
        from app.config import settings

        self.api_key = api_key or settings.openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable."
            )

        # Initialize AsyncOpenAI client
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = settings.openai_model or os.getenv("OPENAI_MODEL", "gpt-4o")

        # Register MCP tools
        self.tool_functions = {
            "add_task": add_task,
            "list_tasks": list_tasks,
            "update_task": update_task,
            "complete_task": complete_task,
            "delete_task": delete_task,
        }

        # Define tools for OpenAI function calling
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Create a new TODO task. Use when user wants to add/create a task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "User ID from JWT authentication"},
                            "title": {"type": "string", "description": "Task title (required)"},
                            "description": {"type": "string", "description": "Task description (optional)"},
                            "priority": {"type": "string", "enum": ["Low", "Medium", "High"], "description": "Task priority"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Task tags"},
                            "due_date": {"type": "string", "description": "Due date in ISO 8601 format"},
                        },
                        "required": ["user_id", "title"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "Retrieve tasks with optional filters. Use when user wants to see/list their tasks.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "User ID from JWT authentication"},
                            "status": {"type": "string", "enum": ["pending", "completed"], "description": "Filter by status"},
                            "priority": {"type": "string", "enum": ["Low", "Medium", "High"], "description": "Filter by priority"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Filter by tags"},
                            "limit": {"type": "integer", "description": "Maximum number of tasks to return"},
                        },
                        "required": ["user_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update an existing task. Only provided fields are updated.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "User ID from JWT authentication"},
                            "task_id": {"type": "string", "description": "Task ID to update"},
                            "title": {"type": "string", "description": "New task title"},
                            "description": {"type": "string", "description": "New task description"},
                            "status": {"type": "string", "enum": ["ready", "in_progress", "done"], "description": "New task status"},
                            "priority": {"type": "string", "enum": ["Low", "Medium", "High"], "description": "New task priority"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "New task tags"},
                            "due_date": {"type": "string", "description": "New due date in ISO 8601 format"},
                        },
                        "required": ["user_id", "task_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Mark a task as completed. Use when user wants to finish/complete/mark done a task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "User ID from JWT authentication"},
                            "task_id": {"type": "string", "description": "Task ID to mark as completed"},
                        },
                        "required": ["user_id", "task_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Delete a task permanently. Use when user explicitly wants to remove/delete a task.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "description": "User ID from JWT authentication"},
                            "task_id": {"type": "string", "description": "Task ID to delete permanently"},
                        },
                        "required": ["user_id", "task_id"],
                    },
                },
            },
        ]

        logger.info(f"TodoAgent initialized with model: {self.model}")

    async def run(
        self,
        messages: List[Dict[str, str]],
        user_id: str,
        max_iterations: int = 5
    ) -> str:
        """
        Run agent with conversation messages and tool calling.

        This implements the multi-turn tool calling loop:
        1. Call OpenAI API with messages and tools
        2. If agent wants to call tools, execute them
        3. Add tool results to messages
        4. Repeat until agent returns final response or max iterations reached

        Args:
            messages: Conversation message history (including system prompt and user messages)
            user_id: User ID for tool calls (CRITICAL: passed to ALL tool calls)
            max_iterations: Maximum tool calling iterations (default: 5)

        Returns:
            Final assistant response text

        Raises:
            Exception: If OpenAI API call fails after retries
        """
        current_messages = messages.copy()
        iterations = 0

        logger.info(f"Starting agent run for user_id={user_id}, max_iterations={max_iterations}")

        while iterations < max_iterations:
            iterations += 1
            logger.debug(f"Agent iteration {iterations}/{max_iterations}")

            try:
                # Call OpenAI API with tools
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=current_messages,
                    tools=self.tools,
                    tool_choice="auto",
                )

                message = response.choices[0].message
                logger.debug(f"OpenAI response: {message.model_dump()}")

                # Add assistant message to conversation
                current_messages.append({
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": [tc.model_dump() for tc in message.tool_calls] if message.tool_calls else None,
                })

                # Check if agent wants to call tools
                if message.tool_calls:
                    logger.info(f"Agent requesting {len(message.tool_calls)} tool calls")

                    # Execute each tool call
                    for tool_call in message.tool_calls:
                        tool_result = await self._execute_tool_call(
                            tool_call, user_id
                        )

                        # Add tool result to messages
                        current_messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(tool_result),
                        })

                    # Continue loop to get final response after tool execution
                    continue

                # No tool calls - agent has final response
                logger.info("Agent returned final response")
                return message.content or "I apologize, but I couldn't complete your request."

            except Exception as e:
                logger.error(f"Error in agent run: {e}", exc_info=True)
                raise Exception(f"OpenAI API error: {str(e)}")

        # Max iterations reached without final response
        logger.warning(f"Max iterations ({max_iterations}) reached")
        return "I apologize, but I couldn't complete your request within the allowed time. Please try again or rephrase your request."

    async def _execute_tool_call(
        self,
        tool_call: ChatCompletionMessageToolCall,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Execute a single MCP tool call.

        Args:
            tool_call: OpenAI tool call object
            user_id: User ID to pass to tool (CRITICAL: for user isolation)

        Returns:
            Tool execution result as dict
        """
        tool_name = tool_call.function.name
        logger.info(f"Executing tool: {tool_name}")

        try:
            # Parse tool arguments
            tool_args = json.loads(tool_call.function.arguments)
            logger.debug(f"Tool arguments: {tool_args}")

            # Get tool function
            tool_func = self.tool_functions.get(tool_name)
            if not tool_func:
                logger.error(f"Unknown tool: {tool_name}")
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }

            # CRITICAL: Ensure user_id is passed to tool
            # This is the PRIMARY security mechanism - all tools filter by user_id
            tool_args["user_id"] = user_id

            # Execute tool
            result = await tool_func(**tool_args)
            logger.info(f"Tool {tool_name} executed successfully")
            logger.debug(f"Tool result: {result}")

            return result

        except Exception as e:
            logger.error(f"Tool execution failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}"
            }


# Singleton instance
_agent_instance: Optional[TodoAgent] = None


def get_agent() -> TodoAgent:
    """
    Get singleton TodoAgent instance.

    Returns:
        TodoAgent instance

    Raises:
        ValueError: If OPENAI_API_KEY not set in environment
    """
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = TodoAgent()
    return _agent_instance


# Export agent getter
__all__ = ["get_agent", "TodoAgent", "TODO_ASSISTANT_SYSTEM_PROMPT"]
