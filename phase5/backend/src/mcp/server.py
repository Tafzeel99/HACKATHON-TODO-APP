"""MCP Server setup and tool registration."""

from typing import Any

from src.config import get_settings

settings = get_settings()


class MCPToolRegistry:
    """Registry for MCP tools available to the AI agent."""

    def __init__(self) -> None:
        self._tools: dict[str, dict[str, Any]] = {}

    def register(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        handler: Any,
    ) -> None:
        """Register an MCP tool.

        Args:
            name: Tool name (e.g., 'add_task')
            description: Tool description for AI agent
            parameters: JSON Schema for tool parameters
            handler: Async function to execute the tool
        """
        self._tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "handler": handler,
        }

    def get_tool(self, name: str) -> dict[str, Any] | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def get_all_tools(self) -> list[dict[str, Any]]:
        """Get all registered tools for OpenAI function calling."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"],
                },
            }
            for tool in self._tools.values()
        ]

    def get_tool_schemas(self) -> list[dict[str, Any]]:
        """Get tool schemas in OpenAI function format."""
        return self.get_all_tools()

    async def execute_tool(self, name: str, **kwargs: Any) -> dict[str, Any]:
        """Execute a tool by name with given arguments.

        Args:
            name: Tool name
            **kwargs: Tool arguments

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool not found
        """
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")

        handler = tool["handler"]
        return await handler(**kwargs)


# Global tool registry instance
tool_registry = MCPToolRegistry()


def get_tool_registry() -> MCPToolRegistry:
    """Get the global tool registry."""
    return tool_registry
