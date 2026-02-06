# Phase 3 Backend - Todo AI Chatbot

AI-powered chatbot backend with natural language task management using FastAPI, OpenRouter (OpenAI-compatible), and MCP tools.

## Tech Stack

- **Framework**: FastAPI 0.115+
- **AI/LLM**: OpenRouter API (OpenAI-compatible)
- **MCP**: Model Context Protocol for tool integration
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL (shared with Phase 2) / SQLite (development)
- **Authentication**: JWT (shared with Phase 2)
- **Python**: 3.11+

---

## Quick Start (Step-by-Step)

### Step 1: Navigate to Backend Directory

```bash
cd phase3/backend
```

### Step 2: Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
```

**Windows (Command Prompt):**
```cmd
python -m venv .venv
```

**Linux/macOS:**
```bash
python3 -m venv .venv
```

### Step 3: Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

> You should see `(.venv)` at the beginning of your terminal prompt.

### Step 4: Upgrade pip (Recommended)

```bash
pip install --upgrade pip
```

### Step 5: Install Dependencies

**Install all dependencies (including dev tools):**
```bash
pip install -e ".[dev]"
```

**Or install only production dependencies:**
```bash
pip install -e .
```


**Edit `.env` with your settings:**
```env
# Database (same as Phase 2)
DATABASE_URL=sqlite+aiosqlite:///./todo_app.db
# For PostgreSQL: DATABASE_URL=postgresql+asyncpg://user:pass@host/dbname

# OpenRouter API Key (get from https://openrouter.ai/keys)
OPEN_ROUTER_KEY=sk-or-v1-your-openrouter-api-key-here
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=openai/gpt-4o-mini

# Better Auth (same as Phase 2)
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters-long

# CORS - Frontend URL
CORS_ORIGINS=["http://localhost:3000"]

# Environment
ENVIRONMENT=development
```

### Step 7: Get OpenRouter API Key

1. Go to https://openrouter.ai
2. Sign up or sign in
3. Navigate to **Keys** section
4. Create a new API key
5. Copy the key to your `.env` file as `OPEN_ROUTER_KEY`

### Step 8: Start the Development Server

```bash
uvicorn src.main:app --reload --port 8001
```

The AI Chat API will be available at: **http://localhost:8001**

---

## Complete Setup Commands (Copy-Paste Ready)

### Windows (PowerShell) - One-Line Setup
```powershell
cd phase3/backend; python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install --upgrade pip; pip install -e ".[dev]"; copy .env.example .env; uvicorn src.main:app --reload --port 8001
```

### Linux/macOS - One-Line Setup
```bash
cd phase3/backend && python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install -e ".[dev]" && cp .env.example .env && uvicorn src.main:app --reload --port 8001
```

---

## Using UV Package Manager (Alternative)

If you have UV installed, you can use it instead of pip:

### Install with UV
```bash
cd phase3/backend
uv sync
```

### Run with UV
```bash
uv run uvicorn src.main:app --reload --port 8001
```

### Run Tests with UV
```bash
uv run pytest
```

---

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | Database connection string | Yes | - |
| `OPEN_ROUTER_KEY` | OpenRouter API key | Yes | - |
| `LLM_BASE_URL` | LLM API base URL | No | `https://openrouter.ai/api/v1` |
| `LLM_MODEL` | Model to use | No | `openai/gpt-4o-mini` |
| `BETTER_AUTH_SECRET` | JWT secret (same as Phase 2) | Yes | - |
| `CORS_ORIGINS` | Allowed CORS origins | No | `["http://localhost:3000"]` |
| `ENVIRONMENT` | `development` or `production` | No | `development` |
| `RATE_LIMIT_REQUESTS` | Rate limit per window | No | `100` |
| `RATE_LIMIT_WINDOW_SECONDS` | Rate limit window | No | `60` |

### Supported LLM Models via OpenRouter

| Model | Description | Speed |
|-------|-------------|-------|
| `openai/gpt-4o-mini` | Default, cost-effective | Fast |
| `openai/gpt-4o` | More capable | Medium |
| `anthropic/claude-3-haiku` | Fast Claude | Fast |
| `anthropic/claude-3-sonnet` | Balanced Claude | Medium |
| `google/gemini-flash-1.5` | Fast Gemini | Fast |
| `meta-llama/llama-3.1-70b-instruct` | Open source | Medium |

---

## API Endpoints

### ChatKit Endpoint (Primary - for Frontend UI)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chatkit` | ChatKit-compatible streaming endpoint |
| OPTIONS | `/chatkit` | CORS preflight for ChatKit |

### Chat API (REST)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/{user_id}/chat` | Send message, get AI response |
| GET | `/api/{user_id}/conversations` | List user's conversations |
| GET | `/api/{user_id}/conversations/{id}` | Get conversation with messages |
| DELETE | `/api/{user_id}/conversations/{id}` | Delete conversation |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | API health check |

---

## MCP Tools

The AI agent has access to these MCP tools for task management:

### Core Tools

| Tool | Description | Example Usage |
|------|-------------|---------------|
| `add_task` | Create new tasks | "Add a task to buy groceries" |
| `list_tasks` | View tasks with filters | "Show my pending tasks" |
| `complete_task` | Mark tasks as done | "Mark task 1 as complete" |
| `delete_task` | Remove tasks | "Delete the groceries task" |
| `update_task` | Modify task details | "Change the priority to high" |
| `get_analytics` | Get task statistics | "How many tasks did I complete?" |

### Collaboration Tools (Phase 3.5)

