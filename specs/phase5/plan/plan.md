# Implementation Plan: Phase 5 - Advanced Cloud Deployment

**Based on**: specs/phase5/spec/spec.md
**Created**: 2026-02-08
**Status**: Draft
**Cloud Provider**: Oracle Cloud (OKE)

---

## Implementation Phases

Phase 5 is divided into 3 sequential parts that build on each other:

```
Part A: Advanced Features (Event-Driven Code)
    ↓
Part B: Local Deployment (Minikube + Kafka + Dapr)
    ↓
Part C: Cloud Deployment (Oracle OKE + CI/CD)
```

---

## Part A: Event-Driven Architecture Code

### Step A1: Event Publisher Module in Backend

**Goal**: Add an event publishing layer to the existing Backend that publishes events via Dapr Pub/Sub HTTP API.

**Files to create/modify**:
- `phase5/backend/src/events/__init__.py` - Events package
- `phase5/backend/src/events/publisher.py` - DaprEventPublisher class
- `phase5/backend/src/events/schemas.py` - Event Pydantic models (TaskEvent, ReminderEvent)
- `phase5/backend/src/events/topics.py` - Topic name constants

**Architecture Decision**:
- Use `httpx` async client to call Dapr sidecar at `http://localhost:3500`
- Fire-and-forget pattern: if Dapr is unavailable, log error but don't fail the task operation
- Configurable via environment variable `DAPR_ENABLED=true/false` for local dev without Dapr

**Integration Points**:
- Modify `phase5/backend/src/services/task.py` (TaskService) to publish events after CRUD operations
- Modify `phase5/backend/src/mcp/tools/*.py` to trigger events through the service layer (already happens if TaskService publishes)

### Step A2: Dapr Jobs Integration for Reminders

**Goal**: Replace or augment the existing APScheduler-based reminder system with Dapr Jobs API for exact-time scheduling.

**Files to create/modify**:
- `phase5/backend/src/events/scheduler.py` - DaprJobScheduler class
- Modify `phase5/backend/src/services/task.py` - Schedule/cancel reminder jobs on task create/update/delete
- Modify `phase5/backend/src/routes/tasks.py` - Add job trigger callback endpoint

**Architecture Decision**:
- Dapr Jobs API schedules a callback at exact `reminder_at` time
- Callback endpoint `POST /api/jobs/trigger` receives the job data
- On callback, publish a `reminder.due` event to `reminders` topic via Dapr Pub/Sub
- Fallback: If Dapr Jobs unavailable, existing APScheduler continues to work

### Step A3: Notification Service (New Microservice)

**Goal**: Create a lightweight FastAPI service that subscribes to the `reminders` topic via Dapr and logs/processes notifications.

**Directory**: `phase5/notification-service/`

**Files to create**:
```
phase5/notification-service/
├── Dockerfile
├── pyproject.toml
├── src/
│   ├── __init__.py
│   ├── main.py          # FastAPI app with Dapr subscription endpoint
│   ├── config.py         # Configuration
│   └── handlers/
│       ├── __init__.py
│       └── reminder.py   # Reminder event handler
```

**How it works**:
1. Dapr sidecar subscribes to `reminders` topic on behalf of this service
2. When a reminder event arrives, Dapr calls `POST /api/reminders` on this service
3. Service logs the notification with structured logging
4. Optionally reuses SendGrid email logic from Phase 3

### Step A4: Recurring Task Service (New Microservice)

**Goal**: Create a service that consumes `task.completed` events and creates next occurrence for recurring tasks.

**Directory**: `phase5/recurring-task-service/`

**Files to create**:
```
phase5/recurring-task-service/
├── Dockerfile
├── pyproject.toml
├── src/
│   ├── __init__.py
│   ├── main.py           # FastAPI app with Dapr subscription
│   ├── config.py          # Configuration
│   └── handlers/
│       ├── __init__.py
│       └── task_completed.py  # Handle task.completed events
```

**How it works**:
1. Subscribes to `task-events` topic via Dapr
2. Filters for `task.completed` events where `recurrence_pattern` is set
3. Calculates next due date based on recurrence pattern
4. Creates new task via Dapr Service Invocation to Backend API
5. Ignores events for non-recurring tasks

### Step A5: Audit Service (New Microservice)

**Goal**: Create a service that consumes all `task-events` and stores them as activity records.

**Directory**: `phase5/audit-service/`

**Files to create**:
```
phase5/audit-service/
├── Dockerfile
├── pyproject.toml
├── src/
│   ├── __init__.py
│   ├── main.py           # FastAPI app with Dapr subscription
│   ├── config.py          # Configuration
│   └── handlers/
│       ├── __init__.py
│       └── task_event.py  # Handle all task events
```

**How it works**:
1. Subscribes to `task-events` topic via Dapr
2. Receives all event types (created, updated, completed, deleted)
3. Stores activity via Dapr Service Invocation to Backend's `/api/activities` endpoint
4. Provides complete audit trail

---

## Part B: Local Deployment (Minikube + Kafka + Dapr)

### Step B1: Kafka Setup on Minikube (Strimzi)

**Goal**: Deploy a single-broker Kafka cluster on Minikube using Strimzi operator.

**Files to create**:
```
phase5/infra/kafka/
├── strimzi-install.sh          # Script to install Strimzi operator
├── kafka-cluster.yaml          # Kafka cluster definition (1 broker, ephemeral)
└── kafka-topics.yaml           # Topic definitions (task-events, reminders, task-updates)
```

**Deployment Steps**:
1. Create `kafka` namespace
2. Install Strimzi operator from official URL
3. Apply kafka-cluster.yaml (1 broker, ephemeral storage)
4. Wait for cluster ready
5. Create topics

