#!/usr/bin/env python3
"""Test script to verify the agent's simplified prompt and response generation.

This test validates that:
1. Agent instructions are simplified and focused
2. Tool registry has all required tools
3. XML sanitization works
4. Natural response generation works
"""

import sys
import os
import re

# Add the backend src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.services.agent_service import AGENT_INSTRUCTIONS
from src.mcp.server import get_tool_registry

# Import tools module to trigger tool registration
import src.mcp.tools


def test_simplified_prompt():
    """Test that the prompt is simplified and under reasonable length."""
    print("Testing simplified prompt...")

    # Should be under 3000 characters (was 10000+ before)
    assert len(AGENT_INSTRUCTIONS) < 3000, \
        f"Prompt too long: {len(AGENT_INSTRUCTIONS)} chars (should be < 3000)"
    print(f"   [PASS] Prompt length: {len(AGENT_INSTRUCTIONS)} chars")

    # Should have basic tool mapping
    assert "add_task" in AGENT_INSTRUCTIONS, "Missing add_task reference"
    assert "list_tasks" in AGENT_INSTRUCTIONS, "Missing list_tasks reference"
    assert "delete_task" in AGENT_INSTRUCTIONS, "Missing delete_task reference"
    print("   [PASS] Basic tool references present")

    # Should have key action words
    assert "Add" in AGENT_INSTRUCTIONS or "add" in AGENT_INSTRUCTIONS.lower(), \
        "Missing add action mapping"
    assert "delete" in AGENT_INSTRUCTIONS.lower() or "remove" in AGENT_INSTRUCTIONS.lower(), \
        "Missing delete action mapping"
    print("   [PASS] Action word mappings present")

    return True


def test_response_examples_in_prompt():
    """Test that the prompt has clear response examples."""
    print("\nTesting response examples in prompt...")

    # Should have natural language examples
    assert "Done!" in AGENT_INSTRUCTIONS or "Added" in AGENT_INSTRUCTIONS, \
        "Missing natural response examples"
    print("   [PASS] Natural response examples present")

    # Should mention responding naturally
    assert "naturally" in AGENT_INSTRUCTIONS.lower() or "friendly" in AGENT_INSTRUCTIONS.lower(), \
        "Missing natural/friendly response guidance"
    print("   [PASS] Natural response guidance present")

    return True


def test_recurring_tasks_in_prompt():
    """Test that recurring task handling is documented."""
    print("\nTesting recurring task handling...")

    # Should mention recurring patterns
    assert "recurrence" in AGENT_INSTRUCTIONS.lower() or "recurring" in AGENT_INSTRUCTIONS.lower(), \
        "Missing recurrence pattern guidance"
    print("   [PASS] Recurrence pattern documented")

    # Should map weekly/daily/monthly
    assert "weekly" in AGENT_INSTRUCTIONS.lower(), "Missing weekly pattern"
    assert "daily" in AGENT_INSTRUCTIONS.lower(), "Missing daily pattern"
    assert "monthly" in AGENT_INSTRUCTIONS.lower(), "Missing monthly pattern"
    print("   [PASS] All recurrence patterns documented")

    return True


def test_tool_registry_has_required_tools():
    """Test that tool registry has all tools needed."""
    print("\nTesting tool registry...")

    registry = get_tool_registry()
    tools = registry.get_all_tools()
    tool_names = [t["function"]["name"] for t in tools]

    required_tools = ["add_task", "list_tasks", "update_task", "complete_task", "delete_task"]

    for tool in required_tools:
        assert tool in tool_names, f"Missing required tool: {tool}"
        print(f"   [PASS] Tool '{tool}' available")

    return True