| Tool | Description | Example Usage |
|------|-------------|---------------|
| `share_task` | Share task with user | "Share this task with john@example.com" |
| `add_comment` | Comment on task | "Add a comment to task 1" |
| `assign_task` | Assign task to user | "Assign this to sarah@example.com" |
| `get_suggestions` | Smart suggestions | "What should I focus on today?" |

### Supported Natural Language

The AI understands:

- **English**: "Add a task", "Show my tasks", "Complete task 1"
- **Roman Urdu**: "Mujhe kal grocery leni hai", "Task complete karo"
- **Urdu Script**: "آج کے کام دکھاؤ"
- **Casual Language**: "tmrw meeting prep high pri"
- **Context**: "Complete it", "Delete that task"

---

## Testing

### Run All Tests
```bash
pytest
```

### Run Tests with Verbose Output
```bash
pytest -v
```

### Run Tests with Coverage
```bash
pytest --cov=src --cov-report=term-missing
```

### Generate HTML Coverage Report
```bash
pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

---

## Project Structure

```
phase3/backend/
├── src/
│   ├── main.py                 # FastAPI application entry
│   ├── config.py               # Settings management
│   ├── db.py                   # Database connection
│   ├── auth.py                 # JWT authentication
│   ├── errors.py               # Error handling
│   ├── middleware.py           # CORS, logging middleware
│   ├── chatkit_server.py       # ChatKit-compatible endpoint
│   │
│   ├── models/                 # SQLModel database models
│   │   ├── __init__.py
│   │   ├── conversation.py     # Chat conversation model
│   │   └── message.py          # Chat message model
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── agent_service.py    # OpenRouter LLM integration
│   │   ├── chat_service.py     # Chat handling
│   │   ├── context_manager.py  # Task reference tracking
│   │   └── suggestions.py      # Smart suggestions
│   │
│   ├── utils/                  # Utility modules
│   │   ├── __init__.py
│   │   └── date_parser.py      # Natural language date parsing
│   │
│   ├── mcp/                    # MCP (Model Context Protocol)
│   │   ├── __init__.py
│   │   ├── server.py           # Tool registry
│   │   └── tools/              # MCP tools
│   │       ├── __init__.py
│   │       ├── add_task.py
│   │       ├── list_tasks.py
│   │       ├── complete_task.py
│   │       ├── delete_task.py
│   │       ├── update_task.py
│   │       ├── get_analytics.py
│   │       ├── get_suggestions.py
│   │       ├── share_task.py
│   │       ├── add_comment.py
│   │       └── assign_task.py
│   │
│   └── api/                    # API routes
│       ├── __init__.py
│       └── chat.py             # Chat endpoints
│
├── tests/                      # Test files
│   └── conftest.py
│
├── .env.example                # Environment template
├── pyproject.toml              # Project dependencies
└── README.md                   # This file
```

---

## Database

Phase 3 adds these tables to the Phase 2 database:

| Table | Description |
|-------|-------------|
| `conversations` | Chat sessions per user |
| `messages` | Chat messages (user and assistant) |

Tables are auto-created on startup via SQLModel.

---

## Running Both Backends

To run the full stack with both Phase 2 and Phase 3 backends:

### Terminal 1 - Phase 2 Backend (Port 8000)
```bash
cd phase2/backend
.\.venv\Scripts\Activate.ps1  # Windows
uvicorn src.main:app --reload --port 8000
```

### Terminal 2 - Phase 3 AI Backend (Port 8001)
```bash
cd phase3/backend
.\.venv\Scripts\Activate.ps1  # Windows
uvicorn src.main:app --reload --port 8001
```

### Terminal 3 - Frontend (Port 3000)
```bash
cd phase2/frontend
npm run dev
```

---

## Troubleshooting

### Virtual Environment Not Activating (Windows PowerShell)
```powershell
# Run this first to allow scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then activate
.\.venv\Scripts\Activate.ps1
```

### OpenRouter API Errors

1. **401 Unauthorized**: Check your `OPEN_ROUTER_KEY` is valid
2. **429 Rate Limited**: Wait or upgrade your OpenRouter plan
3. **Model not found**: Check `LLM_MODEL` is a valid model name

### Database Connection Errors

1. Verify `DATABASE_URL` in `.env` matches Phase 2
2. Ensure Phase 2 backend has run migrations first

### Import Errors
```bash
# Make sure you installed in editable mode
pip install -e ".[dev]"
```

### Port Already in Use
```bash
# Use a different port
uvicorn src.main:app --reload --port 8002
```

---

## API Documentation

When the server is running, interactive API docs are available at:

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

---

## Example Chat Interactions

### Creating Tasks
```
User: "Add a high priority task to prepare presentation for tomorrow"
AI: "I've created a high priority task 'Prepare presentation' due tomorrow."
```

### Listing Tasks
```
User: "Show my overdue tasks"
AI: "You have 2 overdue tasks: 1. Review report (3 days overdue)..."
```

### Natural Language (Roman Urdu)
```
User: "Mujhe kal meeting ki tayyari karni hai"
AI: "Maine 'Meeting ki tayyari' task create kar diya hai kal ke liye."
```

### Getting Suggestions
```
User: "What should I focus on today?"
AI: "Based on your tasks, I recommend: 1. Review report (overdue)..."
```

---

## Development Workflow

1. **Activate virtual environment** before any work
2. **Ensure Phase 2 backend is running** for shared database
3. **Run tests** before committing: `pytest`
4. **Check code style**: `ruff check src/`
5. **Format code**: `ruff format src/`

---

## Production Deployment

```bash
# Install production dependencies only
pip install -e .

# Run with Gunicorn + Uvicorn workers
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8001
```

---

Built with FastAPI + OpenRouter for the Hackathon II - Evolution of Todo
