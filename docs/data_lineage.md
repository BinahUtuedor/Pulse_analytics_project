# Data Lineage

## Overview

This document describes the movement and transformation of data through the Pulse Analytics ETL pipeline, from source ingestion to final storage in PostgreSQL.

---

# Source Systems

## Olist Orders Dataset

Source File:

```text
olist_orders_dataset.csv
```

Provides:

* Order identifiers
* Order status
* Purchase timestamps
* Delivery timestamps

---

## Olist Customers Dataset

Source File:

```text
olist_customers_dataset.csv
```

Provides:

* Customer identifiers
* Geographic information

---

## Olist Order Items Dataset

Source File:

```text
olist_order_items_dataset.csv
```

Provides:

* Item-level pricing
* Freight charges

---

## Olist Payments Dataset

Source File:

```text
olist_order_payments_dataset.csv
```

Provides:

* Payment transaction values

---

## Holiday API

External Source:

```text
https://date.nager.at
```

Provides:

* Brazilian public holidays
* Holiday names
* Holiday classifications

---

# ETL Pipeline Flow

## Phase 1 – Ingestion

Module:

```python
pipeline/ingest.py
```

### Processing Steps

#### Payment Aggregation

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

#### Item Aggregation

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

#### Dataset Consolidation

Joins:

```text
orders
LEFT JOIN customers
LEFT JOIN items_agg
LEFT JOIN payments_agg
```

Output:

```text
orders_df
```

---

## Phase 2 – Enrichment

Module:

```python
pipeline/enrich.py
```

### Holiday Retrieval

API Call:

```text
Nager.Date Public Holiday API
```

Output:

```text
holidays_df
```

### Holiday Join

Join Condition:

```text
order_date = holiday_date
```

Output Columns:

```text
holiday_name
holiday_type
holiday_date
```

Result:

```text
enriched_df
```

---

## Phase 3 – Data Cleaning

Module:

```python
pipeline/clean.py
```

### Transformations

#### Remove Duplicate Orders

```python
drop_duplicates(order_id)
```

#### Remove Invalid Orders

```python
dropna(order_purchase_timestamp)
```

#### Filter Active Orders

Retained Statuses:

```text
delivered
shipped
approved
processing
```

#### Null Handling

```python
holiday_name = 'None'
holiday_type = 'None'
```

#### Data Type Standardization

Convert all date columns to datetime.

#### Numeric Standardization

Convert:

```text
item_count
total_price
total_freight
total_payment
```

to numeric types.

Output:

```text
clean_df
```

---

## Phase 4 – Feature Engineering

Module:

```python
pipeline/features.py
```

### Derived Columns

| Target Column    | Transformation                       |
| ---------------- | ------------------------------------ |
| is_holiday       | holiday_name != 'None'               |
| order_date       | Extract date from purchase timestamp |
| order_year       | Extract year                         |
| order_month      | Extract month                        |
| order_week       | Extract ISO week                     |
| day_of_week      | Extract weekday name                 |
| hour_of_day      | Extract purchase hour                |
| is_weekend       | dayofweek >= 5                       |
| days_to_delivery | delivery date - purchase date        |
| total_revenue    | total_price + total_freight          |

Output:

```text
feature_df
```

---

## Phase 5 – Loading

Module:

```python
pipeline/load.py
```

### Target Database

```text
PostgreSQL
```

Database:

```text
pulse_analytics
```

Target Table:

```text
olist_enriched
```

### Loading Strategy

1. Create table if not exists
2. Truncate existing table
3. Append fresh dataset
4. Commit load

Output:

```text
olist_enriched
```

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
| holiday_date             | Holiday API                        | Date match      |
| holiday_name             | Holiday API                        | Date match      |
| holiday_type             | Holiday API                        | Date match      |
| is_holiday               | holiday_name                       | Derived         |
| order_year               | purchase timestamp                 | Derived         |
| order_month              | purchase timestamp                 | Derived         |
| order_week               | purchase timestamp                 | Derived         |
| day_of_week              | purchase timestamp                 | Derived         |
| hour_of_day              | purchase timestamp                 | Derived         |
| is_weekend               | purchase timestamp                 | Derived         |
| days_to_delivery         | delivery and purchase timestamps   | Date difference |
| total_revenue            | total_price + total_freight        | Calculated      |

---

# Data Quality Checkpoints

## During Cleaning

* Duplicate order removal
* Null timestamp validation
* Order status filtering
* Numeric type validation

## During Validation

Validation SQL checks:

* Total row count
* Null timestamp count
* Null revenue count
* Holiday distribution
* Revenue by holiday status
* Orders by year

---

# Final Data Product

| Attribute      | Value             |
| -------------- | ----------------- |
| Destination    | PostgreSQL        |
| Database       | pulse_analytics   |
| Table          | olist_enriched    |
| Grain          | One row per order |
| Refresh Type   | Full Refresh      |
| Consumer Layer | Analytics & BI    |
