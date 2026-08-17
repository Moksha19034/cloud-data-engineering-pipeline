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
        "fastest_stage": "POST VALIDATION",
        "slowest_stage": "POST INGESTION",
        "fastest_duration": 0.4,
        "slowest_duration": 1.2,
    }

    quality_metrics = {
        "records_checked": 102,
        "null_values": 0,
        "duplicate_post_ids": 0,
        "quality_status": "PASSED",
    }

    retry_information = {
        "POST INGESTION": {
            "attempts": 2,
            "retries": 1,
        }
    }

    record = pipeline_audit.create_audit_record(
        run_id="metrics-run",
        started_at="2026-08-12T10:00:00+00:00",
        finished_at="2026-08-12T10:00:05+00:00",
        status="SUCCESS",
        total_duration=5.0,
        total_stages=9,
        successful_stages=9,
        stage_metrics=stage_metrics,
        quality_metrics=quality_metrics,
        retry_information=retry_information,
    )

    assert record["fastest_stage"] == "POST VALIDATION"
    assert record["slowest_stage"] == "POST INGESTION"

    assert record["fastest_duration"] == 0.4
    assert record["slowest_duration"] == 1.2

    assert record["records_checked"] == 102
    assert record["null_values"] == 0
    assert record["duplicate_post_ids"] == 0
    assert record["quality_status"] == "PASSED"

    assert record["total_retries"] == 1


def test_get_total_retries():

    retry_information = {
        "POST INGESTION": {
            "attempts": 3,
            "retries": 2,
        },
        "USER INGESTION": {
            "attempts": 1,
            "retries": 0,
        },
    }

    result = pipeline_audit.get_total_retries(
        retry_information
    )

    assert result == 2


def test_get_total_retries_empty():

    result = pipeline_audit.get_total_retries({})

    assert result == 0


def test_create_audit_record_includes_retry_metrics():

    retry_information = {
        "POST INGESTION": {
            "attempts": 3,
            "retries": 2,
        }
    }

    record = pipeline_audit.create_audit_record(
        run_id="test-run-retry",
        started_at="2026-08-17T10:00:00+00:00",
        finished_at="2026-08-17T10:00:05+00:00",
        status="SUCCESS",
        total_duration=5.0,
        total_stages=9,
        successful_stages=9,
        retry_information=retry_information,
    )

    assert record["total_retries"] == 2

    assert (
        "POST INGESTION"
        in record["retry_information"]
    )


def test_save_audit_record_handles_existing_timestamp_schema(
    tmp_path,
):
    audit_file = (
        tmp_path
        / "pipeline_runs.parquet"
    )

    pipeline_audit.AUDIT_FILE = audit_file

    existing = pd.DataFrame(
        [
            {
                "run_id": "old-run",
                "started_at": pd.Timestamp(
                    "2026-08-17T04:00:00+00:00"
                ),
                "finished_at": pd.Timestamp(
                    "2026-08-17T04:00:05+00:00"
                ),
                "status": "SUCCESS",
                "total_duration": 5.0,
                "total_stages": 9,
                "successful_stages": 9,
            }
        ]
    )

    existing.to_parquet(
        audit_file,
        index=False,
    )

    new_record = (
        pipeline_audit
        .create_audit_record(
            run_id="new-run",
            started_at=(
                "2026-08-17T05:00:00+00:00"
            ),
            finished_at=(
                "2026-08-17T05:00:05+00:00"
            ),
            status="SUCCESS",
            total_duration=5.0,
            total_stages=9,
            successful_stages=9,
            retry_information={
                "POST INGESTION": {
                    "attempts": 1,
                    "retries": 0,
                }
            },
        )
    )

    pipeline_audit.save_audit_record(
        new_record
    )

    result = pd.read_parquet(
        audit_file
    )

    assert len(result) == 2

    assert (
        result.iloc[0]["run_id"]
        == "old-run"
    )

    assert (
        result.iloc[1]["run_id"]
        == "new-run"
    )

    assert isinstance(
        result["started_at"].dtype,
        pd.DatetimeTZDtype,
    )

    assert (
        result.iloc[1]["total_retries"]
        == 0
    )
