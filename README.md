# GCP / GKE Pre-Assessment — Workspace

> **Mentor-guided, hands-on GKE infrastructure build**  
> Stack: Python/Flask · GCP Free Tier · gcloud / kubectl · Terraform (after manual build)

---

## 📁 Workspace Structure

```
gcp-gke-assessment/
├── README.md                   ← You are here
├── COST_TRACKER.md             ← Flags anything that may incur cost
│
├── docs/
│   ├── architecture/
│   │   └── architecture.md                 
│   ├── troubleshooting_log.md                 
│
├── apps/
│   ├── app-alpha/                      ← Flask web app #1
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── app-beta/                       ← Flask web app #2
│       ├── app.py
│       ├── requirements.txt
│       └── Dockerfile
│
├── k8s/
│   ├── namespace.yaml
│   ├── app-alpha/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   └── hpa.yaml
│   ├── app-beta/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   └── hpa.yaml
│   └── ingress/
│       └── ingress.yaml
│
├── terraform/
│   ├── README.md
│   ├── versions.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── modules/
│   │   ├── project-iam/
│   │   ├── networking/
│   │   ├── gke/
│   │   └── observability/
│   └── environments/
│       └── dev/
│           ├── main.tf
│           └── terraform.tfvars
│
├── observability/
│   ├── bigquery/
│   │   ├── schema.md
│   │   └── queries/
│   │       ├── errors_over_time.sql
│   │       ├── top_error_types.sql
│   │       ├── latency_percentiles.sql
│   │       └── pod_restarts.sql
│   └── grafana/
│       └── dashboard.json
│

```
