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
from src.validation.quality_metrics import (
    load_quality_metrics,
)


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


def run_stage(
    stage_name,
    script_path,
):
    """
    Execute one pipeline stage and return
    its duration.
    """

    start_time = time.perf_counter()

    project_root = (
        Path(__file__)
        .resolve()
        .parents[2]
    )

    environment = os.environ.copy()

    existing_python_path = (
        environment.get(
            "PYTHONPATH",
            "",
        )
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


def run_pipeline():
    """
    Execute all pipeline stages sequentially.

    Stops immediately when a stage fails.

    Every execution is recorded in the
    pipeline audit dataset.
    """

    run_id = generate_run_id()

    started_at = datetime.now(
        timezone.utc
    ).isoformat()

    stage_durations = {}

    try:

        # -----------------------------------------------------
        # Execute pipeline stages
        # -----------------------------------------------------

        for stage_name, script_path in STAGES:

            duration = run_stage(
                stage_name,
                script_path,
            )

            stage_durations[
                stage_name
            ] = duration

        # -----------------------------------------------------
        # Pipeline completion
        # -----------------------------------------------------

        finished_at = datetime.now(
            timezone.utc
        ).isoformat()

        total_duration = sum(
            stage_durations.values()
        )

        # -----------------------------------------------------
        # Stage metrics
        # -----------------------------------------------------

        stage_metrics = get_stage_metrics(
            stage_durations
        )

        # -----------------------------------------------------
        # Data-quality metrics
        # -----------------------------------------------------

        quality_metrics = (
            load_quality_metrics()
        )

        # -----------------------------------------------------
        # Pipeline result
        # -----------------------------------------------------

        result = {
            "status": "SUCCESS",
            "total_duration": total_duration,
            "total_stages": len(
                STAGES
            ),
            "successful_stages": len(
                stage_durations
            ),
            "failed_stage": None,
            "error": None,
            "stage_durations": (
                stage_durations
            ),
            "stage_metrics": (
                stage_metrics
            ),
            "quality_metrics": (
                quality_metrics
            ),
        }

        # -----------------------------------------------------
        # Create audit record
        # -----------------------------------------------------

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

        result["run_id"] = run_id

        return result

    except Exception as error:

        # -----------------------------------------------------
        # Failure information
        # -----------------------------------------------------

        finished_at = datetime.now(
            timezone.utc
        ).isoformat()

        total_duration = sum(
            stage_durations.values()
        )

        failed_stage = None

        if (
            len(stage_durations)
            < len(STAGES)
        ):

            failed_stage = STAGES[
                len(stage_durations)
            ][0]

        # -----------------------------------------------------
        # Stage metrics
        # -----------------------------------------------------

        stage_metrics = get_stage_metrics(
            stage_durations
        )

        # -----------------------------------------------------
        # Data-quality metrics
        # -----------------------------------------------------

        quality_metrics = (
            load_quality_metrics()
        )

        # -----------------------------------------------------
        # Failed pipeline result
        # -----------------------------------------------------

        result = {
            "status": "FAILED",
            "total_duration": total_duration,
            "total_stages": len(
                STAGES
            ),
            "successful_stages": len(
                stage_durations
            ),
            "failed_stage": failed_stage,
            "error": str(error),
            "stage_durations": (
                stage_durations
            ),
            "stage_metrics": (
                stage_metrics
            ),
            "quality_metrics": (
                quality_metrics
            ),
        }

        # -----------------------------------------------------
        # Create failed audit record
        # -----------------------------------------------------

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

        result["run_id"] = run_id

        return result


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

    # ---------------------------------------------------------
    # Stage metrics
    # ---------------------------------------------------------

    stage_metrics = result[
        "stage_metrics"
    ]

    if stage_metrics[
        "total_stages"
    ] > 0:

        print(
            f"Fastest stage: "
            f"{stage_metrics['fastest_stage']} "
            f"("
            f"{stage_metrics['fastest_duration']:.3f}s"
            f")"
        )

        print(
            f"Slowest stage: "
            f"{stage_metrics['slowest_stage']} "
            f"("
            f"{stage_metrics['slowest_duration']:.3f}s"
            f")"
        )

    # ---------------------------------------------------------
    # Quality metrics
    # ---------------------------------------------------------

    quality_metrics = result[
        "quality_metrics"
    ]

    if quality_metrics:

        print(
            "\nDATA QUALITY:"
        )

        print(
            f"Records checked: "
            f"{quality_metrics['records_checked']}"
        )

        print(
            f"Null values: "
            f"{quality_metrics['null_values']}"
        )

        print(
            f"Duplicate post IDs: "
            f"{quality_metrics['duplicate_post_ids']}"
        )

        print(
            f"Quality status: "
            f"{quality_metrics['quality_status']}"
        )

    print(
        "Pipeline orchestration completed."
    )


if __name__ == "__main__":
    main()
