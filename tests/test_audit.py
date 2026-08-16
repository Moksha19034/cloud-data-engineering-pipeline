import pandas as pd

from src.audit import pipeline_audit


def test_generate_run_id_is_unique():
    run_id_1 = pipeline_audit.generate_run_id()
    run_id_2 = pipeline_audit.generate_run_id()

    assert run_id_1 != run_id_2


def test_create_audit_record():
    record = pipeline_audit.create_audit_record(
        run_id="test-run-001",
        started_at="2026-08-12T10:00:00+00:00",
        finished_at="2026-08-12T10:00:05+00:00",
        status="SUCCESS",
        total_duration=5.0,
        total_stages=9,
        successful_stages=9,
    )

    assert record["run_id"] == "test-run-001"
    assert record["status"] == "SUCCESS"
    assert record["total_stages"] == 9
    assert record["successful_stages"] == 9
    assert record["failed_stage"] is None
    assert record["error"] is None


def test_save_audit_record_creates_file(tmp_path):
    audit_file = tmp_path / "pipeline_runs.parquet"

    pipeline_audit.AUDIT_FILE = audit_file

    record = pipeline_audit.create_audit_record(
        run_id="test-run-001",
        started_at="2026-08-12T10:00:00+00:00",
        finished_at="2026-08-12T10:00:05+00:00",
        status="SUCCESS",
        total_duration=5.0,
        total_stages=9,
        successful_stages=9,
    )

    pipeline_audit.save_audit_record(record)

    assert audit_file.exists()

    result = pd.read_parquet(audit_file)

    assert len(result) == 1
    assert result.loc[0, "run_id"] == "test-run-001"
    assert result.loc[0, "status"] == "SUCCESS"


def test_save_audit_record_appends_records(tmp_path):
    audit_file = tmp_path / "pipeline_runs.parquet"

    pipeline_audit.AUDIT_FILE = audit_file

    record_1 = pipeline_audit.create_audit_record(
        run_id="run-001",
        started_at="2026-08-12T10:00:00+00:00",
        finished_at="2026-08-12T10:00:05+00:00",
        status="SUCCESS",
        total_duration=5.0,
        total_stages=9,
        successful_stages=9,
    )

    record_2 = pipeline_audit.create_audit_record(
        run_id="run-002",
        started_at="2026-08-12T11:00:00+00:00",
        finished_at="2026-08-12T11:00:06+00:00",
        status="SUCCESS",
        total_duration=6.0,
        total_stages=9,
        successful_stages=9,
    )

    pipeline_audit.save_audit_record(record_1)
    pipeline_audit.save_audit_record(record_2)

    result = pd.read_parquet(audit_file)

    assert len(result) == 2
    assert result["run_id"].tolist() == [
        "run-001",
        "run-002",
    ]

def test_create_audit_record_includes_metrics():
    stage_metrics = {
        "total_stages": 9,
        "fastest_stage": "POST VALIDATION",
        "fastest_duration": 0.4,
        "slowest_stage": "POST INGESTION",
        "slowest_duration": 2.1,
    }

    quality_metrics = {
        "records_checked": 102,
        "null_values": 0,
        "duplicate_post_ids": 0,
        "quality_status": "PASSED",
    }

    record = pipeline_audit.create_audit_record(
        run_id="metrics-test-001",
        started_at="2026-08-16T14:00:00+00:00",
        finished_at="2026-08-16T14:00:05+00:00",
        status="SUCCESS",
        total_duration=5.0,
        total_stages=9,
        successful_stages=9,
        stage_metrics=stage_metrics,
        quality_metrics=quality_metrics,
    )

    assert record["fastest_stage"] == (
        "POST VALIDATION"
    )

    assert record["fastest_duration"] == 0.4

    assert record["slowest_stage"] == (
        "POST INGESTION"
    )

    assert record["slowest_duration"] == 2.1

    assert record["records_checked"] == 102

    assert record["null_values"] == 0

    assert record["duplicate_post_ids"] == 0

    assert record["quality_status"] == "PASSED"
