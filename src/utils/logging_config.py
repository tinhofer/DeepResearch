"""Centralized logging configuration for DeepResearch.

Call ``setup_logging()`` once at application startup (e.g. in ``webui.main()``)
to configure consistent formatting, levels, and optional JSON output across
every module.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Optional


class StructuredFormatter(logging.Formatter):
    """Outputs each log record as a single JSON line for machine consumption."""

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0] is not None:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, ensure_ascii=False)


class ReadableFormatter(logging.Formatter):
    """Human-friendly formatter with timestamps, level, and logger name."""

    FMT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    DATE_FMT = "%Y-%m-%d %H:%M:%S"

    def __init__(self) -> None:
        super().__init__(fmt=self.FMT, datefmt=self.DATE_FMT)


def setup_logging(
    level: int = logging.INFO,
    json_output: bool = False,
    log_file: Optional[str] = None,
) -> None:
    """Configure the root logger for the entire application.

    Args:
        level: Minimum log level (default INFO).
        json_output: If True, emit JSON lines instead of human-readable text.
        log_file: Optional path to also write logs to a file.
    """
    root = logging.getLogger()

    # Avoid adding duplicate handlers on repeated calls
    if root.handlers:
        return

    root.setLevel(level)

    formatter = StructuredFormatter() if json_output else ReadableFormatter()

    console = logging.StreamHandler(sys.stderr)
    console.setFormatter(formatter)
    root.addHandler(console)

    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    # Quiet noisy third-party loggers
    for name in ("httpx", "httpcore", "urllib3", "playwright", "asyncio"):
        logging.getLogger(name).setLevel(logging.WARNING)
