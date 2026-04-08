import logging
from logging.handlers import RotatingFileHandler
import os
from core.config import settings

# Create logs directory
os.makedirs("logs", exist_ok=True)

# File handler
file_handler = RotatingFileHandler(
    "logs/app.log", maxBytes=10_000_000, backupCount=5
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO if settings.DEBUG else logging.WARNING)
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)

# Logger
logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])
logger = logging.getLogger(__name__)

__all__ = ["logger"]