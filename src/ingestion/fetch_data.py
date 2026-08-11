import json
from datetime import datetime, timezone
from pathlib import Path

import requests


API_URL = "https://jsonplaceholder.typicode.com/posts"


def fetch_data():
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()
    return response.json()


def save_raw_data(data):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"posts_{timestamp}.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    print(f"Raw data saved to: {output_file}")


def main():
    print("Starting data ingestion...")

    data = fetch_data()

    print(f"Records received: {len(data)}")

    save_raw_data(data)

    print("Ingestion completed successfully.")


if __name__ == "__main__":
    main()
