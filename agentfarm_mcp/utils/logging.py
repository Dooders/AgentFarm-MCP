"""Legacy logging configuration - DEPRECATED.

Use structured_logging module instead for better observability.
This module is kept for backwards compatibility only.
"""

import logging
import sys
from pathlib import Path

import structlog

from .structured_logging import setup_structured_logging as _setup_structured


def setup_logging(
    log_level: str = "INFO",
    log_file: str | None = None,
    format_str: str | None = None,
) -> None:
    """Setup logging configuration.

    DEPRECATED: Use structured_logging.setup_structured_logging() instead.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        format_str: Optional custom format string

    Example:
        >>> from agentfarm_mcp.utils.structured_logging import setup_structured_logging
        >>> setup_structured_logging(log_level="DEBUG")
    """
    # Delegate to structured logging with deprecation warning
    structlog.get_logger(__name__).warning(
        "setup_logging() is deprecated, use structured_logging.setup_structured_logging()"
    )
    _setup_structured(log_level=log_level, log_file=log_file, dev_mode=True)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    DEPRECATED: Use structured_logging.get_structured_logger() instead.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance

    Example:
        >>> from agentfarm_mcp.utils.structured_logging import get_structured_logger
        >>> logger = get_structured_logger(__name__)
    """
    return logging.getLogger(name)