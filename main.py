# main.py
from pipeline.ingest   import load_olist
from pipeline.enrich   import fetch_holidays, enrich_with_holidays
from pipeline.clean    import clean, assert_quality
from pipeline.features import engineer_features
from pipeline.load     import load_to_postgres

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


DATA_PATH = 'data/raw/'
YEARS = [2016, 2017, 2018]

if __name__ == '__main__':
    print('--- Phase 1: Ingest ---')
    df = load_olist(DATA_PATH)

    print('--- Phase 2: Enrich ---')
    holidays = fetch_holidays(YEARS)
    df = enrich_with_holidays(df, holidays)

    print('--- Phase 3: Clean ---')
    df = clean(df)
    assert_quality(df)

    print('--- Phase 4: Feature Engineering ---')
    df = engineer_features(df)

    print('--- Phase 5: Load ---')
    load_to_postgres(df, CONN_STR)

    print('Pipeline complete. Rows loaded:', len(df))
