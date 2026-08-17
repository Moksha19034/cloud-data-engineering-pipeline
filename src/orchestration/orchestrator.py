import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from src.audit.pipeline_audit import (
    create_audit_record,
    generate_run_id,
    save_audit_record,
)

from src.audit.pipeline_metrics import (
    get_stage_metrics,
)

from src.audit.stage_audit import (
    create_stage_audit_records,
    save_stage_audit_records,
)

from src.alerting.pipeline_alerts import (
    alert_pipeline_failure,
    alert_retry_exhausted,
)

from src.orchestration.failure_classifier import (
    is_retryable,
)

from src.orchestration.retry import (
    execute_with_retry,
)

from src.validation.quality_metrics import (
    load_quality_metrics,
)


# =========================================================
# PIPELINE STAGES
# =========================================================

STAGES = [
    (
        "POST INGESTION",
        "src/ingestion/fetch_data.py",
    ),
    (
        "USER INGESTION",
        "src/ingestion/fetch_users.py",
    ),
    (
        "POST TRANSFORMATION",
        "src/transformation/transform_posts.py",
    ),
    (
        "USER TRANSFORMATION",
        "src/transformation/transform_users.py",
    ),
    (
        "POST VALIDATION",
        "src/validation/validate_posts.py",
    ),
    (
        "RELATIONSHIP VALIDATION",
        "src/validation/validate_relationships.py",
    ),
    (
        "SCHEMA VALIDATION",
        "src/validation/validate_schema.py",
    ),
    (
        "INCREMENTAL LOAD",
        "src/loading/upsert_posts.py",
    ),
    (
        "ANALYTICS DATASET",
        "src/transformation/create_analytics_dataset.py",
    ),
]


# =========================================================
# RETRY CONFIGURATION
# =========================================================

MAX_RETRIES = 3

INITIAL_RETRY_DELAY = 1.0


# Only external-system stages are retried.

RETRYABLE_STAGES = {
    "POST INGESTION",
    "USER INGESTION",
}


# =========================================================
# RUN ONE PIPELINE STAGE
# =========================================================

def run_stage(
    stage_name,
    script_path,
):
    """
    Execute one pipeline stage.

    Returns:
        Duration in seconds.

    Raises:
        RuntimeError:
            When the stage exits with a non-zero code.
    """

    start_time = time.perf_counter()

    project_root = (
        Path(__file__)
        .resolve()
        .parents[2]
    )

    environment = os.environ.copy()

    existing_python_path = environment.get(
        "PYTHONPATH",
        "",
    )

    if existing_python_path:

        environment["PYTHONPATH"] = (
            f"{project_root}"
            f"{os.pathsep}"
            f"{existing_python_path}"
        )

    else:

        environment["PYTHONPATH"] = (
            str(project_root)
        )

    result = subprocess.run(
        [
            sys.executable,
            script_path,
        ],
        check=False,
        cwd=project_root,
        env=environment,
    )

    duration = (
        time.perf_counter()
        - start_time
    )

    if result.returncode != 0:

        raise RuntimeError(
            f"{stage_name} failed "
            f"(exit code "
            f"{result.returncode})"
        )

    return duration


# =========================================================
# RUN STAGE WITH RETRY
# =========================================================

def run_stage_with_retry(
    stage_name,
    script_path,
):
    """
    Execute a pipeline stage with retry support.

    Only configured transient stages
    are retried.

    Returns:
        Dictionary containing:

        status
        duration
        attempts
        retries
        error
    """

    should_retry = (
        stage_name in RETRYABLE_STAGES
    )

    def execute_stage():

        try:

            return run_stage(
                stage_name,
                script_path,
            )

        except RuntimeError as error:

            if should_retry:

                raise ConnectionError(
                    str(error)
                ) from error

            raise

    retry_result = execute_with_retry(
        function=execute_stage,
        max_retries=MAX_RETRIES,
        initial_delay=INITIAL_RETRY_DELAY,
        is_retryable=is_retryable,
    )

    return retry_result


# =========================================================
# SAVE STAGE AUDIT
# =========================================================

def save_stage_audit(
    run_id,
    stage_durations,
):
    """
    Convert stage durations into audit records
    and persist them.
    """

    records = create_stage_audit_records(
        run_id=run_id,
        stage_durations=stage_durations,
    )

    save_stage_audit_records(
        records
    )


