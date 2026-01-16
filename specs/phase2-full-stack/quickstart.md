# Quickstart: Phase II - Todo Full-Stack Web Application

**Branch**: `phase2-full-stack`
**Date**: 2026-01-16

## Prerequisites

- Python 3.13+
- Node.js 18+
- UV (Python package manager)
- Neon PostgreSQL account (free tier)
- Better Auth account (or self-hosted)

## Environment Setup

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd HACKATHON-TODO-APP
git checkout phase2-full-stack
```

### 2. Create Environment Files

**Backend** (`phase2/backend/.env`):
```env
# Database
DATABASE_URL=postgres://user:password@host.neon.tech/dbname?sslmode=require

# Better Auth
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters-long
BETTER_AUTH_URL=https://your-auth-server.com

# CORS
CORS_ORIGINS=http://localhost:3000

# Environment
ENVIRONMENT=development
```

**Frontend** (`phase2/frontend/.env.local`):
```env
# API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth
NEXT_PUBLIC_BETTER_AUTH_URL=https://your-auth-server.com
```

---

## Backend Setup

### 1. Install Dependencies

```bash
cd phase2/backend
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### 2. Run Database Migrations

```bash
alembic upgrade head
```

### 3. Start Development Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Verify Backend

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

---

## Frontend Setup

### 1. Install Dependencies

```bash
cd phase2/frontend
npm install
```

### 2. Install shadcn/ui Components

```bash
npx shadcn@latest init
npx shadcn@latest add button input card form toast
```

### 3. Start Development Server

```bash
npm run dev
```

### 4. Verify Frontend

- App: http://localhost:3000
- Login page: http://localhost:3000/login
- Signup page: http://localhost:3000/signup

---

## Running Tests

### Backend Tests

```bash
cd phase2/backend
pytest --cov=src --cov-report=term-missing
```

Expected coverage: 70% minimum

### Frontend Tests

```bash
cd phase2/frontend
npm test
```

---

## Development Workflow

### 1. Start Both Services

**Terminal 1 (Backend)**:
```bash
cd phase2/backend
source .venv/bin/activate
uvicorn src.main:app --reload
```

**Terminal 2 (Frontend)**:
```bash
cd phase2/frontend
npm run dev
```

### 2. Create Test User

Via API (curl):
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123","name":"Test User"}'
```

### 3. Get Auth Token

```bash
curl -X POST http://localhost:8000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword123"}'
```

### 4. Create Task

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{"title":"My First Task","description":"Testing the API"}'
```

---

## Project Structure

```
phase2/
├── backend/
│   ├── src/
│   │   ├── main.py           # FastAPI app
│   │   ├── config.py         # Settings
│   │   ├── database.py       # DB connection
│   │   ├── models/           # SQLModel models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── api/              # API routes
│   │   └── services/         # Business logic
│   ├── tests/
│   ├── alembic/              # Migrations
│   └── pyproject.toml
│
└── frontend/
    ├── src/
    │   ├── app/              # Next.js pages
    │   ├── components/       # React components
    │   ├── lib/              # Utilities
    │   └── types/            # TypeScript types
    ├── tests/
    └── package.json
```

---

## Common Issues

### CORS Errors

Ensure `CORS_ORIGINS` in backend `.env` includes your frontend URL:
```env
CORS_ORIGINS=http://localhost:3000
```

### Database Connection

Verify Neon connection string format:
```
postgres://user:password@host.neon.tech/dbname?sslmode=require
```

### Auth Token Expired

JWT tokens expire after 7 days. Re-authenticate via `/api/auth/signin`.

### Port Conflicts

Default ports:
- Backend: 8000
- Frontend: 3000

Change with:
```bash
# Backend
uvicorn src.main:app --port 8001

# Frontend
npm run dev -- -p 3001
```

---

## Deployment

### Backend (Railway/Render)

1. Connect GitHub repository
2. Set environment variables
3. Deploy from `phase2/backend` directory
4. Start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel)

1. Connect GitHub repository
2. Set root directory: `phase2/frontend`
3. Set environment variables
4. Deploy automatically on push

---

## Next Steps

1. Complete all 5 Basic Level features
2. Run tests and verify 70% coverage
3. Deploy to production
4. Submit Phase II for evaluation

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js App Router](https://nextjs.org/docs/app)
- [SQLModel](https://sqlmodel.tiangolo.com/)
- [Better Auth](https://better-auth.com/)
- [Neon PostgreSQL](https://neon.tech/docs)
- [shadcn/ui](https://ui.shadcn.com/)
