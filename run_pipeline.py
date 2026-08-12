import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from src.audit.pipeline_audit import (
    generate_run_id,
    create_audit_record,
    save_audit_record,
)

from src.audit.pipeline_alert import (
    create_alert,
    format_alert,
    save_alert,
)

from src.orchestration.orchestrator import (
    run_pipeline as orchestrate_pipeline,
)


LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "pipeline.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# Kept here for compatibility with the existing pipeline tests.
# The actual main pipeline execution is now handled by the orchestrator.
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


def log_stage_summary(stage_durations):
    """
    Log the fastest and slowest pipeline stages.
    """

    if not stage_durations:
        return

    fastest_stage = min(
        stage_durations,
        key=stage_durations.get,
    )

    slowest_stage = max(
        stage_durations,
        key=stage_durations.get,
    )

    logger.info(
        f"Stage summary | "
        f"total_stages={len(stage_durations)} | "
        f"fastest={fastest_stage}:"
        f"{stage_durations[fastest_stage]:.3f}s | "
        f"slowest={slowest_stage}:"
        f"{stage_durations[slowest_stage]:.3f}s"
    )


def run_stage(stage_name, script_path):
    """
    Execute a single pipeline stage.

    This function is retained for compatibility with the
    existing unit tests. The main pipeline now uses the
    orchestration layer.
    """

    stage_start = time.perf_counter()

    print("\n" + "=" * 60)
    print(f"STARTING: {stage_name}")

    logger.info(
        f"Starting stage | "
        f"stage={stage_name} | "
        f"script={script_path}"
    )

    print("=" * 60)

    result = subprocess.run(
        [sys.executable, script_path],
        check=False,
    )

    stage_duration = time.perf_counter() - stage_start

    if result.returncode != 0:
        print(f"\n❌ {stage_name} FAILED")

        logger.error(
            f"Stage failed | "
            f"stage={stage_name} | "
            f"script={script_path} | "
            f"exit_code={result.returncode} | "
            f"duration={stage_duration:.3f}s"
        )

        raise RuntimeError(
            f"Pipeline stopped because {stage_name} failed "
            f"(exit code {result.returncode})."
        )

    print(f"\n✅ {stage_name} COMPLETED")

    logger.info(
        f"Stage completed | "
        f"stage={stage_name} | "
        f"duration={stage_duration:.3f}s"
    )

    return stage_duration


