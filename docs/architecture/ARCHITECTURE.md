# GKE Assessment: Architecture & Deployment

**Project**: `sre-gke-assessment`  
**Region**: `us-central1`  
**Zone**: `us-central1-a`  
**Cluster**: `assessment-cluster` (Zonal, Standard mode)

---

## System Architecture Overview

The system comprises:
- **GCP Project**: Billing unit and resource container
- **Custom VPC** (`gke-vpc`): Isolated network with controlled IP ranges
- **GKE Cluster**: Managed Kubernetes control plane + 2x e2-medium nodes
- **Applications**: app-alpha, app-beta (3 replicas each)
- **Global Load Balancer**: Routes external traffic to cluster
- **Observability Stack**: Prometheus, Grafana, BigQuery, Cloud Logging

### Network Architecture

| Component | CIDR Range | Purpose |
|---|---|---|
| Node Primary Range | 10.10.0.0/20 | VM instances |
| Pod Secondary Range | 10.20.0.0/16 | Pod IPs (VPC-native) |
| Service Range | 10.30.0.0/20 | ClusterIP addresses |

**Features**:
- VPC-native (alias IP) networking — direct pod-to-pod routing
- Cloud NAT for outbound-only internet access (no public IPs on nodes/pods)
- Custom firewall rules: internal traffic, SSH, ICMP
- Cloud Router for dynamic route management

---

## Request Flow

```
User Request
    ↓
Global Static IP (136.69.103.171)
    ↓
HTTP(S) Load Balancer (GCE)
    ↓
Ingress Controller (path-based routing: /alpha, /beta)
    ↓
Kubernetes Service (ClusterIP, load-balances replicas)
    ↓
Pod (Flask application)
    ↓
Response → back through chain to user
```

**Health Checks** (independent, parallel):
- kubelet periodically probes `/health` and `/ready` directly on pods
- Load balancer uses BackendConfig to define custom health check path
- Failure blocks traffic even if app logic works

**Logging Pipeline** (independent, parallel):
- Application logs → Cloud Logging
- Cloud Logging sink → BigQuery (for historical queries)
- Prometheus scrapes metrics from nodes/pods

---

## Deployment Architecture

### Phase 1: Project & IAM Setup
- GCP Project: `sre-gke-assessment`
- Billing account linked
- Required APIs enabled:
  - Compute Engine API
  - Kubernetes Engine API
  - Artifact Registry API
  - BigQuery API
  - Cloud Logging API
  - Secret Manager API
- Service Accounts created:
  - `app-alpha-sa` (BigQuery, Secret Manager roles)
  - `app-beta-sa` (BigQuery, Secret Manager roles)

### Phase 2: Custom Networking (gke-vpc)
- **VPC**: Custom mode (not auto)
- **Subnet**: `gke-nodes-subnet` (primary 10.10.0.0/20)
- **Secondary Ranges**:
  - `gke-pods`: 10.20.0.0/16
  - `gke-services`: 10.30.0.0/20
- **Cloud Router + Cloud NAT**: Outbound internet access
- **Firewall Rules**:
  - Allow internal traffic (nodes ↔ pods ↔ services)
  - Allow SSH for debugging
  - Allow ICMP for diagnostics

### Phase 3: GKE Cluster Provisioning
- **Cluster Type**: Standard (not Autopilot)
- **Topology**: Zonal (single zone, cheaper than regional)
- **Zone**: us-central1-a
- **Node Pool**:
  - Size: 2x e2-medium (2 vCPU, 4GB RAM)
  - Autoscaling: Disabled (fixed count)
- **Networking**: VPC-native with linked secondary ranges
- **Workload Identity**: Enabled (pod → GCP service account federation)
- **Cluster Credentials**: Retrieved via `gcloud container clusters get-credentials`

### Phase 4: Container Images & Application Deployment
- **Image Registry**: Artifact Registry (`gee-assessment-repo` in us-central1)
- **Images**:
  - `app-alpha:latest` (linux/amd64)
  - `app-beta:latest` (linux/amd64)
- **Namespaces**:
  - `assessment-apps`: App workloads
  - `monitoring`: Grafana, Prometheus
- **Kubernetes Resources**:
  - Deployment: app-alpha (3 replicas), app-beta (3 replicas)
  - ConfigMaps: Non-secret configuration
  - Secrets: Sensitive data (ideally backed by Secret Manager)
  - Service: ClusterIP (stable internal IP per app)
  - HPAs: Optional horizontal scaling based on CPU
- **Workload Identity Bindings**:
  - KSA `app-alpha-ksa` → GSA `app-alpha-sa`
  - KSA `app-beta-ksa` → GSA `app-beta-sa`
  - Short-lived token exchange via metadata server

