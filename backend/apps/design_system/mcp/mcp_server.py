"""
MCP Server implementation using official MCP Python SDK with FastMCP.

This module implements an MCP server using the official mcp library
with support for both stdio and streamable-http transports.

Usage:
    # stdio transport (for Cursor, Claude Desktop)
    python -m apps.design_system.mcp.cli --design-system-id <uuid> --api-key <key>
    
    # streamable-http transport (for web clients)
    The server is mounted as part of the Django/Starlette application
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
        """Get the complete design system including all design tokens (colors, typography, spacing, etc.)"""
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
            "spacing": style_data.get("spacing", {}),
            "borderRadius": style_data.get("borderRadius", {}),
            "shadows": style_data.get("shadows", {}),
            "visualEffects": style_data.get("visualEffects", {}),
            "styleRules": style_data.get("styleRules", []),
        }
        return json.dumps(result, indent=2)
    
    @mcp.tool()
    def get_colors() -> str:
        """Get the color palette including primary, secondary, background, and semantic colors"""
        style_data = _get_style_data()
        result = {
            "colors": style_data.get("colors", {}),
            "usage": {
                "primary": "Main brand color, use for primary buttons and key UI elements",
                "secondary": "Secondary accent color for supporting elements",
                "background": "Page/app background color",
                "surface": "Card and container background color",
                "textPrimary": "Main text color",
                "textSecondary": "Secondary/muted text color",
                "border": "Border and divider color",
                "success": "Success states and positive feedback",
                "warning": "Warning states and caution messages",
                "error": "Error states and negative feedback"
            }
        }
        return json.dumps(result, indent=2)
    
    @mcp.tool()
    def get_typography() -> str:
        """Get typography settings including font families, sizes, and weights"""
        style_data = _get_style_data()
        result = {
            "typography": style_data.get("typography", {}),
            "usage": {
                "fontFamily": "Primary font for body text",
                "fontFamilyHeading": "Font for headings (if different from body)",
                "baseFontSize": "Base font size for scaling",
                "fontWeightRegular": "Regular text weight",
                "fontWeightMedium": "Medium emphasis text",
                "fontWeightBold": "Strong emphasis and headings"
            }
        }
        return json.dumps(result, indent=2)
    
    @mcp.tool()
    def get_spacing() -> str:
        """Get spacing and layout settings"""
        style_data = _get_style_data()
        result = {
            "spacing": style_data.get("spacing", {}),
            "usage": {
                "unit": "Base spacing unit (typically 4px or 8px)",
                "scale": "Spacing scale multipliers for consistent rhythm"
            }
        }
        return json.dumps(result, indent=2)
    
    @mcp.tool()
    def get_component_styles(component: str = "") -> str:
        """Get component-specific styles (shadows, border radius, effects)
        
        Args:
            component: Optional component name (e.g., 'button', 'card', 'input', 'modal')
        """
        style_data = _get_style_data()
        base_styles = {
            "borderRadius": style_data.get("borderRadius", {}),
            "shadows": style_data.get("shadows", {}),
            "visualEffects": style_data.get("visualEffects", {}),
        }
        component_recommendations = {
            "button": {
                "borderRadius": style_data.get("borderRadius", {}).get("medium", "8px"),
                "shadow": "level1 for default, level2 for hover",
                "padding": "Use spacing scale values 3-4 for comfortable click targets"
            },
            "card": {
                "borderRadius": style_data.get("borderRadius", {}).get("large", "12px"),
                "shadow": "level1 for subtle, level2 for elevated",
                "padding": "Use spacing scale values 4-6"
            },
            "input": {
                "borderRadius": style_data.get("borderRadius", {}).get("small", "4px"),
                "border": f"1px solid {style_data.get('colors', {}).get('border', '#e0e0e0')}",
                "padding": "Use spacing scale values 2-3"
            },
            "modal": {
                "borderRadius": style_data.get("borderRadius", {}).get("large", "16px"),
                "shadow": "level3 for prominent elevation",
                "padding": "Use spacing scale values 5-6"
            }
        }
        
        if component and component.lower() in component_recommendations:
            result = {**base_styles, "recommendations": component_recommendations[component.lower()]}
        else:
            result = {**base_styles, "componentRecommendations": component_recommendations}
        
        return json.dumps(result, indent=2)
    
    @mcp.tool()
    def get_css_variables(format: str = "css") -> str:
        """Get CSS custom properties (variables) ready to use in stylesheets
        
        Args:
            format: Output format - 'css', 'scss', or 'json'
        """
        style_data = _get_style_data()
        colors = style_data.get("colors", {})
        typography = style_data.get("typography", {})
        spacing = style_data.get("spacing", {})
        border_radius = style_data.get("borderRadius", {})
        shadows = style_data.get("shadows", {})
        
        variables = {}
        
        # Colors
        for key, value in colors.items():
            var_name = f"--color-{_to_kebab_case(key)}"
            variables[var_name] = value
        
        # Typography
        if typography.get("fontFamily"):
            variables["--font-family"] = typography["fontFamily"]
        if typography.get("fontFamilyHeading"):
            variables["--font-family-heading"] = typography["fontFamilyHeading"]
        if typography.get("baseFontSize"):
            variables["--font-size-base"] = typography["baseFontSize"]
        if typography.get("fontWeightRegular"):
            variables["--font-weight-regular"] = str(typography["fontWeightRegular"])
        if typography.get("fontWeightMedium"):
            variables["--font-weight-medium"] = str(typography["fontWeightMedium"])
        if typography.get("fontWeightBold"):
            variables["--font-weight-bold"] = str(typography["fontWeightBold"])
        
        # Spacing
        if spacing.get("unit"):
            variables["--spacing-unit"] = f"{spacing['unit']}px"
        for idx, value in enumerate(spacing.get("scale", [])):
            variables[f"--spacing-{idx}"] = f"{value}px"
        
        # Border radius
        for key, value in border_radius.items():
            variables[f"--radius-{key}"] = value
        
        # Shadows
        for key, value in shadows.items():
            variables[f"--shadow-{key}"] = value
        
        if format == "json":
            return json.dumps(variables, indent=2)
        elif format == "scss":
            scss_vars = "\n".join([f"${k[2:]}: {v};" for k, v in variables.items()])
            return json.dumps({"scss": scss_vars}, indent=2)
        else:  # css
            css_vars = "\n".join([f"  {k}: {v};" for k, v in variables.items()])
            return json.dumps({"css": f":root {{\n{css_vars}\n}}"}, indent=2)
    
    @mcp.tool()
    def get_tailwind_config() -> str:
        """Get Tailwind CSS configuration generated from the design system"""
        style_data = _get_style_data()
        colors = style_data.get("colors", {})
        typography = style_data.get("typography", {})
        border_radius = style_data.get("borderRadius", {})
        shadows = style_data.get("shadows", {})
        
        tailwind_config = {
            "theme": {
                "extend": {
                    "colors": {k: v for k, v in {
                        "primary": colors.get("primary"),
                        "secondary": colors.get("secondary"),
                        "background": colors.get("background"),
                        "surface": colors.get("surface"),
                        "border": colors.get("border"),
                        "success": colors.get("success"),
                        "warning": colors.get("warning"),
                        "error": colors.get("error"),
                    }.items() if v is not None},
                    "fontFamily": {},
                    "borderRadius": {k: v for k, v in border_radius.items() if v} if border_radius else {},
                    "boxShadow": {k: v for k, v in shadows.items() if v} if shadows else {},
                }
            }
        }
        
        if typography.get("fontFamily"):
            tailwind_config["theme"]["extend"]["fontFamily"]["sans"] = [typography["fontFamily"]]
        if typography.get("fontFamilyHeading"):
            tailwind_config["theme"]["extend"]["fontFamily"]["heading"] = [typography["fontFamilyHeading"]]
        
        return json.dumps(tailwind_config, indent=2)
    
    return mcp


def run_stdio_server(design_system_id: str, api_key: str):
    """
    Run the MCP server with stdio transport.
    
    This is the entry point for CLI-based MCP connections (Cursor, Claude Desktop).
    """
    mcp = create_design_system_mcp(design_system_id, api_key)
    mcp.run(transport="stdio")


def get_streamable_http_app(design_system_id: str, api_key: str):
    """
    Get a Starlette ASGI app for streamable-http transport.
    
    This can be mounted in Django/Starlette for HTTP-based MCP connections.
    """
    mcp = create_design_system_mcp(design_system_id, api_key)
    return mcp.streamable_http_app(
        streamable_http_path="/",
        json_response=True,
        stateless_http=True
    )
