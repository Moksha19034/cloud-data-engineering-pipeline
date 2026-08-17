import json
from datetime import datetime, timezone
from pathlib import Path


ALERT_FILE = Path(
    "data/audit/pipeline_alerts.json"
)


def create_alert(
    alert_type,
    severity,
    run_id,
    message,
    stage=None,
    details=None,
):
    """
    Create a structured pipeline alert.
    """

    timestamp = datetime.now(
        timezone.utc
    )

    return {
        "alert_id": timestamp.strftime(
            "%Y%m%d_%H%M%S_%f"
        ),
        "timestamp": timestamp.isoformat(),
        "alert_type": alert_type,
        "severity": severity,
        "run_id": run_id,
        "stage": stage,
        "message": message,
        "details": details or {},
    }


def save_alert(alert):
    """
    Persist an alert to the historical
    alert JSON file.
    """

    ALERT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    alerts = []

    if ALERT_FILE.exists():
        with open(
            ALERT_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            alerts = json.load(file)

    alerts.append(alert)

    with open(
        ALERT_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            alerts,
            file,
            indent=2,
        )


def load_alerts():
    """
    Load all historical alerts.
    """

    if not ALERT_FILE.exists():
        return []

    with open(
        ALERT_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def get_alert_count():
    """
    Return the total number of
    historical alerts.
    """

    return len(
        load_alerts()
    )


def alert_pipeline_failure(
    run_id,
    failed_stage,
    error,
):
    """
    Create and persist a critical
    pipeline failure alert.
    """

    alert = create_alert(
        alert_type="PIPELINE_FAILURE",
        severity="CRITICAL",
        run_id=run_id,
        stage=failed_stage,
        message=(
            f"Pipeline failed during "
            f"{failed_stage}"
        ),
        details={
            "error": str(error),
        },
    )

    save_alert(alert)

    return alert


def alert_data_quality_failure(
    run_id,
    quality_metrics,
):
    """
    Create and persist a high-severity
    data quality alert.
    """

    alert = create_alert(
        alert_type="DATA_QUALITY_FAILURE",
        severity="HIGH",
        run_id=run_id,
        message=(
            "Data quality validation failed"
        ),
        details=quality_metrics,
    )

    save_alert(alert)

    return alert


def alert_sla_violation(
    run_id,
    stage,
    duration,
    sla,
):
    """
    Create and persist an SLA violation
    alert.
    """

    alert = create_alert(
        alert_type="SLA_VIOLATION",
        severity="WARNING",
        run_id=run_id,
        stage=stage,
        message=(
            f"{stage} exceeded its SLA"
        ),
        details={
            "duration": duration,
            "sla": sla,
            "exceeded_by": (
                duration - sla
            ),
        },
    )

    save_alert(alert)

    return alert


def alert_retry_exhausted(
    run_id,
    stage,
    attempts,
    error,
):
    """
    Create and persist a critical alert
    when retries are exhausted.
    """

    alert = create_alert(
        alert_type="RETRY_EXHAUSTED",
        severity="CRITICAL",
        run_id=run_id,
        stage=stage,
        message=(
            f"Retry attempts exhausted "
            f"for {stage}"
        ),
        details={
            "attempts": attempts,
            "error": str(error),
        },
    )

    save_alert(alert)

    return alert


def main():
    print(
        "Pipeline alerting module ready."
    )


if __name__ == "__main__":
    main()
