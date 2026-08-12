from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


AUDIT_FILE = Path("data/audit/pipeline_runs.parquet")


def generate_run_id():
    timestamp = datetime.now(timezone.utc).strftime(
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
):
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
    }


def save_audit_record(record):
    AUDIT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    new_record = pd.DataFrame([record])

    if AUDIT_FILE.exists():
        existing = pd.read_parquet(AUDIT_FILE)

        result = pd.concat(
            [existing, new_record],
            ignore_index=True,
        )
    else:
        result = new_record

    result.to_parquet(
        AUDIT_FILE,
        index=False,
    )


def main():
    print("Pipeline audit module ready.")


if __name__ == "__main__":
    main()
