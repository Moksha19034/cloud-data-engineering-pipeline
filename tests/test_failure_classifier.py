from src.orchestration import (
    failure_classifier,
)


def test_connection_error_is_retryable():

    error = ConnectionError(
        "API unavailable"
    )

    result = (
        failure_classifier
        .classify_failure(error)
    )

    assert (
        result
        == failure_classifier.FailureType.RETRYABLE
    )


def test_timeout_error_is_retryable():

    error = TimeoutError(
        "Request timed out"
    )

    result = (
        failure_classifier
        .classify_failure(error)
    )

    assert (
        result
        == failure_classifier.FailureType.RETRYABLE
    )


def test_value_error_is_not_retryable():

    error = ValueError(
        "Invalid data"
    )

    result = (
        failure_classifier
        .classify_failure(error)
    )

    assert (
        result
        == failure_classifier.FailureType.NON_RETRYABLE
    )


def test_type_error_is_not_retryable():

    error = TypeError(
        "Invalid type"
    )

    assert (
        failure_classifier.is_retryable(
            error
        )
        is False
    )


def test_unknown_error():

    error = RuntimeError(
        "Unexpected failure"
    )

    result = (
        failure_classifier
        .classify_failure(error)
    )

    assert (
        result
        == failure_classifier.FailureType.UNKNOWN
    )


def test_connection_error_is_retryable_boolean():

    error = ConnectionError(
        "Network failure"
    )

    assert (
        failure_classifier.is_retryable(
            error
        )
        is True
    )


def test_value_error_is_not_retryable_boolean():

    error = ValueError(
        "Bad input"
    )

    assert (
        failure_classifier.is_retryable(
            error
        )
        is False
    )


def test_failure_category():

    error = TimeoutError(
        "Timeout"
    )

    result = (
        failure_classifier
        .get_failure_category(error)
    )

    assert result == "RETRYABLE"
