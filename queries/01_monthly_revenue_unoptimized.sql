-- Benchmark Q1 (Unoptimized): Monthly Revenue & Trip Count
-- SQL Concept Tested: Date-range filtering without index support.
-- Expectation: Full Sequential Scan scanning 100% of rows.

SELECT 
    DATE_TRUNC('month', tpep_pickup_datetime) AS pickup_month,
    COUNT(*) AS total_trips,
    ROUND(SUM(fare_amount), 2) AS total_fare,
    ROUND(SUM(tip_amount), 2) AS total_tips,
    ROUND(SUM(total_amount), 2) AS total_revenue
FROM trips
WHERE tpep_pickup_datetime >= '2023-01-01 00:00:00' 
  AND tpep_pickup_datetime < '2023-02-01 00:00:00'
GROUP BY DATE_TRUNC('month', tpep_pickup_datetime);
