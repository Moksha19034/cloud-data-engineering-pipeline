import pandas as pd
from pathlib import Path


EXISTING_FILE = Path("data/curated/posts.parquet")
INCOMING_FILE = Path("data/staging/posts.parquet")


def upsert_posts():
    print("Starting upsert...")

    incoming = pd.read_parquet(INCOMING_FILE)

    print(f"Incoming records: {len(incoming)}")

    # First-run handling.
    if not EXISTING_FILE.exists():
        EXISTING_FILE.parent.mkdir(parents=True, exist_ok=True)

        incoming.to_parquet(
            EXISTING_FILE,
            index=False,
        )

        print("No existing curated dataset found.")
        print("Created curated dataset from incoming data.")
        print(f"Final records: {len(incoming)}")
        print("Upsert completed successfully.")

        return

    # Normal incremental load.
    existing = pd.read_parquet(EXISTING_FILE)

    print(f"Existing records: {len(existing)}")

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





