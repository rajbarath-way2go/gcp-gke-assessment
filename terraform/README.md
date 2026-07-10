# Terraform README

> Terraform code is added **phase by phase**, after each resource is manually built and verified.  
> Do NOT run `terraform apply` before completing the manual phase for each resource.

## Structure

```
terraform/
├── versions.tf          ← Provider versions (do not change)
├── variables.tf         ← All input variables with defaults
├── outputs.tf           ← Outputs updated per phase
├── modules/
│   ├── project-iam/     ← Phase 2: google_project, APIs, IAM
│   ├── networking/      ← Phase 3: VPC, subnets, NAT, firewall
│   ├── gke/             ← Phase 4: cluster + node pool
│   └── observability/   ← Phase 7: BigQuery dataset, logging sink
└── environments/
    └── dev/
        ├── main.tf          ← Module calls (built up phase by phase)
        └── terraform.tfvars ← Your real values go here
```

## Usage

```bash
cd terraform/environments/dev

# Initialize (first time only)
terraform init

# Preview changes
terraform plan -var-file="terraform.tfvars"

# Apply (only after manual build + verify)
terraform apply -var-file="terraform.tfvars"

# Validate syntax
terraform validate

# Format code
terraform fmt -recursive ../../
```

## Module Build Order

| Phase | Module | Status |
|-------|--------|--------|
| 2 | `modules/project-iam/` | ⬜ Not built yet |
| 3 | `modules/networking/` | ⬜ Not built yet |
| 4 | `modules/gke/` | ⬜ Not built yet |
| 7 | `modules/observability/` | ⬜ Not built yet |
