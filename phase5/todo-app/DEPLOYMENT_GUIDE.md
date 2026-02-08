# Phase 4 - Kubernetes Deployment Guide

**Helm Chart Version**: 4.0.0
**Application Version**: 4.0.0
**Target**: Local Minikube

---

## 📋 Prerequisites

### Required Tools

✅ **Minikube** - Running
```bash
minikube status
# Expected: host, kubelet, apiserver: Running
```

✅ **kubectl** - Installed and configured
```bash
kubectl version --client
```

✅ **Helm** - Version 3.x
```bash
helm version
# Expected: v3.x.x
```

✅ **Docker Images** - Built locally
```bash
docker images | grep -E "todo-backend|todo-frontend"
# Expected:
# todo-backend:4.0.0
# todo-frontend:4.0.0
```

---

## 🚀 Step-by-Step Deployment

### Step 1: Load Docker Images into Minikube

Since we're using local images (not from a registry), load them into Minikube:

```bash
# Load backend image
minikube image load todo-backend:4.0.0

# Load frontend image
minikube image load todo-frontend:4.0.0
```

**Verify images are loaded**:
```bash
minikube image ls | grep todo
```

Expected output:
```
docker.io/library/todo-backend:4.0.0
docker.io/library/todo-frontend:4.0.0
```

### Step 2: Configure Database Connection

**Update values.yaml with your Neon PostgreSQL credentials:**

```bash
cd /mnt/d/IT\ CLASSES\ pc/HACKATHON-TODO-APP/phase4/todo-app
```

Edit `values.yaml` and update the database URL:

```yaml
backend:
  secrets:
    # Replace with your actual Neon PostgreSQL URL
    DATABASE_URL: "postgresql://user:password@host.neon.tech/dbname?sslmode=require"
```

**Important**: The database URL should match your Phase 2/3 Neon database for data consistency.

### Step 3: Validate Helm Chart

Check for syntax errors:

```bash
helm lint .
```

Expected output:
```
==> Linting .
[INFO] Chart.yaml: icon is recommended
1 chart(s) linted, 0 chart(s) failed
```

### Step 4: Dry Run (Optional but Recommended)

See what will be deployed without actually deploying:

```bash
helm install todo-app . --dry-run --debug
```

This shows all the Kubernetes manifests that will be created.

### Step 5: Install the Helm Chart

```bash
helm install todo-app .
```

Expected output:
```
NAME: todo-app
LAST DEPLOYED: [timestamp]
NAMESPACE: default
STATUS: deployed
REVISION: 1
NOTES:
[Deployment notes with access instructions]
```

### Step 6: Verify Deployment

**Check all resources**:
```bash
kubectl get all -l app.kubernetes.io/instance=todo-app
```

Expected output should show:
- 2 Deployments (backend, frontend)
- 2 Pods (backend, frontend)
- 2 Services (backend, frontend)
- 2 ReplicaSets

**Check pod status**:
```bash
kubectl get pods -l app.kubernetes.io/instance=todo-app
```

Wait until both pods show `Running` and `1/1` ready:
```
NAME                                  READY   STATUS    RESTARTS   AGE
todo-app-backend-xxxx                 1/1     Running   0          2m
todo-app-frontend-xxxx                1/1     Running   0          2m
```

**If pods are not ready**, wait:
```bash
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=todo-app --timeout=300s
```

### Step 7: Check Logs

**Backend logs**:
```bash
kubectl logs -l app.kubernetes.io/component=backend -f
```

**Frontend logs**:
```bash
kubectl logs -l app.kubernetes.io/component=frontend -f
```

Look for:
- ✅ Backend: "Uvicorn running on http://0.0.0.0:8000"
- ✅ Frontend: "Ready in [X]ms"

---

## 🔗 Accessing the Application

### Option 1: NodePort Access (Minikube IP)

**Get Minikube IP**:
```bash
minikube ip
```

Example output: `192.168.49.2`

**Access URLs**:
- Frontend: `http://192.168.49.2:30030`
- Backend: `http://192.168.49.2:30080/docs`

⚠️ **Note**: This won't work with ChatKit (ChatKit requires 127.0.0.1)

### Option 2: Port Forwarding (Recommended for ChatKit)

**Set up port forwarding**:

```bash
# Forward frontend
kubectl port-forward svc/todo-app-frontend 3000:3000 &

# Forward backend
kubectl port-forward svc/todo-app-backend 8000:8000 &
```

