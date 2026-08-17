import pandas as pd

from src.audit import stage_monitor


def sample_dataframe():

    return pd.DataFrame(
        {
            "run_id": [
                "run-001",
                "run-001",
                "run-002",
                "run-002",
                "run-003",
            ],
            "stage_name": [
                "POST INGESTION",
                "USER INGESTION",
                "POST INGESTION",
                "USER INGESTION",
                "POST INGESTION",
            ],
            "duration": [
                1.0,
                0.5,
                3.0,
                1.5,
                1.5,
            ],
        }
    )


def test_get_sla_violations():

    df = sample_dataframe()

    thresholds = {
        "POST INGESTION": 2.0,
        "USER INGESTION": 1.0,
    }

    result = stage_monitor.get_sla_violations(
        df,
        thresholds,
    )

    assert len(result) == 2

    assert result.iloc[0]["run_id"] == (
        "run-002"
    )

    assert result.iloc[0]["stage_name"] == (
        "POST INGESTION"
    )

    assert result.iloc[0]["duration"] == 3.0

    assert result.iloc[1]["stage_name"] == (
        "USER INGESTION"
    )


def test_no_sla_violations():

    df = sample_dataframe()

    thresholds = {
        "POST INGESTION": 5.0,
        "USER INGESTION": 5.0,
    }

    result = stage_monitor.get_sla_violations(
        df,
        thresholds,
    )

    assert result.empty


def test_get_sla_compliance_rate():

    df = sample_dataframe()

    result = (
        stage_monitor.get_sla_compliance_rate(
            df,
            "POST INGESTION",
            2.0,
        )
    )

    assert result == 66.67


def test_get_sla_violation_rate():

    df = sample_dataframe()

    result = (
        stage_monitor.get_sla_violation_rate(
            df,
            "POST INGESTION",
            2.0,
        )
    )

    assert result == 33.33


def test_get_stage_sla_summary():

    df = sample_dataframe()

    thresholds = {
        "POST INGESTION": 2.0,
        "USER INGESTION": 1.0,
    }

    result = (
        stage_monitor.get_stage_sla_summary(
            df,
            thresholds,
        )
    )

    assert len(result) == 2

    post_ingestion = next(
        item
        for item in result
        if item["stage_name"]
        == "POST INGESTION"
    )

    assert post_ingestion[
        "executions"
    ] == 3

    assert post_ingestion[
        "violations"
    ] == 1

    assert post_ingestion[
        "compliance_rate"
    ] == 66.67

    assert post_ingestion[
        "violation_rate"
    ] == 33.33

    assert post_ingestion[
        "sla_status"
    ] == "VIOLATION"


def test_get_worst_sla_stage():

    df = sample_dataframe()

    thresholds = {
        "POST INGESTION": 2.0,
        "USER INGESTION": 1.0,
    }

    result = (
        stage_monitor.get_worst_sla_stage(
            df,
            thresholds,
        )
    )

    assert result[
        "stage_name"
    ] == "USER INGESTION"

    assert result[
        "violation_rate"
    ] == 50.0


def test_get_sla_summary():

    df = sample_dataframe()

    thresholds = {
        "POST INGESTION": 2.0,
        "USER INGESTION": 1.0,
    }

    result = stage_monitor.get_sla_summary(
        df,
        thresholds,
    )

    assert result[
        "total_executions"
    ] == 5

    assert result[
        "total_violations"
    ] == 2

    assert result[
        "overall_compliance_rate"
    ] == 60.0

    assert result[
        "worst_stage"
    ]["stage_name"] == (
        "USER INGESTION"
    )


def test_empty_dataframe():

    df = pd.DataFrame(
        columns=[
            "run_id",
            "stage_name",
            "duration",
        ]
    )

    thresholds = {
        "POST INGESTION": 2.0,
    }

    violations = (
        stage_monitor.get_sla_violations(
            df,
            thresholds,
        )
    )

    assert violations.empty

    assert (
        stage_monitor.get_sla_compliance_rate(
            df,
            "POST INGESTION",
            2.0,
        )
        == 0.0
    )

    summary = (
        stage_monitor.get_sla_summary(
            df,
            thresholds,
        )
    )

    assert summary[
        "total_executions"
    ] == 0

    assert summary[
        "total_violations"
    ] == 0

    assert summary[
        "overall_compliance_rate"
    ] == 0.0

    assert summary[
        "worst_stage"
    ] is None
