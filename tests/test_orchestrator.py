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

def test_run_pipeline_includes_quality_metrics(monkeypatch):
    quality_metrics = {
        "records_checked": 102,
        "null_values": 0,
        "duplicate_post_ids": 0,
        "quality_status": "PASSED",
    }

    def fake_run_stage(stage_name, script_path):
        return 1.0

    monkeypatch.setattr(
        orchestrator,
        "run_stage",
        fake_run_stage,
    )

    monkeypatch.setattr(
        orchestrator,
        "load_quality_metrics",
        lambda: quality_metrics,
    )

    result = orchestrator.run_pipeline()

    assert result["status"] == "SUCCESS"

    assert result["quality_metrics"] == quality_metrics

def test_run_stage_with_retry_success(
    monkeypatch,
):
    calls = []

    def fake_run_stage(
        stage_name,
        script_path,
    ):
        calls.append(1)

        return 0.5

    monkeypatch.setattr(
        orchestrator,
        "run_stage",
        fake_run_stage,
    )

    result = (
        orchestrator
        .run_stage_with_retry(
            "POST INGESTION",
            "fake.py",
        )
    )

    assert result["status"] == "SUCCESS"
    assert result["result"] == 0.5
    assert result["attempts"] == 1
    assert result["retries"] == 0
    assert len(calls) == 1


def test_run_stage_with_retry_retries_ingestion(
    monkeypatch,
):
    calls = []

    def fake_run_stage(
        stage_name,
        script_path,
    ):
        calls.append(1)

        if len(calls) < 3:
            raise RuntimeError(
                "temporary failure"
            )

        return 0.7

    sleep_calls = []

    monkeypatch.setattr(
        orchestrator,
        "run_stage",
        fake_run_stage,
    )

    result = (
        orchestrator
        .execute_with_retry
    )

    retry_result = (
        orchestrator
        .run_stage_with_retry(
            "POST INGESTION",
            "fake.py",
        )
    )

    assert (
        retry_result["status"]
        == "SUCCESS"
    )

    assert (
        retry_result["attempts"]
        == 3
    )

    assert (
        retry_result["retries"]
        == 2
    )

    assert len(calls) == 3


def test_run_stage_with_retry_does_not_retry_transformation(
    monkeypatch,
):
    calls = []

    def fake_run_stage(
        stage_name,
        script_path,
    ):
        calls.append(1)

        raise RuntimeError(
            "bad transformation"
        )

    monkeypatch.setattr(
        orchestrator,
        "run_stage",
        fake_run_stage,
    )

    result = (
        orchestrator
        .run_stage_with_retry(
            "POST TRANSFORMATION",
            "fake.py",
        )
    )

    assert (
        result["status"]
        == "FAILED"
    )

    assert (
        result["attempts"]
        == 1
    )

    assert (
        result["retries"]
        == 0
    )

    assert len(calls) == 1
def test_run_pipeline_saves_success_state(monkeypatch):
    saved_states = []

    def fake_run_stage(stage_name, script_path):
        return 1.0

    def fake_save_state(state):
        saved_states.append(state)

    monkeypatch.setattr(
        orchestrator,
        "run_stage",
        fake_run_stage,
    )

    monkeypatch.setattr(
        orchestrator,
        "save_state",
        fake_save_state,
    )

    result = orchestrator.run_pipeline()

    assert result["status"] == "SUCCESS"
    assert len(saved_states) == 1

    state = saved_states[0]

    assert state["last_run_id"] == result["run_id"]
    assert state["last_status"] == "SUCCESS"
    assert "last_finished_at" in state


def test_run_pipeline_saves_failure_state(monkeypatch):
    saved_states = []

    def fake_run_stage(stage_name, script_path):
        if stage_name == "POST TRANSFORMATION":
            raise RuntimeError(
                "temporary transformation failure"
            )

        return 1.0

    def fake_save_state(state):
        saved_states.append(state)

    monkeypatch.setattr(
        orchestrator,
        "run_stage",
        fake_run_stage,
    )

    monkeypatch.setattr(
        orchestrator,
        "save_state",
        fake_save_state,
    )

    result = orchestrator.run_pipeline()

    assert result["status"] == "FAILED"
    assert result["failed_stage"] == "POST TRANSFORMATION"

    assert len(saved_states) == 1

    state = saved_states[0]

    assert state["last_run_id"] == result["run_id"]
    assert state["last_status"] == "FAILED"
    assert state["failed_stage"] == "POST TRANSFORMATION"
    assert "last_finished_at" in state
