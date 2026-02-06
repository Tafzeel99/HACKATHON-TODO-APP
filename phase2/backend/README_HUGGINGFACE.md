---
title: Todo Backend API
emoji: 📝
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# Todo Backend API - Phase 2

Full-stack Todo application REST API built with FastAPI, SQLModel, and Neon PostgreSQL.

## 🚀 Features

- **Authentication**: JWT-based auth with Better Auth integration
- **Tasks Management**: CRUD operations with advanced filtering
- **Projects**: Organize tasks into projects
- **Collaboration**: Task sharing, comments, and activity tracking
- **Real-time**: Background scheduler for reminders and notifications

## 📋 API Endpoints

### Health Check
- `GET /health` - Server health status

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user

### Tasks
- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{id}` - Get task details
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `PATCH /api/tasks/{id}/complete` - Toggle task completion

### Projects
- `GET /api/projects` - List projects
- `POST /api/projects` - Create project
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

### Collaboration
- `POST /api/tasks/{id}/share` - Share task
- `POST /api/tasks/{id}/comments` - Add comment
- `GET /api/activities` - Get activity feed

## 🔧 Environment Variables

Set these in the Hugging Face Space settings:

```bash
DATABASE_URL=postgresql://user:password@host/dbname
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters
BETTER_AUTH_URL=https://your-frontend.vercel.app
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
ENVIRONMENT=production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7
```

## 📖 API Documentation

Once deployed, visit:
- Swagger UI: `https://your-space.hf.space/docs`
- ReDoc: `https://your-space.hf.space/redoc`

## 🛠️ Tech Stack

- **FastAPI** - Modern Python web framework
- **SQLModel** - SQL databases with Python type hints
- **Neon PostgreSQL** - Serverless Postgres
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **Python-JOSE** - JWT authentication

## 📦 Deployment

This Space is automatically deployed when changes are pushed to the repository.

## 🔗 Related

- Frontend: https://your-frontend.vercel.app
- Phase 3 Chatbot: https://huggingface.co/spaces/your-username/todo-ai-chatbot
