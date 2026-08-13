import time

from src.config.pipeline_config import get_pipeline_interval
from src.orchestration.orchestrator import (
    run_pipeline as orchestrate_pipeline,
)


def get_schedule_interval():
    """
    Return the configured pipeline interval in minutes.
    """

    return get_pipeline_interval()


def execute_pipeline():
    """
    Execute one pipeline run through the orchestration layer.
    """

    return orchestrate_pipeline()


def run_scheduler(
    interval_minutes=None,
    stop_on_failure=False,
    max_runs=None,
):
    """
    Continuously execute the pipeline at a fixed interval.

    Args:
        interval_minutes:
            Interval between pipeline executions.
            Uses configuration when omitted.

        stop_on_failure:
            Stop scheduling after the first failed run.

        max_runs:
            Optional maximum number of pipeline executions.
            Useful for testing and controlled execution.

    Returns:
        Dictionary containing execution statistics.
    """

    if interval_minutes is None:
        interval_minutes = get_schedule_interval()

    if interval_minutes <= 0:
        raise ValueError(
            "interval_minutes must be greater than zero."
        )

    runs = 0
    failures = 0

    while True:

        result = execute_pipeline()

        runs += 1

        if result["status"] == "FAILED":
            failures += 1

            if stop_on_failure:
                break

        if max_runs is not None and runs >= max_runs:
            break

        time.sleep(interval_minutes * 60)

    return {
        "runs": runs,
        "failures": failures,
    }


def main():
    """
    Start the production scheduler.
    """

    interval = get_schedule_interval()

    print(
        f"Pipeline scheduler started."
    )

    print(
        f"Pipeline will run every "
        f"{interval} minutes."
    )

    result = run_scheduler(
        interval_minutes=interval,
        stop_on_failure=False,
    )

    print(
        f"Scheduler stopped after "
        f"{result['runs']} runs."
    )


if __name__ == "__main__":
    main()
