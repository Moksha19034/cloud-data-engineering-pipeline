import pandas as pd
import pytest

from src.validation.validate_posts import (
    validate_required_columns,
    validate_not_empty,
    validate_unique_post_ids,
    validate_nulls,
    validate_lengths,
)


def valid_dataframe():
    return pd.DataFrame(
        {
            "user_id": [1, 2],
            "post_id": [101, 102],
            "title": ["Hello", "World"],
            "body": ["First post", "Second post"],
            "title_length": [5, 5],
            "body_length": [10, 11],
            "processed_at": pd.to_datetime(
                ["2026-08-12", "2026-08-12"],
                utc=True,
            ),
        }
    )


def test_required_columns_pass():
    df = valid_dataframe()

    validate_required_columns(df)


def test_missing_column_fails():
    df = valid_dataframe().drop(
        columns=["body"]
    )

    with pytest.raises(
        ValueError,
        match="Missing columns",
    ):
        validate_required_columns(df)


def test_duplicate_post_id_fails():
    df = valid_dataframe()

    df.loc[1, "post_id"] = 101

    with pytest.raises(
        ValueError,
        match="Duplicate post_id",
    ):
        validate_unique_post_ids(df)


def test_null_required_value_fails():
    df = valid_dataframe()

    df.loc[0, "title"] = None

    with pytest.raises(
        ValueError,
        match="Null values found",
    ):
        validate_nulls(df)


def test_incorrect_title_length_fails():
    df = valid_dataframe()

    df.loc[0, "title_length"] = 999

    with pytest.raises(
        ValueError,
        match="title_length values are incorrect",
    ):
        validate_lengths(df)


def test_incorrect_body_length_fails():
    df = valid_dataframe()

    df.loc[0, "body_length"] = 999

    with pytest.raises(
        ValueError,
        match="body_length values are incorrect",
    ):
        validate_lengths(df)


def test_empty_dataframe_fails():
    df = valid_dataframe().iloc[0:0]

    with pytest.raises(
        ValueError,
        match="Dataset is empty",
    ):
        validate_not_empty(df)


def test_quality_metrics_can_be_generated_from_valid_dataframe():
    from src.validation.quality_metrics import (
        get_quality_metrics,
    )

    df = valid_dataframe()

    metrics = get_quality_metrics(df)

    assert metrics["records_checked"] == 2
    assert metrics["null_values"] == 0
    assert metrics["duplicate_post_ids"] == 0
    assert metrics["quality_status"] == "PASSED"


def test_validation_main_returns_quality_metrics(
    monkeypatch,
    tmp_path,
):
    from src.validation import validate_posts
    from src.validation import quality_metrics

    df = valid_dataframe()

    metrics_file = (
        tmp_path
        / "quality_metrics.json"
    )

    monkeypatch.setattr(
        validate_posts,
        "load_data",
        lambda: df,
    )

    monkeypatch.setattr(
        quality_metrics,
        "QUALITY_METRICS_FILE",
        metrics_file,
    )

    result = validate_posts.main()

    assert (
        result["quality_metrics"][
            "records_checked"
        ]
        == 2
    )

    assert (
        result["quality_metrics"][
            "null_values"
        ]
        == 0
    )

    assert (
        result["quality_metrics"][
            "duplicate_post_ids"
        ]
        == 0
    )

    assert (
        result["quality_metrics"][
            "quality_status"
        ]
        == "PASSED"
    )
