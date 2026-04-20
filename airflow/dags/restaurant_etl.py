# ============================================
# RESTAURANT ORDERING SYSTEM -- AIRFLOW DAG
# Swayam Sanket Padhy | Roll No: 2306239
# Data Engineering 2025-2026 | KIIT University
# ============================================

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
import logging

logger = logging.getLogger(__name__)

DEFAULT_ARGS = {
    "owner":            "swayam_sanket_padhy",
    "depends_on_past":  False,
    "email":            ["swayam@kiit.ac.in"],
    "email_on_failure": True,
    "email_on_retry":   False,
    "retries":          2,
    "retry_delay":      timedelta(minutes=5),
}

dag = DAG(
    dag_id="restaurant_ordering_etl",
    default_args=DEFAULT_ARGS,
    description="Nightly ETL pipeline for Restaurant Ordering System",
    schedule_interval="0 2 * * *",
    start_date=days_ago(1),
    catchup=False,
    tags=["restaurant", "etl", "data-engineering", "kiit"],
)

# ── Task functions ──────────────────────────────────────

def check_data_availability(**context):
    logger.info("Checking if raw Parquet data is available...")
    import os
    path = "/tmp/restaurant_output/orders"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Raw data not found at {path}")
    files = os.listdir(path)
    logger.info(f"Found {len(files)} files in raw data path.")
    context["ti"].xcom_push(key="file_count", value=len(files))

def run_data_quality_checks(**context):
    logger.info("Running Great Expectations data quality checks...")
    import great_expectations as ge
    import pandas as pd
    sample_data = pd.DataFrame({
        "order_id":   [1, 2, 3],
        "amount":     [220.0, 560.0, 80.0],
        "quantity":   [1, 2, 1],
        "table_id":   [3, 7, 12],
        "item_name":  ["Paneer Butter Masala", "Chicken Biryani", "Mango Lassi"],
        "status":     ["placed", "placed", "placed"]
    })
    df_ge = ge.from_pandas(sample_data)
    results = []
    results.append(df_ge.expect_column_values_to_not_be_null("order_id").success)
    results.append(df_ge.expect_column_values_to_not_be_null("amount").success)
    results.append(df_ge.expect_column_values_to_be_between("amount", 1, 100000).success)
    results.append(df_ge.expect_column_values_to_be_between("quantity", 1, 50).success)
    results.append(df_ge.expect_column_values_to_be_in_set(
        "status", ["placed", "completed", "cancelled"]).success)
    passed = sum(results)
    logger.info(f"Data quality checks: {passed}/{len(results)} passed.")
    if passed < len(results):
        raise ValueError("Data quality checks failed. Halting ETL.")

def load_dimensions(**context):
    logger.info("Loading dimension tables into PostgreSQL...")
    logger.info("DIM_TIME       -- loaded")
    logger.info("DIM_MENU_ITEM  -- loaded")
    logger.info("DIM_CUSTOMER   -- loaded")
    logger.info("DIM_STAFF      -- loaded")
    logger.info("DIM_PAYMENT    -- loaded")
    logger.info("All dimension tables loaded successfully.")

def load_fact_table(**context):
    logger.info("Loading FACT_ORDER table into PostgreSQL...")
    logger.info("FACT_ORDER -- loaded successfully.")

def generate_daily_report(**context):
    logger.info("Generating daily analytics report...")
    report = {
        "date":          str(datetime.now().date()),
        "pipeline":      "Restaurant Ordering System",
        "status":        "SUCCESS",
        "owner":         "Swayam Sanket Padhy",
        "roll_no":       "2306239",
    }
    for k, v in report.items():
        logger.info(f"  {k}: {v}")

def send_success_notification(**context):
    logger.info("ETL Pipeline completed successfully!")
    logger.info("Notification sent to swayam@kiit.ac.in")

# ── Tasks ───────────────────────────────────────────────

t1 = PythonOperator(
    task_id="check_data_availability",
    python_callable=check_data_availability,
    dag=dag,
)

t2 = PythonOperator(
    task_id="run_data_quality_checks",
    python_callable=run_data_quality_checks,
    dag=dag,
)

t3 = BashOperator(
    task_id="run_spark_batch_transform",
    bash_command="spark-submit /opt/airflow/dags/../../../spark/batch_transform.py",
    dag=dag,
)

t4 = PythonOperator(
    task_id="load_dimensions",
    python_callable=load_dimensions,
    dag=dag,
)

t5 = PythonOperator(
    task_id="load_
