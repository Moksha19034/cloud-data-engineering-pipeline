import pandas as pd

from src.audit import stage_analytics


def sample_dataframe():
    return pd.DataFrame(
        {
            "run_id": [
                "run-001",
                "run-001",
                "run-002",
                "run-002",
                "run-003",
            ],
            "stage_name": [
                "POST INGESTION",
                "USER INGESTION",
                "POST INGESTION",
                "USER INGESTION",
                "POST INGESTION",
            ],
            "duration": [
                1.0,
                0.5,
                2.0,
                0.7,
                1.5,
            ],
        }
    )


def test_get_total_stage_executions():

    df = sample_dataframe()

    result = (
        stage_analytics
        .get_total_stage_executions(df)
    )

    assert result == 5


def test_get_stage_average_duration():

    df = sample_dataframe()

    result = (
        stage_analytics
        .get_stage_average_duration(df)
    )

    assert result[
        "POST INGESTION"
    ] == 1.5

    assert result[
        "USER INGESTION"
    ] == 0.6


def test_get_fastest_stage_execution():

    df = sample_dataframe()

    result = (
        stage_analytics
        .get_fastest_stage_execution(df)
    )

    assert result[
        "stage_name"
    ] == "USER INGESTION"

    assert result[
        "duration"
    ] == 0.5


def test_get_slowest_stage_execution():

    df = sample_dataframe()

    result = (
        stage_analytics
        .get_slowest_stage_execution(df)
    )

    assert result[
        "stage_name"
    ] == "POST INGESTION"

    assert result[
        "duration"
    ] == 2.0


def test_get_slowest_stage_by_average():

    df = sample_dataframe()

    result = (
        stage_analytics
        .get_slowest_stage_by_average(df)
    )

    assert result[
        "stage_name"
    ] == "POST INGESTION"

    assert result[
        "average_duration"
    ] == 1.5


def test_get_fastest_stage_by_average():

    df = sample_dataframe()

    result = (
        stage_analytics
        .get_fastest_stage_by_average(df)
    )

    assert result[
        "stage_name"
    ] == "USER INGESTION"

    assert result[
        "average_duration"
    ] == 0.6


def test_get_stage_summary():

    df = sample_dataframe()

    result = (
        stage_analytics
        .get_stage_summary(df)
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
        == 1.5
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
        == 2.0
    )


def test_get_stage_analytics():

    df = sample_dataframe()

    result = (
        stage_analytics
        .get_stage_analytics(df)
    )

    assert (
        result[
            "total_stage_executions"
        ]
        == 5
    )

    assert (
        result[
            "slowest_stage_by_average"
        ]["stage_name"]
        == "POST INGESTION"
    )

    assert (
        result[
            "fastest_stage_by_average"
        ]["stage_name"]
        == "USER INGESTION"
    )

    assert len(
        result["stage_summary"]
    ) == 2


def test_empty_dataframe():

    df = pd.DataFrame(
        columns=[
            "run_id",
            "stage_name",
            "duration",
        ]
    )

    assert (
        stage_analytics
        .get_total_stage_executions(df)
        == 0
    )

    assert (
        stage_analytics
        .get_stage_average_duration(df)
        == {}
    )

    assert (
        stage_analytics
        .get_fastest_stage_execution(df)
        is None
    )

    assert (
        stage_analytics
        .get_slowest_stage_execution(df)
        is None
    )

    assert (
        stage_analytics
        .get_stage_summary(df)
        == {}
    )

    assert (
        stage_analytics
        .get_slowest_stage_by_average(df)
        is None
    )

    assert (
        stage_analytics
        .get_fastest_stage_by_average(df)
        is None
    )
