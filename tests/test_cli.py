import os
from pathlib import Path
import subprocess
import sys

import pytest


MAIN = Path(__file__).resolve().parents[1] / "main.py"


@pytest.mark.parametrize(("body", "timeout", "exit_code", "message"), [
    ("assert True", 20, 0, "Тесты прошли"),
    ("assert False", 20, 1, "pytest завершился с кодом 1"),
    (None, 20, 1, "Тесты не найдены"),
    ("import time\n    time.sleep(30)", 1, 1, "Истёк таймаут"),
])
def test_check_target_project(tmp_path, body, timeout, exit_code, message):
    project = tmp_path / "web app"
    project.mkdir()
    if body is not None:
        (project / "test_demo.py").write_text(
            f"def test_demo():\n    {body}\n", encoding="utf-8"
        )

    result = subprocess.run(
        [sys.executable, str(MAIN), "check", "--only", "tests",
         "--project", project.name,
         "--python", os.path.relpath(sys.executable, tmp_path),
         "--test-timeout", str(timeout), "--log-file", "logs/check.log"],
        cwd=tmp_path, capture_output=True, text=True, timeout=30,
    )

    assert result.returncode == exit_code, result.stderr
    assert message in result.stderr
    journal = (tmp_path / "logs/check.log").read_text(encoding="utf-8")
    assert "Запуск pytest" in journal
    assert message in journal
