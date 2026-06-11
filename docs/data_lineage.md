# Data Lineage

## Overview

This document describes the end-to-end movement, transformation, enrichment, validation, storage, and consumption of data throughout the Pulse Analytics platform.

The lineage captures how raw e-commerce transaction data is transformed into an analytics-ready warehouse that supports reporting, forecasting, and business intelligence use cases.

---

# Lineage Summary

```text
Raw Olist Data Sources
│
├── Orders
├── Customers
├── Order Items
└── Payments
│
▼
Data Ingestion
(pipeline/ingest.py)
│
▼
Merged Orders Dataset
(orders_df)
│
▼
Holiday API Enrichment
(pipeline/enrich.py)
│
▼
Enriched Dataset
(enriched_df)
│
▼
Data Cleaning & Validation
(pipeline/clean.py)
│
▼
Clean Dataset
(clean_df)
│
▼
Feature Engineering
(pipeline/features.py)
│
▼
Analytics Dataset
(feature_df)
│
▼
PostgreSQL Warehouse
(olist_enriched)
│
├── Revenue Views
├── Holiday Views
├── Delivery Views
└── Geography Views
│
├───────────────┬───────────────┬───────────────┐
│               │               │               │
▼               ▼               ▼               ▼
Revenue      Holiday       Geography      Delivery
Analysis     Analysis      Analysis       Analysis
│
▼
Forecast Dataset
│
▼
Prophet Forecasting
│
▼
Forecast Outputs
(CSV + PNG)
```

---

# Source Systems

The pipeline consumes four Olist transactional datasets and one external API source.

---

## Orders Dataset

Source File:

```text
data/raw/olist_orders_dataset.csv
```

Provides:

* Order identifiers
* Order status
* Purchase timestamps
* Approval timestamps
* Delivery timestamps

Primary Columns:

```text
order_id
customer_id
order_status
order_purchase_timestamp
order_approved_at
order_delivered_customer_date
order_estimated_delivery_date
```

---

## Customers Dataset

Source File:

```text
data/raw/olist_customers_dataset.csv
```

Provides:

* Customer identifiers
* Geographic information

Primary Columns:

```text
customer_id
customer_unique_id
customer_zip_code_prefix
customer_city
customer_state
```

---

## Order Items Dataset

Source File:

```text
data/raw/olist_order_items_dataset.csv
```

Provides:

* Product pricing
* Freight costs

Primary Columns:

```text
order_id
order_item_id
price
freight_value
```

---

## Payments Dataset

Source File:

```text
data/raw/olist_order_payments_dataset.csv
```

Provides:

* Payment transactions
* Payment values

Primary Columns:

```text
order_id
payment_value
```

---

## Public Holiday API

External Source:

```text
https://date.nager.at
```

Endpoint:

```http
GET /api/v3/PublicHolidays/{year}/BR
```

Provides:

* Holiday date
* Holiday name
* Holiday classification

Retrieved Years:

```python
[2016, 2017, 2018]
```

---

# Phase 1 — Data Ingestion

Module:

```text
pipeline/ingest.py
```

Purpose:

Combine multiple Olist datasets into a unified order-level dataset.

---

## Payment Aggregation

Source:

```text
olist_order_payments_dataset.csv
```

Transformation:

```sql
SUM(payment_value)
GROUP BY order_id
```

Output:

```text
total_payment
```

Result:

```text
payments_agg
```

---

## Item Aggregation

Source:

```text
olist_order_items_dataset.csv
```

Transformations:

```sql
COUNT(order_item_id)
SUM(price)
SUM(freight_value)
GROUP BY order_id
```

Outputs:

```text
item_count
total_price
total_freight
```

Result:

```text
items_agg
```

---

## Dataset Consolidation

Join Strategy:

```text
orders
LEFT JOIN customers
LEFT JOIN items_agg
LEFT JOIN payments_agg
```

Output Dataset:

```text
orders_df
```

