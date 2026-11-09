import logging
from pathlib import Path

import pytest

from log import configure_log


@pytest.fixture
def root_logger(monkeypatch):
    root = logging.getLogger()
    level = root.level
    # force=True закрывает прежние обработчики, в том числе обработчики pytest.
    monkeypatch.setattr(root, "handlers", [])
    try:
        yield root
    finally:
        for handler in root.handlers:
            handler.close()
        root.setLevel(level)


def test_reconfigure_writes_each_message_once(tmp_path, root_logger, capsys):
    path = tmp_path / "nested" / "check.log"
    configure_log(path)
    root_logger.info("Начало проверки")
    assert configure_log(path) == path
    root_logger.warning("Результат проверки")

    for output in (path.read_text(encoding="utf-8"), capsys.readouterr().err):
        assert output.count("Начало проверки") == 1
        assert output.count("Результат проверки") == 1


def test_default_creates_new_log_per_run(tmp_path, monkeypatch, root_logger):
    monkeypatch.chdir(tmp_path)
    first = configure_log()
    second = configure_log()
    assert first != second
    assert first.parent == second.parent == Path("logs")
    assert first.is_file() and second.is_file()


def test_invalid_log_directory(tmp_path):
    file = tmp_path / "ordinary-file"
    file.touch()
    with pytest.raises(OSError):
        configure_log(file / "check.log")
