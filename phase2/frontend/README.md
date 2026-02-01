# Todo Frontend

Phase II Todo Full-Stack Web Application - Next.js Frontend

## Tech Stack

- **Framework**: Next.js 15+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui (Radix UI)
- **Forms**: React Hook Form + Zod
- **HTTP Client**: Fetch API

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install
```

### Environment Variables

Copy `.env.example` to `.env.local` and configure:

```bash
cp .env.example .env.local
```

Required variables:
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)

### Running the Development Server

```bash
npm run dev
npm run dev -- -H 127.0.0.1

```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Building for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── (auth)/             # Auth routes (login, signup)
│   │   │   ├── login/
│   │   │   └── signup/
│   │   ├── (dashboard)/        # Protected routes
│   │   │   ├── layout.tsx      # Auth check wrapper
│   │   │   └── tasks/          # Task management
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Landing page
│   │   └── globals.css         # Global styles
│   ├── components/
│   │   ├── auth/               # Authentication components
│   │   │   ├── login-form.tsx
│   │   │   └── signup-form.tsx
│   │   ├── tasks/              # Task components
│   │   │   ├── task-filters.tsx
│   │   │   ├── task-form.tsx
│   │   │   ├── task-item.tsx
│   │   │   └── task-list.tsx
│   │   └── ui/                 # shadcn/ui components
│   ├── hooks/
│   │   └── use-toast.ts        # Toast notifications hook
│   ├── lib/
│   │   ├── api.ts              # API client
│   │   ├── auth.ts             # Auth utilities (token management)
│   │   └── utils.ts            # Utility functions
│   └── types/
│       ├── task.ts             # Task TypeScript types
│       └── user.ts             # User TypeScript types
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── .env.example
```

## Features

### Authentication
- User signup with email validation
- User login with JWT tokens
- Automatic token refresh
- Protected routes

### Task Management
- Create tasks with title and description
- View task list with loading states
- Edit task inline
- Delete tasks with confirmation
- Toggle task completion
- Filter by status (all/pending/completed)
- Sort by date or title

### UI/UX
- Responsive design
- Loading skeletons
- Toast notifications
- Form validation

## Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run ESLint
```

## API Integration

The frontend communicates with the backend API at `NEXT_PUBLIC_API_URL`. All authenticated requests include a JWT token in the Authorization header.

### Auth Endpoints Used
- `POST /api/auth/signup` - User registration
- `POST /api/auth/signin` - User login
- `POST /api/auth/signout` - User logout
- `GET /api/auth/me` - Get current user

### Task Endpoints Used
- `GET /api/tasks` - List tasks (with filters)
- `POST /api/tasks` - Create task
- `PUT /api/tasks/:id` - Update task
- `DELETE /api/tasks/:id` - Delete task
- `PATCH /api/tasks/:id/complete` - Toggle completion
