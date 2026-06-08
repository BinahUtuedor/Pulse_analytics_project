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


def main():

    print("Loading Olist data...")
    orders_df = load_olist()

    print("Fetching holidays...")
    holidays_df = fetch_holidays(
        [2016, 2017, 2018],
        country_code='BR'
    )

    print("Enriching orders...")
    enriched_df = enrich_with_holidays(
        orders_df,
        holidays_df
    )

    print("Cleaning data...")
    clean_df = clean(enriched_df)

    print("Running quality checks...")
    assert_quality(clean_df)

    print("Engineering features...")
    feature_df = engineer_features(clean_df)

    print(feature_df.head())
    print(feature_df.info())

    return feature_df


if __name__ == "__main__":
    final_df = main()
    print(final_df.head())