### Step B2: Dapr Setup on Minikube

**Goal**: Install Dapr on Minikube and configure all components.

**Files to create**:
```
phase5/infra/dapr/
├── dapr-install.sh             # Script to install Dapr on K8s
├── components/
│   ├── kafka-pubsub.yaml       # Pub/Sub component (Kafka)
│   ├── statestore.yaml         # State store component (PostgreSQL/Neon)
│   ├── kubernetes-secrets.yaml # Secret store component
│   └── subscription.yaml       # Topic subscriptions for services
```

### Step B3: Docker Images for New Services

**Goal**: Build Docker images for the 3 new microservices.

**Files to modify/create**:
- `phase5/notification-service/Dockerfile`
- `phase5/recurring-task-service/Dockerfile`
- `phase5/audit-service/Dockerfile`

**Approach**: Lightweight Python images similar to Backend Dockerfile but much smaller (no need for full backend dependencies).

### Step B4: Updated Helm Charts

**Goal**: Extend the existing Helm chart to include all new services, Kafka, and Dapr.

**Files to create/modify**:
```
phase5/todo-app/
├── Chart.yaml                          # Update version to 5.0.0
├── values.yaml                         # Add new service configs
├── templates/
│   ├── (existing backend/frontend)     # Add Dapr annotations
│   ├── notification-deployment.yaml    # New
│   ├── notification-service.yaml       # New
│   ├── recurring-deployment.yaml       # New
│   ├── recurring-service.yaml          # New
│   ├── audit-deployment.yaml           # New
│   ├── audit-service.yaml              # New
│   └── dapr-components.yaml            # Dapr component definitions
```

**Dapr Annotations** (added to all deployments):
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "backend-service"
  dapr.io/app-port: "8000"
```

### Step B5: Minikube Deployment Script

**Goal**: One-command deployment of everything on Minikube.

**File**: `phase5/deploy-minikube.sh`

**Steps**:
1. Start Minikube (4 CPUs, 8GB RAM)
2. Install Strimzi + create Kafka cluster
3. Install Dapr (`dapr init -k`)
4. Apply Dapr components
5. Build Docker images (using Minikube's Docker daemon)
6. Deploy via Helm
7. Wait for all pods ready
8. Print access URLs

---

## Part C: Cloud Deployment (Oracle OKE)

### Step C1: Oracle OKE Cluster Setup

**Goal**: Provision an OKE cluster on Oracle Cloud Always Free tier.

**Files to create**:
```
phase5/infra/oracle/
├── README-OKE-SETUP.md         # Step-by-step OKE provisioning guide
├── oke-cluster-config.md       # Cluster configuration details
└── ocir-setup.md               # Container registry setup
```

**Manual Steps** (documented in README):
1. Sign up at oracle.com/cloud/free
2. Create compartment for the project
3. Create OKE cluster (4 OCPUs, 24GB RAM)
4. Configure kubectl to connect
5. Set up Oracle Container Registry (OCIR)

### Step C2: Cloud-Specific Configurations

**Goal**: Adapt Helm values for cloud deployment.

**Files to create**:
```
phase5/todo-app/
├── values-oracle.yaml          # Oracle OKE overrides
```

**Key Differences from Minikube**:
- Image pull from OCIR (not local)
- LoadBalancer services (not NodePort)
- Resource limits adjusted for OKE free tier
- Production secrets management
- Ingress configuration (optional)

### Step C3: CI/CD Pipeline (GitHub Actions)

**Goal**: Automated build, push, and deploy pipeline.

**Files to create**:
```
.github/workflows/
├── phase5-ci.yml               # CI: Test on PR
├── phase5-cd.yml               # CD: Build + Deploy on push to main
```

**CI Pipeline** (on PR):
1. Run backend tests (pytest)
2. Run frontend tests (npm test)
3. Lint checks

**CD Pipeline** (on push to main):
1. Build Docker images (backend, frontend, notification, recurring, audit)
2. Push to Oracle OCIR
3. Deploy to OKE via kubectl/helm
4. Verify health checks

### Step C4: Monitoring & Logging

**Goal**: Add observability to all services.

**Files to create/modify**:
- Add structured JSON logging to all services
- Add correlation ID propagation
- Health check endpoints on all new services
- Dapr dashboard access

---

## Dependency Graph

```
A1 (Event Publisher) ──→ A2 (Jobs/Reminders)
       │                       │
       ├──→ A3 (Notification)  │
       ├──→ A4 (Recurring)     │
       └──→ A5 (Audit)         │
                               │
B1 (Kafka/Strimzi) ───────────┤
B2 (Dapr Setup) ──────────────┤
B3 (Docker Images) ←── A3,A4,A5
B4 (Helm Charts) ←── B1,B2,B3
B5 (Deploy Script) ←── B4
                               │
C1 (OKE Setup) ───────────────┤
C2 (Cloud Config) ←── B4,C1   │
C3 (CI/CD) ←── C2             │
C4 (Monitoring) ←── C2        │
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Kafka takes too long to start on Minikube | Use single broker, ephemeral storage, generous timeouts |
| Dapr sidecar injection issues | Verify namespace annotations, check Dapr status before deploying apps |
| Oracle free tier resource limits | Keep replicas at 1, use lightweight images, monitor resource usage |
| Event ordering issues | Use task_id as Kafka partition key for per-task ordering |
| Local dev without Dapr/Kafka | `DAPR_ENABLED` env var to disable event publishing in dev mode |

---

## Estimated Effort

| Part | Steps | Estimated Effort |
|------|-------|-----------------|
| Part A | A1-A5 | Core development work |
| Part B | B1-B5 | Infrastructure setup |
| Part C | C1-C4 | Cloud deployment |
