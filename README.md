# GCP / GKE Pre-Assessment — Workspace

> **Mentor-guided, hands-on GKE infrastructure build**  
> Stack: Python/Flask · GCP Free Tier · gcloud / kubectl · Terraform (after manual build)

---

## 📁 Workspace Structure

```
gcp-gke-assessment/
├── README.md                   ← You are here
├── PROGRESS.md                 ← Live checklist — updated after every step
├── TROUBLESHOOTING_LOG.md      ← Real issues + resolutions (builds deliverable #4)
├── COST_TRACKER.md             ← Flags anything that may incur cost
│
├── docs/
│   ├── architecture/
│   │   └── architecture_diagram.md     ← Phase 11 deliverable
│   ├── design_rationale.md             ← Design decisions & tradeoffs
│   ├── setup_guide_manual.md           ← Full manual setup steps
│   └── setup_guide_terraform.md        ← Terraform equivalent steps
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
└── phase-notes/
    ├── phase0-prerequisites.md
    ├── phase1-scoped-plan.md
    ├── phase2-project-iam.md
    ├── phase3-networking.md
    ├── phase4-gke-cluster.md
    ├── phase5-app-deployment.md
    ├── phase6-ingress-traffic.md
    ├── phase7-observability.md
    ├── phase8-bigquery-analysis.md
    ├── phase9-troubleshooting-writeup.md
    ├── phase10-terraform-consolidation.md
    └── phase11-documentation.md
```

---

## 🎯 Deliverables Checklist

| # | Deliverable | Status | File |
|---|-------------|--------|------|
| 1 | Working cluster with accessible application endpoint | ⬜ Pending | — |
| 2 | Grafana dashboard screenshot (≥ 4 panels) | ⬜ Pending | `observability/grafana/` |
| 3 | Sample BigQuery queries demonstrating log analysis | ⬜ Pending | `observability/bigquery/queries/` |
| 4 | Written troubleshooting scenario (real issue + resolution) | ⬜ Pending | `TROUBLESHOOTING_LOG.md` |
| 5 | Architecture diagram + setup steps + BQ schema + design rationale | ⬜ Pending | `docs/` |

---

## 🗺️ Phase Overview

| Phase | Title | Manual | Terraform | Status |
|-------|-------|--------|-----------|--------|
| 0 | Accounts & Prerequisites | ✅ Only | — | ⬜ |
| 1 | Scoped Plan | — | — | ⬜ |
| 2 | GCP Project & IAM | ⬜ | ⬜ | ⬜ |
| 3 | Networking (VPC, subnets, NAT) | ⬜ | ⬜ | ⬜ |
| 4 | GKE Cluster(s) | ⬜ | ⬜ | ⬜ |
| 5 | Application Deployment | ⬜ | ⬜ | ⬜ |
| 6 | Ingress & Traffic | ⬜ | ⬜ | ⬜ |
| 7 | Observability (Logging, Grafana, Monitoring) | ⬜ | ⬜ | ⬜ |
| 8 | BigQuery Log Analysis | ⬜ | — | ⬜ |
| 9 | Troubleshooting Write-Up | ⬜ | — | ⬜ |
| 10 | Terraform Consolidation & Validation | — | ⬜ | ⬜ |
| 11 | Documentation Wrap-Up | ⬜ | — | ⬜ |

---

## ⚙️ Mentor Rules Summary

1. **Plan First** — Phase 1 scoped plan must be approved before building
2. **One Step at a Time** — Each step waits for your verification
3. **Checkpoints** — Every step has a verification command + expected output
4. **Teach As You Go** — 2–4 sentence plain-language explanation before each new concept
5. **Commands, Not Vague Instructions** — Exact copy-pasteable CLI commands with placeholders
6. **Track Progress** — See `PROGRESS.md` at any time
7. **Troubleshooting Log** — See `TROUBLESHOOTING_LOG.md` — real issues only
8. **Cost Awareness** — See `COST_TRACKER.md` before any resource creation
9. **Manual First, Then Terraform** — Build → Verify → Terraform, resource-by-resource

---

## 🚀 Getting Started

**Step 1**: Read `phase-notes/phase1-scoped-plan.md` to see the free-tier-scoped plan.  
**Step 2**: Give your **"approved"** to begin Phase 0.  
**Step 3**: Follow along step-by-step using `PROGRESS.md` as your guide.
