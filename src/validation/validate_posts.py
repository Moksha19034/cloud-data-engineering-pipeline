from pathlib import Path

import pandas as pd


DATA_FILE = Path("data/curated/posts.parquet")


def load_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Data file not found: {DATA_FILE}")

    return pd.read_parquet(DATA_FILE)


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

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    print("✓ Required columns present")


def validate_not_empty(df):
    if df.empty:
        raise ValueError("Dataset is empty")

    print(f"✓ Dataset contains {len(df)} records")


def validate_unique_post_ids(df):
    if df["post_id"].duplicated().any():
        raise ValueError("Duplicate post_id values found")

    print("✓ post_id values are unique")


def validate_nulls(df):
    columns_to_check = [
        "user_id",
        "post_id",
        "title",
        "body",
    ]

    null_counts = df[columns_to_check].isnull().sum()

    if null_counts.any():
        raise ValueError(
            f"Null values found:\n{null_counts[null_counts > 0]}"
        )

    print("✓ No null values in required fields")


def validate_lengths(df):
    calculated_title_length = df["title"].str.len()
    calculated_body_length = df["body"].str.len()

    if not (df["title_length"] == calculated_title_length).all():
        raise ValueError("title_length values are incorrect")

    if not (df["body_length"] == calculated_body_length).all():
        raise ValueError("body_length values are incorrect")

    print("✓ Derived length columns are correct")


def main():
    print("Starting data quality validation...")

    df = load_data()

    validate_required_columns(df)
    validate_not_empty(df)
    validate_unique_post_ids(df)
    validate_nulls(df)
    validate_lengths(df)

    print("\nDATA QUALITY CHECK: PASSED")


if __name__ == "__main__":
    main()
