# Tasks: Phase 3 - Todo AI Chatbot

**Input**: Design documents from `/specs/phase3/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chat-api.yaml
**Created**: 2026-01-19

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `phase3/backend/src/`
- **Frontend**: `phase3/frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for Phase 3

- [X] T001 Create phase3/backend directory structure per implementation plan
- [X] T002 Initialize Python backend with UV and dependencies (fastapi, sqlmodel, openai, mcp) in phase3/backend/pyproject.toml
- [X] T003 [P] Create phase3/frontend directory structure for ChatKit UI
- [X] T004 [P] Initialize Next.js frontend with ChatKit dependencies in phase3/frontend/package.json
- [X] T005 [P] Create environment configuration files (.env.example) for both backend and frontend
- [X] T006 [P] Create phase3/backend/src/config.py for settings management
- [X] T007 [P] Create phase3/frontend/.env.local.example with required variables

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database & Models

- [X] T008 Create database connection module in phase3/backend/src/db.py (reuse Phase 2 Neon connection)
- [X] T009 [P] Create Conversation model in phase3/backend/src/models/conversation.py
- [X] T010 [P] Create Message model in phase3/backend/src/models/message.py
- [X] T011 Create models __init__.py exporting all models in phase3/backend/src/models/__init__.py
- [X] T012 Create database migration for conversations and messages tables

### MCP Server Foundation

- [X] T013 Create MCP server setup module in phase3/backend/src/mcp/server.py
- [X] T014 Create MCP tools __init__.py in phase3/backend/src/mcp/tools/__init__.py

### API Foundation

- [X] T015 Create FastAPI main application in phase3/backend/src/main.py with CORS and middleware
- [X] T016 [P] Create JWT authentication dependency in phase3/backend/src/auth.py (reuse Phase 2 Better Auth)
- [X] T017 [P] Create error handling utilities in phase3/backend/src/errors.py

### Agent Foundation

- [X] T018 Create OpenAI Agents SDK service in phase3/backend/src/services/agent_service.py with agent configuration
- [X] T019 Create chat service module in phase3/backend/src/services/chat_service.py

### Frontend Foundation