Grain:

```text
One row per order
```

---

# Phase 2 — Holiday Enrichment

Module:

```text
pipeline/enrich.py
```

Purpose:

Enhance transactions with Brazilian public holiday information.

---

## Holiday Retrieval

Input:

```text
Nager.Date API
```

Output:

```text
holidays_df
```

Columns Added:

```text
holiday_date
holiday_name
holiday_type
```

---

## Holiday Matching

Join Condition:

```text
order_date = holiday_date
```

Join Type:

```text
LEFT JOIN
```

Output Dataset:

```text
enriched_df
```

---

# Phase 3 — Data Cleaning

Module:

```text
pipeline/clean.py
```

Purpose:

Apply quality controls and standardize data types.

---

## Duplicate Removal

Transformation:

```python
drop_duplicates(subset=["order_id"])
```

---

## Null Timestamp Validation

Transformation:

```python
dropna(subset=["order_purchase_timestamp"])
```

---

## Order Status Filtering

Retained Values:

```text
delivered
shipped
approved
processing
```

---

## Holiday Standardization

Transformation:

```python
holiday_name.fillna("None")
holiday_type.fillna("None")
```

---

## Datetime Conversion

Columns Standardized:

```text
order_purchase_timestamp
order_approved_at
order_delivered_carrier_date
order_delivered_customer_date
order_estimated_delivery_date
```

---

## Numeric Standardization

Columns Standardized:

```text
item_count
total_price
total_freight
total_payment
```

Output Dataset:

```text
clean_df
```

---

# Phase 4 — Feature Engineering

Module:

```text
pipeline/features.py
```

Purpose:

Generate business-ready analytical attributes.

---

## Derived Features

| Output Column    | Source             | Logic                  |
| ---------------- | ------------------ | ---------------------- |
| is_holiday       | holiday_name       | holiday_name != 'None' |
| order_date       | purchase timestamp | Extract date           |
| order_year       | purchase timestamp | Extract year           |
| order_month      | purchase timestamp | Extract month          |
| order_week       | purchase timestamp | Extract ISO week       |
| day_of_week      | purchase timestamp | Extract weekday        |
| hour_of_day      | purchase timestamp | Extract hour           |
| is_weekend       | purchase timestamp | dayofweek >= 5         |
| days_to_delivery | delivery timestamp | Date difference        |
| total_revenue    | price + freight    | Calculated metric      |

Output Dataset:

```text
feature_df
```

---

# Phase 5 — Warehouse Load

Module:

```text
pipeline/load.py
```

Purpose:

Load curated analytics data into PostgreSQL.

---

## Target Environment

Database:

```text
pulse_analytics
```

Table:

```text
olist_enriched
```

Storage Type:

```text
PostgreSQL Relational Warehouse
```

---

## Load Strategy

1. Create analytics table
2. Apply indexes
3. Truncate existing records
4. Load fresh dataset
5. Commit transaction

Output:

```text
olist_enriched
```

---

# Analytics Layer

The warehouse exposes analytical views for downstream reporting.

---

## Revenue Views

Source:

```text
olist_enriched
```

Views:

```text
vw_daily_revenue
vw_monthly_revenue
```

Business Purpose:

* Revenue reporting
* Trend analysis
* KPI tracking

---

## Holiday Views

Views:

```text
vw_holiday_sales
vw_holiday_details
```

Business Purpose:

* Holiday performance analysis
* Seasonal reporting

---

## Delivery Views

Views:

```text
vw_delivery_performance
```

Business Purpose:

* Logistics monitoring
* Delivery SLA reporting

---

## Geography Views

Views:

```text
vw_state_sales
vw_city_sales
```

Business Purpose:

* Geographic performance analysis
* Market intelligence

---

# Forecasting Lineage

Module:

```text
analytics/extract_forecast_data.py
```

Purpose:

Generate forecasting dataset from warehouse data.

---

## Forecast Dataset Extraction

