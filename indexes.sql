-- PostgreSQL Index Definitions for Query Performance Benchmark Optimization
-- Each index is tailored to resolve sequential scan bottlenecks identified in EXPLAIN ANALYZE traces.

-- ============================================================================
-- Index 1: Benchmark Q1 - Monthly Revenue & Trip Count
-- Query Filters: WHERE tpep_pickup_datetime >= '2023-01-01' AND tpep_pickup_datetime < '2023-02-01'
-- Strategy: BTREE index on pickup datetime eliminates full sequential table scan.
-- ============================================================================
CREATE INDEX idx_trips_pickup_datetime 
ON trips (tpep_pickup_datetime);

-- ============================================================================
-- Index 2: Benchmark Q2 - Average Tip Percentage by Borough
-- Query Joins: trips.pu_location_id = pu.location_id AND trips.do_location_id = do.location_id
-- Strategy: Separate single-column indexes on FK pickup/dropoff columns speed up Hash & Nested Loop Joins.
-- ============================================================================
CREATE INDEX idx_trips_pu_location 
ON trips (pu_location_id);

CREATE INDEX idx_trips_do_location 
ON trips (do_location_id);

-- ============================================================================
-- Index 3: Benchmark Q3 - High Volume Zones (>10,000 trips & high avg fare)
-- Query Operations: GROUP BY pu_location_id HAVING COUNT(*) > 10000 AND AVG(fare_amount) > threshold
-- Strategy: Composite index on (pu_location_id, fare_amount) enables index-only group aggregation.
-- ============================================================================
CREATE INDEX idx_trips_pu_fare_comp 
ON trips (pu_location_id, fare_amount);

-- ============================================================================
-- Index 4: Benchmark Q4 - Zone Revenue Rank by Month
-- Query Operations: DATE_TRUNC('month', tpep_pickup_datetime), pu_location_id, SUM(total_amount)
-- Strategy: Composite covering index on (tpep_pickup_datetime, pu_location_id) with INCLUDE (total_amount).
-- ============================================================================
CREATE INDEX idx_trips_monthly_zone_revenue 
ON trips (tpep_pickup_datetime, pu_location_id) INCLUDE (total_amount);

-- ============================================================================
-- Index 5: Benchmark Q5 - Anomaly Trips (High passengers, long distance, low tip)
-- Query Filters: WHERE passenger_count > 4 AND trip_distance > 15.0 AND tip_amount < 1.0
-- Strategy: Multi-column composite index matching high selectivity filter conditions.
-- ============================================================================
CREATE INDEX idx_trips_anomaly_filters 
ON trips (passenger_count, trip_distance, tip_amount);
