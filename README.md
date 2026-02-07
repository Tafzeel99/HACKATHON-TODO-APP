# Hackathon II - The Evolution of Todo

A multi-phase hackathon project that evolves from a simple console application to an AI-powered, cloud-native task management solution.

![Phase Status](https://img.shields.io/badge/Phase%20I-Complete-success)
![Phase Status](https://img.shields.io/badge/Phase%20II-Complete-success)
![Phase Status](https://img.shields.io/badge/Phase%20III-Complete-success)
![Phase Status](https://img.shields.io/badge/Phase%20IV-Complete-success)
![Phase Status](https://img.shields.io/badge/Phase%20V-Upcoming-yellow)

## 🚀 Live Demo

- **Frontend**: [https://hackathon-todox.vercel.app](https://hackathon-todox.vercel.app)
- **Phase 2 API**: [https://tafzeel99-todo-app-phase2.hf.space/docs](https://tafzeel99-todo-app-phase2.hf.space/docs)
- **Phase 3 AI Chatbot**: [https://tafzeel99-todo-app-phase3.hf.space/docs](https://tafzeel99-todo-app-phase3.hf.space/docs)

**Try it now!** → Sign up and start managing your tasks with AI assistance.

## Table of Contents

- [Live Demo](#-live-demo)
- [Overview](#overview)
- [Architecture Evolution](#architecture-evolution)
- [Phase I - Console Application](#phase-i---console-application)
- [Phase II - Full-Stack Web Application](#phase-ii---full-stack-web-application)
- [Phase III - AI Chatbot](#phase-iii---ai-chatbot)
- [Phase IV - Kubernetes Deployment](#phase-iv---kubernetes-deployment)
- [Production Deployment](#-production-deployment)
- [Tech Stack](#tech-stack)
- [API Documentation](#api-documentation)

---

## Overview

This project demonstrates the evolution of a todo application through multiple phases, each adding complexity and capabilities:

| Phase | Description | Stack | Status |
|-------|-------------|-------|--------|
| **Phase I** | In-memory console app | Python | ✅ Complete |
| **Phase II** | Full-stack web application | Next.js + FastAPI + Neon PostgreSQL | ✅ Complete |
| **Phase III** | AI-powered chatbot | OpenRouter LLM + MCP Tools | ✅ Complete |
| **Phase IV** | Containerized deployment | Docker + Minikube + Helm | ✅ Complete |
| **Phase V** | Cloud-native event-driven | AKS/GKE + Kafka + Dapr | ⏳ Upcoming |

---

## Architecture Evolution

```
Phase I (Console)          Phase II (Web)              Phase III (AI)              Phase IV (K8s)
┌─────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│  Python CLI     │    │  Next.js Frontend   │    │  AI Chat Interface  │    │  Docker Containers  │
│  In-Memory Data │ →  │  FastAPI Backend    │ →  │  MCP Tools Server   │ →  │  Minikube/K8s       │
│                 │    │  Neon PostgreSQL    │    │  Smart Suggestions  │    │  Helm Charts        │
│                 │    │  Better Auth        │    │  Natural Language   │    │  NodePort Services  │
└─────────────────┘    └─────────────────────┘    └─────────────────────┘    └─────────────────────┘
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


### Architecture

```
┌──────────────────────────────────────────────────────────┐
│              Vercel (Frontend Deployment)                 │
│           https://hackathon-todox.vercel.app              │
│              Next.js 16 + ChatKit UI                      │
│                    /chat route                            │
└────────────────────┬──────────────────┬──────────────────┘
                     │                  │
            JWT Auth │                  │ API Calls
                     ▼                  ▼
┌──────────────────────────┐  ┌────────────────────────────┐
│  Hugging Face Space      │  │  Hugging Face Space        │
│  Phase 2 Backend         │  │  Phase 3 AI Chatbot        │
│  (REST API)              │  │  (ChatKit + MCP)           │
│  Port 7860               │  │  Port 7860                 │
│  ┌────────────────────┐  │  │  ┌──────────────────────┐  │
│  │ FastAPI            │  │  │  │ ChatKit Server (SSE) │  │
│  │ Better Auth JWT    │  │  │  └──────────┬───────────┘  │
│  │ Task CRUD          │  │  │             ▼              │
│  │ Projects           │  │  │  ┌──────────────────────┐  │
│  │ Collaboration      │  │  │  │ Agent Service        │  │
│  │ Email Reminders    │  │  │  │ OpenRouter LLM       │  │
│  └────────────────────┘  │  │  │ Gemini 2.0 Flash     │  │
└────────────┬─────────────┘  │  └──────────┬───────────┘  │
             │                │             ▼              │
             │                │  ┌──────────────────────┐  │
             │                │  │ MCP Server (10 Tools)│  │
             │                │  │ • add_task           │  │
             │                │  │ • list_tasks         │  │
             │                │  │ • complete_task      │  │
             │                │  │ • delete_task        │  │
             │                │  │ • update_task        │  │
             │                │  │ • assign_task        │  │
             │                │  │ • share_task         │  │
             │                │  │ • add_comment        │  │
             │                │  │ • get_analytics      │  │
             │                │  │ • get_suggestions    │  │
             │                │  └──────────────────────┘  │
             └────────────────┴───────────┬────────────────┘
                                          │
                                          ▼
             ┌──────────────────────────────────────────────┐
             │         Neon PostgreSQL (Serverless)         │
             │              Shared Database                 │
             │         us-east-2.aws.neon.tech              │
             └──────────────────────────────────────────────┘
```


---

## Phase IV - Kubernetes Deployment

Production-ready containerized deployment using Docker, Kubernetes, and Helm.

### Containerization Features

#### Docker Images
| Component | Description |
|-----------|-------------|
| **Backend Image** | Multi-stage Python 3.13 build with UV package manager |
| **Frontend Image** | Multi-stage Node.js build with Next.js standalone output |
| **Optimized Size** | Backend: 339MB, Frontend: 410MB |
| **Security** | Non-root users, minimal attack surface |
| **Health Checks** | Liveness and readiness probes configured |

#### Kubernetes Resources
| Resource | Description |
|----------|-------------|
| **Deployments** | Backend and frontend deployments with replica management |
| **Services** | NodePort services for external access |
| **ConfigMaps** | Environment configuration for both services |
| **Secrets** | Secure storage for API keys and sensitive data |
| **Health Probes** | HTTP-based health checks with configurable delays |


### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      Kubernetes Cluster                       │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              Helm Chart: todo-app v4.0.0               │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌─────────────────────────┐  ┌──────────────────────────┐  │
│  │  Frontend Deployment    │  │  Backend Deployment      │  │
│  │  ┌──────────────────┐   │  │  ┌───────────────────┐  │  │
│  │  │ todo-frontend    │   │  │  │ todo-backend      │  │  │
│  │  │ :4.0.0           │   │  │  │ :4.0.0            │  │  │
│  │  │ Port: 3000       │   │  │  │ Port: 8000        │  │  │
│  │  └──────────────────┘   │  │  └───────────────────┘  │  │
│  └─────────┬───────────────┘  └──────────┬───────────────┘  │
│            │                              │                   │
│  ┌─────────▼───────────────┐  ┌──────────▼───────────────┐  │
│  │  frontend-service       │  │  backend-service         │  │
│  │  NodePort: 30030        │  │  NodePort: 30080         │  │
│  └─────────────────────────┘  └──────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                       │
                       ▼
              Port Forwarding (127.0.0.1)
              - Frontend: :3000
              - Backend: :8000
```


## 🌐 Production Deployment

The application is deployed and running on cloud platforms:

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Vercel (Frontend)                     │
│              https://hackathon-todox.vercel.app          │
│                     Next.js 16 + React                   │
└─────────────────┬────────────────────┬──────────────────┘
                  │                    │
         JWT Auth │                    │ API Calls
                  │                    │
    ┌─────────────▼──────────┐  ┌─────▼──────────────────┐
    │  Hugging Face Space    │  │  Hugging Face Space    │
    │   Phase 2 Backend      │  │   Phase 3 AI Chatbot   │
    │   (REST API)           │  │   (ChatKit + MCP)      │
    │   Port: 7860           │  │   Port: 7860           │
    └────────────┬───────────┘  └────────┬───────────────┘
                 │                       │
                 └───────────┬───────────┘
                             │
                    ┌────────▼─────────┐
                    │ Neon PostgreSQL  │
                    │  (Serverless)    │
                    └──────────────────┘
```

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
- **OpenRouter API** - Multi-model LLM gateway with 18+ free models
- **Google Gemini 2.0 Flash** - Primary model for chat (1M tokens context, free)
- **Alternative Free Models**:
  - Meta Llama 3.3 70B (GPT-4 level performance)
  - DeepSeek V3 (strong reasoning)
  - Mistral Small 3.1 24B
- **MCP Protocol** - Model Context Protocol for tool calling
- **ChatKit** - OpenAI ChatKit for beautiful chat UI

### Container & Orchestration
- **Docker** - Container runtime
- **Docker Compose** - Multi-container orchestration
- **Kubernetes** - Container orchestration platform
- **Minikube** - Local Kubernetes cluster
- **Helm** - Kubernetes package manager
- **kubectl** - Kubernetes CLI

---

## API Documentation

When the backend is running, access the interactive API docs:

- **Local Development**: http://localhost:8000/docs
- **Docker Containers**: http://127.0.0.1:8000/docs
- **Kubernetes (NodePort)**: http://<MINIKUBE-IP>:30080/docs
- **Kubernetes (Port Forward)**: http://127.0.0.1:8000/docs

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

