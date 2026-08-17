import time


DEFAULT_MAX_RETRIES = 3
DEFAULT_INITIAL_DELAY = 1.0


def calculate_backoff(
    retry_number,
    initial_delay=DEFAULT_INITIAL_DELAY,
):
    """
    Calculate exponential backoff delay.

    Retry 1 -> 1 second
    Retry 2 -> 2 seconds
    Retry 3 -> 4 seconds
    """

    if retry_number < 1:
        raise ValueError(
            "retry_number must be >= 1"
        )

    return initial_delay * (
        2 ** (retry_number - 1)
    )


def execute_with_retry(
    function,
    max_retries=DEFAULT_MAX_RETRIES,
    initial_delay=DEFAULT_INITIAL_DELAY,
    sleep_function=time.sleep,
    is_retryable=None,
):
    """
    Execute a function and retry retryable
    failures using exponential backoff.

    Returns execution metadata.

    The function is attempted once initially,
    followed by at most max_retries retries.
    """

    if max_retries < 0:
        raise ValueError(
            "max_retries must be >= 0"
        )

    if initial_delay < 0:
        raise ValueError(
            "initial_delay must be >= 0"
        )

    attempts = 0
    retry_count = 0

    while True:

        attempts += 1

        try:

            result = function()

            return {
                "status": "SUCCESS",
                "result": result,
                "attempts": attempts,
                "retries": retry_count,
                "error": None,
            }

        except Exception as error:

            if is_retryable is not None:

                retryable = is_retryable(
                    error
                )

            else:

                retryable = True

            if not retryable:

                return {
                    "status": "FAILED",
                    "result": None,
                    "attempts": attempts,
                    "retries": retry_count,
                    "error": error,
                }

            if retry_count >= max_retries:

                return {
                    "status": "FAILED",
                    "result": None,
                    "attempts": attempts,
                    "retries": retry_count,
                    "error": error,
                }

            retry_count += 1

            delay = calculate_backoff(
                retry_count,
                initial_delay,
            )

            sleep_function(delay)


def main():
    print(
        "Retry engine ready."
    )


if __name__ == "__main__":
    main()

