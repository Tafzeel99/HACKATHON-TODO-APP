#!/usr/bin/env python3
"""Test script to verify all 5 MCP tools work properly."""

import asyncio
import sys
import os

# Import the tool registry to test the tools
from src.mcp.server import get_tool_registry

# Import tools to register them
from src.mcp.tools import add_task, list_tasks, complete_task, delete_task, update_task


async def test_mcp_tools():
    """Test that all 5 MCP tools are registered and accessible."""
    print("Testing MCP Tools Registration...")

    registry = get_tool_registry()

    expected_tools = [
        "add_task",
        "list_tasks",
        "complete_task",
        "delete_task",
        "update_task"
    ]

    all_tools = registry.get_all_tools()
    registered_tool_names = [tool['function']['name'] for tool in all_tools]

    print(f"Found {len(registered_tool_names)} registered tools: {registered_tool_names}")

    missing_tools = []
    for expected_tool in expected_tools:
        if expected_tool not in registered_tool_names:
            missing_tools.append(expected_tool)

    if missing_tools:
        print(f"❌ ERROR: Missing tools: {missing_tools}")
        return False

    print("✅ All 5 MCP tools are registered:")
    for tool in all_tools:
        print(f"  - {tool['function']['name']}: {tool['function']['description'][:50]}...")

    # Test that each tool can be retrieved
    print("\nTesting individual tool retrieval...")
    for tool_name in expected_tools:
        tool = registry.get_tool(tool_name)
        if tool:
            print(f"  ✅ {tool_name} - Retrieved successfully")
        else:
            print(f"  ❌ {tool_name} - Failed to retrieve")
            return False

    print("\n✅ All MCP tools are properly registered and accessible!")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_mcp_tools())
    if not success:
        sys.exit(1)
    print("\n🎉 All tests passed!")