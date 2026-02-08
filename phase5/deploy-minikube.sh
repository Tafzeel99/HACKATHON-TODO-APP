#!/bin/bash
# Phase 5 - Minikube Deployment Script
# Deploys the full event-driven todo app with Kafka + Dapr on Minikube
set -e

echo "============================================"
echo "  Phase 5: Minikube Full Deployment"
echo "  Kafka + Dapr + Todo App Microservices"
echo "============================================"

# --- Step 1: Start Minikube ---
echo ""
echo "[1/8] Starting Minikube..."
if minikube status | grep -q "Running"; then
    echo "Minikube is already running."
else
    minikube start --cpus=4 --memory=8192 --driver=docker
fi

# Use Minikube's Docker daemon
eval $(minikube docker-env)

# --- Step 2: Install Strimzi Kafka Operator ---
echo ""
echo "[2/8] Installing Strimzi Kafka Operator..."
kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f "https://strimzi.io/install/latest?namespace=kafka" -n kafka
echo "Waiting for Strimzi operator to be ready..."
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=120s || echo "Strimzi operator still starting, continuing..."

# --- Step 3: Deploy Kafka Cluster ---
echo ""
echo "[3/8] Deploying Kafka cluster..."
kubectl apply -f infra/kafka/kafka-cluster.yaml
echo "Waiting for Kafka cluster to be ready (this may take 2-3 minutes)..."
kubectl wait kafka/taskflow-kafka --for=condition=Ready -n kafka --timeout=300s || echo "Kafka still starting, continuing..."
kubectl apply -f infra/kafka/kafka-topics.yaml

# --- Step 4: Install Dapr ---
echo ""
echo "[4/8] Installing Dapr on Kubernetes..."
if dapr status -k 2>/dev/null | grep -q "Running"; then
    echo "Dapr is already installed."
else
    dapr init -k --wait
fi

# --- Step 5: Apply Dapr Components ---
echo ""
echo "[5/8] Applying Dapr components..."
kubectl apply -f infra/dapr/components/

# --- Step 6: Build Docker Images ---
echo ""
echo "[6/8] Building Docker images..."
echo "Building backend..."
docker build -t todo-backend:5.0.0 ./backend/
echo "Building frontend..."
docker build -t todo-frontend:5.0.0 ./frontend/ \
    --build-arg NEXT_PUBLIC_API_URL="http://$(minikube ip):30080" \
    --build-arg NEXT_PUBLIC_OPENAI_DOMAIN_KEY="domain_pk_696ffdeaf57c8197a912387a3d6cfeec07db6318cdf03509"
echo "Building notification service..."
docker build -t todo-notification:5.0.0 ./notification-service/
echo "Building recurring task service..."
docker build -t todo-recurring:5.0.0 ./recurring-task-service/
echo "Building audit service..."
docker build -t todo-audit:5.0.0 ./audit-service/

# --- Step 7: Deploy with Helm ---
echo ""
echo "[7/8] Deploying with Helm..."
helm upgrade --install todo-app ./todo-app/ \
    --set backend.image.tag=5.0.0 \
    --set frontend.image.tag=5.0.0 \
    --set notificationService.image.tag=5.0.0 \
    --set recurringTaskService.image.tag=5.0.0 \
    --set auditService.image.tag=5.0.0 \
    --wait --timeout=300s

# --- Step 8: Verify Deployment ---
echo ""
echo "[8/8] Verifying deployment..."
echo ""
echo "Pod status:"
kubectl get pods -o wide
echo ""
echo "Services:"
kubectl get svc
echo ""
echo "Dapr components:"
dapr components -k
echo ""

MINIKUBE_IP=$(minikube ip)
echo "============================================"
echo "  Deployment Complete!"
echo "============================================"
echo ""
echo "  Frontend:    http://${MINIKUBE_IP}:30030"
echo "  Backend API: http://${MINIKUBE_IP}:30080"
echo "  Health:      http://${MINIKUBE_IP}:30080/health"
echo ""
echo "  Dapr Dashboard: dapr dashboard -k"
echo "  Kafka Topics:   kubectl get kafkatopics -n kafka"
echo ""
echo "============================================"
