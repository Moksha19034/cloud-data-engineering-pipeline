import pandas as pd

from src.audit import stage_audit


def test_create_stage_audit_records():

    stage_durations = {
        "POST INGESTION": 1.5,
        "USER INGESTION": 0.5,
        "POST TRANSFORMATION": 0.8,
    }

    records = (
        stage_audit.create_stage_audit_records(
            "run-001",
            stage_durations,
        )
    )

    assert len(records) == 3

    assert records[0] == {
        "run_id": "run-001",
        "stage_name": "POST INGESTION",
        "duration": 1.5,
    }

    assert records[1]["stage_name"] == (
        "USER INGESTION"
    )

    assert records[2]["duration"] == 0.8


def test_create_stage_audit_records_empty():

    records = (
        stage_audit.create_stage_audit_records(
            "run-001",
            {},
        )
    )

    assert records == []


def test_save_stage_audit_records(
    tmp_path,
    monkeypatch,
):

    audit_file = (
        tmp_path
        / "pipeline_stage_runs.parquet"
    )

    monkeypatch.setattr(
        stage_audit,
        "STAGE_AUDIT_FILE",
        audit_file,
    )

    records = [
        {
            "run_id": "run-001",
            "stage_name": "POST INGESTION",
            "duration": 1.5,
        },
        {
            "run_id": "run-001",
            "stage_name": "USER INGESTION",
            "duration": 0.5,
        },
    ]

    stage_audit.save_stage_audit_records(
        records
    )

    assert audit_file.exists()

    df = pd.read_parquet(
        audit_file
    )

    assert len(df) == 2

    assert (
        df.loc[0, "run_id"]
        == "run-001"
    )

    assert (
        df.loc[0, "stage_name"]
        == "POST INGESTION"
    )

    assert (
        df.loc[0, "duration"]
        == 1.5
    )


def test_save_stage_audit_records_appends(
    tmp_path,
    monkeypatch,
):

    audit_file = (
        tmp_path
        / "pipeline_stage_runs.parquet"
    )

    monkeypatch.setattr(
        stage_audit,
        "STAGE_AUDIT_FILE",
        audit_file,
    )

    first_records = [
        {
            "run_id": "run-001",
            "stage_name": "POST INGESTION",
            "duration": 1.5,
        }
    ]

    second_records = [
        {
            "run_id": "run-002",
            "stage_name": "POST INGESTION",
            "duration": 2.0,
        }
    ]

    stage_audit.save_stage_audit_records(
        first_records
    )

    stage_audit.save_stage_audit_records(
        second_records
    )

    df = pd.read_parquet(
        audit_file
    )

    assert len(df) == 2

    assert df["run_id"].tolist() == [
        "run-001",
        "run-002",
    ]


def test_save_empty_records(
    tmp_path,
    monkeypatch,
):

    audit_file = (
        tmp_path
        / "pipeline_stage_runs.parquet"
    )

    monkeypatch.setattr(
        stage_audit,
        "STAGE_AUDIT_FILE",
        audit_file,
    )

    stage_audit.save_stage_audit_records(
        []
    )

    assert not audit_file.exists()

