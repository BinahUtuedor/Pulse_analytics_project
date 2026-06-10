# Pulse Analytics

## End-to-End Data Engineering Pipeline

**E-Commerce Analytics Enrichment using the Olist Dataset, Public Holiday APIs, and PostgreSQL**

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Processing-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-orange)

---

# Overview

Pulse Analytics is an end-to-end data engineering project that transforms raw Brazilian e-commerce transaction data into an analytics-ready dataset.

The pipeline ingests multiple Olist marketplace datasets, enriches transactions with Brazilian public holiday information from the Nager.Date API, performs data quality checks, engineers analytical features, and loads the final dataset into PostgreSQL for downstream reporting and business intelligence.

The project demonstrates practical data engineering concepts including:

* Data ingestion and consolidation
* REST API integration
* Data enrichment
* Data cleaning and validation
* Feature engineering
* Relational database loading
* SQL-based quality assurance
* Analytics-ready schema design

---

# Architecture

```text
                +------------------+
                | Olist CSV Files  |
                +--------+---------+
                         |
                         v
               +-------------------+
               | Data Ingestion    |
               +--------+----------+
                        |
                        v
               +-------------------+
               | Holiday API       |
               | (Nager.Date)      |
               +--------+----------+
                        |
                        v
               +-------------------+
               | Data Enrichment   |
               +--------+----------+
                        |
                        v
               +-------------------+
               | Data Cleaning     |
               +--------+----------+
                        |
                        v
               +-------------------+
               | Feature Engineering|
               +--------+----------+
                        |
                        v
               +-------------------+
               | PostgreSQL Load   |
               +--------+----------+
                        |
                        v
               +-------------------+
               | Validation & QA   |
               +-------------------+
```

---

# Pipeline Phases

## Phase 1 — Data Ingestion

The ingestion layer loads and consolidates multiple Olist datasets into a single DataFrame.

### Source Datasets

* Orders
* Order Items
* Customers
* Payments

### Processing

#### Payments Aggregation

```python
payments.groupby('order_id').agg(
    total_payment=('payment_value', 'sum')
)
```

#### Order Items Aggregation

```python
items.groupby('order_id').agg(
    item_count=('order_item_id', 'count'),
    total_price=('price', 'sum'),
    total_freight=('freight_value', 'sum')
)
```

#### Dataset Consolidation

```python
orders
    .merge(customers, on='customer_id')
    .merge(items_agg, on='order_id')
    .merge(payments_agg, on='order_id')
```

### Output

Approximately 100,000 consolidated order records.

---

## Phase 2 — Holiday API Enrichment

The pipeline retrieves Brazilian public holiday information from the Nager.Date API.

### API Endpoint

```http
GET https://date.nager.at/api/v3/PublicHolidays/{year}/BR
```

### Years Processed

```python
[2016, 2017, 2018]
```

### Enrichment Logic

Orders are matched to holidays using the purchase date.

Added columns:

* holiday_name
* holiday_type
* holiday_date

---

## Phase 3 — Data Cleaning

Data quality procedures ensure consistency and reliability before analytics.

### Cleaning Operations

* Remove duplicate order IDs
* Remove rows with missing purchase timestamps
* Filter invalid order statuses
* Handle missing holiday values
* Convert timestamps to datetime
* Standardize numeric columns

### Accepted Order Statuses

```python
[
    'delivered',
    'shipped',
    'approved',
    'processing'
]
```

### Quality Checks

```python
assert df['order_id'].nunique() == len(df)
assert df['order_purchase_timestamp'].isna().sum() == 0
assert (df['total_price'] >= 0).all()
```

---

## Phase 4 — Feature Engineering

Business and analytical features are generated to support reporting and data exploration.

### Generated Features

| Feature          | Description                        |
| ---------------- | ---------------------------------- |
| is_holiday       | Order occurred on a public holiday |
| order_date       | Calendar date                      |
| order_year       | Purchase year                      |
| order_month      | Purchase month                     |
| order_week       | ISO week number                    |
| day_of_week      | Day name                           |
| hour_of_day      | Purchase hour                      |
| is_weekend       | Weekend indicator                  |
| days_to_delivery | Delivery duration in days          |
| total_revenue    | Product value + freight            |

### Revenue Calculation

```python
df['total_revenue'] = (
    df['total_price'] +
    df['total_freight']
)
```

### Delivery Lead Time

```python
df['days_to_delivery'] = (
    df['order_delivered_customer_date']
    - df['order_purchase_timestamp']
).dt.days
```

---

## Phase 5 — PostgreSQL Load

The final dataset is loaded into PostgreSQL for analytical querying.

### Database Setup

```sql
CREATE DATABASE pulse_analytics;

CREATE USER pulse_user
WITH PASSWORD 'your_password';

GRANT ALL PRIVILEGES
ON DATABASE pulse_analytics
TO pulse_user;
```

### Connection String

```python
CONN_STR = (
    "postgresql://pulse_user:"
    "your_password@localhost:5432/pulse_analytics"
)
```

### Load Strategy

The pipeline:

1. Creates the analytics table if it does not exist
2. Truncates existing data
3. Loads fresh records
4. Preserves indexes and schema

```python
load_to_postgres(
    df,
    CONN_STR,
    table_name='olist_enriched'
)
```

### Database Table

```sql
olist_enriched
```

Contains:

* Transaction data
* Customer attributes
* Holiday attributes
* Engineered features
* Revenue metrics

