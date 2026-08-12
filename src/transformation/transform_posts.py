import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def find_latest_raw_file():
    raw_files = sorted(Path("data/raw").glob("posts_*.json"))

    if not raw_files:
        raise FileNotFoundError("No raw JSON files found")

    return raw_files[-1]


def load_raw_data(file_path):
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def transform_data(data):
    df = pd.DataFrame(data)

    df = df.rename(
        columns={
            "userId": "user_id",
            "id": "post_id",
        }
    )

    df["title_length"] = df["title"].str.len()
    df["body_length"] = df["body"].str.len()

    df["processed_at"] = datetime.now(timezone.utc)

    return df


def validate_data(df):
    required_columns = {
        "user_id",
        "post_id",
        "title",
        "body",
        "title_length",
        "body_length",
        "processed_at",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")

    if df.empty:
        raise ValueError("Transformed dataset is empty")

    if df["post_id"].duplicated().any():
        raise ValueError("Duplicate post_id values detected")


def save_parquet(df):
    output_dir = Path("data/staging")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "posts.parquet"

    df.to_parquet(output_file, index=False)

    print(f"Staging data saved to: {output_file}")


def main():
    print("Starting transformation...")

    raw_file = find_latest_raw_file()

    print(f"Reading: {raw_file}")

    raw_data = load_raw_data(raw_file)

    df = transform_data(raw_data)

    validate_data(df)

    save_parquet(df)

    print(f"Records processed: {len(df)}")
    print("Transformation completed successfully.")


if __name__ == "__main__":
    main()
