# Phase 4 Backend - Unified Todo API

**Version**: 4.0.0
**Status**: Phase 2 (CRUD) + Phase 3 (AI Chatbot) - Merged

FastAPI backend combining full CRUD operations with AI-powered chat assistant capabilities.

---

## 🎯 What's Included

This unified backend includes **ALL features** from Phase 2 and Phase 3:

✅ **Phase 2 Features:**
- Complete CRUD API for tasks
- User authentication (JWT)
- Task management (priorities, tags, due dates)
- Projects
- Task sharing & collaboration
- Comments
- Activity feed
- User preferences
- Email reminders (optional)

✅ **Phase 3 Features:**
- AI Chat Assistant (OpenAI Agents SDK)
- ChatKit integration
- 13 MCP Tools
- Smart task suggestions
- Auto-categorization
- Natural language processing
- Context-aware responses

---

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- PostgreSQL (Neon) or SQLite for local dev
- OpenRouter API key (for AI features)

### Step 1: Navigate to Backend

```bash
cd phase4/backend
```

### Step 2: Install Dependencies (Using UV)

**Recommended - Using UV (faster):**
```bash
# Install UV if you don't have it
pip install uv

# Sync dependencies
uv sync
```

**Alternative - Using pip:**
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
```
# Windows (Command Prompt):
.venv\Scripts\activate.bat

# Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

### Step 3: Configure Environment

The `.env` file is already configured with your Phase 2 + Phase 3 settings:

```env
# Database - Neon PostgreSQL
DATABASE_URL=postgresql://neondb_owner:npg_pVXCFQuxv41y@...

# OpenRouter API (for AI features)
OPEN_ROUTER_KEY=sk-or-v1-449d16b1e0397f2df...
LLM_MODEL=openai/gpt-4o-mini

# Better Auth
BETTER_AUTH_SECRET=oMJcqdXodnFjgWJGr6gdiXw...
BETTER_AUTH_URL=http://localhost:8000

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001"]

# Environment
ENVIRONMENT=development
```

**All your existing credentials are preserved!** ✅

### Step 4: Run Database Migrations

```bash
# Using UV
uv run alembic upgrade head

# Or with virtual environment activated
alembic upgrade head
```

### Step 5: Start the Backend Server

```bash
# Using UV (recommended)
uv run uvicorn src.main:app --reload --port 8000

# Or with virtual environment activated
uvicorn src.main:app --reload --port 8000
```

**Backend is now running at:**
- 🌐 API: http://localhost:8000
- 📚 Docs: http://localhost:8000/docs
- ❤️ Health: http://localhost:8000/health

---

## 📋 One-Line Startup Commands

### Using UV (Recommended - Fastest)

```bash
cd phase4/backend && uv sync && uv run alembic upgrade head && uv run uvicorn src.main:app --reload --port 8000
```

### Using Traditional venv

**Windows PowerShell:**
```powershell
cd phase4/backend; python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -e ".[dev]"; alembic upgrade head; uvicorn src.main:app --reload --port 8000
```

**Linux/macOS:**
```bash
cd phase4/backend && python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]" && alembic upgrade head && uvicorn src.main:app --reload --port 8000
```

---

## 🔧 Tech Stack

- **Framework**: FastAPI 0.115+
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL (Neon serverless)
- **Authentication**: JWT + Better Auth
- **Migrations**: Alembic
- **AI**: OpenAI Agents SDK + OpenRouter
- **Python**: 3.13+

---

## 📊 API Endpoints

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | API health check (returns v4.0.0) |

### Phase 2 - CRUD Endpoints

**Authentication:**
- `POST /api/auth/signup` - Create account
- `POST /api/auth/signin` - Login (get JWT)
- `GET /api/auth/me` - Get current user

**Tasks:**
- `GET /api/tasks` - List tasks (with filters)
- `POST /api/tasks` - Create task
- `GET /api/tasks/{id}` - Get task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `PATCH /api/tasks/{id}/complete` - Toggle completion

**Collaboration:**
- `POST /api/tasks/{id}/shares` - Share task
- `POST /api/tasks/{id}/comments` - Add comment
- `GET /api/users/search` - Search users
- `GET /api/activities` - Activity feed

**Projects:**
- `GET /api/projects` - List projects
- `POST /api/projects` - Create project

**Preferences:**
- `GET /api/preferences` - Get user preferences
- `PUT /api/preferences` - Update preferences

### Phase 3 - AI Endpoints

**Chat:**
- `POST /api/chat/conversations` - Create conversation
- `POST /api/chat/messages` - Send message
- `GET /api/chat/suggestions` - Get AI suggestions

**ChatKit:**
- `POST /chatkit` - ChatKit endpoint (SSE streaming)

---

## 🤖 MCP Tools Available (13 Tools)

The AI assistant can use these tools via natural language:

1. `add_task` - Create new tasks
2. `list_tasks` - View tasks
3. `update_task` - Modify tasks
4. `delete_task` - Remove tasks
5. `complete_task` - Mark complete/incomplete
6. `assign_task` - Assign to users
7. `share_task` - Share with others
8. `add_comment` - Add comments
9. `get_analytics` - View statistics
10. `get_suggestions` - Get AI suggestions
11. `search_tasks` - Search tasks
12. `prioritize_tasks` - Auto-prioritize
13. `categorize_tasks` - Auto-categorize

---

## 🌍 Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection | `postgresql://user:pass@host/db` |
| `BETTER_AUTH_SECRET` | JWT secret (min 32 chars) | Generated string |
| `OPEN_ROUTER_KEY` | OpenRouter API key | `sk-or-v1-...` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_MODEL` | `openai/gpt-4o-mini` | AI model to use |
| `LLM_BASE_URL` | `https://openrouter.ai/api/v1` | LLM API endpoint |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed origins |
| `ENVIRONMENT` | `development` | Environment mode |
| `RATE_LIMIT_REQUESTS` | `100` | Requests per minute |
| `AGENT_MAX_TOKENS` | `2000` | Max tokens per response |

