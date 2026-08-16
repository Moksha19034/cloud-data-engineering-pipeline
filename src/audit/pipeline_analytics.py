from pathlib import Path

import pandas as pd


AUDIT_FILE = Path(
    "data/audit/pipeline_runs.parquet"
)


def load_audit_data():
    """
    Load historical pipeline audit records.
    """

    if not AUDIT_FILE.exists():
        raise FileNotFoundError(
            f"Audit file not found: {AUDIT_FILE}"
        )

    return pd.read_parquet(
        AUDIT_FILE
    )


def get_total_runs(df):
    """
    Return total number of pipeline runs.
    """

    return len(df)


def get_successful_runs(df):
    """
    Return number of successful pipeline runs.
    """

    if df.empty:
        return 0

    return int(
        (
            df["status"] == "SUCCESS"
        ).sum()
    )


def get_failed_runs(df):
    """
    Return number of failed pipeline runs.
    """

    if df.empty:
        return 0

    return int(
        (
            df["status"] == "FAILED"
        ).sum()
    )


def get_success_rate(df):
    """
    Return pipeline success rate
    as a percentage.
    """

    total_runs = get_total_runs(
        df
    )

    if total_runs == 0:
        return 0.0

    successful_runs = (
        get_successful_runs(df)
    )

    return round(
        (
            successful_runs
            / total_runs
        )
        * 100,
        2,
    )


def get_average_duration(df):
    """
    Return average pipeline duration
    in seconds.
    """

    if df.empty:
        return 0.0

    return float(
        df["total_duration"].mean()
    )


def get_fastest_run(df):
    """
    Return the fastest pipeline run.
    """

    if df.empty:
        return None

    row = df.loc[
        df["total_duration"].idxmin()
    ]

    return row.to_dict()


def get_slowest_run(df):
    """
    Return the slowest pipeline run.
    """

    if df.empty:
        return None

    row = df.loc[
        df["total_duration"].idxmax()
    ]

    return row.to_dict()


def get_pipeline_summary(df):
    """
    Return a complete historical
    pipeline performance summary.
    """

    return {
        "total_runs": get_total_runs(
            df
        ),
        "successful_runs": (
            get_successful_runs(df)
        ),
        "failed_runs": (
            get_failed_runs(df)
        ),
        "success_rate": (
            get_success_rate(df)
        ),
        "average_duration": (
            get_average_duration(df)
        ),
    }


def main():
    print(
        "Starting pipeline analytics..."
    )

    df = load_audit_data()

    summary = get_pipeline_summary(
        df
    )

    print(
        f"Total runs: "
        f"{summary['total_runs']}"
    )

    print(
        f"Successful runs: "
        f"{summary['successful_runs']}"
    )

    print(
        f"Failed runs: "
        f"{summary['failed_runs']}"
    )

    print(
        f"Success rate: "
        f"{summary['success_rate']}%"
    )

    print(
        f"Average duration: "
        f"{summary['average_duration']:.3f}s"
    )

    fastest = get_fastest_run(
        df
    )

    if fastest:

        print(
            "\nFASTEST RUN:"
        )

        print(
            f"Run ID: "
            f"{fastest['run_id']}"
        )

        print(
            f"Duration: "
            f"{fastest['total_duration']:.3f}s"
        )

    slowest = get_slowest_run(
        df
    )

    if slowest:

        print(
            "\nSLOWEST RUN:"
        )

        print(
            f"Run ID: "
            f"{slowest['run_id']}"
        )

        print(
            f"Duration: "
            f"{slowest['total_duration']:.3f}s"
        )

    print(
        "\nPipeline analytics completed."
    )


if __name__ == "__main__":
    main()
