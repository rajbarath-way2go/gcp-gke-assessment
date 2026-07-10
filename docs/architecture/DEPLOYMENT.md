# GKE Assessment: Deployment & Setup Guide

**Project**: `sre-gke-assessment`  
**Region**: `us-central1`  
**Zone**: `us-central1-a`

---

## Prerequisites

- Active GCP account with billing enabled
- `gcloud` CLI installed and authenticated
- `kubectl` installed
- Docker installed (for building images)
- `git` for version control
- Terraform (for IaC deployment)

### Quick Check
```bash
gcloud auth list
gcloud config list --format='value(core.project)'
kubectl version --client
docker version
terraform version
```

---

## Phase 1: Project Setup & IAM

### 1.1 Create GCP Project
```bash
PROJECT_ID="sre-gke-assessment"
gcloud projects create $PROJECT_ID --name="SRE GKE Assessment"
gcloud config set project $PROJECT_ID
```

### 1.2 Link Billing Account
```bash
# List billing accounts
gcloud billing accounts list

# Link to project
BILLING_ACCOUNT_ID="XXXXX"  # Replace with your account ID
gcloud billing projects link $PROJECT_ID \
  --billing-account=$BILLING_ACCOUNT_ID
```

### 1.3 Enable Required APIs
```bash
gcloud services enable \
  compute.googleapis.com \
  container.googleapis.com \
  artifactregistry.googleapis.com \
  bigquery.googleapis.com \
  logging.googleapis.com \
  secretmanager.googleapis.com
```

### 1.4 Create Service Accounts
```bash
# Service account for app-alpha
gcloud iam service-accounts create app-alpha-sa \
  --display-name="Service account for app-alpha"

# Service account for app-beta
gcloud iam service-accounts create app-beta-sa \
  --display-name="Service account for app-beta"

# Grant BigQuery and Secret Manager roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:app-alpha-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataViewer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:app-beta-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataViewer"
```

---

## Phase 2: Networking

### 2.1 Create Custom VPC
```bash
VPC_NAME="gke-vpc"
REGION="us-central1"

gcloud compute networks create $VPC_NAME \
  --subnet-mode=custom
```

### 2.2 Create Subnet with Secondary Ranges
```bash
SUBNET_NAME="gke-nodes-subnet"
PRIMARY_RANGE="10.10.0.0/20"
PODS_RANGE="10.20.0.0/16"
SERVICES_RANGE="10.30.0.0/20"

gcloud compute networks subnets create $SUBNET_NAME \
  --network=$VPC_NAME \
  --region=$REGION \
  --range=$PRIMARY_RANGE \
  --secondary-range pods=$PODS_RANGE,services=$SERVICES_RANGE
```

### 2.3 Create Cloud Router & Cloud NAT
```bash
ROUTER_NAME="gke-router"
NAT_NAME="gke-nat"

gcloud compute routers create $ROUTER_NAME \
  --network=$VPC_NAME \
  --region=$REGION

gcloud compute routers nats create $NAT_NAME \
  --router=$ROUTER_NAME \
  --region=$REGION \
  --nat-all-subnet-ip-ranges \
  --auto-allocate-nat-external-ips
```

### 2.4 Create Firewall Rules
```bash
# Allow internal traffic
gcloud compute firewall-rules create allow-internal \
  --network=$VPC_NAME \
  --allow=tcp,udp,icmp \
  --source-ranges=10.10.0.0/20,10.20.0.0/16,10.30.0.0/20

# Allow SSH
gcloud compute firewall-rules create allow-ssh \
  --network=$VPC_NAME \
  --allow=tcp:22 \
  --source-ranges=0.0.0.0/0

# Allow ICMP
gcloud compute firewall-rules create allow-icmp \
  --network=$VPC_NAME \
  --allow=icmp \
  --source-ranges=0.0.0.0/0
```

---

## Phase 3: GKE Cluster Provisioning

### 3.1 Create GKE Cluster
```bash
CLUSTER_NAME="assessment-cluster"
ZONE="us-central1-a"
NODE_COUNT=2
MACHINE_TYPE="e2-medium"

gcloud container clusters create $CLUSTER_NAME \
  --zone=$ZONE \
  --num-nodes=$NODE_COUNT \
  --machine-type=$MACHINE_TYPE \
  --network=$VPC_NAME \
  --subnetwork=$SUBNET_NAME \
  --cluster-secondary-range-name=pods \
  --services-secondary-range-name=services \
  --enable-ip-alias \
  --enable-workload-identity \
  --workload-pool=$PROJECT_ID.svc.id.goog \
  --addons=HorizontalPodAutoscaling,HttpLoadBalancing \
  --enable-stackdriver-kubernetes
```

