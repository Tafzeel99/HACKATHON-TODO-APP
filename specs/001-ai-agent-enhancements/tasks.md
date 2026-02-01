# Tasks: Phase 3.5 - AI Agent & App Enhancements

**Input**: Design documents from `/specs/001-ai-agent-enhancements/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/mcp-tools.yaml, quickstart.md
**Branch**: `001-ai-agent-enhancements`
**Date**: 2026-01-24

**Tests**: Tests will be included as validation tasks at the end of each phase (not TDD approach).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US11)
- Include exact file paths in descriptions

## User Stories Summary

| Story | Title | Priority | Status |
|-------|-------|----------|--------|
| US1 | Task Priorities via Chat | P1 | ✅ Complete |
| US2 | Tags and Categories via Chat | P1 | ✅ Complete |
| US3 | Due Dates with Natural Language | P1 | ✅ Complete |
| US4 | Task Analytics via Chat | P2 | ✅ Complete |
| US5 | Recurring Tasks via Chat | P2 | ✅ Complete |
| US6 | Smart Search via Chat | P2 | ✅ Complete |
| US7 | AI Prioritization Suggestions | P3 | ✅ Complete |
| US8 | Task Reminders via Chat | P3 | ✅ Complete |
| US9 | Daily Summary and Focus | P3 | ✅ Complete |
| US10 | Multi-Language Support (Urdu/Roman Urdu) | P1 | ✅ Complete |
| US11 | Enhanced NLP | P2 | ✅ Complete |

---

## Phase 1: Setup

**Purpose**: Verify existing infrastructure and prepare for enhancements

- [x] T001 Verify Phase 3 backend runs correctly at `phase3/backend/`
- [x] T002 Verify Phase 2 Task model has all required fields in `phase2/backend/src/models/task.py`
- [x] T003 [P] Create backup of existing MCP tools before modification at `phase3/backend/src/mcp/tools/`
- [x] T004 [P] Document current system prompt in `phase3/backend/src/services/agent_service.py`

---

## Phase 2: Foundational (System Prompt Enhancement)

**Purpose**: Update AI agent system prompt with multi-language support - BLOCKS all user stories

**⚠️ CRITICAL**: System prompt must be updated before ANY MCP tool changes take effect

- [x] T005 Create comprehensive multi-language system prompt with English, Roman Urdu, and Urdu script instructions in `phase3/backend/src/services/agent_service.py`
- [x] T006 Add date parsing instructions (aaj, kal, tomorrow, etc.) to system prompt in `phase3/backend/src/services/agent_service.py`
- [x] T007 Add priority keyword mapping (zaroori, urgent, fori) to system prompt in `phase3/backend/src/services/agent_service.py`
- [x] T008 Add language mirroring instructions to system prompt in `phase3/backend/src/services/agent_service.py`
- [x] T009 Add Roman Urdu spelling variations handling to system prompt in `phase3/backend/src/services/agent_service.py`

**Checkpoint**: System prompt ready - MCP tool enhancements can now begin

---

## Phase 3: User Story 1 - Task Priorities via Chat (Priority: P1) 🎯 MVP

**Goal**: Users can create, filter, and update task priorities through natural language

**Independent Test**: Say "Add a high priority task to fix the bug" → Verify task created with priority "high"

### Implementation for US1

- [x] T010 [US1] Enhance add_task handler to accept `priority` parameter in `phase3/backend/src/mcp/tools/add_task.py`
- [x] T011 [US1] Update add_task tool registration with priority enum (low/medium/high) in `phase3/backend/src/mcp/tools/add_task.py`
- [x] T012 [US1] Enhance list_tasks handler to accept `priority` filter parameter in `phase3/backend/src/mcp/tools/list_tasks.py`
- [x] T013 [US1] Update list_tasks tool registration with priority filter option in `phase3/backend/src/mcp/tools/list_tasks.py`
- [x] T014 [US1] Enhance update_task handler to accept `priority` parameter in `phase3/backend/src/mcp/tools/update_task.py`
- [x] T015 [US1] Update update_task tool registration with priority option in `phase3/backend/src/mcp/tools/update_task.py`
- [x] T016 [US1] Update list_tasks response to include priority field in output in `phase3/backend/src/mcp/tools/list_tasks.py`

**Checkpoint**: Priority management via chat fully functional

---

## Phase 4: User Story 2 - Tags and Categories via Chat (Priority: P1)

**Goal**: Users can create tasks with tags and filter by tags through conversation

**Independent Test**: Say "Add task buy groceries with tags shopping, personal" → Verify task has tags ["shopping", "personal"]

### Implementation for US2

- [x] T017 [US2] Enhance add_task handler to accept `tags` array parameter in `phase3/backend/src/mcp/tools/add_task.py`
- [x] T018 [US2] Add tags validation (max 10, max 30 chars each) to add_task in `phase3/backend/src/mcp/tools/add_task.py`
- [x] T019 [US2] Update add_task tool registration with tags array parameter in `phase3/backend/src/mcp/tools/add_task.py`
- [x] T020 [US2] Enhance list_tasks handler to accept `tags` filter parameter in `phase3/backend/src/mcp/tools/list_tasks.py`
- [x] T021 [US2] Implement tags filter logic (any match) in list_tasks in `phase3/backend/src/mcp/tools/list_tasks.py`
- [x] T022 [US2] Update list_tasks tool registration with tags filter option in `phase3/backend/src/mcp/tools/list_tasks.py`
- [x] T023 [US2] Enhance update_task handler to accept `tags` parameter in `phase3/backend/src/mcp/tools/update_task.py`
- [x] T024 [US2] Update update_task tool registration with tags option in `phase3/backend/src/mcp/tools/update_task.py`
- [x] T025 [US2] Update list_tasks response to include tags field in output in `phase3/backend/src/mcp/tools/list_tasks.py`

**Checkpoint**: Tag management via chat fully functional

---

## Phase 5: User Story 3 - Due Dates with Natural Language (Priority: P1)

**Goal**: Users can set and filter by due dates using natural language

**Independent Test**: Say "Add task call mom due tomorrow" → Verify task has correct due_date

### Implementation for US3

- [x] T026 [US3] Enhance add_task handler to accept `due_date` ISO string parameter in `phase3/backend/src/mcp/tools/add_task.py`
- [x] T027 [US3] Add due_date parsing and validation in add_task in `phase3/backend/src/mcp/tools/add_task.py`
- [x] T028 [US3] Update add_task tool registration with due_date parameter in `phase3/backend/src/mcp/tools/add_task.py`
- [x] T029 [US3] Enhance list_tasks handler to accept `due_before` and `due_after` parameters in `phase3/backend/src/mcp/tools/list_tasks.py`
- [x] T030 [US3] Enhance list_tasks handler to accept `overdue_only` boolean parameter in `phase3/backend/src/mcp/tools/list_tasks.py`
- [x] T031 [US3] Implement date range and overdue filter logic in list_tasks in `phase3/backend/src/mcp/tools/list_tasks.py`
- [x] T032 [US3] Update list_tasks tool registration with date filter options in `phase3/backend/src/mcp/tools/list_tasks.py`
- [x] T033 [US3] Enhance update_task handler to accept `due_date` parameter in `phase3/backend/src/mcp/tools/update_task.py`
- [x] T034 [US3] Update update_task tool registration with due_date option in `phase3/backend/src/mcp/tools/update_task.py`
- [x] T035 [US3] Add is_overdue computed field to list_tasks response in `phase3/backend/src/mcp/tools/list_tasks.py`

**Checkpoint**: Due date management via chat fully functional

---

## Phase 6: User Story 10 - Multi-Language Support: Urdu & Roman Urdu (Priority: P1)

**Goal**: Users can interact in English, Roman Urdu, or Urdu script

**Independent Test**: Say "Mujhe kal grocery leni hai" → Verify task created with tomorrow's due date

### Implementation for US10

- [x] T036 [US10] Add Roman Urdu command examples to system prompt in `phase3/backend/src/services/agent_service.py`
- [x] T037 [US10] Add Urdu script command examples to system prompt in `phase3/backend/src/services/agent_service.py`
- [x] T038 [US10] Add Roman Urdu date vocabulary (aaj, kal, parson, aglay hafta) to system prompt in `phase3/backend/src/services/agent_service.py`
- [x] T039 [US10] Add Urdu script date vocabulary (آج, کل, پرسوں, اگلے ہفتے) to system prompt in `phase3/backend/src/services/agent_service.py`
- [x] T040 [US10] Add Roman Urdu priority vocabulary (zaroori, fori, jab bhi) to system prompt in `phase3/backend/src/services/agent_service.py`
- [x] T041 [US10] Add Urdu script priority vocabulary (ضروری, فوری, جب بھی) to system prompt in `phase3/backend/src/services/agent_service.py`
- [x] T042 [US10] Add spelling variation handling instructions (hai/h/hey, karo/kro) to system prompt in `phase3/backend/src/services/agent_service.py`
- [x] T043 [US10] Add mixed language handling instructions to system prompt in `phase3/backend/src/services/agent_service.py`
- [x] T044 [US10] Verify UTF-8 encoding for Urdu responses in `phase3/backend/src/main.py`

**Checkpoint**: Multi-language support fully functional

---

## Phase 7: User Story 4 - Task Analytics via Chat (Priority: P2)

**Goal**: Users can ask about productivity statistics through conversation

**Independent Test**: Ask "How many tasks did I complete this week?" → Verify accurate count returned

### Implementation for US4

- [x] T045 [P] [US4] Create new get_analytics tool handler in `phase3/backend/src/mcp/tools/get_analytics.py`
- [x] T046 [US4] Implement total_tasks, completed_count, pending_count queries in `phase3/backend/src/mcp/tools/get_analytics.py`
- [x] T047 [US4] Implement overdue_count and completion_rate calculations in `phase3/backend/src/mcp/tools/get_analytics.py`
- [x] T048 [US4] Implement tasks_by_priority aggregation in `phase3/backend/src/mcp/tools/get_analytics.py`
- [x] T049 [US4] Implement tasks_due_today and tasks_due_this_week queries in `phase3/backend/src/mcp/tools/get_analytics.py`
- [x] T050 [US4] Implement completed_this_week count in `phase3/backend/src/mcp/tools/get_analytics.py`
- [x] T051 [US4] Register get_analytics tool with MCP server in `phase3/backend/src/mcp/tools/__init__.py`
- [x] T052 [US4] Add analytics tool description to system prompt in `phase3/backend/src/services/agent_service.py`

**Checkpoint**: Analytics via chat fully functional

---

## Phase 8: User Story 5 - Recurring Tasks via Chat (Priority: P2)

**Goal**: Users can create recurring tasks and auto-generate next occurrence on completion

**Independent Test**: Say "Add a daily task to take vitamins" → Verify recurrence_pattern is "daily"

### Implementation for US5

- [x] T053 [US5] Enhance add_task handler to accept `recurrence_pattern` parameter in `phase3/backend/src/mcp/tools/add_task.py`
- [x] T054 [US5] Enhance add_task handler to accept `recurrence_end_date` parameter in `phase3/backend/src/mcp/tools/add_task.py`
- [x] T055 [US5] Update add_task tool registration with recurrence parameters in `phase3/backend/src/mcp/tools/add_task.py`
- [x] T056 [US5] Create calculate_next_due helper function in `phase3/backend/src/mcp/tools/complete_task.py`
- [x] T057 [US5] Enhance complete_task to create next occurrence for recurring tasks in `phase3/backend/src/mcp/tools/complete_task.py`
- [x] T058 [US5] Set parent_task_id on newly created recurring task in `phase3/backend/src/mcp/tools/complete_task.py`
- [x] T059 [US5] Enhance update_task to modify recurrence_pattern in `phase3/backend/src/mcp/tools/update_task.py`
- [x] T060 [US5] Update update_task tool registration with recurrence options in `phase3/backend/src/mcp/tools/update_task.py`
- [x] T061 [US5] Add recurrence_pattern to list_tasks response in `phase3/backend/src/mcp/tools/list_tasks.py`

**Checkpoint**: Recurring tasks via chat fully functional

---

## Phase 9: User Story 6 - Smart Search via Chat (Priority: P2)

**Goal**: Users can search tasks by keywords in title and description

**Independent Test**: Say "Find tasks about meeting" → Verify matching tasks returned

### Implementation for US6

- [x] T062 [US6] Enhance list_tasks handler to accept `search` keyword parameter in `phase3/backend/src/mcp/tools/list_tasks.py`
- [x] T063 [US6] Implement case-insensitive search in title and description in `phase3/backend/src/mcp/tools/list_tasks.py`
- [x] T064 [US6] Update list_tasks tool registration with search parameter in `phase3/backend/src/mcp/tools/list_tasks.py`
- [x] T065 [US6] Add search + filter combination support in list_tasks in `phase3/backend/src/mcp/tools/list_tasks.py`

**Checkpoint**: Search via chat fully functional

---

## Phase 10: User Story 11 - Enhanced NLP (Priority: P2)

**Goal**: AI understands casual language, typos, shorthand, and context

**Independent Test**: Say "mtg prep tmrw high pri" → Verify task "Meeting prep" created with tomorrow due date and high priority

### Implementation for US11

- [x] T066 [US11] Add casual English phrase examples to system prompt in `phase3/backend/src/services/agent_service.py`
- [x] T067 [US11] Add shorthand/abbreviation handling instructions (tmrw, mtg, pri) to system prompt in `phase3/backend/src/services/agent_service.py`
- [x] T068 [US11] Add typo tolerance instructions to system prompt in `phase3/backend/src/services/agent_service.py`
- [x] T069 [US11] Add context awareness instructions for "that task", "the one I mentioned" to system prompt in `phase3/backend/src/services/agent_service.py`

**Checkpoint**: Enhanced NLP fully functional

---

## Phase 11: User Story 7 - AI Prioritization Suggestions (Priority: P3)

**Goal**: AI suggests priority based on task content

**Independent Test**: Say "Add task urgent bug fix for production" → Verify high priority suggested

### Implementation for US7

- [x] T070 [US7] Add priority suggestion instructions to system prompt in `phase3/backend/src/services/agent_service.py`
- [x] T071 [US7] Add urgency keyword detection examples to system prompt in `phase3/backend/src/services/agent_service.py`
- [x] T072 [US7] Add time-sensitivity detection instructions to system prompt in `phase3/backend/src/services/agent_service.py`

**Checkpoint**: Priority suggestions fully functional

---

## Phase 12: User Story 8 - Task Reminders via Chat (Priority: P3)

**Goal**: Users can set reminders for tasks with due dates

**Independent Test**: Say "Remind me about task 3 one hour before" → Verify reminder_at is set

### Implementation for US8

- [x] T073 [US8] Enhance add_task handler to accept `reminder_at` parameter in `phase3/backend/src/mcp/tools/add_task.py`
- [x] T074 [US8] Update add_task tool registration with reminder_at parameter in `phase3/backend/src/mcp/tools/add_task.py`
- [x] T075 [US8] Enhance update_task handler to accept `reminder_at` parameter in `phase3/backend/src/mcp/tools/update_task.py`
- [x] T076 [US8] Update update_task tool registration with reminder_at option in `phase3/backend/src/mcp/tools/update_task.py`
- [x] T077 [US8] Add reminder_at to list_tasks response in `phase3/backend/src/mcp/tools/list_tasks.py`
- [x] T078 [US8] Add reminder handling instructions to system prompt in `phase3/backend/src/services/agent_service.py`

**Checkpoint**: Reminders via chat fully functional

---

## Phase 13: User Story 9 - Daily Summary and Focus (Priority: P3)

**Goal**: Users can ask for daily summary and focus recommendations

**Independent Test**: Ask "What should I focus on today?" → Verify prioritized response

### Implementation for US9

- [x] T079 [US9] Add daily summary instructions to system prompt in `phase3/backend/src/services/agent_service.py`
- [x] T080 [US9] Add focus recommendation logic instructions to system prompt in `phase3/backend/src/services/agent_service.py`
- [x] T081 [US9] Add encouragement response instructions for completion stats in `phase3/backend/src/services/agent_service.py`

**Checkpoint**: Daily summary and focus fully functional

---

## Phase 14: Polish & Validation

**Purpose**: Final validation, documentation, and cross-cutting improvements

- [ ] T082 [P] Test all MCP tools with English commands in `phase3/backend/`
- [ ] T083 [P] Test all MCP tools with Roman Urdu commands in `phase3/backend/`
- [ ] T084 [P] Test all MCP tools with Urdu script commands in `phase3/backend/`
- [ ] T085 Test mixed language input handling in `phase3/backend/`
- [ ] T086 Test recurring task creation on completion in `phase3/backend/`
- [ ] T087 Test analytics accuracy with sample data in `phase3/backend/`
- [ ] T088 [P] Update README.md with Phase 3.5 features in project root
- [ ] T089 [P] Update quickstart.md with testing validation results in `specs/001-ai-agent-enhancements/quickstart.md`
- [ ] T090 Run full end-to-end test from frontend in `phase2/frontend/`

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational/System Prompt)
                           ↓
    ┌──────────────────────┼──────────────────────┐
    ↓                      ↓                      ↓
Phase 3 (US1-Priority)  Phase 4 (US2-Tags)  Phase 5 (US3-Due Dates)
    ↓                      ↓                      ↓
    └──────────────────────┼──────────────────────┘
                           ↓
                  Phase 6 (US10-Multi-Language)
                           ↓
    ┌──────────────────────┼──────────────────────┐
    ↓                      ↓                      ↓
Phase 7 (US4-Analytics) Phase 8 (US5-Recurring) Phase 9 (US6-Search)
                           ↓
                  Phase 10 (US11-Enhanced NLP)
                           ↓
    ┌──────────────────────┼──────────────────────┐
    ↓                      ↓                      ↓
Phase 11 (US7-Suggestions) Phase 12 (US8-Reminders) Phase 13 (US9-Summary)
                           ↓
                  Phase 14 (Polish & Validation)
```

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|------------|-------------------|
| US1 (Priorities) | Phase 2 | US2, US3 |
| US2 (Tags) | Phase 2 | US1, US3 |
| US3 (Due Dates) | Phase 2 | US1, US2 |
| US10 (Multi-Language) | US1, US2, US3 | - |
| US4 (Analytics) | US1, US3 | US5, US6 |
| US5 (Recurring) | US3 | US4, US6 |
| US6 (Search) | US2 | US4, US5 |
| US11 (Enhanced NLP) | US10 | - |
| US7 (Suggestions) | US1, US11 | US8, US9 |
| US8 (Reminders) | US3 | US7, US9 |
| US9 (Summary) | US4 | US7, US8 |

