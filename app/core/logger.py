import logging
import os
from logging.handlers import TimedRotatingFileHandler

from app.core.config import settings

os.makedirs(settings.LOG_DIR, exist_ok=True)

log_path = os.path.join(settings.LOG_DIR, "app.log")

file_handler = TimedRotatingFileHandler(
    log_path,
    when="midnight",
    interval=1,
    backupCount=settings.LOG_RETENTION_DAYS,
    encoding="utf-8",
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
file_handler.suffix = "%Y-%m-%d"

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO if settings.DEBUG else logging.WARNING)
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)

logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])
logger = logging.getLogger("tapafix")

__all__ = ["logger"]
