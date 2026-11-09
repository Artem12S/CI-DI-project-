from pathlib import Path
import subprocess


class CheckError(Exception):
    """Ошибка запуска pytest или неуспешный результат проверки."""


def run_tests(project: Path, python: Path, timeout: int) -> None:
    """Запускает pytest в окружении проверяемого проекта.

    Args:
        project: Рабочий каталог для pytest.
        python: Путь к интерпретатору относительно каталога запуска CLI.
        timeout: Максимальное время выполнения в секундах.

    Raises:
        CheckError: Проект недоступен, процесс не запустился или тесты
            не завершились успешно.
    """
    project = project.expanduser()
    if not project.is_dir():
        raise CheckError(f"Каталог проекта не найден: {project}")

    # resolve() раскроет ссылку из venv и может выбрать системное окружение.
    interpreter = python.expanduser().absolute()
    try:
        result = subprocess.run([str(interpreter), "-m", "pytest"],
                                cwd=project, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise CheckError(f"Истёк таймаут pytest ({timeout} с)") from exc
    except OSError as exc:
        raise CheckError(f"Не удалось запустить Python: {exc}") from exc

    if result.returncode == 5:
        raise CheckError("Тесты не найдены")
    if result.returncode:
        raise CheckError(f"pytest завершился с кодом {result.returncode}")
