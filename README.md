# GCP GKE Assessment: Production-Ready Kubernetes Platform

> **Assessment** — End-to-end GKE infrastructure build with monitoring, security practices, and real-world troubleshooting

**Project**: `sre-gke-assessment`  
**Status**: ✅ Done  
**Stack**: Python/Flask · GCP · Kubernetes · Terraform · Prometheus · Grafana · BigQuery

---

## 🎯 Project Overview

This assessment demonstrates a **production-ready Google Kubernetes Engine (GKE) environment** with two containerized applications, secure networking, and comprehensive observability. The project showcases:

✅ **Working GKE Cluster** — Accessible applications via global load balancer  
✅ **Two Microservices** — Flask apps (app-alpha, app-beta) with 3 replicas each  
✅ **Secure Networking** — VPC-native cluster with Cloud NAT (no public IPs)  
✅ **Workload Identity** — Pod-to-GCP authentication without downloaded keys  
✅ **Observability** —  Prometheus metrics + Grafana dashboards  
✅ **Real Troubleshooting** — issues documented with solutions  

---

## 📊 Assessment Alignment

| Criterion                                       | Status | Evidence                                                                     |
| -------------------------------------------------| --------| ------------------------------------------------------------------------------|
| **Working cluster with accessible endpoints**   | ✅      | `apps/` with Flask apps, `k8s/ingress.yaml` routing to live endpoints        |
| **Grafana dashboard screenshot/export**         | ✅      | `observability/Grafana - Monitoring Dashboard.png` with 6 key metrics panels             |
| **BigQuery queries demonstrating log analysis** | ✅      | `observability/bigquery/queries/` with production SQL queries                |
| **Troubleshooting scenario documentation**      | ✅      | `docs/troubleshooting_log.md` with 4 real issues + root causes + resolutions |
| **Infrastructure as Code**                      | ⚠️      | `terraform/` - Item pending.                                                 |
| **Architecture diagram & design doc**           | ✅      | `docs/architecture/architecture.md` with 7-phase deployment guide            |
| **BigQuery schema & sample queries**            | ✅      | `observability/bigquery` + SQL and Promotheus queries              |
| **Design decisions & rationale**                | ✅      | `docs/` with explicit rationale for each architectural choice                |

---

## 📁 Repository Structure

```
gcp-gke-assessment/
├── README.md                           ← You are here
├── COST_TRACKER.md                     ← Cost monitoring & Free Tier notes
│
├── docs/
│   ├── ARCHITECTURE.md                 ← System design blueprint (read first)
│   ├── DEPLOYMENT.md                   ← Step-by-step setup guide
│   ├── DESIGN_DECISIONS.md             ← Why each architectural choice
│   ├── DOCS_README.md                  ← Navigation guide for all docs
│   ├── architecture/
│   │   └── architecture.md             ← Detailed system architecture
│   ├── troubleshooting_log.md          ← 4 real issues + solutions
│   └── diagrams/
│       ├── system-architecture.png     ← Infrastructure diagram
│       ├── request-flow.png            ← Request sequence diagram
│       └── deployment-topology.png     ← Deployment topology
│
├── apps/                               ← Application source code
│   ├── app-alpha/
│   │   ├── app.py                      ← Flask application #1
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── README.md
│   └── app-beta/
│       ├── app.py                      ← Flask application #2
│       ├── requirements.txt
│       ├── Dockerfile
│       └── README.md
│
├── k8s/                                ← Kubernetes manifests
│   ├── namespace.yaml                  ← assessment-apps namespace
│   ├── app-alpha/
│   │   ├── deployment.yaml             ← 3 replicas, Workload Identity binding
│   │   ├── service.yaml                ← ClusterIP service + BackendConfig annotation
│   │   ├── configmap.yaml              ← Non-secret configuration
│   │   └── hpa.yaml                    ← Horizontal Pod Autoscaler (optional)
│   ├── app-beta/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   └── hpa.yaml
│   ├── ingress/
│   │   ├── ingress.yaml                ← Path-based routing (/alpha, /beta)
│   │   └── backendconfig.yaml          ← Custom health check config
│   └── monitoring/
│       ├── prometheus-values.yaml      ← Helm chart values
│       └── grafana-values.yaml         ← Helm chart values
│
├── terraform/                          ← Infrastructure as Code
│   ├── README.md                       ← Terraform deployment guide
│   ├── versions.tf                     ← GCP provider config
│   ├── variables.tf                    ← Input variables (project, region, etc.)
│   ├── outputs.tf                      ← Exported values (cluster name, IP, etc.)
│   ├── modules/
│   │   ├── project-iam/                ← Project creation, APIs, service accounts
│   │   ├── networking/                 ← VPC, subnets, Cloud NAT, firewall
│   │   ├── gke/                        ← Cluster provisioning, node pools
│   │   └── observability/              ← BigQuery, Cloud Logging sink, Prometheus/Grafana
│   └── environments/
│       └── dev/
│           ├── main.tf                 ← Module instantiation for dev environment
│           └── terraform.tfvars        ← Dev environment variables
│
├── observability/                      ← Monitoring, logging, dashboards
│   ├── bigquery/
│   │   ├── schema.md                   ← BigQuery logs table schema + field definitions
│   │   └── queries/
│   │       ├── errors_over_time.sql    ← Error count trend (last 24h)
│   │       ├── top_error_types.sql     ← Top 10 error types by frequency
│   │       ├── latency_percentiles.sql ← P50, P95, P99 latency by endpoint
│   │       └── pod_restarts.sql        ← Pod restart events and correlation
│   └── grafana/
│       ├── dashboard.json              ← Pre-built dashboard (Latency, errors, CPU, memory)
│       └── provisioning/
│           └── datasources.yaml        ← Prometheus + BigQuery data source config
│
```

---

## 📚 Documentation

| Document | Purpose | Read Time |
|---|---|---|
| `docs/architecture/ ARCHITECTURE.md` | System design blueprint | 10-15 min |
| `docs/architecture/DEPLOYMENT.md` | Step-by-step setup guide | 10-15 min (reference) |

---

## 🔑 Key Files

| File                                   | Purpose                                                   |
| ----------------------------------------| -----------------------------------------------------------|
| `apps/app-alpha/app.py`                | Flask app #1 (GET /alpha/api/data, /api/error, /health)   |
| `apps/app-beta/app.py`                 | Flask app #2 (GET /beta/api/process, /api/error, /health) |
| `k8s/ingress/ingress.yaml`             | Ingress with path-based routing (/alpha, /beta)           |
| `k8s/ingress/backendconfig.yaml`       | Custom health check config (path: /health)                |
| `observability/bigquery/queries/`      | SQL queries for log analysis                 |
| `observability/Grafana - Monitoring Dashboard.png` | Grafana dashboard                                         |

---


