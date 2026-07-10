-- Query: Latency Percentiles (p50, p95, p99)
-- Purpose: Extracts latency values from structured JSON logs for Grafana latency panel
-- Replace <YOUR_PROJECT_ID> and <YOUR_DATASET> with your values
-- Note: latency_ms must be logged as a JSON field in your Flask app (see app.py)

SELECT
  TIMESTAMP_TRUNC(timestamp, MINUTE)    AS minute,
  resource.labels.container_name        AS container,
  ROUND(APPROX_QUANTILES(
    CAST(JSON_EXTRACT_SCALAR(json_payload, '$.latency_ms') AS FLOAT64), 100
  )[OFFSET(50)], 2)                     AS p50_ms,
  ROUND(APPROX_QUANTILES(
    CAST(JSON_EXTRACT_SCALAR(json_payload, '$.latency_ms') AS FLOAT64), 100
  )[OFFSET(95)], 2)                     AS p95_ms,
  ROUND(APPROX_QUANTILES(
    CAST(JSON_EXTRACT_SCALAR(json_payload, '$.latency_ms') AS FLOAT64), 100
  )[OFFSET(99)], 2)                     AS p99_ms,
  COUNT(*)                              AS request_count
FROM
  `<YOUR_PROJECT_ID>.<YOUR_DATASET>.stdout_*`
WHERE
  JSON_EXTRACT_SCALAR(json_payload, '$.latency_ms') IS NOT NULL
  AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
GROUP BY
  minute, container
ORDER BY
  minute DESC;
