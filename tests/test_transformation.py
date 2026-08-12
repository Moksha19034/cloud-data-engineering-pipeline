import pandas as pd


def test_transformed_posts_have_expected_columns():
    df = pd.read_parquet("data/staging/posts.parquet")

    expected_columns = {
        "user_id",
        "post_id",
        "title",
        "body",
        "title_length",
        "body_length",
        "processed_at",
    }

    assert expected_columns.issubset(df.columns)


def test_title_length_is_correct():
    df = pd.read_parquet("data/staging/posts.parquet")

    assert (df["title_length"] == df["title"].str.len()).all()


def test_body_length_is_correct():
    df = pd.read_parquet("data/staging/posts.parquet")

    assert (df["body_length"] == df["body"].str.len()).all()


def test_source_system_is_correct():
    df = pd.read_parquet("data/staging/posts.parquet")

    assert (df["source_system"] == "jsonplaceholder_api").all()


def test_source_file_is_populated():
    df = pd.read_parquet("data/staging/posts.parquet")

    assert df["source_file"].notna().all()
    assert (df["source_file"].str.len() > 0).all()
