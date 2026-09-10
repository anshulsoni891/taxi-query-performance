-- PostgreSQL Schema Definition for NYC Yellow Taxi Query Performance Benchmark Project

DROP TABLE IF EXISTS trips;
DROP TABLE IF EXISTS locations;

-- Taxi Zone Lookup Table
CREATE TABLE locations (
    location_id INT PRIMARY KEY,
    borough VARCHAR(50) NOT NULL,
    zone VARCHAR(100) NOT NULL,
    service_zone VARCHAR(50) NOT NULL
);

-- Yellow Taxi Trip Records Table
CREATE TABLE trips (
    trip_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vendor_id INT,
    tpep_pickup_datetime TIMESTAMP NOT NULL,
    tpep_dropoff_datetime TIMESTAMP NOT NULL,
    passenger_count INT,
    trip_distance NUMERIC(10, 2),
    rate_code_id INT,
    store_and_fwd_flag CHAR(1),
    pu_location_id INT NOT NULL REFERENCES locations(location_id),
    do_location_id INT NOT NULL REFERENCES locations(location_id),
    payment_type INT,
    fare_amount NUMERIC(10, 2),
    extra NUMERIC(10, 2),
    mta_tax NUMERIC(10, 2),
    tip_amount NUMERIC(10, 2),
    tolls_amount NUMERIC(10, 2),
    improvement_surcharge NUMERIC(10, 2),
    total_amount NUMERIC(10, 2),
    congestion_surcharge NUMERIC(10, 2),
    airport_fee NUMERIC(10, 2)
);
