# Implementation Plan: Phase II - Todo Full-Stack Web Application

**Branch**: `phase2-full-stack` | **Date**: 2026-01-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/phase2-full-stack/spec.md`

## Summary

Transform the Phase I console-based Todo application into a multi-user full-stack web application with:
- **Frontend**: Next.js 16+ with App Router, TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: FastAPI with SQLModel ORM, async/await patterns
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth with JWT tokens
- **Architecture**: Monorepo structure with `/phase2/frontend` and `/phase2/backend`

The application delivers 5 Basic Level features (Add, Delete, Update, View, Mark Complete) with multi-user isolation, persistent storage, and responsive UI.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, python-jose (JWT), Better Auth Python SDK
- Frontend: Next.js 16+, React 19, Tailwind CSS, shadcn/ui, Better Auth client
**Storage**: Neon Serverless PostgreSQL (DATABASE_URL via environment)
**Testing**: pytest (backend, 70% coverage), Jest (frontend)
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge - latest 2 versions)
**Project Type**: Web application (frontend + backend monorepo)
**Performance Goals**: API < 200ms p95, 100 concurrent users
**Constraints**: JWT 7-day max expiry, stateless backend, environment-driven config
**Scale/Scope**: 1000 users initially, 6 RESTful endpoints, responsive 320px-1920px

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
- [x] Sequential phase completion (no skipping) - Phase I completed first
- [x] Current phase builds on previous foundation (console app → web app)
- [x] Architecture follows: CLI → Web → AI Chatbot → K8s → Cloud-Native

### Principle 4: Cloud-Native First
- [x] Stateless design (preparing for Phase III)
- [x] Containerization ready (preparing for Phase IV)
- [ ] Event-driven patterns considered (Phase V - not applicable yet)
- [x] Horizontal scalability designed in (stateless JWT, serverless DB)

### Principle 5: Production Quality
- [x] Clean code principles enforced (PEP 8, ESLint)
- [x] Security best practices followed (Better Auth, JWT, input validation)
- [x] Comprehensive error handling implemented
- [x] Full documentation provided

**Gate Status**: PASSED - All applicable principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/phase2-full-stack/
├── plan.md              # This file
├── research.md          # Phase 0 output - technology decisions
├── data-model.md        # Phase 1 output - database schema
├── quickstart.md        # Phase 1 output - setup instructions
├── contracts/           # Phase 1 output - API specifications
│   └── openapi.yaml     # OpenAPI 3.0 specification
├── checklists/          # Quality validation
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
phase2/
├── backend/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Environment configuration
│   │   ├── database.py          # Database connection
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py          # User SQLModel
│   │   │   └── task.py          # Task SQLModel
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py          # User Pydantic schemas
│   │   │   └── task.py          # Task Pydantic schemas
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py          # Dependency injection
│   │   │   ├── auth.py          # Auth endpoints
│   │   │   └── tasks.py         # Task CRUD endpoints
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── auth.py          # Auth service layer
│   │       └── task.py          # Task service layer
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py          # pytest fixtures
│   │   ├── test_auth.py         # Auth endpoint tests
│   │   └── test_tasks.py        # Task endpoint tests
│   ├── alembic/                 # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   ├── pyproject.toml           # Python dependencies
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js App Router
│   │   │   ├── layout.tsx       # Root layout
│   │   │   ├── page.tsx         # Landing page
│   │   │   ├── (auth)/          # Auth route group
│   │   │   │   ├── login/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── signup/
│   │   │   │       └── page.tsx
│   │   │   └── (dashboard)/     # Protected route group
│   │   │       ├── layout.tsx   # Dashboard layout with auth check
│   │   │       └── tasks/
│   │   │           └── page.tsx # Task list page
│   │   ├── components/
│   │   │   ├── ui/              # shadcn/ui components
│   │   │   ├── auth/
│   │   │   │   ├── login-form.tsx
│   │   │   │   └── signup-form.tsx
│   │   │   └── tasks/
│   │   │       ├── task-list.tsx
│   │   │       ├── task-item.tsx
│   │   │       ├── task-form.tsx
│   │   │       └── task-filters.tsx
│   │   ├── lib/
│   │   │   ├── api.ts           # API client
│   │   │   ├── auth.ts          # Better Auth client
│   │   │   └── utils.ts         # Utility functions
│   │   └── types/
│   │       ├── task.ts          # Task TypeScript types
│   │       └── user.ts          # User TypeScript types
│   ├── tests/
│   │   └── components/
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── README.md
│
└── README.md                    # Phase 2 overview
```

**Structure Decision**: Web application structure selected per constitution Architecture Standards ("Monorepo with `/frontend` and `/backend`"). Using `phase2/` prefix to maintain phase separation as defined in project structure.

## Complexity Tracking

> No constitution violations requiring justification. All patterns align with Phase II requirements.

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Monorepo | Single repo with phase2/frontend + phase2/backend | Constitution requirement |
| Auth | Better Auth + JWT | Constitution Phase II requirement |
| Database | Neon Serverless PostgreSQL | Constitution Phase II requirement |
| State | Stateless backend | Preparing for Phase III/IV |

---

## Technology Decisions Summary

All technology choices are per constitution requirements:

| Layer | Technology | Version | Rationale |
|-------|------------|---------|-----------|
| Frontend Framework | Next.js | 16+ | Constitution Phase II stack |
| Frontend Language | TypeScript | 5.x | Type safety, ESLint compliance |
| UI Components | shadcn/ui + Tailwind | Latest | Accessible, responsive components |
| Backend Framework | FastAPI | Latest | Async Python, OpenAPI auto-docs |
| Backend Language | Python | 3.13+ | Constitution requirement |
| ORM | SQLModel | Latest | SQLAlchemy + Pydantic integration |
| Database | Neon PostgreSQL | Serverless | Constitution Phase II stack |
| Authentication | Better Auth | Latest | Constitution Phase II stack |
| Testing (Backend) | pytest | Latest | 70% coverage requirement |
| Testing (Frontend) | Jest | Latest | Component testing |
| Linting | Ruff (Python), ESLint (TS) | Latest | Constitution quality standards |

## Key Design Decisions

### 1. Authentication Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Authentication Flow                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Frontend (Next.js)              Backend (FastAPI)                  │
│  ┌─────────────────┐             ┌─────────────────┐               │
│  │  Better Auth    │             │  Better Auth    │               │
│  │  Client         │◄───────────►│  Verify JWT     │               │
│  └────────┬────────┘             └────────┬────────┘               │
│           │                               │                         │
│           │ JWT Token                     │ Decoded User            │
│           ▼                               ▼                         │
│  ┌─────────────────┐             ┌─────────────────┐               │
│  │  API Client     │────────────►│  Protected      │               │
│  │  (Authorization │   HTTP      │  Endpoints      │               │
│  │   Header)       │             │  (tasks CRUD)   │               │
│  └─────────────────┘             └─────────────────┘               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2. API Design Pattern

- RESTful endpoints under `/api/`
- JWT in Authorization header for all protected routes
- User isolation via user_id from decoded JWT (not URL parameter)
- Proper HTTP status codes per spec

### 3. Database Design

- Two tables: `users` and `tasks`
- Foreign key: `tasks.user_id` → `users.id`
- Indexes on `user_id` and `completed` for query performance
- Timestamps: `created_at`, `updated_at` auto-managed

### 4. Frontend Architecture

- Next.js App Router for file-based routing
- Route groups: `(auth)` for public, `(dashboard)` for protected
- Server-side auth check in dashboard layout
- Client components for interactive task management
- shadcn/ui for consistent, accessible UI components
