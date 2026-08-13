def get_total_runs(df):
    """
    Return the total number of pipeline runs.
    """

    return len(df)


def get_successful_runs(df):
    """
    Return the number of successful pipeline runs.
    """

    if df.empty:
        return 0

    return int(
        (df["status"] == "SUCCESS").sum()
    )


def get_failed_runs(df):
    """
    Return the number of failed pipeline runs.
    """

    if df.empty:
        return 0

    return int(
        (df["status"] == "FAILED").sum()
    )


def get_success_rate(df):
    """
    Return pipeline success rate as a percentage.
    """

    total_runs = get_total_runs(df)

    if total_runs == 0:
        return 0.0

    successful_runs = get_successful_runs(df)

    return round(
        (successful_runs / total_runs) * 100,
        2,
    )


def get_average_duration(df):
    """
    Return the average pipeline duration in seconds.
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


def get_pipeline_metrics(df):
    """
    Return a summary of pipeline performance.
    """

    return {
        "total_runs": get_total_runs(df),
        "successful_runs": get_successful_runs(df),
        "failed_runs": get_failed_runs(df),
        "success_rate": get_success_rate(df),
        "average_duration": get_average_duration(df),
    }

def get_fastest_stage(stage_durations):
    """
    Return the fastest pipeline stage.
    """

    if not stage_durations:
        return None

    stage = min(
        stage_durations,
        key=stage_durations.get,
    )

    return {
        "stage": stage,
        "duration": stage_durations[stage],
    }


def get_slowest_stage(stage_durations):
    """
    Return the slowest pipeline stage.
    """

    if not stage_durations:
        return None

    stage = max(
        stage_durations,
        key=stage_durations.get,
    )

    return {
        "stage": stage,
        "duration": stage_durations[stage],
    }


def get_average_stage_duration(stage_durations):
    """
    Return the average duration of pipeline stages.
    """

    if not stage_durations:
        return 0.0

    return sum(
        stage_durations.values()
    ) / len(stage_durations)


def get_slow_stages(
    stage_durations,
    threshold,
):
    """
    Return stages whose duration exceeds the threshold.
    """

    if not stage_durations:
        return {}

    return {
        stage: duration
        for stage, duration in stage_durations.items()
        if duration > threshold
    }


def get_stage_metrics(stage_durations):
    """
    Return a summary of stage-level performance.
    """

    if not stage_durations:
        return {
            "total_stages": 0,
            "fastest_stage": None,
            "slowest_stage": None,
            "fastest_duration": 0.0,
            "slowest_duration": 0.0,
        }

    fastest = get_fastest_stage(
        stage_durations
    )

    slowest = get_slowest_stage(
        stage_durations
    )

    return {
        "total_stages": len(stage_durations),
        "fastest_stage": fastest["stage"],
        "slowest_stage": slowest["stage"],
        "fastest_duration": fastest["duration"],
        "slowest_duration": slowest["duration"],
    }
