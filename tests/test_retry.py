import pytest

from src.orchestration import retry


def test_calculate_backoff_first_retry():

    assert (
        retry.calculate_backoff(1)
        == 1.0
    )


def test_calculate_backoff_second_retry():

    assert (
        retry.calculate_backoff(2)
        == 2.0
    )


def test_calculate_backoff_third_retry():

    assert (
        retry.calculate_backoff(3)
        == 4.0
    )


def test_calculate_backoff_custom_delay():

    assert (
        retry.calculate_backoff(
            3,
            initial_delay=0.5,
        )
        == 2.0
    )


def test_calculate_backoff_invalid_retry():

    with pytest.raises(ValueError):

        retry.calculate_backoff(0)


def test_successful_first_attempt():

    calls = []

    def function():

        calls.append(1)

        return "success"

    result = retry.execute_with_retry(
        function,
        max_retries=3,
        initial_delay=1.0,
        sleep_function=lambda _: None,
    )

    assert (
        result["status"]
        == "SUCCESS"
    )

    assert (
        result["result"]
        == "success"
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


def test_retryable_failure_then_success():

    calls = []

    def function():

        calls.append(1)

        if len(calls) < 3:

            raise ConnectionError(
                "Temporary network failure"
            )

        return "success"

    sleep_calls = []

    result = retry.execute_with_retry(
        function,
        max_retries=3,
        initial_delay=1.0,
        sleep_function=sleep_calls.append,
        is_retryable=lambda error: True,
    )

    assert (
        result["status"]
        == "SUCCESS"
    )

    assert (
        result["result"]
        == "success"
    )

    assert (
        result["attempts"]
        == 3
    )

    assert (
        result["retries"]
        == 2
    )

    assert sleep_calls == [
        1.0,
        2.0,
    ]


def test_retryable_failure_exhausts_retries():

    calls = []

    def function():

        calls.append(1)

        raise ConnectionError(
            "Service unavailable"
        )

    sleep_calls = []

    result = retry.execute_with_retry(
        function,
        max_retries=3,
        initial_delay=1.0,
        sleep_function=sleep_calls.append,
        is_retryable=lambda error: True,
    )

    assert (
        result["status"]
        == "FAILED"
    )

    assert (
        result["attempts"]
        == 4
    )

    assert (
        result["retries"]
        == 3
    )

    assert len(calls) == 4

    assert sleep_calls == [
        1.0,
        2.0,
        4.0,
    ]


def test_non_retryable_failure_stops_immediately():

    calls = []

    def function():

        calls.append(1)

        raise ValueError(
            "Invalid data"
        )

    sleep_calls = []

    result = retry.execute_with_retry(
        function,
        max_retries=3,
        initial_delay=1.0,
        sleep_function=sleep_calls.append,
        is_retryable=lambda error: False,
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

    assert sleep_calls == []


def test_zero_max_retries():

    calls = []

    def function():

        calls.append(1)

        raise ConnectionError(
            "Temporary failure"
        )

    result = retry.execute_with_retry(
        function,
        max_retries=0,
        sleep_function=lambda _: None,
        is_retryable=lambda error: True,
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


def test_invalid_max_retries():

    with pytest.raises(ValueError):

        retry.execute_with_retry(
            lambda: "success",
            max_retries=-1,
        )


def test_invalid_initial_delay():

    with pytest.raises(ValueError):

        retry.execute_with_retry(
            lambda: "success",
            initial_delay=-1,
        )


def test_retry_preserves_last_error():

    error = ConnectionError(
        "Final failure"
    )

    def function():

        raise error

    result = retry.execute_with_retry(
        function,
        max_retries=2,
        sleep_function=lambda _: None,
        is_retryable=lambda error: True,
    )

    assert (
        result["error"]
        is error
    )
