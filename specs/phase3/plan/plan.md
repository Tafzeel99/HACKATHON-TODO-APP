# Implementation Plan: Phase 3 - Todo AI Chatbot

**Branch**: `phase3-ai-chatbot` | **Date**: 2026-01-19 | **Spec**: [spec.md](../spec/spec.md)
**Input**: Feature specification from `/specs/phase3/spec/spec.md`

---

## Summary

Phase 3 transforms the todo application into an AI-powered conversational experience. Users manage tasks through natural language using a ChatKit UI frontend that communicates with a FastAPI backend. The backend uses OpenAI Agents SDK to understand user intent and executes task operations through MCP (Model Context Protocol) tools. All state is persisted to Neon PostgreSQL, ensuring stateless server architecture.

**Key Technical Approach**:
- ChatKit UI for conversational interface
- FastAPI `/api/{user_id}/chat` endpoint for message handling
- OpenAI Agents SDK for natural language understanding and tool orchestration
- MCP Server exposing 5 task operation tools (add, list, complete, delete, update)
- SQLModel for database operations with 3 models (Task, Conversation, Message)
- Stateless architecture with all state in Neon PostgreSQL

---

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript/Next.js 16+ (frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, OpenAI Agents SDK, MCP Python SDK
- Frontend: OpenAI ChatKit, React, Next.js
**Storage**: Neon PostgreSQL (serverless) - extending Phase 2 database
**Testing**: pytest (backend), Jest (frontend)
**Target Platform**: Web application (Vercel frontend, Railway/Render backend)
**Project Type**: Web application with AI integration
**Performance Goals**: Chat response < 3 seconds (including AI processing)
**Constraints**: Stateless server, horizontal scaling ready, conversation persistence
**Scale/Scope**: Single user conversations, 5 MCP tools, 3 database models

---

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
- [x] Sequential phase completion (no skipping) - Phase 2 completed
- [x] Current phase builds on previous foundation - Extends Phase 2 backend
- [x] Architecture follows: CLI → Web → AI Chatbot → K8s → Cloud-Native

### Principle 4: Cloud-Native First
- [x] Stateless design (from Phase III onwards) - All state in database
- [ ] Containerization ready (mandatory from Phase IV) - Phase IV requirement
- [ ] Event-driven patterns considered (Phase V) - Phase V requirement
- [x] Horizontal scalability designed in - Stateless enables this

### Principle 5: Production Quality
- [x] Clean code principles enforced
- [x] Security best practices followed (see Security Standards)
- [x] Comprehensive error handling implemented
- [x] Full documentation provided

**GATE STATUS**: ✅ PASS - All applicable Phase 3 requirements met

---

## Project Structure

### Documentation (this feature)

```text
specs/phase3/
├── plan/
│   └── plan.md              # This file
├── spec/
│   └── spec.md              # Feature specification
├── research.md              # Phase 0 output
├── data-model.md            # Phase 1 output
├── quickstart.md            # Phase 1 output
├── contracts/               # Phase 1 output
│   └── chat-api.yaml        # OpenAPI specification
├── tasks/
│   └── tasks.md             # Phase 2 output (/sp.tasks command)
└── checklists/
    └── requirements.md      # Specification checklist
```

### Source Code (repository root)

```text
phase3/
├── backend/
│   ├── src/
│   │   ├── models/          # SQLModel: Task, Conversation, Message
│   │   ├── services/        # Business logic
│   │   │   ├── agent_service.py    # OpenAI Agents SDK integration
│   │   │   └── chat_service.py     # Chat message handling
│   │   ├── mcp/             # MCP Server implementation
│   │   │   ├── server.py           # MCP server setup
│   │   │   └── tools/              # MCP tool definitions
│   │   │       ├── add_task.py
│   │   │       ├── list_tasks.py
│   │   │       ├── complete_task.py
│   │   │       ├── delete_task.py
│   │   │       └── update_task.py
│   │   ├── api/
│   │   │   └── chat.py             # POST /api/{user_id}/chat endpoint
│   │   ├── db.py                   # Database connection
│   │   └── main.py                 # FastAPI app entry
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── conftest.py
│   ├── pyproject.toml
│   └── README.md
│
└── frontend/
    ├── src/
    │   ├── app/
    │   │   ├── chat/
    │   │   │   └── page.tsx        # ChatKit integration page
    │   │   └── layout.tsx
    │   ├── components/
    │   │   └── chat/
    │   │       └── ChatInterface.tsx
    │   ├── lib/
    │   │   └── api.ts              # Chat API client
    │   └── types/
    │       └── chat.ts             # TypeScript types
    ├── package.json
    └── README.md
```

**Structure Decision**: Web application structure with separate frontend (ChatKit UI) and backend (FastAPI + MCP). Backend contains MCP server as an embedded module rather than separate service for simplicity in Phase 3.

---

## Architecture Overview

```
┌─────────────────────┐     ┌────────────────────────────────────────────────┐     ┌─────────────────┐
│                     │     │              FastAPI Server                     │     │                 │
│                     │     │  ┌──────────────────────────────────────────┐  │     │                 │
│  ChatKit UI         │────▶│  │         Chat Endpoint                    │  │     │    Neon DB      │
│  (Next.js)          │     │  │  POST /api/{user_id}/chat                │  │     │  (PostgreSQL)   │
│                     │     │  └───────────────┬──────────────────────────┘  │     │                 │
│                     │     │                  │                             │     │  - tasks        │
│                     │     │                  ▼                             │     │  - conversations│
│                     │     │  ┌──────────────────────────────────────────┐  │     │  - messages     │
│                     │◀────│  │      OpenAI Agents SDK                   │  │     │                 │
│                     │     │  │      (Agent + Runner)                    │  │     │                 │
│                     │     │  └───────────────┬──────────────────────────┘  │     │                 │
│                     │     │                  │                             │     │                 │
│                     │     │                  ▼                             │     │                 │
│                     │     │  ┌──────────────────────────────────────────┐  │────▶│                 │
│                     │     │  │         MCP Server (Embedded)            │  │     │                 │
│                     │     │  │  (5 Tools for Task Operations)           │  │◀────│                 │
│                     │     │  └──────────────────────────────────────────┘  │     │                 │
└─────────────────────┘     └────────────────────────────────────────────────┘     └─────────────────┘
```

---

## Conversation Flow (Stateless Request Cycle)

1. User sends message via ChatKit UI
2. Frontend calls `POST /api/{user_id}/chat` with message and optional conversation_id
3. Backend fetches conversation history from database
4. Backend stores user message in database
5. Backend builds message array (history + new message) for agent
6. OpenAI Agent processes message and invokes MCP tools as needed
7. MCP tools execute database operations (CRUD on tasks)
8. Backend stores assistant response in database
9. Backend returns response to frontend
10. Server holds NO state (ready for next request from any instance)

---

## MCP Tools Specification

| Tool | Purpose | Parameters | Returns |
|------|---------|------------|---------|
| `add_task` | Create new task | user_id, title, description? | task_id, status, title |
| `list_tasks` | Retrieve tasks | user_id, status? (all/pending/completed) | Array of task objects |
| `complete_task` | Mark task done | user_id, task_id | task_id, status, title |
| `delete_task` | Remove task | user_id, task_id | task_id, status, title |
| `update_task` | Modify task | user_id, task_id, title?, description? | task_id, status, title |

---

## Security Considerations

- JWT authentication required for all chat endpoints
- User isolation: MCP tools always filter by user_id
- Input validation on all tool parameters
- Rate limiting: 100 requests/minute per user
- No sensitive data in conversation logs

---

## Complexity Tracking

> No Constitution Check violations requiring justification.

---

## Next Steps

1. Generate `research.md` - Technology research and decisions
2. Generate `data-model.md` - Database model definitions
3. Generate `contracts/chat-api.yaml` - OpenAPI specification
4. Generate `quickstart.md` - Development setup guide
5. Run `/sp.tasks` to create implementation tasks
