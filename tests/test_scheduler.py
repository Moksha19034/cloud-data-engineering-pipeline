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
