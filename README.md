# Hackathon II - The Evolution of Todo

A multi-phase hackathon project that evolves from a simple console application to an AI-powered, cloud-native task management solution.

![Phase Status](https://img.shields.io/badge/Phase%20I-Complete-success)
![Phase Status](https://img.shields.io/badge/Phase%20II-Complete-success)
![Phase Status](https://img.shields.io/badge/Phase%20III-Complete-success)
![Phase Status](https://img.shields.io/badge/Phase%20IV-Upcoming-yellow)
![Phase Status](https://img.shields.io/badge/Phase%20V-Upcoming-yellow)

## Table of Contents

- [Overview](#overview)
- [Architecture Evolution](#architecture-evolution)
- [Phase I - Console Application](#phase-i---console-application)
- [Phase II - Full-Stack Web Application](#phase-ii---full-stack-web-application)
- [Phase III - AI Chatbot](#phase-iii---ai-chatbot)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Contributing](#contributing)

---

## Overview

This project demonstrates the evolution of a todo application through multiple phases, each adding complexity and capabilities:

| Phase | Description | Stack | Status |
|-------|-------------|-------|--------|
| **Phase I** | In-memory console app | Python | ✅ Complete |
| **Phase II** | Full-stack web application | Next.js + FastAPI + Neon PostgreSQL | ✅ Complete |
| **Phase III** | AI-powered chatbot | OpenRouter LLM + MCP Tools | ✅ Complete |
| **Phase IV** | Containerized deployment | Docker + Minikube + Helm | ⏳ Upcoming |
| **Phase V** | Cloud-native event-driven | AKS/GKE + Kafka + Dapr | ⏳ Upcoming |

---

## Architecture Evolution

```
Phase I (Console)          Phase II (Web)              Phase III (AI)
┌─────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│  Python CLI     │    │  Next.js Frontend   │    │  AI Chat Interface  │
│  In-Memory Data │ →  │  FastAPI Backend    │ →  │  MCP Tools Server   │
│                 │    │  Neon PostgreSQL    │    │  Smart Suggestions  │
│                 │    │  Better Auth        │    │  Natural Language   │
└─────────────────┘    └─────────────────────┘    └─────────────────────┘
```

---

## Phase I - Console Application

A simple, in-memory Python console application for managing todo tasks.

### Features

| Feature | Description |
|---------|-------------|
| **Add Task** | Create new todo items with title and optional description |
| **View Tasks** | Display all tasks with status, priority, and timestamps |
| **Update Task** | Modify existing task details |
| **Delete Task** | Remove tasks from the list |
| **Mark Complete** | Toggle task completion status |

### How to Run

```bash
cd phase1
python -m src.main
```

---

## Phase II - Full-Stack Web Application

A modern, responsive web application with rich features for task management.

### Core Features

#### Task Management
| Feature | Description |
|---------|-------------|
| **CRUD Operations** | Create, read, update, delete tasks |
| **Priority Levels** | Low, Medium, High, Urgent with color coding |
| **Due Dates** | Set deadlines with overdue highlighting |
| **Task Status** | Pending, In Progress, Completed states |
| **Completion Celebration** | Confetti animation on task completion |
| **Bulk Actions** | Select and manage multiple tasks |

#### Views & Organization
| Feature | Description |
|---------|-------------|
| **List View** | Traditional task list with sorting |
| **Kanban Board** | Drag-and-drop columns by status |
| **Calendar View** | Tasks organized by due date |
| **Archive** | Soft delete with restore capability |
| **Search & Filter** | Find tasks by title, priority, status |

#### Projects & Categories
| Feature | Description |
|---------|-------------|
| **Projects** | Group tasks into projects |
| **Color Coding** | Custom colors for tasks and projects |
| **Task Position** | Drag to reorder tasks |

#### Collaboration Features
| Feature | Description |
|---------|-------------|
| **Task Sharing** | Share tasks with other users |
| **Comments** | Add comments to tasks |
| **Activity Feed** | Track all changes and updates |
| **User Mentions** | @mention users in comments |
| **Assignees** | Assign tasks to team members |

#### User Experience
| Feature | Description |
|---------|-------------|
| **Responsive Design** | Mobile-first, works on all devices |
| **Dark/Light Mode** | Theme toggle with system preference |
| **Skeleton Loading** | Smooth loading states |
| **Toast Notifications** | Success/error feedback |
| **Keyboard Shortcuts** | Quick actions via keyboard |
| **Pull to Refresh** | Mobile gesture support |
| **Swipe Actions** | Swipe to complete/delete on mobile |

#### Dashboard & Analytics
| Feature | Description |
|---------|-------------|
| **Dashboard** | Overview with stats and quick actions |
| **Analytics** | Task completion trends and insights |
| **Progress Ring** | Visual completion percentage |
| **Motivational Quotes** | Daily inspiration widget |

#### Email Reminders
| Feature | Description |
|---------|-------------|
| **Task Reminders** | Email notifications before due dates |
| **Overdue Alerts** | Notifications for overdue tasks |
| **Daily Digest** | Summary of upcoming tasks |
| **SendGrid Integration** | Reliable email delivery |

#### Authentication & Security
| Feature | Description |
|---------|-------------|
| **Better Auth** | Secure JWT authentication |
| **User Registration** | Email/password signup |
| **Protected Routes** | Secure API endpoints |
| **User Isolation** | Data segregated by user |

### How to Run

```bash
# Terminal 1: Backend
cd phase2/backend
pip install -e .
uvicorn src.main:app --reload --port 8000

# Terminal 2: Frontend
cd phase2/frontend
npm install
npm run dev
```

Access the app at: http://localhost:3000

### Environment Variables

**phase2/backend/.env:**
```env
DATABASE_URL=postgresql://user:pass@host/db
BETTER_AUTH_SECRET=your_secret_key
CORS_ORIGINS=["http://localhost:3000"]
SENDGRID_API_KEY=your_sendgrid_key  # Optional for email reminders
```

**phase2/frontend/.env.local:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
```

---

## Phase III - AI Chatbot

An AI-powered chatbot for managing todos through natural language conversation.

### AI Features

#### Natural Language Processing
| Feature | Description |
|---------|-------------|
| **Conversational Interface** | Chat naturally to manage tasks |
| **Intent Recognition** | Understands add, update, delete, complete intents |
| **Date Parsing** | "tomorrow", "next week", "in 3 days" support |
| **Context Awareness** | Remembers conversation context |

#### MCP Tools (10 Tools)
| Tool | Description |
|------|-------------|
| `add_task` | Create new tasks with title, description, due date, priority |
| `list_tasks` | View tasks with optional filters |
| `update_task` | Modify task details |
| `delete_task` | Remove tasks |
| `complete_task` | Mark tasks as done |
| `assign_task` | Assign tasks to users |
| `share_task` | Share tasks with others |
| `add_comment` | Add comments to tasks |
| `get_analytics` | Get task statistics |
| `get_suggestions` | Get AI-powered suggestions |

#### Smart Suggestions
| Feature | Description |
|---------|-------------|
| **Time Estimation** | Learn from past task durations |
| **Conflict Detection** | Identify scheduling overlaps |
| **Workload Analysis** | Balance task distribution |
| **Habit Tracking** | Track completion patterns |
| **Priority Suggestions** | Recommend task priorities |
| **Auto-Categorization** | Suggest categories based on content |

### Example Conversations

```
User: Add a task to review the project proposal by Friday
AI: ✅ Created task "Review the project proposal"
    Due: Friday, January 31st
    Priority: Medium

User: Show my high priority tasks
AI: Here are your high priority tasks:
    1. Complete quarterly report - Due tomorrow
    2. Client presentation prep - Due Jan 30
    3. Review budget allocation - Due Feb 1

User: Mark the quarterly report as complete
AI: ✅ Great job! "Complete quarterly report" is now complete!
    You've completed 5 tasks this week!

User: What should I work on next?
AI: Based on your workload, I suggest:
    📌 "Client presentation prep" - Due soon, high priority
    💡 You have 3 hours free this afternoon
    ⚠️ "Review budget" conflicts with your meeting at 2pm
```

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Phase 2 Frontend                        │
│              (Next.js + ChatKit UI)                      │
│                    /chat route                           │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP + JWT
                      ▼
┌─────────────────────────────────────────────────────────┐
│                  Phase 3 Backend                         │
│                    (FastAPI)                             │
│  ┌─────────────────────────────────────────────────┐    │
│  │           ChatKit Server (SSE)                   │    │
│  └─────────────────────┬───────────────────────────┘    │
│                        ▼                                 │
│  ┌─────────────────────────────────────────────────┐    │
│  │         Agent Service (OpenRouter LLM)           │    │
│  │              gpt-4o-mini                          │    │
│  └─────────────────────┬───────────────────────────┘    │
│                        ▼                                 │
│  ┌─────────────────────────────────────────────────┐    │
│  │            MCP Server (10 Tools)                 │    │
│  └─────────────────────┬───────────────────────────┘    │
│                        ▼                                 │
│  ┌─────────────────────────────────────────────────┐    │
│  │     Smart Suggestions Service                    │    │
│  │   • Time Estimation    • Conflict Detection      │    │
│  │   • Workload Analysis  • Habit Tracking          │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Neon PostgreSQL                             │
│           (Shared with Phase 2)                          │
└─────────────────────────────────────────────────────────┘
```

### How to Run

```bash
# Terminal 1: Phase 2 Backend (port 8000)
cd phase2/backend
pip install -e .
uvicorn src.main:app --reload --port 8000

# Terminal 2: Phase 3 AI Backend (port 8001)
cd phase3/backend
pip install -e .
uvicorn src.main:app --reload --port 8001

# Terminal 3: Frontend
cd phase2/frontend
npm run dev
```

Access the chat at: http://localhost:3000/chat

### Environment Variables

**phase3/backend/.env:**
```env
DATABASE_URL=postgresql://user:pass@host/db
OPEN_ROUTER_KEY=your_openrouter_api_key
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=openai/gpt-4o-mini
BETTER_AUTH_SECRET=your_secret_key
CORS_ORIGINS=["http://localhost:3000"]
```

---

## Quick Start

### Prerequisites

- Python 3.13+
- Node.js 18+
- PostgreSQL / Neon account
- OpenRouter API key (for AI features)

### Installation

```bash
# Clone the repository
git clone https://github.com/Tafzeel99/HACKATHON-TODO-APP.git
cd HACKATHON-TODO-APP

# Setup Phase 2 Backend
cd phase2/backend
pip install -e .
cp .env.example .env
# Edit .env with your database URL and secrets

# Setup Phase 2 Frontend
cd ../frontend
npm install
cp .env.example .env.local
# Edit .env.local with API URLs

# Setup Phase 3 Backend (AI)
cd ../../phase3/backend
pip install -e .
cp .env.example .env
# Edit .env with OpenRouter API key
```

### Running All Services

```bash
# Terminal 1: Phase 2 Backend
cd phase2/backend && uvicorn src.main:app --reload --port 8000

# Terminal 2: Phase 3 AI Backend
cd phase3/backend && uvicorn src.main:app --reload --port 8001

# Terminal 3: Frontend
cd phase2/frontend && npm run dev
```

---

## Project Structure

```
HACKATHON-TODO-APP/
├── phase1/                     # Console Application
│   └── src/
│       └── main.py
│
├── phase2/                     # Full-Stack Web Application
│   ├── backend/
│   │   ├── src/
│   │   │   ├── api/           # REST API endpoints
│   │   │   ├── models/        # SQLModel database models
│   │   │   ├── schemas/       # Pydantic schemas
│   │   │   ├── services/      # Business logic
│   │   │   └── templates/     # Email templates
│   │   └── alembic/           # Database migrations
│   │
│   └── frontend/
│       └── src/
│           ├── app/           # Next.js App Router pages
│           ├── components/    # React components
│           │   ├── chat/      # AI chat interface
│           │   ├── tasks/     # Task management
│           │   ├── projects/  # Project management
│           │   ├── collaboration/  # Sharing & comments
│           │   └── ui/        # Shadcn UI components
│           ├── hooks/         # Custom React hooks
│           └── types/         # TypeScript types
│
├── phase3/                     # AI Chatbot Backend
│   └── backend/
│       └── src/
│           ├── api/           # Chat API endpoints
│           ├── mcp/           # MCP tools server
│           │   └── tools/     # 10 MCP tools
│           ├── services/      # AI services
│           │   ├── agent_service.py      # LLM integration
│           │   ├── suggestions.py        # Smart suggestions
│           │   ├── auto_categorizer.py   # Auto-categorization
│           │   └── context_manager.py    # Conversation context
│           └── models/        # Chat models
│
├── specs/                      # Specifications (SDD)
│   ├── phase1/
│   ├── phase2/
│   ├── phase3/
│   └── 001-ai-agent-enhancements/
│
├── history/                    # Documentation
│   ├── adr/                   # Architecture Decision Records
│   └── prompts/               # Prompt History Records
│
├── CLAUDE.md                   # AI assistant instructions
└── README.md                   # This file
```

---

## Tech Stack

### Backend
- **Python 3.13+** - Core language
- **FastAPI** - High-performance web framework
- **SQLModel** - SQL database ORM with Pydantic
- **Alembic** - Database migrations
- **Better Auth** - JWT authentication
- **APScheduler** - Background task scheduling
- **SendGrid** - Email service
- **OpenRouter** - LLM API (OpenAI-compatible)

### Frontend
- **Next.js 16+** - React framework with App Router
- **React 18+** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **Shadcn/ui** - Component library
- **Canvas Confetti** - Celebration animations

### Database
- **Neon PostgreSQL** - Serverless PostgreSQL
- **SQLite** - Local development option

### AI/ML
- **OpenRouter API** - Multi-model LLM access
- **GPT-4o-mini** - Primary model for chat
- **MCP Protocol** - Tool calling standard

---

## API Documentation

When the backend is running, access the interactive API docs:

- **Phase 2 Backend**: http://localhost:8000/docs
- **Phase 3 AI Backend**: http://localhost:8001/docs

---

## Contributing

This project follows **Spec-Driven Development (SDD)** principles:

1. All features start with specifications in `/specs`
2. Plans are created from specifications
3. Tasks are broken down from plans
4. Implementation follows tasks exactly

See [CLAUDE.md](./CLAUDE.md) for detailed development guidelines.

---

## License

MIT License - See LICENSE file for details.

---

## Acknowledgments

- Built as part of Hackathon II - The Evolution of Todo
- Follows AI-Native Development principles
- Powered by Claude Code and Spec-Driven Development

---

**Built with AI-Native Development principles using Claude Code**
