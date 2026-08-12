import requests
import pytest

from src.ingestion import fetch_data


def test_fetch_data_succeeds_without_retry(monkeypatch):
    attempts = {"count": 0}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return [{"id": 1}]

    def fake_get(url, timeout):
        attempts["count"] += 1
        return FakeResponse()

    monkeypatch.setattr(fetch_data.requests, "get", fake_get)

    result = fetch_data.fetch_data()

    assert result == [{"id": 1}]
    assert attempts["count"] == 1


def test_fetch_data_retries_on_connection_error(monkeypatch):
    attempts = {"count": 0}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return [{"id": 1}]

    def fake_get(url, timeout):
        attempts["count"] += 1

        if attempts["count"] < 3:
            raise requests.ConnectionError("Temporary connection failure")

        return FakeResponse()

    monkeypatch.setattr(fetch_data.requests, "get", fake_get)
    monkeypatch.setattr(fetch_data, "RETRY_MIN_WAIT", 0)
    monkeypatch.setattr(fetch_data, "RETRY_MAX_WAIT", 0)

    result = fetch_data.fetch_data()

    assert result == [{"id": 1}]
    assert attempts["count"] == 3


def test_fetch_data_does_not_retry_permanent_http_error(monkeypatch):
    attempts = {"count": 0}

    class FakeResponse:
        status_code = 404

        def raise_for_status(self):
            raise requests.HTTPError(
                "404 Client Error",
                response=self,
            )

    def fake_get(url, timeout):
        attempts["count"] += 1
        return FakeResponse()

    monkeypatch.setattr(fetch_data.requests, "get", fake_get)
    monkeypatch.setattr(fetch_data, "RETRY_MIN_WAIT", 0)
    monkeypatch.setattr(fetch_data, "RETRY_MAX_WAIT", 0)

    with pytest.raises(requests.HTTPError):
        fetch_data.fetch_data()

    assert attempts["count"] == 1