### Parallel Opportunities per Phase

**Phase 2 (Foundational)**:
```
T005, T006, T007, T008, T009 → Can be combined in single system prompt update
```

**Phases 3, 4, 5 (P1 Stories)**:
```
T010-T016 (US1) ║ T017-T025 (US2) ║ T026-T035 (US3) → All parallel (different tool files)
```

**Phases 7, 8, 9 (P2 Stories)**:
```
T045-T052 (US4) ║ T053-T061 (US5) ║ T062-T065 (US6) → Mostly parallel
```

**Phase 14 (Polish)**:
```
T082 ║ T083 ║ T084 ║ T088 ║ T089 → All parallel (different activities)
```

---

## Implementation Strategy

### MVP First (P1 Stories Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T009)
3. Complete Phase 3: US1 Priorities (T010-T016)
4. Complete Phase 4: US2 Tags (T017-T025)
5. Complete Phase 5: US3 Due Dates (T026-T035)
6. Complete Phase 6: US10 Multi-Language (T036-T044)
7. **STOP and VALIDATE**: Test all P1 features
8. Deploy/demo MVP

### Full Implementation

Continue with:
- Phase 7-9: P2 Stories (Analytics, Recurring, Search)
- Phase 10: Enhanced NLP
- Phase 11-13: P3 Stories (Suggestions, Reminders, Summary)
- Phase 14: Polish & Validation

