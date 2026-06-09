CREATE TABLE IF NOT EXISTS olist_enriched (
    order_id                    VARCHAR(50) PRIMARY KEY,
    customer_id                 VARCHAR(50),
    customer_unique_id          VARCHAR(50),
    customer_zip_code_prefix    INTEGER,

    order_status                VARCHAR(20),

    order_purchase_timestamp    TIMESTAMP,
    order_approved_at           TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP,

    order_date                  DATE,
    order_year                  INTEGER,
    order_month                 INTEGER,
    order_week                  INTEGER,
    day_of_week                 VARCHAR(10),
    hour_of_day                 INTEGER,
    is_weekend                  BOOLEAN,

    is_holiday                  BOOLEAN,
    holiday_name                VARCHAR(100),
    holiday_type                VARCHAR(50),
    holiday_date                DATE,

    item_count                  INTEGER,
    total_price                 NUMERIC(12,2),
    total_freight               NUMERIC(12,2),
    total_payment               NUMERIC(12,2),
    total_revenue               NUMERIC(12,2),
    days_to_delivery            INTEGER,

    customer_city               VARCHAR(100),
    customer_state              VARCHAR(5)
);

-- Indexes for analytics query performance
CREATE INDEX IF NOT EXISTS idx_order_date ON olist_enriched(order_date);
CREATE INDEX IF NOT EXISTS idx_is_holiday ON olist_enriched(is_holiday);
CREATE INDEX IF NOT EXISTS idx_order_state ON olist_enriched(customer_state);
