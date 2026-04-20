-- ============================================
-- RESTAURANT ORDERING SYSTEM -- STAR SCHEMA
-- Swayam Sanket Padhy | Roll No: 2306239
-- Data Engineering 2025-2026 | KIIT University
-- ============================================

-- DIMENSION: Table
CREATE TABLE IF NOT EXISTS dim_table (
    table_id      SERIAL PRIMARY KEY,
    section       VARCHAR(50),
    capacity      INT,
    status        VARCHAR(20) DEFAULT 'available'
);

-- DIMENSION: Customer
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id   SERIAL PRIMARY KEY,
    name          VARCHAR(100),
    contact       VARCHAR(20),
    loyalty_tier  VARCHAR(20) DEFAULT 'bronze'
);

-- DIMENSION: Menu Item
CREATE TABLE IF NOT EXISTS dim_menu_item (
    menu_item_id  SERIAL PRIMARY KEY,
    name          VARCHAR(100),
    category      VARCHAR(50),
    price         NUMERIC(8,2),
    is_available  BOOLEAN DEFAULT TRUE
);

-- DIMENSION: Staff
CREATE TABLE IF NOT EXISTS dim_staff (
    staff_id      SERIAL PRIMARY KEY,
    name          VARCHAR(100),
    role          VARCHAR(50),
    shift         VARCHAR(20)
);

-- DIMENSION: Time
CREATE TABLE IF NOT EXISTS dim_time (
    time_id       SERIAL PRIMARY KEY,
    full_date     DATE,
    hour          INT,
    day_of_week   VARCHAR(20),
    month         INT,
    year          INT,
    is_weekend    BOOLEAN
);

-- DIMENSION: Payment
CREATE TABLE IF NOT EXISTS dim_payment (
    payment_id       SERIAL PRIMARY KEY,
    method           VARCHAR(30),
    status           VARCHAR(20),
    transaction_ref  VARCHAR(100)
);

-- FACT TABLE: Orders
CREATE TABLE IF NOT EXISTS fact_order (
    order_id      SERIAL PRIMARY KEY,
    table_id      INT REFERENCES dim_table(table_id),
    customer_id   INT REFERENCES dim_customer(customer_id),
    menu_item_id  INT REFERENCES dim_menu_item(menu_item_id),
    staff_id      INT REFERENCES dim_staff(staff_id),
    time_id       INT REFERENCES dim_time(time_id),
    payment_id    INT REFERENCES dim_payment(payment_id),
    quantity      INT,
    amount        NUMERIC(10,2),
    entry_time    TIMESTAMP,
    exit_time     TIMESTAMP
);

-- INDEXES for query performance
CREATE INDEX idx_fact_order_time     ON fact_order(time_id);
CREATE INDEX idx_fact_order_item     ON fact_order(menu_item_id);
CREATE INDEX idx_fact_order_table    ON fact_order(table_id);
CREATE INDEX idx_fact_order_payment  ON fact_order(payment_id);
