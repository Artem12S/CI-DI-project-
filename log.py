import logging
from pathlib import Path
from uuid import uuid4


def configure_log(path: Path | None = None) -> Path:
    """Настраивает корневой логгер CLI для записи в UTF-8 и вывода в stderr.

    Каждый вызов заменяет обработчики корневого логгера. Если файл уже
    существует, новые сообщения добавляются в конец.

    Args:
        path: Путь к журналу. Родительские каталоги создаются при открытии.
            По умолчанию каждый вызов создаёт отдельный файл в logs/ внутри
            текущего каталога.

    Returns:
        Путь к открытому журналу.

    Raises:
        OSError: Если каталог или файл недоступен для записи.
    """
    if path is None:
        path = Path("logs") / f"run-{uuid4().hex}.log"
    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(path, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s"
    ))
    logging.basicConfig(level=logging.INFO, format="%(message)s", force=True,
                        handlers=[file_handler, logging.StreamHandler()])
    return path
