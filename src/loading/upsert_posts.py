import pandas as pd
from pathlib import Path


EXISTING_FILE = Path("data/curated/posts.parquet")
INCOMING_FILE = Path("/tmp/upsert_posts.parquet")


def upsert_posts():
    print("Starting upsert...")

    existing = pd.read_parquet(EXISTING_FILE)
    incoming = pd.read_parquet(INCOMING_FILE)

    print(f"Existing records: {len(existing)}")
    print(f"Incoming records: {len(incoming)}")

    existing_indexed = existing.set_index("post_id")
    incoming_indexed = incoming.set_index("post_id")

    common_ids = existing_indexed.index.intersection(
        incoming_indexed.index
    )

    new_ids = incoming_indexed.index.difference(
        existing_indexed.index
    )

    print(f"Existing records to update: {len(common_ids)}")
    print(f"New records to insert: {len(new_ids)}")

    # Update existing records.
    existing_indexed.update(
        incoming_indexed.loc[common_ids]
    )

    # Add new records.
    new_records = incoming_indexed.loc[new_ids]

    result = pd.concat(
        [existing_indexed, new_records]
    ).reset_index()

    result = result.sort_values("post_id")

    result.to_parquet(
        EXISTING_FILE,
        index=False,
    )

    print(f"Final records: {len(result)}")
    print("Upsert completed successfully.")


def main():
    upsert_posts()


if __name__ == "__main__":
    main()
