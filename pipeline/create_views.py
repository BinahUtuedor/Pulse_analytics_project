from sqlalchemy import create_engine
from sqlalchemy import text

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

VIEW_FILES = [
    "sql/revenue_views.sql",
    "sql/holiday_views.sql",
    "sql/delivery_views.sql",
    "sql/geography_views.sql"
]

engine = create_engine(CONN_STR)

with engine.begin() as conn:

    for file in VIEW_FILES:

        print(f"Executing {file}")

        with open(file, "r", encoding="utf-8") as f:
            sql = f.read()

        conn.execute(text(sql))

print("Views created successfully")