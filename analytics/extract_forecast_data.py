import pandas as pd
from sqlalchemy import create_engine

import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# CONN_STR = 'postgresql://pulse_user:password@localhost:5432/pulse_analytics'

CONN_STR = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    CONN_STR
)

query = """
SELECT
    order_date,
    SUM(total_revenue) AS revenue
FROM olist_enriched
GROUP BY order_date
ORDER BY order_date
"""

df = pd.read_sql(query, engine)


df.to_csv(
    "outputs/extracts/forecast_daily_revenue.csv",
    index=False
)

print(df.head())
