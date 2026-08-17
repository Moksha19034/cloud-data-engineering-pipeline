import logging
from pathlib import Path


LOG_DIR = Path("logs")

LOG_FILE = LOG_DIR / "pipeline.log"


class RunContextFilter(logging.Filter):
    """
    Adds run_id and stage to every log record.
    """

    def __init__(
        self,
        run_id="-",
        stage="-",
    ):
        super().__init__()

        self.run_id = run_id
        self.stage = stage

    def filter(self, record):
        record.run_id = self.run_id
        record.stage = self.stage

        return True


def get_logger(
    name="pipeline",
    run_id="-",
    stage="-",
):
    """
    Create and configure a pipeline logger.
    """

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger = logging.getLogger(name)

    logger.setLevel(logging.INFO)

    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | "
        "%(levelname)s | "
        "run_id=%(run_id)s | "
        "stage=%(stage)s | "
        "%(message)s"
    )

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(
        formatter
    )

    file_handler = logging.FileHandler(
        LOG_FILE
    )

    file_handler.setFormatter(
        formatter
    )

    context_filter = RunContextFilter(
        run_id=run_id,
        stage=stage,
    )

    console_handler.addFilter(
        context_filter
    )

    file_handler.addFilter(
        context_filter
    )

    logger.addHandler(
        console_handler
    )

    logger.addHandler(
        file_handler
    )

    logger.propagate = False

    return logger