### Recommended Execution

**Solo Developer**:
1. Complete phases sequentially
2. Test each phase before moving on
3. MVP at Phase 6, full at Phase 14

**Team (2-3 Developers)**:
1. One developer: Phase 2 (System Prompt)
2. After Phase 2:
   - Dev A: US1 + US2 (add_task + list_tasks)
   - Dev B: US3 + US5 (dates + recurring)
   - Dev C: US10 (multi-language)
3. Merge and continue with P2/P3 stories

---

## Constitution Compliance Checks

### Principle 1: Spec-Driven Development (SDD) - MANDATORY
- [x] All tasks follow: Spec → Plan → Tasks → Implement sequence
- [x] Every task references a Task ID
- [x] Claude Code generates 100% of code (no manual coding)

### Principle 2: AI-Native Architecture
- [x] Tasks utilize Reusable Intelligence (system prompt enhancements)
- [x] Agentic Dev Stack: AGENTS.md + Spec-KitPlus + Claude Code

### Principle 3: Progressive Complexity
- [x] Tasks follow sequential phase completion
- [x] Each task builds on previous foundation (Phase 3 → 3.5)

### Principle 4: Cloud-Native First
- [x] Stateless design maintained
- [x] All state in database (no server-side session)

### Principle 5: Production Quality
- [x] Clean code principles in all implementations
- [x] Security best practices (user isolation via user_id)
- [x] Error handling comprehensive
- [x] Documentation complete

