import pandas as pd

from src.audit import stage_baseline


def sample_dataframe():
    return pd.DataFrame(
        {
            "run_id": [
                "run-001",
                "run-001",
                "run-001",
                "run-002",
                "run-002",
                "run-002",
            ],
            "stage_name": [
                "POST INGESTION",
                "POST INGESTION",
                "POST INGESTION",
                "USER INGESTION",
                "USER INGESTION",
                "USER INGESTION",
            ],
            "duration": [
                1.0,
                2.0,
                3.0,
                0.5,
                1.0,
                1.5,
            ],
        }
    )


def test_get_stage_baseline():

    df = sample_dataframe()

    result = stage_baseline.get_stage_baseline(
        df
    )

    assert len(result) == 2

    post_ingestion = next(
        item
        for item in result
        if item["stage_name"]
        == "POST INGESTION"
    )

    assert (
        post_ingestion["executions"]
        == 3
    )

    assert (
        post_ingestion[
            "average_duration"
        ]
        == 2.0
    )

    assert (
        post_ingestion[
            "minimum_duration"
        ]
        == 1.0
    )

    assert (
        post_ingestion[
            "maximum_duration"
        ]
        == 3.0
    )

    assert (
        post_ingestion[
            "median_duration"
        ]
        == 2.0
    )


def test_get_stage_baseline_for():

    df = sample_dataframe()

    result = (
        stage_baseline.get_stage_baseline_for(
            df,
            "POST INGESTION",
        )
    )

    assert result is not None

    assert (
        result["average_duration"]
        == 2.0
    )


def test_get_stage_baseline_for_missing_stage():

    df = sample_dataframe()

    result = (
        stage_baseline.get_stage_baseline_for(
            df,
            "UNKNOWN STAGE",
        )
    )

    assert result is None


def test_get_slowest_average_stage():

    df = sample_dataframe()

    result = (
        stage_baseline
        .get_slowest_average_stage(df)
    )

    assert (
        result["stage_name"]
        == "POST INGESTION"
    )

    assert (
        result["average_duration"]
        == 2.0
    )


def test_get_fastest_average_stage():

    df = sample_dataframe()

    result = (
        stage_baseline
        .get_fastest_average_stage(df)
    )

    assert (
        result["stage_name"]
        == "USER INGESTION"
    )

    assert (
        result["average_duration"]
        == 1.0
    )


def test_get_highest_p95_stage():

    df = sample_dataframe()

    result = (
        stage_baseline
        .get_highest_p95_stage(df)
    )

    assert result is not None


def test_get_baseline_summary():

    df = sample_dataframe()

    result = (
        stage_baseline
        .get_baseline_summary(df)
    )

    assert (
        result[
            "total_stage_executions"
        ]
        == 6
    )

    assert (
        result["stages_analyzed"]
        == 2
    )

    assert len(
        result["stage_baseline"]
    ) == 2

    assert (
        result[
            "slowest_average_stage"
        ]["stage_name"]
        == "POST INGESTION"
    )


def test_empty_dataframe():

    df = pd.DataFrame(
        columns=[
            "run_id",
            "stage_name",
            "duration",
        ]
    )

    result = (
        stage_baseline
        .get_baseline_summary(df)
    )

    assert (
        result[
            "total_stage_executions"
        ]
        == 0
    )

    assert (
        result["stages_analyzed"]
        == 0
    )

    assert (
        result[
            "slowest_average_stage"
        ]
        is None
    )

    assert (
        result[
            "fastest_average_stage"
        ]
        is None
    )

    assert (
        result[
            "highest_p95_stage"
        ]
        is None
    )
