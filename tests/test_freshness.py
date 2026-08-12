from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

from src.validation.validate_posts import validate_freshness


def test_fresh_data_passes():
    now = datetime.now(timezone.utc)

    df = pd.DataFrame({
        "processed_at": [
            now - timedelta(hours=1),
            now - timedelta(hours=2),
        ]
    })

    validate_freshness(df)


def test_stale_data_fails():
    now = datetime.now(timezone.utc)

    df = pd.DataFrame({
        "processed_at": [
            now - timedelta(hours=25),
        ]
    })

    with pytest.raises(ValueError, match="Data freshness SLA violated"):
        validate_freshness(df)


def test_data_at_freshness_limit_passes():
    now = datetime.now(timezone.utc)

    df = pd.DataFrame({
        "processed_at": [
            now - timedelta(hours=23, minutes=59),
        ]
    })

    validate_freshness(df)
