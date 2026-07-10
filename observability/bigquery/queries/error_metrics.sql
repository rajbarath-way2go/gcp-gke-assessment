SELECT
  TIMESTAMP_TRUNC(timestamp, MINUTE) AS time,
  COUNT(*) AS error_count
FROM `sre-gke-assesment.gke_logs.stderr_*`
WHERE jsonPayload.level = "ERROR"
GROUP BY time
ORDER BY time