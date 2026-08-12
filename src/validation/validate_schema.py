import pandas as pd
from pathlib import Path


INPUT_FILE = Path("data/curated/posts.parquet")


EXPECTED_COLUMNS = {
    "user_id": "int",
    "post_id": "int",
    "title": "string",
    "body": "string",
    "title_length": "int",
    "body_length": "int",
    "processed_at": "datetime",
    "source_system": "string",
    "source_file": "string",
}


def validate_schema():
    print("Starting schema validation...")

    df = pd.read_parquet(INPUT_FILE)

    actual_columns = set(df.columns)
    expected_columns = set(EXPECTED_COLUMNS.keys())

    # Check for missing columns
    missing_columns = expected_columns - actual_columns

    if missing_columns:
        raise ValueError(
            f"SCHEMA FAILURE: Missing columns: {sorted(missing_columns)}"
        )

    # Check for unexpected columns
    unexpected_columns = actual_columns - expected_columns

    if unexpected_columns:
        raise ValueError(
            f"SCHEMA FAILURE: Unexpected columns: {sorted(unexpected_columns)}"
        )

    # Check data types
    for column, expected_type in EXPECTED_COLUMNS.items():

        if expected_type == "int":
            if not pd.api.types.is_integer_dtype(df[column]):
                raise TypeError(
                    f"SCHEMA FAILURE: {column} must be integer"
                )

        elif expected_type == "datetime":
            if not pd.api.types.is_datetime64_any_dtype(df[column]):
                raise TypeError(
                    f"SCHEMA FAILURE: {column} must be datetime"
                )

        elif expected_type == "string":
            if not pd.api.types.is_string_dtype(df[column]):
                raise TypeError(
                    f"SCHEMA FAILURE: {column} must be string"
                )

    print("✓ All required columns present")
    print("✓ No unexpected columns")
    print("✓ Data types are correct")
    print("SCHEMA VALIDATION: PASSED")


def main():
    validate_schema()


if __name__ == "__main__":
    main()
