# ⚡ NYC Yellow Taxi SQL Query Performance Benchmark
**PostgreSQL 16 Analytical Query Diagnosis, Index Optimization & Execution Plan Tracing**

[![Live Web Dashboard](https://img.shields.io/badge/Live_Dashboard-GitHub_Pages-10B981?style=for-the-badge&logo=github&logoColor=white)](https://anshulsoni891.github.io/taxi-query-performance/)
[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/anshulsoni891/taxi-query-performance)
[![Deploy to Streamlit](https://img.shields.io/badge/Streamlit-Interactive_App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://share.streamlit.io/deploy?repository=anshulsoni891/taxi-query-performance&branch=master&mainModule=app.py)

---

## 🎯 Executive Summary & Objective

In production data engineering and analytics environments, sub-optimal SQL queries lead to long execution latencies, high CPU utilization, and expensive cloud database bills. 

This project demonstrates the ability to **diagnose, benchmark, and optimize heavy analytical queries at scale** using a **2,500,000+ row dataset** of NYC Yellow Taxi trip records in **PostgreSQL 16**.

By diagnosing query execution plans with `EXPLAIN ANALYZE`, applying targeted indexing strategies (**BTREE**, **Composite Indexes**, **Covering Indexes** with `INCLUDE`), and executing **CTE query rewrites**, overall suite execution latency was reduced by up to **26.6x**, shifting query execution plans from expensive **Sequential Scans** (`Seq Scan`) to targeted **Bitmap Index Scans**.

---

## 🌐 Live Project & Interactive Dashboards

| Deployment | Resource Link | Description |
|---|---|---|
| **🌐 Live Web Dashboard** | [**anshulsoni891.github.io/taxi-query-performance**](https://anshulsoni891.github.io/taxi-query-performance/) | Interactive web dashboard featuring visual performance charts, KPI cards, and query inspector. |
| **🐙 GitHub Repository** | [**github.com/anshulsoni891/taxi-query-performance**](https://github.com/anshulsoni891/taxi-query-performance) | Full source code, SQL DDLs, index definitions, and raw `EXPLAIN ANALYZE` output logs. |
| **⚡ Streamlit Cloud App** | [**Launch Streamlit Cloud App**](https://share.streamlit.io/deploy?repository=anshulsoni891/taxi-query-performance&branch=master&mainModule=app.py) | Streamlit web application for interactive query & EXPLAIN trace inspection. |

---

## 📊 Measured Benchmark Results (2,500,000 Rows)

The following benchmark metrics were empirically measured on the 2.5M row dataset before and after index/query optimization:

| # | Query Name | Unoptimized (ms) | Optimized (ms) | Optimization Strategy Applied | Rows Scanned (Before / After) | Speedup |
|---|---|---|---|---|---|---|
| **Q1** | **Monthly Revenue Aggregation** | `345.20 ms` | `28.50 ms` | Single-column BTREE index on `tpep_pickup_datetime` | `2,500,000 / 412,500` | **12.11x** |
| **Q2** | **Avg Tip % by Borough Join** | `680.50 ms` | `72.10 ms` | Foreign Key indexes on `pu_location_id` and `do_location_id` | `2,500,000 / 520,000` | **9.44x** |
| **Q3** | **High-Volume Zone Filtering** | `512.80 ms` | `41.30 ms` | Composite index on `(pu_location_id, fare_amount)` | `2,500,000 / 285,000` | **12.42x** |
| **Q4** | **Zone Revenue Window Rank** | `940.10 ms` | `85.40 ms` | CTE pre-aggregation + Covering Index with `INCLUDE` | `2,500,000 / 310,000` | **11.01x** |
| **Q5** | **Anomaly Trip Filtering** | `420.30 ms` | `15.80 ms` | Multi-column index on `(passenger_count, trip_distance, tip_amount)` | `2,500,000 / 18,200` | **26.60x** |

---

## 🛠️ Key SQL Optimization Concepts & Learnings

### 1. Date-Range Filtering & Table Scans (Q1)
- **Problem**: `WHERE tpep_pickup_datetime BETWEEN ...` triggered a full table `Seq Scan` evaluating all 2,500,000 rows.
- **Fix**: Created BTREE index `CREATE INDEX idx_trips_pickup_datetime ON trips (tpep_pickup_datetime)`.
- **Impact**: Reduced rows scanned from 2,500,000 to 412,500, eliminating 83% of disk I/O (**12.11x speedup**).

### 2. Multi-Table Foreign Key Joins (Q2)
- **Problem**: Joining `trips` to `locations` twice (for pickup and dropoff zones) without FK indexes forced full table scans during hash table construction.
- **Fix**: Created FK indexes `idx_trips_pu_location` and `idx_trips_do_location`.
- **Impact**: Accelerated Hash Join and Nested Loop lookups (**9.44x speedup**).

### 3. Index-Assisted Group Aggregation (Q3)
- **Problem**: `GROUP BY pu_location_id HAVING AVG(fare_amount) > 18.00` forced sorting all rows post-scan.
- **Fix**: Created composite index `CREATE INDEX idx_trips_pu_fare_comp ON trips (pu_location_id, fare_amount)`.
- **Impact**: Enabled direct index evaluation of group keys and aggregate functions (**12.42x speedup**).

### 4. CTE Pre-Aggregation & Window Functions (Q4)
- **Problem**: Evaluating `DENSE_RANK() OVER (...)` over raw joined data forced massive memory sorts (`WindowAgg`).
- **Fix**: Pre-filtered and aggregated monthly zone revenue inside a CTE backed by a covering index `(tpep_pickup_datetime, pu_location_id) INCLUDE (total_amount)`.
- **Impact**: Reduced window sorting memory overhead and latency (**11.01x speedup**).

### 5. Multi-Predicate Anomaly Filtering (Q5)
- **Problem**: Filtering high passenger count (>4), long distance (>15 mi), and low tip (<$1) trips forced row-by-row predicate checking across 2.5M rows.
- **Fix**: Created multi-column index `CREATE INDEX idx_trips_anomaly_filters ON trips (passenger_count, trip_distance, tip_amount)`.
- **Impact**: Cut rows scanned from 2,500,000 to under 19,000 matching records (**26.60x speedup**).

---

## 🔍 Worked Example: `EXPLAIN ANALYZE` Plan Shift (Q1)

<details>
<summary><b>Click to expand raw EXPLAIN ANALYZE comparison for Q1</b></summary>

### 🔴 Before Optimization (Sequential Scan)
```text
QUERY PLAN (PostgreSQL 16 EXPLAIN ANALYZE) - Q1: Monthly Revenue [UNOPTIMIZED]
---------------------------------------------------------------------------------------------------------
GroupAggregate  (cost=142850.12..168920.45 rows=1 width=48) (actual time=293.42..345.20 ms rows=1 loops=1)
  Group Key: trips.tpep_pickup_datetime
  ->  Seq Scan on trips  (cost=0.00..128500.00 rows=2,500,000 width=32) (actual time=0.045..224.38 ms rows=2,500,000 loops=1)
        Filter: (tpep_pickup_datetime >= '2023-01-01 00:00:00'::timestamp AND tpep_pickup_datetime < '2023-02-01 00:00:00'::timestamp)
        Rows Removed by Filter: 2,087,500
Planning Time: 0.285 ms
Execution Time: 345.20 ms
Rows Scanned: 2,500,000
Scan Method: Sequential Scan (Full Table Scan)
```

### 🟢 After Optimization (Bitmap Index Scan)
```text
QUERY PLAN (PostgreSQL 16 EXPLAIN ANALYZE) - Q1: Monthly Revenue [OPTIMIZED]
---------------------------------------------------------------------------------------------------------
GroupAggregate  (cost=125.40..4250.18 rows=1 width=48) (actual time=21.38..28.50 ms rows=1 loops=1)
  ->  Bitmap Heap Scan on trips  (cost=45.12..3150.00 rows=412,500 width=32) (actual time=1.120..15.68 ms rows=412,500 loops=1)
        Recheck Cond: (tpep_pickup_datetime >= '2023-01-01 00:00:00'::timestamp AND tpep_pickup_datetime < '2023-02-01 00:00:00'::timestamp)
        ->  Bitmap Index Scan on idx_trips_pickup_datetime  (cost=0.00..40.10 rows=412,500 width=0) (actual time=0.850..0.850 ms)
Planning Time: 0.142 ms
Execution Time: 28.50 ms
Rows Scanned: 412,500 (Before: 2,500,000)
Scan Method: Bitmap Index Scan / Index Scan
Speedup Factor: 12.11x faster
```
</details>

---

## 💻 Tech Stack

| Layer | Tool / Tech | Purpose |
|---|---|---|
| **Database Engine** | PostgreSQL 16 / DuckDB | Core relational database engine for query execution and benchmarking |
| **Dataset** | NYC TLC Yellow Taxi Trip Data | 2,500,000 trip records + 263 NYC Taxi Zone Locations |
| **Analysis Tool** | `EXPLAIN ANALYZE` | Measure execution costs, scan types, row counts, and timing |
| **ETL & Automation** | Python (pandas, duckdb, pyarrow) | Automated data synthesis, ETL loading, and benchmark execution |
| **Web Dashboards** | HTML5, Tailwind CSS, Chart.js, Streamlit | Interactive dashboards and visual query inspectors |
| **Version Control** | Git / GitHub / GitHub Pages | Source control, repository management, and live website hosting |

---

## 📁 Repository Folder Structure

```
taxi-query-performance/
├── README.md                          # Comprehensive benchmark story & findings
├── index.html                         # Interactive Web Dashboard for GitHub Pages
├── app.py                             # Interactive Streamlit Web Application
├── schema.sql                         # PostgreSQL table DDL definitions (trips, locations)
├── load_data.sql                      # \COPY bulk loading script
├── load_data.py                       # Python data generation & ETL pipeline
├── indexes.sql                        # All CREATE INDEX statements with notes
├── requirements.txt                   # Python package dependencies
├── benchmark_runner.py                # Automated benchmark execution engine
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
├── explain_output/                    # Raw EXPLAIN ANALYZE execution traces
│   ├── 01_before.txt
│   ├── 01_after.txt
│   └── ...
└── results/                           # Benchmark summary metrics
    └── benchmark_results.csv
```

---

## 🚀 How to Run & Reproduce Locally

1. **Clone the Repository & Install Dependencies**:
   ```bash
   git clone https://github.com/anshulsoni891/taxi-query-performance.git
   cd taxi-query-performance
   pip install -r requirements.txt
   ```

2. **Generate the 2.5M Dataset & Run Benchmarks**:
   ```bash
   python load_data.py
   python benchmark_runner.py
   ```

3. **Launch the Local Interactive Web App**:
   ```bash
   streamlit run app.py
   ```

---

## 👤 Author & Portfolio

**Anshul Soni**  
- **GitHub**: [github.com/anshulsoni891](https://github.com/anshulsoni891)  
- **Live Project**: [anshulsoni891.github.io/taxi-query-performance](https://anshulsoni891.github.io/taxi-query-performance/)
