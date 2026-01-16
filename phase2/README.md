# Phase II - Todo Full-Stack Web Application

Transform the Phase I console-based Todo application into a multi-user full-stack web application.

## Architecture

```
phase2/
├── backend/          # FastAPI + SQLModel + Neon PostgreSQL
│   ├── src/
│   │   ├── api/      # REST API endpoints
│   │   ├── models/   # SQLModel database models
│   │   ├── schemas/  # Pydantic request/response schemas
│   │   └── services/ # Business logic layer
│   ├── tests/        # pytest test suite
│   └── alembic/      # Database migrations
│
└── frontend/         # Next.js + TypeScript + Tailwind CSS
    ├── src/
    │   ├── app/      # Next.js App Router pages
    │   ├── components/ # React components
    │   ├── lib/      # Utilities and API client
    │   └── types/    # TypeScript type definitions
    └── tests/        # Jest test suite
```

## Tech Stack

### Backend
- **Python 3.13+** with FastAPI
- **SQLModel** ORM (SQLAlchemy + Pydantic)
- **Neon PostgreSQL** (serverless)
- **Better Auth** JWT verification
- **Alembic** for migrations

### Frontend
- **Next.js 15+** with App Router
- **React 19** with TypeScript
- **Tailwind CSS** for styling
- **shadcn/ui** components
- **Better Auth** client

## Quick Start

### Backend Setup

```bash
cd phase2/backend

# Create virtual environment
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e ".[dev]"

# Copy environment file and configure
cp .env.example .env
# Edit .env with your Neon database URL and Better Auth credentials

# Run migrations
alembic upgrade head

# Start development server
uvicorn src.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd phase2/frontend

# Install dependencies
npm install

# Copy environment file and configure
cp .env.example .env.local
# Edit .env.local with your API URL

# Start development server
npm run dev
```

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /api/auth/signup | Create account | No |
| POST | /api/auth/signin | Login | No |
| POST | /api/auth/signout | Logout | Yes |
| GET | /api/tasks | List tasks | Yes |
| POST | /api/tasks | Create task | Yes |
| GET | /api/tasks/{id} | Get task | Yes |
| PUT | /api/tasks/{id} | Update task | Yes |
| DELETE | /api/tasks/{id} | Delete task | Yes |
| PATCH | /api/tasks/{id}/complete | Toggle complete | Yes |

## Features

1. **User Authentication** - Signup, signin, signout with JWT
2. **Task CRUD** - Create, read, update, delete tasks
3. **Task Completion** - Toggle task status
4. **Filtering** - Filter by status (all/pending/completed)
5. **Sorting** - Sort by date or title

## Testing

### Backend Tests
```bash
cd phase2/backend
pytest --cov=src --cov-report=term-missing
```

### Frontend Tests
```bash
cd phase2/frontend
npm test
```

## Deployment

### Backend (Railway/Render)
- Set environment variables
- Start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel)
- Set root directory: `phase2/frontend`
- Set environment variables
- Auto-deploys on push

## Constitution Compliance

- Spec-Driven Development (SDD)
- AI-Native Architecture (Claude Code generated)
- Progressive Complexity (Phase I → Phase II)
- Cloud-Native First (stateless, JWT, serverless DB)
- Production Quality (70% test coverage)
