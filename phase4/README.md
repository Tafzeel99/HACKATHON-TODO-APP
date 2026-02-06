# Phase 4 - Unified Todo Application

**Status**: Consolidated Backend & Frontend (Phase 2 + Phase 3)
**Version**: 4.0.0
**Next Step**: Containerization with Docker & Kubernetes

---

## 📋 Overview

Phase 4 consolidates the complete application from Phase 2 and Phase 3 into a unified codebase:

- **Frontend**: Single Next.js application with all features
- **Backend**: Unified FastAPI backend with CRUD APIs + AI Chatbot

This consolidation prepares the application for containerization and Kubernetes deployment in Phase 4.

---

## 🏗️ Architecture

```
phase4/
├── frontend/              # Next.js 16 App Router
│   ├── src/
│   │   ├── app/          # App Router pages
│   │   ├── components/   # React components
│   │   ├── lib/          # Utilities & API client
│   │   └── types/        # TypeScript types
│   └── package.json
│
└── backend/              # FastAPI Unified Backend
    ├── src/
    │   ├── api/          # REST API endpoints
    │   │   ├── auth.py       # Authentication (Phase 2)
    │   │   ├── tasks.py      # Task CRUD (Phase 2)
    │   │   ├── users.py      # User management (Phase 2)
    │   │   ├── projects.py   # Projects (Phase 2)
    │   │   ├── comments.py   # Comments (Phase 2)
    │   │   ├── shares.py     # Sharing (Phase 2)
    │   │   ├── activities.py # Activity feed (Phase 2)
    │   │   ├── preferences.py # User preferences (Phase 2)
    │   │   └── chat.py       # AI Chat API (Phase 3)
    │   │
    │   ├── mcp/          # MCP Tools (Phase 3)
    │   │   ├── server.py
    │   │   └── tools/
    │   │       ├── add_task.py
    │   │       ├── list_tasks.py
    │   │       ├── complete_task.py
    │   │       └── ... (10 more tools)
    │   │
    │   ├── models/       # Database models
    │   ├── services/     # Business logic
    │   │   ├── scheduler.py      # Email reminders (Phase 2)
    │   │   ├── agent_service.py  # OpenAI Agents (Phase 3)
    │   │   ├── chat_service.py   # Chat logic (Phase 3)
    │   │   └── suggestions.py    # AI suggestions (Phase 3)
    │   │
    │   ├── utils/        # Utilities (Phase 3)
    │   ├── auth.py       # JWT verification (Phase 3)
    │   ├── chatkit_server.py # ChatKit integration (Phase 3)
    │   ├── config.py     # Unified configuration
    │   ├── database.py   # Database connection
    │   ├── middleware.py # Rate limiting (Phase 3)
    │   └── main.py       # Unified FastAPI app
    │
    └── pyproject.toml
```

---

## ✨ Features Included

### Phase 2 Features (Full-Stack CRUD)

**Core Task Management:**
- ✅ Create, Read, Update, Delete tasks
- ✅ Mark tasks complete/incomplete
- ✅ Task priorities (Low, Medium, High)
- ✅ Task tags and categories
- ✅ Task descriptions and notes
- ✅ Due dates and scheduling

**Projects:**
- ✅ Create and manage projects
- ✅ Organize tasks by project
- ✅ Project colors and themes

**Collaboration:**
- ✅ Share tasks with other users
- ✅ Assign tasks to team members
- ✅ Comments on tasks
- ✅ Activity feed (who did what, when)

**User Management:**
- ✅ User authentication (Better Auth + JWT)
- ✅ User profiles
- ✅ User preferences (theme, notifications)

**Advanced Features:**
- ✅ Email reminders (optional SendGrid integration)
- ✅ Task statistics and analytics
- ✅ Calendar view
- ✅ Archive completed tasks
- ✅ Search and filter tasks

**UI/UX:**
- ✅ Responsive design (mobile-first)
- ✅ Dark mode / Light mode
- ✅ Theme colors (12 themes)
- ✅ Kanban board view
- ✅ List view
- ✅ Pull-to-refresh
- ✅ Swipeable tasks
- ✅ Bottom navigation (mobile)
- ✅ Sidebar navigation (desktop)

### Phase 3 Features (AI Chatbot)

**AI Chat Assistant:**
- ✅ Natural language task management
- ✅ Conversational interface (ChatKit)
- ✅ Smart task suggestions
- ✅ Auto-categorization
- ✅ Context-aware responses

**MCP Tools (13 tools):**
- ✅ `add_task` - Create tasks via chat
- ✅ `list_tasks` - View tasks
- ✅ `update_task` - Modify tasks
- ✅ `delete_task` - Remove tasks
- ✅ `complete_task` - Mark complete
- ✅ `assign_task` - Assign to users
- ✅ `share_task` - Share tasks
- ✅ `add_comment` - Add comments
- ✅ `get_analytics` - View stats
- ✅ `get_suggestions` - Get AI suggestions
- ✅ And more...

