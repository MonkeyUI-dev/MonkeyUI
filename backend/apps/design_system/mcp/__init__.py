"""
MCP (Model Context Protocol) server for exposing design systems.

This module provides an MCP server that exposes design systems as tools
for vibe coding tools like Cursor, Claude, etc.
"""
from .server import MCPDesignSystemServer, get_design_system_mcp_config

__all__ = ['MCPDesignSystemServer', 'get_design_system_mcp_config']
