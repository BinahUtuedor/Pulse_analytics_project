import pandas as pd

from enrich import fetch_holidays, enrich_with_holidays

def load_olist(data_path='data/raw/'):
    orders   = pd.read_csv(f'{data_path}olist_orders_dataset.csv')
    items    = pd.read_csv(f'{data_path}olist_order_items_dataset.csv')
    customers = pd.read_csv(f'{data_path}olist_customers_dataset.csv')
    payments = pd.read_csv(f'{data_path}olist_order_payments_dataset.csv')

    # Aggregate payments per order
    payments_agg = payments.groupby('order_id').agg(
        total_payment=('payment_value', 'sum')
    ).reset_index()

    # Aggregate items per order
    items_agg = items.groupby('order_id').agg(
        item_count=('order_item_id', 'count'),
        total_price=('price', 'sum'),
        total_freight=('freight_value', 'sum')
    ).reset_index()

    # Merge all together
    df = (orders
          .merge(customers, on='customer_id', how='left')
          .merge(items_agg, on='order_id', how='left')
          .merge(payments_agg, on='order_id', how='left'))

    print(f'Loaded {len(df):,} rows')
    return df
    
if __name__ == '__main__':
    orders_df = load_olist()

    # Olist dataset spans 2016-2018
    holidays_df = fetch_holidays([2016, 2017, 2018], country_code='BR')

    enriched_df = enrich_with_holidays(
        orders_df,
        holidays_df
    )

    print(enriched_df.head())