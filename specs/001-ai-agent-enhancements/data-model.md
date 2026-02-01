# Data Model: Phase 3.5 - AI Agent & App Enhancements

**Feature**: 001-ai-agent-enhancements
**Date**: 2026-01-24
**Status**: No schema changes required - existing model sufficient

---

## Overview

The Phase 2 Task model already contains all fields required for Phase 3.5 enhancements. This document describes the existing schema and how it maps to new features.

---

## Existing Entities

### Task (Already Complete)

**Location**: `phase2/backend/src/models/task.py`

| Field | Type | Default | Description | Used By Feature |
|-------|------|---------|-------------|-----------------|
| id | UUID | auto | Primary key | All |
| user_id | UUID | required | Foreign key to users | User isolation |
| title | str(200) | required | Task title | All |
| description | str(1000) | null | Task description | All |
| completed | bool | false | Completion status | Complete task |
| created_at | datetime | now | Creation timestamp | Analytics |
| updated_at | datetime | now | Last update timestamp | All |
| **priority** | str | "medium" | low/medium/high | Priorities (P1) |
| **tags** | JSON array | [] | Up to 10 tags | Tags (P1) |
| **due_date** | datetime | null | Task due date | Due dates (P1) |
| **recurrence_pattern** | str | "none" | none/daily/weekly/monthly | Recurring (P2) |
| **recurrence_end_date** | datetime | null | End date for recurrence | Recurring (P2) |
| **parent_task_id** | UUID | null | FK to parent task | Recurring chain |
| **reminder_at** | datetime | null | Reminder datetime | Reminders (P3) |

**Indexes** (existing):
- `ix_tasks_user_id` - User isolation queries
- `ix_tasks_completed` - Status filtering
- `ix_tasks_priority` - Priority filtering
- `ix_tasks_due_date` - Due date filtering

### Conversation (Existing)

**Location**: `phase3/backend/src/models/conversation.py`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| id | UUID | auto | Primary key |
| user_id | UUID | required | Owner user |
| created_at | datetime | now | Creation timestamp |
| updated_at | datetime | now | Last update timestamp |

### Message (Existing)

**Location**: `phase3/backend/src/models/message.py`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| id | UUID | auto | Primary key |
| conversation_id | UUID | required | FK to conversation |
| user_id | UUID | required | Owner user |
| role | str | required | "user" or "assistant" |
| content | str | required | Message text |
| tool_calls | JSON | null | MCP tool invocations |
| created_at | datetime | now | Creation timestamp |

---

## Computed Fields (Application Layer)

These are calculated at query time, not stored:

### Task.is_overdue

```python
@property
def is_overdue(self) -> bool:
    """Task is overdue if due_date is past and not completed."""
    if self.due_date is None or self.completed:
        return False
    return self.due_date < datetime.utcnow()
```

### Analytics (Computed Response)

```python
class Analytics:
    """Computed from task aggregation queries."""
    total_tasks: int
    completed_count: int
    pending_count: int
    overdue_count: int
    completion_rate: float  # (completed / total) * 100
    tasks_by_priority: dict[str, dict]  # {priority: {total, completed, pending}}
    tasks_due_today: int
    tasks_due_this_week: int
    completed_this_week: int
```

---

## Entity Relationships

```
┌─────────────┐       ┌─────────────────┐       ┌─────────────┐
│    User     │──1:N──│      Task       │──1:N──│    Task     │
│             │       │                 │       │  (children) │
└─────────────┘       │  parent_task_id │───────│             │
                      └─────────────────┘       └─────────────┘
                             │
                             │ 1:N (via user_id)
                             │
                      ┌──────▼──────┐
                      │ Conversation│
                      │             │
                      └──────┬──────┘
                             │ 1:N
                      ┌──────▼──────┐
                      │   Message   │
                      └─────────────┘
```

---

## Validation Rules

### Task Validation

