#!/bin/bash
# ============================================
# RESTAURANT ORDERING SYSTEM -- SETUP SCRIPT
# Swayam Sanket Padhy | Roll No: 2306239
# Data Engineering 2025-2026 | KIIT University
# ============================================

set -e

echo "============================================"
echo " Restaurant Ordering System -- Setup"
echo " Swayam Sanket Padhy | Roll No: 2306239"
echo " KIIT University | Data Engineering 2025-26"
echo "============================================"

# ── Check Prerequisites ─────────────────────────────────

echo ""
echo "[1/6] Checking prerequisites..."

command -v docker        >/dev/null 2>&1 || { echo "ERROR: Docker not installed.";        exit 1; }
command -v docker-compose>/dev/null 2>&1 || { echo "ERROR: Docker Compose not installed."; exit 1; }
command -v python3       >/dev/null 2>&1 || { echo "ERROR: Python3 not installed.";        exit 1; }
command -v java          >/dev/null 2>&1 || { echo "ERROR: Java not installed.";           exit 1; }

echo "  Docker        -- OK"
echo "  Docker Compose -- OK"
echo "  Python3       -- OK"
echo "  Java          -- OK"

# ── Install Python Dependencies ─────────────────────────

echo ""
echo "[2/6] Installing Python dependencies..."
pip install -r requirements.txt --quiet
echo "  Python dependencies installed -- OK"

# ── Start Docker Services ────────────────────────────────

echo ""
echo "[3/6] Starting Docker services..."
docker-compose -f docker/docker-compose.yml up -d

echo "  Waiting for services to be ready..."
sleep 20

echo "  Zookeeper  -- started"
echo "  Kafka      -- started"
echo "  PostgreSQL -- started"
echo "  Redis      -- started"
echo "  Airflow    -- started"
echo "  Grafana    -- started"
echo "  FastAPI    -- started"

# ── Create Kafka Topics ──────────────────────────────────

echo ""
echo "[4/6] Creating Kafka topics..."

docker exec restaurant_kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create --if-not-exists \
  --topic orders \
  --partitions 3 \
  --replication-factor 1

docker exec restaurant_kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create --if-not-exists \
  --topic payments \
  --partitions 3 \
  --replication-factor 1

docker exec restaurant_kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create --if-not-exists \
  --topic inventory \
  --partitions 2 \
  --replication-factor 1

docker exec restaurant_kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create --if-not-exists \
  --topic feedback \
  --partitions 2 \
  --replication-factor 1

echo "  Kafka topics created -- OK"

# ── Initialize PostgreSQL Schema ─────────────────────────

echo ""
echo "[5/6] Initializing PostgreSQL schema..."

docker exec -i restaurant_postgres psql \
  -U postgres \
  -d restaurant_db \
  < sql/schema.sql

echo "  Star schema created -- OK"

# ── Final Summary ────────────────────────────────────────

echo ""
echo "[6/6] Setup complete!"
echo ""
echo "============================================"
echo " Services running:"
echo "  Airflow    --> http://localhost:8080  (admin/admin)"
echo "  Grafana    --> http://localhost:3000  (admin/admin)"
echo "  FastAPI    --> http://localhost:8000"
echo "  API Docs   --> http://localhost:8000/docs"
echo "============================================"
echo ""
echo " Next steps:"
echo "  1. python kafka/producer.py"
echo "  2. spark-submit spark/streaming_job.py"
echo "  3. streamlit run streamlit/dashboard.py"
echo ""
echo " Swayam Sanket Padhy | 2306239 | KIIT"
echo "============================================"
