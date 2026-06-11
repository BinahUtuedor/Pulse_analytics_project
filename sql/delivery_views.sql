CREATE OR REPLACE VIEW vw_delivery_performance AS
SELECT
    customer_state,
    COUNT(*) AS total_orders,
    AVG(days_to_delivery) AS avg_delivery_days,
    MIN(days_to_delivery) AS min_delivery_days,
    MAX(days_to_delivery) AS max_delivery_days
FROM olist_enriched
WHERE days_to_delivery IS NOT NULL
GROUP BY customer_state;