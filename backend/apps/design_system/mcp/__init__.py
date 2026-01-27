"""
MCP (Model Context Protocol) server for exposing design systems.

This module provides an MCP server that exposes design systems as tools
for vibe coding tools like Cursor, Claude Desktop, etc.

Supports two official MCP transport protocols:
- stdio: For local CLI tools (Cursor, Claude Desktop)
- streamable-http: For web-based clients and remote connections
"""
from .server import MCPDesignSystemServer, get_design_system_mcp_config
from .mcp_server import (
    create_design_system_mcp,
    run_stdio_server,
    get_streamable_http_app
)

__all__ = [
    # Legacy REST API server
    'MCPDesignSystemServer',
    'get_design_system_mcp_config',
    # Standard MCP protocol server (FastMCP)
    'create_design_system_mcp',
    'run_stdio_server',
    'get_streamable_http_app',
]
