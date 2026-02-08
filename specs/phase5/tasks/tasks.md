# Task Breakdown: Phase 5 - Advanced Cloud Deployment

**Based on**: specs/phase5/plan/plan.md
**Created**: 2026-02-08
**Status**: Complete
**Completed**: 2026-02-08

---

## Part A: Event-Driven Architecture Code

### T5-001: Create Event Schemas & Publisher Module [DONE]
**Priority**: P1 | **Depends on**: None
**Files**:
- CREATE `phase5/backend/src/events/__init__.py`
- CREATE `phase5/backend/src/events/schemas.py`
- CREATE `phase5/backend/src/events/topics.py`
- CREATE `phase5/backend/src/events/publisher.py`
- MODIFY `phase5/backend/src/config.py` (add DAPR_HTTP_PORT, DAPR_ENABLED)

**Acceptance Criteria**:
- [x] `TaskEvent` Pydantic model with event_id, event_type, task_id, task_data, user_id, timestamp
- [x] `ReminderEvent` Pydantic model with task_id, title, due_at, remind_at, user_id
- [x] Topic constants: `TASK_EVENTS = "task-events"`, `REMINDERS = "reminders"`, `TASK_UPDATES = "task-updates"`
- [x] `DaprEventPublisher` class with `publish(topic, event_type, data)` method using httpx
- [x] Fire-and-forget: catches exceptions, logs errors, never fails the caller
- [x] `DAPR_ENABLED` config flag (default: False for local dev)

---

### T5-002: Integrate Event Publishing into TaskService [DONE]
**Priority**: P1 | **Depends on**: T5-001
**Files**:
- MODIFY `phase5/backend/src/services/task.py`

**Acceptance Criteria**:
- [x] After `create_task()` → publish `task.created` event
- [x] After `update_task()` → publish `task.updated` event
- [x] After `complete_task()` → publish `task.completed` event
- [x] After `delete_task()` → publish `task.deleted` event
- [x] Events include full task data serialized to dict
- [x] Publishing is non-blocking (fire-and-forget)
- [x] When `DAPR_ENABLED=false`, skip publishing silently

---

### T5-003: Add Dapr Jobs Integration for Reminders [DONE]
**Priority**: P1 | **Depends on**: T5-001
**Files**:
- CREATE `phase5/backend/src/events/scheduler.py` (DaprJobScheduler)
- MODIFY `phase5/backend/src/services/task.py` (schedule/cancel reminders)
- MODIFY `phase5/backend/src/main.py` (add `/api/jobs/trigger` endpoint)

**Acceptance Criteria**:
- [x] `DaprJobScheduler` class with `schedule_reminder(task_id, remind_at, user_id)` method
- [x] Uses Dapr Jobs API: `POST http://localhost:{DAPR_HTTP_PORT}/v1.0-alpha1/jobs/reminder-task-{task_id}`
- [x] `cancel_reminder(task_id)` method to delete scheduled jobs
- [x] `/api/jobs/trigger` POST endpoint that receives Dapr job callback
- [x] On callback, publishes `reminder.due` event to `reminders` topic
- [x] When task with reminder_at is created → schedule job
- [x] When task with reminder_at is updated → cancel old + schedule new
- [x] When task is deleted → cancel associated job

---

### T5-004: Create Notification Service [DONE]
**Priority**: P1 | **Depends on**: T5-001
**Files**:
- CREATE `phase5/notification-service/pyproject.toml`
- CREATE `phase5/notification-service/src/__init__.py`
- CREATE `phase5/notification-service/src/main.py`
- CREATE `phase5/notification-service/src/config.py`
- CREATE `phase5/notification-service/src/handlers/__init__.py`
- CREATE `phase5/notification-service/src/handlers/reminder.py`
- CREATE `phase5/notification-service/Dockerfile`

**Acceptance Criteria**:
- [x] FastAPI app on port 8001
- [x] `GET /health` returns `{"status": "healthy", "service": "notification-service"}`
- [x] `GET /dapr/subscribe` returns subscription config for `reminders` topic
- [x] `POST /api/reminders` endpoint handles Dapr Pub/Sub delivery
- [x] Logs notification with structured JSON: task_id, title, user_id, due_at
- [x] Dockerfile: multi-stage build, non-root user, health check

---

### T5-005: Create Recurring Task Service [DONE]
**Priority**: P1 | **Depends on**: T5-001
**Files**:
- CREATE `phase5/recurring-task-service/pyproject.toml`
- CREATE `phase5/recurring-task-service/src/__init__.py`
- CREATE `phase5/recurring-task-service/src/main.py`
- CREATE `phase5/recurring-task-service/src/config.py`
- CREATE `phase5/recurring-task-service/src/handlers/__init__.py`
- CREATE `phase5/recurring-task-service/src/handlers/task_completed.py`
- CREATE `phase5/recurring-task-service/Dockerfile`