### 3.2 Get Cluster Credentials
```bash
gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE
```

### 3.3 Verify Cluster
```bash
kubectl cluster-info
kubectl get nodes
kubectl get namespaces
```

---

## Phase 4: Artifact Registry & Container Images

### 4.1 Create Artifact Registry Repository
```bash
REGISTRY_REPO="gee-assessment-repo"

gcloud artifacts repositories create $REGISTRY_REPO \
  --repository-format=docker \
  --location=$REGION \
  --description="Docker images for GKE assessment"
```

### 4.2 Configure Docker Authentication
```bash
gcloud auth configure-docker $REGION-docker.pkg.dev
```

### 4.3 Build & Push Images
```bash
IMAGE_URI_ALPHA="$REGION-docker.pkg.dev/$PROJECT_ID/$REGISTRY_REPO/app-alpha:latest"
IMAGE_URI_BETA="$REGION-docker.pkg.dev/$PROJECT_ID/$REGISTRY_REPO/app-beta:latest"

# Build with platform specification
docker build --platform linux/amd64 -t app-alpha:latest ./flask-apps/app-alpha
docker tag app-alpha:latest $IMAGE_URI_ALPHA
docker push $IMAGE_URI_ALPHA

docker build --platform linux/amd64 -t app-beta:latest ./flask-apps/app-beta
docker tag app-beta:latest $IMAGE_URI_BETA
docker push $IMAGE_URI_BETA
```

### 4.4 Grant Node Service Account Access to Images
```bash
NODE_SA="${PROJECT_ID}-compute@developer.gserviceaccount.com"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$NODE_SA" \
  --role="roles/artifactregistry.reader"
```

---

## Phase 5: Kubernetes Application Deployment

### 5.1 Create Namespace
```bash
kubectl create namespace assessment-apps
```

### 5.2 Create Kubernetes Service Accounts
```bash
kubectl create serviceaccount app-alpha-ksa -n assessment-apps
kubectl create serviceaccount app-beta-ksa -n assessment-apps
```

### 5.3 Bind Kubernetes SA to GCP SA (Workload Identity)
```bash
# For app-alpha
gcloud iam service-accounts add-iam-policy-binding \
  app-alpha-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/iam.workloadIdentityUser \
  --member="serviceAccount:$PROJECT_ID.svc.id.goog[assessment-apps/app-alpha-ksa]"

kubectl annotate serviceaccount app-alpha-ksa -n assessment-apps \
  iam.gke.io/gcp-service-account=app-alpha-sa@$PROJECT_ID.iam.gserviceaccount.com

# For app-beta
gcloud iam service-accounts add-iam-policy-binding \
  app-beta-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/iam.workloadIdentityUser \
  --member="serviceAccount:$PROJECT_ID.svc.id.goog[assessment-apps/app-beta-ksa]"

kubectl annotate serviceaccount app-beta-ksa -n assessment-apps \
  iam.gke.io/gcp-service-account=app-beta-sa@$PROJECT_ID.iam.gserviceaccount.com
```

### 5.4 Deploy Applications
```bash
# Apply deployment manifests
kubectl apply -f kubernetes/deployments/app-alpha.yaml
kubectl apply -f kubernetes/deployments/app-beta.yaml
kubectl apply -f kubernetes/services/app-alpha-service.yaml
kubectl apply -f kubernetes/services/app-beta-service.yaml

# Verify deployments
kubectl get deployments -n assessment-apps
kubectl get pods -n assessment-apps
kubectl get services -n assessment-apps
```

---

## Phase 6: Traffic Management & Ingress

### 6.1 Reserve Global Static IP
```bash
STATIC_IP="assessment-ip"

gcloud compute addresses create $STATIC_IP \
  --global \
  --ip-version=IPV4
```

### 6.2 Get IP Address
```bash
EXTERNAL_IP=$(gcloud compute addresses describe $STATIC_IP --global \
  --format="value(address)")
echo "Static IP: $EXTERNAL_IP"
```

### 6.3 Create BackendConfig for Custom Health Checks
```bash
kubectl apply -f kubernetes/backendconfig.yaml
```