- [X] T020 Create chat API client in phase3/frontend/src/lib/api.ts
- [X] T021 [P] Create TypeScript types for chat in phase3/frontend/src/types/chat.ts
- [X] T022 Create chat page layout in phase3/frontend/src/app/chat/layout.tsx
- [X] T023 Create base ChatInterface component in phase3/frontend/src/components/chat/ChatInterface.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Natural Language Task Creation (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks by typing natural language messages like "Add a task to buy groceries"

**Independent Test**: Send message "Add a task to buy milk" and verify task appears in database with title "Buy milk"

### Implementation for User Story 1

- [X] T024 [US1] Implement add_task MCP tool in phase3/backend/src/mcp/tools/add_task.py
- [X] T025 [US1] Register add_task tool with MCP server in phase3/backend/src/mcp/server.py
- [X] T026 [US1] Configure agent with add_task tool instructions in phase3/backend/src/services/agent_service.py
- [X] T027 [US1] Implement chat endpoint POST /api/{user_id}/chat in phase3/backend/src/api/chat.py
- [X] T028 [US1] Add conversation creation logic when no conversation_id provided
- [X] T029 [US1] Add user message storage to database in chat service
- [X] T030 [US1] Add assistant response storage to database in chat service
- [X] T031 [US1] Connect frontend ChatInterface to chat API with message sending
- [X] T032 [US1] Display AI response in ChatInterface with user/assistant distinction
- [X] T033 [US1] Add loading/typing indicator while AI processes in ChatInterface

**Checkpoint**: User Story 1 complete - users can create tasks via chat

---

## Phase 4: User Story 2 - View Tasks via Conversation (Priority: P1)

**Goal**: Users can ask "Show me my tasks" or "What's pending?" and see their task list

**Independent Test**: Ask "Show me all my tasks" and verify AI returns formatted list of existing tasks

### Implementation for User Story 2

- [X] T034 [US2] Implement list_tasks MCP tool in phase3/backend/src/mcp/tools/list_tasks.py
- [X] T035 [US2] Register list_tasks tool with MCP server
- [X] T036 [US2] Add list_tasks tool instructions to agent configuration
- [X] T037 [US2] Add status filtering (all/pending/completed) to list_tasks tool
- [X] T038 [US2] Format task list response with IDs, titles, and status in agent response

**Checkpoint**: User Story 2 complete - users can view tasks via chat

---

## Phase 5: User Story 3 - Mark Tasks Complete via Chat (Priority: P1)

**Goal**: Users can say "Mark task 3 as complete" or "I finished buying groceries"

**Independent Test**: Say "Mark task 1 as complete" and verify task completed status changes to true

### Implementation for User Story 3

- [X] T039 [US3] Implement complete_task MCP tool in phase3/backend/src/mcp/tools/complete_task.py
- [X] T040 [US3] Register complete_task tool with MCP server
- [X] T041 [US3] Add complete_task tool instructions to agent configuration
- [X] T042 [US3] Handle task not found error gracefully in complete_task tool
- [X] T043 [US3] Add confirmation message with task title in agent response

**Checkpoint**: User Story 3 complete - users can complete tasks via chat

---

## Phase 6: User Story 4 - Delete Tasks via Chat (Priority: P2)

**Goal**: Users can say "Delete task 2" or "Remove the meeting task"

**Independent Test**: Say "Delete task 2" and verify task is removed from database

### Implementation for User Story 4

- [X] T044 [US4] Implement delete_task MCP tool in phase3/backend/src/mcp/tools/delete_task.py
- [X] T045 [US4] Register delete_task tool with MCP server
- [X] T046 [US4] Add delete_task tool instructions to agent configuration
- [X] T047 [US4] Handle task not found error gracefully in delete_task tool
- [X] T048 [US4] Add confirmation message with deleted task title in agent response

**Checkpoint**: User Story 4 complete - users can delete tasks via chat

---

## Phase 7: User Story 5 - Update Tasks via Chat (Priority: P2)

**Goal**: Users can say "Change task 1 to 'Call mom tonight'" or update description

**Independent Test**: Say "Change task 1 to 'Call mom tonight'" and verify task title is updated

### Implementation for User Story 5

- [X] T049 [US5] Implement update_task MCP tool in phase3/backend/src/mcp/tools/update_task.py
- [X] T050 [US5] Register update_task tool with MCP server
- [X] T051 [US5] Add update_task tool instructions to agent configuration
- [X] T052 [US5] Support both title and description updates in update_task tool
- [X] T053 [US5] Handle task not found error gracefully in update_task tool
- [X] T054 [US5] Add confirmation message with updated task details in agent response

**Checkpoint**: User Story 5 complete - users can update tasks via chat

---

## Phase 8: User Story 6 - Conversation Continuity (Priority: P2)

**Goal**: Chat history persists and users can continue conversations across sessions

**Independent Test**: Have a conversation, close browser, reopen, verify previous messages are displayed

### Implementation for User Story 6

- [X] T055 [US6] Implement conversation history loading in chat service
- [X] T056 [US6] Add conversation context to agent when processing new messages
- [X] T057 [US6] Create GET /api/{user_id}/conversations endpoint in phase3/backend/src/api/chat.py
- [X] T058 [US6] Create GET /api/{user_id}/conversations/{id} endpoint for conversation with messages
- [X] T059 [US6] Add conversation list sidebar to frontend chat page
- [X] T060 [US6] Load and display previous messages when selecting a conversation
- [X] T061 [US6] Add "New Conversation" button to start fresh chat

**Checkpoint**: User Story 6 complete - conversation history persists

---

## Phase 9: User Story 7 - Authenticated Chat Access (Priority: P1)

**Goal**: Chat and tasks are private - only authenticated user can access their data

**Independent Test**: Attempt to access another user's conversation and verify access denied

### Implementation for User Story 7

- [X] T062 [US7] Add JWT verification to chat endpoint
- [X] T063 [US7] Verify user_id in path matches authenticated user
- [X] T064 [US7] Add user_id filtering to all MCP tool database queries
- [X] T065 [US7] Add user_id filtering to conversation queries
- [X] T066 [US7] Redirect unauthenticated users to login in frontend
- [X] T067 [US7] Pass JWT token in chat API requests from frontend

**Checkpoint**: User Story 7 complete - chat access is authenticated and isolated

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, edge cases, and documentation

### Error Handling

- [X] T068 [P] Add friendly error response for AI service unavailable
- [X] T069 [P] Add friendly error response for empty messages
- [X] T070 [P] Add friendly error response for gibberish/unclear messages
- [ ] T071 Add rate limiting (100 requests/minute per user) in phase3/backend/src/middleware.py

### Documentation

- [X] T072 [P] Create phase3/backend/README.md with setup instructions
- [X] T073 [P] Create phase3/frontend/README.md with setup instructions
- [ ] T074 Update main README.md with Phase 3 information

### Final Validation

- [ ] T075 Run quickstart.md validation - verify all setup steps work
- [ ] T076 Test all 5 MCP tools with sample conversations
- [ ] T077 Verify stateless architecture - server restart preserves all data

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup (T001-T007)
    ↓
Phase 2: Foundational (T008-T023) - BLOCKS all user stories
    ↓
Phases 3-9: User Stories (can proceed in priority order or parallel)
    ↓
Phase 10: Polish (T068-T077)
```

### User Story Dependencies

| Story | Priority | Dependencies | Can Parallel With |
|-------|----------|--------------|-------------------|
| US1 - Task Creation | P1 | Foundation only | - |
| US2 - View Tasks | P1 | Foundation only | US1 |
| US3 - Complete Tasks | P1 | Foundation only | US1, US2 |
| US7 - Authentication | P1 | Foundation only | US1, US2, US3 |
| US4 - Delete Tasks | P2 | Foundation only | Any P1 story |
| US5 - Update Tasks | P2 | Foundation only | Any P1 story |
| US6 - Conversation History | P2 | US1 (messages exist) | US4, US5 |

### Within Each User Story

1. MCP tool implementation
2. Tool registration with server
3. Agent instruction update
4. Error handling
5. Frontend integration (if applicable)

---

## Parallel Execution Examples

### Phase 1 - All can run in parallel:
```bash
Task: T001 "Create phase3/backend directory structure"
Task: T003 "Create phase3/frontend directory structure"
Task: T004 "Initialize Next.js frontend"
Task: T005 "Create environment configuration files"
```

### Phase 2 - Models can run in parallel:
```bash
Task: T009 "Create Conversation model"
Task: T010 "Create Message model"
Task: T016 "Create JWT authentication dependency"
Task: T017 "Create error handling utilities"
```

### User Stories - P1 stories can run in parallel:
```bash
# After Foundation complete, these can start simultaneously:
Task: T024-T033 "User Story 1 - Task Creation"
Task: T034-T038 "User Story 2 - View Tasks"
Task: T039-T043 "User Story 3 - Complete Tasks"
Task: T062-T067 "User Story 7 - Authentication"
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 + 7)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Task Creation) ← **FIRST MVP**
4. Complete Phase 4: User Story 2 (View Tasks)
5. Complete Phase 5: User Story 3 (Complete Tasks)
6. Complete Phase 9: User Story 7 (Authentication)
7. **STOP and VALIDATE**: Test core task operations via chat

