import pandas as pd

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ts = df['order_purchase_timestamp']

    # Holiday flag
    df['is_holiday'] = df['holiday_name'] != 'None'

    # Time-based features
    df['order_date']    = ts.dt.date
    df['order_year']    = ts.dt.year
    df['order_month']   = ts.dt.month
    df['order_week']    = ts.dt.isocalendar().week.astype(int)
    df['day_of_week']   = ts.dt.day_name()
    df['hour_of_day']   = ts.dt.hour
    df['is_weekend']    = ts.dt.dayofweek >= 5

    # Delivery delta (days)
    df['days_to_delivery'] = (
        df['order_delivered_customer_date'] - ts
    ).dt.days

    # Revenue metric
    df['total_revenue'] = df['total_price'] + df['total_freight']

    return df