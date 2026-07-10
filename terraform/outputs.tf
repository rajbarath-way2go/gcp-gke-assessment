output "project_id" {
  description = "The GCP project ID"
  value       = var.project_id
}

output "cluster_name" {
  description = "The GKE cluster name"
  value       = var.cluster_name
}

output "cluster_endpoint" {
  description = "The GKE cluster endpoint"
  value       = "Populated after Phase 4 Terraform"
  sensitive   = false
}

output "ingress_ip" {
  description = "The external IP of the Ingress load balancer"
  value       = "Populated after Phase 6 Terraform"
}

output "bigquery_dataset" {
  description = "The BigQuery dataset for log exports"
  value       = var.bigquery_dataset_id
}
