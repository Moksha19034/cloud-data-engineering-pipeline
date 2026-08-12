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
    assert "run-004" in message
    assert "POST VALIDATION" in message
    assert "Duplicate post_id" in message


def test_format_warning_alert():
    alert = pipeline_alert.create_alert(
        status="WARNING",
        run_id="run-005",
        failed_stage=None,
        error=None,
        total_duration=7.1,
    )

    message = pipeline_alert.format_alert(alert)

    assert "PIPELINE ALERT" in message
    assert "WARNING" in message
    assert "run-005" in message
    assert "7.1" in message