**Access URLs**:
- Frontend: http://127.0.0.1:3000
- AI Chat: http://127.0.0.1:3000/chat
- Backend: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

✅ **This method works with ChatKit!**

### Option 3: Minikube Service (Alternative)

```bash
# Open frontend in browser
minikube service todo-app-frontend

# Open backend in browser
minikube service todo-app-backend
```

This automatically opens the service in your default browser.

---

## 🧪 Testing the Deployment

### 1. Test Backend Health

```bash
# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

# Test health endpoint
curl http://$MINIKUBE_IP:30080/health
```

Expected response:
```json
{"status":"healthy","version":"4.0.0"}
```

Or with port forwarding:
```bash
curl http://127.0.0.1:8000/health
```

### 2. Test Frontend

```bash
# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

# Test frontend
curl -I http://$MINIKUBE_IP:30030
```

Expected: `HTTP/1.1 200 OK`

Or with port forwarding:
```bash
curl -I http://127.0.0.1:3000
```

### 3. Test Full Application Flow

1. **Open browser** (with port forwarding active):
   ```
   http://127.0.0.1:3000
   ```

2. **Register a new account**
3. **Create some tasks**
4. **Test AI chat**:
   ```
   http://127.0.0.1:3000/chat
   ```

---

## 🔧 Managing the Deployment

### View Helm Release

```bash
helm list
```

### View Release Status

```bash
helm status todo-app
```

### Get Deployment Values

```bash
helm get values todo-app
```

### Upgrade Deployment

If you made changes to the chart:

```bash
helm upgrade todo-app .
```

### Rollback Deployment

If something goes wrong:

```bash
# List revisions
helm history todo-app

# Rollback to previous revision
helm rollback todo-app

# Rollback to specific revision
helm rollback todo-app 1
```

### Uninstall Deployment

```bash
helm uninstall todo-app
```

This removes all Kubernetes resources created by the chart.

---

## 📊 Monitoring and Debugging

### View All Resources

```bash
kubectl get all -l app.kubernetes.io/instance=todo-app
```

### Describe Resources

**Backend deployment**:
```bash
kubectl describe deployment todo-app-backend
```

**Frontend deployment**:
```bash
kubectl describe deployment todo-app-frontend
```

**Backend pod**:
```bash
kubectl describe pod -l app.kubernetes.io/component=backend
```

### View Events

```bash
kubectl get events --sort-by=.metadata.creationTimestamp
```

### Check Resource Usage

```bash
kubectl top pods -l app.kubernetes.io/instance=todo-app
```

### Execute Commands in Pods

**Backend shell**:
```bash
kubectl exec -it deploy/todo-app-backend -- /bin/bash
```

**Frontend shell**:
```bash
kubectl exec -it deploy/todo-app-frontend -- /bin/sh
```

### View Environment Variables

**Backend**:
```bash
kubectl exec deploy/todo-app-backend -- env
```

**Frontend**:
```bash
kubectl exec deploy/todo-app-frontend -- env
```

---

## 🐛 Troubleshooting

### Issue: Pods Not Starting

**Check pod status**:
```bash
kubectl get pods -l app.kubernetes.io/instance=todo-app
```

**Check pod events**:
```bash
kubectl describe pod -l app.kubernetes.io/instance=todo-app
```

**Common causes**:
- Image pull errors → Load images into Minikube
- Resource limits too high → Adjust in values.yaml
- Health checks failing → Increase initialDelaySeconds

### Issue: ImagePullBackOff Error

**Problem**: Minikube can't find the Docker images

**Solution**:
```bash
# Load images into Minikube
minikube image load todo-backend:4.0.0
minikube image load todo-frontend:4.0.0

# Restart deployment
kubectl rollout restart deployment todo-app-backend
kubectl rollout restart deployment todo-app-frontend
```

### Issue: CrashLoopBackOff

**Check logs**:
```bash
kubectl logs -l app.kubernetes.io/component=backend --tail=50
kubectl logs -l app.kubernetes.io/component=frontend --tail=50
```

**Common causes**:
- Database connection errors
- Missing environment variables
- Application crashes on startup

**Solution**: Check logs and fix configuration in values.yaml

### Issue: Health Checks Failing

**Symptoms**: Pods restart frequently

**Check**:
```bash
kubectl describe pod -l app.kubernetes.io/instance=todo-app | grep -A 10 Liveness
```

