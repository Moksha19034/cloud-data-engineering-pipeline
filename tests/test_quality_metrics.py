import pandas as pd

from src.validation import quality_metrics


def sample_dataframe():
    return pd.DataFrame(
        {
            "user_id": [1, 2, 3, 4],
            "post_id": [101, 102, 103, 104],
            "title": ["A", "B", "C", "D"],
            "body": [
                "One",
                "Two",
                "Three",
                "Four",
            ],
            "title_length": [1, 1, 1, 1],
            "body_length": [3, 3, 5, 4],
        }
    )


def test_get_record_count():
    df = sample_dataframe()

    assert (
        quality_metrics.get_record_count(df)
        == 4
    )


def test_get_null_count():
    df = sample_dataframe()

    assert (
        quality_metrics.get_null_count(df)
        == 0
    )


def test_get_null_count_with_nulls():
    df = sample_dataframe()

    df.loc[1, "title"] = None

    assert (
        quality_metrics.get_null_count(df)
        == 1
    )


def test_get_duplicate_post_id_count():
    df = sample_dataframe()

    assert (
        quality_metrics
        .get_duplicate_post_id_count(df)
        == 0
    )


def test_get_duplicate_post_id_count_with_duplicates():
    df = sample_dataframe()

    df.loc[3, "post_id"] = 103

    assert (
        quality_metrics
        .get_duplicate_post_id_count(df)
        == 1
    )


def test_get_quality_metrics():
    df = sample_dataframe()

    result = (
        quality_metrics
        .get_quality_metrics(df)
    )

    assert result["records_checked"] == 4
    assert result["null_values"] == 0
    assert result["duplicate_post_ids"] == 0
    assert result["quality_status"] == "PASSED"


def test_quality_metrics_detects_failure():
    df = sample_dataframe()

    df.loc[1, "title"] = None
    df.loc[3, "post_id"] = 103

    result = (
        quality_metrics
        .get_quality_metrics(df)
    )

    assert result["records_checked"] == 4
    assert result["null_values"] == 1
    assert result["duplicate_post_ids"] == 1
    assert result["quality_status"] == "FAILED"


def test_quality_metrics_empty_dataframe():
    df = pd.DataFrame()

    result = (
        quality_metrics
        .get_quality_metrics(df)
    )

    assert result["records_checked"] == 0
    assert result["null_values"] == 0
    assert result["duplicate_post_ids"] == 0
    assert result["quality_status"] == "FAILED"


def test_save_and_load_quality_metrics(
    monkeypatch,
    tmp_path,
):
    metrics_file = (
        tmp_path
        / "quality_metrics.json"
    )

    monkeypatch.setattr(
        quality_metrics,
        "QUALITY_METRICS_FILE",
        metrics_file,
    )

    metrics = {
        "records_checked": 102,
        "null_values": 0,
        "duplicate_post_ids": 0,
        "quality_status": "PASSED",
    }

    quality_metrics.save_quality_metrics(
        metrics
    )

    loaded = (
        quality_metrics
        .load_quality_metrics()
    )

    assert loaded == metrics
