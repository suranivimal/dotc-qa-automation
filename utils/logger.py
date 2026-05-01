"""
=============================================================================
DOTC Admin Panel — QA Logger Utility
=============================================================================
Provides a shared logger instance used by every page object and test file.
Outputs to both console (coloured) and a rotating log file.
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler


# ─── Colour Codes (ANSI — for terminal readability) ────────────────────────
class _Colours:
    GREY = "\033[90m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD_RED = "\033[1;91m"
    CYAN = "\033[96m"
    RESET = "\033[0m"


class _ColouredFormatter(logging.Formatter):
    """Apply colour per log-level for console output only."""

    LEVEL_COLOURS = {
        logging.DEBUG: _Colours.GREY,
        logging.INFO: _Colours.GREEN,
        logging.WARNING: _Colours.YELLOW,
        logging.ERROR: _Colours.RED,
        logging.CRITICAL: _Colours.BOLD_RED,
    }

    def format(self, record: logging.LogRecord) -> str:
        colour = self.LEVEL_COLOURS.get(record.levelno, _Colours.RESET)
        record.levelname = f"{colour}{record.levelname:<8}{_Colours.RESET}"
        record.msg = f"{_Colours.CYAN}{record.msg}{_Colours.RESET}"
        return super().format(record)


def get_logger(name: str = "dotc_qa") -> logging.Logger:
    """Return a configured logger. Call once per module — cached by name."""

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # already configured

    logger.setLevel(logging.DEBUG)

    # ── Console handler ─────────────────────────────────────────────────
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(
        _ColouredFormatter("%(asctime)s │ %(levelname)s │ %(name)s │ %(message)s",
                           datefmt="%H:%M:%S")
    )
    logger.addHandler(console)

    # ── File handler (rotating, 5 MB × 3 backups) ──────────────────────
    log_dir = os.path.join(os.path.dirname(__file__), "..", "reports", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(
        log_dir, f"dotc_qa_{datetime.now():%Y-%m-%d}.log"
    )

    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s │ %(levelname)-8s │ %(name)s │ %(funcName)s:%(lineno)d │ %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(file_handler)

    return logger


# ─── Convenience step-logger for test readability ──────────────────────────
class StepLogger:
    """
    Usage inside tests:
        step = StepLogger("test_login")
        step.info("Entering valid credentials")
        step.passed("Login redirected to dashboard")
        step.failed("Expected dashboard URL, got /error")
    """

    def __init__(self, test_name: str):
        self._log = get_logger(test_name)
        self._step = 0

    def _next(self) -> int:
        self._step += 1
        return self._step

    def info(self, msg: str) -> None:
        self._log.info(f"[Step {self._next():02d}] {msg}")

    def passed(self, msg: str) -> None:
        self._log.info(f"[Step {self._step:02d}] ✅ PASSED — {msg}")

    def failed(self, msg: str) -> None:
        self._log.error(f"[Step {self._step:02d}] ❌ FAILED — {msg}")

    def warn(self, msg: str) -> None:
        self._log.warning(f"[Step {self._step:02d}] ⚠️  {msg}")

    def debug(self, msg: str) -> None:
        self._log.debug(f"  ↳ {msg}")