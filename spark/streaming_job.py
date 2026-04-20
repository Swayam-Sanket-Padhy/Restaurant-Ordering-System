# ============================================
# RESTAURANT ORDERING SYSTEM -- SPARK STREAMING
# Swayam Sanket Padhy | Roll No: 2306239
# Data Engineering 2025-2026 | KIIT University
# ============================================

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    from_json, col, sum as _sum, count, avg,
    window, current_timestamp, round as _round
)
from pyspark.sql.types import (
    StructType, StructField, StringType,
    IntegerType, DoubleType, TimestampType
)

KAFKA_BROKER  = "localhost:9092"
CHECKPOINT    = "/tmp/restaurant_checkpoints"
OUTPUT_PATH   = "/tmp/restaurant_output"

ORDER_SCHEMA = StructType([
    StructField("order_id",        IntegerType()),
    StructField("table_id",        IntegerType()),
    StructField("customer_id",     IntegerType()),
    StructField("menu_item_id",    IntegerType()),
    StructField("item_name",       StringType()),
    StructField("category",        StringType()),
    StructField("quantity",        IntegerType()),
    StructField("amount",          DoubleType()),
    StructField("payment_method",  StringType()),
    StructField("section",         StringType()),
    StructField("loyalty_tier",    StringType()),
    StructField("staff_id",        IntegerType()),
    StructField("entry_time",      StringType()),
    StructField("status",          StringType()),
])

def create_spark_session():
    return SparkSession.builder \
        .appName("RestaurantOrderingSystem") \
        .config("spark.jars.packages",
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()

def read_kafka_stream(spark):
    return spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("subscribe", "orders") \
        .option("startingOffsets", "latest") \
        .load()

def parse_orders(raw_df):
    return raw_df \
        .selectExpr("CAST(value AS STRING) as json_str") \
        .select(from_json(col("json_str"), ORDER_SCHEMA).alias("data")) \
        .select("data.*") \
        .withColumn("event_time", current_timestamp())

def revenue_by_category(orders_df):
    return orders_df \
        .withWatermark("event_time", "2 minutes") \
        .groupBy(
            window(col("event_time"), "5 minutes", "1 minute"),
            col("category")
        ) \
        .agg(
            _sum("amount").alias("total_revenue"),
            count("order_id").alias("order_count"),
            _round(avg("amount"), 2).alias("avg_order_value")
        )

def revenue_by_table(orders_df):
    return orders_df \
        .withWatermark("event_time", "2 minutes") \
        .groupBy(
            window(col("event_time"), "5 minutes", "1 minute"),
            col("table_id"),
            col("section")
        ) \
        .agg(
            _sum("amount").alias("table_revenue"),
            count("order_id").alias("orders_served")
        )

def top_items_stream(orders_df):
    return orders_df \
        .withWatermark("event_time", "5 minutes") \
        .groupBy(
            window(col("event_time"), "10 minutes", "2 minutes"),
            col("item_name"),
            col("category")
        ) \
        .agg(
            _sum("quantity").alias("total_qty_sold"),
            _sum("amount").alias("item_revenue")
        ) \
        .orderBy("total_qty_sold", ascending=False)

def write_stream(df, name, output_mode="update"):
    return df.writeStream \
        .outputMode(output_mode) \
        .format("parquet") \
        .option("path", f"{OUTPUT_PATH}/{name}") \
        .option("checkpointLocation", f"{CHECKPOINT}/{name}") \
        .trigger(processingTime="30 seconds") \
        .start()

def write_console(df, name, output_mode="update"):
    return df.writeStream \
        .outputMode(output_mode) \
        .format("console") \
        .option("truncate", False) \
        .option("numRows", 10) \
        .queryName(name) \
        .start()

if __name__ == "__main__":
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    print("Restaurant Spark Streaming Job started...")

    raw      = read_kafka_stream(spark)
    orders   = parse_orders(raw)

    cat_rev  = revenue_by_category(orders)
    tbl_rev  = revenue_by_table(orders)
    top_items = top_items_stream(orders)

    q1 = write_console(cat_rev,   "category_revenue")
    q2 = write_console(tbl_rev,   "table_revenue")
    q3 = write_console(top_items, "top_items")

    q1.awaitTermination()