**backendconfig.yaml**:
```yaml
apiVersion: cloud.google.com/v1
kind: BackendConfig
metadata:
  name: app-alpha-backendconfig
  namespace: assessment-apps
spec:
  healthCheck:
    checkIntervalSec: 15
    timeoutSec: 5
    healthyThreshold: 1
    unhealthyThreshold: 3
    type: HTTP
    requestPath: /health
    port: 8080
---
apiVersion: cloud.google.com/v1
kind: BackendConfig
metadata:
  name: app-beta-backendconfig
  namespace: assessment-apps
spec:
  healthCheck:
    checkIntervalSec: 15
    timeoutSec: 5
    healthyThreshold: 1
    unhealthyThreshold: 3
    type: HTTP
    requestPath: /health
    port: 8080
```

### 6.4 Update Services with BackendConfig Annotation
```yaml
apiVersion: v1
kind: Service
metadata:
  name: app-alpha-service
  namespace: assessment-apps
  annotations:
    cloud.google.com/backend-config: '{"default": "app-alpha-backendconfig"}'
spec:
  type: ClusterIP
  selector:
    app: app-alpha
  ports:
  - port: 80
    targetPort: 8080
```

### 6.5 Create Ingress
```bash
kubectl apply -f kubernetes/ingress.yaml
```

**ingress.yaml**:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: assessment-ingress
  namespace: assessment-apps
