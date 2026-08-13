from src.config import pipeline_config


def test_get_pipeline_interval_uses_default(monkeypatch):
    monkeypatch.delenv("PIPELINE_INTERVAL_MINUTES", raising=False)

    assert pipeline_config.get_pipeline_interval() == 60


def test_get_pipeline_interval_reads_environment(monkeypatch):
    monkeypatch.setenv("PIPELINE_INTERVAL_MINUTES", "30")

    assert pipeline_config.get_pipeline_interval() == 30


def test_get_pipeline_interval_rejects_invalid_value(monkeypatch):
    monkeypatch.setenv("PIPELINE_INTERVAL_MINUTES", "invalid")

    assert pipeline_config.get_pipeline_interval() == 60


def test_get_pipeline_interval_rejects_zero(monkeypatch):
    monkeypatch.setenv("PIPELINE_INTERVAL_MINUTES", "0")

    assert pipeline_config.get_pipeline_interval() == 60


def test_get_pipeline_interval_rejects_negative_value(monkeypatch):
    monkeypatch.setenv("PIPELINE_INTERVAL_MINUTES", "-10")

    assert pipeline_config.get_pipeline_interval() == 60
