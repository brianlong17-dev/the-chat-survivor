import logging
import os
import re

from dotenv import load_dotenv

load_dotenv(override=True)

LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
MASTER_LOG_DIR = os.path.join(LOGS_DIR, "master_logs")

_master_loggers: dict[str, logging.Logger] = {}


def get_master_logger(name: str, filename: str) -> logging.Logger:
    if name not in _master_loggers:
        os.makedirs(MASTER_LOG_DIR, exist_ok=True)
        handler = logging.FileHandler(os.path.join(MASTER_LOG_DIR, filename))
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        _master_loggers[name] = logger
    return _master_loggers[name]


def is_dev_mode() -> bool:
    return os.getenv("DEV_MODE", "false").lower() in ("1", "true", "yes")


_COLON = re.compile(r'\s*:\s*')
_BRACKET_TAG = re.compile(r'\[(SYSTEM|ERROR|ADMIN|GAME|HOST|RULE)\]', re.IGNORECASE)
_FENCE = re.compile(r'[-=_]{3,}')


def sanitize_text(text: str) -> str:
    text = _COLON.sub(' - ', text)
    text = _BRACKET_TAG.sub('', text)
    text = _FENCE.sub('', text)
    return text


INACTIVITY_TIMEOUT = 900  # seconds before idle round gate disconnects the session
