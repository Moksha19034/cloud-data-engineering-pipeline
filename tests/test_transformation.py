from pathlib import Path

import pandas as pd

from src.transformation.transform_posts import (
    transform_data,
    validate_data,
)


def create_test_data():
    return [
        {
            "userId": 1,
            "id": 101,
            "title": "Test title",
            "body": "Test body",
        },
        {
            "userId": 2,
            "id": 102,
            "title": "Another title",
            "body": "Another test body",
        },
    ]


def load_transformed_data():
    data = create_test_data()
    source_file = Path("test_posts.json")

    df = transform_data(data, source_file)

    validate_data(df)

    return df


def test_transformed_posts_have_expected_columns():
    df = load_transformed_data()

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
    df = load_transformed_data()

    assert (df["title_length"] == df["title"].str.len()).all()


def test_body_length_is_correct():
    df = load_transformed_data()

    assert (df["body_length"] == df["body"].str.len()).all()


def test_source_system_is_correct():
    df = load_transformed_data()

    assert (df["source_system"] == "jsonplaceholder_api").all()


def test_source_file_is_populated():
    df = load_transformed_data()

    assert df["source_file"].notna().all()
    assert (df["source_file"].str.len() > 0).all()
