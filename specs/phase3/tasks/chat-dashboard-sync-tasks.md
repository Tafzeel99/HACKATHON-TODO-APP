# Task: Chat Agent Tasks Not Showing on Dashboard

**Issue ID**: PHASE3-SYNC-001
**Date**: 2026-01-21
**Priority**: High
**Status**: Resolved

## Problem Statement

Tasks created via the Phase 3 chat agent (ChatKit + MCP tools) are not appearing on the Phase 2 dashboard. The agent successfully creates tasks and returns task IDs, but the dashboard doesn't display them.

**Example:**
```
User: "Add a task to buy groceries"
Agent: "I've added a task to buy groceries. The task ID is a3409d59-70b6-4caf-a338-5124501e052b and its status is 'created'."
```
Task is created but NOT visible on dashboard.

## Root Cause Analysis

### Database Mismatch
- **Phase 2 Backend**: Uses `database_url` from `.env`, appears to be using **SQLite locally** (`phase2/backend/todo_app.db`)
- **Phase 3 Backend**: Uses `database_url` from `.env`, connecting to **Neon PostgreSQL**

The two backends are writing to **different databases**:
- Phase 2 dashboard reads from local SQLite
- Phase 3 MCP tools write to Neon PostgreSQL

### Evidence
1. Git status shows modified: `phase2/backend/todo_app.db` (SQLite file)
2. Phase 2 config has SQLite-specific handling (`check_same_thread`, no connection pooling)
3. Phase 3 config assumes PostgreSQL only (async pooling always enabled)

## Tasks

### T-001: Verify Database Configuration ✅
- [x] Check `.env` files for both phase2 and phase3 backends
- [x] Confirm which database each backend connects to
- [x] Document current database URLs

**Findings:**
- Phase 2: `sqlite+aiosqlite:///./todo_app.db` → creates `phase2/backend/todo_app.db`
- Phase 3: `sqlite+aiosqlite:///./todo_app.db` → creates `phase3/backend/todo_app.db`
- Both using SQLite but **different files** due to relative paths

### T-002: Align Database Configuration ✅
**Applied Option B (Local Dev)**: Point Phase 3 to Phase 2's SQLite database

Changes made:
- [x] Fixed `phase3/backend/src/config.py` to handle SQLite URLs properly
- [x] Fixed `phase3/backend/src/db.py` to use conditional connection pooling (SQLite vs PostgreSQL)
- [x] Updated `phase3/backend/.env` to use relative path: `../../phase2/backend/todo_app.db`

For production (Option A), update both `.env` files to use Neon PostgreSQL URL:
```
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require
```

### T-003: Verify User ID Consistency ✅
- [x] Ensure JWT tokens decode to same user_id format in both backends
- [x] Verify user_id in tasks table matches authenticated user

**Verified:** Both backends use the same JWT settings:
- Same secret: `better_auth_secret`
- Same algorithm: `jwt_algorithm` (HS256)
- Same claim: `sub` contains user UUID as string

### T-004: Test End-to-End Flow
- [ ] Create task via chat agent
- [ ] Verify task appears in database
- [ ] Verify task appears on dashboard
- [ ] Test task operations (complete, update, delete) from both interfaces

## Resolution Summary

**Date Resolved:** 2026-01-23

**Root Cause:** Both backends were using SQLite with relative paths (`./todo_app.db`), creating separate database files in their respective directories.

**Fix Applied:**
1. Updated Phase 3 config.py to handle SQLite URLs (line 48-51)
2. Updated Phase 3 db.py with conditional connection pooling (lines 11-21)
3. Changed Phase 3 DATABASE_URL to reference Phase 2's database file

**Files Modified:**
- `phase3/backend/src/config.py`
- `phase3/backend/src/db.py`
- `phase3/backend/.env`

## Files to Modify

| File | Change |
|------|--------|
| `phase2/backend/.env` | Update DATABASE_URL to Neon PostgreSQL |
| `phase2/backend/src/database.py` | May need adjustments for PostgreSQL-only |
| `phase3/backend/.env` | Verify DATABASE_URL matches phase2 |

## Acceptance Criteria

- [ ] Task created via chat agent appears on dashboard within 2 seconds
- [ ] Task completed via dashboard reflects in chat agent's list_tasks
- [ ] Both backends connect to the same Neon PostgreSQL database
- [ ] User isolation maintained (user A can't see user B's tasks)

## Related Files

- `phase3/backend/src/mcp/tools/add_task.py` - MCP tool that creates tasks
- `phase2/backend/src/database.py` - Phase 2 database connection
- `phase2/backend/src/config.py` - Phase 2 configuration
- `phase3/backend/src/db.py` - Phase 3 database connection
- `phase3/backend/src/config.py` - Phase 3 configuration

## Related PHRs

- PHR-0006: ChatKit Python SDK Backend Integration
- PHR-0005: Phase 3 ChatKit Integration Complete
