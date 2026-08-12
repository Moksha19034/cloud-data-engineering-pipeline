import pandas as pd

from src.loading import upsert_posts


def make_posts(post_ids, titles):
    return pd.DataFrame(
        {
            "post_id": post_ids,
            "user_id": list(range(1, len(post_ids) + 1)),
            "title": titles,
            "body": [f"Body for {title}" for title in titles],
            "title_length": [len(title) for title in titles],
            "body_length": [
                len(f"Body for {title}") for title in titles
            ],
            "processed_at": pd.to_datetime(
                ["2026-08-12"] * len(post_ids),
                utc=True,
            ),
        }
    )


def test_upsert_inserts_new_record(tmp_path):
    existing_file = tmp_path / "existing.parquet"
    incoming_file = tmp_path / "incoming.parquet"

    existing = make_posts(
        [1],
        ["Original post"],
    )

    incoming = make_posts(
        [2],
        ["New post"],
    )

    existing.to_parquet(existing_file, index=False)
    incoming.to_parquet(incoming_file, index=False)

    upsert_posts.EXISTING_FILE = existing_file
    upsert_posts.INCOMING_FILE = incoming_file

    upsert_posts.upsert_posts()

    result = pd.read_parquet(existing_file)

    assert len(result) == 2
    assert 2 in result["post_id"].values


def test_upsert_updates_existing_record(tmp_path):
    existing_file = tmp_path / "existing.parquet"
    incoming_file = tmp_path / "incoming.parquet"

    existing = make_posts(
        [1],
        ["Original post"],
    )

    incoming = make_posts(
        [1],
        ["Updated post"],
    )

    existing.to_parquet(existing_file, index=False)
    incoming.to_parquet(incoming_file, index=False)

    upsert_posts.EXISTING_FILE = existing_file
    upsert_posts.INCOMING_FILE = incoming_file

    upsert_posts.upsert_posts()

    result = pd.read_parquet(existing_file)

    assert len(result) == 1
    assert result.loc[0, "title"] == "Updated post"


def test_upsert_handles_update_and_insert(tmp_path):
    existing_file = tmp_path / "existing.parquet"
    incoming_file = tmp_path / "incoming.parquet"

    existing = make_posts(
        [1, 2],
        ["Original 1", "Original 2"],
    )

    incoming = make_posts(
        [2, 3],
        ["Updated 2", "New 3"],
    )

    existing.to_parquet(existing_file, index=False)
    incoming.to_parquet(incoming_file, index=False)

    upsert_posts.EXISTING_FILE = existing_file
    upsert_posts.INCOMING_FILE = incoming_file

    upsert_posts.upsert_posts()

    result = pd.read_parquet(existing_file)

    assert len(result) == 3
    assert result["post_id"].is_unique

    assert result.loc[
        result["post_id"] == 2, "title"
    ].iloc[0] == "Updated 2"

    assert 3 in result["post_id"].values


def test_upsert_creates_file_on_first_run(tmp_path):
    existing_file = tmp_path / "existing.parquet"
    incoming_file = tmp_path / "incoming.parquet"

    incoming = make_posts(
        [1, 2],
        ["First post", "Second post"],
    )

    incoming.to_parquet(incoming_file, index=False)

    upsert_posts.EXISTING_FILE = existing_file
    upsert_posts.INCOMING_FILE = incoming_file

    upsert_posts.upsert_posts()

    result = pd.read_parquet(existing_file)

    assert len(result) == 2
    assert result["post_id"].is_unique