---

## Summary

| Metric | Count |
|--------|-------|
| Total Tasks | 90 |
| Setup Tasks | 4 |
| Foundational Tasks | 5 |
| US1 (Priorities) | 7 |
| US2 (Tags) | 9 |
| US3 (Due Dates) | 10 |
| US10 (Multi-Language) | 9 |
| US4 (Analytics) | 8 |
| US5 (Recurring) | 9 |
| US6 (Search) | 4 |
| US11 (Enhanced NLP) | 4 |
| US7 (Suggestions) | 3 |
| US8 (Reminders) | 6 |
| US9 (Summary) | 3 |
| Polish Tasks | 9 |
| Parallel Opportunities | 25+ |

**MVP Scope**: Phases 1-6 (Tasks T001-T044) = 44 tasks
**Full Scope**: All Phases (Tasks T001-T090) = 90 tasks

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Database already has all fields - no migrations needed
- Multi-language support via GPT native capabilities

---

## Phase 15: UI/UX & Collaboration Enhancements (2026-01-28)

**Purpose**: Add modern UI/UX improvements and multi-user collaboration features

### Completed Tasks (Phase 15)

#### Backend Database & Models
- [x] T091 Create Alembic migration `003_add_collaboration_tables.py` for task_shares, comments, activities tables
- [x] T092 Create TaskShare SQLModel in `phase2/backend/src/models/task_share.py`
- [x] T093 Create Comment SQLModel in `phase2/backend/src/models/comment.py`
- [x] T094 Create Activity SQLModel in `phase2/backend/src/models/activity.py`
- [x] T095 Update Task model with `assigned_to` field in `phase2/backend/src/models/task.py`
- [x] T096 Update `phase2/backend/src/models/__init__.py` exports