**Solution**: Increase initialDelaySeconds in values.yaml:
```yaml
backend:
  livenessProbe:
    initialDelaySeconds: 60  # Increase from 30
```

### Issue: Port Forwarding Stops

**Restart port forwarding**:
```bash
# Kill existing port forwards
pkill -f "port-forward"

# Start new ones
kubectl port-forward svc/todo-app-frontend 3000:3000 &
kubectl port-forward svc/todo-app-backend 8000:8000 &
```

### Issue: ChatKit Not Working

**Verify**:
1. Using 127.0.0.1 (not minikube IP)
2. Port forwarding is active
3. Domain key is in the frontend image

**Check domain key in image**:
```bash
kubectl exec deploy/todo-app-frontend -- env | grep OPENAI
```

---

## 🔄 Updating the Application

### Update Docker Images

1. **Rebuild images**:
   ```bash
   cd phase4/backend
   docker build -t todo-backend:4.0.1 .

   cd ../frontend
   docker build -t todo-frontend:4.0.1 .
   ```

2. **Load into Minikube**:
   ```bash
   minikube image load todo-backend:4.0.1
   minikube image load todo-frontend:4.0.1
   ```

3. **Update values.yaml**:
   ```yaml
   backend:
     image:
       tag: "4.0.1"
   frontend:
     image:
       tag: "4.0.1"
   ```

4. **Upgrade Helm release**:
   ```bash
   helm upgrade todo-app .
   ```

### Update Configuration

1. **Edit values.yaml** with new configuration

2. **Upgrade**:
   ```bash
   helm upgrade todo-app .
   ```

3. **Verify**:
   ```bash
   kubectl rollout status deployment todo-app-backend
   kubectl rollout status deployment todo-app-frontend
   ```

---

## 📈 Scaling

### Manual Scaling

**Scale backend**:
```bash
kubectl scale deployment todo-app-backend --replicas=3
```

**Scale frontend**:
```bash
kubectl scale deployment todo-app-frontend --replicas=2
```

### Via Helm (Persistent)

Edit values.yaml:
```yaml
backend:
  replicaCount: 3
frontend:
  replicaCount: 2
```

Apply:
```bash
helm upgrade todo-app .
```

### Enable Autoscaling

Edit values.yaml:
```yaml
autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 5
  targetCPUUtilizationPercentage: 80
```

Apply:
```bash
helm upgrade todo-app .
```

---

## 🗑️ Cleanup

### Remove Everything

```bash
# Uninstall Helm release
helm uninstall todo-app

# Verify all resources removed
kubectl get all -l app.kubernetes.io/instance=todo-app

# Stop port forwarding
pkill -f "port-forward"

# Remove images from Minikube (optional)
minikube image rm todo-backend:4.0.0
minikube image rm todo-frontend:4.0.0
```

---

## 📚 Additional Resources

### Helm Commands

- `helm list` - List releases
- `helm status <release>` - Get release status
- `helm get values <release>` - Get values
- `helm history <release>` - Get revision history
- `helm upgrade <release> .` - Upgrade release
- `helm rollback <release>` - Rollback release
- `helm uninstall <release>` - Uninstall release

### Kubectl Commands

- `kubectl get pods` - List pods
- `kubectl logs <pod>` - View pod logs
- `kubectl describe pod <pod>` - Pod details
- `kubectl exec -it <pod> -- /bin/bash` - Shell into pod
- `kubectl port-forward <pod> <local>:<remote>` - Port forward

### Useful Aliases

Add to your `.bashrc` or `.zshrc`:

```bash
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kgd='kubectl get deployments'
alias kl='kubectl logs'
alias kd='kubectl describe'
alias kpf='kubectl port-forward'
```

---

## ✅ Deployment Checklist

- [ ] Minikube is running
- [ ] Docker images are built (backend:4.0.0, frontend:4.0.0)
- [ ] Images loaded into Minikube
- [ ] Helm chart validated (`helm lint`)
- [ ] Helm release installed (`helm install`)
- [ ] Pods are running
- [ ] Health checks passing
- [ ] Port forwarding configured
- [ ] Frontend accessible at http://127.0.0.1:3000
- [ ] Backend accessible at http://127.0.0.1:8000
- [ ] ChatKit working at http://127.0.0.1:3000/chat

---

**Your Todo App is now running on Kubernetes! 🎉**
