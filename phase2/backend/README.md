# Phase 2 Backend - Todo REST API

FastAPI backend for the Todo application with user authentication, task management, and collaboration features.

## Tech Stack

- **Framework**: FastAPI 0.115+
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL (Neon serverless) / SQLite (development)
- **Authentication**: JWT (python-jose)
- **Migrations**: Alembic
- **Python**: 3.13+

---

## Quick Start (Step-by-Step)

### Step 1: Navigate to Backend Directory

```bash
cd phase2/backend
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
# Database - Neon PostgreSQL or local SQLite
DATABASE_URL=sqlite+aiosqlite:///./todo_app.db
# For PostgreSQL: DATABASE_URL=postgresql+asyncpg://user:pass@host/dbname

# JWT Authentication
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters-long

# CORS - Frontend URL
CORS_ORIGINS=http://localhost:3000

# Environment
ENVIRONMENT=development
```

### Step 7: Run Database Migrations

```bash
alembic upgrade head
```

### Step 8: Start the Development Server

```bash
uvicorn src.main:app --reload --port 8000
```

The API will be available at: **http://localhost:8000**

---

## Complete Setup Commands (Copy-Paste Ready)

### Windows (PowerShell) - One-Line Setup
```powershell
cd phase2/backend; python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install --upgrade pip; pip install -e ".[dev]"; copy .env.example .env; alembic upgrade head; uvicorn src.main:app --reload --port 8000
```

### Linux/macOS - One-Line Setup
```bash
cd phase2/backend && python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install -e ".[dev]" && cp .env.example .env && alembic upgrade head && uvicorn src.main:app --reload --port 8000
```

---

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | Database connection string | Yes | - |
| `BETTER_AUTH_SECRET` | JWT secret key (min 32 chars) | Yes | - |
| `CORS_ORIGINS` | Allowed CORS origins | No | `http://localhost:3000` |
| `ENVIRONMENT` | `development` or `production` | No | `development` |
| `JWT_ALGORITHM` | JWT signing algorithm | No | `HS256` |
| `JWT_EXPIRATION_DAYS` | Token expiration in days | No | `7` |

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Create new account |
| POST | `/api/auth/signin` | Login and get JWT token |
| POST | `/api/auth/signout` | Logout (client-side) |
| GET | `/api/auth/me` | Get current user info |

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | List user's tasks (with filters) |
| POST | `/api/tasks` | Create new task |
| GET | `/api/tasks/{id}` | Get task by ID |
| PUT | `/api/tasks/{id}` | Update task |
| DELETE | `/api/tasks/{id}` | Delete task |
| PATCH | `/api/tasks/{id}/complete` | Toggle task completion |
| GET | `/api/tasks/tags` | Get all user's tags |

### Collaboration (Phase 2.5)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks/{id}/shares` | List task shares |
| POST | `/api/tasks/{id}/shares` | Share task with user |
| DELETE | `/api/tasks/{id}/shares/{share_id}` | Remove share |
| GET | `/api/tasks/{id}/comments` | List task comments |
| POST | `/api/tasks/{id}/comments` | Add comment |
| GET | `/api/users/search` | Search users |
| GET | `/api/activities` | Get activity feed |

### Query Parameters (GET /api/tasks)

| Parameter | Values | Description |
|-----------|--------|-------------|
| `status` | `all`, `pending`, `completed` | Filter by completion |
| `sort` | `created`, `title`, `priority`, `due_date` | Sort field |
| `order` | `asc`, `desc` | Sort direction |
| `priority` | `low`, `medium`, `high` | Filter by priority |
| `tags` | comma-separated | Filter by tags |
| `search` | string | Search in title/description |
| `due_before` | ISO date | Due date filter |
| `due_after` | ISO date | Due date filter |
| `overdue_only` | boolean | Only overdue tasks |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | API health check |

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

### Run Tests with Coverage Report
```bash
pytest --cov=src --cov-report=term-missing
```

### Run Specific Test File
```bash
pytest tests/test_auth.py -v
pytest tests/test_tasks.py -v
```

### Generate HTML Coverage Report
```bash
pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

---

## Project Structure

```
phase2/backend/
├── alembic/                  # Database migrations
│   ├── versions/             # Migration files
│   │   ├── 001_initial.py
│   │   ├── 002_add_task_fields.py
│   │   └── 003_add_collaboration_tables.py
│   └── env.py
├── src/
│   ├── api/                  # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication routes
│   │   ├── tasks.py          # Task CRUD routes
│   │   ├── shares.py         # Task sharing routes
│   │   ├── comments.py       # Comment routes
│   │   ├── activities.py     # Activity feed routes
│   │   ├── users.py          # User search routes
│   │   └── deps.py           # Dependencies (auth)
│   ├── models/               # SQLModel database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── task.py
│   │   ├── task_share.py
│   │   ├── comment.py
│   │   └── activity.py
│   ├── schemas/              # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── task.py
│   │   ├── task_share.py
│   │   ├── comment.py
│   │   └── activity.py
│   ├── services/             # Business logic
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── task.py
│   │   ├── share.py
│   │   ├── comment.py
│   │   └── activity.py
│   ├── config.py             # Settings management
│   ├── database.py           # Database connection
│   └── main.py               # FastAPI application
├── tests/                    # Test files
│   ├── conftest.py           # Test fixtures
│   ├── test_auth.py
│   └── test_tasks.py
├── .env.example              # Environment template
├── alembic.ini               # Alembic configuration
├── pyproject.toml            # Project dependencies
└── README.md                 # This file
```

---

## Database Migrations

### Create New Migration
```bash
alembic revision --autogenerate -m "description of changes"
```

### Run Migrations
```bash
alembic upgrade head
```

### Rollback Last Migration
```bash
alembic downgrade -1
```

### View Migration History
```bash
alembic history
```

---

## API Documentation

When the server is running, interactive API docs are available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Troubleshooting

### Virtual Environment Not Activating (Windows PowerShell)
```powershell
# Run this first to allow scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then activate
.\.venv\Scripts\Activate.ps1
```

### Database Connection Errors
1. Verify `DATABASE_URL` in `.env` is correct
2. For SQLite: ensure the directory is writable
3. For PostgreSQL: check network connectivity and credentials

### Import Errors
```bash
# Make sure you installed in editable mode
pip install -e ".[dev]"
```

### Port Already in Use
```bash
# Use a different port
uvicorn src.main:app --reload --port 8001
```

---

## Development Workflow

1. **Activate virtual environment** before any work
2. **Run migrations** after pulling changes: `alembic upgrade head`
3. **Run tests** before committing: `pytest`
4. **Check code style**: `ruff check src/`
5. **Format code**: `ruff format src/`

---

## Production Deployment

```bash
# Install production dependencies only
pip install -e .

# Run with Gunicorn + Uvicorn workers
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

---

Built with FastAPI for the Hackathon II - Evolution of Todo
