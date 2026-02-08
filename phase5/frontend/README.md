# Todo Frontend - Phase 4

**Phase 4 Full-Stack Todo Application - Next.js Frontend**

> Unified frontend combining Phase 2 (Todo App) + Phase 3 (AI Chatbot)

---

## ✅ What's Included

- ✅ **Phase 2**: Task CRUD operations with Better Auth
- ✅ **Phase 3**: AI Chatbot with OpenAI ChatKit UI
- ✅ **Unified**: Single Next.js app serving both features
- ✅ **Configured**: All environment variables set up

---

## 🎯 Quick Start

**Prerequisites:**
- Node.js 18+
- Backend running at http://localhost:8000 (see `../backend/README.md`)

### One Command Startup:

```bash
cd phase4/frontend && npm install && npm run dev
```

### Or Step by Step:

```bash
# 1. Navigate to frontend
cd phase4/frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
```

---

## 🌐 Your Frontend Will Run At

- **App**: http://localhost:3000
- **Tasks**: http://localhost:3000/tasks
- **Chat**: http://localhost:3000/chat
- **Login**: http://localhost:3000/login
- **Signup**: http://localhost:3000/signup

---

## 🔧 Tech Stack

- **Framework**: Next.js 15+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui (Radix UI)
- **Forms**: React Hook Form + Zod
- **HTTP Client**: Fetch API
- **AI Chat**: OpenAI ChatKit

---

## 📁 Environment Variables

Your `.env` file is already configured with:

```bash
# Phase 2 Backend (Tasks API)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Phase 3 Backend (AI Chat API)
NEXT_PUBLIC_CHAT_API_URL=http://localhost:8001

# OpenAI ChatKit Domain Key
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=domain_pk_696ffdeaf57c8197a912387a3d6cfeec07db6318cdf03509

# Better Auth URL
NEXT_PUBLIC_BETTER_AUTH_URL=https://your-auth-server.com
```

**Note**: `.env.example` contains the template for these values.

---

## 📦 Building for Production

```bash
# Build the app
npm run build

# Start production server
npm start
```

Production server runs at: http://localhost:3000

---

## 📂 Project Structure

```
phase4/frontend/
├── src/
│   ├── app/                     # Next.js App Router
│   │   ├── (auth)/              # Auth routes (login, signup)
│   │   │   ├── login/
│   │   │   └── signup/
│   │   ├── (dashboard)/         # Protected routes
│   │   │   ├── layout.tsx       # Auth check wrapper
│   │   │   └── tasks/           # Task management (Phase 2)
│   │   ├── chat/                # AI Chatbot (Phase 3)
│   │   ├── layout.tsx           # Root layout
│   │   ├── page.tsx             # Landing page
│   │   └── globals.css          # Global styles
│   ├── components/
│   │   ├── auth/                # Authentication components
│   │   │   ├── login-form.tsx
│   │   │   └── signup-form.tsx
│   │   ├── tasks/               # Task components (Phase 2)
│   │   │   ├── task-filters.tsx
│   │   │   ├── task-form.tsx
│   │   │   ├── task-item.tsx
│   │   │   └── task-list.tsx
│   │   ├── chat/                # Chat components (Phase 3)
│   │   │   └── chatkit-wrapper.tsx
│   │   └── ui/                  # shadcn/ui components
│   ├── hooks/
│   │   └── use-toast.ts         # Toast notifications
│   ├── lib/
│   │   ├── api.ts               # REST API client (Phase 2)
│   │   ├── chat-api.ts          # Chat API client (Phase 3)
│   │   ├── auth.ts              # Auth utilities (JWT tokens)
│   │   └── utils.ts             # Utility functions
│   └── types/
│       ├── task.ts              # Task TypeScript types
│       ├── user.ts              # User TypeScript types
│       └── chat.ts              # Chat TypeScript types
├── package.json
├── tailwind.config.ts
├── tsconfig.json
├── .env                         # ✅ Configured
└── .env.example                 # Template
```

---

## ✨ Features

