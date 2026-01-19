# Phase 2: Intermediate & Advanced Todo Features Specification

**Version**: 1.0.0
**Status**: Approved
**Last Updated**: January 17, 2026

## Overview

Upgrade Phase 2 Todo app from Basic Level to include Intermediate and Advanced features.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Tags Storage | JSON array field | Simpler, no extra tables needed |
| Recurrence | Create next on completion | No background scheduler required |
| Notifications | Client-side only | Works when app is open, no server push |
| Priorities | Three levels | Low, Medium, High - simple and intuitive |

---

## Intermediate Level Features

### F1: Task Priorities

**Description**: Allow users to set priority levels on tasks.

**Priority Levels**:
- `low` - Blue badge
- `medium` - Yellow/amber badge (default)
- `high` - Red badge

**Acceptance Criteria**:
- [ ] Tasks have a priority field with default "medium"
- [ ] Priority badge displays with color coding
- [ ] Tasks can be filtered by priority
- [ ] Tasks can be sorted by priority (high > medium > low)

### F2: Tags/Categories

**Description**: Allow users to categorize tasks with tags.

**Constraints**:
- Maximum 10 tags per task
- Maximum 30 characters per tag
- Tags stored as JSON array

**Acceptance Criteria**:
- [ ] Tasks can have 0-10 tags
- [ ] Tag input with autocomplete from user's existing tags
- [ ] Tags display as colored chips on task item
- [ ] Tasks can be filtered by tags (multi-select)

### F3: Search

**Description**: Search tasks by keyword.

**Search Scope**:
- Title
- Description

**Acceptance Criteria**:
- [ ] Search input with debounced input (300ms)
- [ ] Case-insensitive search
- [ ] Highlights matching tasks
- [ ] Clear button to reset search

### F4: Enhanced Filtering

**Description**: Advanced filtering options.

**New Filters**:
- Priority (all/low/medium/high)
- Tags (multi-select)
- Due date range (from/to)
- Overdue only toggle

**Acceptance Criteria**:
- [ ] All filters combinable
- [ ] Filter state preserved during session
- [ ] Clear all filters button

### F5: Sort by Priority/Due Date

**Description**: Additional sort options.

**Sort Fields**:
- Created date (existing)
- Title (existing)
- Priority (new)
- Due date (new)

**Acceptance Criteria**:
- [ ] Sort dropdown includes priority and due date options
- [ ] Priority sorts: high > medium > low
- [ ] Due date sorts chronologically, nulls last

---

## Advanced Level Features

### F6: Due Dates

**Description**: Set due dates on tasks.

**Features**:
- Date picker component
- Overdue indicator (red styling when past due)
- Visual indication of upcoming due dates

**Acceptance Criteria**:
- [ ] Tasks can have optional due date
- [ ] Date picker for date selection
- [ ] Overdue tasks highlighted in red
- [ ] `is_overdue` computed field in API response

### F7: Recurring Tasks

**Description**: Tasks that repeat on a schedule.

**Recurrence Patterns**:
- `none` - One-time task (default)
- `daily` - Repeats every day
- `weekly` - Repeats every 7 days
- `monthly` - Repeats same day next month

**Behavior**:
- When recurring task is completed, create next occurrence
- Original task marked complete
- New task created with next due date
- Recurrence ends when end_date is reached

**Acceptance Criteria**:
- [ ] Recurrence selector shown when due date is set
- [ ] Optional end date for recurrence
- [ ] Next occurrence created on completion
- [ ] Recurrence icon displayed on task item
- [ ] Parent-child relationship tracked (parent_task_id)

### F8: Reminders

**Description**: Browser notifications for upcoming due dates.

**Features**:
- Request notification permission on first use
- Reminder set to 1 hour before due date
- Client-side notification when app is open

**Acceptance Criteria**:
- [ ] Reminder toggle when due date is set
- [ ] Browser notification permission requested
- [ ] Notification shows task title and due date
- [ ] Bell icon on tasks with reminders

---

## Data Model Changes

### Task Model (Updated)

```python
class Task:
    # Existing fields
    id: UUID
    user_id: UUID (FK -> users.id)
    title: str (max 200)
    description: str | None (max 1000)
    completed: bool (default: false)
    created_at: datetime
    updated_at: datetime

    # New fields - Intermediate
    priority: str (default: "medium")  # low, medium, high
    tags: list[str] (default: [])      # JSON array, max 10 items

    # New fields - Advanced
    due_date: datetime | None
    recurrence_pattern: str (default: "none")  # none, daily, weekly, monthly
    recurrence_end_date: datetime | None
    parent_task_id: UUID | None (FK -> tasks.id)  # For recurring task chain
    reminder_at: datetime | None
```

### Database Indexes

```sql
CREATE INDEX ix_tasks_priority ON tasks(priority);
CREATE INDEX ix_tasks_due_date ON tasks(due_date);
CREATE INDEX ix_tasks_tags ON tasks USING GIN(tags);  -- PostgreSQL GIN index for JSON
```

---

## API Changes

### Updated Endpoints

#### GET /api/tasks

New query parameters:
- `priority` (string): "all" | "low" | "medium" | "high"
- `tags` (string): Comma-separated list of tags
- `search` (string): Search keyword
- `due_before` (datetime): Filter tasks due before date
- `due_after` (datetime): Filter tasks due after date
- `overdue_only` (boolean): Only show overdue tasks
- `sort` (string): Add "priority" and "due_date" options

#### POST /api/tasks

New body fields:
- `priority` (string, optional, default: "medium")
- `tags` (array, optional, default: [])
- `due_date` (datetime, optional)
- `recurrence_pattern` (string, optional, default: "none")
- `recurrence_end_date` (datetime, optional)
- `reminder_at` (datetime, optional)

#### PUT /api/tasks/{id}

Same new fields as POST.

### New Endpoints

#### GET /api/tasks/tags

Get all unique tags used by the current user.

Response:
```json
{
  "tags": ["work", "personal", "urgent", "shopping"]
}
```

---

## UI Components

### New Components

1. **PriorityBadge** - Color-coded priority indicator
2. **TagInput** - Multi-select with autocomplete
3. **DatePicker** - Date selection with optional time
4. **RecurrenceSelector** - Pattern dropdown with end date
5. **SearchInput** - Debounced search input

### Updated Components

1. **TaskForm** - Add priority, tags, due date, recurrence, reminder fields
2. **TaskItem** - Display priority badge, tags, due date, overdue indicator, icons
3. **TaskFilters** - Add priority, tags, search, date range filters

---

## Dependencies

### Backend
- `python-dateutil` for relativedelta (monthly recurrence calculation)

### Frontend
- `date-fns` for date formatting (if not already installed)
- shadcn/ui Calendar and Popover for DatePicker

---

## Backward Compatibility

All new fields have defaults to ensure existing tasks continue to work:
- `priority`: defaults to "medium"
- `tags`: defaults to []
- `due_date`: defaults to null
- `recurrence_pattern`: defaults to "none"
- `reminder_at`: defaults to null
