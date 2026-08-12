import subprocess
import sys
import time


STAGES = [
    ("POST INGESTION", "src/ingestion/fetch_data.py"),
    ("USER INGESTION", "src/ingestion/fetch_users.py"),
    ("POST TRANSFORMATION", "src/transformation/transform_posts.py"),
    ("USER TRANSFORMATION", "src/transformation/transform_users.py"),
    ("POST VALIDATION", "src/validation/validate_posts.py"),
    ("RELATIONSHIP VALIDATION", "src/validation/validate_relationships.py"),
    ("SCHEMA VALIDATION", "src/validation/validate_schema.py"),
    ("INCREMENTAL LOAD", "src/loading/upsert_posts.py"),
    ("ANALYTICS DATASET", "src/transformation/create_analytics_dataset.py"),
]


def run_stage(stage_name, script_path):
    """
    Execute one pipeline stage and return its duration.
    """

    start_time = time.perf_counter()

    result = subprocess.run(
        [sys.executable, script_path],
        check=False,
    )

    duration = time.perf_counter() - start_time

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

            stage_durations[stage_name] = duration

        total_duration = sum(
            stage_durations.values()
        )

        return {
            "status": "SUCCESS",
            "total_duration": total_duration,
            "total_stages": len(STAGES),
            "successful_stages": len(stage_durations),
            "failed_stage": None,
            "stage_durations": stage_durations,
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

        return {
            "status": "FAILED",
            "total_duration": total_duration,
            "total_stages": len(STAGES),
            "successful_stages": len(stage_durations),
            "failed_stage": failed_stage,
            "error": str(error),
            "stage_durations": stage_durations,
        }


def main():
    print("Starting pipeline orchestration...")

    result = run_pipeline()

    print(f"Pipeline status: {result['status']}")
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

    print("Pipeline orchestration completed.")


if __name__ == "__main__":
    main()