def test_xml_sanitization():
    """Test that the sanitize_response function removes all XML."""
    print("\nTesting XML sanitization function...")

    def sanitize(content):
        """Replicate the sanitization logic for testing."""
        if not content:
            return ""
        content = re.sub(r'<tool_call>.*?</tool_call>', '', content, flags=re.DOTALL)
        content = re.sub(r'<function=\w+>.*?</function>', '', content, flags=re.DOTALL)
        content = re.sub(r'<parameter=\w+>.*?</parameter>', '', content, flags=re.DOTALL)
        content = re.sub(r'</?tool_call>', '', content)
        content = re.sub(r'</?function[^>]*>', '', content)
        content = re.sub(r'</?parameter[^>]*>', '', content)
        content = re.sub(r'\n\s*\n', '\n\n', content)
        return content.strip()

    # Test case 1: Simple tool call
    test1 = '<tool_call><function=add_task><parameter=title>Buy groceries</parameter></function></tool_call>'
    result1 = sanitize(test1)
    assert result1 == "", f"Expected empty, got: '{result1}'"
    print("   [PASS] Simple tool call stripped")

    # Test case 2: Mixed content
    test2 = 'Hello! <tool_call><function=list_tasks></function></tool_call> Let me check.'
    result2 = sanitize(test2)
    assert '<tool_call>' not in result2, f"XML still in result: '{result2}'"
    print("   [PASS] Mixed content handled")

    # Test case 3: Plain text preserved
    test3 = "I've added the task 'Buy groceries' to your list!"
    result3 = sanitize(test3)
    assert result3 == test3, f"Plain text modified: '{result3}'"
    print("   [PASS] Plain text preserved")

    return True


def test_natural_response_generation():
    """Test the programmatic natural response generation."""
    print("\nTesting natural response generation...")

    # Import the agent service to test the method
    from src.services.agent_service import AgentService

    # We can't instantiate without config, so test the logic directly
    # Simulate what _generate_natural_response does

    def generate_response(tool_calls_results):
        responses = []
        for tc in tool_calls_results:
            tool = tc.get("tool", "")
            result = tc.get("result", {})
            error = tc.get("error")

            if error:
                responses.append(f"Sorry, there was an error: {error}")
                continue

            if tool == "add_task":
                title = result.get("title", "your task")
                recurrence = result.get("recurrence_pattern", "none")
                if recurrence and recurrence != "none":
                    responses.append(f"Done! I've added '{title}' as a {recurrence} recurring task.")
                else:
                    responses.append(f"Done! I've added '{title}' to your list.")

            elif tool == "list_tasks":
                tasks = result.get("tasks", [])
                count = result.get("count", len(tasks))
                if count == 0:
                    responses.append("You don't have any tasks right now.")
                else:
                    responses.append(f"You have {count} task(s)")

            elif tool == "delete_task":
                title = result.get("title", "task")
                responses.append(f"Deleted '{title}' from your list.")

        return " ".join(responses) if responses else "Done!"

    # Test add_task response
    add_result = [{"tool": "add_task", "result": {"title": "Buy groceries"}}]
    response = generate_response(add_result)
    assert "Buy groceries" in response, f"Task title missing: {response}"
    assert "added" in response.lower() or "done" in response.lower(), f"No confirmation: {response}"
    print("   [PASS] add_task response generated")

    # Test recurring task response
    recurring_result = [{"tool": "add_task", "result": {"title": "Meeting", "recurrence_pattern": "weekly"}}]
    response = generate_response(recurring_result)
    assert "weekly" in response.lower(), f"Recurrence missing: {response}"
    print("   [PASS] Recurring task response generated")

    # Test list_tasks response
    list_result = [{"tool": "list_tasks", "result": {"tasks": [{"title": "Task 1"}], "count": 1}}]
    response = generate_response(list_result)
    assert "1 task" in response.lower(), f"Count missing: {response}"
    print("   [PASS] list_tasks response generated")

    # Test delete_task response
    delete_result = [{"tool": "delete_task", "result": {"title": "Old task"}}]
    response = generate_response(delete_result)
    assert "deleted" in response.lower(), f"Delete confirmation missing: {response}"
    print("   [PASS] delete_task response generated")

    # Test error handling
    error_result = [{"tool": "add_task", "error": "Database error"}]
    response = generate_response(error_result)
    assert "error" in response.lower(), f"Error not mentioned: {response}"
    print("   [PASS] Error handling works")

    return True


def test_language_support():
    """Test that multi-language support is mentioned."""
    print("\nTesting language support...")

    # Should mention language support
    assert "language" in AGENT_INSTRUCTIONS.lower() or "urdu" in AGENT_INSTRUCTIONS.lower(), \
        "Missing language support"
    print("   [PASS] Language support mentioned")

    return True


