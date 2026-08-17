from pathlib import Path

from src.config import settings


def test_environment_has_default():
    assert settings.ENVIRONMENT


def test_api_urls_exist():
    assert settings.POSTS_API_URL
    assert settings.USERS_API_URL


def test_retry_configuration():
    assert settings.MAX_RETRIES >= 0
    assert settings.INITIAL_RETRY_DELAY >= 0


def test_data_freshness_configuration():
    assert settings.DATA_FRESHNESS_HOURS > 0


def test_data_directories_are_defined():
    assert isinstance(
        settings.DATA_DIR,
        Path,
    )

    assert isinstance(
        settings.RAW_DIR,
        Path,
    )

    assert isinstance(
        settings.STAGING_DIR,
        Path,
    )

    assert isinstance(
        settings.CURATED_DIR,
        Path,
    )

    assert isinstance(
        settings.AUDIT_DIR,
        Path,
    )


def test_audit_files_are_defined():
    assert isinstance(
        settings.PIPELINE_AUDIT_FILE,
        Path,
    )

    assert isinstance(
        settings.STAGE_AUDIT_FILE,
        Path,
    )

    assert isinstance(
        settings.QUALITY_METRICS_FILE,
        Path,
    )

    assert isinstance(
        settings.ALERT_FILE,
        Path,
    )


def test_paths_are_inside_project():
    assert (
        settings.DATA_DIR.parent
        == settings.PROJECT_ROOT
    )


def test_ensure_directories(tmp_path, monkeypatch):
    raw_dir = tmp_path / "raw"
    staging_dir = tmp_path / "staging"
    curated_dir = tmp_path / "curated"
    audit_dir = tmp_path / "audit"

    monkeypatch.setattr(
        settings,
        "RAW_DIR",
        raw_dir,
    )

    monkeypatch.setattr(
        settings,
        "STAGING_DIR",
        staging_dir,
    )

    monkeypatch.setattr(
        settings,
        "CURATED_DIR",
        curated_dir,
    )

    monkeypatch.setattr(
        settings,
        "AUDIT_DIR",
        audit_dir,
    )

    settings.ensure_directories()

    assert raw_dir.exists()
    assert staging_dir.exists()
    assert curated_dir.exists()
    assert audit_dir.exists()


def test_ensure_directories_are_directories(
    tmp_path,
    monkeypatch,
):
    raw_dir = tmp_path / "raw"
    staging_dir = tmp_path / "staging"
    curated_dir = tmp_path / "curated"
    audit_dir = tmp_path / "audit"

    monkeypatch.setattr(
        settings,
        "RAW_DIR",
        raw_dir,
    )

    monkeypatch.setattr(
        settings,
        "STAGING_DIR",
        staging_dir,
    )

    monkeypatch.setattr(
        settings,
        "CURATED_DIR",
        curated_dir,
    )

    monkeypatch.setattr(
        settings,
        "AUDIT_DIR",
        audit_dir,
    )

    settings.ensure_directories()

    assert raw_dir.is_dir()
    assert staging_dir.is_dir()
    assert curated_dir.is_dir()
    assert audit_dir.is_dir()

