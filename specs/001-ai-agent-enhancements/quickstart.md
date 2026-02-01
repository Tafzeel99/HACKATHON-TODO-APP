# Quickstart Guide: Phase 3.5 - AI Agent & App Enhancements

**Feature**: 001-ai-agent-enhancements
**Date**: 2026-01-24

---

## Overview

This guide covers implementing enhanced AI chatbot features including:
- Task priorities, tags, due dates, recurring tasks, reminders
- Multi-language support (English, Urdu, Roman Urdu)
- Smart analytics and daily summaries

---

## Prerequisites

✅ **Phase 3 Complete**: AI chatbot with MCP tools working
✅ **Phase 2 Database**: Task model has all required fields
✅ **Environment**: Python 3.13+, Node.js 18+, OpenAI API key

---

## Implementation Steps

### Step 1: Update MCP Tools (Backend)

**Files to modify**:
- `phase3/backend/src/mcp/tools/add_task.py`
- `phase3/backend/src/mcp/tools/list_tasks.py`
- `phase3/backend/src/mcp/tools/complete_task.py`
- `phase3/backend/src/mcp/tools/update_task.py`

**New file**:
- `phase3/backend/src/mcp/tools/get_analytics.py`

#### 1.1 Enhance add_task

Add parameters: `priority`, `tags`, `due_date`, `recurrence_pattern`, `recurrence_end_date`, `reminder_at`

```python
# add_task.py - Enhanced parameter registration
tool_registry.register(
    name="add_task",
    description="Create a new task with priority, tags, due date, and recurrence support.",
    parameters={
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Task title"},
            "description": {"type": "string", "description": "Task description"},
            "priority": {"type": "string", "enum": ["low", "medium", "high"], "default": "medium"},
            "tags": {"type": "array", "items": {"type": "string"}, "description": "Task tags"},
            "due_date": {"type": "string", "description": "ISO 8601 due date"},
            "recurrence_pattern": {"type": "string", "enum": ["none", "daily", "weekly", "monthly"]},
            "recurrence_end_date": {"type": "string", "description": "ISO 8601 recurrence end"},
            "reminder_at": {"type": "string", "description": "ISO 8601 reminder time"},
        },
        "required": ["title"],
    },
    handler=add_task_handler,
)
```

#### 1.2 Enhance list_tasks

Add filtering: `priority`, `tags`, `due_before`, `due_after`, `overdue_only`, `search`

#### 1.3 Enhance complete_task

Add recurring task logic:
```python
if task.recurrence_pattern != "none":
    next_due = calculate_next_due(task.due_date, task.recurrence_pattern)
    if not task.recurrence_end_date or next_due <= task.recurrence_end_date:
        # Create next occurrence
        new_task = Task(
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            tags=task.tags,
            due_date=next_due,
            recurrence_pattern=task.recurrence_pattern,
            recurrence_end_date=task.recurrence_end_date,
            parent_task_id=task.id,
        )
```

#### 1.4 Create get_analytics

New tool for productivity statistics.

---

### Step 2: Update AI Agent System Prompt

**File**: `phase3/backend/src/services/agent_service.py`

Add multi-language instructions:

```python
SYSTEM_PROMPT = """
You are a multilingual task management assistant. You help users manage their
todos through natural conversation in English, Urdu, and Roman Urdu.

## Language Rules
1. MIRROR the user's language - respond in the language they use
2. Understand Roman Urdu variations (hai/h/hey, karo/kro/krdo)
3. Parse dates in any language and convert to ISO format
4. Confirm actions in the user's language

## Command Recognition

### English
- Add: "add", "create", "remember", "need to"
- List: "show", "list", "what's pending"
- Complete: "done", "finished", "complete"
- Delete: "delete", "remove"
- Update: "change", "update", "modify"
- Analytics: "how many", "stats", "summary"

### Roman Urdu
- Add: "add karo", "banana hai", "yaad rakhna"
- List: "dikhao", "batao", "mere tasks"
- Complete: "ho gaya", "khatam", "mukammal"
- Delete: "hata do", "nikalo"
- Update: "badal do", "change karo"
- Analytics: "kitne", "summary dikhao"

### Urdu Script (اردو)
- Add: شامل کرو، بناؤ
- List: دکھاؤ، بتاؤ
- Complete: ہو گیا، مکمل
- Delete: ہٹاؤ، حذف کرو
- Update: تبدیل کرو
- Analytics: کتنے، خلاصہ

## Date Parsing
- today/aaj/آج → current date
- tomorrow/kal/کل → +1 day
- day after tomorrow/parson/پرسوں → +2 days
- next week/aglay hafta/اگلے ہفتے → +7 days (Monday)
- next month/aglay mahina/اگلے مہینے → +1 month
- in N days/N din mein → +N days

## Priority Keywords
- HIGH: urgent, important, asap, zaroori, fori, ضروری, فوری
- LOW: sometime, whenever, jab bhi, جب بھی

## Available Tools
{tool_descriptions}

Always confirm actions with a friendly message in the user's language.
"""
```

