"""Response models for MCP tools."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ToolMetadata(BaseModel):
    """Metadata included in tool responses."""

    tool: str = Field(..., description="Tool name")
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(), description="Response timestamp"
    )
    from_cache: bool = Field(False, description="Whether result came from cache")
    execution_time_ms: float = Field(0.0, description="Execution time in milliseconds")


class ToolError(BaseModel):
    """Error information."""

    type: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class ToolResponse(BaseModel):
    """Standard tool response format."""

    success: bool = Field(..., description="Whether operation succeeded")
    data: Optional[Any] = Field(None, description="Response data")
    metadata: ToolMetadata = Field(..., description="Response metadata")
    error: Optional[ToolError] = Field(None, description="Error information if failed")