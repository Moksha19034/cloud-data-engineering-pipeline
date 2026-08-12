import subprocess
import sys
import logging
import time
from pathlib import Path
from datetime import datetime, timezone


LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "pipeline.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

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
    fastest_stage = min(stage_durations, key=stage_durations.get)
    slowest_stage = max(stage_durations, key=stage_durations.get)

    logger.info(
        f"Stage summary | "
        f"total_stages={len(stage_durations)} | "
        f"fastest={fastest_stage}:{stage_durations[fastest_stage]:.3f}s | "
        f"slowest={slowest_stage}:{stage_durations[slowest_stage]:.3f}s"
    )


def run_stage(stage_name, script_path):
    stage_start = time.perf_counter()

    print("\n" + "=" * 60)
    print(f"STARTING: {stage_name}")
    logger.info(f"Starting stage | stage={stage_name} | script={script_path}")
    print("=" * 60)

    result = subprocess.run(
        [sys.executable, script_path],
        check=False,
    )

    stage_duration = time.perf_counter() - stage_start

    if result.returncode != 0:
        print(f"\n❌ {stage_name} FAILED")
        logger.error(
            f"Stage failed | stage={stage_name} | script={script_path} | "
            f"exit_code={result.returncode} | duration={stage_duration:.3f}s"
        )
        raise RuntimeError(
            f"Pipeline stopped because {stage_name} failed "
            f"(exit code {result.returncode})."
        )

    print(f"\n✅ {stage_name} COMPLETED")
    logger.info(
        f"Stage completed | stage={stage_name} | "
        f"duration={stage_duration:.3f}s"
    )
    return stage_duration


def main():
    start_time = datetime.now(timezone.utc)

    print("=" * 60)
    print("DATA ENGINEERING PIPELINE")
    print(f"Started: {start_time.isoformat()}")
    logger.info("========== PIPELINE STARTED ==========")
    print("=" * 60)

    try:
        stage_durations = {}

        for stage_name, script_path in STAGES:
            duration = run_stage(stage_name, script_path)
            stage_durations[stage_name] = duration

        end_time = datetime.now(timezone.utc)
        total_duration = sum(stage_durations.values())

        logger.info(
            f"Pipeline metrics | stages={len(stage_durations)} | "
            f"successful_stages={len(stage_durations)} | "
            f"total_duration={total_duration:.3f}s"
        )

        log_stage_summary(stage_durations)


        print("\n" + "=" * 60)
        print("🎉 PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("========== PIPELINE COMPLETED SUCCESSFULLY ==========")
        print(f"Finished: {end_time.isoformat()}")
        print("=" * 60)

    except Exception as error:
        end_time = datetime.now(timezone.utc)
        print("\n" + "=" * 60)
        print("❌ PIPELINE FAILED")
        print(f"Finished: {end_time.isoformat()}")
        print(f"Error: {error}")
        logger.exception("Pipeline failed")
        print("=" * 60)

        sys.exit(1)


if __name__ == "__main__":
    main()
