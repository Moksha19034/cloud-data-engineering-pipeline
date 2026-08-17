def should_retry(
    state,
    retry_count,
    max_retries,
):
    """
    Determine whether a failed pipeline run should be retried.

    A retry is allowed only when:
    - previous state exists
    - previous run failed
    - retry count is below the maximum
    """

    if state is None:
        return False

    if state.get("last_status") != "FAILED":
        return False

    if retry_count >= max_retries:
        return False

    return True


def should_skip_run(state):
    """
    Determine whether a pipeline run should be skipped.

    A run is skipped when the previous pipeline state
    indicates a successful completion.
    """

    if state is None:
        return False

    return state.get("last_status") == "SUCCESS"
