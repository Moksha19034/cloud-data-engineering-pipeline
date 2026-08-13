import pandas as pd

from src.audit import pipeline_metrics


def sample_stage_durations():
    return {
        "POST INGESTION": 1.2,
        "USER INGESTION": 0.8,
        "POST TRANSFORMATION": 2.5,
        "USER TRANSFORMATION": 1.1,
        "POST VALIDATION": 0.6,
        "RELATIONSHIP VALIDATION": 0.9,
        "SCHEMA VALIDATION": 0.7,
        "INCREMENTAL LOAD": 1.4,
        "ANALYTICS DATASET": 1.8,
    }


def test_get_fastest_stage():
    durations = sample_stage_durations()

    result = pipeline_metrics.get_fastest_stage(durations)

    assert result["stage"] == "POST VALIDATION"
    assert result["duration"] == 0.6


def test_get_slowest_stage():
    durations = sample_stage_durations()

    result = pipeline_metrics.get_slowest_stage(durations)

    assert result["stage"] == "POST TRANSFORMATION"
    assert result["duration"] == 2.5


def test_get_average_stage_duration():
    durations = sample_stage_durations()

    result = pipeline_metrics.get_average_stage_duration(
        durations
    )

    assert round(result, 2) == 1.22


def test_get_slow_stages():
    durations = sample_stage_durations()

    result = pipeline_metrics.get_slow_stages(
        durations,
        threshold=2.0,
    )

    assert result == {
        "POST TRANSFORMATION": 2.5,
    }


def test_get_stage_metrics():
    durations = sample_stage_durations()

    result = pipeline_metrics.get_stage_metrics(
        durations
    )

    assert result["total_stages"] == 9
    assert result["fastest_stage"] == "POST VALIDATION"
    assert result["slowest_stage"] == "POST TRANSFORMATION"
    assert result["fastest_duration"] == 0.6
    assert result["slowest_duration"] == 2.5


def test_get_stage_metrics_empty():
    result = pipeline_metrics.get_stage_metrics({})

    assert result["total_stages"] == 0
    assert result["fastest_stage"] is None
    assert result["slowest_stage"] is None
    assert result["fastest_duration"] == 0.0
    assert result["slowest_duration"] == 0.0


def test_get_slow_stages_empty():
    result = pipeline_metrics.get_slow_stages(
        {},
        threshold=2.0,
    )

    assert result == {}
