# Todo Backend API

Phase II Todo Full-Stack Web Application - FastAPI Backend

## Tech Stack

- **Framework**: FastAPI 0.115+
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL (Neon serverless)
- **Authentication**: JWT (python-jose)
- **Migrations**: Alembic

## Setup

### Prerequisites

- Python 3.13+
- PostgreSQL database (or Neon account)

### Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required variables:
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Secret key for JWT signing
- `JWT_ALGORITHM`: Algorithm for JWT (default: HS256)
- `JWT_EXPIRE_MINUTES`: Token expiration time (default: 60)

### Database Migrations

```bash
# Run migrations
alembic upgrade head
```

### Running the Server

```bash
# Development
uvicorn src.main:app --reload --port 8000

# Production
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Create new account |
| POST | `/api/auth/signin` | Login and get token |
| POST | `/api/auth/signout` | Logout (client-side) |
| GET | `/api/auth/me` | Get current user info |

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | List user's tasks |
| POST | `/api/tasks` | Create new task |
| GET | `/api/tasks/{id}` | Get task by ID |
| PUT | `/api/tasks/{id}` | Update task |
| DELETE | `/api/tasks/{id}` | Delete task |
| PATCH | `/api/tasks/{id}/complete` | Toggle completion |

### Query Parameters (GET /api/tasks)

- `status`: Filter by status (`all`, `pending`, `completed`)
- `sort`: Sort field (`created`, `title`)
- `order`: Sort order (`asc`, `desc`)

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check endpoint |

## Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_auth.py -v
```

## Project Structure

```
backend/
├── alembic/              # Database migrations
│   └── versions/
├── src/
│   ├── api/              # API endpoints
│   │   ├── auth.py
│   │   ├── tasks.py
│   │   └── deps.py       # Dependencies (auth)
│   ├── models/           # SQLModel models
│   │   ├── user.py
│   │   └── task.py
│   ├── schemas/          # Pydantic schemas
│   │   ├── user.py
│   │   └── task.py
│   ├── services/         # Business logic
│   │   ├── auth.py
│   │   └── task.py
│   ├── config.py         # Settings
│   ├── database.py       # DB connection
│   └── main.py           # FastAPI app
├── tests/
│   ├── conftest.py       # Test fixtures
│   ├── test_auth.py
│   └── test_tasks.py
├── pyproject.toml
└── .env.example
```

## API Documentation

When running, interactive API docs are available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
