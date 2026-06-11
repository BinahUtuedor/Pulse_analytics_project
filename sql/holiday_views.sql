CREATE OR REPLACE VIEW vw_holiday_sales AS
SELECT
    is_holiday,
    COUNT(*) AS total_orders,
    SUM(total_revenue) AS total_revenue,
    AVG(total_revenue) AS avg_order_value
FROM olist_enriched
GROUP BY is_holiday;


CREATE OR REPLACE VIEW vw_holiday_details AS
SELECT
    holiday_name,
    COUNT(*) AS total_orders,
    SUM(total_revenue) AS total_revenue,
    AVG(total_revenue) AS avg_order_value
FROM olist_enriched
WHERE is_holiday = TRUE
GROUP BY holiday_name;