### Full Feature Delivery

1. MVP complete (above)
2. Add User Story 4: Delete Tasks
3. Add User Story 5: Update Tasks
4. Add User Story 6: Conversation Continuity
5. Complete Phase 10: Polish

---

## Summary

| Phase | Task Count | Purpose |
|-------|------------|---------|
| Phase 1: Setup | 7 | Project initialization |
| Phase 2: Foundational | 16 | Core infrastructure |
| Phase 3: US1 - Create | 10 | Task creation via chat |
| Phase 4: US2 - View | 5 | View tasks via chat |
| Phase 5: US3 - Complete | 5 | Complete tasks via chat |
| Phase 6: US4 - Delete | 5 | Delete tasks via chat |
| Phase 7: US5 - Update | 6 | Update tasks via chat |
| Phase 8: US6 - History | 7 | Conversation persistence |
| Phase 9: US7 - Auth | 6 | Authentication & isolation |
| Phase 10: Polish | 10 | Error handling & docs |
| **Total** | **77** | |

### By Priority

- **P1 Stories** (MVP): US1, US2, US3, US7 = 26 tasks
- **P2 Stories**: US4, US5, US6 = 18 tasks
- **Infrastructure**: Setup + Foundational + Polish = 33 tasks

---

## Constitution Compliance Checks

### Principle 1: Spec-Driven Development (SDD) - MANDATORY
- [x] All tasks follow: Spec → Plan → Tasks → Implement sequence
- [x] Every task references a Task ID
- [x] Claude Code generates 100% of code (no manual coding)

### Principle 2: AI-Native Architecture
- [x] Tasks utilize Reusable Intelligence (OpenAI Agents SDK, MCP SDK)
- [x] Agentic Dev Stack: AGENTS.md + Spec-KitPlus + Claude Code

### Principle 3: Progressive Complexity
- [x] Tasks follow sequential phase completion (no skipping)
- [x] Phase 3 builds on Phase 2 foundation

### Principle 4: Cloud-Native First
- [x] Stateless design - all state in database
- [x] Horizontal scalability designed in

### Principle 5: Production Quality
- [x] Error handling tasks included
- [x] Documentation tasks included
- [x] Security (authentication) tasks included

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
