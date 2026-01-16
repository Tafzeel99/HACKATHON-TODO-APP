# Tasks: Phase II - Todo Full-Stack Web Application

**Input**: Design documents from `/specs/phase2-full-stack/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/openapi.yaml
**Branch**: `phase2-full-stack`
**Date**: 2026-01-16

**Tests**: Tests are included as this is a production-quality Phase II implementation requiring 70% coverage per constitution.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `phase2/backend/src/`, `phase2/backend/tests/`
- **Frontend**: `phase2/frontend/src/`, `phase2/frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and folder structure creation

- [x] T001 Create phase2 root folder structure with backend/ and frontend/ directories
- [x] T002 [P] Initialize Python backend project with pyproject.toml in phase2/backend/pyproject.toml
- [x] T003 [P] Initialize Next.js frontend project with package.json in phase2/frontend/package.json
- [x] T004 [P] Create backend folder structure: src/, tests/, alembic/ in phase2/backend/
- [x] T005 [P] Create frontend folder structure: src/app/, src/components/, src/lib/, src/types/ in phase2/frontend/
- [x] T006 [P] Configure Ruff linting for backend in phase2/backend/pyproject.toml
- [x] T007 [P] Configure ESLint and TypeScript for frontend in phase2/frontend/
- [x] T008 [P] Create backend .env.example with required environment variables in phase2/backend/.env.example
- [x] T009 [P] Create frontend .env.example with required environment variables in phase2/frontend/.env.example
- [x] T010 Create phase2/README.md with project overview and setup instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Foundation

- [x] T011 Create environment configuration with Pydantic Settings in phase2/backend/src/config.py
- [x] T012 Create database connection with async SQLModel engine in phase2/backend/src/database.py
- [x] T013 [P] Create User SQLModel in phase2/backend/src/models/user.py
- [x] T014 [P] Create Task SQLModel in phase2/backend/src/models/task.py
- [x] T015 Create models __init__.py with exports in phase2/backend/src/models/__init__.py
- [x] T016 [P] Create User Pydantic schemas (UserCreate, UserLogin, UserResponse, TokenResponse) in phase2/backend/src/schemas/user.py
- [x] T017 [P] Create Task Pydantic schemas (TaskCreate, TaskUpdate, TaskResponse, TaskListResponse) in phase2/backend/src/schemas/task.py
- [x] T018 Create schemas __init__.py with exports in phase2/backend/src/schemas/__init__.py
- [x] T019 Setup Alembic configuration in phase2/backend/alembic/env.py
- [x] T020 Create initial database migration for users and tasks tables in phase2/backend/alembic/versions/001_initial_schema.py
- [x] T021 Create JWT authentication dependency (get_current_user) in phase2/backend/src/api/deps.py
- [x] T022 Create FastAPI app entry point with CORS and routers in phase2/backend/src/main.py
- [x] T023 Create backend src __init__.py in phase2/backend/src/__init__.py

### Frontend Foundation

- [x] T024 Configure Tailwind CSS in phase2/frontend/tailwind.config.ts
- [x] T025 Initialize shadcn/ui with required components (button, input, card, form, toast) in phase2/frontend/
- [x] T026 Create TypeScript types for User in phase2/frontend/src/types/user.ts
- [x] T027 Create TypeScript types for Task in phase2/frontend/src/types/task.ts
- [x] T028 Create Better Auth client configuration in phase2/frontend/src/lib/auth.ts
- [x] T029 Create API client with fetch wrapper and auth header injection in phase2/frontend/src/lib/api.ts
- [x] T030 Create utility functions (cn, formatDate) in phase2/frontend/src/lib/utils.ts
- [x] T031 Create root layout with providers in phase2/frontend/src/app/layout.tsx
- [x] T032 Create landing page (redirect to login or dashboard) in phase2/frontend/src/app/page.tsx

### Test Infrastructure

- [x] T033 Create pytest configuration and fixtures (async client, auth headers, test db) in phase2/backend/tests/conftest.py
- [x] T034 Create backend tests __init__.py in phase2/backend/tests/__init__.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - New User Signup and First Task (Priority: P1) 🎯 MVP

**Goal**: Enable new users to create an account, log in, and add their first task

**Independent Test**: Sign up with new email, log in, create one task, verify it appears in list

**From spec.md**: User Story 1 - New User Signup and First Task

### Backend Implementation for User Story 1

