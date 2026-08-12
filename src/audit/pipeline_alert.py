from pathlib import Path

import pandas as pd


ALERT_FILE = Path("data/audit/pipeline_alerts.parquet")


def create_alert(
    status,
    run_id,
    failed_stage=None,
    error=None,
    total_duration=None,
):
    """
    Create an alert when the pipeline requires attention.

    FAILED  -> CRITICAL alert
    WARNING -> WARNING alert
    HEALTHY -> no alert
    """

    if status == "HEALTHY":
        return None

    if status == "FAILED":
        severity = "CRITICAL"

    elif status == "WARNING":
        severity = "WARNING"

    else:
        raise ValueError(
            f"Unknown pipeline status: {status}"
        )

    return {
        "severity": severity,
        "status": status,
        "run_id": run_id,
        "failed_stage": failed_stage,
        "error": error,
        "total_duration": total_duration,
    }


def format_alert(alert):
    """
    Convert an alert dictionary into a readable message.
    """

    if alert is None:
        return None

    message = [
        "🚨 PIPELINE ALERT",
        "",
        f"Severity: {alert['severity']}",
        f"Status: {alert['status']}",
        f"Run ID: {alert['run_id']}",
    ]

    if alert["failed_stage"]:
        message.append(
            f"Failed Stage: {alert['failed_stage']}"
        )

    if alert["error"]:
        message.append(
            f"Error: {alert['error']}"
        )

    if alert["total_duration"] is not None:
        message.append(
            f"Duration: {alert['total_duration']}s"
        )

    return "\n".join(message)


def save_alert(alert):
    """
    Save an alert to the alert history dataset.

    Creates the file if it does not exist.
    Appends to the existing file if it does exist.
    """

    if alert is None:
        return

    ALERT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    new_alert = pd.DataFrame([alert])

    if ALERT_FILE.exists():
        existing = pd.read_parquet(ALERT_FILE)

        result = pd.concat(
            [existing, new_alert],
            ignore_index=True,
        )
    else:
        result = new_alert

    result.to_parquet(
        ALERT_FILE,
        index=False,
    )


def main():
    print("Pipeline alert module ready.")


if __name__ == "__main__":
    main()
