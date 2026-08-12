import pandas as pd

from src.audit import pipeline_alert


def test_create_failed_alert():
    alert = pipeline_alert.create_alert(
        status="FAILED",
        run_id="run-001",
        failed_stage="SCHEMA VALIDATION",
        error="Schema validation failed",
        total_duration=4.5,
    )

    assert alert["severity"] == "CRITICAL"
    assert alert["status"] == "FAILED"
    assert alert["run_id"] == "run-001"
    assert alert["failed_stage"] == "SCHEMA VALIDATION"
    assert alert["error"] == "Schema validation failed"


def test_create_warning_alert():
    alert = pipeline_alert.create_alert(
        status="WARNING",
        run_id="run-002",
        failed_stage=None,
        error=None,
        total_duration=6.2,
    )

    assert alert["severity"] == "WARNING"
    assert alert["status"] == "WARNING"
    assert alert["run_id"] == "run-002"
    assert alert["total_duration"] == 6.2


def test_no_alert_for_healthy_pipeline():
    alert = pipeline_alert.create_alert(
        status="HEALTHY",
        run_id="run-003",
        failed_stage=None,
        error=None,
        total_duration=3.2,
    )

    assert alert is None


def test_format_failed_alert():
    alert = pipeline_alert.create_alert(
        status="FAILED",
        run_id="run-004",
        failed_stage="POST VALIDATION",
        error="Duplicate post_id",
        total_duration=4.8,
    )

    message = pipeline_alert.format_alert(alert)

    assert "PIPELINE ALERT" in message
    assert "CRITICAL" in message
    assert "FAILED" in message
    assert "run-004" in message
    assert "POST VALIDATION" in message
    assert "Duplicate post_id" in message


def test_format_warning_alert():
    alert = pipeline_alert.create_alert(
        status="WARNING",
        run_id="run-005",
        failed_stage=None,
        error=None,
        total_duration=6.2,
    )

    message = pipeline_alert.format_alert(alert)

    assert "PIPELINE ALERT" in message
    assert "WARNING" in message
    assert "run-005" in message
    assert "6.2s" in message


def test_save_alert_creates_file(tmp_path):
    alert_file = tmp_path / "pipeline_alerts.parquet"

    pipeline_alert.ALERT_FILE = alert_file

    alert = pipeline_alert.create_alert(
        status="FAILED",
        run_id="run-001",
        failed_stage="SCHEMA VALIDATION",
        error="Schema validation failed",
        total_duration=4.5,
    )

    pipeline_alert.save_alert(alert)

    assert alert_file.exists()

    result = pd.read_parquet(alert_file)

    assert len(result) == 1
    assert result.loc[0, "run_id"] == "run-001"
    assert result.loc[0, "severity"] == "CRITICAL"


def test_save_alert_appends_records(tmp_path):
    alert_file = tmp_path / "pipeline_alerts.parquet"

    pipeline_alert.ALERT_FILE = alert_file

    alert_1 = pipeline_alert.create_alert(
        status="FAILED",
        run_id="run-001",
        failed_stage="POST INGESTION",
        error="API failed",
        total_duration=3.0,
    )

    alert_2 = pipeline_alert.create_alert(
        status="WARNING",
        run_id="run-002",
        failed_stage=None,
        error=None,
        total_duration=6.0,
    )

    pipeline_alert.save_alert(alert_1)
    pipeline_alert.save_alert(alert_2)

    result = pd.read_parquet(alert_file)

    assert len(result) == 2
    assert result["run_id"].tolist() == [
        "run-001",
        "run-002",
    ]