---

## Analytics Schema

### Core Metrics

| Column           | Description        |
| ---------------- | ------------------ |
| total_price      | Product value      |
| total_freight    | Shipping cost      |
| total_payment    | Payment amount     |
| total_revenue    | Product + freight  |
| days_to_delivery | Delivery lead time |

### Time Dimensions

| Column      | Description   |
| ----------- | ------------- |
| order_date  | Calendar date |
| order_year  | Year          |
| order_month | Month         |
| order_week  | ISO week      |
| day_of_week | Weekday       |
| hour_of_day | Hour          |

### Holiday Dimensions

| Column       | Description       |
| ------------ | ----------------- |
| is_holiday   | Holiday indicator |
| holiday_name | Holiday name      |
| holiday_type | Holiday category  |
| holiday_date | Holiday date      |

---

# SQL Optimization

The schema includes indexes for common analytical queries.

```sql
CREATE INDEX IF NOT EXISTS idx_order_date
ON olist_enriched(order_date);

CREATE INDEX IF NOT EXISTS idx_is_holiday
ON olist_enriched(is_holiday);

CREATE INDEX IF NOT EXISTS idx_order_state
ON olist_enriched(customer_state);
```

---

# Validation & QA

Validation queries are provided in:

```text
sql/validate.sql
```

### Checks Performed

#### Row Count Verification

```sql
SELECT COUNT(*)
FROM olist_enriched;
```

#### Null Audits

```sql
SELECT
    SUM(CASE WHEN order_purchase_timestamp IS NULL THEN 1 ELSE 0 END),
    SUM(CASE WHEN total_revenue IS NULL THEN 1 ELSE 0 END)
FROM olist_enriched;
```

#### Holiday Analysis

```sql
SELECT
    is_holiday,
    COUNT(*)
FROM olist_enriched
GROUP BY is_holiday;
```

#### Revenue Comparison

```sql
SELECT
    is_holiday,
    ROUND(AVG(total_revenue),2)
FROM olist_enriched
GROUP BY is_holiday;
```

#### Yearly Trends

```sql
SELECT
    order_year,
    COUNT(*)
FROM olist_enriched
GROUP BY order_year
ORDER BY order_year;
```

---

# Project Structure

```text
pulse-analytics/
│
├── data/
│   └── raw/
│       └── Olist CSV files
│
├── pipeline/
│   ├── ingest.py
│   ├── enrich.py
│   ├── clean.py
│   ├── features.py
│   └── load.py
│
├── sql/
│   ├── create_table.sql
│   └── validate.sql
│
├── docs/
│   ├── data_lineage.md
│   └── data_dictionary.md
│
├── main.py
├── requirements.txt
└── README.md
```

---

# Installation

## 1. Clone Repository

```bash
git clone https://github.com/your-username/pulse-analytics.git

cd pulse-analytics
```

## 2. Create Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Mac/Linux

```bash
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Dataset Setup

Download the Olist Brazilian E-Commerce Dataset from Kaggle:

https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

Place the CSV files in:

```text
data/raw/
```

Required files:

```text
olist_orders_dataset.csv
olist_order_items_dataset.csv
olist_customers_dataset.csv
olist_order_payments_dataset.csv
```

---

# PostgreSQL Usage

### Connect to the Database

```bash
psql -U pulse_user -d pulse_analytics
```

Exit:

```sql
\q
```

### Run SQL Commands Directly

```bash
psql -U pulse_user -d pulse_analytics \
-c "DROP TABLE IF EXISTS olist_enriched;"
```

### Execute SQL Files

```bash
psql -U pulse_user -d pulse_analytics \
-f sql/create_table.sql
```

---

# Running the Pipeline

Execute the complete workflow:

```bash
python main.py
```

Expected output:

```text
--- Phase 1: Ingest ---
Loaded 100,000 rows

--- Phase 2: Enrich ---
Fetched holiday records

--- Phase 3: Clean ---
All quality checks passed

--- Phase 4: Feature Engineering ---

--- Phase 5: Load ---
Loaded rows into olist_enriched

Pipeline complete.
```

---

# Example Business Questions

This dataset can help answer:

* Do holidays increase order volume?
* Do holidays influence revenue?
* Which weekdays generate the most sales?
* Which Brazilian states generate the most revenue?
* How long do deliveries take on average?
* What purchasing hours drive peak activity?
* Are holiday purchases associated with higher order values?

---

# Future Enhancements

Potential next steps:

* Incremental loading strategy
* Docker containerization
* Airflow orchestration
* dbt transformations
* Automated unit testing
* Data quality monitoring
* AWS deployment
* GCP deployment
* Azure deployment
* CI/CD automation
* Power BI dashboards
* Tableau dashboards

---

# Requirements

```text
pandas==2.2.0
requests==2.31.0
sqlalchemy==2.0.0
psycopg2-binary==2.9.9
```

---

# Key Skills Demonstrated

* Data Engineering
* ETL / ELT Design
* API Integration
* Data Quality Validation
* Feature Engineering
* SQL Development
* PostgreSQL Administration
* Analytics Data Modeling
* Python Data Processing
* Pipeline Orchestration

---

# License

This project is intended for educational, portfolio, and demonstration purposes.

---

# Author

**Binah Utuedor*

An end-to-end data engineering project showcasing modern ETL development, API integration, PostgreSQL loading, and analytics-ready data modeling.
