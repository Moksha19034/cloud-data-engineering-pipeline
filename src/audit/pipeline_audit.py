from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


AUDIT_FILE = Path(
    "data/audit/pipeline_runs.parquet"
)


def generate_run_id():
    """
    Generate a unique identifier for each
    pipeline run.
    """

    timestamp = datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    return timestamp


def create_audit_record(
    run_id,
    started_at,
    finished_at,
    status,
    total_duration,
    total_stages,
    successful_stages,
    failed_stage=None,
    error=None,
    stage_metrics=None,
    quality_metrics=None,
):
    """
    Create one structured pipeline audit record.
    """

    stage_metrics = stage_metrics or {}
    quality_metrics = quality_metrics or {}

    return {
        # -----------------------------------------------------
        # Pipeline execution
        # -----------------------------------------------------

        "run_id": run_id,
        "started_at": started_at,
        "finished_at": finished_at,
        "status": status,
        "total_duration": float(
            total_duration
        ),
        "total_stages": int(
            total_stages
        ),
        "successful_stages": int(
            successful_stages
        ),
        "failed_stage": failed_stage,
        "error": error,

        # -----------------------------------------------------
        # Stage performance
        # -----------------------------------------------------

        "fastest_stage": stage_metrics.get(
            "fastest_stage"
        ),
        "fastest_duration": float(
            stage_metrics.get(
                "fastest_duration",
                0.0,
            )
        ),
        "slowest_stage": stage_metrics.get(
            "slowest_stage"
        ),
        "slowest_duration": float(
            stage_metrics.get(
                "slowest_duration",
                0.0,
            )
        ),

        # -----------------------------------------------------
        # Data quality
        # -----------------------------------------------------

        "records_checked": int(
            quality_metrics.get(
                "records_checked",
                0,
            )
        ),
        "null_values": int(
            quality_metrics.get(
                "null_values",
                0,
            )
        ),
        "duplicate_post_ids": int(
            quality_metrics.get(
                "duplicate_post_ids",
                0,
            )
        ),
        "quality_status": quality_metrics.get(
            "quality_status"
        ),
    }


def _ensure_audit_columns(df):
    """
    Ensure historical audit records contain
    all fields introduced by newer versions
    of the audit schema.
    """

    defaults = {
        "fastest_stage": None,
        "fastest_duration": 0.0,
        "slowest_stage": None,
        "slowest_duration": 0.0,
        "records_checked": 0,
        "null_values": 0,
        "duplicate_post_ids": 0,
        "quality_status": None,
    }

    for column, default in defaults.items():

        if column not in df.columns:
            df[column] = default

    return df


def _prepare_audit_dataframe(df):
    """
    Normalize audit columns before writing
    to Parquet.

    This prevents schema conflicts between
    historical and new audit records.
    """

    if df.empty:
        return df

    # ---------------------------------------------------------
    # Timestamp normalization
    # ---------------------------------------------------------

    df["started_at"] = pd.to_datetime(
        df["started_at"],
        utc=True,
    )

    df["finished_at"] = pd.to_datetime(
        df["finished_at"],
        utc=True,
    )

    # ---------------------------------------------------------
    # Floating-point columns
    # ---------------------------------------------------------

    numeric_columns = [
        "total_duration",
        "fastest_duration",
        "slowest_duration",
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    # ---------------------------------------------------------
    # Integer columns
    # ---------------------------------------------------------

    integer_columns = [
        "total_stages",
        "successful_stages",
        "records_checked",
        "null_values",
        "duplicate_post_ids",
    ]

    for column in integer_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        ).astype("Int64")

    # ---------------------------------------------------------
    # String columns
    # ---------------------------------------------------------

    string_columns = [
        "run_id",
        "status",
        "failed_stage",
        "error",
        "fastest_stage",
        "slowest_stage",
        "quality_status",
    ]

    for column in string_columns:

        df[column] = df[column].astype(
            "string"
        )

    return df


def save_audit_record(record):
    """
    Append one audit record to the pipeline
    audit Parquet dataset.
    """

    AUDIT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ---------------------------------------------------------
    # New record
    # ---------------------------------------------------------

    new_record = pd.DataFrame(
        [record]
    )

    new_record = _ensure_audit_columns(
        new_record
    )

    new_record = _prepare_audit_dataframe(
        new_record
    )

    # ---------------------------------------------------------
    # Existing records
    # ---------------------------------------------------------

    if AUDIT_FILE.exists():

        existing = pd.read_parquet(
            AUDIT_FILE
        )

        existing = _ensure_audit_columns(
            existing
        )

        existing = _prepare_audit_dataframe(
            existing
        )

        result = pd.concat(
            [
                existing,
                new_record,
            ],
            ignore_index=True,
        )

    else:

        result = new_record

    # ---------------------------------------------------------
    # Final normalization
    # ---------------------------------------------------------

    result = _ensure_audit_columns(
        result
    )

    result = _prepare_audit_dataframe(
        result
    )

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    result.to_parquet(
        AUDIT_FILE,
        index=False,
    )


def main():
    print(
        "Pipeline audit module ready."
    )


if __name__ == "__main__":
    main()
