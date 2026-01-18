"""
MCP Server implementation for design systems.

This module implements an MCP server that exposes design system data
as tools for AI coding assistants. Each design system can be independently
accessed via its own API key.
"""
import json
import logging
from typing import Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """Represents an MCP tool definition."""
    name: str
    description: str
    input_schema: dict


@dataclass
class MCPToolResponse:
    """Represents an MCP tool response."""
    content: list[dict]
    is_error: bool = False


class MCPDesignSystemServer:
    """
    MCP Server that exposes a design system's data as tools.
    
    Each instance is associated with a specific design system and provides
    tools for accessing colors, typography, spacing, and other design tokens.
    """
    
    def __init__(self, design_system_id: str, api_key: str):
        """
        Initialize the MCP server for a design system.
        
        Args:
            design_system_id: UUID of the design system
            api_key: API key for authenticating requests
        """
        self.design_system_id = design_system_id
        self.api_key = api_key
        self._design_system = None
    
    def _load_design_system(self):
        """Load the design system from database."""
        if self._design_system is None:
            from ..models import DesignSystem
            try:
                # Just load the design system, MCP access controlled by UserAPIKey
                self._design_system = DesignSystem.objects.get(
                    id=self.design_system_id
                )
            except DesignSystem.DoesNotExist:
                return None
        return self._design_system
    
    def validate_api_key(self, provided_key: str) -> bool:
        """Validate the provided API key."""
        design_system = self._load_design_system()
        if not design_system:
            return False
        return design_system.mcp_api_key == provided_key
    
    def get_tools(self) -> list[MCPTool]:
        """
        Get the list of available MCP tools for this design system.
        
        Returns:
            List of MCPTool objects describing available tools
        """
        design_system = self._load_design_system()
        if not design_system:
            return []
        
        tools = [
            MCPTool(
                name="get_design_system",
                description=f"Get the complete design system '{design_system.name}' including all design tokens (colors, typography, spacing, etc.)",
                input_schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            MCPTool(
                name="get_colors",
                description=f"Get the color palette from '{design_system.name}' design system including primary, secondary, background, and semantic colors",
                input_schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            MCPTool(
                name="get_typography",
                description=f"Get typography settings from '{design_system.name}' design system including font families, sizes, and weights",
                input_schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            MCPTool(
                name="get_spacing",
                description=f"Get spacing and layout settings from '{design_system.name}' design system",
                input_schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            MCPTool(
                name="get_component_styles",
                description=f"Get component-specific styles (shadows, border radius, effects) from '{design_system.name}' design system",
                input_schema={
                    "type": "object",
                    "properties": {
                        "component": {
                            "type": "string",
                            "description": "Optional component name (e.g., 'button', 'card', 'input')"
                        }
                    },
                    "required": []
                }
            ),
            MCPTool(
                name="get_css_variables",
                description=f"Get CSS custom properties (variables) generated from '{design_system.name}' design system, ready to use in stylesheets",
                input_schema={
                    "type": "object",
                    "properties": {
                        "format": {
                            "type": "string",
                            "enum": ["css", "scss", "json"],
                            "description": "Output format for CSS variables"
                        }
                    },
                    "required": []
                }
            ),
            MCPTool(
                name="get_tailwind_config",
                description=f"Get Tailwind CSS configuration generated from '{design_system.name}' design system",
                input_schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
        ]
        
        return tools
    
    def call_tool(self, name: str, arguments: dict) -> MCPToolResponse:
        """
        Execute an MCP tool call.
        
        Args:
            name: Name of the tool to call
            arguments: Arguments for the tool
            
        Returns:
            MCPToolResponse with the result
        """
        design_system = self._load_design_system()
        if not design_system:
            return MCPToolResponse(
                content=[{"type": "text", "text": "Design system not found or MCP not enabled"}],
                is_error=True
            )
        
        style_data = design_system.design_tokens or {}
        
        handlers = {
            "get_design_system": self._get_full_design_system,
            "get_colors": self._get_colors,
            "get_typography": self._get_typography,
            "get_spacing": self._get_spacing,
            "get_component_styles": self._get_component_styles,
            "get_css_variables": self._get_css_variables,
            "get_tailwind_config": self._get_tailwind_config,
        }
        
        handler = handlers.get(name)
        if not handler:
            return MCPToolResponse(
                content=[{"type": "text", "text": f"Unknown tool: {name}"}],
                is_error=True
            )
        
        try:
            result = handler(style_data, arguments)
            return MCPToolResponse(
                content=[{"type": "text", "text": json.dumps(result, indent=2)}]
            )
        except Exception as e:
            logger.exception(f"Error executing MCP tool {name}: {e}")
            return MCPToolResponse(
                content=[{"type": "text", "text": f"Error: {str(e)}"}],
                is_error=True
            )
    
    def _get_full_design_system(self, style_data: dict, arguments: dict) -> dict:
        """Get the complete design system."""
        design_system = self._load_design_system()
        return {
            "name": design_system.name,
            "description": design_system.description,
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
    
    def _get_colors(self, style_data: dict, arguments: dict) -> dict:
        """Get color palette."""
        return {
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
    
    def _get_typography(self, style_data: dict, arguments: dict) -> dict:
        """Get typography settings."""
        return {
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
    
    def _get_spacing(self, style_data: dict, arguments: dict) -> dict:
        """Get spacing settings."""
        return {
            "spacing": style_data.get("spacing", {}),
            "usage": {
                "unit": "Base spacing unit (typically 4px or 8px)",
                "scale": "Spacing scale multipliers for consistent rhythm"
            }
        }
    
    def _get_component_styles(self, style_data: dict, arguments: dict) -> dict:
        """Get component styles."""
        component = arguments.get("component")
        
        base_styles = {
            "borderRadius": style_data.get("borderRadius", {}),
            "shadows": style_data.get("shadows", {}),
            "visualEffects": style_data.get("visualEffects", {}),
        }
        
        # Component-specific recommendations
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
            return {
                **base_styles,
                "recommendations": component_recommendations[component.lower()]
            }
        
        return {
            **base_styles,
            "componentRecommendations": component_recommendations
        }
    
    def _get_css_variables(self, style_data: dict, arguments: dict) -> dict:
        """Generate CSS custom properties."""
        format_type = arguments.get("format", "css")
        colors = style_data.get("colors", {})
        typography = style_data.get("typography", {})
        spacing = style_data.get("spacing", {})
        border_radius = style_data.get("borderRadius", {})
        shadows = style_data.get("shadows", {})
        
        variables = {}
        
        # Colors
        for key, value in colors.items():
            var_name = f"--color-{self._to_kebab_case(key)}"
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
        
        if format_type == "json":
            return variables
        elif format_type == "scss":
            scss_vars = "\n".join([f"${k[2:]}: {v};" for k, v in variables.items()])
            return {"scss": scss_vars}
        else:  # css
            css_vars = "\n".join([f"  {k}: {v};" for k, v in variables.items()])
            return {"css": f":root {{\n{css_vars}\n}}"}
    
    def _get_tailwind_config(self, style_data: dict, arguments: dict) -> dict:
        """Generate Tailwind CSS configuration."""
        colors = style_data.get("colors", {})
        typography = style_data.get("typography", {})
        spacing = style_data.get("spacing", {})
        border_radius = style_data.get("borderRadius", {})
        shadows = style_data.get("shadows", {})
        
        tailwind_config = {
            "theme": {
                "extend": {
                    "colors": {
                        "primary": colors.get("primary"),
                        "secondary": colors.get("secondary"),
                        "background": colors.get("background"),
                        "surface": colors.get("surface"),
                        "border": colors.get("border"),
                        "success": colors.get("success"),
                        "warning": colors.get("warning"),
                        "error": colors.get("error"),
                    },
                    "fontFamily": {},
                    "borderRadius": {},
                    "boxShadow": {},
                }
            }
        }
        
        # Remove None values from colors
        tailwind_config["theme"]["extend"]["colors"] = {
            k: v for k, v in tailwind_config["theme"]["extend"]["colors"].items() 
            if v is not None
        }
        
        # Typography
        if typography.get("fontFamily"):
            tailwind_config["theme"]["extend"]["fontFamily"]["sans"] = [typography["fontFamily"]]
        if typography.get("fontFamilyHeading"):
            tailwind_config["theme"]["extend"]["fontFamily"]["heading"] = [typography["fontFamilyHeading"]]
        
        # Border radius
        if border_radius:
            tailwind_config["theme"]["extend"]["borderRadius"] = {
                k: v for k, v in border_radius.items() if v
            }
        
        # Shadows
        if shadows:
            tailwind_config["theme"]["extend"]["boxShadow"] = {
                k: v for k, v in shadows.items() if v
            }
        
        return tailwind_config
    
    @staticmethod
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


def get_design_system_mcp_config(design_system_id: str) -> Optional[dict]:
    """
    Get the MCP configuration for a design system.
    
    This returns the configuration that vibe coding tools need
    to connect to this design system's MCP server.
    
    Args:
        design_system_id: UUID of the design system
        
    Returns:
        MCP configuration dict or None if not enabled
    """
    from ..models import DesignSystem
    from apps.accounts.models import UserAPIKey
    
    try:
        design_system = DesignSystem.objects.get(id=design_system_id)
        
        # Check if user has any active API key (MCP enabled)
        api_key = UserAPIKey.objects.filter(
            user=design_system.user,
            is_active=True
        ).first()
        
        if not api_key:
            return None
        
        return {
            "name": f"monkeyui-{design_system.name.lower().replace(' ', '-')}",
            "description": f"Design system: {design_system.name}",
            "api_key": api_key.key,
            "endpoints": {
                "tools": f"/api/design-system/mcp/{design_system_id}/tools/",
                "call": f"/api/design-system/mcp/{design_system_id}/call/",
            }
        }
    except DesignSystem.DoesNotExist:
        return None
