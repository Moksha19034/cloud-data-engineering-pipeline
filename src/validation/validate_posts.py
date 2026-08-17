import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv


DATA_FILE = Path("data/staging/posts.parquet")


def load_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Data file not found: {DATA_FILE}"
        )

    return pd.read_parquet(DATA_FILE)


load_dotenv()

DATA_FRESHNESS_HOURS = int(
    os.getenv("DATA_FRESHNESS_HOURS", "24")
)


def validate_freshness(df):
    processed_at = pd.to_datetime(
        df["processed_at"],
        utc=True,
    )

    latest_processed_at = processed_at.max()

    current_time = datetime.now(timezone.utc)

    age = (
        current_time
        - latest_processed_at.to_pydatetime()
    )

    max_age = timedelta(
        hours=DATA_FRESHNESS_HOURS
    )

    if age > max_age:
        raise ValueError(
            f"Data freshness SLA violated: "
            f"age={age}, "
            f"maximum_allowed={max_age}"
        )

    print(
        f"✓ Data freshness check passed | age={age}"
    )


def validate_required_columns(df):
    required_columns = {
        "user_id",
        "post_id",
        "title",
        "body",
        "title_length",
        "body_length",
        "processed_at",
    }

    missing = (
        required_columns
        - set(df.columns)
    )

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    print("✓ Required columns present")


def validate_not_empty(df):
    if df.empty:
        raise ValueError(
            "Dataset is empty"
        )

    print(
        f"✓ Dataset contains {len(df)} records"
    )


def validate_unique_post_ids(df):
    if df["post_id"].duplicated().any():
        raise ValueError(
            "Duplicate post_id values found"
        )

    print(
        "✓ post_id values are unique"
    )


def validate_nulls(df):
    columns_to_check = [
        "user_id",
        "post_id",
        "title",
        "body",
    ]

    null_counts = (
        df[columns_to_check]
        .isnull()
        .sum()
    )

    if null_counts.any():
        raise ValueError(
            "Null values found:\n"
            f"{null_counts[null_counts > 0]}"
        )

    print(
        "✓ No null values in required fields"
    )


def validate_lengths(df):
    calculated_title_length = (
        df["title"].str.len()
    )

    calculated_body_length = (
        df["body"].str.len()
    )

    if not (
        df["title_length"]
        == calculated_title_length
    ).all():
        raise ValueError(
            "title_length values are incorrect"
        )

    if not (
        df["body_length"]
        == calculated_body_length
    ).all():
        raise ValueError(
            "body_length values are incorrect"
        )

    print(
        "✓ Derived length columns are correct"
    )


def main():
    print(
        "Starting data quality validation..."
    )

    df = load_data()

    validate_required_columns(df)
    validate_not_empty(df)
    validate_unique_post_ids(df)
    validate_nulls(df)
    validate_lengths(df)

    from src.validation.quality_metrics import (
        get_quality_metrics,
        save_quality_metrics,
    )

    quality_metrics = get_quality_metrics(df)

    save_quality_metrics(
        quality_metrics
    )

    print(
        "\nDATA QUALITY CHECK: PASSED"
    )

    print(
        f"Records checked: "
        f"{quality_metrics['records_checked']}"
    )

    print(
        f"Null values: "
        f"{quality_metrics['null_values']}"
    )

    print(
        f"Duplicate post IDs: "
        f"{quality_metrics['duplicate_post_ids']}"
    )

    print(
        f"Quality status: "
        f"{quality_metrics['quality_status']}"
    )

    return {
        "quality_metrics": quality_metrics,
    }


if __name__ == "__main__":
    main()