spec:
  rules:
  - http:
      paths:
      - path: /alpha/*
        pathType: ImplementationSpecific
        backend:
          service:
            name: app-alpha-service
            port:
              number: 80
      - path: /beta/*
        pathType: ImplementationSpecific
        backend:
          service:
            name: app-beta-service
            port:
              number: 80
```

### 6.6 Verify Ingress
```bash
kubectl get ingress -n assessment-apps
kubectl describe ingress assessment-ingress -n assessment-apps
```

### 6.7 Test Endpoints
```bash
curl http://$EXTERNAL_IP/alpha/api/data
curl http://$EXTERNAL_IP/beta/api/process
curl http://$EXTERNAL_IP/alpha/api/error
```

---

## Phase 7: Observability Setup

### 7.1 Create BigQuery Dataset
```bash
DATASET_ID="logs_dataset"

bq mk --dataset \
  --description="Exported logs from GKE cluster" \
  $DATASET_ID
```

### 7.2 Create Cloud Logging Sink
```bash
SINK_NAME="k8s-logs-to-bq"

gcloud logging sinks create $SINK_NAME \
  bigquery.googleapis.com/projects/$PROJECT_ID/datasets/$DATASET_ID \
  --log-filter='resource.type="k8s_container" AND resource.labels.namespace_name="assessment-apps"'
```

### 7.3 Grant Sink Service Account Permissions
```bash
# Get sink service account
SINK_SA=$(gcloud logging sinks describe $SINK_NAME --format='value(writerIdentity)')

# Grant BigQuery access
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=$SINK_SA \
  --role=roles/bigquery.dataEditor
```

### 7.4 Deploy Prometheus (via Helm)
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

kubectl create namespace monitoring
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --values kubernetes/prometheus-values.yaml
```

### 7.5 Deploy Grafana (via Helm)
```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm install grafana grafana/grafana \
  --namespace monitoring \
  --values kubernetes/grafana-values.yaml
```

### 7.6 Access Grafana
```bash
# Get Grafana admin password
kubectl get secret -n monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode

# Port forward
kubectl port-forward -n monitoring svc/grafana 3000:80

# Access: http://localhost:3000
# Login: admin / [password from above]
```

### 7.7 Configure Grafana Data Sources
- **Prometheus**: `http://prometheus-kube-prom-prometheus:9090` (in-cluster)
- **BigQuery**: Use BigQuery plugin, provide project ID and credentials

---

## Phase 8: Verification & Testing

### 8.1 Verify All Resources
```bash
# Cluster
kubectl cluster-info
kubectl get nodes

# Namespaces
kubectl get namespaces

# Deployments
kubectl get deployments -A

# Services
kubectl get services -A

# Pods
kubectl get pods -A

# Ingress
kubectl get ingress -A

# VPC resources
gcloud compute networks list
gcloud compute networks subnets list --network=$VPC_NAME
gcloud compute routers list
gcloud compute addresses list

# Artifact Registry
gcloud artifacts docker images list $REGION-docker.pkg.dev/$PROJECT_ID/$REGISTRY_REPO
```

### 8.2 Test API Endpoints
```bash
EXTERNAL_IP=$(gcloud compute addresses describe $STATIC_IP --global \
  --format="value(address)")

# Test app-alpha
curl http://$EXTERNAL_IP/alpha/api/data
curl http://$EXTERNAL_IP/alpha/api/error
curl http://$EXTERNAL_IP/alpha/health

# Test app-beta
curl http://$EXTERNAL_IP/beta/api/process
curl http://$EXTERNAL_IP/beta/api/error
curl http://$EXTERNAL_IP/beta/health

# Generate load for metrics
for i in {1..100}; do
  curl -s http://$EXTERNAL_IP/alpha/api/data > /dev/null
  curl -s http://$EXTERNAL_IP/beta/api/process > /dev/null
  curl -s http://$EXTERNAL_IP/alpha/api/error > /dev/null
  curl -s http://$EXTERNAL_IP/beta/api/error > /dev/null
done
```

### 8.3 Query BigQuery Logs
```bash
bq query --use_legacy_sql=false '
SELECT
  timestamp,
  resource.labels.pod_name,
  severity,
  text_payload
FROM `sre-gke-assessment.logs_dataset.*`
WHERE resource.type = "k8s_container"
  AND TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), timestamp, HOUR) < 1
ORDER BY timestamp DESC
LIMIT 50
'
```

### 8.4 Check Prometheus Metrics
```bash
# Port forward Prometheus
kubectl port-forward -n monitoring svc/prometheus-kube-prom-prometheus 9090:9090

# Access: http://localhost:9090
# Query examples:
# - node_cpu_seconds_total
# - container_memory_usage_bytes
# - rate(http_requests_total[5m])
```

---

## Cleanup

### Delete All Resources
```bash
# Delete Kubernetes resources
kubectl delete namespace assessment-apps
kubectl delete namespace monitoring

# Delete GKE cluster
gcloud container clusters delete $CLUSTER_NAME --zone=$ZONE

# Delete VPC resources
gcloud compute firewall-rules delete allow-internal allow-ssh allow-icmp
gcloud compute routers nats delete $NAT_NAME --router=$ROUTER_NAME --region=$REGION
gcloud compute routers delete $ROUTER_NAME --region=$REGION
gcloud compute networks subnets delete $SUBNET_NAME --region=$REGION
gcloud compute networks delete $VPC_NAME

# Delete static IP
gcloud compute addresses delete $STATIC_IP --global

# Delete Artifact Registry
gcloud artifacts repositories delete $REGISTRY_REPO --location=$REGION

# Delete BigQuery dataset
bq rm -d -r $DATASET_ID

# Delete service accounts
gcloud iam service-accounts delete app-alpha-sa@$PROJECT_ID.iam.gserviceaccount.com
gcloud iam service-accounts delete app-beta-sa@$PROJECT_ID.iam.gserviceaccount.com

# Delete project (optional)
gcloud projects delete $PROJECT_ID
```

---

## Troubleshooting

### Pod not starting
```bash
kubectl describe pod <pod-name> -n assessment-apps
kubectl logs <pod-name> -n assessment-apps
```

### Ingress not routing traffic
```bash
kubectl describe ingress assessment-ingress -n assessment-apps
gcloud compute backend-services list
gcloud compute health-checks list
```

### Logs not appearing in BigQuery
```bash
# Verify sink
gcloud logging sinks describe k8s-logs-to-bq

# Check sink filter
gcloud logging read "resource.type=k8s_container" --limit 10
```

### Image pull errors
```bash
# Check node service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:$NODE_SA"

# Grant access if missing
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$NODE_SA" \
  --role="roles/artifactregistry.reader"
```

---

## Estimated Costs

| Resource | Estimate | Notes |
|---|---|---|
| GKE Cluster | ~$73/month | Zonal, 2x e2-medium nodes |
| Compute Engine (2 nodes) | ~$60/month | e2-medium: 2 vCPU, 4 GB RAM each |
| Load Balancer | ~$18/month | Global HTTP(S) LB |
| BigQuery | Minimal | First 1 TB/month free |
| Cloud Logging | Minimal | Free tier: 50 GB/month |
| **Total** | **~$150/month** | Subject to region/usage |

Free trial credit should cover initial testing period.

---

## Next Steps

1. Run full deployment (all phases)
2. Test API endpoints
3. Verify Grafana dashboards
4. Query BigQuery logs
5. Document any customizations
6. Commit Terraform IaC to Git
7. Archive dashboards and configurations
