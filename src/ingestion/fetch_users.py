import json
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

API_URL = "https://jsonplaceholder.typicode.com/users"


def fetch_users():
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()
    return response.json()


def save_raw_users(data):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"users_{timestamp}.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    print(f"Raw users saved to: {output_file}")


def main():
    print("Starting user ingestion...")

    data = fetch_users()

    print(f"Users received: {len(data)}")

    save_raw_users(data)

    print("User ingestion completed successfully.")


if __name__ == "__main__":
    main()
