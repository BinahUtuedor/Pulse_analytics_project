-- Daily Revenue

CREATE OR REPLACE VIEW vw_daily_revenue AS
SELECT
    order_date,
    COUNT(*) AS total_orders,
    SUM(total_revenue) AS total_revenue,
    AVG(total_revenue) AS avg_order_value
FROM olist_enriched
GROUP BY order_date;


-- Monthly Revenue

CREATE OR REPLACE VIEW vw_monthly_revenue AS
SELECT
    order_year,
    order_month,
    COUNT(*) AS total_orders,
    SUM(total_revenue) AS total_revenue,
    AVG(total_revenue) AS avg_order_value
FROM olist_enriched
GROUP BY
    order_year,
    order_month;