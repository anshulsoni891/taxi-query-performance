-- Benchmark Q2 (Optimized): Average Tip % by Pickup & Dropoff Borough
-- Optimization Applied: Foreign Key Indexes on pu_location_id and do_location_id.
-- Plan Shift: Accelerated JOIN lookup avoiding expensive un-indexed table scans.

SELECT 
    pu_loc.borough AS pickup_borough,
    do_loc.borough AS dropoff_borough,
    COUNT(*) AS trip_count,
    ROUND(AVG(t.tip_amount), 2) AS avg_tip_dollars,
    ROUND(AVG(CASE WHEN t.fare_amount > 0 THEN (t.tip_amount / t.fare_amount) * 100 ELSE 0 END), 2) AS avg_tip_pct
FROM trips t
JOIN locations pu_loc ON t.pu_location_id = pu_loc.location_id
JOIN locations do_loc ON t.do_location_id = do_loc.location_id
WHERE t.fare_amount > 0
GROUP BY pu_loc.borough, do_loc.borough
ORDER BY trip_count DESC;
