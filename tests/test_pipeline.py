import logging

import pytest

from run_pipeline import run_stage


def test_run_stage_success(tmp_path, caplog):
    script = tmp_path / "success.py"
    script.write_text("print('success')")

    with caplog.at_level(logging.INFO):
        run_stage("TEST SUCCESS", str(script))

    assert "Stage completed | stage=TEST SUCCESS" in caplog.text
    assert "duration=" in caplog.text


def test_run_stage_failure(tmp_path, caplog):
    script = tmp_path / "failure.py"
    script.write_text("raise SystemExit(7)")

    with caplog.at_level(logging.ERROR):
        with pytest.raises(
            RuntimeError,
            match="TEST FAILURE failed \\(exit code 7\\)",
        ):
            run_stage("TEST FAILURE", str(script))

    assert "Stage failed | stage=TEST FAILURE" in caplog.text
    assert "exit_code=7" in caplog.text
    assert "duration=" in caplog.text


def test_run_stage_missing_script(tmp_path, caplog):
    script = tmp_path / "does_not_exist.py"

    with caplog.at_level(logging.ERROR):
        with pytest.raises(
            RuntimeError,
            match="MISSING SCRIPT failed \\(exit code 2\\)",
        ):
            run_stage("MISSING SCRIPT", str(script))

    assert "Stage failed | stage=MISSING SCRIPT" in caplog.text
    assert "exit_code=2" in caplog.text