### Phase 5: Traffic Management & Ingress
- **Static IP**: Global IP `136.69.103.171` (reserved in VPC)
- **Ingress Resource**: Path-based routing
  - `/alpha/*` → `app-alpha-service`
  - `/beta/*` → `app-beta-service`
- **GCE Ingress Controller**: Provisions Google Cloud Load Balancer
- **Note**: No path rewriting — Flask app routes must match ingress paths
- **BackendConfig**: Custom health check
  - Path: `/health` (not default `/`)
  - Interval: 15 seconds
  - Thresholds: 1 healthy, 3 unhealthy

---

## Observability Architecture

### Logging
- **Source**: Application logs, kubelet, API server
- **Cloud Logging**: Central aggregation
- **Sink**: Exports k8s_container logs to BigQuery
- **BigQuery Dataset**: `logs_dataset`
- **Retention**: Historical query capability (SQL, joins, analytics)

### Metrics
- **Prometheus**: Scrapes infrastructure metrics
  - CPU, memory per node/pod
  - Request latency (if instrumented)
  - Pod restart counts
  - Network I/O
- **Scrape Interval**: 15 seconds
- **Retention**: ~15 days (default)

### Visualization
- **Grafana**: Dashboards (self-hosted on cluster)
- **Data Sources**:
  - Prometheus (real-time infrastructure metrics)
  - BigQuery (historical application logs)
- **Dashboard Panels**:
  - Avg Response Latency (latency_ms)
  - Error Metrics (5xx count)
  - Pod Restarts (restart events)
  - CPU Usage (per node/pod)
  - Memory Usage (MiB)
  - Pod Replicas (desired vs. running)

---

## Core Design Principles

### Security
- **Workload Identity**: Pod authentication via federated service accounts (no downloaded keys)
- **Least Privilege**: Each app SA has only required roles
- **Network Isolation**: VPC with no public IPs; Cloud NAT for outbound only
- **Image Security**: Private Artifact Registry; signed images recommended

### Scalability
- **VPC-Native Networking**: 4k pods per cluster (secondary range)
- **Horizontal Pod Autoscaling**: Optional HPA for dynamic replica scaling
- **Multi-Zone/Region**: Current setup is single-zone; production uses regional clusters

### Reliability
- **Health Checks**: Decoupled from app routes (BackendConfig)
- **Service Abstraction**: ClusterIP hides pod volatility
- **Pod Disruption Budgets**: Optional; ensures availability during maintenance
- **Cluster Autoscaling**: Optional; scales node pool based on pending pods

### Observability
- **Logs & Metrics**: Complementary signals
- **Structured Logging**: JSON for queryable insights
- **Alerting**: Prometheus alert rules (optional)
- **SLOs**: Track availability and latency targets

---

## Deployment Topology

