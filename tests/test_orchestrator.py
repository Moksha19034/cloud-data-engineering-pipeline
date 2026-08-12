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
