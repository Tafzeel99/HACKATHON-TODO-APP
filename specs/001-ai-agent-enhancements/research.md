# Research Notes: Phase 3.5 - AI Agent & App Enhancements

**Feature**: 001-ai-agent-enhancements
**Date**: 2026-01-24
**Purpose**: Resolve technical decisions and research unknowns

---

## Research Topics

### 1. Multi-Language Support Strategy

**Decision**: Use OpenAI GPT's native multilingual capabilities

**Rationale**:
- GPT-4 and GPT-4o natively understand 95+ languages including Urdu and Roman Urdu
- No additional translation APIs or NLP libraries needed
- System prompt can instruct language behavior (mirroring, examples)
- Cost-effective: no extra API calls for translation

**Alternatives Considered**:
| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| GPT Native | Zero additional cost, seamless | Relies on GPT understanding | ✅ Selected |
| Google Translate API | Accurate translation | Extra cost, latency, complexity | ❌ Rejected |
| Custom NLP Model | Full control | High development effort, maintenance | ❌ Rejected |
| Language Detection Library | Explicit detection | Unnecessary with GPT | ❌ Rejected |

**Implementation**:
```python
# System prompt excerpt for multi-language support
SYSTEM_PROMPT = """
You are a multilingual task management assistant. You MUST:

1. LANGUAGE MIRRORING: Respond in the SAME language the user writes in
   - English → Reply in English
   - Roman Urdu (e.g., "Mujhe task add karo") → Reply in Roman Urdu
   - Urdu script (e.g., "میرا ٹاسک دکھاؤ") → Reply in Urdu script

2. UNDERSTAND these Roman Urdu commands:
   - "add karo", "banana hai", "yaad dilao" → add_task
   - "dikhao", "batao", "list karo" → list_tasks
   - "khatam", "ho gaya", "complete" → complete_task
   - "delete karo", "hata do", "nikalo" → delete_task
   - "badal do", "change karo" → update_task

3. UNDERSTAND these Urdu script commands:
   - "شامل کرو", "بناؤ" → add_task
   - "دکھاؤ", "بتاؤ" → list_tasks
   - "مکمل کرو", "ہو گیا" → complete_task
   - "حذف کرو", "ہٹاؤ" → delete_task
   - "تبدیل کرو" → update_task

4. UNDERSTAND date expressions:
   - Roman Urdu: "aaj" (today), "kal" (tomorrow), "parson" (day after),
     "aglay hafta" (next week), "aglay mahine" (next month)
   - Urdu: "آج", "کل", "پرسوں", "اگلے ہفتے", "اگلے مہینے"

5. UNDERSTAND priority keywords:
   - High: "zaroori", "zaruri", "fori", "urgent", "ضروری", "فوری"
   - Low: "jab bhi", "baad mein", "جب بھی", "بعد میں"
"""
```

---

### 2. Natural Language Date Parsing

**Decision**: Let GPT handle date interpretation, pass ISO format to tools

**Rationale**:
- GPT understands natural language dates in multiple languages
- Agent interprets "tomorrow", "kal", "کل" and calculates actual date
- MCP tools receive standardized ISO 8601 datetime strings
- No additional date parsing libraries needed in backend

**Date Mapping Reference** (for system prompt):

| English | Roman Urdu | Urdu Script | Interpretation |
|---------|------------|-------------|----------------|
| today | aaj | آج | Current date |
| tomorrow | kal | کل | +1 day |
| day after tomorrow | parson | پرسوں | +2 days |
| next week | aglay hafta | اگلے ہفتے | +7 days (Monday) |
| next month | aglay mahina | اگلے مہینے | +1 month |
| this Friday | is jumma | اس جمعے | Next Friday |
| in 3 days | 3 din mein | 3 دن میں | +3 days |

**Implementation**:
- GPT calculates date and passes ISO string to add_task/update_task
- Tools accept `due_date: str` in ISO 8601 format
- Backend validates and stores as datetime

---

### 3. Recurring Task Implementation

**Decision**: Create next occurrence on completion (simple approach)

**Rationale**:
- No background scheduler needed (stateless architecture)
- Works naturally with user workflow
- Parent-child relationship tracks task chain

**Algorithm**:
```
When complete_task is called:
1. Mark current task as completed
2. If recurrence_pattern != "none":
   a. Calculate next due_date based on pattern
   b. If next_date <= recurrence_end_date (or no end date):
      - Create new task with same title, description, priority, tags
      - Set parent_task_id = current task id
      - Set due_date = next calculated date
      - Return message about both completion and new task
```

