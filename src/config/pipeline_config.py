import os


DEFAULT_INTERVAL_MINUTES = 60


def get_pipeline_interval():
    """
    Return the pipeline execution interval in minutes.

    Uses PIPELINE_INTERVAL_MINUTES when it contains
    a positive integer. Otherwise returns the default.
    """

    value = os.getenv(
        "PIPELINE_INTERVAL_MINUTES"
    )

    if value is None:
        return DEFAULT_INTERVAL_MINUTES

    try:
        interval = int(value)

        if interval <= 0:
            return DEFAULT_INTERVAL_MINUTES

        return interval

    except ValueError:
        return DEFAULT_INTERVAL_MINUTES
