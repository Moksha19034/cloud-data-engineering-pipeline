import pandas as pd

from src.audit import pipeline_metrics


def sample_runs():
    return pd.DataFrame(
        [
            {
                "run_id": "run-001",
                "status": "SUCCESS",
                "total_duration": 3.0,
                "total_stages": 9,
                "successful_stages": 9,
            },
            {
                "run_id": "run-002",
                "status": "SUCCESS",
                "total_duration": 5.0,
                "total_stages": 9,
                "successful_stages": 9,
            },
            {
                "run_id": "run-003",
                "status": "FAILED",
                "total_duration": 4.0,
                "total_stages": 9,
                "successful_stages": 5,
            },
        ]
    )


def test_get_total_runs():
    df = sample_runs()

    assert pipeline_metrics.get_total_runs(df) == 3


def test_get_successful_runs():
    df = sample_runs()

    assert pipeline_metrics.get_successful_runs(df) == 2


def test_get_failed_runs():
    df = sample_runs()

    assert pipeline_metrics.get_failed_runs(df) == 1


def test_get_success_rate():
    df = sample_runs()

    assert pipeline_metrics.get_success_rate(df) == 66.67


def test_get_average_duration():
    df = sample_runs()

    assert pipeline_metrics.get_average_duration(df) == 4.0


def test_get_fastest_run():
    df = sample_runs()

    result = pipeline_metrics.get_fastest_run(df)

    assert result["run_id"] == "run-001"
    assert result["total_duration"] == 3.0


def test_get_slowest_run():
    df = sample_runs()

    result = pipeline_metrics.get_slowest_run(df)

    assert result["run_id"] == "run-002"
    assert result["total_duration"] == 5.0


def test_get_metrics_empty_dataframe():
    df = pd.DataFrame()

    metrics = pipeline_metrics.get_pipeline_metrics(df)

    assert metrics["total_runs"] == 0
    assert metrics["successful_runs"] == 0
    assert metrics["failed_runs"] == 0
    assert metrics["success_rate"] == 0.0
    assert metrics["average_duration"] == 0.0