**Date Calculations**:
| Pattern | Calculation |
|---------|-------------|
| daily | current_due_date + 1 day |
| weekly | current_due_date + 7 days |
| monthly | current_due_date + 1 month (same day) |

---

### 4. Analytics Tool Design

**Decision**: Query-based analytics with caching consideration

**Rationale**:
- Provides instant productivity insights
- All data already in database
- User-scoped queries maintain isolation

**get_analytics Tool Output**:
```json
{
  "total_tasks": 25,
  "completed_count": 18,
  "pending_count": 7,
  "overdue_count": 2,
  "completion_rate": 72.0,
  "tasks_by_priority": {
    "high": {"total": 5, "completed": 3, "pending": 2},
    "medium": {"total": 15, "completed": 12, "pending": 3},
    "low": {"total": 5, "completed": 3, "pending": 2}
  },
  "tasks_due_today": 3,
  "tasks_due_this_week": 8,
  "completed_this_week": 5
}
```

**Query Strategy**:
- Single database round-trip with aggregation
- Filter by user_id for isolation
- Calculate overdue as: due_date < now AND completed = false

---

### 5. Roman Urdu Spelling Variations

**Decision**: Document common variations in system prompt

**Rationale**:
- GPT handles variations naturally through context
- Explicit examples improve accuracy
- No fuzzy matching library needed

**Common Variations**:
| Standard | Variations |
|----------|------------|
| hai | hey, h, hy |
| karo | kro, krdo, kar do |
| nahi | nhi, ni, nahin |
| mujhe | mje, mjhe |
| karna | krna |
| dikhao | dikhao, dkhao |
| kal | kl |

**System Prompt Handling**:
```
Note: Users may use informal Roman Urdu spelling variations:
- "hai" might be written as "h", "hey", "hy"
- "karo" might be written as "kro", "krdo"
- Interpret based on context and common patterns
```

---

### 6. Tool Parameter Extensions

**Decision**: Extend existing tools with optional parameters

**add_task Enhancement**:
```python
parameters = {
    "title": str,           # Required
    "description": str,     # Optional
    "priority": str,        # Optional, default: "medium"
    "tags": list[str],      # Optional, default: []
    "due_date": str,        # Optional, ISO 8601 format
    "recurrence_pattern": str,  # Optional, default: "none"
    "recurrence_end_date": str, # Optional, ISO 8601
    "reminder_at": str,     # Optional, ISO 8601
}
```

**list_tasks Enhancement**:
```python
parameters = {
    "status": str,          # "all", "pending", "completed"
    "priority": str,        # "all", "low", "medium", "high"
    "tags": list[str],      # Filter by tags (any match)
    "due_before": str,      # ISO 8601 date
    "due_after": str,       # ISO 8601 date
    "overdue_only": bool,   # Only show overdue tasks
    "search": str,          # Keyword search in title/description
}
```

---

### 7. Error Handling for Multi-Language

**Decision**: Return errors in user's language

**Implementation**:
- Detect language from user's last message
- Return error messages in same language
- Include helpful suggestions

**Error Message Examples**:
| Scenario | English | Roman Urdu | Urdu |
|----------|---------|------------|------|
| Task not found | Task not found | Task nahi mila | ٹاسک نہیں ملا |
| Invalid date | Invalid date format | Date sahi nahi hai | تاریخ درست نہیں |
| Too many tags | Maximum 10 tags allowed | 10 se zyada tags nahi | زیادہ سے زیادہ 10 ٹیگز |

---

## Resolved Clarifications

All technical unknowns from the spec have been resolved:

| Unknown | Resolution |
|---------|------------|
| NLP for Urdu | Use GPT native multilingual |
| Date parsing library | Not needed - GPT handles |
| Recurring task scheduler | Not needed - on-completion creation |
| Translation service | Not needed - GPT native |
| Fuzzy matching for typos | Not needed - GPT context understanding |

---

## Technology Decisions Summary

| Component | Technology | Reason |
|-----------|------------|--------|
| Multi-language NLP | OpenAI GPT | Native support, no extra cost |
| Date parsing | GPT + ISO 8601 | Natural language → standard format |
| Recurring tasks | On-completion creation | Stateless, no scheduler |
| Analytics | SQL aggregation | Single query, instant results |
| Spelling variations | System prompt examples | GPT context understanding |

---

## References

- OpenAI GPT Language Support: https://platform.openai.com/docs/guides/multilingual
- ISO 8601 Date Format: https://en.wikipedia.org/wiki/ISO_8601
- Python dateutil relativedelta: https://dateutil.readthedocs.io/
- MCP Tool Definition: https://modelcontextprotocol.io/docs
