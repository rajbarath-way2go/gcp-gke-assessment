-- Query: Errors Over Time

SELECT
  TIMESTAMP_TRUNC(timestamp, HOUR)  AS hour,
  resource.labels.container_name    AS container,
  severity,
  COUNT(*)                          AS error_count
FROM
  `sre-gke-assesment.gke_logs.stderr_*`
WHERE
  severity IN ('ERROR', 'CRITICAL', 'ALERT', 'EMERGENCY')
  AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
GROUP BY
  hour, container, severity
ORDER BY
  hour DESC, error_count DESC;
