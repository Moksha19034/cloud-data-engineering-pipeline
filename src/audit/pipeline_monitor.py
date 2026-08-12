from pathlib import Path

import pandas as pd


AUDIT_FILE = Path("data/audit/pipeline_runs.parquet")


def load_audit_records():
    """
    Load pipeline audit records from the audit dataset.
    """
    if not AUDIT_FILE.exists():
        raise FileNotFoundError(
            f"Audit file not found: {AUDIT_FILE}"
        )

    return pd.read_parquet(AUDIT_FILE)


def get_latest_run(df):
    """
    Return the most recent pipeline run.
    """
    df = df.copy()

    df["started_at"] = pd.to_datetime(
        df["started_at"],
        utc=True,
    )

    latest_index = df["started_at"].idxmax()

    return df.loc[latest_index]


def get_failed_runs(df):
    """
    Return all pipeline runs that failed.
    """
    return df[df["status"] == "FAILED"].copy()


def get_slow_runs(df, duration_threshold):
    """
    Return pipeline runs whose duration exceeds
    the specified threshold.
    """
    return df[
        df["total_duration"] > duration_threshold
    ].copy()



def check_pipeline_health(df, duration_threshold):
    """
    Determine pipeline health.

    Returns:
        FAILED if any pipeline run failed.
        WARNING if any pipeline run is slow.
        HEALTHY otherwise.
    """
    failed_runs = get_failed_runs(df)

    if not failed_runs.empty:
        return "FAILED"

    slow_runs = get_slow_runs(
        df,
        duration_threshold,
    )

    if not slow_runs.empty:
        return "WARNING"

    return "HEALTHY"

def main():
    print("Starting pipeline monitoring...")

    df = load_audit_records()

    duration_threshold = 5.0

    latest_run = get_latest_run(df)

    failed_runs = get_failed_runs(df)

    slow_runs = get_slow_runs(
        df,
        duration_threshold,
    )

    health = check_pipeline_health(
        df,
        duration_threshold,
    )

    print(f"Total pipeline runs: {len(df)}")
    print(f"Failed runs: {len(failed_runs)}")
    print(f"Slow runs: {len(slow_runs)}")
    print(f"Pipeline health: {health}")

    print("\nLATEST RUN:")
    print(
        latest_run[
            [
                "run_id",
                "status",
                "started_at",
                "total_duration",
            ]
        ].to_string()
    )

    if not failed_runs.empty:
        print("\nFAILED RUNS:")

        print(
            failed_runs[
                [
                    "run_id",
                    "failed_stage",
                    "error",
                ]
            ].to_string(index=False)
        )

    if not slow_runs.empty:
        print("\nSLOW RUNS:")

        print(
            slow_runs[
                [
                    "run_id",
                    "status",
                    "total_duration",
                ]
            ].to_string(index=False)
        )

    print("\nPipeline monitoring completed.")


if __name__ == "__main__":
    main()
