"""
==============================================================
Pulse Analytics
Main ETL Pipeline

Pipeline Workflow

Raw CSV Files
        │
        ▼
Incremental Ingestion
        │
        ▼
Holiday Enrichment
        │
        ▼
Data Cleaning
        │
        ▼
Quality Validation
        │
        ▼
Feature Engineering
        │
        ▼
PostgreSQL Load
        │
        ▼
Update Pipeline Metadata
==============================================================
"""

from pipeline.ingest import load_olist
from pipeline.enrich import (
    fetch_holidays,
    enrich_with_holidays
)
from pipeline.clean import (
    clean,
    assert_quality
)
from pipeline.features import engineer_features
from pipeline.load import load_to_postgres
from pipeline.metadata import (
    get_last_loaded,
    update_last_loaded
)

import os
from dotenv import load_dotenv

# ==========================================================
# Load environment variables
# ==========================================================

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

CONN_STR = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

DATA_PATH = "data/raw/"
YEARS = [2016, 2017, 2018]


def main():
    """
    Execute the complete ETL pipeline.
    """

    print("=" * 60)
    print("PULSE ANALYTICS ETL PIPELINE")
    print("=" * 60)

    # ======================================================
    # Create database objects if they do not exist.
    #
    # This creates:
    #   • pipeline_metadata
    #   • olist_enriched
    # ======================================================

    load_to_postgres(
        df=None,
        conn_str=CONN_STR,
        initialize_only=True
    )

    # ======================================================
    # Read pipeline metadata
    # ======================================================

    print("\nReading pipeline metadata...")

    last_loaded = get_last_loaded(CONN_STR)

    print(f"Last successful load: {last_loaded}")

    # ======================================================
    # Phase 1 - Incremental Ingestion
    # ======================================================

    print("\nPhase 1 - Data Ingestion")

    df = load_olist(
        data_path=DATA_PATH,
        last_loaded=last_loaded
    )

    # Stop if nothing new exists.

    if df.empty:

        print("\nNo new records detected.")

        print("Pipeline completed successfully.")

        return

    # ======================================================
    # Phase 2 - Holiday Enrichment
    # ======================================================

    print("\nPhase 2 - Holiday Enrichment")

    holidays = fetch_holidays(
        YEARS,
        country_code="BR"
    )

    df = enrich_with_holidays(
        df,
        holidays
    )

    # ======================================================
    # Phase 3 - Data Cleaning
    # ======================================================

    print("\nPhase 3 - Data Cleaning")

    df = clean(df)

    # ======================================================
    # Phase 4 - Data Quality Validation
    # ======================================================

    print("\nPhase 4 - Quality Validation")

    assert_quality(df)

    # ======================================================
    # Phase 5 - Feature Engineering
    # ======================================================

    print("\nPhase 5 - Feature Engineering")

    df = engineer_features(df)

    # ======================================================
    # Phase 6 - Load to PostgreSQL
    # ======================================================

    print("\nPhase 6 - PostgreSQL Load")

    load_to_postgres(
        df=df,
        conn_str=CONN_STR
    )

    # ======================================================
    # Update Metadata Watermark
    # ======================================================

    latest_timestamp = df[
        "order_purchase_timestamp"
    ].max()

    update_last_loaded(
        CONN_STR,
        latest_timestamp
    )

    # ======================================================
    # Pipeline Summary
    # ======================================================

    print("\n" + "=" * 60)

    print("Pipeline completed successfully.")

    print(f"Rows processed : {len(df):,}")

    print(f"Latest watermark: {latest_timestamp}")

    print("=" * 60)

    return df


if __name__ == "__main__":
    main()