---
name: architecture-planner
description: |
  Design system architecture with component breakdown, data flow, technology choices, and scalability considerations.
---

# Architecture Planner

Design system architecture with component breakdown, data flow, technology choices, and scalability considerations.

## When to Use This Skill
- Starting a new project or major feature
- User mentions "system design" or "architecture"
- Need to choose tech stack or patterns
- Planning for scale or performance requirements

## Procedure
1. **Gather requirements**: Scale, performance, team size, constraints
2. **Design high-level architecture**: Services, layers, boundaries
3. **Break down components**: Modules, responsibilities, interfaces
4. **Map data flow**: How information moves through system
5. **Document decisions**: Trade-offs and rationale

## Output Format
**Architecture Document**:
- System overview diagram
- Component breakdown with responsibilities
- Data flow and state management
- Technology choices with rationale
- Scalability and performance considerations
- Deployment architecture

## Quality Criteria
- Clear separation of concerns
- Scalable to projected growth
- Technology choices justified with trade-offs
- Data flow documented end-to-end
- Component responsibilities well-defined
- Future extensibility considered

## Example
**Input**: "Design architecture for collaborative task management app like Todoist"

**Output**:

# Architecture: Collaborative Task Management

## System Overview
**Problem**: Teams need real-time task management with collaboration features.
**Goal**: Support 10k concurrent users with sub-second response times.

**Architecture Style**: Micro-frontend with monolithic backend initially, planned migration to services.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   WebSocket     │    │   Database      │
│   (React)       │◄──►│   (Socket.io)   │◄──►│   (PostgreSQL)  │
│                 │    │                 │    │                 │
│   Cache         │    │   API Server    │    │   Cache         │
│   (In-memory)   │    │   (Node.js)     │    │   (Redis)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Component Breakdown

### Frontend Components (`src/`)

**Responsibility**: UI rendering, real-time updates, local state management

```
src/
├── tasks/
│   ├── TaskList.tsx          # List view with virtualization
│   ├── TaskItem.tsx          # Single task display
│   ├── TaskForm.tsx          # Create/edit form
│   └── TaskFilters.tsx       # Filter sidebar
├── projects/
│   ├── ProjectBoard.tsx      # Kanban board view
│   ├── ProjectList.tsx       # Project overview
│   └── ProjectSettings.tsx   # Project configuration
├── collaboration/
│   ├── UserPresence.tsx      # Who's online indicator
│   ├── CollaboratorList.tsx  # Team members
│   └── ActivityFeed.tsx      # Recent changes
└── shared/
    ├── Avatar.tsx
    ├── Button.tsx
    └── Modal.tsx
```

**Key Decisions**:
- Use `shadcn/ui` for base components (customizable, not opinionated)
- Virtualized lists for 1000+ tasks (react-window)
- Optimistic updates with rollback on error

#### 2. State Management (`src/store/`)
**Responsibility**: Client-side state, cache, real-time sync

```typescript
// Zustand stores
stores/
├── authStore.ts          # Current user, session
├── taskStore.ts          # Task CRUD operations
├── projectStore.ts       # Project data
├── presenceStore.ts      # Who's viewing what
└── uiStore.ts            # UI state (modals, sidebar)

// React Query for server state
queries/
├── useTasks.ts           # Task data fetching
├── useProjects.ts        # Project queries
└── useActivity.ts        # Activity feed
```

**Key Decisions**:
- Zustand for local UI state (lightweight, TypeScript-first)
- React Query for server state (caching, invalidation)
- Separate stores = easier testing, clearer boundaries

#### 3. Real-time Client (`src/realtime/`)
**Responsibility**: WebSocket connection, event handling

```typescript
// Real-time event handlers
realtime/
├── socket.ts             # Socket.io client setup
├── taskSync.ts           # Task update events
├── presenceSync.ts       # User presence updates
└── conflictResolver.ts   # Handle concurrent edits
```

**Event Flow**:
```
User edits task
  → Optimistic update (UI shows change immediately)
  → Emit 'task:update' to server
  → Server broadcasts to room
  → Other clients receive update
  → Merge changes (CRDT-like)
```

### Backend Components

#### 4. API Layer (`src/server/api/`)
**Responsibility**: Request handling, validation, authorization