- [x] T035 [US1] Create auth service with signup and signin logic in phase2/backend/src/services/auth.py
- [x] T036 [US1] Create task service with create operation in phase2/backend/src/services/task.py
- [x] T037 [US1] Create services __init__.py with exports in phase2/backend/src/services/__init__.py
- [x] T038 [US1] Create auth router with POST /api/auth/signup endpoint in phase2/backend/src/api/auth.py
- [x] T039 [US1] Add POST /api/auth/signin endpoint to auth router in phase2/backend/src/api/auth.py
- [x] T040 [US1] Create tasks router with POST /api/tasks endpoint in phase2/backend/src/api/tasks.py
- [x] T041 [US1] Add GET /api/tasks endpoint for listing user tasks in phase2/backend/src/api/tasks.py
- [x] T042 [US1] Create api __init__.py with router exports in phase2/backend/src/api/__init__.py

### Frontend Implementation for User Story 1

- [x] T043 [P] [US1] Create signup form component in phase2/frontend/src/components/auth/signup-form.tsx
- [x] T044 [P] [US1] Create login form component in phase2/frontend/src/components/auth/login-form.tsx
- [x] T045 [US1] Create signup page in phase2/frontend/src/app/(auth)/signup/page.tsx
- [x] T046 [US1] Create login page in phase2/frontend/src/app/(auth)/login/page.tsx
- [x] T047 [US1] Create protected dashboard layout with auth check in phase2/frontend/src/app/(dashboard)/layout.tsx
- [x] T048 [US1] Create task form component for adding tasks in phase2/frontend/src/components/tasks/task-form.tsx
- [x] T049 [US1] Create task list component in phase2/frontend/src/components/tasks/task-list.tsx
- [x] T050 [US1] Create task item component in phase2/frontend/src/components/tasks/task-item.tsx
- [x] T051 [US1] Create tasks dashboard page in phase2/frontend/src/app/(dashboard)/tasks/page.tsx

### Tests for User Story 1

- [x] T052 [P] [US1] Write auth endpoint tests (signup, signin) in phase2/backend/tests/test_auth.py
- [x] T053 [P] [US1] Write task creation and listing tests in phase2/backend/tests/test_tasks.py

**Checkpoint**: User Story 1 complete - users can signup, login, create tasks, view task list

---

## Phase 4: User Story 2 - Existing User Task Management (Priority: P2)

**Goal**: Enable returning users to manage existing tasks (view, update, complete, delete)

**Independent Test**: Login with existing credentials, view tasks, update one, mark another complete, delete a third

**From spec.md**: User Story 2 - Existing User Task Management

### Backend Implementation for User Story 2

- [x] T054 [US2] Add get_by_id operation to task service in phase2/backend/src/services/task.py
- [x] T055 [US2] Add update operation to task service in phase2/backend/src/services/task.py
- [x] T056 [US2] Add delete operation to task service in phase2/backend/src/services/task.py
- [x] T057 [US2] Add toggle_complete operation to task service in phase2/backend/src/services/task.py
- [x] T058 [US2] Add GET /api/tasks/{task_id} endpoint in phase2/backend/src/api/tasks.py
- [x] T059 [US2] Add PUT /api/tasks/{task_id} endpoint in phase2/backend/src/api/tasks.py
- [x] T060 [US2] Add DELETE /api/tasks/{task_id} endpoint in phase2/backend/src/api/tasks.py
- [x] T061 [US2] Add PATCH /api/tasks/{task_id}/complete endpoint in phase2/backend/src/api/tasks.py
- [x] T062 [US2] Add POST /api/auth/signout endpoint in phase2/backend/src/api/auth.py

### Frontend Implementation for User Story 2

- [x] T063 [US2] Add edit functionality to task-item component in phase2/frontend/src/components/tasks/task-item.tsx
- [x] T064 [US2] Add complete toggle functionality to task-item component in phase2/frontend/src/components/tasks/task-item.tsx
- [x] T065 [US2] Add delete functionality with confirmation to task-item component in phase2/frontend/src/components/tasks/task-item.tsx
- [x] T066 [US2] Add edit task modal/form to tasks page in phase2/frontend/src/app/(dashboard)/tasks/page.tsx
- [x] T067 [US2] Add logout button to dashboard layout in phase2/frontend/src/app/(dashboard)/layout.tsx

### Tests for User Story 2

- [x] T068 [P] [US2] Write task CRUD tests (get, update, delete) in phase2/backend/tests/test_tasks.py
- [x] T069 [P] [US2] Write task completion toggle tests in phase2/backend/tests/test_tasks.py

**Checkpoint**: User Story 2 complete - full task lifecycle management working

---

## Phase 5: User Story 3 - Task Filtering and Organization (Priority: P3)

**Goal**: Enable users to filter tasks by status and sort by different fields

