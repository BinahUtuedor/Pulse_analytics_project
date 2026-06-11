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
SELECT *
FROM vw_monthly_revenue
ORDER BY order_year, order_month
"""

df = pd.read_sql(query, engine)

df.to_csv("outputs/revenue/monthly_revenue.csv", index=False)
df.to_json("outputs/revenue/monthly_revenue.json", orient="records", indent=4)

print(df.head())

print(
    "\nTotal Revenue:",
    round(df["total_revenue"].sum(), 2)
)

print(
    "Average Monthly Revenue:",
    round(df["total_revenue"].mean(), 2)
)