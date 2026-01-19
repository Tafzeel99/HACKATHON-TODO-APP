---
id: PHR-0002
title: Phase 2 Backend Server & Dependency Fixes
stage: green
date: 2026-01-18
surface: agent
model: claude-opus-4-5-20251101
feature: phase2
branch: phase2-full-stack
user: unknown
command: user-request
labels: [backend, server, dependencies, uvicorn, bcrypt, hydration, debugging]
links:
  spec: specs/phase2/spec/intermediate-advanced-features.md
  ticket: null
  adr: null
  pr: null
files:
  - phase2/backend/tests/conftest.py
  - phase2/backend/pyproject.toml
  - phase2/frontend/src/app/layout.tsx
tests:
  - phase2/backend/tests/test_auth.py
  - phase2/backend/tests/test_tasks.py
---

## Prompt

Continue work from PHR-0001, fix remaining test issues, and resolve "Failed to fetch" errors in frontend when connecting to backend API.

## Response snapshot

1. Fixed conftest.py bcrypt/passlib issue (changed from `passlib.hash.bcrypt` to direct `bcrypt` library)
2. All 43 backend tests now passing
3. Frontend build successful
4. Committed all Phase 2 intermediate/advanced features (37 files, +4161/-341 lines)
5. Diagnosed and fixed "Failed to fetch" errors - backend server not running
6. Fixed missing dependencies in venv (uvicorn, aiosqlite, email-validator)
7. Fixed pyproject.toml build configuration for hatchling
8. Fixed React hydration warning caused by browser extensions
9. Fixed server hanging issue - removed `--reload` flag from uvicorn

## Outcome

- Impact: Phase 2 backend fully operational, all tests passing, frontend connected
- Tests: 43/43 backend tests PASSED
- Files: conftest.py (bcrypt fix), pyproject.toml (build config + deps), layout.tsx (hydration fix)
- Commit: 730be68 - "feat: Add Intermediate & Advanced features to Phase 2 Todo App"
- Next prompts: Test full app flow, verify all features working end-to-end

## Outcome Details

### Issues Fixed:

1. **conftest.py bcrypt/passlib** (line 107-112)
   - Changed `from passlib.hash import bcrypt` to `import bcrypt as bcrypt_lib`
   - Used `bcrypt_lib.hashpw()` instead of `bcrypt.hash()`

2. **Missing venv dependencies**
   - uvicorn not installed (added via `uv sync`)
   - aiosqlite missing (added via `uv add aiosqlite`)
   - email-validator missing (added via `uv add email-validator`)

3. **pyproject.toml build config**
   - Added `[tool.hatch.build.targets.wheel]` section
   - Set `packages = ["src"]` for hatchling to find source

4. **React hydration warning**
   - Browser extensions adding attributes to body tag
   - Added `suppressHydrationWarning` to body element in layout.tsx

5. **Server hanging with --reload flag**
   - uvicorn `--reload` causing issues with Windows/WSL interop
   - Running without `--reload` resolves the hanging requests

### Test Results:
- Auth tests: 14/14 passed
- Task tests: 29/29 passed
- Total: 43/43 passed (100%)

### Server Status:
- Backend running on http://127.0.0.1:8000
- Health check: {"status":"healthy","version":"2.0.0"}
- Auth endpoints working (signup/signin tested)

## Evaluation notes (flywheel)

- Failure modes observed: uvicorn --reload flag incompatible with Windows/WSL cross-execution; uv sync removes some packages that need to be re-added
- Graders run and results (PASS/FAIL): PASS - all tests passing, server operational
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test full frontend-backend integration flow
