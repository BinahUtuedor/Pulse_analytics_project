-- 1. Row count sanity check
SELECT COUNT(*) AS total_rows FROM olist_enriched;

-- 2. Null check on critical columns
SELECT
    SUM(CASE WHEN order_purchase_timestamp IS NULL THEN 1 ELSE 0 END) AS null_timestamps,
    SUM(CASE WHEN total_revenue IS NULL THEN 1 ELSE 0 END)            AS null_revenue,
    SUM(CASE WHEN is_holiday IS NULL THEN 1 ELSE 0 END)               AS null_holidays
FROM olist_enriched;

-- 3. Holiday distribution
SELECT is_holiday, COUNT(*) AS order_count
FROM olist_enriched
GROUP BY is_holiday;

-- 4. Revenue on holidays vs non-holidays
SELECT
    is_holiday,
    ROUND(AVG(total_revenue), 2) AS avg_revenue,
    ROUND(SUM(total_revenue), 2) AS total_revenue
FROM olist_enriched
GROUP BY is_holiday;

-- 5. Orders per year
SELECT order_year, COUNT(*) AS orders
FROM olist_enriched
GROUP BY order_year ORDER BY order_year;
