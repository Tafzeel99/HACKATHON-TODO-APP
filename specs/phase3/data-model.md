# Data Model: Phase 3 - Todo AI Chatbot

**Date**: 2026-01-19
**Feature**: Phase 3 AI Chatbot
**Database**: Neon PostgreSQL (extending Phase 2 schema)

---

## Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────────┐       ┌─────────────────────┐
│      User       │       │    Conversation     │       │      Message        │
│  (from Auth)    │       │                     │       │                     │
├─────────────────┤       ├─────────────────────┤       ├─────────────────────┤
│ id (PK)         │──┐    │ id (PK)             │──┐    │ id (PK)             │
│ email           │  │    │ user_id (FK)        │  │    │ conversation_id(FK) │
│ ...             │  └───▶│ created_at          │  └───▶│ user_id (FK)        │
└─────────────────┘       │ updated_at          │       │ role                │
         │                └─────────────────────┘       │ content             │
         │                                              │ tool_calls          │
         │                                              │ created_at          │
         │                                              └─────────────────────┘
         │
         │                ┌─────────────────────┐
         │                │       Task          │
         │                │   (from Phase 2)    │
         │                ├─────────────────────┤
         └───────────────▶│ id (PK)             │
                          │ user_id (FK)        │
                          │ title               │
                          │ description         │
                          │ completed           │
                          │ priority            │
                          │ tags                │
                          │ due_date            │
                          │ ...                 │
                          │ created_at          │
                          │ updated_at          │
                          └─────────────────────┘
```

---

## Models

### 1. Task (Extended from Phase 2)

**Purpose**: Represents a todo item belonging to a user. Reuses Phase 2 model.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique task identifier |
| user_id | String | FK, NOT NULL, indexed | Owner user ID |
| title | String(200) | NOT NULL | Task title |
| description | String(1000) | NULL | Optional description |
| completed | Boolean | DEFAULT FALSE | Completion status |
| priority | Enum | DEFAULT 'medium' | low/medium/high |
| tags | Array[String] | DEFAULT [] | Task tags |
| due_date | DateTime | NULL | Optional due date |
| recurrence_pattern | Enum | DEFAULT 'none' | none/daily/weekly/monthly |
| reminder_at | DateTime | NULL | Optional reminder time |
| created_at | DateTime | NOT NULL, auto | Creation timestamp |
| updated_at | DateTime | NOT NULL, auto | Last update timestamp |

**Indexes**:
- `idx_tasks_user_id` on user_id
- `idx_tasks_completed` on (user_id, completed)

**Notes**: No schema changes needed from Phase 2. MCP tools will query existing Task table.

---

### 2. Conversation (NEW)

**Purpose**: Represents a chat session for a user.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique conversation identifier |
| user_id | String | NOT NULL, indexed | Owner user ID |
| title | String(200) | NULL | Optional conversation title |
| created_at | DateTime | NOT NULL, auto | Creation timestamp |
| updated_at | DateTime | NOT NULL, auto | Last update timestamp |

**Indexes**:
- `idx_conversations_user_id` on user_id
- `idx_conversations_user_updated` on (user_id, updated_at DESC)

**Relationships**:
- One User has Many Conversations
- One Conversation has Many Messages

**SQLModel Definition**:
```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str | None = Field(max_length=200, default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    messages: list["Message"] = Relationship(back_populates="conversation")
```

---

### 3. Message (NEW)

**Purpose**: Represents a single chat message in a conversation.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique message identifier |
| conversation_id | UUID | FK, NOT NULL | Parent conversation |
| user_id | String | NOT NULL, indexed | Owner user ID |
| role | Enum | NOT NULL | 'user' or 'assistant' |
| content | Text | NOT NULL | Message content |
| tool_calls | JSON | NULL | MCP tool calls made (if any) |
| created_at | DateTime | NOT NULL, auto | Creation timestamp |

**Indexes**:
- `idx_messages_conversation_id` on conversation_id
- `idx_messages_user_id` on user_id
- `idx_messages_created` on (conversation_id, created_at)

**Relationships**:
- Many Messages belong to One Conversation
- Messages ordered by created_at within conversation

**SQLModel Definition**:
```python
class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(index=True, nullable=False)
    role: MessageRole = Field(nullable=False)
    content: str = Field(nullable=False)
    tool_calls: dict | None = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    conversation: Conversation = Relationship(back_populates="messages")
```

---

## State Transitions

### Conversation States

```
┌─────────┐     User sends      ┌──────────┐
│  None   │────first message───▶│  Active  │
└─────────┘                     └──────────┘
                                     │
                                     │ (implicit - always active)
                                     ▼
                                ┌──────────┐
                                │  Active  │◀──── User sends more messages
                                └──────────┘
```

### Task States (via MCP Tools)

```
┌─────────┐     add_task      ┌──────────┐
│  None   │──────────────────▶│  Pending │
└─────────┘                   └──────────┘
                                   │
                           complete_task
                                   │
                                   ▼
                              ┌───────────┐
                              │ Completed │
                              └───────────┘
                                   │
            ┌──────────────────────┴──────────────────────┐
            │                                              │
       delete_task                                    delete_task
            │                                              │
            ▼                                              ▼
       ┌─────────┐                                    ┌─────────┐
       │ Deleted │                                    │ Deleted │
       └─────────┘                                    └─────────┘
```

---

## Validation Rules

### Conversation
- `user_id`: Required, non-empty string
- `title`: Optional, max 200 characters

### Message
- `conversation_id`: Must reference existing conversation
- `user_id`: Required, must match conversation owner
- `role`: Must be 'user' or 'assistant'
- `content`: Required, non-empty string
- `tool_calls`: Valid JSON if present

### Task (unchanged from Phase 2)
- `title`: Required, 1-200 characters
- `description`: Optional, max 1000 characters
- `priority`: Must be 'low', 'medium', or 'high'

---

## Migration Plan

### New Tables Required
1. `conversations` - Chat session tracking
2. `messages` - Chat message history

### Migration Script Outline
```sql
-- Migration: Create Phase 3 chat tables

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR NOT NULL,
    title VARCHAR(200),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_user_updated ON conversations(user_id, updated_at DESC);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id VARCHAR NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    tool_calls JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_created ON messages(conversation_id, created_at);
```

---

## Query Patterns

### Load Conversation History
```sql
SELECT m.* FROM messages m
WHERE m.conversation_id = :conversation_id
ORDER BY m.created_at ASC
LIMIT 50;
```

### Get User's Recent Conversations
```sql
SELECT c.* FROM conversations c
WHERE c.user_id = :user_id
ORDER BY c.updated_at DESC
LIMIT 10;
```

### MCP Tool: List Tasks
```sql
SELECT * FROM tasks
WHERE user_id = :user_id
  AND (:status = 'all' OR completed = (:status = 'completed'))
ORDER BY created_at DESC;
```

---

## Data Retention

- **Conversations**: Kept indefinitely (user can delete)
- **Messages**: Kept with parent conversation
- **Tasks**: Kept indefinitely (user manages lifecycle)

---

## Summary

| Model | Status | Changes from Phase 2 |
|-------|--------|---------------------|
| Task | Existing | No changes needed |
| Conversation | New | Chat session tracking |
| Message | New | Chat history storage |

Total new tables: 2
Total indexes: 5 (3 new)