```
┌─────────────────────────────────────────────────────────┐
│ GCP Project (sre-gke-assessment)                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Custom VPC (gke-vpc): 10.10.0.0/16              │  │
│  │                                                  │  │
│  │  ┌──────────────────────────────────────────┐   │  │
│  │  │ GKE Cluster (assessment-cluster)         │   │  │
│  │  │ Zone: us-central1-a                      │   │  │
│  │  │                                          │   │  │
│  │  │  ┌──────────────────────────────────┐   │   │  │
│  │  │  │ Nodes (2x e2-medium)             │   │   │  │
│  │  │  │ Primary: 10.10.0.0/20            │   │   │  │
│  │  │  └──────────────────────────────────┘   │   │  │
│  │  │                                          │   │  │
│  │  │  ┌──────────────────────────────────┐   │   │  │
│  │  │  │ assessment-apps namespace        │   │   │  │
│  │  │  │ Pod CIDR: 10.20.0.0/16           │   │   │  │
│  │  │  │                                  │   │   │  │
│  │  │  │ app-alpha (3 replicas)           │   │   │  │
│  │  │  │ app-beta (3 replicas)            │   │   │  │
│  │  │  └──────────────────────────────────┘   │   │  │
│  │  │                                          │   │  │
│  │  │  ┌──────────────────────────────────┐   │   │  │
│  │  │  │ monitoring namespace             │   │   │  │
│  │  │  │                                  │   │   │  │
│  │  │  │ Grafana (self-hosted)            │   │   │  │
│  │  │  │ Prometheus (self-hosted)         │   │   │  │
│  │  │  └──────────────────────────────────┘   │   │  │
│  │  │                                          │   │  │
│  │  │ Services (10.30.0.0/20):                │   │  │
│  │  │  app-alpha-service (ClusterIP)          │   │  │
│  │  │  app-beta-service (ClusterIP)           │   │  │
│  │  │  Ingress: path-based routing            │   │  │
│  │  └──────────────────────────────────────────┘   │  │
│  │                                                  │  │
│  │  ┌──────────────────────────────────────────┐   │  │
│  │  │ Managed Control Plane (Google-operated) │   │  │
│  │  │ API Server, Scheduler, Controller Mgr   │   │  │
│  │  └──────────────────────────────────────────┘   │  │
│  │                                                  │  │
│  │  ┌──────────────────────────────────────────┐   │  │
│  │  │ Cloud NAT (outbound only)                │   │  │
│  │  │ Cloud Router                             │   │  │
│  │  └──────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Global Load Balancer                            │  │
│  │ Static IP: 136.69.103.171                       │  │
│  │ Backend Services: app-alpha, app-beta           │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Observability Services (Managed)                │  │
│  │ • Artifact Registry (private Docker images)     │  │
│  │ • Cloud Logging (log aggregation)               │  │
│  │ • BigQuery (logs warehouse + analytics)         │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Infrastructure** | Google Compute Engine | Node VMs (e2-medium) |
| **Orchestration** | Google Kubernetes Engine (GKE) | Cluster management |
| **Networking** | VPC, Cloud NAT, Cloud Router | Secure isolation, outbound access |
| **Load Balancing** | Google Cloud Load Balancer | External traffic distribution |
| **Container Registry** | Artifact Registry | Private image storage |
| **Application** | Flask (Python) | HTTP API endpoints |
| **Metrics** | Prometheus | Infrastructure monitoring |
| **Visualization** | Grafana | Dashboards |
| **Logging** | Cloud Logging | Log aggregation |
| **Analytics** | BigQuery | Log warehouse & SQL queries |
| **Authentication** | Workload Identity | Pod-to-GCP service auth |

---

## API Endpoints

### Application: app-alpha
- `GET /alpha/api/data` → Fetch sample user data
- `GET /alpha/api/error` → Trigger 500 error (testing)
- `GET /health` → Liveness probe
- `GET /ready` → Readiness probe

### Application: app-beta
- `GET /beta/api/process` → Background job simulation
- `GET /beta/api/error` → Trigger 500 error (testing)
- `GET /health` → Liveness probe
- `GET /ready` → Readiness probe

### External Access
- **Base URL**: `http://136.69.103.171`
- **Endpoints**: `/alpha/*` and `/beta/*` routed via Ingress
- **Health Checks**: Load balancer → `/health` (via BackendConfig)

---

## Known Design Trade-offs

| Decision | Trade-off | Rationale |
|---|---|---|
| **Zonal Cluster** | Single zone failure = full cluster down | Cost efficiency for assessment; production uses regional |
| **Standard Mode** | Manual node management | More control; Autopilot abstracts nodes but less predictable |
| **2x e2-medium** | Limited capacity | Appropriate for test/demo; production scales horizontally |
| **No Autoscaling** | Manual scaling required | Predictable costs; production uses HPA + cluster autoscaling |
| **Public Cluster Endpoint** | Any authenticated user can reach API | Assessment simplicity; production uses private endpoints |

---

## Troubleshooting Reference

| Issue | Symptom | Solution |
|---|---|---|
| **Image Pull 403** | Pod stuck in ImagePullBackOff | Grant node SA `Artifact Registry Reader` role |
| **Architecture Mismatch** | `no match for platform in manifest` | Build with `--platform linux/amd64` |
| **404 on Ingress Path** | `/alpha` returns 404 | Define Flask routes under `/alpha` prefix (Ingress doesn't rewrite paths) |
| **Backend Unhealthy** | Load balancer serves generic error page | Create BackendConfig to point health check to `/health` (not `/`) |

---

## Deployment Checklist

- [ ] GCP project created and billing linked
- [ ] APIs enabled (Compute, GKE, Artifact Registry, BigQuery, Logging)
- [ ] Service accounts created with appropriate roles
- [ ] Custom VPC and subnets configured
- [ ] Cloud NAT and Cloud Router set up
- [ ] GKE cluster provisioned (zonal, standard, VPC-native)
- [ ] Workload Identity enabled and configured
- [ ] Container images built and pushed to Artifact Registry
- [ ] Kubernetes manifests applied (namespace, deployments, services)
- [ ] Ingress and BackendConfig deployed
- [ ] Global static IP reserved and mapped
- [ ] Cloud Logging sink configured
- [ ] BigQuery dataset created
- [ ] Prometheus and Grafana deployed (Helm)
- [ ] Dashboards configured
- [ ] API endpoints tested and responding
- [ ] Health checks passing

---

## References

- [Google Kubernetes Engine Documentation](https://cloud.google.com/kubernetes-engine/docs)
- [VPC-Native Networking](https://cloud.google.com/kubernetes-engine/docs/concepts/alias-ips)
- [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)
- [GKE Ingress](https://cloud.google.com/kubernetes-engine/docs/concepts/ingress)
- [BackendConfig for Custom Health Checks](https://cloud.google.com/kubernetes-engine/docs/concepts/backendconfig)
