import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from pytest_runner import CheckError, run_tests


def test_runs_selected_interpreter_in_project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    project = tmp_path / "web app"
    project.mkdir()
    python = Path(".venv/bin/python")

    with patch("pytest_runner.subprocess.run") as launch:
        launch.return_value.returncode = 0
        assert run_tests(project, python, 15) is None

    launch.assert_called_once_with(
        [str(tmp_path / python), "-m", "pytest"], cwd=project, timeout=15
    )


def test_missing_project_stops_before_launch(tmp_path):
    with patch("pytest_runner.subprocess.run") as launch:
        with pytest.raises(CheckError, match="Каталог проекта не найден"):
            run_tests(tmp_path / "missing", Path("python"), 10)
    launch.assert_not_called()


@pytest.mark.parametrize(("code", "message"), [
    (5, "Тесты не найдены"),
    (1, "pytest завершился с кодом 1"),
])
def test_unsuccessful_pytest_result(tmp_path, code, message):
    with patch("pytest_runner.subprocess.run") as launch:
        launch.return_value.returncode = code
        with pytest.raises(CheckError, match=message):
            run_tests(tmp_path, Path("python"), 10)


@pytest.mark.parametrize(("cause", "message"), [
    (FileNotFoundError("python"), "Не удалось запустить Python"),
    (subprocess.TimeoutExpired("pytest", 10), "Истёк таймаут pytest"),
])
def test_process_errors_keep_original_cause(tmp_path, cause, message):
    with patch("pytest_runner.subprocess.run", side_effect=cause):
        with pytest.raises(CheckError, match=message) as error:
            run_tests(tmp_path, Path("python"), 10)
    assert error.value.__cause__ is cause
