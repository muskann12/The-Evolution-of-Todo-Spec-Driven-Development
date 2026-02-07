# Phase III: Model Context Protocol (MCP) Tools Module
# This module implements stateless MCP tools for AI agent interaction

from app.mcp.server import (
    mcp_server,
    get_db_session,
    tool,
    _tool_handlers,
    add_task,
    list_tasks,
    update_task,
    complete_task,
    delete_task,
)

__all__ = [
    "mcp_server",
    "get_db_session",
    "tool",
    "_tool_handlers",
    "add_task",
    "list_tasks",
    "update_task",
    "complete_task",
    "delete_task",
]