**Independent Test**: Create 5 tasks (3 pending, 2 completed), filter by status, sort by title/date

**From spec.md**: User Story 3 - Task Filtering and Organization

### Backend Implementation for User Story 3

- [x] T070 [US3] Add filtering by status (all/pending/completed) to task service in phase2/backend/src/services/task.py
- [x] T071 [US3] Add sorting by created_at and title to task service in phase2/backend/src/services/task.py
- [x] T072 [US3] Update GET /api/tasks endpoint with query params (status, sort, order) in phase2/backend/src/api/tasks.py

### Frontend Implementation for User Story 3

- [x] T073 [US3] Create task-filters component with status and sort dropdowns in phase2/frontend/src/components/tasks/task-filters.tsx
- [x] T074 [US3] Integrate filters into tasks page with state management in phase2/frontend/src/app/(dashboard)/tasks/page.tsx
- [x] T075 [US3] Update API client to support filter and sort query params in phase2/frontend/src/lib/api.ts

### Tests for User Story 3

- [x] T076 [P] [US3] Write task filtering tests in phase2/backend/tests/test_tasks.py
- [x] T077 [P] [US3] Write task sorting tests in phase2/backend/tests/test_tasks.py

**Checkpoint**: User Story 3 complete - filtering and sorting working

---

## Phase 6: User Story 4 - Security and Access Control (Priority: P4)

**Goal**: Ensure unauthorized access is prevented and authentication failures are handled gracefully

**Independent Test**: Access protected routes without login, use invalid credentials, attempt to access another user's tasks

**From spec.md**: User Story 4 - Security and Access Control

### Backend Implementation for User Story 4

- [x] T078 [US4] Add user ownership validation to all task endpoints in phase2/backend/src/api/tasks.py
- [x] T079 [US4] Add proper error responses for 401/403/404 in task endpoints in phase2/backend/src/api/tasks.py
- [x] T080 [US4] Add password validation (min 8 chars) to signup in phase2/backend/src/api/auth.py
- [x] T081 [US4] Add duplicate email handling (409 Conflict) to signup in phase2/backend/src/api/auth.py
- [x] T082 [US4] Add token expiration handling in auth dependency in phase2/backend/src/api/deps.py

### Frontend Implementation for User Story 4

- [x] T083 [US4] Add auth redirect for unauthenticated access in dashboard layout in phase2/frontend/src/app/(dashboard)/layout.tsx
- [x] T084 [US4] Add error handling for invalid credentials in login form in phase2/frontend/src/components/auth/login-form.tsx
- [x] T085 [US4] Add password validation in signup form in phase2/frontend/src/components/auth/signup-form.tsx
- [x] T086 [US4] Add global error handling for 401 responses (redirect to login) in phase2/frontend/src/lib/api.ts
- [x] T087 [US4] Add loading states during API operations in task components in phase2/frontend/src/components/tasks/

### Tests for User Story 4