**Acceptance Criteria**:
- [x] FastAPI app on port 8002
- [x] `GET /health` returns `{"status": "healthy", "service": "recurring-task-service"}`
- [x] `GET /dapr/subscribe` returns subscription for `task-events` topic
- [x] `POST /api/task-events` endpoint receives all task events via Dapr
- [x] Filters for `task.completed` events only
- [x] Checks if task has `recurrence_pattern` set
- [x] Calculates next due date: daily (+1 day), weekly (+7 days), monthly (+1 month), yearly (+1 year)
- [x] Respects `recurrence_end_date` - no new task if past end date
- [x] Creates next task via Dapr Service Invocation: `POST http://localhost:3500/v1.0/invoke/backend-service/method/api/tasks`
- [x] Dockerfile: multi-stage build, non-root user, health check

---

### T5-006: Create Audit Service [DONE]
**Priority**: P2 | **Depends on**: T5-001
**Files**:
- CREATE `phase5/audit-service/pyproject.toml`
- CREATE `phase5/audit-service/src/__init__.py`
- CREATE `phase5/audit-service/src/main.py`
- CREATE `phase5/audit-service/src/config.py`
- CREATE `phase5/audit-service/src/handlers/__init__.py`
- CREATE `phase5/audit-service/src/handlers/task_event.py`
- CREATE `phase5/audit-service/Dockerfile`

**Acceptance Criteria**:
- [x] FastAPI app on port 8003
- [x] `GET /health` returns `{"status": "healthy", "service": "audit-service"}`
- [x] `GET /dapr/subscribe` returns subscription for `task-events` topic
- [x] `POST /api/task-events` endpoint receives all task events via Dapr
- [x] Stores activity via Dapr Service Invocation to Backend: `POST /api/activities`
- [x] Logs all events with structured JSON logging
- [x] Dockerfile: multi-stage build, non-root user, health check

---

## Part B: Local Deployment (Minikube + Kafka + Dapr)

### T5-007: Create Kafka Infrastructure (Strimzi) [DONE]
**Priority**: P1 | **Depends on**: None
**Files**:
- CREATE `phase5/infra/kafka/kafka-cluster.yaml`
- CREATE `phase5/infra/kafka/kafka-topics.yaml`

**Acceptance Criteria**:
- [x] Kafka cluster YAML: 1 broker, ephemeral storage, plain listener on 9092
- [x] Topic definitions: `task-events`, `reminders`, `task-updates` (3/1/3 partitions, 1 replica each)
- [x] All in `kafka` namespace

---

### T5-008: Create Dapr Component Configurations [DONE]
**Priority**: P1 | **Depends on**: None
**Files**:
- CREATE `phase5/infra/dapr/components/kafka-pubsub.yaml`
- CREATE `phase5/infra/dapr/components/statestore.yaml`
- CREATE `phase5/infra/dapr/components/kubernetes-secrets.yaml`

**Acceptance Criteria**:
- [x] `kafka-pubsub` component: type `pubsub.kafka`, brokers pointing to Strimzi bootstrap service
- [x] `statestore` component: type `state.postgresql`, connection string from K8s secret
- [x] `kubernetes-secrets` component: type `secretstores.kubernetes`
- [x] All components in correct namespace for Dapr to discover

---

### T5-009: Update Helm Chart for Phase 5 [DONE]
**Priority**: P1 | **Depends on**: T5-004, T5-005, T5-006, T5-007, T5-008
**Files**:
- MODIFY `phase5/todo-app/Chart.yaml` (version 5.0.0)
- MODIFY `phase5/todo-app/values.yaml` (add new services, Dapr config)
- MODIFY `phase5/todo-app/templates/backend-deployment.yaml` (add Dapr annotations)
- MODIFY `phase5/todo-app/templates/frontend-deployment.yaml` (add Dapr annotations)
- CREATE `phase5/todo-app/templates/notification-deployment.yaml`
- CREATE `phase5/todo-app/templates/notification-service.yaml`
- CREATE `phase5/todo-app/templates/recurring-deployment.yaml`
- CREATE `phase5/todo-app/templates/recurring-service.yaml`
- CREATE `phase5/todo-app/templates/audit-deployment.yaml`
- CREATE `phase5/todo-app/templates/audit-service.yaml`
- CREATE `phase5/todo-app/templates/dapr-components.yaml`

**Acceptance Criteria**:
- [x] Chart version bumped to 5.0.0
- [x] Backend/Frontend deployments have Dapr sidecar annotations
- [x] New deployments for notification, recurring, audit services with Dapr annotations
- [x] New ClusterIP services for each microservice
- [x] Dapr components (pubsub, statestore, secrets) included in chart
- [x] Values.yaml has config for all new services (image, port, resources, env vars)
- [x] Backend configmap includes `DAPR_ENABLED=true`

---

### T5-010: Build Docker Images for New Services [DONE]
**Priority**: P1 | **Depends on**: T5-004, T5-005, T5-006
**Files**: Dockerfiles already created in T5-004, T5-005, T5-006

