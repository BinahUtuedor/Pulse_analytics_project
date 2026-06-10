# Data Dictionary

## Overview

**Project:** Pulse Analytics

**Target Table:** `olist_enriched`

**Grain:** One row per order

**Description:**
The `olist_enriched` table contains enriched e-commerce order data sourced from the Olist Brazilian marketplace dataset. Data is consolidated from orders, customers, order items, and payments datasets, enriched with Brazilian public holiday information, and augmented with engineered analytical features.

---

# Primary Key

| Column   | Data Type   | Description                       |
| -------- | ----------- | --------------------------------- |
| order_id | VARCHAR(50) | Unique identifier for each order. |

---

# Customer Attributes

| Column                   | Data Type    | Description                                            |
| ------------------------ | ------------ | ------------------------------------------------------ |
| customer_id              | VARCHAR(50)  | Customer identifier associated with the order.         |
| customer_unique_id       | VARCHAR(50)  | Persistent customer identifier across multiple orders. |
| customer_zip_code_prefix | INTEGER      | Customer postal code prefix.                           |
| customer_city            | VARCHAR(100) | Customer city.                                         |
| customer_state           | VARCHAR(5)   | Customer state abbreviation.                           |

---

# Order Attributes

| Column                        | Data Type   | Description                                            |
| ----------------------------- | ----------- | ------------------------------------------------------ |
| order_status                  | VARCHAR(20) | Current order status.                                  |
| order_purchase_timestamp      | TIMESTAMP   | Date and time the order was placed.                    |
| order_approved_at             | TIMESTAMP   | Date and time the payment was approved.                |
| order_delivered_carrier_date  | TIMESTAMP   | Date and time the carrier received the shipment.       |
| order_delivered_customer_date | TIMESTAMP   | Date and time the order was delivered to the customer. |
| order_estimated_delivery_date | TIMESTAMP   | Estimated delivery date provided to the customer.      |

---

# Financial Metrics

| Column        | Data Type     | Description                                           |
| ------------- | ------------- | ----------------------------------------------------- |
| item_count    | INTEGER       | Number of items purchased in the order.               |
| total_price   | NUMERIC(12,2) | Sum of item prices for the order.                     |
| total_freight | NUMERIC(12,2) | Sum of freight charges for the order.                 |
| total_payment | NUMERIC(12,2) | Total amount paid for the order.                      |
| total_revenue | NUMERIC(12,2) | Total order revenue calculated as price plus freight. |

---

# Holiday Enrichment

| Column       | Data Type    | Description                                          |
| ------------ | ------------ | ---------------------------------------------------- |
| holiday_date | DATE         | Public holiday date matched to order date.           |
| holiday_name | VARCHAR(100) | Name of the holiday.                                 |
| holiday_type | VARCHAR(50)  | Holiday category returned by the API.                |
| is_holiday   | BOOLEAN      | Indicates whether the order was placed on a holiday. |

---

# Time-Based Features

| Column      | Data Type   | Description                                       |
| ----------- | ----------- | ------------------------------------------------- |
| order_date  | DATE        | Purchase date extracted from timestamp.           |
| order_year  | INTEGER     | Purchase year.                                    |
| order_month | INTEGER     | Purchase month.                                   |
| order_week  | INTEGER     | ISO calendar week number.                         |
| day_of_week | VARCHAR(10) | Day name of purchase date.                        |
| hour_of_day | INTEGER     | Hour of purchase.                                 |
| is_weekend  | BOOLEAN     | Indicates whether purchase occurred on a weekend. |

---

# Operational Metrics

| Column           | Data Type | Description                                   |
| ---------------- | --------- | --------------------------------------------- |
| days_to_delivery | INTEGER   | Number of days between purchase and delivery. |

---

# Data Quality Rules

| Rule                         | Description                                                            |
| ---------------------------- | ---------------------------------------------------------------------- |
| Unique Orders                | Each order_id must be unique.                                          |
| Mandatory Purchase Timestamp | Orders must contain a purchase timestamp.                              |
| Valid Order Status           | Only delivered, shipped, approved, and processing orders are retained. |
| Non-Negative Revenue         | Total price values must be greater than or equal to zero.              |
| Holiday Defaults             | Missing holiday values are populated with 'None'.                      |
| Standardized Dates           | All date fields are converted to TIMESTAMP format.                     |

---

# Refresh Strategy

* Load Type: Full Refresh
* Load Frequency: Manual Pipeline Execution
* Destination: PostgreSQL
* Table: `olist_enriched`

---

# Intended Business Use Cases

* Revenue trend analysis
* Holiday sales impact analysis
* Delivery performance monitoring
* Customer geographic analysis
* Time-series forecasting
* Business intelligence dashboards
