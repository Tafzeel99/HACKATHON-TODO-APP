# Feature Specification: Phase 5 - Advanced Cloud Deployment

**Feature Branch**: `phase5-cloud-deployment`
**Created**: 2026-02-08
**Status**: Draft
**Cloud Provider**: Oracle Cloud (OKE) - Always Free Tier
**Input**: Phase 5 guide requirements - Event-driven architecture with Kafka/Dapr, local Minikube deployment, cloud deployment on Oracle OKE

---

## Overview

Phase 5 transforms the Todo application from a locally-deployed Kubernetes app (Phase 4) into a production-grade, event-driven microservices system deployed on Oracle Kubernetes Engine (OKE). The system adds Kafka for event streaming, Dapr for distributed application runtime, and introduces specialized microservices (Notification Service, Recurring Task Service, Audit Service) that communicate through events rather than direct API calls.

**Key Value Proposition**: The application evolves from a monolithic CRUD+AI app into a scalable, loosely-coupled event-driven architecture where services operate independently, enabling real-time notifications, automatic recurring task creation, and a complete audit trail - all orchestrated through Dapr and Kafka within Kubernetes.

---

## Architecture Summary

```
KUBERNETES CLUSTER (Oracle OKE)
├── Frontend Pod (Next.js + Dapr Sidecar)
├── Backend Pod (FastAPI + MCP + Dapr Sidecar)
├── Notification Service Pod (+ Dapr Sidecar)
├── Recurring Task Service Pod (+ Dapr Sidecar)
├── Audit Service Pod (+ Dapr Sidecar)
├── Kafka Cluster (Strimzi Operator)
├── Dapr Control Plane
│   ├── Pub/Sub Component (pubsub.kafka)
│   ├── State Store Component (state.postgresql)
│   ├── Jobs API (scheduled reminders)
│   └── Secret Store Component (secretstores.kubernetes)
└── External: Neon PostgreSQL (existing)
```

---

## Part A: Advanced Features

### A1 - Kafka Event-Driven Architecture

#### User Story A1.1 - Task Event Publishing (Priority: P1)

As the system, when any task CRUD operation occurs, I want to publish an event to Kafka so that downstream services can react independently.

**Why this priority**: This is the foundational event infrastructure. All other event-driven features depend on events being published.

**Acceptance Scenarios**:

1. **Given** a user creates a task via API or chat, **When** the task is persisted, **Then** a `task.created` event is published to the `task-events` Kafka topic with task_id, task_data, user_id, and timestamp
2. **Given** a user updates a task, **When** the update is persisted, **Then** a `task.updated` event is published to `task-events`
3. **Given** a user deletes a task, **When** the deletion occurs, **Then** a `task.deleted` event is published to `task-events`
4. **Given** a user completes a task, **When** the completion is persisted, **Then** a `task.completed` event is published to `task-events`
5. **Given** Kafka is temporarily unavailable, **When** a task operation occurs, **Then** the operation still succeeds (fire-and-forget with logging) and the event is logged as failed

**Event Schema - TaskEvent**:
```json
{
  "event_id": "uuid",
  "event_type": "created | updated | completed | deleted",
  "task_id": 123,
  "task_data": { "title": "...", "priority": "...", ... },
  "user_id": "user-uuid",
  "timestamp": "2026-02-08T12:00:00Z"
}
```

---

#### User Story A1.2 - Reminder Event Publishing (Priority: P1)

As the system, when a task with a due date is created or updated, I want to schedule a reminder event so that users get notified before their task is due.

**Acceptance Scenarios**:

1. **Given** a user creates a task with `due_date=2026-02-10` and `reminder_at=2026-02-09T09:00:00Z`, **When** the task is created, **Then** a reminder is scheduled via Dapr Jobs API to fire at `remind_at` time
2. **Given** a scheduled reminder fires, **When** the Dapr Job triggers the callback, **Then** a `reminder.due` event is published to the `reminders` Kafka topic
3. **Given** a task's due date is updated, **When** the update occurs, **Then** the old reminder job is cancelled and a new one is scheduled
4. **Given** a task is deleted, **When** the deletion occurs, **Then** any associated reminder job is cancelled

**Event Schema - ReminderEvent**:
```json
{
  "task_id": 123,
  "title": "Task title",
  "due_at": "2026-02-10T00:00:00Z",
  "remind_at": "2026-02-09T09:00:00Z",
  "user_id": "user-uuid"
}
```