**Acceptance Criteria**:
- [x] `docker build` Dockerfile ready for notification-service
- [x] `docker build` Dockerfile ready for recurring-task-service
- [x] `docker build` Dockerfile ready for audit-service
- [x] All use multi-stage builds with health checks
- [x] Non-root user in all containers

---

### T5-011: Create Minikube Deployment Script [DONE]
**Priority**: P1 | **Depends on**: T5-009, T5-010
**Files**:
- CREATE `phase5/deploy-minikube.sh`

**Acceptance Criteria**:
- [x] Script starts Minikube with 4 CPUs, 8GB RAM
- [x] Installs Strimzi operator and creates Kafka cluster
- [x] Installs Dapr on K8s (`dapr init -k`)
- [x] Applies Dapr components
- [x] Builds all Docker images in Minikube's Docker daemon
- [x] Deploys via `helm upgrade --install`
- [x] Waits for all pods to be ready
- [x] Prints access URLs (frontend, backend, Dapr dashboard)
- [x] Script is idempotent (can re-run safely)

---

## Part C: Cloud Deployment (Oracle OKE)

### T5-012: Oracle OKE Setup Documentation [DONE]
**Priority**: P1 | **Depends on**: None
**Files**:
- CREATE `phase5/infra/oracle/README-OKE-SETUP.md`

**Acceptance Criteria**:
- [x] Step-by-step guide: sign up, create compartment, create OKE cluster
- [x] kubectl configuration for OKE
- [x] OCIR (Container Registry) setup
- [x] Auth token generation for OCIR push
- [x] Cluster sizing: 4 OCPUs, 24GB RAM (Always Free)

---

### T5-013: Create Oracle Cloud Helm Values [DONE]
**Priority**: P1 | **Depends on**: T5-009, T5-012
**Files**:
- CREATE `phase5/todo-app/values-oracle.yaml`

**Acceptance Criteria**:
- [x] Image references point to OCIR (region.ocir.io/namespace/image:tag)
- [x] `imagePullPolicy: Always` (not Never like Minikube)
- [x] `imagePullSecrets` configured for OCIR auth
- [x] Service type: `LoadBalancer` (not NodePort)
- [x] Resource limits appropriate for OKE free tier
- [x] Dapr configuration for cloud environment

---

### T5-014: Create CI/CD Pipeline (GitHub Actions) [DONE]
**Priority**: P2 | **Depends on**: T5-013
**Files**:
- CREATE `.github/workflows/phase5-ci.yml`
- CREATE `.github/workflows/phase5-cd.yml`

**Acceptance Criteria**:
- [x] CI workflow: triggers on PR, runs pytest + eslint
- [x] CD workflow: triggers on push to main
- [x] CD builds 5 Docker images (backend, frontend, notification, recurring, audit)
- [x] CD pushes to Oracle OCIR
- [x] CD deploys to OKE via helm upgrade
- [x] GitHub secrets documented: OCI_AUTH_TOKEN, OCI_TENANCY, KUBECONFIG
- [x] Rolling update with zero downtime

---

### T5-015: Add Monitoring & Structured Logging [DONE]
**Priority**: P3 | **Depends on**: T5-004, T5-005, T5-006
**Files**:
- All 3 microservice `main.py` files include structured logging
- All 3 microservice `config.py` files include LOG_LEVEL

**Acceptance Criteria**:
- [x] All services use structured JSON logging (Python `logging` with JSON formatter)
- [x] Log entries include: timestamp, service_name, level, message
- [x] Health check endpoints on all services
- [x] Event processing logged: received, processed, failed

---

## Task Summary

| Task ID | Title | Priority | Depends On | Part | Status |
|---------|-------|----------|------------|------|--------|
| T5-001 | Event Schemas & Publisher Module | P1 | - | A | DONE |
| T5-002 | Integrate Events into TaskService | P1 | T5-001 | A | DONE |
| T5-003 | Dapr Jobs for Reminders | P1 | T5-001 | A | DONE |
| T5-004 | Notification Service | P1 | T5-001 | A | DONE |
| T5-005 | Recurring Task Service | P1 | T5-001 | A | DONE |
| T5-006 | Audit Service | P2 | T5-001 | A | DONE |
| T5-007 | Kafka Infrastructure (Strimzi) | P1 | - | B | DONE |
| T5-008 | Dapr Component Configs | P1 | - | B | DONE |
| T5-009 | Update Helm Charts | P1 | T5-004-008 | B | DONE |
| T5-010 | Build Docker Images | P1 | T5-004-006 | B | DONE |
| T5-011 | Minikube Deploy Script | P1 | T5-009-010 | B | DONE |
| T5-012 | OKE Setup Docs | P1 | - | C | DONE |
| T5-013 | Oracle Helm Values | P1 | T5-009,012 | C | DONE |
| T5-014 | CI/CD Pipeline | P2 | T5-013 | C | DONE |
| T5-015 | Monitoring & Logging | P3 | T5-004-006 | C | DONE |

**All 15 tasks completed.** Phase 5 implementation is finished.
