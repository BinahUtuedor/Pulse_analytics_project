import requests
import pandas as pd

def fetch_holidays(years: list, country_code='BR') -> pd.DataFrame:
    all_holidays = []

    for year in years:
        url = f'https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}'
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise error on bad status

        holidays = response.json()
        for h in holidays:
            all_holidays.append({
                'holiday_date': h['date'],
                'holiday_name': h['name'],
                'holiday_type': h.get('types', [''])[0]
            })

    df = pd.DataFrame(all_holidays)
    df['holiday_date'] = pd.to_datetime(df['holiday_date'])
    print(f'Fetched {len(df)} holiday records')
    return df


def enrich_with_holidays(orders_df: pd.DataFrame,
                          holidays_df: pd.DataFrame) -> pd.DataFrame:
    # Extract date from timestamp
    orders_df = orders_df.copy()
    orders_df['order_date'] = pd.to_datetime(
        orders_df['order_purchase_timestamp']
    ).dt.normalize()  # strips time, keeps date

    # Left join: all orders kept, holiday cols null if not a holiday
    enriched = orders_df.merge(
        holidays_df,
        left_on='order_date',
        right_on='holiday_date',
        how='left'
    )

    return enriched
