from pathlib import Path

from src.logging.pipeline_logger import (
    LOG_FILE,
    LOG_DIR,
    RunContextFilter,
    get_logger,
)


def test_log_directory_is_defined():
    assert isinstance(
        LOG_DIR,
        Path,
    )


def test_log_file_is_defined():
    assert isinstance(
        LOG_FILE,
        Path,
    )


def test_context_filter_adds_run_id_and_stage():
    import logging

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    context_filter = RunContextFilter(
        run_id="run-001",
        stage="TEST",
    )

    result = context_filter.filter(
        record
    )

    assert result is True
    assert record.run_id == "run-001"
    assert record.stage == "TEST"


def test_get_logger_returns_logger():
    import logging

    logger = get_logger(
        name="test_logger",
        run_id="run-001",
        stage="TEST",
    )

    assert isinstance(
        logger,
        logging.Logger,
    )


def test_logger_has_handlers():
    logger = get_logger(
        name="test_handler_logger",
        run_id="run-002",
        stage="TEST",
    )

    assert len(logger.handlers) == 2


def test_logger_can_write_message(tmp_path, monkeypatch):
    import src.logging.pipeline_logger as pipeline_logger

    test_log_dir = tmp_path / "logs"

    test_log_file = (
        test_log_dir / "pipeline.log"
    )

    monkeypatch.setattr(
        pipeline_logger,
        "LOG_DIR",
        test_log_dir,
    )

    monkeypatch.setattr(
        pipeline_logger,
        "LOG_FILE",
        test_log_file,
    )

    logger = pipeline_logger.get_logger(
        name="test_write_logger",
        run_id="run-003",
        stage="TEST",
    )

    logger.info(
        "Test logging message"
    )

    for handler in logger.handlers:
        handler.flush()

    assert test_log_file.exists()

    content = test_log_file.read_text()

    assert "run-003" in content
    assert "TEST" in content
    assert "Test logging message" in content
