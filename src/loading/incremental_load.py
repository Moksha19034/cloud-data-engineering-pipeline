import pandas as pd
from pathlib import Path


EXISTING_FILE = Path("data/curated/posts.parquet")
INCOMING_FILE = Path("/tmp/new_posts.parquet")


def incremental_load():
    print("Starting incremental load...")

    existing = pd.read_parquet(EXISTING_FILE)
    incoming = pd.read_parquet(INCOMING_FILE)

    print(f"Existing records: {len(existing)}")
    print(f"Incoming records: {len(incoming)}")

    existing_ids = set(existing["post_id"])

    new_records = incoming[
        ~incoming["post_id"].isin(existing_ids)
    ].copy()

    print(f"New records detected: {len(new_records)}")

    if new_records.empty:
        print("No new records to load.")
        return

    updated = pd.concat(
        [existing, new_records],
        ignore_index=True,
    )

    updated = updated.drop_duplicates(
        subset=["post_id"],
        keep="first",
    )

    updated.to_parquet(
        EXISTING_FILE,
        index=False,
    )

    print(f"Records added: {len(new_records)}")
    print(f"Total records after load: {len(updated)}")
    print(f"Updated dataset: {EXISTING_FILE}")


def main():
    incremental_load()


if __name__ == "__main__":
    main()
