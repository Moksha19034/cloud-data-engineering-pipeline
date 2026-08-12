import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)


load_dotenv()


def get_int_config(name, default):
    value = os.getenv(name, str(default))

    try:
        return int(value)
    except ValueError:
        raise ValueError(
            f"Invalid configuration: {name} must be an integer"
        )


API_URL = os.getenv("API_URL")
API_TIMEOUT = get_int_config("API_TIMEOUT", 30)
RETRY_ATTEMPTS = get_int_config("RETRY_ATTEMPTS", 3)
RETRY_MIN_WAIT = get_int_config("RETRY_MIN_WAIT", 2)
RETRY_MAX_WAIT = get_int_config("RETRY_MAX_WAIT", 10)


LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "ingestion.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


def is_retryable_error(error):
    """
    Return True when an error represents a temporary
    failure that should be retried.
    """

    if isinstance(
        error,
        (
            requests.ConnectionError,
            requests.Timeout,
        ),
    ):
        return True

    if isinstance(error, requests.HTTPError):
        response = error.response

        if response is None:
            return False

        return response.status_code in {
            429,
            500,
            502,
            503,
            504,
        }

    return False


@retry(
    retry=retry_if_exception(is_retryable_error),
    stop=stop_after_attempt(RETRY_ATTEMPTS),
    wait=wait_exponential(
        multiplier=1,
        min=RETRY_MIN_WAIT,
        max=RETRY_MAX_WAIT,
    ),
    before_sleep=before_sleep_log(
        logger,
        logging.WARNING,
    ),
    reraise=True,
)
def fetch_data():
    logger.info("Starting API request")

    response = requests.get(
        API_URL,
        timeout=API_TIMEOUT,
    )

    response.raise_for_status()

    logger.info("API request successful")

    return response.json()


def validate_data(data):
    if not isinstance(data, list):
        raise ValueError("Expected API response to be a list")

    if len(data) == 0:
        raise ValueError("API returned zero records")

    logger.info(
        "Data validation successful | records=%s",
        len(data),
    )


def save_raw_data(data):
    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S"
    )

    output_dir = Path("data/raw")
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = output_dir / f"posts_{timestamp}.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    logger.info(
        "Raw data saved | file=%s",
        output_file,
    )

    print(f"Raw data saved to: {output_file}")


def main():
    try:
        logger.info(
            "========== INGESTION STARTED =========="
        )

        if not API_URL:
            raise ValueError(
                "API_URL is missing from .env"
            )

        data = fetch_data()

        logger.info(
            "Records received | count=%s",
            len(data),
        )

        validate_data(data)

        save_raw_data(data)

        logger.info(
            "========== INGESTION COMPLETED =========="
        )

        print("Ingestion completed successfully.")

    except Exception as error:
        logger.exception(
            "Pipeline failed | error=%s",
            error,
        )

        print(f"Ingestion failed: {error}")

        raise


if __name__ == "__main__":
    main()
