"""MCP tools for task operations.

Import all tool modules to register them with the tool registry.
"""

# Import tools to trigger their registration
from src.mcp.tools import add_task
from src.mcp.tools import list_tasks
from src.mcp.tools import complete_task
from src.mcp.tools import delete_task
from src.mcp.tools import update_task
from src.mcp.tools import get_analytics
from src.mcp.tools import get_suggestions
from src.mcp.tools import share_task
from src.mcp.tools import add_comment
from src.mcp.tools import assign_task

__all__ = [
    "add_task",
    "list_tasks",
    "complete_task",
    "delete_task",
    "update_task",
    "get_analytics",
    "get_suggestions",
    "share_task",
    "add_comment",
    "assign_task",
]
