from src.recovery import pipeline_recovery


def test_should_retry_failed_run():
    state = {
        "last_run_id": "run-001",
        "last_status": "FAILED",
        "failed_stage": "POST INGESTION",
        "error": "API failed",
    }

    assert pipeline_recovery.should_retry(
        state,
        retry_count=0,
        max_retries=3,
    ) is True


def test_should_not_retry_after_max_retries():
    state = {
        "last_run_id": "run-001",
        "last_status": "FAILED",
        "failed_stage": "POST INGESTION",
        "error": "API failed",
    }

    assert pipeline_recovery.should_retry(
        state,
        retry_count=3,
        max_retries=3,
    ) is False


def test_should_not_retry_successful_run():
    state = {
        "last_run_id": "run-002",
        "last_status": "SUCCESS",
    }

    assert pipeline_recovery.should_retry(
        state,
        retry_count=0,
        max_retries=3,
    ) is False


def test_should_retry_when_no_previous_state():
    assert pipeline_recovery.should_retry(
        None,
        retry_count=0,
        max_retries=3,
    ) is False


def test_should_skip_successful_run():
    state = {
        "last_run_id": "run-003",
        "last_status": "SUCCESS",
    }

    assert pipeline_recovery.should_skip_run(state) is True


def test_should_not_skip_failed_run():
    state = {
        "last_run_id": "run-004",
        "last_status": "FAILED",
    }

    assert pipeline_recovery.should_skip_run(state) is False


def test_should_not_skip_missing_state():
    assert pipeline_recovery.should_skip_run(None) is False

