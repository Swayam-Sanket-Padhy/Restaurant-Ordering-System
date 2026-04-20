# ============================================
# RESTAURANT ORDERING SYSTEM -- SPARK BATCH ETL
# Swayam Sanket Padhy | Roll No: 2306239
# Data Engineering 2025-2026 | KIIT University
# ============================================

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, to_date, hour, dayofweek, month, year,
    when, lit, current_timestamp, round as _round,
    sum as _sum, count, avg, max as _max, min as _min
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RestaurantBatchETL")

PARQUET_INPUT  = "/tmp/restaurant_output/orders"
POSTGRES_URL   = "jdbc:postgresql://localhost:5432/restaurant_db"
POSTGRES_PROPS = {
    "user":     "postgres",
    "password": "postgres",
    "driver":   "org.postgresql.Driver"
}

def create_spark_session():
    return SparkSession.builder \
        .appName("RestaurantBatchTransform") \
        .config("spark.jars",
                "https://jdbc.postgresql.org/download/postgresql-42.6.0.jar") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()

def read_raw_orders(spark):
    logger.info("Reading raw Parquet orders...")
    return spark.read.parquet(PARQUET_INPUT)

def build_dim_time(orders_df):
    logger.info("Building DIM_TIME...")
    return orders_df \
        .select(col("entry_time").cast("timestamp").alias("ts")) \
        .distinct() \
        .withColumn("full_date",   to_date(col("ts"))) \
        .withColumn("hour",        hour(col("ts"))) \
        .withColumn("day_of_week", dayofweek(col("ts"))) \
        .withColumn("month",       month(col("ts"))) \
        .withColumn("year",        year(col("ts"))) \
        .withColumn("is_weekend",
            when(dayofweek(col("ts")).isin([1, 7]), lit(True))
            .otherwise(lit(False))
        ) \
        .drop("ts")

def build_dim_menu_item(orders_df):
    logger.info("Building DIM_MENU_ITEM...")
    return orders_df \
        .select(
            col("menu_item_id"),
            col("item_name").alias("name"),
            col("category"),
        ) \
        .distinct() \
        .withColumn("is_available", lit(True))

def build_dim_customer(orders_df):
    logger.info("Building DIM_CUSTOMER...")
    return orders_df \
        .select(
            col("customer_id"),
            col("loyalty_tier")
        ) \
        .distinct() \
        .withColumn("name",    lit("Customer_" + col("customer_id").cast("string"))) \
        .withColumn("contact", lit("N/A"))

def build_dim_staff(orders_df):
    logger.info("Building DIM_STAFF...")
    return orders_df \
        .select(col("staff_id")) \
        .distinct() \
        .withColumn("name",  lit("Staff_" + col("staff_id").cast("string"))) \
        .withColumn("role",  lit("Waiter")) \
        .withColumn("shift", when(col("staff_id") % 2 == 0,
                                  lit("Morning")).otherwise(lit("Evening")))

def build_dim_payment(orders_df):
    logger.info("Building DIM_PAYMENT...")
    return orders_df \
        .select(
            col("payment_method").alias("method"),
        ) \
        .distinct() \
        .withColumn("status",          lit("success")) \
        .withColumn("transaction_ref", lit("BATCH_LOAD"))

def build_fact_order(orders_df):
    logger.info("Building FACT_ORDER...")
    return orders_df \
        .select(
            col("order_id"),
            col("table_id"),
            col("customer_id"),
            col("menu_item_id"),
            col("staff_id"),
            col("quantity"),
            col("amount"),
            col("entry_time").cast("timestamp").alias("entry_time"),
            col("entry_time").cast("timestamp").alias("exit_time"),
        ) \
        .withColumn("loaded_at", current_timestamp())

def write_to_postgres(df, table_name, mode="append"):
    logger.info(f"Writing {table_name} to PostgreSQL...")
    df.write.jdbc(
        url=POSTGRES_URL,
        table=table_name,
        mode=mode,
        properties=POSTGRES_PROPS
    )
    logger.info(f"{table_name} written successfully.")

def run_summary_report(orders_df):
    logger.info("Generating batch summary report...")
    summary = orders_df.agg(
        count("order_id").alias("total_orders"),
        _round(_sum("amount"), 2).alias("total_revenue"),
        _round(avg("amount"), 2).alias("avg_order_value"),
        _max("amount").alias("max_order"),
        _min("amount").alias("min_order")
    )
    summary.show()

if __name__ == "__main__":
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    logger.info("Starting Restaurant Batch ETL Job...")

    orders = read_raw_orders(spark)
    orders.cache()

    run_summary_report(orders)

    write_to_postgres(build_dim_time(orders),      "dim_time",      mode="overwrite")
    write_to_postgres(build_dim_menu_item(orders),  "dim_menu_item", mode="overwrite")
    write_to_postgres(build_dim_customer(ord
