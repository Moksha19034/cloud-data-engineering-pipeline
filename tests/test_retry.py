from tenacity import retry, stop_after_attempt, wait_none

import pytest


def test_retry_succeeds_after_temporary_failures():
    attempts = {"count": 0}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_none(),
    )
    def unreliable_function():
        attempts["count"] += 1

        if attempts["count"] < 3:
            raise RuntimeError("Temporary failure")

        return "success"

    result = unreliable_function()

    assert result == "success"
    assert attempts["count"] == 3


def test_retry_stops_after_three_failures():
    attempts = {"count": 0}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_none(),
    )
    def failing_function():
        attempts["count"] += 1
        raise RuntimeError("Permanent failure")

    with pytest.raises(Exception):
        failing_function()

    assert attempts["count"] == 3


def test_retry_does_not_exceed_three_attempts():
    attempts = {"count": 0}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_none(),
    )
    def failing_function():
        attempts["count"] += 1
        raise ValueError("Failure")

    with pytest.raises(Exception):
        failing_function()

    assert attempts["count"] == 3
