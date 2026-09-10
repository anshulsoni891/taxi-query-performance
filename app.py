import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="NYC Taxi SQL Benchmark Suite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_CSV = os.path.join(PROJECT_DIR, "results", "benchmark_results.csv")
EXPLAIN_DIR = os.path.join(PROJECT_DIR, "explain_output")
QUERIES_DIR = os.path.join(PROJECT_DIR, "queries")

st.title("⚡ NYC Yellow Taxi SQL Query Performance Benchmark")
st.markdown("""
**PostgreSQL 16 Analytical Query Optimization Suite**  
*Demonstrating SQL Query Diagnosis, Index Optimization (BTREE, Composite, Covering), and EXPLAIN ANALYZE Plan Transformations on a **2,500,000 Row Dataset**.*
""")

st.divider()

# Load Results CSV
if os.path.exists(RESULTS_CSV):
    df_results = pd.read_csv(RESULTS_CSV)
else:
    st.error("Benchmark results CSV not found. Please run `python benchmark_runner.py` first.")
    st.stop()

# Key Metrics Overview
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Dataset Size", value="2,500,000 rows", delta="NYC TLC Yellow Taxi")
with col2:
    st.metric(label="Max Query Speedup", value="26.6x Faster", delta="Q5: Anomaly Filtering")
with col3:
    st.metric(label="Avg Suite Speedup", value="14.3x Faster", delta="Across 5 Benchmark Queries")
with col4:
    st.metric(label="Scan Optimization", value="Seq Scan -> Index Scan", delta="90%+ Row I/O Reduction")

st.divider()

# Performance Charts & Comparison Table
st.header("📊 Benchmark Performance Summary")

col_chart, col_data = st.columns([1, 1])

with col_chart:
    st.subheader("Execution Time Comparison (ms)")
    chart_df = df_results[["Query", "Before (ms)", "After (ms)"]].set_index("Query")
    st.bar_chart(chart_df)

with col_data:
    st.subheader("Benchmark Metrics Data")
    st.dataframe(
        df_results,
        use_container_width=True,
        hide_index=True
    )

st.divider()

# Detailed Query Inspector
st.header("🔍 Interactive Query & EXPLAIN ANALYZE Inspector")

query_options = {
    "Q1: Monthly revenue": ("01", "01_monthly_revenue_unoptimized.sql", "01_monthly_revenue_optimized.sql"),
    "Q2: Avg tip by borough": ("02", "02_avg_tip_by_borough_unoptimized.sql", "02_avg_tip_by_borough_optimized.sql"),
    "Q3: High-volume zones": ("03", "03_high_volume_zones_unoptimized.sql", "03_high_volume_zones_optimized.sql"),
    "Q4: Zone revenue rank": ("04", "04_zone_revenue_rank_unoptimized.sql", "04_zone_revenue_rank_optimized.sql"),
    "Q5: Anomaly trips": ("05", "05_anomaly_trips_unoptimized.sql", "05_anomaly_trips_optimized.sql")
}

selected_q_name = st.selectbox("Select a Benchmark Query to Deep-Dive:", list(query_options.keys()))
qid, unopt_file, opt_file = query_options[selected_q_name]

# Read SQL files
with open(os.path.join(QUERIES_DIR, unopt_file), "r", encoding="utf-8") as f:
    sql_unopt = f.read()

with open(os.path.join(QUERIES_DIR, opt_file), "r", encoding="utf-8") as f:
    sql_opt = f.read()

# Read EXPLAIN outputs
before_txt_file = os.path.join(EXPLAIN_DIR, f"{qid}_before.txt")
after_txt_file = os.path.join(EXPLAIN_DIR, f"{qid}_after.txt")

explain_before = open(before_txt_file, "r", encoding="utf-8").read() if os.path.exists(before_txt_file) else "N/A"
explain_after = open(after_txt_file, "r", encoding="utf-8").read() if os.path.exists(after_txt_file) else "N/A"

q_row = df_results[df_results["Query"] == selected_q_name].iloc[0]

st.subheader(f"Query Strategy & Fix: `{q_row['Fix Applied']}`")
st.info(f"**Speedup**: {q_row['Speedup']} | **Before**: {q_row['Before (ms)']} ms | **After**: {q_row['After (ms)']} ms | **Rows Scanned**: {q_row['Rows Scanned (Before / After)']}")

col_sql_unopt, col_sql_opt = st.columns(2)

with col_sql_unopt:
    st.markdown("### 🔴 Unoptimized SQL")
    st.code(sql_unopt, language="sql")
    with st.expander("Show Unoptimized EXPLAIN ANALYZE"):
        st.code(explain_before, language="text")

with col_sql_opt:
    st.markdown("### 🟢 Optimized SQL")
    st.code(sql_opt, language="sql")
    with st.expander("Show Optimized EXPLAIN ANALYZE"):
        st.code(explain_after, language="text")

st.sidebar.title("📌 About Project")
st.sidebar.markdown("""
**Query Performance Benchmark Project**
- **Engine**: PostgreSQL 16
- **Dataset**: NYC TLC Yellow Taxi (2.5M Rows)
- **Author**: Anshul Soni
- **GitHub Repository**: [GitHub Link](https://github.com/anshulsoni891/taxi-query-performance)
""")
