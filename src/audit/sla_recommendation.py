import pandas as pd


def recommend_sla(
    baseline,
    current_sla,
):
    """
    Recommend an SLA based on historical P95
    performance.

    The recommendation does not automatically
    modify the configured SLA.
    """

    if baseline is None:
        return None

    p95 = float(
        baseline["p95_duration"]
    )

    average = float(
        baseline["average_duration"]
    )

    if p95 <= current_sla:
        recommendation = "KEEP"
    else:
        recommendation = "INVESTIGATE"

    return {
        "stage_name": baseline[
            "stage_name"
        ],
        "executions": baseline[
            "executions"
        ],
        "average_duration": average,
        "p95_duration": p95,
        "current_sla": float(
            current_sla
        ),
        "recommended_sla": round(
            p95,
            3,
        ),
        "recommendation": recommendation,
    }


def get_sla_recommendations(
    baseline,
    sla_thresholds,
):
    """
    Generate SLA recommendations for
    every stage with baseline data.
    """

    results = []

    for stage in baseline:

        stage_name = stage[
            "stage_name"
        ]

        if stage_name not in sla_thresholds:
            continue

        recommendation = recommend_sla(
            stage,
            sla_thresholds[
                stage_name
            ],
        )

        if recommendation is not None:
            results.append(
                recommendation
            )

    return results


def get_investigation_stages(
    recommendations,
):
    """
    Return stages whose historical P95
    exceeds the configured SLA.
    """

    return [
        item
        for item in recommendations
        if item["recommendation"]
        == "INVESTIGATE"
    ]


def get_sla_recommendation_summary(
    baseline,
    sla_thresholds,
):
    """
    Return a complete SLA recommendation
    summary.
    """

    recommendations = (
        get_sla_recommendations(
            baseline,
            sla_thresholds,
        )
    )

    investigation_stages = (
        get_investigation_stages(
            recommendations
        )
    )

    return {
        "total_stages": len(
            recommendations
        ),
        "stages_to_investigate": len(
            investigation_stages
        ),
        "recommendations": (
            recommendations
        ),
        "investigation_stages": (
            investigation_stages
        ),
    }


def main():
    print(
        "Starting SLA recommendation analysis..."
    )

    from src.audit.stage_audit import (
        load_stage_audit_records,
    )

    from src.audit.stage_baseline import (
        get_stage_baseline,
    )

    from src.audit.stage_monitor import (
        SLA_THRESHOLDS,
    )

    df = load_stage_audit_records()

    baseline = get_stage_baseline(
        df
    )

    summary = (
        get_sla_recommendation_summary(
            baseline,
            SLA_THRESHOLDS,
        )
    )

    print()

    print(
        "SLA RECOMMENDATIONS:"
    )

    print()

    for item in summary[
        "recommendations"
    ]:

        print(
            f"{item['stage_name']}:"
        )

        print(
            f"  Executions: "
            f"{item['executions']}"
        )

        print(
            f"  Average: "
            f"{item['average_duration']:.3f}s"
        )

        print(
            f"  P95: "
            f"{item['p95_duration']:.3f}s"
        )

        print(
            f"  Current SLA: "
            f"{item['current_sla']:.3f}s"
        )

        print(
            f"  Recommended SLA: "
            f"{item['recommended_sla']:.3f}s"
        )

        print(
            f"  Recommendation: "
            f"{item['recommendation']}"
        )

        print()

    print(
        "SUMMARY:"
    )

    print(
        f"Stages analyzed: "
        f"{summary['total_stages']}"
    )

    print(
        f"Stages requiring investigation: "
        f"{summary['stages_to_investigate']}"
    )

    if summary[
        "investigation_stages"
    ]:

        print()

        print(
            "STAGES TO INVESTIGATE:"
        )

        for item in summary[
            "investigation_stages"
        ]:

            print(
                f"- {item['stage_name']}: "
                f"P95={item['p95_duration']:.3f}s "
                f"> SLA={item['current_sla']:.3f}s"
            )

    print()

    print(
        "SLA recommendation analysis completed."
    )


if __name__ == "__main__":
    main()