def main():
    """
    Main pipeline entry point.

    The orchestration layer executes the pipeline stages.
    This function handles:
        - Run identification
        - Logging
        - Audit records
        - Alerts
        - Final pipeline reporting
    """

    run_id = generate_run_id()
    start_time = datetime.now(timezone.utc)

    print("=" * 60)
    print("DATA ENGINEERING PIPELINE")
    print(f"Run ID: {run_id}")
    print(f"Started: {start_time.isoformat()}")
    print("=" * 60)

    logger.info(
        f"========== PIPELINE STARTED | "
        f"run_id={run_id} =========="
    )

    try:
        # --------------------------------------------------
        # ORCHESTRATION
        # --------------------------------------------------

        pipeline_result = orchestrate_pipeline()

        stage_durations = pipeline_result.get(
            "stage_durations",
            {},
        )

        total_duration = pipeline_result.get(
            "total_duration",
            sum(stage_durations.values()),
        )

        total_stages = pipeline_result.get(
            "total_stages",
            len(STAGES),
        )

        successful_stages = pipeline_result.get(
            "successful_stages",
            len(stage_durations),
        )

        failed_stage = pipeline_result.get(
            "failed_stage"
        )

        log_stage_summary(stage_durations)

        # --------------------------------------------------
        # SUCCESS
        # --------------------------------------------------

        if pipeline_result["status"] == "SUCCESS":

            end_time = datetime.now(timezone.utc)

            logger.info(
                f"Pipeline metrics | "
                f"run_id={run_id} | "
                f"stages={total_stages} | "
                f"successful_stages={successful_stages} | "
                f"total_duration={total_duration:.3f}s"
            )

            audit_record = create_audit_record(
                run_id=run_id,
                started_at=start_time,
                finished_at=end_time,
                status="SUCCESS",
                total_duration=total_duration,
                total_stages=total_stages,
                successful_stages=successful_stages,
            )

            save_audit_record(audit_record)

            # A healthy pipeline should not generate an alert.
            alert = create_alert(
                status="HEALTHY",
                run_id=run_id,
                failed_stage=None,
                error=None,
                total_duration=total_duration,
            )

            if alert is not None:
                save_alert(alert)
                print("\n" + format_alert(alert))

            print("\n" + "=" * 60)
            print("🎉 PIPELINE COMPLETED SUCCESSFULLY")
            print(f"Run ID: {run_id}")
            print(f"Duration: {total_duration:.3f}s")
            print(
                f"Stages: "
                f"{successful_stages}/{total_stages}"
            )
            print(f"Finished: {end_time.isoformat()}")
            print("=" * 60)

            logger.info(
                f"========== PIPELINE COMPLETED SUCCESSFULLY | "
                f"run_id={run_id} =========="
            )

            return

        # --------------------------------------------------
        # FAILURE
        # --------------------------------------------------

        end_time = datetime.now(timezone.utc)

        error_message = pipeline_result.get(
            "error",
            "Pipeline orchestration failed.",
        )

        logger.error(
            f"Pipeline failed | "
            f"run_id={run_id} | "
            f"failed_stage={failed_stage} | "
            f"error={error_message}"
        )

        audit_record = create_audit_record(
            run_id=run_id,
            started_at=start_time,
            finished_at=end_time,
            status="FAILED",
            total_duration=total_duration,
            total_stages=total_stages,
            successful_stages=successful_stages,
            failed_stage=failed_stage,
            error=error_message,
        )

        save_audit_record(audit_record)

        # --------------------------------------------------
        # CREATE AND SAVE CRITICAL ALERT
        # --------------------------------------------------

        alert = create_alert(
            status="FAILED",
            run_id=run_id,
            failed_stage=failed_stage,
            error=error_message,
            total_duration=total_duration,
        )

        if alert is not None:
            save_alert(alert)

            print("\n" + "=" * 60)
            print(format_alert(alert))
            print("=" * 60)

        print("\n" + "=" * 60)
        print("❌ PIPELINE FAILED")
        print(f"Run ID: {run_id}")
        print(f"Failed stage: {failed_stage}")
        print(f"Finished: {end_time.isoformat()}")
        print(f"Error: {error_message}")
        print("=" * 60)

        sys.exit(1)

    except Exception as error:
        # --------------------------------------------------
        # UNEXPECTED FAILURE
        # --------------------------------------------------

        end_time = datetime.now(timezone.utc)

        logger.exception(
            f"Unexpected pipeline failure | "
            f"run_id={run_id}"
        )

        # If the orchestration layer itself fails before
        # returning a result, create an audit record here.
        audit_record = create_audit_record(
            run_id=run_id,
            started_at=start_time,
            finished_at=end_time,
            status="FAILED",
            total_duration=0.0,
            total_stages=len(STAGES),
            successful_stages=0,
            failed_stage=None,
            error=str(error),
        )

        save_audit_record(audit_record)

        alert = create_alert(
            status="FAILED",
            run_id=run_id,
            failed_stage=None,
            error=str(error),
            total_duration=0.0,
        )

        if alert is not None:
            save_alert(alert)

            print("\n" + "=" * 60)
            print(format_alert(alert))
            print("=" * 60)

        print("\n" + "=" * 60)
        print("❌ PIPELINE FAILED")
        print(f"Run ID: {run_id}")
        print(f"Finished: {end_time.isoformat()}")
        print(f"Error: {error}")
        print("=" * 60)

        sys.exit(1)


if __name__ == "__main__":
    main()
