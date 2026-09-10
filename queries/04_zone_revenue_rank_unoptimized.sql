-- Benchmark Q4 (Unoptimized): Rank Zones by Monthly Revenue
-- SQL Concept Tested: Window Functions (DENSE_RANK) over raw aggregated data.
-- Expectation: Heavy WindowAgg + Sort steps over raw scanned rows.

SELECT 
    pickup_month,
    pickup_zone,
    monthly_revenue,
    DENSE_RANK() OVER (PARTITION BY pickup_month ORDER BY monthly_revenue DESC) AS revenue_rank
FROM (
    SELECT 
        DATE_TRUNC('month', t.tpep_pickup_datetime) AS pickup_month,
        loc.zone AS pickup_zone,
        SUM(t.total_amount) AS monthly_revenue
    FROM trips t
    JOIN locations loc ON t.pu_location_id = loc.location_id
    GROUP BY DATE_TRUNC('month', t.tpep_pickup_datetime), loc.zone
) sub
ORDER BY pickup_month, revenue_rank;