```typescript
api/
├── routers/
│   ├── tasks.ts          # Task CRUD endpoints
│   ├── projects.ts       # Project management
│   ├── users.ts          # User profile
│   └── activity.ts       # Activity logs
├── middleware/
│   ├── auth.ts           # JWT validation
│   ├── rateLimit.ts      # Rate limiting
│   └── logger.ts         # Request logging
└── trpc.ts               # tRPC router setup
```

**tRPC Procedure Example**:
```typescript
// tasks.ts
export const tasksRouter = router({
  create: protectedProcedure
    .input(z.object({
      title: z.string().min(1).max(200),
      project_id: z.string().uuid(),
      assignee_id: z.string().uuid().optional()
    }))
    .mutation(async ({ ctx, input }) => {
      const task = await ctx.prisma.task.create({
        data: {
          ...input,
          created_by: ctx.user.id
        }
      });

      // Notify real-time clients
      ctx.io.to(`project:${input.project_id}`).emit('task:created', task);

      return task;
    }),

  update: protectedProcedure
    .input(z.object({
      id: z.string().uuid(),
      data: taskUpdateSchema
    }))
    .mutation(async ({ ctx, input }) => {
      // Optimistic locking
      const current = await ctx.prisma.task.findUnique({
        where: { id: input.id }
      });

      if (current.version !== input.version) {
        throw new TRPCError({
          code: 'CONFLICT',
          message: 'Task was modified by another user'
        });
      }

      const updated = await ctx.prisma.task.update({
        where: { id: input.id },
        data: {
          ...input.data,
          version: { increment: 1 }
        }
      });

      ctx.io.to(`task:${input.id}`).emit('task:updated', updated);

      return updated;
    })
});
```

#### 5. Business Logic (`src/server/services/`)
**Responsibility**: Core business rules, complex operations

```typescript
services/
├── TaskService.ts        # Task business logic
├── ProjectService.ts     # Project operations
├── NotificationService.ts # Notification dispatch
└── SyncService.ts        # Conflict resolution
```

**Service Pattern**:
```typescript
// TaskService.ts
export class TaskService {
  constructor(
    private prisma: PrismaClient,
    private cache: RedisClient
  ) {}

  async assignTask(taskId: string, userId: string) {
    // Business rule: Check user has permission
    await this.checkPermission(taskId, userId);

    // Update task
    const task = await this.prisma.task.update({
      where: { id: taskId },
      data: { assignee_id: userId }
    });

    // Invalidate cache
    await this.cache.del(`task:${taskId}`);

    // Send notification
    await this.notificationService.notify(userId, {
      type: 'TASK_ASSIGNED',
      task_id: taskId
    });

    return task;
  }
}
```

#### 6. Real-time Sync (`src/server/realtime/`)
**Responsibility**: WebSocket server, room management, presence

```typescript
realtime/
├── socketServer.ts       # Socket.io setup
├── roomManager.ts        # Join/leave rooms
├── presenceTracker.ts    # Who's online
└── eventHandlers/
    ├── taskEvents.ts
    └── presenceEvents.ts
```

**Room Structure**:
```typescript
// Users join rooms based on what they're viewing
Rooms:
- `user:{userId}`        → Personal notifications
- `project:{projectId}`  → Project updates
- `task:{taskId}`        → Task-specific edits
```

**Presence Tracking**:
```typescript
// When user opens a task
socket.on('task:view', async ({ taskId }) => {
  await socket.join(`task:${taskId}`);

  // Track in Redis (expires in 30s)
  await redis.sadd(`presence:task:${taskId}`, userId);
  await redis.expire(`presence:task:${taskId}`, 30);

  // Broadcast to room
  io.to(`task:${taskId}`).emit('presence:join', {
    user_id: userId,
    user_name: user.name
  });
});

// Heartbeat every 15s to keep presence alive
socket.on('presence:heartbeat', async ({ taskId }) => {
  await redis.expire(`presence:task:${taskId}`, 30);
});
```

## Data Flow