- [x] T088 [P] [US4] Write auth security tests (invalid token, expired token) in phase2/backend/tests/test_auth.py
- [x] T089 [P] [US4] Write task access control tests (403 for other user's tasks) in phase2/backend/tests/test_tasks.py
- [x] T090 [P] [US4] Write validation tests (password length, duplicate email) in phase2/backend/tests/test_auth.py

**Checkpoint**: User Story 4 complete - security and access control working

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T091 [P] Add comprehensive error handling and user-friendly messages across frontend components
- [x] T092 [P] Add loading skeletons for task list in phase2/frontend/src/components/tasks/task-list.tsx
- [x] T093 [P] Add toast notifications for success/error feedback in phase2/frontend/src/components/
- [x] T094 Implement responsive design for mobile (320px+) across all pages
- [x] T095 Add health check endpoint at GET /health in phase2/backend/src/main.py
- [x] T096 [P] Create backend README.md with API documentation in phase2/backend/README.md
- [x] T097 [P] Create frontend README.md with setup instructions in phase2/frontend/README.md
- [x] T098 Run pytest with coverage report and verify 70% minimum in phase2/backend/ (73% achieved)
- [x] T099 Run ESLint and fix any issues in phase2/frontend/
- [x] T100 Validate quickstart.md instructions work end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKS ALL USER STORIES
    ↓
┌───────────────────────────────────────────────┐
│ User Stories can proceed in parallel or       │
│ sequentially after Foundation is complete     │
├───────────────────────────────────────────────┤
│ Phase 3: US1 (P1) - Signup + First Task  🎯   │
│ Phase 4: US2 (P2) - Task Management          │
│ Phase 5: US3 (P3) - Filtering/Sorting        │
│ Phase 6: US4 (P4) - Security                 │
└───────────────────────────────────────────────┘
    ↓
Phase 7 (Polish)
```

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 2 - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Phase 2 - Builds on US1 task infrastructure but independently testable
- **User Story 3 (P3)**: Can start after Phase 2 - Builds on US1/US2 list display but independently testable
- **User Story 4 (P4)**: Can start after Phase 2 - Cross-cutting security but independently testable

### Within Each User Story

- Backend services before API endpoints
- API endpoints before frontend integration
- Core implementation before tests
- Story complete = backend + frontend + tests passing

### Parallel Opportunities

**Phase 1 (Setup)**:
- T002, T003 can run in parallel (backend/frontend init)
- T004, T005 can run in parallel (folder structures)
- T006, T007, T008, T009 can run in parallel (configs)

**Phase 2 (Foundational)**:
- T013, T014 can run in parallel (User/Task models)
- T016, T017 can run in parallel (User/Task schemas)
- T024-T030 frontend tasks can run in parallel with backend T011-T023

**User Stories**:
- All user stories can start in parallel after Phase 2 (if team capacity allows)
- Within each story, backend and frontend can partially overlap

---

## Parallel Example: Phase 2 Foundation

```bash
# Launch backend model tasks in parallel:
Task: "Create User SQLModel in phase2/backend/src/models/user.py"
Task: "Create Task SQLModel in phase2/backend/src/models/task.py"

# Launch schema tasks in parallel:
Task: "Create User Pydantic schemas in phase2/backend/src/schemas/user.py"
Task: "Create Task Pydantic schemas in phase2/backend/src/schemas/task.py"

# Launch frontend type tasks in parallel:
Task: "Create TypeScript types for User in phase2/frontend/src/types/user.ts"
Task: "Create TypeScript types for Task in phase2/frontend/src/types/task.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T010)
2. Complete Phase 2: Foundational (T011-T034)
3. Complete Phase 3: User Story 1 (T035-T053)
4. **STOP and VALIDATE**: Test signup → login → create task → view list
5. Deploy/demo if ready - this is the MVP!

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy (MVP!)
3. Add User Story 2 → Full task management → Deploy
4. Add User Story 3 → Filtering/sorting → Deploy
5. Add User Story 4 → Security hardened → Deploy
6. Polish → Production ready

### Full Implementation

1. Complete all phases sequentially: 1 → 2 → 3 → 4 → 5 → 6 → 7
2. Run full test suite after each user story
3. Verify 70% coverage at Phase 7

---

## Constitution Compliance Checks

### Principle 1: Spec-Driven Development (SDD) - MANDATORY
- [x] All tasks follow: Spec → Plan → Tasks → Implement sequence
- [x] Every task references a Task ID
- [x] Claude Code will generate 100% of code (no manual coding)

### Principle 2: AI-Native Architecture
- [x] Tasks utilize Reusable Intelligence (Skills, Agents)
- [x] Agentic Dev Stack: AGENTS.md + Spec-KitPlus + Claude Code

### Principle 3: Progressive Complexity
- [x] Tasks follow sequential phase completion (no skipping)
- [x] Phase II builds on Phase I foundation (console → web)

### Principle 4: Cloud-Native First
- [x] Stateless backend design (JWT-based auth)
- [x] Environment-driven configuration
- [x] Serverless database (Neon PostgreSQL)

### Principle 5: Production Quality
- [x] Clean code principles (Ruff, ESLint)
- [x] Security best practices (Better Auth, JWT, input validation)
- [x] Error handling comprehensive
- [x] 70% test coverage target
- [x] Documentation complete

---

## Summary

| Metric | Count |
|--------|-------|
| **Total Tasks** | 100 |
| **Phase 1 (Setup)** | 10 |
| **Phase 2 (Foundational)** | 24 |
| **Phase 3 (US1 - MVP)** | 19 |
| **Phase 4 (US2)** | 16 |
| **Phase 5 (US3)** | 8 |
| **Phase 6 (US4)** | 13 |
| **Phase 7 (Polish)** | 10 |
| **Parallel Opportunities** | 40+ tasks marked [P] |

### MVP Scope (Recommended)
- **Phases 1-3**: Setup + Foundation + User Story 1
- **Tasks**: T001-T053 (53 tasks)
- **Delivers**: Working signup, login, task creation, task viewing

### Test Coverage Targets
- Backend: 70% minimum (pytest)
- Frontend: Component tests (Jest)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story (US1, US2, US3, US4)
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All file paths use phase2/ prefix per CLAUDE.md structure
