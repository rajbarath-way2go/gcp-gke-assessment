# Terraform Environment: dev
# Fill in your real values here after Phase 2

project_id          = "<YOUR_PROJECT_ID>"    # e.g. "gke-assessment-abc123"
region              = "us-central1"
zone                = "us-central1-a"
cluster_name        = "gke-assessment-cluster"
node_machine_type   = "e2-medium"
node_count          = 2
vpc_name            = "gke-vpc"
subnet_name         = "gke-nodes-subnet"
bigquery_dataset_id = "gke_logs"