---

### Step 3: Test Multi-Language Support

Create test cases for each language:

```python
# test_multilingual.py

@pytest.mark.asyncio
async def test_roman_urdu_add_task():
    response = await chat("Mujhe kal grocery leni hai")
    assert "grocery" in response.lower()
    # Verify task created with tomorrow's date

@pytest.mark.asyncio
async def test_urdu_list_tasks():
    response = await chat("میرے ٹاسک دکھاؤ")
    # Verify response is in Urdu script

@pytest.mark.asyncio
async def test_mixed_language():
    response = await chat("Add task kal meeting hai with high priority")
    # Verify handles mixed input
```

---

## Testing Checklist

### MCP Tools
- [ ] add_task with priority, tags, due_date
- [ ] add_task with recurrence pattern
- [ ] list_tasks with priority filter
- [ ] list_tasks with tags filter
- [ ] list_tasks with overdue_only
- [ ] list_tasks with search keyword
- [ ] complete_task creates recurring next occurrence
- [ ] update_task modifies all fields
- [ ] get_analytics returns correct counts

### Multi-Language
- [ ] English commands work
- [ ] Roman Urdu commands work
- [ ] Urdu script commands work
- [ ] Mixed language handled
- [ ] Response mirrors user's language
- [ ] Date parsing in all languages
- [ ] Priority keywords recognized

### Edge Cases
- [ ] Task with 10 tags (max limit)
- [ ] Task with past due date (warning)
- [ ] Recurring task with end date
- [ ] Analytics with no tasks
- [ ] Search with no results

---

## Running the Enhanced System

```bash
# 1. Start Phase 3 Backend
cd phase3/backend
pip install -e .
uvicorn src.main:app --reload --port 8001

# 2. Start Phase 2 Frontend
cd phase2/frontend
npm run dev

# 3. Access chat at http://localhost:3000/chat
```

---

## Example Conversations

### English
```
User: Add a high priority task to finish report due tomorrow
AI: ✅ Created task "Finish report" with high priority, due January 25.

User: Show my overdue tasks
AI: You have 2 overdue tasks:
    1. Call client (due Jan 20) - high priority
    2. Review docs (due Jan 22) - medium priority
```

### Roman Urdu
```
User: Mujhe ek zaroori task add karna hai - meeting ki tayari
AI: ✅ Task "Meeting ki tayari" high priority ke saath add ho gaya!

User: Mere pending tasks dikhao
AI: Aap ke 3 pending tasks hain:
    1. Meeting ki tayari - zaroori
    2. Grocery lena - medium
    3. Email check karna - low
```

### Urdu Script
```
User: نیا ٹاسک شامل کرو: رپورٹ مکمل کرنی ہے
AI: ✅ ٹاسک "رپورٹ مکمل کرنی ہے" شامل ہو گیا!

User: آج کے ٹاسک دکھاؤ
AI: آج کے لیے 2 ٹاسک ہیں:
    1. رپورٹ مکمل کرنی ہے
    2. میٹنگ اٹینڈ کرنی ہے
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Roman Urdu not recognized | Check system prompt includes examples |
| Dates parsing wrong | Ensure ISO 8601 format passed to tools |
| Urdu script not displaying | Verify UTF-8 encoding in responses |
| Recurring task not created | Check recurrence_pattern != "none" |
| Analytics slow | Add database indexes on user_id, due_date |

---

## Next Steps

After implementation:
1. Run `/sp.tasks` to generate task breakdown
2. Run `/sp.implement` to execute implementation
3. Test all scenarios
4. Update README.md
5. Prepare for Phase 4 (containerization)
