"""Tests for response models."""

import pytest
from datetime import datetime

from agentfarm_mcp.models.responses import ToolError, ToolMetadata, ToolResponse


def test_tool_metadata_creation():
    """Test ToolMetadata model."""
    metadata = ToolMetadata(
        tool="test_tool", from_cache=True, execution_time_ms=42.5
    )

    assert metadata.tool == "test_tool"
    assert metadata.from_cache is True
    assert metadata.execution_time_ms == 42.5
    assert isinstance(metadata.timestamp, str)


def test_tool_metadata_timestamp_auto():
    """Test that timestamp is auto-generated."""
    metadata = ToolMetadata(tool="test_tool")

    # Should have timestamp
    assert metadata.timestamp is not None
    # Should be ISO format
    assert "T" in metadata.timestamp


def test_tool_error_creation():
    """Test ToolError model."""
    error = ToolError(
        type="ValidationError",
        message="Invalid parameter",
        details={"field": "value"},
    )

    assert error.type == "ValidationError"
    assert error.message == "Invalid parameter"
    assert error.details == {"field": "value"}


def test_tool_error_without_details():
    """Test ToolError without details."""
    error = ToolError(type="DatabaseError", message="Connection failed")

    assert error.type == "DatabaseError"
    assert error.message == "Connection failed"
    assert error.details is None


def test_tool_response_success():
    """Test successful ToolResponse."""
    metadata = ToolMetadata(tool="test_tool")

    response = ToolResponse(
        success=True, data={"result": "success"}, metadata=metadata, error=None
    )

    assert response.success is True
    assert response.data == {"result": "success"}
    assert response.metadata == metadata
    assert response.error is None


def test_tool_response_error():
    """Test error ToolResponse."""
    metadata = ToolMetadata(tool="test_tool")
    error = ToolError(type="ValidationError", message="Invalid")

    response = ToolResponse(success=False, data=None, metadata=metadata, error=error)

    assert response.success is False
    assert response.data is None
    assert response.error == error