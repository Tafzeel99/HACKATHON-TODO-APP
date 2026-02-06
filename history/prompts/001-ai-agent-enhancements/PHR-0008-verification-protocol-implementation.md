# PHR-0008: AI Agent Verification Protocol Implementation

**Date**: 2026-01-26
**Feature**: 001-ai-agent-enhancements
**Type**: Implementation
**Status**: Completed

## User Request (Verbatim)

```
We are working on phase3 ai agent enhancement
You are Claude Code acting as a senior Agentic AI engineer.

You are implementing **Phase III: Todo AI Chatbot** using the Agentic Dev Stack:
Spec-Kit Plus + Claude Code + OpenAI Agents SDK + Official MCP SDK.

You must strictly follow the provided specification and architecture.
No manual coding assumptions. No shortcuts.

Your responsibility is to:
- Fully understand the requirements
- Identify logical, architectural, and agent-behavior flaws
- Improve the agent's intelligence, reliability, and correctness
- Fix issues without being explicitly told what is broken

================================================
CORE PRINCIPLES (NON-NEGOTIABLE)
================================================

1. **MCP is the single source of truth**
   - The agent must NEVER assume an operation succeeded
   - All create/update/delete actions MUST be verified via MCP tools
   - Spoken confirmations must exactly match MCP results

2. **Stateless Server, Stateful Intelligence**
   - Backend holds NO in-memory state
   - Conversation state MUST be reconstructed from database on every request
   - Agent reasoning must rely on fetched conversation + tool results only

3. **Correctness > Confidence**
   - The agent must NEVER falsely confirm success
   - If a task still exists after deletion, the agent must detect it
   - If MCP returns inconsistent state, the agent must re-fetch and retry

================================================
MANDATORY AGENT BEHAVIOR
================================================

After EVERY mutating MCP call (add, update, complete, delete):
1. Call the MCP tool
2. Immediately call `list_tasks`
3. Compare expected vs actual state
4. Respond ONLY after verification

DELETE TASK RULE (CRITICAL):
1. Call `list_tasks` FIRST
2. Resolve task IDs (by title or ID)
3. Call `delete_task`
4. Call `list_tasks` AGAIN
5. If ANY task still exists → do NOT confirm deletion

USER FEEDBACK HANDLING:
If user says "still one left", "task not deleted", "no you didn't":
- Assume MCP state may be stale or incorrect
- Re-fetch using `list_tasks`
- Reconcile and fix
- NEVER argue with the user
```

## Analysis

### Identified Gaps (Before Implementation)

| Requirement | Current State | Gap |
|------------|---------------|-----|
| Verify after every mutation | Agent trusted tool return values | No `list_tasks` called after add/update/delete/complete |
| Delete requires pre/post list | Direct delete without verification | Missing list_tasks before AND after delete |
| User feedback handling | Not implemented | Agent may argue instead of re-fetching |
| Retry on inconsistency | No retry logic | Agent assumed success even if state mismatch |
| Correctness > Confidence | Trusted single tool result | No comparison of expected vs actual state |

### Root Cause

The original `AGENT_INSTRUCTIONS` in `agent_service.py` focused on:
- Never hallucinating (Rule 0)
- Always using tools (Rule 1)
- Multi-language support

But lacked:
- Mandatory verification after mutations
- Specific delete verification protocol
- User feedback handling procedures
- Retry logic for inconsistent state

## Implementation

### Files Modified

1. **`phase3/backend/src/services/agent_service.py`**
   - Completely rewrote `AGENT_INSTRUCTIONS` with verification protocol
   - Added 12 rules instead of original 6
   - Added verification examples
   - Added NL-to-tool mapping
   - Added verification summary table

### New Rules Added

| Rule | Purpose |
|------|---------|
| Rule 0: CORRECTNESS > CONFIDENCE | Never falsely confirm, always verify |
| Rule 1: MANDATORY VERIFICATION PROTOCOL | Call list_tasks after every mutation |
| Rule 2: DELETE TASK PROTOCOL | 4-step: resolve, delete, verify, respond |
| Rule 3: USER FEEDBACK OVERRIDE | Re-fetch when user disputes |
| Rule 11: MULTI-TOOL CALLING | Combine mutation + list_tasks in one call |
| Rule 12: STATELESS AWARENESS | Database is truth, not memory |

### Files Created

1. **`phase3/backend/test_verification_protocol.py`**
   - Test suite validating agent instructions contain all required protocols
   - 8 test functions covering all verification requirements
   - All tests pass

## Verification

```
============================================================
VERIFICATION PROTOCOL TEST SUITE
============================================================
Testing verification protocol in agent instructions...
   [PASS] Mandatory verification protocol present
   [PASS] Verification flow steps documented
   [PASS] Warning about premature confirmation present

Testing delete protocol in agent instructions...
   [PASS] Delete task protocol section present
   [PASS] Pre-delete verification (list_tasks first) documented
   [PASS] Post-delete verification (list_tasks again) documented
   [PASS] Delete failure handling documented
   [PASS] Warning about false delete confirmation present

Testing user feedback handling in agent instructions...
   [PASS] User feedback handling rule present
   [PASS] User phrase handled: 'still one left'
   [PASS] User phrase handled: 'task not deleted'
   [PASS] User phrase handled: 'no you didn't'
   [PASS] User phrase handled: 'it's still there'
   [PASS] Re-fetch requirement documented
   [PASS] Non-arguing behavior documented

Testing multi-tool calling documentation...
   [PASS] Multi-tool calling documented
   [PASS] Tool combination example present

Testing stateless awareness in instructions...
   [PASS] Stateless awareness rule present
   [PASS] Database as source of truth documented
   [PASS] MCP as single source of truth documented

Testing correctness over confidence principle...
   [PASS] Correctness over confidence rule present
   [PASS] False confirmation warning present
   [PASS] Retry logic documented

Testing tool registry for verification protocol support...
   [PASS] Tool 'add_task' available
   [PASS] Tool 'list_tasks' available
   [PASS] Tool 'update_task' available
   [PASS] Tool 'complete_task' available
   [PASS] Tool 'delete_task' available
   [PASS] list_tasks available for verification

Testing verification summary presence...
   [PASS] Verification summary present

============================================================
RESULTS: 8 passed, 0 failed
============================================================
```

## Expected Agent Behavior (After Implementation)

### Adding a Task
```
User: "Add buy groceries"
Agent:
1. Calls add_task(title="Buy groceries") → gets task_id
2. Calls list_tasks() → verifies task exists
3. Says "I've added 'Buy groceries' - verified in your list"
```

### Deleting a Task
```
User: "Delete the groceries task"
Agent:
1. Calls list_tasks() → finds task ID for "groceries"
2. Calls delete_task(task_id) → gets success
3. Calls list_tasks() → confirms task is GONE
4. Says "I've deleted 'Buy groceries' - verified it's removed"
```

### User Disputes
```
User: "It's still there, check again"
Agent:
1. Says "Let me check..."
2. Calls list_tasks() immediately
3. If task exists: "You're right, it's still there. Let me delete it properly..."
4. If task gone: "I've verified - it's not in your list. Try refreshing?"
```

## Tags

#phase3 #ai-agent #verification-protocol #mcp #stateless #correctness

## Related

- PHR-0007: Phase3 UI Enhancements and AI Integration
- specs/001-ai-agent-enhancements/