### Read Flow (Task List)
```
1. User opens project page
   ↓
2. React Query checks cache
   ↓
3. If stale, fetch via tRPC
   ↓
4. Server checks Redis cache
   ↓
5. If miss, query PostgreSQL
   ↓
6. Store in Redis (TTL 5 min)
   ↓
7. Return to client
   ↓
8. React Query caches result
   ↓
9. UI renders with data
```

### Write Flow (Update Task)
```
1. User edits task title
   ↓
2. Optimistic update (UI shows immediately)
   ↓
3. tRPC mutation called
   ↓
4. Server validates input
   ↓
5. Check version (optimistic lock)
   ↓
6. Update PostgreSQL (increment version)
   ↓
7. Invalidate Redis cache
   ↓
8. Broadcast WebSocket event to room
   ↓
9. Other clients receive update
   ↓
10. Merge with local state
```

### Real-time Collaboration Flow
```
User A edits task ──→ Server ──→ Broadcast
                        ↓
User B receives update ──→ Conflict check
                              ↓
                         Local state ≠ Server?
                              ↓
                    ┌─────────┴──────────┐
                    ↓                    ↓
              Version match         Version conflict
                    ↓                    ↓
            Apply update         Show conflict modal
```

## Data Models

### PostgreSQL Schema
```prisma
model User {
  id            String    @id @default(uuid())
  email         String    @unique
  name          String
  avatar_url    String?
  created_at    DateTime  @default(now())

  created_tasks Task[]    @relation("CreatedTasks")
  assigned_tasks Task[]   @relation("AssignedTasks")
  projects      ProjectMember[]
}

model Project {
  id          String    @id @default(uuid())
  name        String
  description String?
  created_at  DateTime  @default(now())

  tasks       Task[]
  members     ProjectMember[]
}

model Task {
  id          String     @id @default(uuid())
  title       String
  description String?
  status      TaskStatus @default(TODO)
  priority    Priority   @default(MEDIUM)
  version     Int        @default(1)

  project_id  String
  project     Project    @relation(fields: [project_id], references: [id])

  created_by  String
  creator     User       @relation("CreatedTasks", fields: [created_by], references: [id])

  assignee_id String?
  assignee    User?      @relation("AssignedTasks", fields: [assignee_id], references: [id])

  created_at  DateTime   @default(now())
  updated_at  DateTime   @updatedAt

  @@index([project_id, status])
  @@index([assignee_id])
}

enum TaskStatus {
  TODO
  IN_PROGRESS
  REVIEW
  DONE
}

enum Priority {
  LOW
  MEDIUM
  HIGH
  URGENT
}
```

### Redis Data Structures
```
# Caching
task:{taskId}               → Task JSON (TTL 5min)
project:{projectId}:tasks   → List of task IDs (TTL 5min)

# Real-time Presence
presence:task:{taskId}      → Set of user IDs (TTL 30s)
presence:project:{projectId} → Set of user IDs (TTL 30s)

# WebSocket Pub/Sub
channel:project:{projectId} → Events for project
channel:user:{userId}       → Personal notifications
```

## Technology Choices

### Frontend: React + Vite
**Why**: Fast HMR, minimal config, mature ecosystem
**Alternatives considered**: Next.js (overkill for SPA), Vue (team unfamiliar)

### State: Zustand + React Query
**Why**: Simple, TypeScript-first, separation of concerns
**Alternatives**: Redux (too much boilerplate), Jotai (less mature)

### Backend: Node.js + tRPC
**Why**: Type safety, shared code with frontend, fast iteration
**Alternatives**: FastAPI (separate language), GraphQL (unnecessary complexity)

### Database: PostgreSQL
**Why**: ACID guarantees, relational data, proven scale
**Alternatives**: MongoDB (data is relational), MySQL (weaker JSON support)

### Cache: Redis
**Why**: In-memory speed, pub/sub, presence tracking
**Alternatives**: Memcached (no pub/sub), In-memory JS (not persistent)

### Real-time: Socket.io
**Why**: Reliable, fallback transports, rooms support
**Alternatives**: Native WebSocket (more complex), SSE (one-way only)

## Scalability Considerations

### Current Capacity (Single Server)
- 10k concurrent users
- 50k tasks
- 100 req/sec
- 500 WebSocket connections

### Scaling Path

**Phase 1: Vertical Scaling (10k → 50k users)**
- Increase server resources (CPU, RAM)
- Add read replicas for PostgreSQL
- Increase Redis memory

