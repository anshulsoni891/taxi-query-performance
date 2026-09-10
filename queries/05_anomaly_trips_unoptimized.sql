-- Benchmark Q5 (Unoptimized): High Passenger Count, Long Distance, Low Tip Anomaly Trips
-- SQL Concept Tested: Multi-condition complex filtering.
-- Expectation: Seq Scan evaluating 3 un-indexed predicates across entire table.

SELECT 
    t.vendor_id,
    t.tpep_pickup_datetime,
    t.passenger_count,
    t.trip_distance,
    t.fare_amount,
    t.tip_amount,
    t.total_amount,
    pu_loc.zone AS pickup_zone,
    do_loc.zone AS dropoff_zone
FROM trips t
JOIN locations pu_loc ON t.pu_location_id = pu_loc.location_id
JOIN locations do_loc ON t.do_location_id = do_loc.location_id
WHERE t.passenger_count >= 5
  AND t.trip_distance > 15.0
  AND t.tip_amount < 1.00
ORDER BY t.trip_distance DESC;
