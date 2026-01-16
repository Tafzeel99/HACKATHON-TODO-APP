# Research: Phase II - Todo Full-Stack Web Application

**Branch**: `phase2-full-stack`
**Date**: 2026-01-16
**Status**: Complete

## Overview

This document consolidates research findings for all technology decisions in Phase II. All technologies are per constitution requirements - research focuses on best practices and integration patterns.

---

## 1. Better Auth Integration

### Decision
Use Better Auth for authentication with JWT tokens shared between Next.js frontend and FastAPI backend.

### Rationale
- Constitution mandates Better Auth for Phase II
- Provides both client SDK (Next.js) and JWT verification (FastAPI)
- Handles password hashing, session management
- JWT format allows stateless backend verification

### Best Practices

**Frontend (Next.js)**:
```typescript
// lib/auth.ts
import { createAuthClient } from "better-auth/react"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
})
```

**Backend (FastAPI)**:
```python
# api/deps.py
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(credentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401)
        return user_id
    except JWTError:
        raise HTTPException(status_code=401)
```

### Alternatives Considered

| Alternative | Rejected Because |
|-------------|------------------|
| NextAuth.js | Constitution specifies Better Auth |
| Custom JWT | Better Auth handles security properly |
| Session cookies | Constitution requires stateless JWT |

---

## 2. SQLModel with Neon PostgreSQL

### Decision
Use SQLModel ORM with async support connecting to Neon Serverless PostgreSQL.

### Rationale
- Constitution mandates SQLModel and Neon PostgreSQL
- SQLModel combines SQLAlchemy power with Pydantic validation
- Neon provides serverless PostgreSQL with connection pooling
- Async support enables non-blocking database operations

### Best Practices

**Database Connection**:
```python
# database.py
from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

DATABASE_URL = os.getenv("DATABASE_URL")
# Convert postgres:// to postgresql+asyncpg:// for async
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://")

engine = create_async_engine(ASYNC_DATABASE_URL, echo=False, pool_pre_ping=True)

async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session
```

**Model Definition**:
```python
# models/task.py
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid

class Task(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Alternatives Considered

| Alternative | Rejected Because |
|-------------|------------------|
| Raw SQL | Constitution requires SQLModel ORM |
| Django ORM | FastAPI ecosystem, not Django |
| Prisma | Python ecosystem preference |

---

## 3. Next.js App Router with shadcn/ui

### Decision
Use Next.js 16+ App Router with shadcn/ui components and Tailwind CSS.

### Rationale
- Constitution mandates Next.js with App Router
- shadcn/ui provides accessible, customizable components
- Tailwind CSS enables rapid responsive styling
- App Router supports server components and route groups

### Best Practices

**Route Groups for Auth**:
```text
app/
├── (auth)/           # Public routes
│   ├── login/
│   └── signup/
└── (dashboard)/      # Protected routes
    ├── layout.tsx    # Auth check here
    └── tasks/
```

**Protected Layout**:
```typescript
// app/(dashboard)/layout.tsx
import { redirect } from "next/navigation"
import { getSession } from "@/lib/auth"

export default async function DashboardLayout({ children }) {
  const session = await getSession()
  if (!session) {
    redirect("/login")
  }
  return <div>{children}</div>
}
```

**API Client**:
```typescript
// lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL

export async function fetchTasks(token: string) {
  const response = await fetch(`${API_URL}/api/tasks`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
  if (!response.ok) throw new Error("Failed to fetch tasks")
  return response.json()
}
```

### Alternatives Considered

| Alternative | Rejected Because |
|-------------|------------------|
| Pages Router | App Router is current standard |
| Material UI | shadcn/ui preferred for customization |
| Chakra UI | Tailwind + shadcn/ui is lighter |

---

## 4. FastAPI REST API Design

### Decision
RESTful API under `/api/` with proper HTTP methods and status codes.

### Rationale
- Constitution mandates RESTful API with proper HTTP verbs
- FastAPI provides automatic OpenAPI documentation
- Dependency injection for auth and database
- Pydantic schemas for request/response validation

### Best Practices

**Router Organization**:
```python
# main.py
from fastapi import FastAPI
from api import auth, tasks

app = FastAPI(title="Todo API", version="2.0.0")
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
```

**Error Handling**:
```python
# api/tasks.py
from fastapi import HTTPException, status

@router.get("/{task_id}")
async def get_task(task_id: uuid.UUID, user_id: str = Depends(get_current_user)):
    task = await task_service.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return task
```

### Alternatives Considered

| Alternative | Rejected Because |
|-------------|------------------|
| GraphQL | Constitution specifies RESTful API |
| gRPC | Web frontend requires HTTP/REST |
| WebSocket | Not needed for Phase II CRUD |

---

## 5. Testing Strategy

### Decision
pytest for backend (70% coverage), Jest for frontend components.

### Rationale
- Constitution requires 70% coverage for Phase I-II
- pytest is standard for FastAPI testing
- Jest integrates with Next.js ecosystem

### Best Practices

**Backend Test Fixtures**:
```python
# tests/conftest.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def auth_headers():
    # Generate test JWT token
    token = create_test_token(user_id="test-user")
    return {"Authorization": f"Bearer {token}"}
```

**Test Example**:
```python
# tests/test_tasks.py
@pytest.mark.asyncio
async def test_create_task(client, auth_headers):
    response = await client.post(
        "/api/tasks",
        json={"title": "Test Task"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Task"
```

---

## 6. Environment Configuration

### Decision
All secrets via environment variables, validated at startup.

### Rationale
- Constitution prohibits hardcoded secrets
- Environment variables work across deployment platforms
- Pydantic Settings provides validation

### Best Practices

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    better_auth_secret: str
    better_auth_url: str
    cors_origins: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()
```

**Required Environment Variables**:

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Neon PostgreSQL connection string | `postgres://user:pass@host/db` |
| `BETTER_AUTH_SECRET` | JWT signing secret | `your-secret-key-min-32-chars` |
| `BETTER_AUTH_URL` | Better Auth server URL | `https://auth.example.com` |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:3000` |

---

## Summary

All technology decisions align with constitution requirements. No clarifications needed - research confirms best practices for mandated stack.

| Research Area | Decision | Status |
|---------------|----------|--------|
| Authentication | Better Auth + JWT | Confirmed |
| Database | SQLModel + Neon PostgreSQL | Confirmed |
| Frontend | Next.js App Router + shadcn/ui | Confirmed |
| Backend | FastAPI RESTful | Confirmed |
| Testing | pytest + Jest (70% coverage) | Confirmed |
| Configuration | Environment variables | Confirmed |