| Field | Rule | Error Message |
|-------|------|---------------|
| title | 1-200 characters | "Title must be 1-200 characters" |
| description | 0-1000 characters | "Description must be under 1000 characters" |
| priority | "low", "medium", "high" | "Priority must be low, medium, or high" |
| tags | max 10 items | "Maximum 10 tags allowed" |
| tags[item] | max 30 characters | "Each tag must be under 30 characters" |
| due_date | valid datetime or null | "Invalid date format" |
| recurrence_pattern | "none", "daily", "weekly", "monthly" | "Invalid recurrence pattern" |
| recurrence_end_date | >= due_date or null | "End date must be after due date" |

### Recurring Task Rules

1. If `recurrence_pattern != "none"`, `due_date` should be set
2. When completed, new task created with:
   - Same: title, description, priority, tags, recurrence_pattern, recurrence_end_date
   - Updated: due_date (calculated), parent_task_id (set to completed task)
3. Recurrence stops when:
   - `recurrence_end_date` is reached
   - User manually sets `recurrence_pattern = "none"`

---

## Query Patterns

### List Tasks with Filters

```sql
SELECT * FROM tasks
WHERE user_id = :user_id
  AND (:status = 'all' OR completed = :is_completed)
  AND (:priority = 'all' OR priority = :priority)
  AND (:search IS NULL OR title ILIKE :search OR description ILIKE :search)
  AND (:due_after IS NULL OR due_date >= :due_after)
  AND (:due_before IS NULL OR due_date <= :due_before)
  AND (:tags IS NULL OR tags ?| :tags)  -- PostgreSQL JSON contains any
  AND (:overdue_only = false OR (due_date < NOW() AND completed = false))
ORDER BY
  CASE WHEN :sort = 'priority' THEN
    CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END
  END,
  CASE WHEN :sort = 'due_date' THEN due_date END,
  created_at DESC;
```

### Analytics Query

```sql
SELECT
  COUNT(*) as total_tasks,
  SUM(CASE WHEN completed THEN 1 ELSE 0 END) as completed_count,
  SUM(CASE WHEN NOT completed THEN 1 ELSE 0 END) as pending_count,
  SUM(CASE WHEN due_date < NOW() AND NOT completed THEN 1 ELSE 0 END) as overdue_count,
  SUM(CASE WHEN due_date::date = CURRENT_DATE THEN 1 ELSE 0 END) as tasks_due_today,
  SUM(CASE WHEN due_date BETWEEN NOW() AND NOW() + INTERVAL '7 days' THEN 1 ELSE 0 END) as tasks_due_this_week,
  SUM(CASE WHEN completed AND updated_at >= NOW() - INTERVAL '7 days' THEN 1 ELSE 0 END) as completed_this_week
FROM tasks
WHERE user_id = :user_id;
```

### Analytics by Priority

```sql
SELECT
  priority,
  COUNT(*) as total,
  SUM(CASE WHEN completed THEN 1 ELSE 0 END) as completed,
  SUM(CASE WHEN NOT completed THEN 1 ELSE 0 END) as pending
FROM tasks
WHERE user_id = :user_id
GROUP BY priority;
```

---

## Migration Status

**No migrations required** - All fields exist in current schema.

Existing fields from Phase 2 intermediate/advanced feature implementation:
- ✅ priority (added in Phase 2)
- ✅ tags (added in Phase 2)
- ✅ due_date (added in Phase 2)
- ✅ recurrence_pattern (added in Phase 2)
- ✅ recurrence_end_date (added in Phase 2)
- ✅ parent_task_id (added in Phase 2)
- ✅ reminder_at (added in Phase 2)

---

## Unicode Support

For Urdu script storage:
- PostgreSQL/Neon: UTF-8 encoding (default)
- SQLModel/SQLAlchemy: Unicode strings supported
- Task titles and descriptions can contain: اردو متن

No special configuration needed - Unicode support is built-in.