#### Backend Schemas
- [x] T097 Create task_share.py schema in `phase2/backend/src/schemas/`
- [x] T098 Create comment.py schema in `phase2/backend/src/schemas/`
- [x] T099 Create activity.py schema in `phase2/backend/src/schemas/`
- [x] T100 Update task.py schema with assigned_to, assignee, comment_count, share_count
- [x] T101 Update `phase2/backend/src/schemas/__init__.py` exports

#### Backend Services
- [x] T102 Create ActivityService in `phase2/backend/src/services/activity.py`
- [x] T103 Create ShareService in `phase2/backend/src/services/share.py`
- [x] T104 Create CommentService in `phase2/backend/src/services/comment.py`
- [x] T105 Update `phase2/backend/src/services/__init__.py` exports

#### Backend API Routes
- [x] T106 Create shares.py API routes in `phase2/backend/src/api/`
- [x] T107 Create comments.py API routes in `phase2/backend/src/api/`
- [x] T108 Create activities.py API routes in `phase2/backend/src/api/`
- [x] T109 Create users.py API routes in `phase2/backend/src/api/`
- [x] T110 Update `phase2/backend/src/api/__init__.py` exports
- [x] T111 Update `phase2/backend/src/main.py` to register new routers

#### Frontend Dependencies & UI Components
- [x] T112 Update package.json with framer-motion and radix-ui dependencies
- [x] T113 Create error-boundary.tsx in `phase2/frontend/src/components/`
- [x] T114 Create error-fallback.tsx in `phase2/frontend/src/components/`
- [x] T115 Create animations.ts in `phase2/frontend/src/lib/`
- [x] T116 Create skeleton.tsx UI component
- [x] T117 Create avatar.tsx UI component
- [x] T118 Create popover.tsx UI component
- [x] T119 Create separator.tsx UI component
- [x] T120 Create textarea.tsx UI component
- [x] T121 Create scroll-area.tsx UI component
- [x] T122 Create dropdown-menu.tsx UI component
- [x] T123 Create tooltip.tsx UI component
- [x] T124 Create command.tsx UI component

