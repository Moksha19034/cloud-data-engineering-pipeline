import time

from src.config.pipeline_config import get_pipeline_interval
from src.orchestration.orchestrator import (
    run_pipeline as orchestrate_pipeline,
)
from src.recovery.pipeline_recovery import (
    should_retry,
    should_skip_run,
)
from src.state.pipeline_state import load_state


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
    max_retries=3,
):
    """
    Continuously execute the pipeline at a fixed interval.

    Recovery behavior:
        - A previously successful run is skipped.
        - A failed run can be retried.
        - Retries stop after max_retries.
        - stop_on_failure stops immediately after a failure.

    Args:
        interval_minutes:
            Interval between pipeline executions.

        stop_on_failure:
            Stop scheduling immediately after a failed run.

        max_runs:
            Maximum number of pipeline executions.

        max_retries:
            Maximum number of retries after a failure.

    Returns:
        Dictionary containing execution statistics.
    """

    if interval_minutes is None:
        interval_minutes = get_schedule_interval()

    if interval_minutes <= 0:
        raise ValueError(
            "interval_minutes must be greater than zero."
        )

    if max_retries < 0:
        raise ValueError(
            "max_retries cannot be negative."
        )

    runs = 0
    failures = 0
    retries = 0
    skipped_runs = 0

    previous_state = load_state()

    # --------------------------------------------------
    # PREVIOUS RUN / IDEMPOTENCY CHECK
    # --------------------------------------------------

    if should_skip_run(previous_state):
        skipped_runs += 1

        return {
            "runs": runs,
            "failures": failures,
            "retries": retries,
            "skipped_runs": skipped_runs,
        }

    # --------------------------------------------------
    # MAIN SCHEDULER LOOP
    # --------------------------------------------------

    while True:

        retry_count = 0

        while True:

            result = execute_pipeline()

            runs += 1

            # ------------------------------------------
            # SUCCESS
            # ------------------------------------------

            if result["status"] == "SUCCESS":
                break

            # ------------------------------------------
            # FAILURE
            # ------------------------------------------

            failures += 1

            # stop_on_failure has priority over retries
            if stop_on_failure:
                break

            # ------------------------------------------
            # FAILURE RECOVERY
            # ------------------------------------------

            current_state = {
                "last_status": "FAILED",
            }

            if not should_retry(
                current_state,
                retry_count,
                max_retries,
            ):
                break

            retry_count += 1
            retries += 1

        # --------------------------------------------------
        # STOP AFTER FAILURE
        # --------------------------------------------------

        if result["status"] == "FAILED":
            if stop_on_failure:
                break

            # If retries were exhausted, stop this scheduler
            # execution rather than immediately starting another
            # scheduled run from the same failure.
            if retry_count >= max_retries:
                break

        # --------------------------------------------------
        # MAX RUNS
        # --------------------------------------------------

        if max_runs is not None and runs >= max_runs:
            break

        # --------------------------------------------------
        # WAIT FOR NEXT SCHEDULED RUN
        # --------------------------------------------------

        time.sleep(
            interval_minutes * 60
        )

        # --------------------------------------------------
        # REFRESH PREVIOUS STATE
        # --------------------------------------------------

        previous_state = load_state()

        if should_skip_run(previous_state):
            skipped_runs += 1
            continue

    return {
        "runs": runs,
        "failures": failures,
        "retries": retries,
        "skipped_runs": skipped_runs,
    }


def main():
    """
    Start the production scheduler.
    """

    interval = get_schedule_interval()

    print(
        "Pipeline scheduler started."
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

    print(
        f"Failures: {result['failures']}"
    )

    print(
        f"Retries: {result['retries']}"
    )

    print(
        f"Skipped runs: "
        f"{result['skipped_runs']}"
    )


if __name__ == "__main__":
    main()
