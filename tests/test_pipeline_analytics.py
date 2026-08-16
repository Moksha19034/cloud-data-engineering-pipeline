import pandas as pd

from src.audit import pipeline_analytics


def sample_audit_dataframe():
    return pd.DataFrame(
        {
            "run_id": [
                "run-001",
                "run-002",
                "run-003",
                "run-004",
            ],
            "status": [
                "SUCCESS",
                "SUCCESS",
                "FAILED",
                "SUCCESS",
            ],
            "total_duration": [
                5.0,
                10.0,
                20.0,
                15.0,
            ],
        }
    )


def test_get_total_runs():
    df = sample_audit_dataframe()

    assert (
        pipeline_analytics.get_total_runs(df)
        == 4
    )


def test_get_successful_runs():
    df = sample_audit_dataframe()

    assert (
        pipeline_analytics.get_successful_runs(df)
        == 3
    )


def test_get_failed_runs():
    df = sample_audit_dataframe()

    assert (
        pipeline_analytics.get_failed_runs(df)
        == 1
    )


def test_get_success_rate():
    df = sample_audit_dataframe()

    assert (
        pipeline_analytics.get_success_rate(df)
        == 75.0
    )


def test_get_average_duration():
    df = sample_audit_dataframe()

    assert (
        pipeline_analytics.get_average_duration(df)
        == 12.5
    )


def test_get_fastest_run():
    df = sample_audit_dataframe()

    result = (
        pipeline_analytics.get_fastest_run(df)
    )

    assert result["run_id"] == "run-001"
    assert result["total_duration"] == 5.0


def test_get_slowest_run():
    df = sample_audit_dataframe()

    result = (
        pipeline_analytics.get_slowest_run(df)
    )

    assert result["run_id"] == "run-003"
    assert result["total_duration"] == 20.0


def test_get_pipeline_summary():
    df = sample_audit_dataframe()

    result = (
        pipeline_analytics.get_pipeline_summary(
            df
        )
    )

    assert result["total_runs"] == 4
    assert result["successful_runs"] == 3
    assert result["failed_runs"] == 1
    assert result["success_rate"] == 75.0
    assert result["average_duration"] == 12.5


def test_empty_dataframe():
    df = pd.DataFrame(
        columns=[
            "run_id",
            "status",
            "total_duration",
        ]
    )

    assert (
        pipeline_analytics.get_total_runs(df)
        == 0
    )

    assert (
        pipeline_analytics.get_successful_runs(df)
        == 0
    )

    assert (
        pipeline_analytics.get_failed_runs(df)
        == 0
    )

    assert (
        pipeline_analytics.get_success_rate(df)
        == 0.0
    )

    assert (
        pipeline_analytics.get_average_duration(df)
        == 0.0
    )

    assert (
        pipeline_analytics.get_fastest_run(df)
        is None
    )

    assert (
        pipeline_analytics.get_slowest_run(df)
        is None
    )
