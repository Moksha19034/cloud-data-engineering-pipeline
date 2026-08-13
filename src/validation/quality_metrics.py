import json
from pathlib import Path


QUALITY_METRICS_FILE = Path(
    "data/audit/quality_metrics.json"
)


def get_record_count(df):
    """
    Return the number of records checked.
    """

    return len(df)


def get_null_count(df):
    """
    Return the total number of null values
    across the entire dataset.
    """

    if df.empty:
        return 0

    return int(
        df.isnull().sum().sum()
    )


def get_duplicate_post_id_count(df):
    """
    Return the number of duplicate post_id records.
    """

    if (
        df.empty
        or "post_id" not in df.columns
    ):
        return 0

    return int(
        df["post_id"].duplicated().sum()
    )


def get_quality_metrics(df):
    """
    Return structured data-quality metrics.
    """

    records_checked = get_record_count(df)

    null_values = get_null_count(df)

    duplicate_post_ids = (
        get_duplicate_post_id_count(df)
    )

    quality_status = "PASSED"

    if (
        records_checked == 0
        or null_values > 0
        or duplicate_post_ids > 0
    ):
        quality_status = "FAILED"

    return {
        "records_checked": records_checked,
        "null_values": null_values,
        "duplicate_post_ids": duplicate_post_ids,
        "quality_status": quality_status,
    }


def save_quality_metrics(metrics):
    """
    Save the latest quality metrics to disk.
    """

    QUALITY_METRICS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        QUALITY_METRICS_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metrics,
            file,
            indent=2,
        )


def load_quality_metrics():
    """
    Load the latest quality metrics.

    Returns an empty dictionary when no
    metrics file exists.
    """

    if not QUALITY_METRICS_FILE.exists():
        return {}

    with open(
        QUALITY_METRICS_FILE,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)