---

#### User Story A1.3 - Real-time Task Sync Events (Priority: P3)

As a user with multiple browser tabs open, I want changes made in one tab to appear in all tabs so that my task list is always up-to-date.

**Acceptance Scenarios**:

1. **Given** a user has 2 browser tabs open, **When** a task is created in tab 1, **Then** tab 2 receives the update via WebSocket within 2 seconds
2. **Given** a task is completed in any client, **When** the event is published to `task-updates`, **Then** a WebSocket service broadcasts to all connected clients of that user

---

### A2 - Notification Service (New Microservice)

#### User Story A2.1 - Consume Reminder Events (Priority: P1)

As the Notification Service, I want to consume events from the `reminders` Kafka topic so that I can notify users about upcoming due dates.

**Acceptance Scenarios**:

1. **Given** a `reminder.due` event is published, **When** the Notification Service consumes it, **Then** it logs the notification (console/structured log) with task title, user_id, and due_at
2. **Given** the Notification Service starts, **When** it connects to Kafka via Dapr Pub/Sub, **Then** it subscribes to the `reminders` topic successfully
3. **Given** a reminder event is consumed, **When** processing completes, **Then** an activity record is created noting the reminder was sent

**Technical Notes**:
- Lightweight FastAPI service
- Subscribes via Dapr Pub/Sub (no direct Kafka client)
- For hackathon scope: log-based notifications (no real email/push required, but the SendGrid integration from Phase 3 can be reused if desired)

---

### A3 - Recurring Task Service (New Microservice)

#### User Story A3.1 - Auto-Create Next Occurrence (Priority: P1)

As the Recurring Task Service, when a recurring task is completed, I want to automatically create the next occurrence so that the user's recurring workflow continues seamlessly.

**Acceptance Scenarios**:

1. **Given** a `task.completed` event for a task with `recurrence_pattern=daily`, **When** the Recurring Task Service consumes it, **Then** a new task is created with the next due date (tomorrow) via Dapr Service Invocation to the Backend
2. **Given** a recurring task with `recurrence_end_date=2026-03-01` is completed on 2026-03-01, **When** the event is consumed, **Then** no new task is created (recurrence ended)
3. **Given** a non-recurring task is completed, **When** the event is consumed, **Then** it is ignored (no action taken)

**Supported Recurrence Patterns**: daily, weekly, monthly, yearly (already in Task model)

---

### A4 - Audit Service (New Microservice)

#### User Story A4.1 - Complete Activity Log (Priority: P2)

As the Audit Service, I want to consume all events from `task-events` and store a complete history so that users can review all changes made to their tasks.

**Acceptance Scenarios**:

1. **Given** any task event is published, **When** the Audit Service consumes it, **Then** it stores the event in the activity log (existing Activity model in Neon DB)
2. **Given** a user requests their activity feed, **When** the API is called, **Then** all events (create, update, complete, delete) are returned in chronological order

**Technical Notes**:
- Can use the existing Activity model and ActivityService from the backend
- Stores events via Dapr Service Invocation or directly to Neon DB via Dapr State Store

---

## Part B: Dapr Integration

### B1 - Dapr Pub/Sub Component (Kafka)

#### User Story B1.1 - Publish Events via Dapr (Priority: P1)

As the Backend service, I want to publish events through Dapr's Pub/Sub API instead of using kafka-python directly so that the code is infrastructure-agnostic.

**Acceptance Scenarios**:

1. **Given** the Backend has Dapr sidecar running, **When** it publishes to `http://localhost:3500/v1.0/publish/kafka-pubsub/task-events`, **Then** the event reaches the Kafka `task-events` topic
2. **Given** Dapr Pub/Sub is configured with Kafka component, **When** a service subscribes to a topic, **Then** Dapr delivers messages to the service's HTTP endpoint

**Dapr Component**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "taskflow-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
    - name: consumerGroup
      value: "todo-service"
    - name: authType
      value: "none"
