import logging
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

import main as cli
from pytest_runner import CheckError


@pytest.fixture
def command(monkeypatch):
    monkeypatch.setattr(sys, "argv", [
        "main.py", "check", "--only", "tests", "--project", "web app",
        "--python", "env/bin/python", "--log-file", "check.log",
        "--test-timeout", "15",
    ])
    configure = Mock(return_value=Path("check.log"))
    runner = Mock()
    monkeypatch.setattr(cli, "configure_log", configure)
    monkeypatch.setattr(cli, "run_tests", runner)
    return configure, runner


def test_success_forwards_arguments(command, caplog):
    configure, runner = command
    with caplog.at_level(logging.INFO):
        assert cli.main() == 0
    configure.assert_called_once_with(Path("check.log"))
    runner.assert_called_once_with(Path("web app"), Path("env/bin/python"), 15)
    assert "Тесты прошли" in caplog.text


@pytest.mark.parametrize(("error", "code", "message"), [
    (CheckError("Тесты не найдены"), 1, "Тесты не найдены"),
    (KeyboardInterrupt(), 130, "Проверка прервана пользователем"),
])
def test_runner_failure_is_reported(command, caplog, error, code, message):
    _, runner = command
    runner.side_effect = error
    assert cli.main() == code
    assert message in caplog.text


def test_log_error_stops_check(command, capsys):
    configure, runner = command
    configure.side_effect = OSError("каталог недоступен")
    assert cli.main() == 1
    runner.assert_not_called()
    assert "Не удалось открыть журнал" in capsys.readouterr().err


def test_invalid_timeout_stops_before_setup(command, monkeypatch, capsys):
    configure, runner = command
    monkeypatch.setattr(sys, "argv", [*sys.argv[:-1], "0"])
    with pytest.raises(SystemExit) as error:
        cli.main()
    assert error.value.code == 2
    assert "--test-timeout должен быть положительным" in capsys.readouterr().err
    configure.assert_not_called()
    runner.assert_not_called()
