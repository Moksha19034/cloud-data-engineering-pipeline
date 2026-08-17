import pandas as pd
from pathlib import Path


# =========================================================
# INPUT FILE
# =========================================================

INPUT_FILE = Path("data/staging/posts.parquet")


# =========================================================
# EXPECTED SCHEMA
# =========================================================

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


# =========================================================
# SCHEMA VALIDATION
# =========================================================

def validate_schema():
    print("Starting schema validation...")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Data file not found: {INPUT_FILE}"
        )

    df = pd.read_parquet(INPUT_FILE)

    actual_columns = set(df.columns)
    expected_columns = set(EXPECTED_COLUMNS.keys())

    # -----------------------------------------------------
    # Missing columns
    # -----------------------------------------------------

    missing_columns = expected_columns - actual_columns

    if missing_columns:
        raise ValueError(
            f"SCHEMA FAILURE: Missing columns: "
            f"{sorted(missing_columns)}"
        )

    # -----------------------------------------------------
    # Unexpected columns
    # -----------------------------------------------------

    unexpected_columns = actual_columns - expected_columns

    if unexpected_columns:
        raise ValueError(
            f"SCHEMA FAILURE: Unexpected columns: "
            f"{sorted(unexpected_columns)}"
        )

    # -----------------------------------------------------
    # Data types
    # -----------------------------------------------------

    for column, expected_type in EXPECTED_COLUMNS.items():

        if expected_type == "int":

            if not pd.api.types.is_integer_dtype(
                df[column]
            ):
                raise TypeError(
                    f"SCHEMA FAILURE: "
                    f"{column} must be integer"
                )

        elif expected_type == "datetime":

            if not pd.api.types.is_datetime64_any_dtype(
                df[column]
            ):
                raise TypeError(
                    f"SCHEMA FAILURE: "
                    f"{column} must be datetime"
                )

        elif expected_type == "string":

            if not pd.api.types.is_string_dtype(
                df[column]
            ):
                raise TypeError(
                    f"SCHEMA FAILURE: "
                    f"{column} must be string"
                )

    print("✓ All required columns present")
    print("✓ No unexpected columns")
    print("✓ Data types are correct")
    print("SCHEMA VALIDATION: PASSED")


# =========================================================
# MAIN
# =========================================================

def main():
    validate_schema()


if __name__ == "__main__":
    main()
