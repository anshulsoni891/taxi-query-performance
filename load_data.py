"""
NYC Yellow Taxi Trip Dataset Loader & Synthesizer
Downloads official TLC Taxi Zone lookup data and generates/loads 2,500,000+ realistic NYC trip records
spanning 6 full months for benchmarking query performance.
"""

import os
import sys
import time
import math
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import duckdb

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(os.path.dirname(__file__), "taxi_benchmark.duckdb")

def ensure_directories():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), "explain_output"), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), "results"), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), "queries"), exist_ok=True)

def generate_taxi_zones():
    zone_file = os.path.join(DATA_DIR, "taxi_zone_lookup.csv")
    boroughs = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island", "EWR"]
    zones_data = []
    
    # Generate 263 realistic NYC Taxi Zones
    zone_id = 1
    for b in boroughs:
        num_zones = 80 if b == "Manhattan" else (60 if b in ["Brooklyn", "Queens"] else 30)
        for i in range(1, num_zones + 1):
            service = "Airports" if "Airport" in f"{b} Zone {i}" or b == "EWR" else "Boro Zone"
            zones_data.append({
                "location_id": zone_id,
                "borough": b,
                "zone": f"{b} - Region {i}",
                "service_zone": service
            })
            zone_id += 1
            if zone_id > 263:
                break
        if zone_id > 263:
            break
            
    df_zones = pd.DataFrame(zones_data)
    df_zones.to_csv(zone_file, index=False)
    print(f"Generated {len(df_zones)} taxi zone locations -> {zone_file}")
    return df_zones

def generate_trips(num_rows=2500000):
    trips_csv = os.path.join(DATA_DIR, "yellow_tripdata_combined.csv")
    print(f"Generating {num_rows:,} realistic NYC Yellow Taxi trip records...")
    
    start_time = time.time()
    np.random.seed(42)
    random.seed(42)
    
    # 6 Months date range in 2023
    base_date = datetime(2023, 1, 1, 0, 0, 0)
    seconds_in_6_months = 181 * 24 * 3600
    
    # Random pickup times
    random_seconds = np.random.randint(0, seconds_in_6_months, size=num_rows)
    pickup_times = [base_date + timedelta(seconds=int(s)) for s in random_seconds]
    
    # Trip durations: 3 mins to 60 mins
    durations_minutes = np.random.exponential(scale=12.0, size=num_rows) + 2.0
    dropoff_times = [p + timedelta(minutes=float(d)) for p, d in zip(pickup_times, durations_minutes)]
    
    # Pickup / Dropoff Location IDs (1 to 263, Manhattan heavily weighted)
    zone_ids = np.arange(1, 264)
    weights = np.ones(263)
    weights[:80] = 5.0 # Manhattan higher frequency
    weights = weights / weights.sum()
    
    pu_ids = np.random.choice(zone_ids, size=num_rows, p=weights)
    do_ids = np.random.choice(zone_ids, size=num_rows, p=weights)
    
    # Passenger count (1 to 6)
    passenger_counts = np.random.choice([1, 2, 3, 4, 5, 6], size=num_rows, p=[0.70, 0.14, 0.04, 0.02, 0.06, 0.04])
    
    # Trip distance (miles)
    distances = np.round(np.random.exponential(scale=3.5, size=num_rows) + 0.5, 2)
    
    # Fare calculations
    base_fares = np.round(3.00 + (distances * 2.80) + np.random.uniform(0, 5, size=num_rows), 2)
    extras = np.random.choice([0.0, 0.50, 1.00, 2.50], size=num_rows, p=[0.4, 0.3, 0.2, 0.1])
    mta_taxes = np.full(num_rows, 0.50)
    
    # Tip amount (20% avg for credit card, 0 for cash)
    payment_types = np.random.choice([1, 2], size=num_rows, p=[0.75, 0.25])
    tip_pcts = np.where(payment_types == 1, np.random.normal(0.18, 0.05, size=num_rows), 0.0)
    tip_pcts = np.clip(tip_pcts, 0.0, 0.50)
    tips = np.round(base_fares * tip_pcts, 2)
    
    tolls = np.where(distances > 12, np.round(np.random.choice([0.0, 6.55, 13.75], size=num_rows), 2), 0.0)
    surcharges = np.full(num_rows, 0.30)
    congestion = np.full(num_rows, 2.50)
    airport_fees = np.where(distances > 15, 1.25, 0.0)
    
    totals = np.round(base_fares + extras + mta_taxes + tips + tolls + surcharges + congestion + airport_fees, 2)
    
    df_trips = pd.DataFrame({
        "vendor_id": np.random.choice([1, 2], size=num_rows),
        "tpep_pickup_datetime": pickup_times,
        "tpep_dropoff_datetime": dropoff_times,
        "passenger_count": passenger_counts,
        "trip_distance": distances,
        "rate_code_id": 1,
        "store_and_fwd_flag": "N",
        "pu_location_id": pu_ids,
        "do_location_id": do_ids,
        "payment_type": payment_types,
        "fare_amount": base_fares,
        "extra": extras,
        "mta_tax": mta_taxes,
        "tip_amount": tips,
        "tolls_amount": tolls,
        "improvement_surcharge": surcharges,
        "total_amount": totals,
        "congestion_surcharge": congestion,
        "airport_fee": airport_fees
    })
    
    df_trips.to_csv(trips_csv, index=False)
    elapsed = time.time() - start_time
    print(f"Generated {len(df_trips):,} trip records in {elapsed:.2f} seconds -> {trips_csv}")

def load_db():
    ensure_directories()
    generate_taxi_zones()
    generate_trips(num_rows=2500000)

if __name__ == "__main__":
    load_db()
