from pathlib import Path

import pandas as pd


STAGE_AUDIT_FILE = Path(
    "data/audit/pipeline_stage_runs.parquet"
)


def create_stage_audit_records(
    run_id,
    stage_durations,
):
    """
    Convert stage duration information into
    one audit record per pipeline stage.
    """

    records = []

    for stage_name, duration in (
        stage_durations.items()
    ):
        records.append(
            {
                "run_id": run_id,
                "stage_name": stage_name,
                "duration": float(duration),
            }
        )

    return records


def save_stage_audit_records(
    records,
):
    """
    Append stage-level audit records to
    the historical stage audit dataset.
    """

    if not records:
        return

    STAGE_AUDIT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    new_records = pd.DataFrame(
        records
    )

    if STAGE_AUDIT_FILE.exists():

        existing = pd.read_parquet(
            STAGE_AUDIT_FILE
        )

        result = pd.concat(
            [
                existing,
                new_records,
            ],
            ignore_index=True,
        )

    else:

        result = new_records

    result["run_id"] = (
        result["run_id"].astype("string")
    )

    result["stage_name"] = (
        result["stage_name"].astype("string")
    )

    result["duration"] = pd.to_numeric(
        result["duration"],
        errors="coerce",
    )

    result.to_parquet(
        STAGE_AUDIT_FILE,
        index=False,
    )


def load_stage_audit_records():
    """
    Load historical stage-level audit records.
    """

    if not STAGE_AUDIT_FILE.exists():
        raise FileNotFoundError(
            "Stage audit file not found: "
            f"{STAGE_AUDIT_FILE}"
        )

    return pd.read_parquet(
        STAGE_AUDIT_FILE
    )


def main():
    print(
        "Pipeline stage audit module ready."
    )


if __name__ == "__main__":
    main()
