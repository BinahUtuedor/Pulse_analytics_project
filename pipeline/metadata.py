"""
==============================================================
Pipeline Metadata Utilities

Stores and retrieves the ETL watermark.

The watermark is the latest order_purchase_timestamp
successfully loaded into PostgreSQL.
==============================================================
"""

from sqlalchemy import create_engine, text


PIPELINE_NAME = "olist_pipeline"


def get_last_loaded(conn_str: str):
    """
    Return the latest successful load timestamp.

    If the metadata record does not yet exist,
    return None.
    """

    engine = create_engine(conn_str)

    with engine.begin() as conn:

        result = conn.execute(

            text(
                """
                SELECT last_loaded
                FROM pipeline_metadata
                WHERE pipeline_name = :pipeline
                """
            ),

            {
                "pipeline": PIPELINE_NAME
            }

        )

        row = result.fetchone()

    if row is None:

        return None

    return row[0]


def update_last_loaded(
    conn_str: str,
    latest_timestamp
):
    """
    Update the watermark after a successful load.
    """

    engine = create_engine(conn_str)

    with engine.begin() as conn:

        conn.execute(

            text(
                """
                UPDATE pipeline_metadata

                SET last_loaded = :latest

                WHERE pipeline_name = :pipeline
                """
            ),

            {
                "latest": latest_timestamp,
                "pipeline": PIPELINE_NAME
            }

        )

    print(f"Watermark updated -> {latest_timestamp}")