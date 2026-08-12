import pandas as pd
import pytest

from src.audit import pipeline_monitor


def make_audit_data():
    return pd.DataFrame(
        [
            {
                "run_id": "run-001",
                "status": "SUCCESS",
                "total_duration": 3.0,
                "failed_stage": None,
                "error": None,
            },
            {
                "run_id": "run-002",
                "status": "SUCCESS",
                "total_duration": 4.0,
                "failed_stage": None,
                "error": None,
            },
            {
                "run_id": "run-003",
                "status": "FAILED",
                "total_duration": 2.0,
                "failed_stage": "SCHEMA VALIDATION",
                "error": "Schema validation failed",
            },
            {
                "run_id": "run-004",
                "status": "SUCCESS",
                "total_duration": 7.0,
                "failed_stage": None,
                "error": None,
            },
        ]
    )


def test_get_failed_runs():
    df = make_audit_data()

    result = pipeline_monitor.get_failed_runs(df)

    assert len(result) == 1
    assert result.iloc[0]["run_id"] == "run-003"


def test_get_slow_runs():
    df = make_audit_data()

    result = pipeline_monitor.get_slow_runs(
        df,
        duration_threshold=5.0,
    )

    assert len(result) == 1
    assert result.iloc[0]["run_id"] == "run-004"


def test_pipeline_health_is_failed():
    df = make_audit_data()

    result = pipeline_monitor.check_pipeline_health(
        df,
        duration_threshold=5.0,
    )

    assert result == "FAILED"


def test_pipeline_health_is_warning():
    df = pd.DataFrame(
        [
            {
                "run_id": "run-001",
                "status": "SUCCESS",
                "total_duration": 7.0,
                "failed_stage": None,
                "error": None,
            }
        ]
    )

    result = pipeline_monitor.check_pipeline_health(
        df,
        duration_threshold=5.0,
    )

    assert result == "WARNING"


def test_pipeline_health_is_healthy():
    df = pd.DataFrame(
        [
            {
                "run_id": "run-001",
                "status": "SUCCESS",
                "total_duration": 3.0,
                "failed_stage": None,
                "error": None,
            }
        ]
    )

    result = pipeline_monitor.check_pipeline_health(
        df,
        duration_threshold=5.0,
    )

    assert result == "HEALTHY"


def test_load_audit_records_missing_file(tmp_path):
    pipeline_monitor.AUDIT_FILE = (
        tmp_path / "missing.parquet"
    )

    with pytest.raises(
        FileNotFoundError,
        match="Audit file not found",
    ):
        pipeline_monitor.load_audit_records()

def test_get_latest_run():
    df = pd.DataFrame(
        [
            {
                "run_id": "run-001",
                "started_at": "2026-08-12T10:00:00+00:00",
                "status": "SUCCESS",
                "total_duration": 3.0,
            },
            {
                "run_id": "run-002",
                "started_at": "2026-08-12T11:00:00+00:00",
                "status": "SUCCESS",
                "total_duration": 4.0,
            },
        ]
    )

    result = pipeline_monitor.get_latest_run(df)

    assert result["run_id"] == "run-002"

def test_pipeline_health_uses_latest_run():
    df = pd.DataFrame(
        [
            {
                "run_id": "run-001",
                "started_at": "2026-08-12T10:00:00+00:00",
                "status": "SUCCESS",
                "total_duration": 8.0,
            },
            {
                "run_id": "run-002",
                "started_at": "2026-08-12T11:00:00+00:00",
                "status": "SUCCESS",
                "total_duration": 3.0,
            },
        ]
    )

    latest_run = pipeline_monitor.get_latest_run(df)

    assert latest_run["run_id"] == "run-002"
    assert latest_run["total_duration"] == 3.0
