# ============================================
# RESTAURANT ORDERING SYSTEM -- TERRAFORM IaC
# Swayam Sanket Padhy | Roll No: 2306239
# Data Engineering 2025-2026 | KIIT University
# ============================================

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ── Variables ───────────────────────────────────────────

variable "aws_region" {
  description = "AWS region for all resources"
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Project name prefix"
  default     = "restaurant-ordering-system"
}

variable "environment" {
  description = "Deployment environment"
  default     = "dev"
}

# ── S3 Bucket -- Raw Data Lake ───────────────────────────

resource "aws_s3_bucket" "raw_data_lake" {
  bucket = "${var.project_name}-raw-data-lake-${var.environment}"
  tags = {
    Name        = "Restaurant Raw Data Lake"
    Project     = var.project_name
    Environment = var.environment
    Owner       = "Swayam Sanket Padhy"
    RollNo      = "2306239"
    University  = "KIIT University"
  }
}

resource "aws_s3_bucket_versioning" "raw_data_versioning" {
  bucket = aws_s3_bucket.raw_data_lake.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket" "processed_data" {
  bucket = "${var.project_name}-processed-${var.environment}"
  tags = {
    Name        = "Restaurant Processed Data"
    Project     = var.project_name
    Environment = var.environment
  }
}

# ── S3 Folders (prefixes) ────────────────────────────────

resource "aws_s3_object" "orders_prefix" {
  bucket  = aws_s3_bucket.raw_data_lake.id
  key     = "orders/"
  content = ""
}

resource "aws_s3_object" "payments_prefix" {
  bucket  = aws_s3_bucket.raw_data_lake.id
  key     = "payments/"
  content = ""
}

resource "aws_s3_object" "inventory_prefix" {
  bucket  = aws_s3_bucket.raw_data_lake.id
  key     = "inventory/"
  content = ""
}

resource "aws_s3_object" "feedback_prefix" {
  bucket  = aws_s3_bucket.raw_data_lake.id
  key     = "feedback/"
  content = ""
}

# ── Glue Database -- Data Catalog ────────────────────────

resource "aws_glue_catalog_database" "restaurant_catalog" {
  name        = "restaurant_ordering_db"
  description = "Glue catalog for Restaurant Ordering System"
}

resource "aws_glue_catalog_table" "orders_table" {
  name          = "orders"
  database_name = aws_glue_catalog_database.restaurant_catalog.name

  table_type = "EXTERNAL_TABLE"

  parameters = {
    "classification" = "parquet"
  }

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.raw_data_lake.bucket}/orders/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "order_id"
      type = "int"
    }
    columns {
      name = "table_id"
      type = "int"
    }
    columns {
      name = "item_name"
      type = "string"
    }
    columns {
      name = "category"
      type = "string"
    }
    columns {
      name = "amount"
      type = "double"
    }
    columns {
      name = "payment_method"
      type = "string"
    }
    columns {
      name = "entry_time"
      type = "string"
    }
  }
}

# ── RDS PostgreSQL -- Data Warehouse ─────────────────────

resource "aws_db_instance" "restaurant_dwh" {
  identifier        = "${var.project_name}-postgres-${var.environment}"
  engine            = "postgres"
  engine_version    = "15.4"
  instance_class    = "db.t3.micro"
  allocated_storage = 20
  db_name           = "restaurant_db"
  username          = "postgres"
  password          = "postgres123"

  skip_final_snapshot    = true
  publicly_accessible    = true
  multi_az               = false
  deletion_protection    = false

  tags = {
    Name        = "Restaurant DWH PostgreSQL"
    Project     = var.project_name
    Environment = var.environment
    Owner       = "Swayam Sanket Padhy"
  }
}

# ── ElastiCache Redis -- Live Cache ──────────────────────

resource "aws_elasticache_cluster" "restaurant_cache" {
  cluster_id           = "${var.project_name}-redis-${var.environment}"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  engine_version       = "7.0"
  port                 = 6379

  tags = {
    Name        = "Restaurant Redis Cache"
    Project     = var.project_name
    Environment = var.environment
  }
}

# ── Outputs ──────────────────────────────────────────────

output "s3_raw_bucket" {
  description = "S3 raw data lake bucket name"
  value       = aws_s3_bucket.raw_data_lake.bucket
}

output "s3_processed_bucket" {
  description = "S3 processed
