import logging
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    bot_handler = logging.FileHandler(LOG_DIR / "bot.log", encoding="utf-8")
    bot_handler.setFormatter(formatter)
    bot_handler.setLevel(logging.INFO)

    error_handler = logging.FileHandler(LOG_DIR / "errors.log", encoding="utf-8")
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)

    logger.addHandler(bot_handler)
    logger.addHandler(error_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False
    return logger


def log_exception(logger: logging.Logger, message: str, error: BaseException) -> None:
    logger.exception("%s: %s", message, error)