**Phase 2: Horizontal Scaling (50k → 200k users)**
- Multiple app servers behind load balancer
- Redis Cluster for distributed cache
- PostgreSQL sharding by project_id
- Separate WebSocket server pool

**Phase 3: Service Split (200k+ users)**
- Split into auth, task, project, notification services
- Event-driven architecture with message queue
- Separate real-time service cluster

## Deployment Architecture

### Current (Single Server)
```
┌─────────────────────────────────────────────────────────────┐
│                    Application Server                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │    React    │  │    tRPC     │  │    Socket.io        │ │
│  │   Frontend  │  │   Backend   │  │    WebSocket      │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│                           │                                  │
│                    ┌─────────────┐                          │
│                    │    Cache    │                          │
│                    │   (Redis)   │                          │
│                    └─────────────┘                          │
└─────────────────────────────────────────────────────────────┘
                    │
        ┌─────────────────────────┐
        │    Database Server      │
        │   PostgreSQL + Backup   │
        └─────────────────────────┘
```

### Planned (Microservices)
```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Frontend      │  │   WebSocket     │  │   Auth Service  │
│   Gateway       │  │   Service       │  │                 │
└─────────┬───────┘  └─────────┬───────┘  └─────────┬───────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               │
    ┌─────────────────────────────────────────────────┐
    │              API Gateway                        │
    └─────────────────┬───────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
┌───▼────┐    ┌─────▼─────┐    ┌─────▼─────┐
│Task SVC  │    │Project SVC│    │Notify SVC │
│          │    │           │    │           │
└──────────┘    └───────────┘    └───────────┘
```

## Security Considerations

### Authentication
- JWT tokens with refresh rotation
- Role-based access control (RBAC)
- Session management with Redis

### Authorization
- Row-level security for multi-tenant data
- Permission checks at API layer
- Audit logging for sensitive operations

### Data Protection
- Encrypt sensitive data at rest (PGP)
- TLS 1.3 for all communications
- Input validation and sanitization

## Performance Targets

### Response Times
- API endpoints: <200ms (p95)
- Real-time events: <100ms
- Initial page load: <2s
- Subsequent page loads: <500ms

### Throughput
- 1000 concurrent WebSocket connections
- 1000 requests/second sustained
- 5000 peak requests/second

## Monitoring & Observability

### Metrics
- API response times and error rates
- WebSocket connection counts
- Database query performance
- Cache hit/miss ratios

### Logging
- Structured JSON logs
- Request tracing across services
- Error aggregation with context

### Health Checks
- Service-level health endpoints
- Database connectivity checks
- External dependency monitoring

## Architecture Decision Records (ADRs)

### ADR-001: Use tRPC for API Layer
**Context**: Need type-safe communication between frontend and backend.
**Decision**: Use tRPC instead of REST or GraphQL.
**Status**: Accepted
**Rationale**: Type safety, shared code, simpler than GraphQL for our use case.

### ADR-002: PostgreSQL for Primary Database
**Context**: Need reliable, transactional database for task management.
**Decision**: Use PostgreSQL instead of MongoDB.
**Status**: Accepted
**Rationale**: Relational data, ACID transactions, proven scale path.

### ADR-003: Socket.io for Real-time Communication
**Context**: Need real-time collaboration features.
**Decision**: Use Socket.io instead of native WebSockets.
**Status**: Accepted
**Rationale**: Built-in fallbacks, room management, battle-tested.

## Best Practices
1. **Separation of Concerns**: Each component has clear responsibility
2. **CQRS Pattern**: Separate read and write models where beneficial
3. **Eventual Consistency**: Accept eventual consistency for real-time features
4. **Circuit Breakers**: Protect against cascading failures
5. **Graceful Degradation**: System continues functioning when real-time fails
6. **Observability First**: Design for monitoring from the start
7. **Security by Design**: Security considerations in every component

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing architecture patterns, current tech stack, deployment infrastructure |
| **Conversation** | User's specific scalability requirements, team size, performance expectations |
| **Skill References** | Architecture patterns, scalability best practices, technology comparisons |
| **User Guidelines** | Project-specific constraints, security requirements, compliance needs |