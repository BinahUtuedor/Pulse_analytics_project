CREATE OR REPLACE VIEW vw_state_sales AS
SELECT
    customer_state,
    COUNT(*) AS total_orders,
    SUM(total_revenue) AS total_revenue,
    AVG(total_revenue) AS avg_order_value
FROM olist_enriched
GROUP BY customer_state;


CREATE OR REPLACE VIEW vw_city_sales AS
SELECT
    customer_city,
    COUNT(*) AS total_orders,
    SUM(total_revenue) AS total_revenue
FROM olist_enriched
GROUP BY customer_city;