# Hackathon II - The Evolution of Todo

This is the Evolution of Todo project, a multi-phase hackathon project that evolves from a simple console application to an AI-powered, cloud-native solution.

## Phases

### Phase I - Console Application
A simple, in-memory Python console application for managing todo tasks.

#### Features
This application provides the 5 basic todo features:
1. **Add Task** - Create new todo items with title and optional description
2. **View Task List** - Display all tasks with their status
3. **Update Task** - Modify existing task details
4. **Delete Task** - Remove tasks from the list
5. **Mark Task Complete/Incomplete** - Toggle task completion status

#### How to Run Phase I
```bash
python -m src.phase1.main
```

### Phase II - Full-Stack Web Application
A Next.js frontend with FastAPI backend, Neon PostgreSQL database, and Better Auth for authentication.

#### Features
- Full CRUD operations for tasks
- User authentication and authorization
- Responsive web interface
- Database persistence

#### How to Run Phase II
```bash
# Backend
cd phase2/backend
uvicorn src.main:app --reload

# Frontend
cd phase2/frontend
npm run dev
```

### Phase III - AI Chatbot ✅ Complete
An AI-powered chatbot interface for managing todos through natural language using OpenAI Agents SDK, MCP tools, and ChatKit UI integrated into the Phase 2 frontend.

#### Features
- **Natural Language Task Management** - Add, view, update, delete, and complete tasks via conversation
- **5 MCP Tools** - add_task, list_tasks, complete_task, delete_task, update_task
- **OpenAI Agents SDK** - Intelligent agent that understands context and executes actions
- **ChatKit Integration** - Beautiful chat UI with SSE streaming responses
- **Conversation History** - Messages and conversations persisted to database
- **User Isolation** - JWT authentication with user_id filtering on all queries
- **Stateless Architecture** - Horizontally scalable, all state in database

#### Architecture
```
Phase 2 Frontend (Next.js)
    └── /chat route with ChatKit UI
            │
            ▼ (HTTP + JWT)
Phase 3 Backend (FastAPI)
    └── /chatkit endpoint (SSE streaming)
            │
            ▼
    TodoChatKitServer (ChatKit Python SDK)
            │
            ▼
    AgentService (OpenAI Agents SDK)
            │
            ▼
    MCP Server with 5 Tools
            │
            ▼
    Neon PostgreSQL (shared with Phase 2)
```

#### How to Run Phase III
```bash
# 1. Start Phase 3 Backend (port 8001)
cd phase3/backend
pip install -e .
uvicorn src.main:app --reload --port 8001

# 2. Start Phase 2 Frontend (includes ChatKit UI)
cd phase2/frontend
npm run dev

# 3. Access the chat at http://localhost:3000/chat
```

#### Environment Variables
**phase3/backend/.env:**
```env
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=sqlite:///./todo_app.db  # or Neon PostgreSQL URL
BETTER_AUTH_SECRET=your_better_auth_secret
FRONTEND_URL=http://localhost:3000
```

**phase2/frontend/.env.local:**
```env
NEXT_PUBLIC_CHATKIT_API_URL=http://localhost:8001
```

#### Example Conversations
```
User: Add a task to buy groceries tomorrow
AI: ✅ Task created: "Buy groceries tomorrow" (ID: 5)

User: Show me my tasks
AI: Here are your tasks:
    1. Buy groceries tomorrow - pending
    2. Call mom - completed
    ...

User: Mark task 1 as complete
AI: ✅ Task "Buy groceries tomorrow" marked as complete!

User: Delete task 2
AI: ✅ Task "Call mom" has been deleted.
```

## Architecture Evolution

| Phase | Description | Status |
|-------|-------------|--------|
| **Phase I** | In-memory Python console app | ✅ Complete |
| **Phase II** | Full-stack web app (Next.js + FastAPI + Neon + Better Auth) | ✅ Complete |
| **Phase III** | AI chatbot (OpenAI Agents SDK + MCP + ChatKit) | ✅ Complete |
| **Phase IV** | Containerized solution (Docker + Minikube + Helm) | ⏳ Upcoming |
| **Phase V** | Cloud-native event-driven (AKS/GKE + Kafka + Dapr) | ⏳ Upcoming |

## Requirements

- Python 3.13+ (backend services)
- Node.js 18+ (frontend)
- PostgreSQL / Neon (persistent storage)
- OpenAI API key (AI chatbot - Phase III)

## Project Structure

```
HACKATHON-TODO-APP/
├── phase1/                 # Console Application
├── phase2/
│   ├── backend/           # FastAPI + SQLModel + Better Auth
│   └── frontend/          # Next.js + ChatKit UI (Phase 3 integrated)
├── phase3/
│   └── backend/           # OpenAI Agents SDK + MCP Server
├── specs/                 # Specifications (Spec-Driven Development)
│   ├── phase1/
│   ├── phase2/
│   └── phase3/
└── history/               # ADRs and Prompt History Records
```

## Important Notes

This project follows **Spec-Driven Development (SDD)** principles - all implementations are derived from specifications. It demonstrates progressive complexity from a simple console app to an AI-powered cloud-native system.



