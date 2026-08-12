import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log


load_dotenv()

API_URL = os.getenv("API_URL")

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "ingestion.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    before_sleep=before_sleep_log(logger, logging.WARNING),
)
def fetch_data():
    logger.info("Starting API request")

    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()

    logger.info("API request successful")

    return response.json()


def validate_data(data):
    if not isinstance(data, list):
        raise ValueError("Expected API response to be a list")

    if len(data) == 0:
        raise ValueError("API returned zero records")

    logger.info("Data validation successful | records=%s", len(data))


def save_raw_data(data):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"posts_{timestamp}.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    logger.info("Raw data saved | file=%s", output_file)

    print(f"Raw data saved to: {output_file}")


def main():
    try:
        logger.info("========== INGESTION STARTED ==========")

        if not API_URL:
            raise ValueError("API_URL is missing from .env")

        data = fetch_data()

        logger.info("Records received | count=%s", len(data))

        validate_data(data)

        save_raw_data(data)

        logger.info("========== INGESTION COMPLETED ==========")

        print("Ingestion completed successfully.")

    except Exception as error:
        logger.exception("Pipeline failed | error=%s", error)
        print(f"Ingestion failed: {error}")
        raise


if __name__ == "__main__":
    main()
