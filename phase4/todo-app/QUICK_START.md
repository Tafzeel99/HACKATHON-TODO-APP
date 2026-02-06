# Quick Start - Deploy to Minikube 🚀

Fast deployment guide for local Kubernetes with Minikube.

---

## ⚠️ Prerequisites

**IMPORTANT**: Before deploying, update `values.yaml` with your Neon PostgreSQL database URL:

```yaml
backend:
  secrets:
    DATABASE_URL: "postgresql://user:password@host.neon.tech/dbname?sslmode=require"
```

This should be the same database used in Phase 2 and Phase 3 for data consistency.

---

## ⚡ Quick Deploy (5 Commands)

```bash
# 1. Load images into Minikube
minikube image load todo-backend:4.0.0
minikube image load todo-frontend:4.0.0

# 2. Install Helm chart (after configuring DATABASE_URL in values.yaml)
cd /mnt/d/IT\ CLASSES\ pc/HACKATHON-TODO-APP/phase4/todo-app
helm install todo-app .

# 3. Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=todo-app --timeout=300s

# 4. Set up port forwarding for ChatKit
kubectl port-forward svc/todo-app-frontend 3000:3000 &
kubectl port-forward svc/todo-app-backend 8000:8000 &

# 5. Open in browser
echo "Access: http://127.0.0.1:3000"
```

---

## 🔍 Verify Deployment

```bash
# Check pods
kubectl get pods -l app.kubernetes.io/instance=todo-app

# Check services
kubectl get svc -l app.kubernetes.io/instance=todo-app

# Test backend
curl http://127.0.0.1:8000/health

# Test frontend
curl -I http://127.0.0.1:3000
```

---

## 🌐 Access Points

**With Port Forwarding** (Recommended for ChatKit):
- Frontend: http://127.0.0.1:3000
- Chat: http://127.0.0.1:3000/chat
- Backend API: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

**With NodePort** (Direct Minikube access):
```bash
minikube ip  # Get Minikube IP (e.g., 192.168.49.2)
```
- Frontend: http://192.168.49.2:30030
- Backend: http://192.168.49.2:30080/docs

---

## 📊 Monitoring

```bash
# View all resources
kubectl get all -l app.kubernetes.io/instance=todo-app

# View logs (live)
kubectl logs -l app.kubernetes.io/component=backend -f
kubectl logs -l app.kubernetes.io/component=frontend -f

# Check resource usage
kubectl top pods -l app.kubernetes.io/instance=todo-app
```

---

## 🐛 Troubleshooting

**Pods not starting?**
```bash
# Check pod status
kubectl describe pod -l app.kubernetes.io/instance=todo-app

# Check events
kubectl get events --sort-by=.metadata.creationTimestamp
```

**ImagePullBackOff error?**
```bash
# Reload images
minikube image load todo-backend:4.0.0
minikube image load todo-frontend:4.0.0

# Restart pods
kubectl rollout restart deployment todo-app-backend
kubectl rollout restart deployment todo-app-frontend
```

**Port forwarding stopped?**
```bash
# Kill old port forwards
pkill -f "port-forward"

# Restart
kubectl port-forward svc/todo-app-frontend 3000:3000 &
kubectl port-forward svc/todo-app-backend 8000:8000 &
```

---

## 🔄 Update

```bash
# Upgrade deployment
helm upgrade todo-app .

# Rollback if needed
helm rollback todo-app
```

---

## 🗑️ Cleanup

```bash
# Uninstall
helm uninstall todo-app

# Verify removal
kubectl get all -l app.kubernetes.io/instance=todo-app

# Stop port forwarding
pkill -f "port-forward"
```

---

## 📚 Full Documentation

For detailed instructions, see:
- `DEPLOYMENT_GUIDE.md` - Complete deployment guide
- `values.yaml` - Configuration reference
- `../RUNNING_CONTAINERS.md` - Container documentation

---

**Ready to deploy! 🎉**
