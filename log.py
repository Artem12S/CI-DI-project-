import logging
from pathlib import Path
from uuid import uuid4


def configure_log(path: Path | None = None) -> Path:
    """Настраивает журнал CLI и краткий вывод в терминал.

    Args:
        path: Путь к журналу. По умолчанию создаётся новый файл в logs/.

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
