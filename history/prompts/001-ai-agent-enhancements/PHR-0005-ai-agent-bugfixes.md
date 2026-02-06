# PHR-0005: AI Agent Bug Fixes - Hallucination & Tool Call Issues

**Date**: 2026-01-25
**Branch**: `001-ai-agent-enhancements`
**Status**: Bug Fixes Applied

## User Report

User identified critical issues with the AI agent:

### Issue 1: Recurring Tasks Not Working
```
User: "I have meeting with my boss every monday"
AI: "I've added a recurring task for your weekly meeting!"
Reality: Task was NOT actually added, or recurrence_pattern was not set
```

### Issue 2: AI Showing Raw XML Tool Calls
```
User: "Ok wdit this priority to Medium"
AI: <tool_call>
    <function=update_task>
    <parameter=task_id>99657e07...</parameter>
    <parameter=priority>medium</parameter>
    </function>
    </tool_call>
```
The AI was outputting raw XML instead of natural responses.

### Issue 3: AI Hallucinating Actions
```
User: "Every monday i have meetings with office manager"
AI: "I've added a recurring task!" (but didn't actually call the tool)
User: "Show my all tasks"
AI: Shows a task with made-up ID "7e4c1a2b" that doesn't exist
```

## Root Cause Analysis

1. **Model Not Using Function Calling**: The OpenRouter model (gpt-4o-mini) was outputting tool calls as XML text instead of using proper OpenAI function calling API.

2. **No Fallback Parser**: The original code only handled proper `assistant_message.tool_calls` but not text-based XML tool calls.

3. **No Anti-Hallucination Rules**: System prompt didn't explicitly forbid lying about actions.

## Fixes Applied

### 1. Enhanced System Prompt with Strict Rules

Added new rules to `phase3/backend/src/services/agent_service.py`:

```
## ⚠️ ABSOLUTE RULES - VIOLATION IS FORBIDDEN

### Rule 0: NEVER HALLUCINATE OR LIE
- NEVER say "I've added a task" unless you ACTUALLY called the add_task function
- NEVER make up task IDs - only use IDs returned from actual tool calls
- If a tool call fails, ADMIT IT and offer to try again

### Rule 1: ALWAYS USE TOOLS - NEVER FAKE IT
- When user wants to ADD a task → You MUST call add_task function
- DO NOT describe what you would do - ACTUALLY DO IT

### Rule 2: NEVER Show Raw Tool Call Syntax
- NEVER output <tool_call>, <function=...>, XML, or JSON to the user

### Rule 6: Bulk Operations
When user says "delete ALL tasks":
1. First call list_tasks to get all task IDs
2. Then call delete_task for EACH task ID one by one
```

### 2. Text-Based Tool Call Parser

Added `_parse_text_tool_calls()` method to parse XML tool calls:

```python
def _parse_text_tool_calls(self, content: str) -> list[dict[str, Any]] | None:
    """Parse tool calls from text if model outputs them as XML."""
    if not content:
        return None
    if "<tool_call>" not in content and "<function=" not in content:
        return None

    # Pattern to match <function=name>...<parameter=key>value</parameter>...</function>
    function_pattern = r'<function=(\w+)>(.*?)</function>'
    param_pattern = r'<parameter=(\w+)>([^<]*)</parameter>'
    # ... parsing logic
```

### 3. Fallback Execution Flow

When model outputs text-based tool calls:
1. Parse the XML to extract function name and parameters
2. Execute the tools against the real database
3. Generate a natural response based on actual results
4. Strip any remaining XML from the response

### 4. Enhanced Logging

Added comprehensive logging to debug issues:
```python
logger.info(f"Processing message: {message[:100]}...")
logger.info(f"Response has tool_calls: {bool(assistant_message.tool_calls)}")
logger.info(f"Content contains <tool_call>: {'<tool_call>' in content}")
logger.info(f"Parsed tool call: {func_name} with args: {params}")
```

### 5. Bug Fixes

- Fixed logic error: `if not content or "<tool_call>" not in content and "<function=" not in content`
- Fixed parser requiring non-empty params (some tools have no params)
- Increased max_tokens from 1000 to 2000

## Files Modified

1. `phase3/backend/src/services/agent_service.py`
   - Added `_parse_text_tool_calls()` method
   - Added anti-hallucination rules (Rule 0, 1, 2)
   - Added bulk operations rule (Rule 6)
   - Added fallback execution for text-based tool calls
   - Added comprehensive logging
   - Fixed parser bugs

2. `phase3/backend/src/config.py`
   - Increased `agent_max_tokens` from 1000 to 2000

## Expected Behavior After Fix

### Before (Broken)
```
User: "Delete all tasks"
AI: <tool_call><function=delete_task>...</function></tool_call>
```

### After (Fixed)
```
User: "Delete all tasks"
AI: "I've deleted all 5 tasks from your list."
```

## Testing Instructions

1. Restart the Phase 3 backend:
   ```bash
   cd phase3/backend
   uvicorn src.main:app --reload --port 8001
   ```

2. Check console logs for parsing activity:
   ```
   INFO: No proper tool calls, checking for text-based tool calls...
   INFO: Content contains <tool_call>: True
   INFO: Parsed tool call: delete_task with args: {'task_id': '...'}
   INFO: Executing 1 text-based tool calls
   ```

3. Test scenarios:
   - "Add a task to buy groceries" → Should actually add task
   - "Show my tasks" → Should show real tasks from database
   - "Every Monday I have a meeting" → Should set recurrence_pattern="weekly"
   - "Delete all tasks" → Should delete each task and confirm

## Lessons Learned

1. **Always verify tool execution**: Don't trust AI claims - verify with actual database state
2. **Handle model limitations**: Some models output tool calls as text instead of proper function calls
3. **Add fallback parsers**: When using external APIs, handle unexpected response formats
4. **Strict system prompts**: Explicit anti-hallucination rules are necessary

## Constitution Compliance

- [x] Bug fixes follow Spec-Driven Development (identified issue → planned fix → implemented)
- [x] Claude Code generated 100% of fixes
- [x] Production quality with proper error handling and logging
