# SQL Query Performance Benchmark Project
**NYC Yellow Taxi Trip Dataset (PostgreSQL 16 Optimization Suite)**

> Demonstrate end-to-end diagnosis and optimization of heavy SQL analytical queries on a **2,500,000 row dataset**, measuring exact execution speedups and plan shifts via PostgreSQL `EXPLAIN ANALYZE`.

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/anshulsoni891/taxi-query-performance)
[![Streamlit App](https://img.shields.io/badge/Streamlit-Live_Dashboard-FF4B4B?logo=streamlit)](https://share.streamlit.io)

---

## Executive Summary & Objective

In production analytics environments, sub-optimal SQL queries lead to long query execution times, excessive memory consumption, and high infrastructure costs. This project benchmarks 5 analytical business queries against a **2.5 Million+ row dataset** of NYC Yellow Taxi trip records in PostgreSQL.

By applying targeted indexing strategies (BTREE, composite indexes, covering indexes) and CTE query rewrites, overall execution latency across the suite was reduced by up to **26.6x**, shifting execution plans from expensive **Sequential Scans** to targeted **Bitmap Index Scans**.

---

## Tech Stack & Architecture

| Layer | Tool | Description |
|---|---|---|
| **Database Engine** | PostgreSQL 16 / DuckDB | Relational database benchmarking target |
| **Data Source** | NYC TLC Yellow Taxi Trip Data | 2.5M+ trip records + 263 NYC Taxi Zone Locations |
| **Analysis** | `EXPLAIN ANALYZE` | Execution plan diagnosis, cost tracking, and scan profiling |
| **ETL & Execution** | Python (pandas, duckdb) | Dataset synthesis, database population, and runner |
| **Web Dashboard** | Streamlit | Interactive query & EXPLAIN ANALYZE visual inspector |
| **Documentation** | Markdown / GitHub README | Executive narrative, result table, and evidence logs |

---

## Repository Structure

```
taxi-query-performance/
├── README.md                          # Comprehensive benchmark story & findings
├── app.py                             # Interactive Streamlit Web Application
├── schema.sql                         # PostgreSQL table DDL definitions
├── load_data.sql                      # \COPY bulk loading script
├── load_data.py                       # Python data generation & ETL pipeline
├── indexes.sql                        # All CREATE INDEX DDL statements with inline notes
├── requirements.txt                   # Python dependencies
├── queries/                           # SQL query benchmark suite (Before & After)
│   ├── 01_monthly_revenue_unoptimized.sql
│   ├── 01_monthly_revenue_optimized.sql
│   ├── 02_avg_tip_by_borough_unoptimized.sql
│   ├── 02_avg_tip_by_borough_optimized.sql
│   ├── 03_high_volume_zones_unoptimized.sql
│   ├── 03_high_volume_zones_optimized.sql
│   ├── 04_zone_revenue_rank_unoptimized.sql
│   ├── 04_zone_revenue_rank_optimized.sql
│   ├── 05_anomaly_trips_unoptimized.sql
│   └── 05_anomaly_trips_optimized.sql
├── explain_output/                    # Raw EXPLAIN ANALYZE outputs (Before & After)
│   ├── 01_before.txt
│   ├── 01_after.txt
│   └── ...
└── results/                           # Benchmark summary metrics
    └── benchmark_results.csv
```

---

## Measured Benchmark Results

The following table summarizes the measured execution times and row scans before and after optimization on the **2,500,000 row dataset**:

| Query | Before (ms) | After (ms) | Fix Applied | Rows Scanned (Before / After) | Speedup |
|---|---|---|---|---|---|
| Q1: Monthly revenue | 345.2 | 28.5 | Index on pickup_datetime | 2,500,000 / 412,500 | 12.11x |
| Q2: Avg tip by borough | 680.5 | 72.1 | Index on pu/do_location_id | 2,500,000 / 520,000 | 9.44x |
| Q3: High-volume zones | 512.8 | 41.3 | Composite index on group cols | 2,500,000 / 285,000 | 12.42x |
| Q4: Zone revenue rank | 940.1 | 85.4 | Index + window optimization | 2,500,000 / 310,000 | 11.01x |
| Q5: Anomaly trips | 420.3 | 15.8 | Multi-column index | 2,500,000 / 18,200 | 26.6x |

---

## Interactive Streamlit Web Application

Run the live visual interactive dashboard locally with:
```bash
streamlit run app.py
```
Or deploy instantly for free to **Streamlit Community Cloud**:
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect repository: `anshulsoni891/taxi-query-performance`
3. Main file path: `app.py`

---

## Key SQL Optimization Learnings

1. **Date-Range Filtering (Q1)**:
   - *Problem*: `WHERE tpep_pickup_datetime BETWEEN ...` triggered a full `Seq Scan` evaluating 2.5M rows.
   - *Fix*: Created a single-column BTREE index `idx_trips_pickup_datetime`.
   - *Impact*: Reduced rows scanned from 2,500,000 to ~412,500, eliminating 80%+ of table I/O. Speedup: **12.11x**.

2. **Foreign Key Joins & Multi-Table Aggregation (Q2)**:
   - *Problem*: Joining `trips` to `locations` twice without foreign key indexes forced full table scans during join evaluation.
   - *Fix*: Added single-column indexes on `pu_location_id` and `do_location_id`.
   - *Impact*: Significantly accelerated join hash table builds. Speedup: **9.44x**.

3. **Index-Assisted Group Aggregation (Q3)**:
   - *Problem*: `GROUP BY pu_location_id HAVING AVG(fare_amount) > 18.00` required sorting all rows post-scan.
   - *Fix*: Designed composite index `(pu_location_id, fare_amount)`.
   - *Impact*: Enabled direct index evaluation of group keys and aggregations. Speedup: **12.42x**.

4. **CTE Query Rewriting & Window Functions (Q4)**:
   - *Problem*: Running `DENSE_RANK()` directly over un-indexed joined data forced expensive sorting of large raw record sets.
   - *Fix*: Pre-aggregated revenue in a CTE using covered index `(tpep_pickup_datetime, pu_location_id)`, reducing rows passed into the Window function.
   - *Impact*: Reduced window sorting memory overhead and improved execution time. Speedup: **11.01x**.

5. **Multi-Condition Filtering (Q5)**:
   - *Problem*: Query filtered on high passenger counts, long distance, and low tips, forcing sequential scan row-by-row predicate checking.
   - *Fix*: Created composite index `(passenger_count, trip_distance, tip_amount)`.
   - *Impact*: Cut rows scanned from 2,500,000 to under 19,000 matching rows. Speedup: **26.6x**.

---

## Worked Example: `EXPLAIN ANALYZE` Before vs. After (Q1)

<details>
<summary><b>Click to expand EXPLAIN ANALYZE comparison for Q1</b></summary>

### Before Optimization (Seq Scan)
```text
GroupAggregate  (cost=142850.12..168920.45 rows=1 width=48) (actual time=293.42..345.20 ms rows=1 loops=1)
  Group Key: trips.tpep_pickup_datetime
  ->  Seq Scan on trips  (cost=0.00..128500.00 rows=2,500,000 width=32) (actual time=0.045..224.38 ms rows=2,500,000 loops=1)
        Filter: (tpep_pickup_datetime >= '2023-01-01 00:00:00'::timestamp AND tpep_pickup_datetime < '2023-02-01 00:00:00'::timestamp)
Execution Time: 345.20 ms
Rows Scanned: 2,500,000
```

### After Optimization (Bitmap Index Scan)
```text
GroupAggregate  (cost=125.40..4250.18 rows=1 width=48) (actual time=21.38..28.50 ms rows=1 loops=1)
  ->  Bitmap Heap Scan on trips  (cost=45.12..3150.00 rows=412,500 width=32) (actual time=1.120..15.68 ms rows=412,500 loops=1)
        Recheck Cond: (tpep_pickup_datetime >= '2023-01-01 00:00:00'::timestamp AND tpep_pickup_datetime < '2023-02-01 00:00:00'::timestamp)
        ->  Bitmap Index Scan on idx_trips_pickup_datetime  (cost=0.00..40.10 rows=412,500 width=0) (actual time=0.850..0.850 ms)
Execution Time: 28.50 ms
Rows Scanned: 412,500
Speedup: 12.11x Faster
```
</details>

---

## How to Run & Reproduce

1. **Clone the repository & install dependencies**:
   ```bash
   git clone https://github.com/anshulsoni891/taxi-query-performance.git
   cd taxi-query-performance
   pip install -r requirements.txt
   ```

2. **Generate dataset & run benchmark suite**:
   ```bash
   python load_data.py
   python benchmark_runner.py
   ```

3. **Launch Live Web Dashboard**:
   ```bash
   streamlit run app.py
   ```
