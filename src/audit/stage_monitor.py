import pandas as pd


SLA_THRESHOLDS = {
    "POST INGESTION": 2.0,
    "USER INGESTION": 2.0,
    "POST TRANSFORMATION": 2.0,
    "USER TRANSFORMATION": 2.0,
    "POST VALIDATION": 2.0,
    "RELATIONSHIP VALIDATION": 2.0,
    "SCHEMA VALIDATION": 2.0,
    "INCREMENTAL LOAD": 2.0,
    "ANALYTICS DATASET": 2.0,
}


def get_sla_violations(
    df,
    sla_thresholds,
):
    """
    Return every stage execution that exceeded
    its configured SLA threshold.
    """

    if df.empty:
        return pd.DataFrame(
            columns=[
                "run_id",
                "stage_name",
                "duration",
                "sla_threshold",
            ]
        )

    records = []

    for _, row in df.iterrows():

        stage_name = row["stage_name"]

        if stage_name not in sla_thresholds:
            continue

        threshold = sla_thresholds[
            stage_name
        ]

        if row["duration"] > threshold:

            records.append(
                {
                    "run_id": row["run_id"],
                    "stage_name": stage_name,
                    "duration": float(
                        row["duration"]
                    ),
                    "sla_threshold": float(
                        threshold
                    ),
                }
            )

    return pd.DataFrame(records)


def get_sla_compliance_rate(
    df,
    stage_name,
    threshold,
):
    """
    Return the percentage of executions for
    a stage that stayed within its SLA.
    """

    stage_df = df[
        df["stage_name"] == stage_name
    ]

    if stage_df.empty:
        return 0.0

    compliant = (
        stage_df["duration"] <= threshold
    ).sum()

    total = len(stage_df)

    return round(
        (compliant / total) * 100,
        2,
    )


def get_sla_violation_rate(
    df,
    stage_name,
    threshold,
):
    """
    Return the percentage of executions for
    a stage that violated its SLA.
    """

    compliance_rate = (
        get_sla_compliance_rate(
            df,
            stage_name,
            threshold,
        )
    )

    return round(
        100 - compliance_rate,
        2,
    )


def get_stage_sla_summary(
    df,
    sla_thresholds,
):
    """
    Return SLA performance for every
    configured stage.
    """

    results = []

    for stage_name, threshold in (
        sla_thresholds.items()
    ):

        stage_df = df[
            df["stage_name"]
            == stage_name
        ]

        executions = len(stage_df)

        if executions == 0:

            results.append(
                {
                    "stage_name": stage_name,
                    "executions": 0,
                    "sla_threshold": float(
                        threshold
                    ),
                    "violations": 0,
                    "compliance_rate": 0.0,
                    "violation_rate": 0.0,
                    "sla_status": "NO DATA",
                }
            )

            continue

        violations = int(
            (
                stage_df["duration"]
                > threshold
            ).sum()
        )

        compliance_rate = round(
            (
                (
                    executions
                    - violations
                )
                / executions
            )
            * 100,
            2,
        )

        violation_rate = round(
            (violations / executions)
            * 100,
            2,
        )

        if violations == 0:
            status = "PASSED"
        else:
            status = "VIOLATION"

        results.append(
            {
                "stage_name": stage_name,
                "executions": executions,
                "sla_threshold": float(
                    threshold
                ),
                "violations": violations,
                "compliance_rate": (
                    compliance_rate
                ),
                "violation_rate": (
                    violation_rate
                ),
                "sla_status": status,
            }
        )

    return results


def get_worst_sla_stage(
    df,
    sla_thresholds,
):
    """
    Return the stage with the highest
    SLA violation rate.
    """

    summary = get_stage_sla_summary(
        df,
        sla_thresholds,
    )

    valid_results = [
        item
        for item in summary
        if item["executions"] > 0
    ]

    if not valid_results:
        return None

    return max(
        valid_results,
        key=lambda item: item[
            "violation_rate"
        ],
    )


def get_sla_summary(
    df,
    sla_thresholds,
):
    """
    Return a complete SLA monitoring report.
    """

    violations = get_sla_violations(
        df,
        sla_thresholds,
    )

    summary = get_stage_sla_summary(
        df,
        sla_thresholds,
    )

    worst_stage = get_worst_sla_stage(
        df,
        sla_thresholds,
    )

    total_executions = len(df)

    total_violations = len(
        violations
    )

    if total_executions == 0:

        overall_compliance = 0.0

    else:

        overall_compliance = round(
            (
                (
                    total_executions
                    - total_violations
                )
                / total_executions
            )
            * 100,
            2,
        )

    return {
        "total_executions": (
            total_executions
        ),
        "total_violations": (
            total_violations
        ),
        "overall_compliance_rate": (
            overall_compliance
        ),
        "stage_summary": summary,
        "worst_stage": worst_stage,
    }


def main():
    print(
        "Starting stage SLA monitoring..."
    )

    from src.audit.stage_audit import (
        load_stage_audit_records,
    )

    df = load_stage_audit_records()

    print(
        f"Total stage executions: {len(df)}"
    )

    result = get_sla_summary(
        df,
        SLA_THRESHOLDS,
    )

    print()
    print("SLA SUMMARY:")
    print()

    for stage in result["stage_summary"]:

        print(
            f"{stage['stage_name']}:"
        )

        print(
            f"  Executions: "
            f"{stage['executions']}"
        )

        print(
            f"  SLA: "
            f"{stage['sla_threshold']:.2f}s"
        )

        print(
            f"  Violations: "
            f"{stage['violations']}"
        )

        print(
            f"  Compliance: "
            f"{stage['compliance_rate']:.2f}%"
        )

        print(
            f"  Violation rate: "
            f"{stage['violation_rate']:.2f}%"
        )

        print(
            f"  Status: "
            f"{stage['sla_status']}"
        )

        print()

    print("OVERALL SLA:")

    print(
        f"Total executions: "
        f"{result['total_executions']}"
    )

    print(
        f"Total violations: "
        f"{result['total_violations']}"
    )

    print(
        f"Overall compliance: "
        f"{result['overall_compliance_rate']:.2f}%"
    )

    print()

    worst_stage = result[
        "worst_stage"
    ]

    if worst_stage:

        print(
            "WORST SLA STAGE:"
        )

        print(
            f"Stage: "
            f"{worst_stage['stage_name']}"
        )

        print(
            f"Violation rate: "
            f"{worst_stage['violation_rate']:.2f}%"
        )

        print(
            f"Violations: "
            f"{worst_stage['violations']}"
        )

    print()
    print(
        "Stage SLA monitoring completed."
    )


if __name__ == "__main__":
    main()
