
import os
import subprocess
import sys
import time
from pathlib import Path

from src.audit.pipeline_metrics import get_stage_metrics
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


def run_stage(stage_name, script_path):
    """
    Execute one pipeline stage and return its duration.
    """

    start_time = time.perf_counter()

    project_root = Path(__file__).resolve().parents[2]

    environment = os.environ.copy()

    existing_python_path = environment.get(
        "PYTHONPATH",
        "",
    )

    if existing_python_path:
        environment["PYTHONPATH"] = (
            f"{project_root}{os.pathsep}"
            f"{existing_python_path}"
        )
    else:
        environment["PYTHONPATH"] = str(
            project_root
        )

    result = subprocess.run(
        [sys.executable, script_path],
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
            f"(exit code {result.returncode})"
        )

    return duration


def run_pipeline():
    """
    Execute all pipeline stages sequentially.

    Stops immediately when a stage fails.
    """

    stage_durations = {}

    try:
        for stage_name, script_path in STAGES:
            duration = run_stage(
                stage_name,
                script_path,
            )

            stage_durations[
                stage_name
            ] = duration

        total_duration = sum(
            stage_durations.values()
        )

        stage_metrics = get_stage_metrics(
            stage_durations
        )

        quality_metrics = (
            load_quality_metrics()
        )

        return {
            "status": "SUCCESS",
            "total_duration": total_duration,
            "total_stages": len(STAGES),
            "successful_stages": len(
                stage_durations
            ),
            "failed_stage": None,
            "stage_durations": stage_durations,
            "stage_metrics": stage_metrics,
            "quality_metrics": quality_metrics,
        }

    except Exception as error:
        total_duration = sum(
            stage_durations.values()
        )

        failed_stage = (
            STAGES[len(stage_durations)][0]
            if len(stage_durations) < len(STAGES)
            else None
        )

        stage_metrics = get_stage_metrics(
            stage_durations
        )

        quality_metrics = (
            load_quality_metrics()
        )

        return {
            "status": "FAILED",
            "total_duration": total_duration,
            "total_stages": len(STAGES),
            "successful_stages": len(
                stage_durations
            ),
            "failed_stage": failed_stage,
            "error": str(error),
            "stage_durations": stage_durations,
            "stage_metrics": stage_metrics,
            "quality_metrics": quality_metrics,
        }


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

    stage_metrics = result[
        "stage_metrics"
    ]

    if stage_metrics["total_stages"] > 0:
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

    quality_metrics = result[
        "quality_metrics"
    ]

    if quality_metrics:
        print("\nDATA QUALITY:")

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
