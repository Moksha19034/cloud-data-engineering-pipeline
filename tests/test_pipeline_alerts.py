from src.alerting import pipeline_alerts


def test_create_alert():

    alert = pipeline_alerts.create_alert(
        alert_type="TEST",
        severity="WARNING",
        run_id="run-001",
        message="Test alert",
    )

    assert alert["alert_type"] == "TEST"
    assert alert["severity"] == "WARNING"
    assert alert["run_id"] == "run-001"
    assert alert["message"] == "Test alert"


def test_save_alert(
    tmp_path,
    monkeypatch,
):

    alert_file = (
        tmp_path
        / "pipeline_alerts.json"
    )

    monkeypatch.setattr(
        pipeline_alerts,
        "ALERT_FILE",
        alert_file,
    )

    alert = pipeline_alerts.create_alert(
        alert_type="TEST",
        severity="INFO",
        run_id="run-001",
        message="Test",
    )

    pipeline_alerts.save_alert(
        alert
    )

    assert alert_file.exists()

    alerts = (
        pipeline_alerts.load_alerts()
    )

    assert len(alerts) == 1
    assert alerts[0]["run_id"] == "run-001"


def test_alert_pipeline_failure(
    tmp_path,
    monkeypatch,
):

    monkeypatch.setattr(
        pipeline_alerts,
        "ALERT_FILE",
        tmp_path / "alerts.json",
    )

    alert = (
        pipeline_alerts
        .alert_pipeline_failure(
            run_id="run-001",
            failed_stage="POST INGESTION",
            error="Connection failed",
        )
    )

    assert (
        alert["alert_type"]
        == "PIPELINE_FAILURE"
    )

    assert (
        alert["severity"]
        == "CRITICAL"
    )

    assert (
        alert["stage"]
        == "POST INGESTION"
    )


def test_alert_data_quality_failure(
    tmp_path,
    monkeypatch,
):

    monkeypatch.setattr(
        pipeline_alerts,
        "ALERT_FILE",
        tmp_path / "alerts.json",
    )

    metrics = {
        "records_checked": 100,
        "null_values": 5,
        "duplicate_post_ids": 0,
    }

    alert = (
        pipeline_alerts
        .alert_data_quality_failure(
            run_id="run-001",
            quality_metrics=metrics,
        )
    )

    assert (
        alert["alert_type"]
        == "DATA_QUALITY_FAILURE"
    )

    assert (
        alert["severity"]
        == "HIGH"
    )

    assert (
        alert["details"]["null_values"]
        == 5
    )


def test_alert_sla_violation(
    tmp_path,
    monkeypatch,
):

    monkeypatch.setattr(
        pipeline_alerts,
        "ALERT_FILE",
        tmp_path / "alerts.json",
    )

    alert = (
        pipeline_alerts
        .alert_sla_violation(
            run_id="run-001",
            stage="POST TRANSFORMATION",
            duration=3.5,
            sla=2.0,
        )
    )

    assert (
        alert["alert_type"]
        == "SLA_VIOLATION"
    )

    assert (
        alert["details"]["duration"]
        == 3.5
    )

    assert (
        alert["details"]["sla"]
        == 2.0
    )


def test_alert_retry_exhausted(
    tmp_path,
    monkeypatch,
):

    monkeypatch.setattr(
        pipeline_alerts,
        "ALERT_FILE",
        tmp_path / "alerts.json",
    )

    alert = (
        pipeline_alerts
        .alert_retry_exhausted(
            run_id="run-001",
            stage="POST INGESTION",
            attempts=3,
            error="Timeout",
        )
    )

    assert (
        alert["alert_type"]
        == "RETRY_EXHAUSTED"
    )

    assert (
        alert["severity"]
        == "CRITICAL"
    )

    assert (
        alert["details"]["attempts"]
        == 3
    )


def test_alert_count(
    tmp_path,
    monkeypatch,
):

    monkeypatch.setattr(
        pipeline_alerts,
        "ALERT_FILE",
        tmp_path / "alerts.json",
    )

    alert = pipeline_alerts.create_alert(
        alert_type="TEST",
        severity="INFO",
        run_id="run-001",
        message="Test",
    )

    pipeline_alerts.save_alert(
        alert
    )

    assert (
        pipeline_alerts.get_alert_count()
        == 1
    )
