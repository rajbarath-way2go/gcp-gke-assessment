SELECT
  TIMESTAMP_TRUNC(timestamp, MINUTE) AS time,
  AVG(CAST(REGEXP_EXTRACT(jsonPayload.message, r'([0-9]+\.?[0-9]*)ms') AS FLOAT64)) AS avg_latency_ms
FROM `sre-gke-assesment.gke_logs.stderr_*`
WHERE jsonPayload.app IN ('app-alpha', 'app-beta')
  AND jsonPayload.message LIKE '%served in%'
GROUP BY time
ORDER BY time
