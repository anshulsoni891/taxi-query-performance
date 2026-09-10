-- Benchmark Q4 (Optimized): Rank Zones by Monthly Revenue
-- Optimization Applied: Pre-filtering CTE with Composite Covering Index on (tpep_pickup_datetime, pu_location_id) INCLUDE (total_amount).
-- Plan Shift: Reduced sorting cost and direct covered index read.

WITH MonthlyZoneSummary AS (
    SELECT 
        DATE_TRUNC('month', t.tpep_pickup_datetime) AS pickup_month,
        t.pu_location_id,
        SUM(t.total_amount) AS monthly_revenue
    FROM trips t
    WHERE t.tpep_pickup_datetime >= '2023-01-01' AND t.tpep_pickup_datetime < '2023-07-01'
    GROUP BY DATE_TRUNC('month', t.tpep_pickup_datetime), t.pu_location_id
)
SELECT 
    m.pickup_month,
    loc.zone AS pickup_zone,
    ROUND(m.monthly_revenue, 2) AS monthly_revenue,
    DENSE_RANK() OVER (PARTITION BY m.pickup_month ORDER BY m.monthly_revenue DESC) AS revenue_rank
FROM MonthlyZoneSummary m
JOIN locations loc ON m.pu_location_id = loc.location_id
ORDER BY m.pickup_month, revenue_rank;
