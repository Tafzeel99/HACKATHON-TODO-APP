# Oracle OKE Setup Guide (Always Free Tier)

## Why Oracle?

- **Always Free**: 4 OCPUs, 24GB RAM - no charges after trial
- **No credit card charge**: After 30-day trial, free tier resources remain
- Best for learning Kubernetes without time/cost pressure

## Step 1: Create Oracle Cloud Account

1. Go to https://www.oracle.com/cloud/free/
2. Sign up with email, set home region (choose closest)
3. You get $300 credits for 30 days + Always Free resources

## Step 2: Create Compartment

```bash
# In Oracle Cloud Console:
# Identity & Security > Compartments > Create Compartment
# Name: todo-app
# Description: Phase 5 Todo Application
```

## Step 3: Create OKE Cluster

1. **Oracle Cloud Console** > Developer Services > Kubernetes Clusters (OKE)
2. Click **Create Cluster** > **Quick Create**
3. Configure:
   - **Name**: todo-app-cluster
   - **Compartment**: todo-app
   - **Kubernetes version**: Latest stable
   - **Node shape**: VM.Standard.A1.Flex (Always Free - ARM)
   - **OCPUs per node**: 2
   - **Memory per node**: 12 GB
   - **Number of nodes**: 2 (total: 4 OCPUs, 24GB RAM)
   - **Network**: Create new VCN

4. Click **Create Cluster** (takes ~10 minutes)

## Step 4: Configure kubectl

```bash
# Install OCI CLI
bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"

# Configure OCI CLI
oci setup config

# Set up kubeconfig
oci ce cluster create-kubeconfig \
    --cluster-id <your-cluster-ocid> \
    --file $HOME/.kube/config \
    --region <your-region> \
    --token-version 2.0.0 \
    --kube-endpoint PUBLIC_ENDPOINT

# Verify connection
kubectl get nodes
```

## Step 5: Set Up Oracle Container Registry (OCIR)

```bash
# 1. Generate Auth Token
# Oracle Console > Identity > Users > Your User > Auth Tokens > Generate Token
# Save the token - you won't see it again!

# 2. Login to OCIR
docker login <region-key>.ocir.io
# Username: <tenancy-namespace>/<username>
# Password: <auth-token>

# Region keys:
# us-ashburn-1 = iad
# us-phoenix-1 = phx
# ap-mumbai-1 = bom
# ap-singapore-1 = sin
# etc.

# 3. Create Kubernetes secret for OCIR pulling
kubectl create secret docker-registry ocir-secret \
    --docker-server=<region>.ocir.io \
    --docker-username='<tenancy-namespace>/<username>' \
    --docker-password='<auth-token>' \
    --docker-email='<email>'
```

## Step 6: Push Docker Images to OCIR

```bash
REGION="<region-key>.ocir.io"
NAMESPACE="<tenancy-namespace>"

# Tag and push all images
for SERVICE in todo-backend todo-frontend todo-notification todo-recurring todo-audit; do
    docker tag ${SERVICE}:5.0.0 ${REGION}/${NAMESPACE}/${SERVICE}:5.0.0
    docker push ${REGION}/${NAMESPACE}/${SERVICE}:5.0.0
done
```

## Step 7: Install Kafka & Dapr on OKE

```bash
# Install Strimzi Kafka Operator
kubectl create namespace kafka
kubectl apply -f "https://strimzi.io/install/latest?namespace=kafka"
kubectl apply -f infra/kafka/kafka-cluster.yaml
kubectl apply -f infra/kafka/kafka-topics.yaml

# Install Dapr
dapr init -k --wait

# Apply Dapr components
kubectl apply -f infra/dapr/components/
```

## Step 8: Deploy Application

```bash
# Update values-oracle.yaml with your OCIR details
# Replace <region>, <tenancy-namespace>, secrets

# Deploy with Helm
helm upgrade --install todo-app ./todo-app/ \
    -f todo-app/values-oracle.yaml \
    --wait --timeout=300s

# Check status
kubectl get pods
kubectl get svc
```

## Step 9: Access Application

```bash
# Get LoadBalancer IPs
kubectl get svc

# Frontend: http://<EXTERNAL-IP>:3000
# Backend:  http://<EXTERNAL-IP>:8000
```

## Resource Budget (Always Free)

| Resource | Allocation | Usage |
|----------|-----------|-------|
| OCPUs | 4 total | Backend (0.5) + Frontend (0.25) + 3 services (0.3) + Kafka (0.5) + Dapr (~0.5) = ~2.05 |
| Memory | 24 GB total | Backend (512M) + Frontend (256M) + 3 services (384M) + Kafka (1G) + Zookeeper (512M) + Dapr (~1G) = ~3.7G |
| Storage | 200 GB block | Ephemeral Kafka storage only |

Plenty of headroom for the Always Free tier.