```

---

### B2 - Dapr State Store Component

#### User Story B2.1 - State Management via Dapr (Priority: P2)

As the system, I want to optionally use Dapr State Store for conversation state caching so that state management is abstracted from the database.

**Acceptance Scenarios**:

1. **Given** Dapr state store is configured with PostgreSQL (Neon), **When** conversation state is saved via `POST /v1.0/state/statestore`, **Then** it persists in Neon DB
2. **Given** state is saved, **When** retrieved via `GET /v1.0/state/statestore/{key}`, **Then** the correct state is returned

---

### B3 - Dapr Service Invocation

#### User Story B3.1 - Inter-Service Communication (Priority: P1)

As a microservice, I want to call other services through Dapr Service Invocation so that I get automatic retries, mTLS, and service discovery.

**Acceptance Scenarios**:

1. **Given** the Recurring Task Service needs to create a task, **When** it calls `http://localhost:3500/v1.0/invoke/backend-service/method/api/tasks`, **Then** Dapr routes the request to the Backend service with automatic retries
2. **Given** the Frontend calls the Backend, **When** it uses Dapr service invocation, **Then** the request is load-balanced and secured with mTLS

---

### B4 - Dapr Secrets Management

#### User Story B4.1 - Secrets via Dapr (Priority: P2)

As the system, I want to access secrets through Dapr's Secrets API using Kubernetes Secrets as the backing store so that credentials are managed securely.

**Acceptance Scenarios**:

1. **Given** Kubernetes Secrets contain `DATABASE_URL` and `OPEN_ROUTER_KEY`, **When** a service calls `GET /v1.0/secrets/kubernetes-secrets/todo-secrets`, **Then** the secrets are returned without the service needing direct Kubernetes API access

---

### B5 - Dapr Jobs API (Scheduled Reminders)

#### User Story B5.1 - Schedule Exact-Time Reminders (Priority: P1)

As the Backend, when a task with a due date is created, I want to schedule a Dapr Job at the exact reminder time so that notifications fire precisely, not via polling.

**Acceptance Scenarios**:

1. **Given** a task is created with `reminder_at=2026-02-09T09:00:00Z`, **When** the Backend schedules a Dapr Job, **Then** at 09:00 UTC on Feb 9, Dapr calls `POST /api/jobs/trigger` on the Backend
2. **Given** the job fires, **When** the Backend receives the callback, **Then** it publishes a `reminder.due` event to the `reminders` Kafka topic via Dapr Pub/Sub

---

## Part C: Deployment

### C1 - Local Deployment (Minikube)

#### User Story C1.1 - Deploy Full Stack on Minikube (Priority: P1)

As a developer, I want to deploy the entire system (Backend, Frontend, Kafka, Dapr, Notification Service, Recurring Task Service, Audit Service) on Minikube so that I can test locally before cloud deployment.

**Acceptance Scenarios**:

1. **Given** Minikube is running with sufficient resources (4 CPU, 8GB RAM), **When** I run the deployment script/helm commands, **Then** all services start successfully within 5 minutes
2. **Given** all services are running, **When** I access the frontend, **Then** I can create tasks and see events flow through Kafka to downstream services
3. **Given** Dapr is initialized on Minikube, **When** I check `dapr status -k`, **Then** all Dapr system services are running

**Deployment Components**:
- Strimzi Kafka Operator + Kafka Cluster (1 broker, ephemeral)
- Dapr Control Plane (`dapr init -k`)
- Backend + Dapr Sidecar
- Frontend + Dapr Sidecar
- Notification Service + Dapr Sidecar
- Recurring Task Service + Dapr Sidecar
- Audit Service + Dapr Sidecar
- Dapr Components (Pub/Sub, State, Secrets, Jobs)

---

### C2 - Oracle Cloud Deployment (OKE)

#### User Story C2.1 - Deploy to Oracle Kubernetes Engine (Priority: P1)

As a developer, I want to deploy the full system to Oracle OKE so that it runs in production-grade cloud infrastructure.

**Why Oracle**: Always Free tier with 4 OCPUs, 24GB RAM - no credit card charges after trial, best for learning.

**Acceptance Scenarios**:

1. **Given** an OKE cluster is provisioned, **When** I apply the Kubernetes manifests, **Then** all services deploy and become healthy
2. **Given** the system is running on OKE, **When** a user creates a task, **Then** the event flows through Kafka and downstream services process it
3. **Given** Oracle Container Registry (OCIR) is configured, **When** images are pushed, **Then** OKE pulls and deploys them

**Cloud Infrastructure**:
- Oracle OKE cluster (4 OCPUs, 24GB RAM - Always Free)
- Oracle Container Registry (OCIR) for Docker images
- Strimzi Kafka within the cluster (self-hosted, free)
- Dapr on OKE
- External: Neon PostgreSQL (existing)

---

### C3 - CI/CD Pipeline

#### User Story C3.1 - GitHub Actions Pipeline (Priority: P2)

