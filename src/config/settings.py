import os
from pathlib import Path

from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]


# =========================================================
# ENVIRONMENT
# =========================================================

ENVIRONMENT = os.getenv(
    "ENVIRONMENT",
    "development",
)


# =========================================================
# API CONFIGURATION
# =========================================================

POSTS_API_URL = os.getenv(
    "POSTS_API_URL",
    "https://jsonplaceholder.typicode.com/posts",
)

USERS_API_URL = os.getenv(
    "USERS_API_URL",
    "https://jsonplaceholder.typicode.com/users",
)


# =========================================================
# RETRY CONFIGURATION
# =========================================================

MAX_RETRIES = int(
    os.getenv(
        "MAX_RETRIES",
        "3",
    )
)

INITIAL_RETRY_DELAY = float(
    os.getenv(
        "INITIAL_RETRY_DELAY",
        "1.0",
    )
)


# =========================================================
# DATA QUALITY CONFIGURATION
# =========================================================

DATA_FRESHNESS_HOURS = int(
    os.getenv(
        "DATA_FRESHNESS_HOURS",
        "24",
    )
)


# =========================================================
# DATA DIRECTORIES
# =========================================================

DATA_DIR = PROJECT_ROOT / "data"

RAW_DIR = DATA_DIR / "raw"

STAGING_DIR = DATA_DIR / "staging"

CURATED_DIR = DATA_DIR / "curated"

AUDIT_DIR = DATA_DIR / "audit"


# =========================================================
# AUDIT FILES
# =========================================================

PIPELINE_AUDIT_FILE = (
    AUDIT_DIR
    / "pipeline_runs.parquet"
)

STAGE_AUDIT_FILE = (
    AUDIT_DIR
    / "pipeline_stage_runs.parquet"
)

QUALITY_METRICS_FILE = (
    AUDIT_DIR
    / "quality_metrics.json"
)

ALERT_FILE = (
    AUDIT_DIR
    / "pipeline_alerts.json"
)


# =========================================================
# HELPER
# =========================================================

def ensure_directories():
    """
    Create required data directories.
    """

    for directory in (
        RAW_DIR,
        STAGING_DIR,
        CURATED_DIR,
        AUDIT_DIR,
    ):
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )
