-- ============================================
-- RESTAURANT ORDERING SYSTEM -- ANALYTICS QUERIES
-- Swayam Sanket Padhy | Roll No: 2306239
-- Data Engineering 2025-2026 | KIIT University
-- ============================================

-- 1. Total revenue today
SELECT
    SUM(f.amount) AS total_revenue,
    COUNT(f.order_id) AS total_orders
FROM fact_order f
JOIN dim_time t ON f.time_id = t.time_id
WHERE t.full_date = CURRENT_DATE;

-- 2. Top 5 best-selling menu items
SELECT
    m.name AS item_name,
    m.category,
    SUM(f.quantity) AS total_quantity_sold,
    SUM(f.amount) AS total_revenue
FROM fact_order f
JOIN dim_menu_item m ON f.menu_item_id = m.menu_item_id
GROUP BY m.name, m.category
ORDER BY total_quantity_sold DESC
LIMIT 5;

-- 3. Revenue by hour of day (peak hours analysis)
SELECT
    t.hour,
    COUNT(f.order_id) AS orders_count,
    SUM(f.amount) AS hourly_revenue
FROM fact_order f
JOIN dim_time t ON f.time_id = t.time_id
GROUP BY t.hour
ORDER BY t.hour;

-- 4. Revenue by payment method
SELECT
    p.method AS payment_method,
    COUNT(f.order_id) AS transactions,
    SUM(f.amount) AS total_amount
FROM fact_order f
JOIN dim_payment p ON f.payment_id = p.payment_id
GROUP BY p.method
ORDER BY total_amount DESC;

-- 5. Table utilization -- avg time spent per table
SELECT
    tb.section,
    tb.table_id,
    ROUND(AVG(EXTRACT(EPOCH FROM (f.exit_time - f.entry_time))/60), 2) AS avg_minutes_per_order,
    COUNT(f.order_id) AS total_orders
FROM fact_order f
JOIN dim_table tb ON f.table_id = tb.table_id
WHERE f.exit_time IS NOT NULL
GROUP BY tb.section, tb.table_id
ORDER BY avg_minutes_per_order DESC;

-- 6. Customer loyalty tier breakdown
SELECT
    c.loyalty_tier,
    COUNT(DISTINCT f.customer_id) AS customer_count,
    SUM(f.amount) AS total_spent
FROM fact_order f
JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY c.loyalty_tier
ORDER BY total_spent DESC;

-- 7. Weekly revenue trend
SELECT
    t.full_date,
    t.day_of_week,
    SUM(f.amount) AS daily_revenue,
    COUNT(f.order_id) AS daily_orders
FROM fact_order f
JOIN dim_time t ON f.time_id = t.time_id
WHERE t.full_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY t.full_date, t.day_of_week
ORDER BY t.full_date;

-- 8. Staff performance -- orders handled per staff
SELECT
    s.name AS staff_name,
    s.role,
    s.shift,
    COUNT(f.order_id) AS orders_handled,
    SUM(f.amount) AS revenue_generated
FROM fact_order f
JOIN dim_staff s ON f.staff_id = s.staff_id
GROUP BY s.name, s.role, s.shift
ORDER BY orders_handled DESC;

-- 9. Category-wise revenue breakdown
SELECT
    m.category,
    COUNT(f.order_id) AS orders,
    SUM(f.quantity) AS items_sold,
    SUM(f.amount) AS revenue
FROM fact_order f
JOIN dim_menu_item m ON f.menu_item_id = m.menu_item_id
GROUP BY m.category
ORDER BY revenue DESC;

-- 10. Weekend vs weekday revenue comparison
SELECT
    CASE WHEN t.is_weekend THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    COUNT(f.order_id) AS total_orders,
    SUM(f.amount) AS total_revenue,
    ROUND(AVG(f.amount), 2) AS avg_order_value
FROM fact_order f
JOIN dim_time t ON f.time_id = t.time_id
GROUP BY t.is_weekend;
