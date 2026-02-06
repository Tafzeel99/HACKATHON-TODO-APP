# Quickstart Guide: Phase 3 - Todo AI Chatbot

**Date**: 2026-01-19
**Feature**: Phase 3 AI Chatbot
**Prerequisites**: Phase 2 backend and frontend running

---

## Prerequisites

Before starting Phase 3 development, ensure:

1. **Phase 2 Completed**
   - Backend running on `http://localhost:8000`
   - Frontend running on `http://localhost:3000`
   - Database migrations applied
   - Authentication working

2. **Required Accounts**
   - OpenAI API account with API key
   - OpenAI ChatKit domain allowlist configured (for deployment)

3. **Development Environment**
   - Python 3.13+
   - Node.js 18+
   - UV package manager
   - pnpm or npm

---

## Directory Setup

```bash
# From repository root
cd "/mnt/d/IT CLASSES pc/HACKATHON-TODO-APP"

# Create Phase 3 directories (already created by /sp.specify)
mkdir -p phase3/backend/src/{models,services,mcp/tools,api}
mkdir -p phase3/backend/tests/{unit,integration}
mkdir -p phase3/frontend/src/{app/chat,components/chat,lib,types}
```

---

## Backend Setup

### 1. Initialize Backend Project

```bash
cd phase3/backend

# Initialize with UV
uv init --name todo-ai-chatbot

# Add dependencies
uv add fastapi uvicorn sqlmodel asyncpg
uv add openai  # OpenAI Agents SDK
uv add mcp     # MCP Python SDK
uv add python-dotenv pydantic-settings

# Dev dependencies
uv add --dev pytest pytest-asyncio httpx
```

### 2. Environment Configuration

Create `.env` file:

```env
# Database (reuse Phase 2)
DATABASE_URL=postgresql+asyncpg://user:password@host/dbname

# OpenAI
OPENAI_API_KEY=sk-your-api-key-here

# Auth (reuse Phase 2)
JWT_SECRET=your-jwt-secret
```

### 3. Run Backend

```bash
# Development
uv run uvicorn src.main:app --reload --port 8001

# Or with the dev script
uv run dev
```

---

## Frontend Setup

### 1. Initialize Frontend Project

```bash
cd phase3/frontend

# Initialize Next.js
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir

# Add ChatKit dependencies
npm install @openai/chatkit
npm install @tanstack/react-query
```

### 2. Environment Configuration

Create `.env.local`:

```env
# API endpoint
NEXT_PUBLIC_API_URL=http://localhost:8001

# OpenAI ChatKit (for hosted deployment)
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key
```

### 3. Run Frontend

```bash
# Development
npm run dev

# Runs on http://localhost:3001
```

---

## Database Migration

Apply new tables for Phase 3:

```bash
cd phase3/backend

# Generate migration
uv run alembic revision --autogenerate -m "Add conversations and messages tables"

# Apply migration
uv run alembic upgrade head
```

Or manually via SQL:

```sql
-- Connect to Neon database and run:

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR NOT NULL,
    title VARCHAR(200),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);

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
```

---

## Quick Test

### 1. Test Chat Endpoint

```bash
# Get auth token (from Phase 2 login)
TOKEN="your-jwt-token"

# Send chat message
curl -X POST "http://localhost:8001/api/user_123/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy groceries"}'
```

Expected response:

```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "response": "I've added 'Buy groceries' to your task list!",
  "tool_calls": [
    {
      "tool": "add_task",
      "result": {
        "task_id": 5,
        "status": "created",
        "title": "Buy groceries"
      }
    }
  ]
}
```

### 2. Test via Frontend

1. Navigate to `http://localhost:3001/chat`
2. Login with existing credentials
3. Type "Add a task to test the chatbot"
4. Verify task appears and confirmation received

---

## Project Structure After Setup

```
phase3/
├── backend/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Settings
│   │   ├── db.py                # Database connection
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── conversation.py  # Conversation model
│   │   │   └── message.py       # Message model
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── agent_service.py # OpenAI Agents SDK
│   │   │   └── chat_service.py  # Chat logic
│   │   ├── mcp/
│   │   │   ├── __init__.py
│   │   │   ├── server.py        # MCP server setup
│   │   │   └── tools/
│   │   │       ├── __init__.py
│   │   │       ├── add_task.py
│   │   │       ├── list_tasks.py
│   │   │       ├── complete_task.py
│   │   │       ├── delete_task.py
│   │   │       └── update_task.py
│   │   └── api/
│   │       ├── __init__.py
│   │       └── chat.py          # Chat endpoint
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── unit/
│   │   └── integration/
│   ├── pyproject.toml
│   ├── .env
│   └── README.md
│
└── frontend/
    ├── src/
    │   ├── app/
    │   │   ├── layout.tsx
    │   │   └── chat/
    │   │       └── page.tsx     # Chat page
    │   ├── components/
    │   │   └── chat/
    │   │       └── ChatInterface.tsx
    │   ├── lib/
    │   │   └── api.ts           # API client
    │   └── types/
    │       └── chat.ts
    ├── package.json
    ├── .env.local
    └── README.md
```

---

## Common Issues

### OpenAI API Key Issues
- Ensure `OPENAI_API_KEY` is set in `.env`
- Check API key has sufficient credits
- Verify key permissions include chat completions

### Database Connection
- Ensure Phase 2 database URL is correct
- Check Neon connection pooling settings
- Verify SSL mode if required

### CORS Issues
- Backend must allow frontend origin
- Check CORS middleware configuration

### ChatKit Domain Issues
- Add your deployment domain to OpenAI allowlist
- localhost typically works without configuration

---

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Implement backend MCP tools
3. Implement chat endpoint
4. Integrate ChatKit UI
5. Test end-to-end flow
6. Deploy to Vercel/Railway
