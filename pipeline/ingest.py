"""
==============================================================
Data Ingestion Module

This module is responsible for:

1. Reading the raw Olist CSV datasets.
2. Performing lightweight aggregations.
3. Merging the datasets into a single DataFrame.
4. Supporting incremental extraction by loading only
   records newer than the last successful pipeline run.

This module intentionally performs NO cleaning or feature
engineering. Those belong in later pipeline stages.

Pipeline Stage:
Raw CSV Files
        ↓
    Ingestion
==============================================================
"""

import pandas as pd


def load_olist(
    data_path: str = "data/raw/",
    last_loaded=None
) -> pd.DataFrame:
    """
    Load and merge the Olist datasets.

    Parameters
    ----------
    data_path : str
        Directory containing the raw CSV files.

    last_loaded : datetime, optional
        Watermark timestamp retrieved from the metadata table.

        If supplied, only orders newer than this timestamp
        are extracted (incremental loading).

        If None, every order is loaded.

    Returns
    -------
    pd.DataFrame
        Combined Olist dataset.
    """

    print("\nLoading raw datasets...")

    # ======================================================
    # Orders
    # ======================================================

    orders = pd.read_csv(
        f"{data_path}olist_orders_dataset.csv"
    )

    # Convert purchase timestamp to datetime so that
    # incremental filtering can be performed correctly.
    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"]
    )

    # ======================================================
    # Incremental Extraction
    # ======================================================
    #
    # Only keep records that are newer than the timestamp
    # stored in the metadata table.
    #
    # During the very first pipeline execution,
    # last_loaded will be 1900-01-01,
    # therefore every record will be extracted.
    # ======================================================

    if last_loaded is not None:

        orders = orders[
            orders["order_purchase_timestamp"] > last_loaded
        ]

        print(
            f"Incremental extraction complete."
            f"\nNew orders found: {len(orders):,}"
        )

    else:

        print(
            f"Full extraction complete."
            f"\nOrders loaded: {len(orders):,}"
        )

    # ======================================================
    # If there are no new orders,
    # return an empty DataFrame immediately.
    #
    # This avoids reading the remaining CSV files
    # unnecessarily.
    # ======================================================

    if orders.empty:

        print("No new orders found.")

        return pd.DataFrame()

    # ======================================================
    # Load remaining datasets
    # ======================================================

    customers = pd.read_csv(
        f"{data_path}olist_customers_dataset.csv"
    )

    items = pd.read_csv(
        f"{data_path}olist_order_items_dataset.csv"
    )

    payments = pd.read_csv(
        f"{data_path}olist_order_payments_dataset.csv"
    )

    # ======================================================
    # Aggregate Payments
    # ======================================================
    #
    # One order may have multiple payment records.
    #
    # Example:
    #
    # Order A
    # Card = 100
    # Voucher = 20
    #
    # becomes
    #
    # Order A
    # Total Payment = 120
    # ======================================================

    payments_agg = (

        payments

        .groupby("order_id")

        .agg(

            total_payment=("payment_value", "sum")

        )

        .reset_index()

    )

    # ======================================================
    # Aggregate Order Items
    # ======================================================
    #
    # Multiple products may belong to one order.
    #
    # Calculate:
    #
    # • Number of items
    # • Total product price
    # • Total freight
    # ======================================================

    items_agg = (

        items

        .groupby("order_id")

        .agg(

            item_count=("order_item_id", "count"),

            total_price=("price", "sum"),

            total_freight=("freight_value", "sum")

        )

        .reset_index()

    )

    # ======================================================
    # Merge datasets
    # ======================================================
    #
    # Orders
    #      LEFT JOIN Customers
    #      LEFT JOIN Item Aggregates
    #      LEFT JOIN Payment Aggregates
    # ======================================================

    df = (

        orders

        .merge(
            customers,
            on="customer_id",
            how="left"
        )

        .merge(
            items_agg,
            on="order_id",
            how="left"
        )

        .merge(
            payments_agg,
            on="order_id",
            how="left"
        )

    )

    print(f"\nMerged dataset contains {len(df):,} orders.")

    return df