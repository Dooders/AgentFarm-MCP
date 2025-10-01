"""Structured logging configuration using structlog.

This module provides structured logging with rich context for better observability.
"""

import logging
import sys
from typing import Any, Dict, Optional

import structlog
from structlog.types import EventDict, Processor


def add_app_context(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add application-specific context to log events.

    Args:
        logger: Logger instance
        method_name: Method name being logged
        event_dict: Event dictionary

    Returns:
        Updated event dictionary with app context
    """
    event_dict["app"] = "agentfarm_mcp"
    return event_dict


def setup_structured_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    json_logs: bool = False,
    dev_mode: bool = True,
) -> None:
    """Setup structured logging with structlog.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        json_logs: Whether to output JSON formatted logs (useful for production)
        dev_mode: Whether to use development-friendly formatting

    Example:
        >>> setup_structured_logging(log_level="DEBUG", dev_mode=True)
        >>> logger = get_structured_logger(__name__)
        >>> logger.info("server_started", port=8000, host="localhost")
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Build processor chain
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        add_app_context,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
    ]

    # Add exception formatting
    if dev_mode:
        processors.append(structlog.processors.ExceptionPrettyPrinter())
    else:
        processors.append(structlog.processors.format_exc_info)

    # Add final renderer based on mode
    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        if dev_mode:
            processors.append(structlog.dev.ConsoleRenderer(colors=True))
        else:
            processors.append(structlog.processors.KeyValueRenderer(key_order=["timestamp", "level", "event"]))

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure file logging if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        logging.root.addHandler(file_handler)

    # Suppress noisy loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_structured_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Structured logger instance

    Example:
        >>> logger = get_structured_logger(__name__)
        >>> logger.info("user_login", user_id="123", ip="192.168.1.1")
    """
    return structlog.get_logger(name)


def bind_context(**kwargs: Any) -> None:
    """Bind context variables to all subsequent log messages in this context.

    Args:
        **kwargs: Context key-value pairs to bind

    Example:
        >>> bind_context(request_id="abc-123", user_id="user-456")
        >>> logger.info("processing_request")  # Will include request_id and user_id
    """
    structlog.contextvars.bind_contextvars(**kwargs)


def unbind_context(*keys: str) -> None:
    """Unbind context variables.

    Args:
        *keys: Context keys to unbind

    Example:
        >>> unbind_context("request_id", "user_id")
    """
    structlog.contextvars.unbind_contextvars(*keys)


def clear_context() -> None:
    """Clear all context variables.

    Example:
        >>> clear_context()
    """
    structlog.contextvars.clear_contextvars()


class LogContext:
    """Context manager for temporary log context binding.

    Example:
        >>> with LogContext(request_id="abc-123"):
        ...     logger.info("processing")  # Includes request_id
        >>> logger.info("done")  # request_id not included
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize context manager with context to bind.

        Args:
            **kwargs: Context key-value pairs
        """
        self.context = kwargs
        self.keys = list(kwargs.keys())

    def __enter__(self) -> "LogContext":
        """Enter context and bind variables.

        Returns:
            Self
        """
        bind_context(**self.context)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context and unbind variables.

        Args:
            exc_type: Exception type if raised
            exc_val: Exception value if raised
            exc_tb: Exception traceback if raised
        """
        unbind_context(*self.keys)
