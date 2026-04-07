"""
Logger — Structured logging utilities.

Provides a project-wide logger with JSON Lines support for trace persistence.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

from src.core.settings import ObservabilityConfig


# Module-level logger (lazy-initialized)
_logger: Optional[logging.Logger] = None


def get_logger(name: str = "modular_rag") -> logging.Logger:
    """
    Return the project logger, configured from settings.

    - Console output goes to stderr (keeps stdout clean for MCP protocol)
    - Log level is read from settings.observability.logging.log_level
    - Trace records (JSON Lines) are handled by TraceContext in Phase F
    """
    global _logger
    if _logger is not None:
        return _logger

    _logger = logging.getLogger(name)
    _logger.setLevel(logging.INFO)

    # Avoid duplicate handlers if called multiple times
    if _logger.handlers:
        return _logger

    # Console handler → stderr
    console = logging.StreamHandler(sys.stderr)
    console.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console.setFormatter(formatter)
    _logger.addHandler(console)

    return _logger
