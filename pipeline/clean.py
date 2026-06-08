import pandas as pd


def clean(df: pd.DataFrame) -> pd.DataFrame:
    original_len = len(df)

    # Drop duplicate order IDs
    df = df.drop_duplicates(subset=['order_id'])

    # Drop rows with no purchase timestamp
    df = df.dropna(subset=['order_purchase_timestamp'])

    # Keep only active/completed orders
    df = df[df['order_status'].isin([
        'delivered',
        'shipped',
        'approved',
        'processing'
    ])]

    # Fill holiday nulls
    df['holiday_name'] = df['holiday_name'].fillna('None')
    df['holiday_type'] = df['holiday_type'].fillna('None')

    # Parse date columns
    date_cols = [
        'order_purchase_timestamp',
        'order_approved_at',
        'order_delivered_carrier_date',
        'order_delivered_customer_date',
        'order_estimated_delivery_date'
    ]

    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Numeric columns
    df['total_price'] = df['total_price'].fillna(0).astype(float)
    df['total_freight'] = df['total_freight'].fillna(0).astype(float)
    df['total_payment'] = df['total_payment'].fillna(0).astype(float)
    df['item_count'] = df['item_count'].fillna(0).astype(int)

    print(f'Rows before: {original_len:,} | After: {len(df):,}')

    return df


def assert_quality(df: pd.DataFrame):
    assert df['order_id'].nunique() == len(df), 'Duplicate order IDs found'
    assert df['order_purchase_timestamp'].isna().sum() == 0, 'Null timestamps found'
    assert (df['total_price'] >= 0).all(), 'Negative prices found'

    print('All quality checks passed.')