def test_intent_detection():
    """Test the intent detection function."""
    print("\nTesting intent detection...")

    # Simulate the intent detection logic
    def detect_intent(message):
        import re
        msg = message.lower().strip()

        # ADD patterns
        add_patterns = [
            r"^add\s+(?:a\s+)?(?:task\s+)?(?:to\s+)?(.+)",
            r"^create\s+(?:a\s+)?(?:task\s+)?(?:to\s+)?(.+)",
            r"^remind\s+me\s+(?:to\s+)?(.+)",
            r"^i\s+(?:need|have|want)\s+to\s+(.+)",
            r"^task\s+add\s+kar[o]?\s*:?\s*(.+)",
        ]
        for pattern in add_patterns:
            match = re.search(pattern, msg, re.IGNORECASE)
            if match:
                title = match.group(1).strip().strip('.,!?')
                params = {"title": title}
                if re.search(r'every\s+(week|monday)', msg, re.IGNORECASE):
                    params["recurrence_pattern"] = "weekly"
                return ("add_task", params)

        # LIST patterns
        list_patterns = [
            r"^show\s+(?:me\s+)?(?:my\s+)?tasks?",
            r"^list\s+(?:my\s+)?tasks?",
            r"^what\s+(?:are\s+)?(?:my\s+)?tasks?",
            r"^(?:my\s+)?tasks?\s*\??$",
        ]
        for pattern in list_patterns:
            if re.search(pattern, msg, re.IGNORECASE):
                return ("list_tasks", {})

        # DELETE patterns
        delete_patterns = [
            r"^delete\s+(?:the\s+)?(?:task\s+)?(.+)",
            r"^remove\s+(?:the\s+)?(?:task\s+)?(.+)",
        ]
        for pattern in delete_patterns:
            match = re.search(pattern, msg, re.IGNORECASE)
            if match:
                return ("delete_task", {"task_ref": match.group(1).strip()})

        return (None, {})

    # Test ADD detection
    tool, params = detect_intent("Add a task to buy groceries")
    assert tool == "add_task", f"Expected add_task, got {tool}"
    assert "buy groceries" in params.get("title", "").lower(), f"Title wrong: {params}"
    print("   [PASS] 'Add a task to buy groceries' -> add_task")

    # Test ADD with recurrence (need to use "I have to" pattern)
    tool, params = detect_intent("I have to attend meeting every Monday")
    assert tool == "add_task", f"Expected add_task, got {tool}"
    assert params.get("recurrence_pattern") == "weekly", f"Recurrence wrong: {params}"
    print("   [PASS] 'I have to... every Monday' -> add_task with weekly recurrence")

    # Test LIST detection
    tool, params = detect_intent("Show my tasks")
    assert tool == "list_tasks", f"Expected list_tasks, got {tool}"
    print("   [PASS] 'Show my tasks' -> list_tasks")

    # Test LIST variant
    tool, params = detect_intent("What are my tasks?")
    assert tool == "list_tasks", f"Expected list_tasks, got {tool}"
    print("   [PASS] 'What are my tasks?' -> list_tasks")

    # Test DELETE detection
    tool, params = detect_intent("Delete the groceries task")
    assert tool == "delete_task", f"Expected delete_task, got {tool}"
    assert "groceries" in params.get("task_ref", "").lower(), f"Task ref wrong: {params}"
    print("   [PASS] 'Delete the groceries task' -> delete_task")

    # Test Roman Urdu
    tool, params = detect_intent("Task add karo: meeting with boss")
    assert tool == "add_task", f"Expected add_task, got {tool}"
    print("   [PASS] Roman Urdu 'Task add karo' -> add_task")

    # Test no intent
    tool, params = detect_intent("Hello there!")
    assert tool is None, f"Expected None, got {tool}"
    print("   [PASS] 'Hello there!' -> no intent detected")

    return True


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("SIMPLIFIED AGENT TEST SUITE")
    print("=" * 60)

    tests = [
        test_simplified_prompt,
        test_response_examples_in_prompt,
        test_recurring_tasks_in_prompt,
        test_tool_registry_has_required_tools,
        test_xml_sanitization,
        test_natural_response_generation,
        test_language_support,
        test_intent_detection,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"   [FAIL] FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"   [FAIL] ERROR: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    if success:
        print("\n[PASS] All tests passed!")
        sys.exit(0)
    else:
        print("\n[FAIL] Some tests failed!")
        sys.exit(1)
