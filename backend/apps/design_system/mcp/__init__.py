"""
MCP (Model Context Protocol) server for exposing design systems.

This module provides an MCP server that exposes design systems as tools
for AI coding assistants like VS Code Copilot, Cursor, and other MCP-compatible clients.

Supports Streamable HTTP transport protocol for remote connections.
For connection instructions, see docs/MCP_CONNECTION.md
"""
from .server import MCPDesignSystemServer, get_design_system_mcp_config
from .mcp_server import create_design_system_mcp

__all__ = [
    # Legacy REST API server
    'MCPDesignSystemServer',
    'get_design_system_mcp_config',
    # Standard MCP protocol server (FastMCP)
    'create_design_system_mcp',
]
