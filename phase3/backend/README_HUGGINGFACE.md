---
title: Todo AI Chatbot
emoji: 🤖
colorFrom: green
colorTo: blue
sdk: docker
pinned: false
license: mit
---

# Todo AI Chatbot - Phase 3

AI-powered chatbot for todo management using OpenAI Agents SDK, MCP Tools, and ChatKit.

## 🤖 Features

- **AI-Powered Chat**: Natural language task management
- **MCP Tools**: Modular Control Protocol for extensible functionality
- **Smart Suggestions**: AI suggests task priorities and due dates
- **Context-Aware**: Understands user preferences and patterns
- **ChatKit Integration**: Beautiful chat UI with streaming responses

## 🚀 Capabilities

### Task Management via Chat
- "Add a task to buy groceries tomorrow"
- "Show me all my high-priority tasks"
- "Mark the meeting task as complete"
- "What tasks are due this week?"

### Smart Features
- Natural language date parsing
- Priority inference from context
- Task categorization suggestions
- Reminder recommendations

## 📋 API Endpoints

### Health Check
- `GET /health` - Server health status

### Chat
- `POST /api/chat/message` - Send chat message
- `GET /api/chat/history` - Get chat history

### ChatKit
- `POST /chatkit` - ChatKit-compatible endpoint with SSE streaming

## 🔧 Environment Variables

Set these in the Hugging Face Space settings:

```bash
# Database (reuse from Phase 2)
DATABASE_URL=postgresql://user:password@host/dbname

# OpenRouter API (OpenAI-compatible)
OPEN_ROUTER_KEY=sk-or-v1-your-key-here
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=google/gemini-flash-1.5-8b

# Alternative Models:
# LLM_MODEL=anthropic/claude-3-haiku
# LLM_MODEL=meta-llama/llama-3.1-70b-instruct

# Auth (from Phase 2)
BETTER_AUTH_SECRET=your-jwt-secret-key
BETTER_AUTH_URL=https://your-frontend.vercel.app

# CORS
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000

# Environment
ENVIRONMENT=production

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60
```

## 📖 API Documentation

Once deployed, visit:
- Swagger UI: `https://your-space.hf.space/docs`
- ReDoc: `https://your-space.hf.space/redoc`

## 🛠️ Tech Stack

- **FastAPI** - Web framework
- **OpenAI Agents SDK** - AI agent orchestration
- **MCP (Model Context Protocol)** - Tool integration
- **ChatKit** - Chat UI protocol
- **OpenRouter** - Multi-model AI gateway
- **SQLModel** - Database ORM

## 🎯 MCP Tools

Built-in tools for the AI agent:

1. **create_task** - Create new tasks
2. **list_tasks** - Query and filter tasks
3. **update_task** - Modify task details
4. **delete_task** - Remove tasks
5. **search_tasks** - Semantic search
6. **get_task_suggestions** - AI-powered recommendations

## 📦 Deployment

This Space is automatically deployed when changes are pushed to the repository.

## 🔗 Related

- Frontend: https://your-frontend.vercel.app
- Phase 2 API: https://huggingface.co/spaces/your-username/todo-backend-api

## 💡 Example Usage

```python
import requests

# Chat with the AI
response = requests.post(
    "https://your-space.hf.space/api/chat/message",
    json={
        "message": "Add a task to finish the project report by Friday",
        "user_id": "user123"
    },
    headers={"Authorization": "Bearer your-jwt-token"}
)

print(response.json())
```
