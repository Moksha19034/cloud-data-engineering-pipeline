from src.state import pipeline_state


def test_save_state_creates_file(tmp_path):
    state_file = tmp_path / "pipeline_state.json"

    pipeline_state.STATE_FILE = state_file

    state = {
        "last_run_id": "run-001",
        "last_status": "SUCCESS",
        "last_finished_at": "2026-08-13T10:00:00+00:00",
    }

    pipeline_state.save_state(state)

    assert state_file.exists()


def test_load_state_returns_saved_state(tmp_path):
    state_file = tmp_path / "pipeline_state.json"

    pipeline_state.STATE_FILE = state_file

    state = {
        "last_run_id": "run-001",
        "last_status": "SUCCESS",
        "last_finished_at": "2026-08-13T10:00:00+00:00",
    }

    pipeline_state.save_state(state)

    result = pipeline_state.load_state()

    assert result["last_run_id"] == "run-001"
    assert result["last_status"] == "SUCCESS"


def test_load_state_returns_none_when_file_missing(tmp_path):
    state_file = tmp_path / "missing_state.json"

    pipeline_state.STATE_FILE = state_file

    result = pipeline_state.load_state()

    assert result is None


def test_is_previous_run_successful(tmp_path):
    state_file = tmp_path / "pipeline_state.json"

    pipeline_state.STATE_FILE = state_file

    state = {
        "last_run_id": "run-001",
        "last_status": "SUCCESS",
        "last_finished_at": "2026-08-13T10:00:00+00:00",
    }

    pipeline_state.save_state(state)

    assert pipeline_state.is_previous_run_successful() is True


def test_is_previous_run_successful_returns_false_when_failed(tmp_path):
    state_file = tmp_path / "pipeline_state.json"

    pipeline_state.STATE_FILE = state_file

    state = {
        "last_run_id": "run-002",
        "last_status": "FAILED",
        "last_finished_at": "2026-08-13T10:05:00+00:00",
    }

    pipeline_state.save_state(state)

    assert pipeline_state.is_previous_run_successful() is False
