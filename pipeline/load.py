from sqlalchemy import create_engine, text
import pandas as pd


def load_to_postgres(df: pd.DataFrame,
                      conn_str: str,
                      table_name: str = 'olist_enriched'):

    engine = create_engine(conn_str)

    # Step 1: Ensure schema exists (safe to run repeatedly)
    with engine.begin() as conn:
        with open('sql/create_table.sql', 'r', encoding='utf-8') as f:
            conn.execute(text(f.read()))

    # Step 2: Clear existing data (recommended approach)
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {table_name}"))

    # Step 3: Load fresh data (append into empty table)
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists='append',
        index=False,
        chunksize=1000
    )

    print(f'Loaded {len(df):,} rows into {table_name}')