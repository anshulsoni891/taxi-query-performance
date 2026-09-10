-- Benchmark Q3 (Unoptimized): High Volume Zones (>10,000 Pickups & High Avg Fare)
-- SQL Concept Tested: GROUP BY + HAVING threshold filtering.
-- Expectation: Hash Aggregate scanning full trips table.

SELECT 
    loc.zone AS pickup_zone,
    loc.borough,
    COUNT(*) AS total_pickups,
    ROUND(AVG(t.fare_amount), 2) AS avg_fare,
    ROUND(SUM(t.total_amount), 2) AS zone_revenue
FROM trips t
JOIN locations loc ON t.pu_location_id = loc.location_id
GROUP BY loc.zone, loc.borough
HAVING COUNT(*) > 10000 AND AVG(t.fare_amount) > 18.00
ORDER BY total_pickups DESC;
