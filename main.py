import argparse
import logging
from pathlib import Path
import sys
from time import monotonic

from log import configure_log
from pytest_runner import CheckError, run_tests


def main() -> int:
    """Читает аргументы из sys.argv, открывает журнал и запускает проверку.

    Returns:
        0 при успехе, 1 при ошибке журнала или проверки, 130 при прерывании
        вызова run_tests пользователем.

    Raises:
        SystemExit: argparse завершает разбор с кодом 2 при ошибке аргументов
            или с кодом 0 при запросе справки.
    """
    parser = argparse.ArgumentParser(description="Проверка Python-проекта")
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check", help="проверить проект")
    check.add_argument("--only", choices=["tests"], required=True,
                       help="вид проверки")
    check.add_argument("--project", type=Path, default=Path.cwd(),
                       help="каталог проверяемого проекта")
    check.add_argument("--python", type=Path, default=Path(sys.executable),
                       help="путь к Python проверяемого проекта")
    check.add_argument("--test-timeout", type=int, default=300,
                       help="время на pytest в секундах (по умолчанию 300)")
    check.add_argument("--log-file", type=Path, help="путь к журналу запуска")
    args = parser.parse_args()
    if args.test_timeout <= 0:
        check.error("--test-timeout должен быть положительным")

    try:
        log_path = configure_log(args.log_file)
    except OSError as exc:
        print(f"Не удалось открыть журнал: {exc}", file=sys.stderr)
        return 1

    logger = logging.getLogger(__name__)
    logger.info("Журнал: %s", log_path)
    logger.info("Запуск pytest в %s", args.project)
    start = monotonic()
    try:
        run_tests(args.project, args.python, args.test_timeout)
    except CheckError as exc:
        logger.error("Проверка остановлена через %.1f с: %s",
                     monotonic() - start, exc)
        return 1
    except KeyboardInterrupt:
        logger.warning("Проверка прервана пользователем")
        return 130
    logger.info("Тесты прошли за %.1f с", monotonic() - start)
    return 0


if __name__ == "__main__":
    sys.exit(main())