---

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# With coverage
uv run pytest --cov=src --cov-report=term-missing

# Specific test file
uv run pytest tests/test_auth.py -v

# Generate HTML coverage report
uv run pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

---

## 📁 Project Structure

```
phase4/backend/
├── .env                      # ✅ Your configuration (merged)
├── .env.example              # Environment template
├── alembic/                  # Database migrations
│   ├── versions/             # Migration files
│   └── env.py
├── src/
│   ├── api/                  # API endpoints
│   │   ├── auth.py           # Authentication (Phase 2)
│   │   ├── tasks.py          # Task CRUD (Phase 2)
│   │   ├── users.py          # User management (Phase 2)
│   │   ├── projects.py       # Projects (Phase 2)
│   │   ├── comments.py       # Comments (Phase 2)
│   │   ├── shares.py         # Sharing (Phase 2)
│   │   ├── activities.py     # Activity feed (Phase 2)
│   │   ├── preferences.py    # Preferences (Phase 2)
│   │   └── chat.py           # AI Chat (Phase 3)
│   │
│   ├── mcp/                  # MCP Tools (Phase 3)
│   │   ├── server.py         # MCP server
│   │   └── tools/            # 13 MCP tools
│   │
│   ├── models/               # Database models
│   │   ├── user.py
│   │   ├── task.py
│   │   ├── conversation.py   # Phase 3
│   │   └── message.py        # Phase 3
│   │
│   ├── services/             # Business logic
│   │   ├── auth.py
│   │   ├── task.py
│   │   ├── scheduler.py      # Email reminders (Phase 2)
│   │   ├── agent_service.py  # OpenAI Agents (Phase 3)
│   │   ├── chat_service.py   # Chat logic (Phase 3)
│   │   └── suggestions.py    # AI suggestions (Phase 3)
│   │
│   ├── utils/                # Utilities (Phase 3)
│   │   └── date_parser.py    # Natural date parsing
│   │
│   ├── auth.py               # JWT verification (Phase 3)
│   ├── chatkit_server.py     # ChatKit integration (Phase 3)
│   ├── config.py             # ✨ Unified configuration
│   ├── database.py           # Database connection
│   ├── middleware.py         # Rate limiting (Phase 3)
│   └── main.py               # ✨ Unified FastAPI app (v4.0.0)
│
├── tests/                    # Test files
├── pyproject.toml            # Project dependencies
└── README.md                 # This file
```

---

## 🗄️ Database Migrations

### Create New Migration
```bash
uv run alembic revision --autogenerate -m "description"
```

### Run Migrations
```bash
uv run alembic upgrade head
```

### Rollback Last Migration
```bash
uv run alembic downgrade -1
```

---

## 🔍 API Documentation

When running, interactive docs are available:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🐛 Troubleshooting

### Backend Won't Start

```bash
# Check if port 8000 is in use
# Use a different port
uv run uvicorn src.main:app --reload --port 8001
```

### Database Connection Errors

1. Verify `DATABASE_URL` in `.env` is correct
2. Check Neon database is accessible
3. Try local SQLite: `DATABASE_URL=sqlite:///./todo_app.db`

### AI Features Not Working

1. Verify `OPEN_ROUTER_KEY` is valid
2. Check OpenRouter API status
3. Ensure model (`gpt-4o-mini`) is available

### Import Errors

```bash
# Reinstall in editable mode
uv sync
# Or
pip install -e ".[dev]"
```

---

## 🚀 What Changed from Phase 2 & 3

### Before
- `phase2/backend` - CRUD only
- `phase3/backend` - AI only (separate)

### After (Phase 4)
- **Single unified backend** with ALL features
- Merged configuration (`.env`)
- Single `main.py` with all routers
- Shared database connection
- Combined middleware

### Benefits
✅ One server instead of two
✅ Simpler deployment
✅ Better resource usage
✅ Easier testing
✅ Container-ready for Phase 4

---

## 📈 Next Steps

Phase 4 will containerize this backend:

1. Create `Dockerfile`
2. Create `docker-compose.yaml`
3. Deploy to Kubernetes (Minikube)
4. Create Helm charts

**No new features - just packaging!**

---

**Ready to run! Start with:** `uv run uvicorn src.main:app --reload --port 8000` 🚀
