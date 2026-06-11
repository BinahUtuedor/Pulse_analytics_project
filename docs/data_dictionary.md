# Data Dictionary

## Overview

**Project:** Pulse Analytics

**Target Table:** `olist_enriched`

**Database:** PostgreSQL

**Grain:** One row per order

**Source Systems:**

* Olist Orders Dataset
* Olist Customers Dataset
* Olist Order Items Dataset
* Olist Payments Dataset
* Nager.Date Public Holiday API

**Description**

The `olist_enriched` table is the primary analytical dataset used throughout the Pulse Analytics platform.

Data is consolidated from multiple Olist marketplace datasets, enriched with Brazilian public holiday information, cleaned using data quality rules, and enhanced through feature engineering to support analytics, forecasting, and business intelligence reporting.

The table serves as the foundation for:

* Revenue trend analysis
* Holiday sales analysis
* Delivery performance monitoring
* Geographic sales reporting
* Revenue forecasting
* Business intelligence dashboards

---

# Table Information

| Attribute      | Value              |
| -------------- | ------------------ |
| Table Name     | `olist_enriched`   |
| Database       | PostgreSQL         |
| Schema         | Public             |
| Grain          | One row per order  |
| Primary Key    | `order_id`         |
| Load Type      | Full Refresh       |
| Refresh Method | Pipeline Execution |
| Data Volume    | ~98,000 Orders     |

---

# Primary Key

| Column   | Data Type   | Description                               |
| -------- | ----------- | ----------------------------------------- |
| order_id | VARCHAR(50) | Unique identifier assigned to each order. |

---

# Customer Attributes

| Column                   | Data Type    | Description                                            |
| ------------------------ | ------------ | ------------------------------------------------------ |
| customer_id              | VARCHAR(50)  | Customer identifier associated with an order.          |
| customer_unique_id       | VARCHAR(50)  | Persistent customer identifier across multiple orders. |
| customer_zip_code_prefix | INTEGER      | Customer postal code prefix.                           |
| customer_city            | VARCHAR(100) | Customer city.                                         |
| customer_state           | VARCHAR(5)   | Brazilian state abbreviation.                          |

### Business Purpose

Used for:

* Geographic sales analysis
* Regional performance reporting
* Market segmentation

---

# Order Attributes

| Column                        | Data Type   | Description                                    |
| ----------------------------- | ----------- | ---------------------------------------------- |
| order_status                  | VARCHAR(20) | Current order lifecycle status.                |
| order_purchase_timestamp      | TIMESTAMP   | Timestamp when order was placed.               |
| order_approved_at             | TIMESTAMP   | Timestamp when payment was approved.           |
| order_delivered_carrier_date  | TIMESTAMP   | Timestamp when shipment was handed to carrier. |
| order_delivered_customer_date | TIMESTAMP   | Timestamp when order was delivered.            |
| order_estimated_delivery_date | TIMESTAMP   | Customer-facing estimated delivery date.       |

### Business Purpose

Used for:

* Order lifecycle analysis
* Fulfillment tracking
* Delivery performance metrics

---

# Financial Metrics

| Column        | Data Type     | Description                             |
| ------------- | ------------- | --------------------------------------- |
| item_count    | INTEGER       | Number of items purchased in the order. |
| total_price   | NUMERIC(12,2) | Total product value across all items.   |
| total_freight | NUMERIC(12,2) | Total shipping charges.                 |
| total_payment | NUMERIC(12,2) | Total payment received for the order.   |
| total_revenue | NUMERIC(12,2) | Product value plus freight charges.     |

### Revenue Formula

```python
total_revenue = total_price + total_freight
```

### Business Purpose

Used for:

* Revenue reporting
* Average order value analysis
* Forecasting
* Profitability studies

---

# Holiday Enrichment Attributes

Source:

Brazilian Public Holiday API (Nager.Date)

| Column       | Data Type    | Description                                              |
| ------------ | ------------ | -------------------------------------------------------- |
| holiday_date | DATE         | Holiday date matched to purchase date.                   |
| holiday_name | VARCHAR(100) | Name of public holiday.                                  |
| holiday_type | VARCHAR(50)  | Holiday classification returned by API.                  |
| is_holiday   | BOOLEAN      | Indicates whether purchase occurred on a public holiday. |

### Business Purpose

Used for:

* Holiday sales analysis
* Promotional planning
* Seasonal trend analysis