# =========================================================
# RUN COMPLETE PIPELINE
# =========================================================

def run_pipeline():
    """
    Execute all pipeline stages sequentially.

    Retry transient ingestion failures.

    Stop when a stage fails.

    Record:
        - pipeline audit
        - stage audit
        - retry information
        - quality metrics
        - alerts
    """

    run_id = generate_run_id()

    started_at = datetime.now(
        timezone.utc
    ).isoformat()

    stage_durations = {}

    retry_information = {}

    try:

        # =================================================
        # EXECUTE PIPELINE
        # =================================================

        for stage_name, script_path in STAGES:

            retry_result = run_stage_with_retry(
                stage_name,
                script_path,
            )

            retry_information[
                stage_name
            ] = {
                "attempts": retry_result[
                    "attempts"
                ],
                "retries": retry_result[
                    "retries"
                ],
            }

            # ---------------------------------------------
            # RETRY EXHAUSTED
            # ---------------------------------------------

            if (
                retry_result["status"]
                != "SUCCESS"
            ):

                error = retry_result[
                    "error"
                ]

                if stage_name in RETRYABLE_STAGES:

                    alert_retry_exhausted(
                        run_id=run_id,
                        stage=stage_name,
                        attempts=retry_result[
                            "attempts"
                        ],
                        error=error,
                    )

                raise error

            duration = retry_result[
                "result"
            ]

            stage_durations[
                stage_name
            ] = duration

        # =================================================
        # PIPELINE SUCCESS
        # =================================================

        finished_at = datetime.now(
            timezone.utc
        ).isoformat()

        total_duration = sum(
            stage_durations.values()
        )

        # =================================================
        # STAGE METRICS
        # =================================================

        stage_metrics = get_stage_metrics(
            stage_durations
        )

        # =================================================
        # DATA QUALITY
        # =================================================

        quality_metrics = (
            load_quality_metrics()
        )

        # =================================================
        # SUCCESS RESULT
        # =================================================

        result = {
            "status": "SUCCESS",

            "total_duration":
                total_duration,

            "total_stages":
                len(STAGES),

            "successful_stages":
                len(stage_durations),

            "failed_stage":
                None,

            "error":
                None,

            "stage_durations":
                stage_durations,

            "stage_metrics":
                stage_metrics,

            "quality_metrics":
                quality_metrics,

            "retry_information":
                retry_information,
        }

        # =================================================
        # PIPELINE AUDIT
        # =================================================

        audit_record = create_audit_record(
            run_id=run_id,
            started_at=started_at,
            finished_at=finished_at,
            status=result["status"],
            total_duration=result[
                "total_duration"
            ],
            total_stages=result[
                "total_stages"
            ],
            successful_stages=result[
                "successful_stages"
            ],
            failed_stage=result[
                "failed_stage"
            ],
            error=result["error"],
            stage_metrics=stage_metrics,
            quality_metrics=quality_metrics,
        )

        save_audit_record(
            audit_record
        )

        # =================================================
        # STAGE AUDIT
        # =================================================

        save_stage_audit(
            run_id=run_id,
            stage_durations=stage_durations,
        )

        result["run_id"] = run_id

        return result

    # =====================================================
    # PIPELINE FAILURE
    # =====================================================

    except Exception as error:

        finished_at = datetime.now(
            timezone.utc
        ).isoformat()

        total_duration = sum(
            stage_durations.values()
        )

        # ---------------------------------------------
        # DETERMINE FAILED STAGE
        # ---------------------------------------------

        failed_stage = None

        if (
            len(stage_durations)
            < len(STAGES)
        ):

            failed_stage = STAGES[
                len(stage_durations)
            ][0]

        # ---------------------------------------------
        # CREATE PIPELINE FAILURE ALERT
        # ---------------------------------------------

        if failed_stage:

            alert_pipeline_failure(
                run_id=run_id,
                failed_stage=failed_stage,
                error=error,
            )

        # ---------------------------------------------
        # STAGE METRICS
        # ---------------------------------------------

        stage_metrics = get_stage_metrics(
            stage_durations
        )

        # ---------------------------------------------
        # QUALITY METRICS
        # ---------------------------------------------

        quality_metrics = (
            load_quality_metrics()
        )

        # ---------------------------------------------
        # FAILED RESULT
        # ---------------------------------------------

        result = {
            "status": "FAILED",

            "total_duration":
                total_duration,

            "total_stages":
                len(STAGES),

            "successful_stages":
                len(stage_durations),

            "failed_stage":
                failed_stage,

            "error":
                str(error),

            "stage_durations":
                stage_durations,

            "stage_metrics":
                stage_metrics,

            "quality_metrics":
                quality_metrics,

            "retry_information":
                retry_information,
        }

        # ---------------------------------------------
        # FAILED PIPELINE AUDIT
        # ---------------------------------------------

        audit_record = create_audit_record(
            run_id=run_id,
            started_at=started_at,
            finished_at=finished_at,
            status=result["status"],
            total_duration=result[
                "total_duration"
            ],
            total_stages=result[
                "total_stages"
            ],
            successful_stages=result[
                "successful_stages"
            ],
            failed_stage=result[
                "failed_stage"
            ],
            error=result["error"],
            stage_metrics=stage_metrics,
            quality_metrics=quality_metrics,
        )

        save_audit_record(
            audit_record
        )

        # ---------------------------------------------
        # SAVE COMPLETED STAGES
        # ---------------------------------------------

        save_stage_audit(
            run_id=run_id,
            stage_durations=stage_durations,
        )

        result["run_id"] = run_id

        return result


