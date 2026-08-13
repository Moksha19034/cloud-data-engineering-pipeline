from src.scheduler import pipeline_scheduler


def test_scheduler_uses_configured_interval(monkeypatch):
    monkeypatch.setattr(
        pipeline_scheduler,
        "get_pipeline_interval",
        lambda: 30,
    )

    assert pipeline_scheduler.get_schedule_interval() == 30


def test_scheduler_uses_default_interval(monkeypatch):
    monkeypatch.setattr(
        pipeline_scheduler,
        "get_pipeline_interval",
        lambda: 60,
    )

    assert pipeline_scheduler.get_schedule_interval() == 60


def test_scheduler_runs_pipeline(monkeypatch):
    executed = []

    def fake_pipeline():
        executed.append(True)
        return {
            "status": "SUCCESS",
            "total_duration": 3.0,
        }

    monkeypatch.setattr(
        pipeline_scheduler,
        "orchestrate_pipeline",
        fake_pipeline,
    )

    result = pipeline_scheduler.execute_pipeline()

    assert result["status"] == "SUCCESS"
    assert executed == [True]

def test_scheduler_runs_multiple_times(monkeypatch):
    executions = []
    sleeps = []

    def fake_pipeline():
        executions.append(len(executions) + 1)
        return {
            "status": "SUCCESS",
            "total_duration": 1.0,
        }

    def fake_sleep(seconds):
        sleeps.append(seconds)

        if len(executions) >= 3:
            raise KeyboardInterrupt

    monkeypatch.setattr(
        pipeline_scheduler,
        "orchestrate_pipeline",
        fake_pipeline,
    )

    monkeypatch.setattr(
        pipeline_scheduler.time,
        "sleep",
        fake_sleep,
    )

    try:
        pipeline_scheduler.run_scheduler(
            interval_minutes=30
        )
    except KeyboardInterrupt:
        pass

    assert executions == [1, 2, 3]
    assert sleeps == [1800, 1800, 1800]


def test_scheduler_stops_after_pipeline_failure(monkeypatch):
    executions = []

    def fake_pipeline():
        executions.append(True)

        return {
            "status": "FAILED",
            "total_duration": 2.0,
        }

    monkeypatch.setattr(
        pipeline_scheduler,
        "orchestrate_pipeline",
        fake_pipeline,
    )

    result = pipeline_scheduler.run_scheduler(
        interval_minutes=30,
        stop_on_failure=True,
        max_runs=5,
    )

    assert result["runs"] == 1
    assert result["failures"] == 1

def test_scheduler_retries_failed_pipeline_then_succeeds(monkeypatch):
    executions = []
    states = [
        {
            "last_status": "FAILED",
            "last_run_id": "run-001",
        },
        {
            "last_status": "SUCCESS",
            "last_run_id": "run-002",
        },
    ]

    def fake_pipeline():
        executions.append(len(executions) + 1)

        if len(executions) == 1:
            return {
                "status": "FAILED",
                "total_duration": 2.0,
            }

        return {
            "status": "SUCCESS",
            "total_duration": 2.0,
        }

    def fake_load_state():
        if states:
            return states.pop(0)

        return {
            "last_status": "SUCCESS",
            "last_run_id": "run-002",
        }

    monkeypatch.setattr(
        pipeline_scheduler,
        "orchestrate_pipeline",
        fake_pipeline,
    )

    monkeypatch.setattr(
        pipeline_scheduler,
        "load_state",
        fake_load_state,
    )

    result = pipeline_scheduler.run_scheduler(
        interval_minutes=30,
        max_retries=3,
        max_runs=1,
    )

    assert executions == [1, 2]
    assert result["runs"] == 2
    assert result["failures"] == 1
    assert result["retries"] == 1


def test_scheduler_stops_after_max_retries(monkeypatch):
    executions = []

    def fake_pipeline():
        executions.append(len(executions) + 1)

        return {
            "status": "FAILED",
            "total_duration": 2.0,
        }

    def fake_load_state():
        return {
            "last_status": "FAILED",
            "last_run_id": "run-001",
        }

    monkeypatch.setattr(
        pipeline_scheduler,
        "orchestrate_pipeline",
        fake_pipeline,
    )

    monkeypatch.setattr(
        pipeline_scheduler,
        "load_state",
        fake_load_state,
    )

    result = pipeline_scheduler.run_scheduler(
        interval_minutes=30,
        max_retries=2,
        max_runs=1,
    )

    assert executions == [1, 2, 3]
    assert result["runs"] == 3
    assert result["failures"] == 3
    assert result["retries"] == 2


def test_scheduler_skips_successful_previous_run(monkeypatch):
    executions = []

    def fake_pipeline():
        executions.append(True)

        return {
            "status": "SUCCESS",
            "total_duration": 1.0,
        }

    def fake_load_state():
        return {
            "last_status": "SUCCESS",
            "last_run_id": "run-001",
        }

    monkeypatch.setattr(
        pipeline_scheduler,
        "orchestrate_pipeline",
        fake_pipeline,
    )

    monkeypatch.setattr(
        pipeline_scheduler,
        "load_state",
        fake_load_state,
    )

    result = pipeline_scheduler.run_scheduler(
        interval_minutes=30,
        max_runs=1,
    )

    assert executions == []
    assert result["runs"] == 0
    assert result["failures"] == 0
    assert result["retries"] == 0
    assert result["skipped_runs"] == 1
