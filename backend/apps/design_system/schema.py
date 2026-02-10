"""
JSON Schema definitions for design system structured output.

This module defines the schema for LLM structured output to ensure
consistent design token extraction from images.

MVP Fields (per PRD):
- Colors: primary, secondary, background, surface
- Typography: font_family, font_weight, base_font_size
- Shadow Depth: 0-5 integer

"""
from pydantic import BaseModel, Field


class ColorPalette(BaseModel):
    """Color palette extracted from design."""
    primary: str = Field(description="Primary brand color in HEX format (e.g., #3B82F6)")
    secondary: str = Field(description="Secondary accent color in HEX format")
    background: str = Field(description="Main background color in HEX format")
    surface: str = Field(description="Surface/card background color in HEX format")


class Typography(BaseModel):
    """Typography settings extracted from design."""
    font_family: str = Field(description="Font family names (e.g., 'Inter, SF Pro Display')")
    font_weight: str = Field(description="Available font weights (e.g., '400, 600, 700')")
    base_font_size: str = Field(description="Base font size with unit (e.g., '16px')")


class DesignSystemOutput(BaseModel):
    """
    Structured output schema for design system extraction.
    
    MVP schema with only essential fields per PRD:
    - Colors (4 required)
    - Typography (3 required)
    - Shadow depth (1 required)
    """
    colors: ColorPalette = Field(
        description="Extracted color palette from the design"
    )
    typography: Typography = Field(
        description="Typography settings extracted from the design"
    )
    shadow_depth: int = Field(
        ge=0, le=5,
        description="Shadow intensity level from 0 (flat) to 5 (heavy shadows)"
    )


def get_design_system_json_schema() -> dict:
    """
    Get the JSON schema for design system output.
    
    Returns:
        JSON schema dict compatible with both Gemini and OpenRouter
    """
    return DesignSystemOutput.model_json_schema()


def get_gemini_response_schema() -> dict:
    """
    Get the response schema formatted for Gemini API.
    
    MVP schema with only essential fields per PRD.
    See: https://ai.google.dev/gemini-api/docs/structured-output
    
    Returns:
        Schema dict formatted for Gemini's response_schema parameter
    """
    return {
        "type": "object",
        "properties": {
            "colors": {
                "type": "object",
                "properties": {
                    "primary": {"type": "string", "description": "Primary color in HEX"},
                    "secondary": {"type": "string", "description": "Secondary color in HEX"},
                    "background": {"type": "string", "description": "Background color in HEX"},
                    "surface": {"type": "string", "description": "Surface color in HEX"}
                },
                "required": ["primary", "secondary", "background", "surface"]
            },
            "typography": {
                "type": "object",
                "properties": {
                    "font_family": {"type": "string", "description": "Font family names"},
                    "font_weight": {"type": "string", "description": "Available font weights"},
                    "base_font_size": {"type": "string", "description": "Base font size"}
                },
                "required": ["font_family", "font_weight", "base_font_size"]
            },
            "shadow_depth": {
                "type": "integer",
                "description": "Shadow intensity 0-5",
                "minimum": 0,
                "maximum": 5
            }
        },
        "required": [
            "colors", "typography", "shadow_depth"
        ]
    }


def get_openrouter_response_format() -> dict:
    """
    Get the response format for OpenRouter API.
    
    OpenRouter uses json_schema format similar to OpenAI.
    See: https://openrouter.ai/docs/guides/features/structured-outputs
    
    Returns:
        Response format dict for OpenRouter
    """
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "design_system",
            "strict": True,
            "schema": get_gemini_response_schema()
        }
    }


def validate_design_system_output(data: dict) -> DesignSystemOutput:
    """
    Validate and parse design system output data.
    
    Args:
        data: Raw dict from LLM response
        
    Returns:
        Validated DesignSystemOutput instance
        
    Raises:
        ValidationError: If data doesn't match schema
    """
    return DesignSystemOutput.model_validate(data)


def convert_to_frontend_format(data: dict) -> dict:
    """
    Convert the structured output to frontend-compatible format.
    
    MVP fields only:
    - colors: primary, secondary, background, surface
    - typography: fontFamily, fontWeight, baseFontSize
    - shadowDepth: integer 0-5
    
    Args:
        data: Validated design system dict from LLM
        
    Returns:
        Dict formatted for frontend consumption and database storage
    """
    colors = data.get("colors", {})
    typography = data.get("typography", {})
    
    return {
        "colors": {
            "primary": colors.get("primary"),
            "secondary": colors.get("secondary"),
            "background": colors.get("background"),
            "surface": colors.get("surface"),
        },
        "typography": {
            "fontFamily": typography.get("font_family"),
            "fontWeight": typography.get("font_weight"),
            "baseFontSize": typography.get("base_font_size"),
        },
        "shadowDepth": data.get("shadow_depth"),
    }
