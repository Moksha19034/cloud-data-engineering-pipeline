from enum import Enum


class FailureType(Enum):
    RETRYABLE = "RETRYABLE"
    NON_RETRYABLE = "NON_RETRYABLE"
    UNKNOWN = "UNKNOWN"


RETRYABLE_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
)


NON_RETRYABLE_EXCEPTIONS = (
    ValueError,
    TypeError,
    KeyError,
    FileNotFoundError,
)


def classify_failure(error):
    """
    Classify a pipeline exception into a
    retryable, non-retryable, or unknown failure.
    """

    if isinstance(
        error,
        RETRYABLE_EXCEPTIONS,
    ):
        return FailureType.RETRYABLE

    if isinstance(
        error,
        NON_RETRYABLE_EXCEPTIONS,
    ):
        return FailureType.NON_RETRYABLE

    return FailureType.UNKNOWN


def is_retryable(error):
    """
    Return True when the failure is considered
    safe to retry.
    """

    return (
        classify_failure(error)
        == FailureType.RETRYABLE
    )


def get_failure_category(error):
    """
    Return the string representation of the
    failure category.
    """

    return classify_failure(
        error
    ).value


def main():
    print(
        "Pipeline failure classifier ready."
    )


if __name__ == "__main__":
    main()