# =========================================================
# MAIN
# =========================================================

def main():

    print(
        "Starting pipeline orchestration..."
    )

    result = run_pipeline()

    print(
        f"Pipeline status: "
        f"{result['status']}"
    )

    print(
        f"Run ID: "
        f"{result['run_id']}"
    )

    print(
        f"Stages: "
        f"{result['successful_stages']}/"
        f"{result['total_stages']}"
    )

    print(
        f"Duration: "
        f"{result['total_duration']:.3f}s"
    )

    if result["failed_stage"]:

        print(
            f"Failed stage: "
            f"{result['failed_stage']}"
        )

    if result["error"]:

        print(
            f"Error: "
            f"{result['error']}"
        )

    # =====================================================
    # STAGE METRICS
    # =====================================================

    stage_metrics = result.get(
        "stage_metrics",
        {},
    )

    if stage_metrics.get(
        "fastest_stage"
    ):

        print(
            f"Fastest stage: "
            f"{stage_metrics['fastest_stage']} "
            f"("
            f"{stage_metrics['fastest_duration']:.3f}s"
            f")"
        )

    if stage_metrics.get(
        "slowest_stage"
    ):

        print(
            f"Slowest stage: "
            f"{stage_metrics['slowest_stage']} "
            f"("
            f"{stage_metrics['slowest_duration']:.3f}s"
            f")"
        )

    # =====================================================
    # RETRY INFORMATION
    # =====================================================

    retry_information = result.get(
        "retry_information",
        {},
    )

    total_retries = sum(
        information.get(
            "retries",
            0,
        )
        for information
        in retry_information.values()
    )

    print()

    print(
        "RETRY INFORMATION:"
    )

    print(
        f"Total retries: "
        f"{total_retries}"
    )

    for (
        stage_name,
        information,
    ) in retry_information.items():

        if information["retries"] > 0:

            print(
                f"{stage_name}: "
                f"{information['retries']} "
                f"retry(s), "
                f"{information['attempts']} "
                f"attempt(s)"
            )

    # =====================================================
    # DATA QUALITY
    # =====================================================

    quality_metrics = result.get(
        "quality_metrics",
        {},
    )

    if quality_metrics:

        print()

        print(
            "DATA QUALITY:"
        )

        print(
            "Records checked: "
            f"{quality_metrics.get('records_checked', 0)}"
        )

        print(
            "Null values: "
            f"{quality_metrics.get('null_values', 0)}"
        )

        print(
            "Duplicate post IDs: "
            f"{quality_metrics.get('duplicate_post_ids', 0)}"
        )

        print(
            "Quality status: "
            f"{quality_metrics.get('quality_status', 'UNKNOWN')}"
        )

    print(
        "Pipeline orchestration completed."
    )


if __name__ == "__main__":
    main()