**OpenAI Agents SDK:**
- ✅ Agent-based architecture
- ✅ Multi-turn conversations
- ✅ Context management
- ✅ Streaming responses

**Smart Features:**
- ✅ Date parsing ("tomorrow", "next Friday")
- ✅ Priority detection
- ✅ Auto-categorization by keywords
- ✅ Task breakdown suggestions

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.13+
- PostgreSQL (Neon recommended) or SQLite for local dev

### 1. Backend Setup

```bash
cd phase4/backend

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your credentials:
# - DATABASE_URL
# - BETTER_AUTH_SECRET
# - OPEN_ROUTER_KEY

# Run migrations
alembic upgrade head

# Start backend
uv run uvicorn src.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd phase4/frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with:
# - NEXT_PUBLIC_API_URL=http://localhost:8000

# Start frontend
npm run dev
```

### 3. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🔧 Configuration

### Backend Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@host/dbname

# Better Auth
BETTER_AUTH_SECRET=your-secret-key
BETTER_AUTH_URL=https://your-auth-domain.com

# OpenRouter (for AI features)
OPEN_ROUTER_KEY=sk-or-v1-xxxxx
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=openai/gpt-4o-mini

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001"]

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60
```

### Frontend Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=https://your-auth-domain.com
```

---

## 📊 API Endpoints

### Phase 2 CRUD Endpoints

```
POST   /api/auth/login          # User login
POST   /api/auth/signup         # User registration
GET    /api/tasks               # List tasks
POST   /api/tasks               # Create task
GET    /api/tasks/{id}          # Get task
PUT    /api/tasks/{id}          # Update task
DELETE /api/tasks/{id}          # Delete task
POST   /api/tasks/{id}/share    # Share task
POST   /api/tasks/{id}/comments # Add comment
GET    /api/projects            # List projects
GET    /api/users               # List users
GET    /api/activities          # Activity feed
GET    /api/preferences         # User preferences
```

### Phase 3 AI Endpoints

```
POST   /api/chat/conversations  # Create chat conversation
POST   /api/chat/messages       # Send chat message
GET    /api/chat/suggestions    # Get AI suggestions
POST   /chatkit                 # ChatKit endpoint (SSE streaming)
```

---

## 🧪 Testing

### Backend Tests

```bash
cd phase4/backend
uv run pytest
```

### Frontend Tests

```bash
cd phase4/frontend
npm test
```

---

## 📈 Database Schema

**Core Tables:**
- `users` - User accounts
- `tasks` - Todo tasks
- `projects` - Project organization
- `task_shares` - Shared tasks
- `comments` - Task comments
- `activities` - Activity log
- `preferences` - User preferences
- `conversations` - Chat conversations (Phase 3)
- `messages` - Chat messages (Phase 3)

---

## 🔄 What Changed from Phase 2 & 3

### Unified Backend

**Before:**
- `phase2/backend` - CRUD APIs only
- `phase3/backend` - AI Chat only (separate codebase)

**After:**
- `phase4/backend` - All features in one codebase
- Single database connection
- Single configuration
- Single deployment unit

### Merged Configuration

- Combined `config.py` with all settings from both phases
- Unified CORS origins
- Single JWT verification
- Shared database connection

### Unified Main Application

- Single `main.py` with all routers
- Both Phase 2 CRUD and Phase 3 AI endpoints
- Shared middleware (CORS + Rate Limiting)
- Single health check

### Benefits

✅ **Simpler Deployment**: One backend instead of two
✅ **Shared Resources**: Single database, single config
✅ **Better Integration**: CRUD and AI features work together seamlessly
✅ **Easier Testing**: Test all features in one environment
✅ **Container Ready**: Single backend container for Phase 4

---

## 🐳 Next Steps (Containerization)

Phase 4 will containerize this unified application:

1. **Docker**
   - Create Dockerfile for backend
   - Create Dockerfile for frontend
   - Docker Compose for local development

2. **Kubernetes (Minikube)**
   - Deploy to local Kubernetes
   - Helm charts for deployment
   - kubectl-ai for management

3. **Tools**
   - kagent for Kubernetes AI assistance
   - Gordon for Docker AI assistance

**No new features** - Just packaging and deployment!

---

## 📝 Notes

- Frontend is identical to Phase 2 (already had chat UI from Phase 3)
- Backend is merged from Phase 2 + Phase 3
- All Phase 2 and Phase 3 features are preserved
- Database schema includes all tables from both phases
- Environment variables from both phases are required

---

## 🎯 Points Status

- ✅ Phase 1: 100 points (Console App)
- ✅ Phase 2: 200 points (Full-Stack Web App)
- ✅ Phase 3: 300 points (AI Chatbot)
- ⏳ Phase 4: 200 points (Containerization) - In Progress
- ⏳ Phase 5: 300+ points (Cloud + Advanced) - Not Started

**Total so far**: 600/1100+ points

---

**Ready for containerization! 🐳**
