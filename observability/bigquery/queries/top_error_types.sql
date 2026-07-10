SELECT
  resource.labels.container_name    AS container,
  jsonPayload.message AS error_message,
  severity,
  COUNT(*)                          AS occurrence_count,
  MAX(timestamp)                    AS last_seen
FROM
`sre-gke-assesment.gke_logs.stderr_*`
WHERE
  severity IN ('ERROR', 'CRITICAL')
  AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY
  container, error_message, severity
ORDER BY
  occurrence_count DESC
LIMIT 20;
