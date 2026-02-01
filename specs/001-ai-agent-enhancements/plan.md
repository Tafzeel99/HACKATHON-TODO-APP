# Implementation Plan: Phase 3.5 - AI Agent & App Enhancements

**Branch**: `001-ai-agent-enhancements` | **Date**: 2026-01-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-ai-agent-enhancements/spec.md`

## Summary

Enhance the Phase 3 AI chatbot with intermediate/advanced task features (priorities, tags, due dates, recurring tasks, reminders), smart analytics, and multi-language support for English, Urdu (اردو), and Roman Urdu. The implementation leverages OpenAI's GPT model's native multilingual capabilities and extends existing MCP tools to support new task fields.

## Technical Context

**Language/Version**: Python 3.13+, TypeScript 5.x
**Primary Dependencies**: FastAPI, OpenAI Agents SDK, MCP SDK, SQLModel, Next.js 16+
**Storage**: Neon PostgreSQL (via SQLModel) - Task model already has required fields
**Testing**: pytest (backend), Jest (frontend)
**Target Platform**: Web (Linux server backend, Vercel frontend)
**Project Type**: Web (monorepo with frontend + backend)
**Performance Goals**: <200ms p95 response time, natural language parsing <5s
**Constraints**: Stateless backend, JWT auth required, 100 req/min rate limit
**Scale/Scope**: Single user isolation, conversation context within session

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle 1: Spec-Driven Development (SDD) - MANDATORY
- [x] All development follows: Spec → Plan → Tasks → Implement sequence
- [x] No code implementation without approved specification
- [x] Every implementation references a Task ID
- [x] Claude Code generates 100% of code (no manual coding)
- [x] Specifications refined until correct output achieved

### Principle 2: AI-Native Architecture
- [x] Engineer role is System Architect (not code writer)
- [x] Claude Code used as primary development tool
- [x] Reusable Intelligence (Skills, Agents) actively used
- [x] Agentic Dev Stack: AGENTS.md + Spec-KitPlus + Claude Code

### Principle 3: Progressive Complexity
- [x] Sequential phase completion (no skipping)
- [x] Current phase builds on previous foundation (Phase 3 → 3.5)
- [x] Architecture follows: CLI → Web → AI Chatbot → K8s → Cloud-Native

### Principle 4: Cloud-Native First
- [x] Stateless design (from Phase III onwards) - maintained
- [x] Containerization ready (mandatory from Phase IV) - prepared
- [x] Event-driven patterns considered (Phase V) - deferred
- [x] Horizontal scalability designed in - all state in database

### Principle 5: Production Quality
- [x] Clean code principles enforced
- [x] Security best practices followed (see Security Standards)
- [x] Comprehensive error handling implemented
- [x] Full documentation provided

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-agent-enhancements/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (API contracts)
│   └── mcp-tools.yaml   # Enhanced MCP tool definitions
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
phase3/backend/
├── src/
│   ├── main.py                    # FastAPI entry + ChatKit endpoint
│   ├── chatkit_server.py          # ChatKit SDK wrapper
│   ├── config.py                  # Settings management
│   ├── auth.py                    # JWT verification
│   ├── db.py                      # Database connection
│   ├── errors.py                  # Error handling
│   ├── middleware.py              # Rate limiting
│   ├── models/
│   │   ├── conversation.py        # Conversation model
│   │   └── message.py             # Message model
│   ├── mcp/
│   │   ├── server.py              # MCP server setup
│   │   └── tools/
│   │       ├── add_task.py        # UPDATE: Add new fields support
│   │       ├── list_tasks.py      # UPDATE: Add filtering by priority/tags/due_date
│   │       ├── complete_task.py   # UPDATE: Handle recurring task creation
│   │       ├── delete_task.py     # (minimal changes)
│   │       ├── update_task.py     # UPDATE: Support all new fields
│   │       └── get_analytics.py   # NEW: Productivity statistics
│   └── services/
│       ├── agent_service.py       # UPDATE: Multi-language system prompt
│       └── chat_service.py        # Chat logic
└── tests/
    ├── test_mcp_tools.py          # Tool tests
    └── test_multilingual.py       # NEW: Language support tests

phase2/frontend/
├── src/
│   ├── app/(dashboard)/
│   │   └── chat/page.tsx          # Chat interface (existing)
│   └── components/
│       └── chat/
│           └── TodoChatKit.tsx    # ChatKit UI (existing)
└── (minimal frontend changes - AI handles language)
```

**Structure Decision**: Extending existing Phase 3 backend structure. Task model in Phase 2 already has all required fields (priority, tags, due_date, recurrence_pattern, recurrence_end_date, parent_task_id, reminder_at). Focus is on enhancing MCP tools and AI agent system prompt.

## Implementation Approach

### Key Insight: Database Already Ready

The Phase 2 Task model (`phase2/backend/src/models/task.py`) already contains:
- `priority` (low/medium/high)
- `tags` (JSON array)
- `due_date` (datetime)
- `recurrence_pattern` (none/daily/weekly/monthly)
- `recurrence_end_date` (datetime)
- `parent_task_id` (UUID for recurring chain)
- `reminder_at` (datetime)

**No database migrations needed!**

### Implementation Strategy

1. **MCP Tool Updates** (Backend)
   - Extend `add_task` tool to accept priority, tags, due_date, recurrence, reminder
   - Extend `list_tasks` tool with filtering (priority, tags, due_date range, overdue)
   - Extend `update_task` tool to modify all new fields
   - Add `complete_task` recurring logic (create next occurrence)
   - Add new `get_analytics` tool for productivity stats

2. **AI Agent Enhancement** (Backend)
   - Update system prompt with multi-language instructions
   - Include Urdu/Roman Urdu command examples
   - Add date parsing guidance (kal, aaj, aglay hafta, etc.)
   - Add priority keyword mapping (zaroori, fori → high)

3. **Natural Language Processing** (Handled by GPT)
   - GPT-4 natively understands Urdu and Roman Urdu
   - System prompt instructs language mirroring
   - No additional NLP libraries needed

4. **Frontend** (Minimal changes)
   - AI responses already display correctly (Unicode support exists)
   - No UI changes needed - chat interface works for all languages

## Complexity Tracking

No constitution violations. Implementation extends existing architecture without adding complexity.

| Aspect | Current | After Enhancement |
|--------|---------|-------------------|
| MCP Tools | 5 | 6 (+get_analytics) |
| Tool Parameters | Basic | Extended with new fields |
| Languages | English | English + Urdu + Roman Urdu |
| Database Schema | Already complete | No changes |

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| GPT may not understand Roman Urdu variations | Include common variations in system prompt examples |
| Date parsing ambiguity | Use sensible defaults + confirmation in response |
| Recurring task edge cases | Comprehensive testing with various recurrence patterns |
| Performance impact of analytics queries | Add database indexes, limit query scope |

## Dependencies

- **Phase 3 Backend**: Working AI agent with MCP tools ✅
- **Phase 2 Database**: Task model with all fields ✅
- **Phase 2 Frontend**: Chat UI with ChatKit ✅
- **OpenAI API**: GPT model with multilingual support ✅
