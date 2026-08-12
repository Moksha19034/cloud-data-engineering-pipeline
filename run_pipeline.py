import subprocess
import sys
from datetime import datetime, timezone


STAGES = [
    ("POST INGESTION", "src/ingestion/fetch_data.py"),
    ("USER INGESTION", "src/ingestion/fetch_users.py"),
    ("POST TRANSFORMATION", "src/transformation/transform_posts.py"),
    ("USER TRANSFORMATION", "src/transformation/transform_users.py"),
    ("POST VALIDATION", "src/validation/validate_posts.py"),
    ("RELATIONSHIP VALIDATION", "src/validation/validate_relationships.py"),
    ("SCHEMA VALIDATION", "src/validation/validate_schema.py"),
    ("ANALYTICS DATASET", "src/transformation/create_analytics_dataset.py"),
]


def run_stage(stage_name, script_path):
    print("\n" + "=" * 60)
    print(f"STARTING: {stage_name}")
    print("=" * 60)

    result = subprocess.run(
        [sys.executable, script_path],
        check=False,
    )

    if result.returncode != 0:
        print(f"\n❌ {stage_name} FAILED")
        raise RuntimeError(
            f"Pipeline stopped because {stage_name} failed."
        )

    print(f"\n✅ {stage_name} COMPLETED")


def main():
    start_time = datetime.now(timezone.utc)

    print("=" * 60)
    print("DATA ENGINEERING PIPELINE")
    print(f"Started: {start_time.isoformat()}")
    print("=" * 60)

    try:
        for stage_name, script_path in STAGES:
            run_stage(stage_name, script_path)

        end_time = datetime.now(timezone.utc)

        print("\n" + "=" * 60)
        print("🎉 PIPELINE COMPLETED SUCCESSFULLY")
        print(f"Finished: {end_time.isoformat()}")
        print("=" * 60)

    except Exception as error:
        end_time = datetime.now(timezone.utc)

        print("\n" + "=" * 60)
        print("❌ PIPELINE FAILED")
        print(f"Finished: {end_time.isoformat()}")
        print(f"Error: {error}")
        print("=" * 60)

        sys.exit(1)


if __name__ == "__main__":
    main()
