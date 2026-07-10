# BigQuery Log Schema

> The Cloud Logging → BigQuery sink automatically creates tables in the `gke_logs` dataset.  
> This document describes the key tables and fields used in our queries.

## Log Sink Tables

When you configure a BigQuery log sink for a GKE cluster, Cloud Logging creates tables  
named by log type. Key tables:

| Table Name Pattern | Contents |
|---|---|
| `stdout_*` | Container stdout/stderr (your Flask app logs) |
| `cloudaudit_googleapis_com_activity_*` | GCP API audit logs (project-level actions) |
| `events_*` | Kubernetes events (pod restarts, OOMKills, etc.) |
| `requests_*` | Load balancer access logs |

## Common Fields (all tables)

| Field | Type | Description |
|---|---|---|
| `timestamp` | TIMESTAMP | Log entry timestamp |
| `severity` | STRING | Log severity: DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `resource.type` | STRING | Resource type (e.g., `k8s_container`) |
| `resource.labels.cluster_name` | STRING | GKE cluster name |
| `resource.labels.namespace_name` | STRING | Kubernetes namespace |
| `resource.labels.pod_name` | STRING | Pod name |
| `resource.labels.container_name` | STRING | Container name (app-alpha or app-beta) |
| `json_payload` | JSON | Structured log fields (from Flask JSON logging) |
| `text_payload` | STRING | Unstructured log text |

## Flask App Custom Fields (json_payload)

Our Flask apps log structured JSON. These fields appear in `json_payload`:

| Field | Type | Description |
|---|---|---|
| `json_payload.message` | STRING | Log message |
| `json_payload.latency_ms` | FLOAT | Request latency in milliseconds |
| `json_payload.app` | STRING | App name (app-alpha / app-beta) |
| `json_payload.level` | STRING | Python log level |

## Example: Query for app-alpha errors in last hour

```sql
SELECT timestamp, json_payload.message, severity
FROM `<PROJECT>.<DATASET>.stdout_*`
WHERE resource.labels.container_name = 'app-alpha'
  AND severity = 'ERROR'
  AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
ORDER BY timestamp DESC;
```
