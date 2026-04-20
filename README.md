# Restaurant Ordering System

Swayam Sanket Padhy | Roll No: 2306239 | Course: Data Engineering 2025–2026 | KIIT University

# Problem Statement

Manual restaurant order management causes billing errors, long wait times, and zero real-time visibility into sales and inventory. This project builds a fully automated, cloud-native data pipeline that ingests live POS and mobile app order events, processes them in real time using Apache Kafka and PySpark Structured Streaming, stores them in a PostgreSQL data warehouse with a star schema, and exposes live KPI dashboards via Grafana and Streamlit.


# Architecture

POS Terminal / Mobile App / Menu API / Payment Events
↓
Apache Kafka (orders, payments, inventory, feedback topics)
↓
PySpark Structured Streaming → S3 Raw (Parquet)
↓
Great Expectations (Data Quality Checks)
↓
Redis Cache (live counters)    PostgreSQL DWH (Star Schema)
↓
Apache Airflow (nightly batch ETL)
↓
Grafana Dashboard        Streamlit Analytics App


# Project Structure

restaurant-ordering-system/
├── kafka/
│   ├── producer.py
│   └── consumer_test.py
├── spark/
│   ├── streaming_job.py
│   └── batch_transform.py
├── airflow/
│   └── dags/
│       └── restaurant_etl.py
├── sql/
│   ├── schema.sql
│   └── queries.sql
├── great_expectations/
│   └── checkpoints/
│       └── orders_checkpoint.py
├── api/
│   └── app.py
├── streamlit/
│   └── dashboard.py
├── terraform/
│   └── main.tf
├── docker/
│   └── docker-compose.yml
├── scripts/
│   ├── setup.sh
│   └── test_producer.py
├── requirements.txt
└── README.md


# Tech Stack

| Layer | Technology |
|---|---|
| Ingestion | Apache Kafka 3.6 |
| Streaming | PySpark 3.5 Structured Streaming |
| Orchestration | Apache Airflow 2.8 |
| Raw Storage | Amazon S3 (Parquet) |
| Data Warehouse | PostgreSQL |
| Cache | Redis (ElastiCache) |
| Data Quality | Great Expectations 0.18 |
| Visualization | Grafana 10 + Streamlit |
| API | FastAPI |
| IaC | Terraform 1.0 |
| Language | Python 3.11 |
| Container | Docker / Docker Compose |


# Quick Start (Local)


# Prerequisites

- Docker & Docker Compose installed
- Python 3.11+
- Java 11+ (for Spark)


## 1. Clone the repo

```bash
git clone https://github.com/your-username/restaurant-ordering-system.git
cd restaurant-ordering-system
```

## 2. Start local services

```bash
docker-compose -f docker/docker-compose.yml up -d
```

## 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

## 4. Run the Kafka producer (simulates restaurant orders)

```bash
python kafka/producer.py
```

## 5. Run the Spark Streaming job

```bash
spark-submit spark/streaming_job.py
```

## 6. Access Airflow UI

http://localhost:8080  (admin / admin)

## 7. Access Grafana

http://localhost:3000  (admin / admin)

## 8. Launch Streamlit Dashboard

```bash
streamlit run streamlit/dashboard.py
```


##  Star Schema

```sql
FACT_ORDER (order_id, table_id, customer_id, menu_item_id,
            staff_id, time_id, payment_id, quantity,
            amount, entry_time, exit_time)

DIM_TABLE       (table_id, section, capacity, status)
DIM_CUSTOMER    (customer_id, name, contact, loyalty_tier)
DIM_MENU_ITEM   (menu_item_id, name, category, price, is_available)
DIM_STAFF       (staff_id, name, role, shift)
DIM_TIME        (time_id, date, hour, day_of_week, is_weekend)
DIM_PAYMENT     (payment_id, method, status, transaction_ref)
```


Swayam Sanket Padhy | Roll No: 2306239 | Course: Data Engineering 2025–2026 | KIIT University