### **Phase 2 - Task Management**
- ✅ User authentication (signup, login, JWT)
- ✅ Create tasks with title and description
- ✅ View task list with loading states
- ✅ Edit tasks inline
- ✅ Delete tasks with confirmation
- ✅ Toggle task completion
- ✅ Filter by status (all/pending/completed)
- ✅ Sort by date or title
- ✅ Responsive UI with Tailwind CSS
- ✅ Loading skeletons and toast notifications

### **Phase 3 - AI Chatbot**
- ✅ OpenAI ChatKit integration
- ✅ Smart task suggestions
- ✅ Natural language task creation
- ✅ Context-aware responses
- ✅ MCP tools for task operations

### **UI/UX**
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Loading skeletons for better UX
- ✅ Toast notifications for feedback
- ✅ Form validation with Zod
- ✅ shadcn/ui components

---

## 📜 Available Scripts

```bash
npm run dev      # Start development server (http://localhost:3000)
npm run build    # Build for production
npm start        # Start production server
npm run lint     # Run ESLint
npm run type-check # TypeScript type checking
```

---

## 🔗 API Integration

### **Phase 2 - Tasks API** (`http://localhost:8000`)

**Auth Endpoints:**
- `POST /api/auth/signup` - User registration
- `POST /api/auth/signin` - User login
- `POST /api/auth/signout` - User logout
- `GET /api/auth/me` - Get current user

**Task Endpoints:**
- `GET /api/tasks` - List tasks (with filters)
- `POST /api/tasks` - Create task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `PATCH /api/tasks/{id}/complete` - Toggle completion

### **Phase 3 - Chat API** (`http://localhost:8001`)

**Chat Endpoints:**
- `POST /chat/send` - Send message to AI chatbot
- `GET /chat/history` - Get chat history
- `POST /chat/task-suggestions` - Get AI task suggestions

**MCP Tools Available:**
- `create_task` - Create task via natural language
- `list_tasks` - Get user's tasks
- `update_task` - Update existing task
- `delete_task` - Delete task
- `mark_complete` - Toggle task completion

---

## 🚀 Deployment

### **Vercel (Recommended)**

```bash
# Deploy to Vercel
vercel

# Or connect your GitHub repo to Vercel
# Auto-deploys on every push to main
```

**Environment Variables in Vercel:**
- Add all variables from `.env` to your Vercel project settings
- Update `NEXT_PUBLIC_API_URL` to your production backend URL
- Update `NEXT_PUBLIC_CHAT_API_URL` to your production chat backend URL

### **Production URLs**
- Frontend: `https://your-app.vercel.app`
- Backend (Phase 2): `https://your-backend.railway.app`
- Backend (Phase 3): `https://your-chat-backend.railway.app`

---

## 🧪 Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Generate coverage report
npm test -- --coverage
```

---

## 📚 Documentation

- [Next.js Docs](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com)
- [OpenAI ChatKit](https://platform.openai.com/docs/chatkit)
- [React Hook Form](https://react-hook-form.com)
- [Zod](https://zod.dev)

---

## 🐛 Troubleshooting

### **Backend not responding**
```bash
# Check if backend is running
curl http://localhost:8000/health
# Should return: {"status":"healthy","version":"v4.0.0"}
```

### **CORS errors**
- Ensure backend CORS is configured to allow `http://localhost:3000`
- Check `backend/.env` has `CORS_ORIGINS=http://localhost:3000`

### **ChatKit not loading**
- Verify `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` in `.env`
- Check domain is allowlisted at: https://platform.openai.com/settings/organization/security/domain-allowlist

### **Authentication issues**
- Clear browser localStorage: `localStorage.clear()`
- Check JWT token in Network tab
- Verify `BETTER_AUTH_SECRET` matches backend

---

## 📞 Support

- **Phase 4 Guide**: See `../README.md`
- **Backend Setup**: See `../backend/README.md`
- **Hackathon Brief**: See `../../specs/hackathon-brief.md`

---

**Version**: 4.0.0
**Last Updated**: February 6, 2026
**Status**: ✅ Ready for Phase 4 Deployment
