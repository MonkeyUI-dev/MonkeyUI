"""
MCP Server implementation using official MCP Python SDK with FastMCP.

This module implements an MCP server using the official mcp library
with support for Streamable HTTP transport.

Usage:
    # Streamable HTTP transport (for VS Code Copilot, Cursor, web clients)
    The server is exposed via HTTP endpoint (POST /api/v1/design-systems/mcp/{id}/)
"""
import json
import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


def create_design_system_mcp(design_system_id: str, api_key: str) -> FastMCP:
    """
    Create a FastMCP server instance for a specific design system.
    
    Args:
        design_system_id: UUID of the design system
        api_key: API key for authentication
        
    Returns:
        Configured FastMCP server instance
    """
    # We'll load design system lazily to avoid circular imports
    _design_system_cache = {}
    
    def _load_design_system():
        """Load design system from database."""
        if 'ds' in _design_system_cache:
            return _design_system_cache['ds']
        
        # Import Django models (must be done after Django setup)
        import django
        if not django.apps.apps.ready:
            django.setup()
        
        from apps.design_system.models import DesignSystem
        
        try:
            ds = DesignSystem.objects.get(id=design_system_id)
            _design_system_cache['ds'] = ds
            return ds
        except DesignSystem.DoesNotExist:
            return None
    
    def _get_style_data() -> dict:
        """Get style data from design system."""
        ds = _load_design_system()
        if ds:
            return ds.design_tokens or {}
        return {}
    
    def _to_kebab_case(s: str) -> str:
        """Convert camelCase to kebab-case."""
        result = []
        for char in s:
            if char.isupper():
                result.append('-')
                result.append(char.lower())
            else:
                result.append(char)
        return ''.join(result).lstrip('-')
    
    # Get design system name for server naming
    ds = _load_design_system()
    server_name = f"monkeyui-{ds.name.lower().replace(' ', '-')}" if ds else "monkeyui-design-system"
    
    # Create FastMCP server
    mcp = FastMCP(server_name)
    
    @mcp.tool()
    def get_design_system() -> str:
        """Get the complete design system including all design tokens (colors, typography, shadow depth, etc.)"""
        ds = _load_design_system()
        if not ds:
            return json.dumps({"error": "Design system not found"})
        
        style_data = _get_style_data()
        result = {
            "name": ds.name,
            "description": ds.description,
            "styleName": style_data.get("styleName"),
            "styleDescription": style_data.get("styleDescription"),
            "colors": style_data.get("colors", {}),
            "typography": style_data.get("typography", {}),
            "shadowDepth": style_data.get("shadowDepth", 0),
        }
        return json.dumps(result, indent=2)
    
    return mcp
