import pandas as pd


def get_stage_baseline(df):
    """
    Calculate historical performance statistics
    for every pipeline stage.

    Returns one dictionary per stage containing:

    - executions
    - average duration
    - minimum duration
    - maximum duration
    - median duration
    - p95 duration
    - p99 duration
    """

    if df.empty:
        return []

    results = []

    for stage_name, stage_df in df.groupby(
        "stage_name"
    ):
        durations = pd.to_numeric(
            stage_df["duration"],
            errors="coerce",
        ).dropna()

        if durations.empty:
            continue

        results.append(
            {
                "stage_name": stage_name,
                "executions": int(
                    len(durations)
                ),
                "average_duration": round(
                    float(durations.mean()),
                    3,
                ),
                "minimum_duration": round(
                    float(durations.min()),
                    3,
                ),
                "maximum_duration": round(
                    float(durations.max()),
                    3,
                ),
                "median_duration": round(
                    float(durations.median()),
                    3,
                ),
                "p95_duration": round(
                    float(
                        durations.quantile(0.95)
                    ),
                    3,
                ),
                "p99_duration": round(
                    float(
                        durations.quantile(0.99)
                    ),
                    3,
                ),
            }
        )

    return results


def get_stage_baseline_for(
    df,
    stage_name,
):
    """
    Return the historical performance baseline
    for one specific stage.

    Returns None if the stage does not exist.
    """

    result = get_stage_baseline(df)

    for stage in result:
        if stage["stage_name"] == stage_name:
            return stage

    return None


def get_slowest_average_stage(df):
    """
    Return the stage with the highest historical
    average duration.
    """

    baseline = get_stage_baseline(df)

    if not baseline:
        return None

    return max(
        baseline,
        key=lambda item: item[
            "average_duration"
        ],
    )


def get_fastest_average_stage(df):
    """
    Return the stage with the lowest historical
    average duration.
    """

    baseline = get_stage_baseline(df)

    if not baseline:
        return None

    return min(
        baseline,
        key=lambda item: item[
            "average_duration"
        ],
    )


def get_highest_p95_stage(df):
    """
    Return the stage with the highest
    P95 duration.
    """

    baseline = get_stage_baseline(df)

    if not baseline:
        return None

    return max(
        baseline,
        key=lambda item: item[
            "p95_duration"
        ],
    )


def get_baseline_summary(df):
    """
    Return a complete performance baseline summary.
    """

    baseline = get_stage_baseline(df)

    if not baseline:
        return {
            "total_stage_executions": 0,
            "stages_analyzed": 0,
            "stage_baseline": [],
            "slowest_average_stage": None,
            "fastest_average_stage": None,
            "highest_p95_stage": None,
        }

    return {
        "total_stage_executions": int(
            len(df)
        ),
        "stages_analyzed": len(
            baseline
        ),
        "stage_baseline": baseline,
        "slowest_average_stage": (
            get_slowest_average_stage(df)
        ),
        "fastest_average_stage": (
            get_fastest_average_stage(df)
        ),
        "highest_p95_stage": (
            get_highest_p95_stage(df)
        ),
    }


def main():
    print(
        "Starting stage performance baseline..."
    )

    from src.audit.stage_audit import (
        load_stage_audit_records,
    )

    df = load_stage_audit_records()

    print(
        f"Total stage executions: {len(df)}"
    )

    result = get_baseline_summary(df)

    print()
    print("STAGE PERFORMANCE BASELINE:")
    print()

    for stage in result[
        "stage_baseline"
    ]:

        print(
            f"{stage['stage_name']}:"
        )

        print(
            f"  Executions: "
            f"{stage['executions']}"
        )

        print(
            f"  Average: "
            f"{stage['average_duration']:.3f}s"
        )

        print(
            f"  Minimum: "
            f"{stage['minimum_duration']:.3f}s"
        )

        print(
            f"  Maximum: "
            f"{stage['maximum_duration']:.3f}s"
        )

        print(
            f"  Median: "
            f"{stage['median_duration']:.3f}s"
        )

        print(
            f"  P95: "
            f"{stage['p95_duration']:.3f}s"
        )

        print(
            f"  P99: "
            f"{stage['p99_duration']:.3f}s"
        )

        print()

    slowest = result[
        "slowest_average_stage"
    ]

    fastest = result[
        "fastest_average_stage"
    ]

    highest_p95 = result[
        "highest_p95_stage"
    ]

    if slowest:

        print(
            "SLOWEST AVERAGE STAGE:"
        )

        print(
            f"Stage: "
            f"{slowest['stage_name']}"
        )

        print(
            f"Average: "
            f"{slowest['average_duration']:.3f}s"
        )

        print()

    if fastest:

        print(
            "FASTEST AVERAGE STAGE:"
        )

        print(
            f"Stage: "
            f"{fastest['stage_name']}"
        )

        print(
            f"Average: "
            f"{fastest['average_duration']:.3f}s"
        )

        print()

    if highest_p95:

        print(
            "HIGHEST P95 STAGE:"
        )

        print(
            f"Stage: "
            f"{highest_p95['stage_name']}"
        )

        print(
            f"P95: "
            f"{highest_p95['p95_duration']:.3f}s"
        )

    print()
    print(
        "Stage performance baseline completed."
    )


if __name__ == "__main__":
    main()
