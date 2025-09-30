"""Tests for logging module."""

import logging
import pytest
from pathlib import Path

from mcp_server.utils.logging import get_logger, setup_logging


def test_setup_logging_basic():
    """Test basic logging setup."""
    setup_logging(log_level="INFO")

    # Should not raise an error
    logger = logging.getLogger("test")
    logger.info("Test message")


def test_setup_logging_with_file(tmp_path):
    """Test logging setup with log file."""
    log_file = tmp_path / "test.log"

    setup_logging(log_level="DEBUG", log_file=str(log_file))

    # Log file should be created
    logger = logging.getLogger("test_file")
    logger.info("Test message")


def test_setup_logging_custom_format():
    """Test logging with custom format."""
    custom_format = "%(levelname)s - %(message)s"

    setup_logging(log_level="INFO", format_str=custom_format)

    # Should not raise an error
    logger = logging.getLogger("test_custom")
    logger.info("Test")


def test_get_logger():
    """Test get_logger function."""
    logger = get_logger("my_module")

    assert isinstance(logger, logging.Logger)
    assert logger.name == "my_module"


def test_setup_logging_levels():
    """Test different logging levels."""
    for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        setup_logging(log_level=level)
        # Should not raise an error