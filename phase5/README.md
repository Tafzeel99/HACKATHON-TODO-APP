# Phase 5 - Complete Setup Guide

**Event-Driven Todo App with Kafka + Dapr on Kubernetes**

---

## Prerequisites

Install these tools before starting:

```bash
# Check versions
python --version      # 3.13+
node --version        # 18+
docker --version      # Docker Desktop running
minikube version      # 1.32+
kubectl version       # 1.28+
helm version          # 3.14+
dapr version          # 1.12+ (install: brew install dapr/tap/dapr-cli)
```

---

## Option 1: Quick Setup (One Command)

```bash
cd phase5
chmod +x deploy-minikube.sh
./deploy-minikube.sh
```

Wait ~5-10 minutes. Done! Skip to [Access Application](#access-application).

---

## Option 2: Manual Setup (Step-by-Step)

### Step 1: Start Minikube

```bash
# Start with 4 CPUs and 8GB RAM
minikube start --cpus=4 --memory=8192 --driver=docker

# Use Minikube's Docker daemon
eval $(minikube docker-env)
```

### Step 2: Install Kafka (Strimzi)

```bash
# Create namespace and install operator
kubectl create namespace kafka
kubectl apply -f "https://strimzi.io/install/latest?namespace=kafka" -n kafka

# Wait for operator (1-2 min)
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=120s

# Deploy Kafka cluster (2-3 min)
kubectl apply -f infra/kafka/kafka-cluster.yaml
kubectl wait kafka/taskflow-kafka --for=condition=Ready -n kafka --timeout=300s

# Create topics
kubectl apply -f infra/kafka/kafka-topics.yaml
```

### Step 3: Install Dapr

```bash
# Initialize Dapr on Kubernetes
dapr init -k --wait

# Verify
dapr status -k

# Apply Dapr components
kubectl apply -f infra/dapr/components/
```

### Step 4: Build Docker Images

```bash
cd phase5

# Backend
docker build -t todo-backend:5.0.0 ./backend/

# Frontend (with Minikube IP)
docker build -t todo-frontend:5.0.0 ./frontend/ \
    --build-arg NEXT_PUBLIC_API_URL="http://$(minikube ip):30080" \
    --build-arg NEXT_PUBLIC_OPENAI_DOMAIN_KEY="your-chatkit-domain-key"

# Microservices
docker build -t todo-notification:5.0.0 ./notification-service/
docker build -t todo-recurring:5.0.0 ./recurring-task-service/
docker build -t todo-audit:5.0.0 ./audit-service/
```

### Step 5: Configure Secrets

Edit `todo-app/values.yaml` with your credentials:

```yaml
backend:
  secrets:
    DATABASE_URL: "postgresql://user:pass@host/dbname"  # Your Neon DB URL
    OPEN_ROUTER_KEY: "sk-or-v1-xxxxx"                   # Your OpenRouter key
```

### Step 6: Deploy with Helm

```bash
helm upgrade --install todo-app ./todo-app/ \
    --set backend.image.tag=5.0.0 \
    --set frontend.image.tag=5.0.0 \
    --set notificationService.image.tag=5.0.0 \
    --set recurringTaskService.image.tag=5.0.0 \
    --set auditService.image.tag=5.0.0 \
    --wait --timeout=300s
```

### Step 7: Verify Deployment

```bash
# Check all pods are running (2/2 = app + Dapr sidecar)
kubectl get pods

# Expected output:
# NAME                                    READY   STATUS    RESTARTS   AGE
# todo-app-audit-xxxxx                    2/2     Running   0          1m
# todo-app-backend-xxxxx                  2/2     Running   0          1m
# todo-app-frontend-xxxxx                 2/2     Running   0          1m
# todo-app-notification-xxxxx             2/2     Running   0          1m
# todo-app-recurring-xxxxx                2/2     Running   0          1m

# Check services
kubectl get svc
```

---

## Access Application

```bash
# Get Minikube IP
echo "Frontend: http://$(minikube ip):30030"
echo "Backend:  http://$(minikube ip):30080"
echo "API Docs: http://$(minikube ip):30080/docs"

# Open Dapr Dashboard
dapr dashboard -k
```

---

## Oracle Cloud Deployment (OKE)

### Step 1: Create Oracle Account

1. Go to https://oracle.com/cloud/free
2. Sign up (get $300 credits + Always Free tier)

### Step 2: Create OKE Cluster

```
Oracle Console → Developer Services → Kubernetes Clusters (OKE)
→ Create Cluster → Quick Create

Settings:
- Name: todo-app-cluster
- Shape: VM.Standard.A1.Flex (Always Free ARM)
- OCPUs: 2 per node
- Memory: 12 GB per node
- Nodes: 2
```

### Step 3: Configure kubectl

```bash
# Install OCI CLI
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"

# Configure
oci setup config

# Get kubeconfig
oci ce cluster create-kubeconfig \
    --cluster-id <cluster-ocid> \
    --file $HOME/.kube/config \
    --region <region> \
    --token-version 2.0.0 \
    --kube-endpoint PUBLIC_ENDPOINT

# Verify
kubectl get nodes
```

### Step 4: Setup Container Registry (OCIR)

```bash
# Generate auth token: Oracle Console → Identity → Users → Auth Tokens → Generate

# Login to OCIR
docker login <region>.ocir.io
# Username: <tenancy-namespace>/<username>
# Password: <auth-token>

# Create K8s secret for pulling images
kubectl create secret docker-registry ocir-secret \
    --docker-server=<region>.ocir.io \
    --docker-username='<tenancy-namespace>/<username>' \
    --docker-password='<auth-token>' \
    --docker-email='<email>'
```

### Step 5: Build & Push Images

```bash
REGION="<region>.ocir.io"
NAMESPACE="<tenancy-namespace>"

# Build for ARM64 (Oracle Always Free uses ARM)
docker buildx build --platform linux/arm64 -t ${REGION}/${NAMESPACE}/todo-backend:5.0.0 ./backend/ --push
docker buildx build --platform linux/arm64 -t ${REGION}/${NAMESPACE}/todo-frontend:5.0.0 ./frontend/ --push
docker buildx build --platform linux/arm64 -t ${REGION}/${NAMESPACE}/todo-notification:5.0.0 ./notification-service/ --push
docker buildx build --platform linux/arm64 -t ${REGION}/${NAMESPACE}/todo-recurring:5.0.0 ./recurring-task-service/ --push
docker buildx build --platform linux/arm64 -t ${REGION}/${NAMESPACE}/todo-audit:5.0.0 ./audit-service/ --push
```

### Step 6: Install Kafka & Dapr on OKE

```bash
# Kafka
kubectl create namespace kafka
kubectl apply -f "https://strimzi.io/install/latest?namespace=kafka"
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s
kubectl apply -f infra/kafka/kafka-cluster.yaml
kubectl wait kafka/taskflow-kafka --for=condition=Ready -n kafka --timeout=300s
kubectl apply -f infra/kafka/kafka-topics.yaml

# Dapr
dapr init -k --wait
kubectl apply -f infra/dapr/components/
```

### Step 7: Update values-oracle.yaml

```yaml
# Edit todo-app/values-oracle.yaml
backend:
  image:
    repository: <region>.ocir.io/<namespace>/todo-backend
    pullPolicy: Always
    tag: "5.0.0"
  secrets:
    DATABASE_URL: "your-neon-db-url"
    OPEN_ROUTER_KEY: "your-openrouter-key"

imagePullSecrets:
  - name: ocir-secret
```

### Step 8: Deploy to OKE

```bash
helm upgrade --install todo-app ./todo-app/ \
    -f todo-app/values-oracle.yaml \
    --wait --timeout=300s

# Get external IPs
kubectl get svc
# Access via LoadBalancer EXTERNAL-IP
```

---

## Local Development (Without Kubernetes)

```bash
# Terminal 1: Backend
cd phase5/backend
uv sync
cp .env.example .env  # Edit with your credentials
uv run alembic upgrade head
uv run uvicorn src.main:app --reload --port 8000

# Terminal 2: Frontend
cd phase5/frontend
npm install
cp .env.example .env  # Set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Access: http://localhost:3000

---

## Environment Variables

### Backend (.env)

```env
DATABASE_URL=postgresql://user:pass@host/dbname
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
OPEN_ROUTER_KEY=sk-or-v1-xxxxx
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=openai/gpt-4o-mini
CORS_ORIGINS=["http://localhost:3000"]
DAPR_ENABLED=true
DAPR_HTTP_PORT=3500
```

### Frontend (.env)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-chatkit-domain-key
```

---

## Useful Commands

```bash
# View logs
kubectl logs -l app=todo-app-backend -f
kubectl logs -l app=todo-app-notification -f

# Restart deployment
kubectl rollout restart deployment todo-app-backend

# Check Kafka topics
kubectl get kafkatopics -n kafka

# Check Dapr components
dapr components -k

# Port forward for debugging
kubectl port-forward svc/todo-app-backend 8000:8000

# Delete everything
helm uninstall todo-app
kubectl delete namespace kafka
dapr uninstall -k
minikube stop
```

---

## Troubleshooting

### Pods not starting

```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name> -c daprd  # Dapr sidecar logs
```

### Kafka not ready

```bash
kubectl get pods -n kafka
kubectl logs -l strimzi.io/name=taskflow-kafka-kafka -n kafka
```

### Events not publishing

```bash
# Check DAPR_ENABLED is true
kubectl get configmap todo-app-backend-config -o yaml

# Watch for events
kubectl exec -it taskflow-kafka-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic task-events \
    --from-beginning
```

### Image pull errors (Oracle)

```bash
# Verify secret exists
kubectl get secret ocir-secret

# Check image path matches values-oracle.yaml
kubectl describe pod <pod-name> | grep Image
```

---

## Services & Ports

| Service | Port | NodePort | Description |
|---------|------|----------|-------------|
| Frontend | 3000 | 30030 | Next.js UI |
| Backend | 8000 | 30080 | FastAPI + MCP |
| Notification | 8001 | - | Reminder handler |
| Recurring Task | 8002 | - | Auto-create next task |
| Audit | 8003 | - | Activity log |
| Kafka | 9092 | - | Event broker |

---

## Architecture

```
User → Frontend (Next.js) → Backend (FastAPI + MCP Tools)
                                    ↓
                            Dapr Pub/Sub → Kafka
                                    ↓
            ┌───────────────────────┼───────────────────────┐
            ↓                       ↓                       ↓
    Notification           Recurring Task              Audit
    Service                Service                     Service
    (reminders)            (auto-create)               (activity log)
```

---

## Done!

Your Phase 5 event-driven todo app is now running on Kubernetes with:
- Kafka for event streaming
- Dapr for infrastructure abstraction
- 3 new microservices (Notification, Recurring Task, Audit)
- Full CI/CD pipeline ready

Access your app at `http://$(minikube ip):30030`
