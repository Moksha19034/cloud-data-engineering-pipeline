import pandas as pd

from src.audit import sla_recommendation


def sample_baseline():
    return [
        {
            "stage_name": "POST TRANSFORMATION",
            "executions": 20,
            "average_duration": 1.8,
            "minimum_duration": 0.4,
            "maximum_duration": 3.0,
            "median_duration": 1.5,
            "p95_duration": 3.0,
            "p99_duration": 3.0,
        },
        {
            "stage_name": "POST VALIDATION",
            "executions": 20,
            "average_duration": 1.2,
            "minimum_duration": 0.4,
            "maximum_duration": 1.8,
            "median_duration": 1.0,
            "p95_duration": 1.8,
            "p99_duration": 1.8,
        },
    ]


def test_recommend_sla_investigate():

    baseline = sample_baseline()[0]

    result = sla_recommendation.recommend_sla(
        baseline,
        2.0,
    )

    assert (
        result["stage_name"]
        == "POST TRANSFORMATION"
    )

    assert (
        result["p95_duration"]
        == 3.0
    )

    assert (
        result["current_sla"]
        == 2.0
    )

    assert (
        result["recommended_sla"]
        == 3.0
    )

    assert (
        result["recommendation"]
        == "INVESTIGATE"
    )


def test_recommend_sla_keep():

    baseline = sample_baseline()[1]

    result = sla_recommendation.recommend_sla(
        baseline,
        2.0,
    )

    assert (
        result["recommendation"]
        == "KEEP"
    )


def test_recommend_sla_missing_baseline():

    result = sla_recommendation.recommend_sla(
        None,
        2.0,
    )

    assert result is None


def test_get_sla_recommendations():

    baseline = sample_baseline()

    thresholds = {
        "POST TRANSFORMATION": 2.0,
        "POST VALIDATION": 2.0,
    }

    result = (
        sla_recommendation
        .get_sla_recommendations(
            baseline,
            thresholds,
        )
    )

    assert len(result) == 2


def test_get_investigation_stages():

    recommendations = [
        {
            "stage_name": "POST TRANSFORMATION",
            "recommendation": "INVESTIGATE",
        },
        {
            "stage_name": "POST VALIDATION",
            "recommendation": "KEEP",
        },
    ]

    result = (
        sla_recommendation
        .get_investigation_stages(
            recommendations
        )
    )

    assert len(result) == 1

    assert (
        result[0]["stage_name"]
        == "POST TRANSFORMATION"
    )


def test_get_sla_recommendation_summary():

    baseline = sample_baseline()

    thresholds = {
        "POST TRANSFORMATION": 2.0,
        "POST VALIDATION": 2.0,
    }

    result = (
        sla_recommendation
        .get_sla_recommendation_summary(
            baseline,
            thresholds,
        )
    )

    assert (
        result["total_stages"]
        == 2
    )

    assert (
        result[
            "stages_to_investigate"
        ]
        == 1
    )


def test_empty_baseline():

    result = (
        sla_recommendation
        .get_sla_recommendation_summary(
            [],
            {},
        )
    )

    assert (
        result["total_stages"]
        == 0
    )

    assert (
        result[
            "stages_to_investigate"
        ]
        == 0
    )

    assert (
        result[
            "recommendations"
        ]
        == []
    )
