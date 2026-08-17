from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


AUDIT_FILE = Path(
    "data/audit/pipeline_runs.parquet"
)


def generate_run_id():
    """
    Generate a unique UTC-based pipeline run ID.
    """

    timestamp = datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    return timestamp


def get_total_retries(
    retry_information,
):
    """
    Return the total number of retries
    across all pipeline stages.
    """

    if not retry_information:
        return 0

    return int(
        sum(
            information.get(
                "retries",
                0,
            )
            for information
            in retry_information.values()
        )
    )


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
    retry_information=None,
):
    """
    Create one complete pipeline audit record.
    """

    stage_metrics = (
        stage_metrics or {}
    )

    quality_metrics = (
        quality_metrics or {}
    )

    retry_information = (
        retry_information or {}
    )

    return {
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": finished_at,
        "status": status,
        "total_duration": total_duration,
        "total_stages": total_stages,
        "successful_stages": successful_stages,
        "failed_stage": failed_stage,
        "error": error,

        # Stage performance
        "fastest_stage": stage_metrics.get(
            "fastest_stage"
        ),
        "slowest_stage": stage_metrics.get(
            "slowest_stage"
        ),
        "fastest_duration": stage_metrics.get(
            "fastest_duration"
        ),
        "slowest_duration": stage_metrics.get(
            "slowest_duration"
        ),

        # Data quality
        "records_checked": quality_metrics.get(
            "records_checked"
        ),
        "null_values": quality_metrics.get(
            "null_values"
        ),
        "duplicate_post_ids": quality_metrics.get(
            "duplicate_post_ids"
        ),
        "quality_status": quality_metrics.get(
            "quality_status"
        ),

        # Retry information
        "total_retries": get_total_retries(
            retry_information
        ),
        "retry_information": str(
            retry_information
        ),
    }


def normalize_audit_dataframe(
    df,
):
    """
    Normalize the audit dataframe schema
    before writing to Parquet.

    This protects the audit dataset from
    schema conflicts when new columns are
    introduced or when values arrive with
    inconsistent Python types.
    """

    df = df.copy()

    # ---------------------------------------------------------
    # Ensure required columns exist.
    # ---------------------------------------------------------

    required_columns = {
        "run_id": None,
        "started_at": None,
        "finished_at": None,
        "status": None,
        "total_duration": None,
        "total_stages": None,
        "successful_stages": None,
        "failed_stage": None,
        "error": None,
        "fastest_stage": None,
        "slowest_stage": None,
        "fastest_duration": None,
        "slowest_duration": None,
        "records_checked": None,
        "null_values": None,
        "duplicate_post_ids": None,
        "quality_status": None,
        "total_retries": None,
        "retry_information": None,
    }

    for column, default_value in (
        required_columns.items()
    ):
        if column not in df.columns:
            df[column] = default_value

    # ---------------------------------------------------------
    # Normalize timestamps.
    #
    # This is the important fix.
    #
    # Existing Parquet data contains timestamps.
    # New records may arrive as ISO strings.
    #
    # Convert everything to timezone-aware UTC
    # timestamps before writing.
    # ---------------------------------------------------------

    for column in (
        "started_at",
        "finished_at",
    ):
        df[column] = pd.to_datetime(
            df[column],
            utc=True,
            errors="coerce",
        )

    # ---------------------------------------------------------
    # Normalize numeric columns.
    # ---------------------------------------------------------

    numeric_columns = [
        "total_duration",
        "total_stages",
        "successful_stages",
        "fastest_duration",
        "slowest_duration",
        "records_checked",
        "null_values",
        "duplicate_post_ids",
        "total_retries",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    # ---------------------------------------------------------
    # Normalize text columns.
    #
    # Pandas nullable string dtype allows missing
    # values without mixing arbitrary Python objects.
    # ---------------------------------------------------------

    string_columns = [
        "run_id",
        "status",
        "failed_stage",
        "error",
        "fastest_stage",
        "slowest_stage",
        "quality_status",
        "retry_information",
    ]

    for column in string_columns:
        df[column] = (
            df[column].astype("string")
        )

    # ---------------------------------------------------------
    # Explicit column ordering.
    #
    # This makes the Parquet schema predictable.
    # ---------------------------------------------------------

    column_order = [
        "run_id",
        "started_at",
        "finished_at",
        "status",
        "total_duration",
        "total_stages",
        "successful_stages",
        "failed_stage",
        "error",
        "fastest_stage",
        "slowest_stage",
        "fastest_duration",
        "slowest_duration",
        "records_checked",
        "null_values",
        "duplicate_post_ids",
        "quality_status",
        "total_retries",
        "retry_information",
    ]

    return df[column_order]


def save_audit_record(
    record,
):
    """
    Append a pipeline audit record.

    The complete dataset is normalized before
    being written to Parquet so historical
    schema differences do not break the pipeline.
    """

    AUDIT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    new_record = pd.DataFrame(
        [record]
    )

    if AUDIT_FILE.exists():

        existing = pd.read_parquet(
            AUDIT_FILE
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
    # Normalize schema BEFORE writing.
    # ---------------------------------------------------------

    result = normalize_audit_dataframe(
        result
    )

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
