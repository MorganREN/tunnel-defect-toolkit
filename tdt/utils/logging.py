"""Logging helpers."""

from __future__ import annotations

import logging


def get_logger(name: str = "tdt") -> logging.Logger:
    """Return a package logger with a simple default handler."""

    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