---

# Time Dimensions

| Column      | Data Type   | Description                             |
| ----------- | ----------- | --------------------------------------- |
| order_date  | DATE        | Purchase date extracted from timestamp. |
| order_year  | INTEGER     | Purchase year.                          |
| order_month | INTEGER     | Purchase month.                         |
| order_week  | INTEGER     | ISO week number.                        |
| day_of_week | VARCHAR(10) | Day name.                               |
| hour_of_day | INTEGER     | Hour purchase occurred.                 |
| is_weekend  | BOOLEAN     | Weekend purchase indicator.             |

### Business Purpose

Used for:

* Trend analysis
* Seasonal reporting
* Peak purchasing hour analysis
* Time-series forecasting

---

# Operational Metrics

| Column           | Data Type | Description                                            |
| ---------------- | --------- | ------------------------------------------------------ |
| days_to_delivery | INTEGER   | Number of days between purchase and customer delivery. |

### Calculation

```python
days_to_delivery =
order_delivered_customer_date
-
order_purchase_timestamp
```

### Business Purpose

Used for:

* Delivery monitoring
* Logistics reporting
* Service-level performance tracking

---

# Derived Analytical Views

The following PostgreSQL views are built from the `olist_enriched` table.

## Revenue Analytics

| View               | Purpose                 |
| ------------------ | ----------------------- |
| vw_daily_revenue   | Daily revenue reporting |
| vw_monthly_revenue | Monthly revenue trends  |

---

## Holiday Analytics

| View               | Purpose                           |
| ------------------ | --------------------------------- |
| vw_holiday_sales   | Holiday vs non-holiday comparison |
| vw_holiday_details | Revenue by holiday name           |

---

## Delivery Analytics

| View                    | Purpose                   |
| ----------------------- | ------------------------- |
| vw_delivery_performance | Delivery metrics by state |

---

## Geographic Analytics

| View           | Purpose          |
| -------------- | ---------------- |
| vw_state_sales | Revenue by state |
| vw_city_sales  | Revenue by city  |

---

# Forecasting Dataset

The following dataset is generated for machine learning forecasting:

```text
outputs/extracts/forecast_daily_revenue.csv
```

Structure:

| Column     | Description            |
| ---------- | ---------------------- |
| order_date | Revenue date           |
| revenue    | Total revenue for date |

Used By:

```text
analytics/forecast.py
```

Forecast Horizon:

```text
90 Days
```

Forecasting Framework:

```text
Facebook Prophet
```

---

# Data Quality Rules

| Rule                     | Description                                           |
| ------------------------ | ----------------------------------------------------- |
| Unique Orders            | Each order_id must be unique.                         |
| Mandatory Timestamp      | Purchase timestamp cannot be null.                    |
| Valid Order Status       | Only active/completed orders retained.                |
| Non-Negative Revenue     | Revenue values must be greater than or equal to zero. |
| Holiday Defaults         | Missing holiday values populated as "None".           |
| Datetime Standardization | Date columns converted to TIMESTAMP format.           |

---

# Accepted Order Statuses

```python
[
    "delivered",
    "shipped",
    "approved",
    "processing"
]
```

Orders outside these statuses are excluded during cleaning.

---

# Refresh Strategy

| Attribute         | Value                  |
| ----------------- | ---------------------- |
| Load Type         | Full Refresh           |
| Refresh Frequency | Manual Execution       |
| Destination       | PostgreSQL             |
| Target Table      | olist_enriched         |
| Analytics Views   | Automatically Reusable |
| Forecast Data     | Generated On Demand    |

---

# Intended Business Use Cases

### Revenue Analytics

* Daily revenue tracking
* Monthly revenue trends
* Average order value reporting

### Holiday Analysis

* Holiday impact assessment
* Revenue uplift measurement
* Seasonal sales planning

### Delivery Monitoring

* Delivery lead-time analysis
* State-level logistics performance

### Geographic Intelligence

* State revenue ranking
* City revenue ranking
* Regional market analysis

### Forecasting

* Revenue prediction
* Trend identification
* Seasonality detection

### Business Intelligence

* Power BI dashboards
* Tableau reporting
* Executive KPI reporting

---

# Ownership

**Project:** Pulse Analytics

**Author:** Binah Utuedor

**Purpose:** Portfolio Data Engineering & Analytics Project

**Last Updated:** June 2026