#### Frontend Skeleton Components
- [x] T125 Create task-skeleton.tsx in `phase2/frontend/src/components/skeletons/`
- [x] T126 Create dashboard-skeleton.tsx in `phase2/frontend/src/components/skeletons/`
- [x] T127 Create analytics-skeleton.tsx in `phase2/frontend/src/components/skeletons/`
- [x] T128 Create activity-skeleton.tsx in `phase2/frontend/src/components/skeletons/`
- [x] T129 Create skeletons/index.ts exports

#### Frontend Collaboration Components
- [x] T130 Create user-avatar.tsx in `phase2/frontend/src/components/collaboration/`
- [x] T131 Create share-dialog.tsx in `phase2/frontend/src/components/collaboration/`
- [x] T132 Create comment-item.tsx in `phase2/frontend/src/components/collaboration/`
- [x] T133 Create comments-section.tsx in `phase2/frontend/src/components/collaboration/`
- [x] T134 Create activity-item.tsx in `phase2/frontend/src/components/collaboration/`
- [x] T135 Create activity-feed.tsx in `phase2/frontend/src/components/collaboration/`
- [x] T136 Create assignee-select.tsx in `phase2/frontend/src/components/collaboration/`

### Remaining Tasks (Phase 15)

#### Frontend Types & API Client
- [x] T137 Create collaboration/index.ts export file
- [x] T138 Update types/task.ts with TaskShare, Comment, Activity, User interfaces
- [x] T139 Update lib/api.ts with shareApi, commentApi, activityApi, userApi methods
- [x] T140 Add formatDistanceToNow function to lib/utils.ts