As a developer, I want a CI/CD pipeline using GitHub Actions so that code changes are automatically built, tested, and deployed.

**Acceptance Scenarios**:

1. **Given** a push to the `main` branch, **When** GitHub Actions triggers, **Then** it builds Docker images, pushes to OCIR, and deploys to OKE
2. **Given** a pull request is opened, **When** GitHub Actions triggers, **Then** it runs tests and linting (no deployment)
3. **Given** the pipeline succeeds, **When** new images are deployed, **Then** Kubernetes performs a rolling update with zero downtime

**Pipeline Stages**:
1. Lint & Test (pytest, eslint)
2. Build Docker Images (multi-stage)
3. Push to Oracle Container Registry
4. Deploy to OKE (kubectl apply / helm upgrade)

---

### C4 - Monitoring & Logging

#### User Story C4.1 - Observability Setup (Priority: P3)

As a developer, I want monitoring and structured logging so that I can observe the system's health and debug issues.

**Acceptance Scenarios**:

1. **Given** services are running, **When** I check health endpoints, **Then** all services report healthy status
2. **Given** structured logging is enabled, **When** events flow through the system, **Then** I can trace an event from publish to consume via correlation IDs
3. **Given** Kubernetes metrics are available, **When** I check pod status, **Then** I can see CPU/memory usage and restart counts

**Approach**:
- Structured JSON logging in all services
- Health check endpoints (`/health`) on all services
- Kubernetes-native monitoring (kubectl top, pod status)
- Dapr dashboard for sidecar observability

---

## Kafka Topics

| Topic | Producer | Consumer(s) | Purpose |
|-------|----------|-------------|---------|
| `task-events` | Backend (via Dapr) | Recurring Task Service, Audit Service | All task CRUD operations |
| `reminders` | Backend (via Dapr Jobs callback) | Notification Service | Scheduled reminder triggers |
| `task-updates` | Backend (via Dapr) | WebSocket Service (P3 - optional) | Real-time client sync |

---

## New Microservices

### Notification Service
- **Language**: Python (FastAPI)
- **Purpose**: Consume reminder events, log/send notifications
- **Dapr**: Pub/Sub subscriber on `reminders` topic
- **Port**: 8001

### Recurring Task Service
- **Language**: Python (FastAPI)
- **Purpose**: Consume task.completed events, create next occurrence for recurring tasks
- **Dapr**: Pub/Sub subscriber on `task-events` topic, Service Invocation to Backend
- **Port**: 8002

### Audit Service
- **Language**: Python (FastAPI)
- **Purpose**: Consume all task events, store activity history
- **Dapr**: Pub/Sub subscriber on `task-events` topic
- **Port**: 8003

---

## Technology Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Cloud Provider | Oracle OKE | Always Free (4 OCPUs, 24GB RAM), no charges after trial |
| Kafka Deployment | Strimzi Operator (self-hosted in K8s) | Free, learning experience, Dapr-compatible |
| Container Registry | Oracle OCIR | Integrated with OKE, free tier available |
| Dapr | Full suite (Pub/Sub, State, Jobs, Secrets, Service Invocation) | Infrastructure abstraction, cloud-portable |
| CI/CD | GitHub Actions | Free for public repos, good OKE integration |
| Monitoring | Structured logging + K8s native | Simple, sufficient for hackathon |

---

## Non-Functional Requirements

- **Performance**: Event processing latency < 5 seconds end-to-end
- **Reliability**: Task CRUD operations must not fail if Kafka is down (fire-and-forget events)
- **Security**: All inter-service communication via Dapr mTLS, secrets in K8s Secrets
- **Scalability**: Each microservice independently scalable via K8s replicas
- **Portability**: Dapr abstraction allows swapping Kafka for RabbitMQ, PostgreSQL for Redis, etc.

---

## Out of Scope

- Real push notifications (mobile/browser) - log-based is sufficient
- WebSocket real-time sync (P3 - nice to have, not required)
- Multi-region deployment
- Auto-scaling (HPA) - manual scaling is fine for hackathon
- Service mesh (Istio) - Dapr provides sufficient service-to-service security

---

## Dependencies

- Phase 4 completed (Docker images, Helm charts, Minikube deployment) ✅
- Oracle Cloud account with Always Free tier
- Neon PostgreSQL (existing from Phase 2) ✅
- OpenRouter API key (existing from Phase 3) ✅
- GitHub repository (existing) ✅
