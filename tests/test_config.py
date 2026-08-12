import pytest

from src.ingestion.fetch_data import get_int_config


def test_get_int_config_returns_integer(monkeypatch):
    monkeypatch.setenv("TEST_CONFIG", "60")

    result = get_int_config("TEST_CONFIG", 30)

    assert result == 60


def test_get_int_config_uses_default(monkeypatch):
    monkeypatch.delenv("TEST_CONFIG", raising=False)

    result = get_int_config("TEST_CONFIG", 30)

    assert result == 30


def test_get_int_config_rejects_invalid_value(monkeypatch):
    monkeypatch.setenv("TEST_CONFIG", "abc")

    with pytest.raises(
        ValueError,
        match="Invalid configuration: TEST_CONFIG must be an integer",
    ):
        get_int_config("TEST_CONFIG", 30)
