from pathlib import Path
import subprocess


class CheckError(Exception):
    """Ошибка запуска pytest или неуспешный результат проверки."""


def run_tests(project: Path, python: Path, timeout: int) -> None:
    """Запускает pytest в окружении проверяемого проекта.

    Args:
        project: Рабочий каталог для pytest. В нём выполняется поиск тестов.
        python: Абсолютный путь к интерпретатору или путь от каталога запуска
            CLI. Может указывать на Python из виртуального окружения.
        timeout: Максимальное время выполнения в секундах.

    Returns:
        None при успешном завершении pytest.

    Raises:
        CheckError: Каталог проекта недоступен, процесс не запустился,
            истёк таймаут или pytest вернул ненулевой код. Отсутствие
            собранных тестов также считается ошибкой.
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
