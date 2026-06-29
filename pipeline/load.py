"""
==============================================================
Database Load Module

Responsibilities
----------------
1. Create required database objects.
2. Initialize metadata table.
3. Load new data into a staging table.
4. Merge staging data into the production table.
5. Prevent duplicate records using PostgreSQL UPSERT.

Pipeline Stage

Feature Engineering
        │
        ▼
 Staging Table
        │
        ▼
Production Table (olist_enriched)
==============================================================
"""

from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text


def load_to_postgres(
    df: pd.DataFrame | None,
    conn_str: str,
    table_name: str = "olist_enriched",
    staging_table: str = "olist_enriched_staging",
    initialize_only: bool = False
):
    """
    Create database objects and load data into PostgreSQL.

    Parameters
    ----------
    df : pd.DataFrame | None
        DataFrame to load.

    conn_str : str
        SQLAlchemy PostgreSQL connection string.

    table_name : str
        Production table.

    staging_table : str
        Temporary staging table.

    initialize_only : bool
        If True only creates required tables.
    """

    engine = create_engine(conn_str)

    sql_dir = Path(__file__).resolve().parent.parent / "sql"

    metadata_sql = sql_dir / "create_metadata.sql"
    table_sql = sql_dir / "create_table.sql"

    # ==========================================================
    # Create required tables
    # ==========================================================

    with engine.begin() as conn:

        print("Creating metadata table (if needed)...")

        conn.execute(text(metadata_sql.read_text()))

        print("Creating analytics table (if needed)...")

        conn.execute(text(table_sql.read_text()))

    if initialize_only:

        print("Database initialization complete.")

        return

    if df is None or df.empty:

        print("No new rows to load.")

        return

    # ==========================================================
    # Drop staging table if it exists
    # ==========================================================

    with engine.begin() as conn:

        conn.execute(
            text(
                f"""
                DROP TABLE IF EXISTS {staging_table};
                """
            )
        )

    # ==========================================================
    # Load DataFrame into staging table
    # ==========================================================

    print("Loading data into staging table...")

    df.to_sql(

        staging_table,

        engine,

        if_exists="replace",

        index=False,

        chunksize=5000,

        method="multi"

    )

    # ==========================================================
    # Merge staging table into production table
    #
    # Existing order_ids are ignored.
    #
    # This makes the pipeline idempotent.
    # ==========================================================

    print("Merging staging table into production table...")

    columns = list(df.columns)

    column_list = ", ".join(columns)

    merge_sql = f"""
    INSERT INTO {table_name}
    ({column_list})

    SELECT
    {column_list}

    FROM {staging_table}

    ON CONFLICT (order_id)
    DO NOTHING;
    """

    with engine.begin() as conn:

        conn.execute(text(merge_sql))

        conn.execute(

            text(

                f"""
                DROP TABLE IF EXISTS {staging_table};
                """

            )

        )

    print(f"Successfully loaded {len(df):,} records.")