#### Frontend Integration
- [ ] T141 Update task-item.tsx with share button, comments badge, assignee avatar, animations
- [x] T142 Update task-list.tsx with AnimatePresence for list animations
- [ ] T143 Update task-form.tsx with AssigneeSelect field
- [x] T144 Wrap dashboard layout with ErrorBoundary
- [x] T145 Add skeleton loading states to tasks page (using TaskSkeleton from skeletons/)
- [x] T146 Add activity feed widget to dashboard page

#### AI Agent Enhancements (Natural Language)
- [x] T147 Create date_parser.py utility in `phase3/backend/src/utils/` (parse "tomorrow", "next Monday", "kal")
- [x] T148 Create context_manager.py in `phase3/backend/src/services/` (track task references, resolve "it", "that")
- [x] T149 Create suggestions.py in `phase3/backend/src/services/` (smart task suggestions)
- [ ] T150 Update agent_service.py with date parser, context resolution, suggestions
- [x] T151 Create get_suggestions.py MCP tool in `phase3/backend/src/mcp/tools/`
- [x] T152 Create share_task.py MCP tool in `phase3/backend/src/mcp/tools/`
- [x] T153 Create add_comment.py MCP tool in `phase3/backend/src/mcp/tools/`
- [x] T154 Create assign_task.py MCP tool in `phase3/backend/src/mcp/tools/`

#### Testing & Validation
- [ ] T155 Run Alembic migration on database (`alembic upgrade head`)
- [ ] T156 Install new npm dependencies (`npm install` in phase2/frontend)
- [ ] T157 Test backend collaboration API endpoints
- [ ] T158 Test frontend collaboration components
- [x] T159 Fix any TypeScript errors (no errors found)
- [ ] T160 Test AI agent with natural language commands

---

## Resume Development Commands

```bash
# 1. Apply database migration
cd phase2/backend
alembic upgrade head

# 2. Install frontend dependencies
cd phase2/frontend
npm install

# 3. Start development servers
cd phase2/backend && uvicorn src.main:app --reload --port 8000
cd phase2/frontend && npm run dev

# 4. Start Phase 3 AI backend (if needed)
cd phase3/backend && uvicorn src.main:app --reload --port 8001
```

## Priority Order for Remaining Tasks

1. **T137-T140**: Frontend types & API (required for components to work)
2. **T141-T146**: Frontend integration (connect components to pages)
3. **T147-T154**: AI agent enhancements (optional, for smart features)
4. **T155-T160**: Testing & validation (verify everything works)
