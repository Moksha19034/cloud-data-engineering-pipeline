import pandas as pd
from pathlib import Path


EXISTING_FILE = Path("data/curated/posts.parquet")
INCOMING_FILE = Path("data/staging/posts.parquet")


def upsert_posts():
    print("Starting upsert...")

    incoming = pd.read_parquet(INCOMING_FILE)

    print(f"Incoming records: {len(incoming)}")

    # First-run handling.
    # If the curated dataset does not exist yet,
    # create it directly from the incoming staging data.
    if not EXISTING_FILE.exists():
        EXISTING_FILE.parent.mkdir(parents=True, exist_ok=True)

        incoming.to_parquet(
            EXISTING_FILE,
            index=False,
        )

        print("No existing curated dataset found.")
        print("Created curated dataset from incoming data.")
        print(f"Records inserted: {len(incoming)}")
        print("Records updated: 0")
        print("Records unchanged: 0")
        print(f"Final records: {len(incoming)}")
        print("Upsert completed successfully.")

        return

    # Normal incremental load.
    existing = pd.read_parquet(EXISTING_FILE)

    print(f"Existing records: {len(existing)}")

    existing_indexed = existing.set_index("post_id")
    incoming_indexed = incoming.set_index("post_id")

    # Records that exist in both datasets.
    common_ids = existing_indexed.index.intersection(
        incoming_indexed.index
    )

    # Records that exist only in incoming data.
    new_ids = incoming_indexed.index.difference(
        existing_indexed.index
    )

    # Determine which common records actually changed.
    updated_ids = []

    for post_id in common_ids:
        existing_record = existing_indexed.loc[post_id]
        incoming_record = incoming_indexed.loc[post_id]

        if not existing_record.equals(incoming_record):
            updated_ids.append(post_id)

    updated_count = len(updated_ids)
    inserted_count = len(new_ids)
    unchanged_count = len(common_ids) - updated_count

    print(f"Records updated: {updated_count}")
    print(f"Records inserted: {inserted_count}")
    print(f"Records unchanged: {unchanged_count}")

    # Update existing records.
    existing_indexed.update(
        incoming_indexed.loc[common_ids]
    )

    # Add new records.
    new_records = incoming_indexed.loc[new_ids]

    result = pd.concat(
        [existing_indexed, new_records]
    ).reset_index()

    # Keep records ordered by post_id.
    result = result.sort_values("post_id")

    # Save the updated curated dataset.
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



