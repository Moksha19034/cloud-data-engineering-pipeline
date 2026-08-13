from src.orchestration import orchestrator


def test_run_pipeline_executes_all_stages(monkeypatch):
    executed = []

    def fake_run_stage(stage_name, script_path):
        executed.append((stage_name, script_path))
        return 1.0

    monkeypatch.setattr(
        orchestrator,
        "run_stage",
        fake_run_stage,
    )

    result = orchestrator.run_pipeline()

    assert result["status"] == "SUCCESS"
    assert result["successful_stages"] == 9
    assert result["total_stages"] == 9
    assert len(executed) == 9


def test_run_pipeline_stops_when_stage_fails(monkeypatch):
    executed = []

    def fake_run_stage(stage_name, script_path):
        executed.append(stage_name)

        if stage_name == "POST TRANSFORMATION":
            raise RuntimeError("Stage failed")

        return 1.0

    monkeypatch.setattr(
        orchestrator,
        "run_stage",
        fake_run_stage,
    )

    result = orchestrator.run_pipeline()

    assert result["status"] == "FAILED"
    assert result["successful_stages"] == 2
    assert result["total_stages"] == 9
    assert result["failed_stage"] == "POST TRANSFORMATION"

    assert executed == [
        "POST INGESTION",
        "USER INGESTION",
        "POST TRANSFORMATION",
    ]


def test_run_pipeline_records_stage_durations(monkeypatch):
    def fake_run_stage(stage_name, script_path):
        return 2.5

    monkeypatch.setattr(
        orchestrator,
        "run_stage",
        fake_run_stage,
    )

    result = orchestrator.run_pipeline()

    assert result["total_duration"] == 22.5
    assert result["successful_stages"] == 9

def test_run_pipeline_includes_stage_metrics(monkeypatch):
    def fake_run_stage(stage_name, script_path):
        durations = {
            "POST INGESTION": 1.0,
            "USER INGESTION": 2.0,
            "POST TRANSFORMATION": 3.0,
            "USER TRANSFORMATION": 1.5,
            "POST VALIDATION": 0.5,
            "RELATIONSHIP VALIDATION": 0.8,
            "SCHEMA VALIDATION": 0.7,
            "INCREMENTAL LOAD": 1.2,
            "ANALYTICS DATASET": 2.5,
        }

        return durations[stage_name]

    monkeypatch.setattr(
        orchestrator,
        "run_stage",
        fake_run_stage,
    )

    result = orchestrator.run_pipeline()

    assert result["status"] == "SUCCESS"

    assert result["stage_metrics"]["total_stages"] == 9

    assert (
        result["stage_metrics"]["fastest_stage"]
        == "POST VALIDATION"
    )

    assert (
        result["stage_metrics"]["slowest_stage"]
        == "POST TRANSFORMATION"
    )

    assert (
        result["stage_metrics"]["fastest_duration"]
        == 0.5
    )

    assert (
        result["stage_metrics"]["slowest_duration"]
        == 3.0
    )