Source:

```text
olist_enriched
```

Query:

```sql
SELECT
    order_date,
    SUM(total_revenue)
FROM olist_enriched
GROUP BY order_date
```

Output:

```text
outputs/extracts/forecast_daily_revenue.csv
```

---

## Forecast Model

Module:

```text
analytics/forecast.py
```

Framework:

```text
Prophet
```

Input:

```text
forecast_daily_revenue.csv
```

Output:

```text
outputs/forecast/revenue_forecast.csv
outputs/forecast/revenue_forecast.png
outputs/forecast/revenue_components.png
```

Business Purpose:

* Revenue forecasting
* Trend analysis
* Seasonality detection

---

# Column-Level Lineage

| Target Column            | Source                             | Transformation  |
| ------------------------ | ---------------------------------- | --------------- |
| order_id                 | orders.order_id                    | Direct          |
| customer_id              | customers.customer_id              | Direct          |
| customer_unique_id       | customers.customer_unique_id       | Direct          |
| customer_zip_code_prefix | customers.customer_zip_code_prefix | Direct          |
| customer_city            | customers.customer_city            | Direct          |
| customer_state           | customers.customer_state           | Direct          |
| order_status             | orders.order_status                | Direct          |
| order_purchase_timestamp | orders.order_purchase_timestamp    | Direct          |
| item_count               | order_items.order_item_id          | COUNT           |
| total_price              | order_items.price                  | SUM             |
| total_freight            | order_items.freight_value          | SUM             |
| total_payment            | payments.payment_value             | SUM             |
| holiday_date             | Holiday API                        | Date Match      |
| holiday_name             | Holiday API                        | Date Match      |
| holiday_type             | Holiday API                        | Date Match      |
| is_holiday               | holiday_name                       | Derived         |
| order_date               | purchase timestamp                 | Derived         |
| order_year               | purchase timestamp                 | Derived         |
| order_month              | purchase timestamp                 | Derived         |
| order_week               | purchase timestamp                 | Derived         |
| day_of_week              | purchase timestamp                 | Derived         |
| hour_of_day              | purchase timestamp                 | Derived         |
| is_weekend               | purchase timestamp                 | Derived         |
| days_to_delivery         | delivery timestamp                 | Date Difference |
| total_revenue            | total_price + total_freight        | Calculated      |

---

# Data Quality Checkpoints

## Pipeline Validation

Performed During:

```text
pipeline/clean.py
```

Checks:

* Duplicate order detection
* Null timestamp validation
* Status filtering
* Datetime validation
* Numeric validation

---

## Warehouse Validation

Performed Using:

```text
sql/validate.sql
```

Checks:

* Total row count
* Revenue completeness
* Holiday completeness
* Holiday distribution
* Revenue comparison
* Year-over-year order counts

---

# Final Data Products

| Data Product               | Consumer           |
| -------------------------- | ------------------ |
| olist_enriched             | Analytics          |
| vw_daily_revenue           | Reporting          |
| vw_monthly_revenue         | Reporting          |
| vw_holiday_sales           | Business Analysis  |
| vw_delivery_performance    | Operations         |
| vw_state_sales             | Geography Analysis |
| forecast_daily_revenue.csv | Forecasting        |
| revenue_forecast.csv       | Data Science       |
| revenue_forecast.png       | Stakeholders       |
| revenue_components.png     | Stakeholders       |

---

# Data Consumers

The curated datasets support:

* Business Intelligence Dashboards
* Executive KPI Reporting
* Revenue Analytics
* Holiday Performance Analysis
* Delivery Operations Monitoring
* Geographic Sales Analysis
* Revenue Forecasting
* Future Power BI Dashboards
* Future Tableau Dashboards

---

# Ownership

**Project:** Pulse Analytics

**Author:** Binah Utuedor

**Purpose:** End-to-End Data Engineering & Analytics Platform

**Last Updated:** June 2026
