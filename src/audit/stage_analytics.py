from pathlib import Path

import pandas as pd


STAGE_AUDIT_FILE = Path(
    "data/audit/pipeline_stage_runs.parquet"
)


def get_total_stage_executions(df):
    """
    Return the total number of stage executions.
    """

    return len(df)


def get_stage_average_duration(df):
    """
    Return the average duration for each stage.

    Result:
        {
            "POST INGESTION": 0.85,
            "USER INGESTION": 0.52,
            ...
        }
    """

    if df.empty:
        return {}

    return (
        df.groupby("stage_name")["duration"]
        .mean()
        .round(3)
        .to_dict()
    )


def get_fastest_stage_execution(df):
    """
    Return the single fastest stage execution
    across all historical records.
    """

    if df.empty:
        return None

    row = df.loc[
        df["duration"].idxmin()
    ]

    return row.to_dict()


def get_slowest_stage_execution(df):
    """
    Return the single slowest stage execution
    across all historical records.
    """

    if df.empty:
        return None

    row = df.loc[
        df["duration"].idxmax()
    ]

    return row.to_dict()


def get_stage_summary(df):
    """
    Return historical performance statistics
    for every pipeline stage.
    """

    if df.empty:
        return {}

    summary = (
        df.groupby("stage_name")["duration"]
        .agg(
            executions="count",
            average_duration="mean",
            minimum_duration="min",
            maximum_duration="max",
        )
        .reset_index()
    )

    summary[
        "average_duration"
    ] = summary[
        "average_duration"
    ].round(3)

    summary[
        "minimum_duration"
    ] = summary[
        "minimum_duration"
    ].round(3)

    summary[
        "maximum_duration"
    ] = summary[
        "maximum_duration"
    ].round(3)

    return summary.to_dict(
        orient="records"
    )


def get_slowest_stage_by_average(df):
    """
    Return the stage with the highest
    historical average duration.
    """

    if df.empty:
        return None

    averages = (
        df.groupby("stage_name")["duration"]
        .mean()
    )

    stage_name = averages.idxmax()

    return {
        "stage_name": stage_name,
        "average_duration": round(
            float(averages[stage_name]),
            3,
        ),
    }


def get_fastest_stage_by_average(df):
    """
    Return the stage with the lowest
    historical average duration.
    """

    if df.empty:
        return None

    averages = (
        df.groupby("stage_name")["duration"]
        .mean()
    )

    stage_name = averages.idxmin()

    return {
        "stage_name": stage_name,
        "average_duration": round(
            float(averages[stage_name]),
            3,
        ),
    }


def load_stage_audit_data():
    """
    Load historical stage audit records.
    """

    if not STAGE_AUDIT_FILE.exists():
        raise FileNotFoundError(
            "Stage audit file not found: "
            f"{STAGE_AUDIT_FILE}"
        )

    return pd.read_parquet(
        STAGE_AUDIT_FILE
    )


def get_stage_analytics(df):
    """
    Return a complete stage performance
    analytics summary.
    """

    return {
        "total_stage_executions": (
            get_total_stage_executions(df)
        ),
        "stage_average_duration": (
            get_stage_average_duration(df)
        ),
        "fastest_stage_execution": (
            get_fastest_stage_execution(df)
        ),
        "slowest_stage_execution": (
            get_slowest_stage_execution(df)
        ),
        "slowest_stage_by_average": (
            get_slowest_stage_by_average(df)
        ),
        "fastest_stage_by_average": (
            get_fastest_stage_by_average(df)
        ),
        "stage_summary": (
            get_stage_summary(df)
        ),
    }


def main():
    print(
        "Starting stage analytics..."
    )

    df = load_stage_audit_data()

    analytics = get_stage_analytics(
        df
    )

    print(
        f"Total stage executions: "
        f"{analytics['total_stage_executions']}"
    )

    print()
    print(
        "AVERAGE DURATION BY STAGE:"
    )

    for (
        stage,
        duration,
    ) in analytics[
        "stage_average_duration"
    ].items():

        print(
            f"{stage}: "
            f"{duration:.3f}s"
        )

    fastest = analytics[
        "fastest_stage_execution"
    ]

    if fastest:
        print()
        print(
            "FASTEST STAGE EXECUTION:"
        )

        print(
            f"Stage: "
            f"{fastest['stage_name']}"
        )

        print(
            f"Run ID: "
            f"{fastest['run_id']}"
        )

        print(
            f"Duration: "
            f"{fastest['duration']:.3f}s"
        )

    slowest = analytics[
        "slowest_stage_execution"
    ]

    if slowest:
        print()
        print(
            "SLOWEST STAGE EXECUTION:"
        )

        print(
            f"Stage: "
            f"{slowest['stage_name']}"
        )

        print(
            f"Run ID: "
            f"{slowest['run_id']}"
        )

        print(
            f"Duration: "
            f"{slowest['duration']:.3f}s"
        )

    slowest_average = analytics[
        "slowest_stage_by_average"
    ]

    if slowest_average:
        print()
        print(
            "HISTORICALLY SLOWEST STAGE:"
        )

        print(
            f"Stage: "
            f"{slowest_average['stage_name']}"
        )

        print(
            f"Average duration: "
            f"{slowest_average['average_duration']:.3f}s"
        )

    fastest_average = analytics[
        "fastest_stage_by_average"
    ]

    if fastest_average:
        print()
        print(
            "HISTORICALLY FASTEST STAGE:"
        )

        print(
            f"Stage: "
            f"{fastest_average['stage_name']}"
        )

        print(
            f"Average duration: "
            f"{fastest_average['average_duration']:.3f}s"
        )

    print()
    print(
        "Stage analytics completed."
    )


if __name__ == "__main__":
    main()
