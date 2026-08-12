import json
from pathlib import Path

import pandas as pd


def find_latest_raw_file():
    raw_files = sorted(Path("data/raw").glob("users_*.json"))

    if not raw_files:
        raise FileNotFoundError("No raw user JSON files found")

    return raw_files[-1]


def load_raw_data(file_path):
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def transform_data(data):
    df = pd.DataFrame(data)

    df = df.rename(
        columns={
            "id": "user_id",
        }
    )

    # Keep only the fields we need for analytics.
    df = df[
        [
            "user_id",
            "name",
            "username",
            "email",
            "phone",
            "website",
        ]
    ]

    return df


def validate_data(df):
    required_columns = {
        "user_id",
        "name",
        "username",
        "email",
        "phone",
        "website",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")

    if df.empty:
        raise ValueError("User dataset is empty")

    if df["user_id"].duplicated().any():
        raise ValueError("Duplicate user_id values detected")

    if df["user_id"].isnull().any():
        raise ValueError("Null user_id values detected")


def save_parquet(df):
    output_dir = Path("data/curated")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "users.parquet"

    df.to_parquet(output_file, index=False)

    print(f"Curated users saved to: {output_file}")


def main():
    print("Starting user transformation...")

    raw_file = find_latest_raw_file()

    print(f"Reading: {raw_file}")

    raw_data = load_raw_data(raw_file)

    df = transform_data(raw_data)

    validate_data(df)

    save_parquet(df)

    print(f"Users processed: {len(df)}")
    print("User transformation completed successfully.")


if __name__ == "__main__":
    main()
