-- Bulk data loading script for PostgreSQL using \COPY commands

-- 1. Load Locations Lookup Data
\COPY locations(location_id, borough, zone, service_zone) FROM 'data/taxi_zone_lookup.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');

-- 2. Load Yellow Taxi Trips Data
\COPY trips(vendor_id, tpep_pickup_datetime, tpep_dropoff_datetime, passenger_count, trip_distance, rate_code_id, store_and_fwd_flag, pu_location_id, do_location_id, payment_type, fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, total_amount, congestion_surcharge, airport_fee) FROM 'data/yellow_tripdata_combined.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');

-- Verify Loaded Counts
SELECT 'locations' AS table_name, COUNT(*) AS row_count FROM locations
UNION ALL
SELECT 'trips' AS table_name, COUNT(*) AS row_count FROM trips;
