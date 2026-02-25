"""MCP models."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class McpServer(BaseModel):
    """MCP server model."""

    mcp_code: str = Field(..., description="MCP code")
    name: str = Field(..., description="MCP name")
    description: Optional[str] = Field(None, description="MCP description")
    type: Optional[str] = Field(None, description="MCP type")
    author: Optional[str] = Field(None, description="MCP author")
    email: Optional[str] = Field(None, description="MCP author email")
    version: Optional[str] = Field(None, description="MCP version")
    stdio_cmd: Optional[str] = Field(None, description="MCP stdio cmd")
    sse_url: Optional[str] = Field(None, description="MCP sse connect url")
    sse_headers: Optional[Dict[str, str]] = Field(None, description="MCP sse connect headers")
    token: Optional[str] = Field(None, description="MCP sse connect token")
    icon: Optional[str] = Field(None, description="MCP icon")
    category: Optional[str] = Field(None, description="MCP category")
    installed: Optional[int] = Field(None, description="MCP installed count")
    available: Optional[bool] = Field(None, description="MCP availability status")
    server_ips: Optional[str] = Field(None, description="MCP server run machine ips")
    gmt_created: Optional[str] = Field(None, description="ISO format creation time")
    gmt_modified: Optional[str] = Field(None, description="ISO format modification time")


class McpCreateRequest(BaseModel):
    """MCP create request model."""

    mcp_code: Optional[str] = Field(None, description="mcp_code")
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="mcp name")
    description: Optional[str] = Field(None, min_length=1, description="mcp description")
    type: Optional[str] = Field(None, min_length=1, max_length=255, description="mcp type")
    author: Optional[str] = Field(None, max_length=255, description="mcp author")
    email: Optional[str] = Field(None, max_length=255, description="mcp author email")
    version: Optional[str] = Field(None, max_length=255, description="mcp version")
    stdio_cmd: Optional[str] = Field(None, description="mcp stdio cmd")
    sse_url: Optional[str] = Field(None, description="mcp sse connect url")
    sse_headers: Optional[Dict[str, str]] = Field(None, description="mcp sse connect headers")
    token: Optional[str] = Field(None, description="mcp sse connect token")
    icon: Optional[str] = Field(None, description="mcp icon")
    category: Optional[str] = Field(None, description="mcp category")
    installed: Optional[int] = Field(None, ge=0, description="mcp installed count")
    available: Optional[bool] = Field(None, description="mcp availability status")


class McpTool(BaseModel):
    """MCP tool model."""

    name: str = Field(..., description="mcp tool name")
    description: Optional[str] = Field(None, description="mcp tool description")
    param_schema: Optional[Any] = Field(None, description="mcp tool param schema")


class McpRunRequest(BaseModel):
    """MCP run request model."""

    name: str = Field(..., min_length=1, max_length=255, description="mcp name")
    stdio_cmd: Optional[str] = Field(None, description="mcp stdio cmd")
    sse_url: Optional[str] = Field(None, description="mcp sse connect url")
    sse_headers: Optional[Dict[str, str]] = Field(None, description="mcp sse connect headers")
    token: Optional[str] = Field(None, description="mcp sse connect token")
    method: Optional[str] = Field(None, description="mcp sse call method")
    params: Optional[Dict[str, Any]] = Field(None, description="mcp tool call params")
