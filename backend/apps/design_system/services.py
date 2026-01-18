"""
Design system generation service.

This module provides the service layer for design system generation,
coordinating between LLM providers, prompts, and task management.
"""
import json
import logging
from typing import Optional
from dataclasses import dataclass
from json_repair import repair_json
from .llm import create_llm_provider, LLMResponse
from .llm.config import get_provider_config, get_default_provider, LLMProviderType
from .prompts import get_image_analysis_prompt, get_design_system_prompt

logger = logging.getLogger(__name__)


@dataclass
class DesignSystemResult:
    """Result of design system generation."""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None


class DesignSystemService:
    """
    Service for generating design systems from images using LLM providers.
    
    This service handles:
    - LLM provider selection and configuration
    - Image analysis using vision models
    - Design system token extraction
    - Result parsing and validation
    """
    
    def __init__(self, provider_type: Optional[str] = None):
        """
        Initialize the design system service.
        
        Args:
            provider_type: Optional specific provider to use.
                          If not specified, uses default provider.
        """
        self.provider_type = provider_type
        self._provider = None
        self._config = None
    
    def _get_provider(self):
        """Get or create the LLM provider instance."""
        if self._provider is None:
            if self.provider_type:
                try:
                    provider_enum = LLMProviderType(self.provider_type)
                    self._config = get_provider_config(provider_enum, for_vision=True)
                except ValueError:
                    raise ValueError(f"Unsupported provider: {self.provider_type}")
            else:
                self._config = get_default_provider(for_vision=True)
            
            if not self._config:
                raise ValueError("No LLM provider configured")
            
            self._provider = create_llm_provider(self._config)
        
        return self._provider
    
    async def analyze_image(
        self,
        image_data: bytes,
        image_mime_type: str = "image/png",
        context: Optional[str] = None
    ) -> DesignSystemResult:
        """
        Analyze a single image to extract design system tokens.
        
        Args:
            image_data: Raw image bytes
            image_mime_type: MIME type of the image
            context: Optional additional context (vibe name, description)
            
        Returns:
            DesignSystemResult with extracted design tokens
        """
        try:
            provider = self._get_provider()
            prompt = get_image_analysis_prompt()
            
            if context:
                prompt = f"{prompt}\n\n# Additional Context\n{context}"
            
            response = await provider.generate_with_image(
                prompt=prompt,
                image_data=image_data,
                image_mime_type=image_mime_type
            )
            
            parsed = self._parse_llm_response(response.content)
            
            return DesignSystemResult(
                success=True,
                data=parsed,
                provider=self._config.provider_type.value,
                model=self._config.model
            )
            
        except Exception as e:
            logger.exception(f"Image analysis failed: {str(e)}")
            return DesignSystemResult(
                success=False,
                error=str(e)
            )
    
    async def generate_from_images(
        self,
        images: list[tuple[bytes, str]],  # [(image_data, mime_type), ...]
        vibe_name: Optional[str] = None,
        vibe_description: Optional[str] = None
    ) -> DesignSystemResult:
        """
        Generate a design system from multiple images.
        
        Args:
            images: List of tuples (image_data, mime_type)
            vibe_name: Optional name for the design system
            vibe_description: Optional description of desired style
            
        Returns:
            DesignSystemResult with merged design system
        """
        if not images:
            return DesignSystemResult(
                success=False,
                error="No images provided"
            )
        
        context = ""
        if vibe_name:
            context += f"- Design System Name: {vibe_name}\n"
        if vibe_description:
            context += f"- Style Description: {vibe_description}\n"
        
        results = []
        
        for image_data, mime_type in images:
            result = await self.analyze_image(
                image_data=image_data,
                image_mime_type=mime_type,
                context=context if context else None
            )
            
            if result.success and result.data:
                results.append(result.data)
        
        if not results:
            return DesignSystemResult(
                success=False,
                error="Failed to analyze any images"
            )
        
        # Merge results
        merged = self._merge_results(results)
        
        # Add metadata
        merged['metadata'] = {
            'name': vibe_name or 'Untitled Design System',
            'description': vibe_description or '',
            'images_analyzed': len(results),
            'provider': self._config.provider_type.value if self._config else None,
            'model': self._config.model if self._config else None
        }
        
        return DesignSystemResult(
            success=True,
            data=merged,
            provider=self._config.provider_type.value if self._config else None,
            model=self._config.model if self._config else None
        )
    
    def _parse_llm_response(self, content: str) -> dict:
        """
        Parse LLM response content to extract JSON with automatic repair.
        
        Uses json_repair to handle:
        - Markdown code blocks
        - Missing quotes, commas, brackets
        - Trailing commas
        - Single quotes instead of double quotes
        - Invalid JSON values
        
        Args:
            content: Raw LLM response content
            
        Returns:
            Parsed dict or dict with raw_response if parsing fails
        """
        try:
            result = repair_json(content)
            
            # repair_json might return a string if content is already valid JSON string
            if isinstance(result, str):
                result = json.loads(result)
            
            if not isinstance(result, dict):
                logger.warning(f"repair_json returned {type(result).__name__}, expected dict")
                return {"raw_response": content}
                
            return result
        except Exception as e:
            logger.warning(f"Failed to parse/repair LLM response: {e}")
            logger.debug(f"Raw content preview: {content[:500]}...")
            return {"raw_response": content}
    
    def _merge_results(self, results: list[dict]) -> dict:
        """
        Merge multiple design system results into one.
        
        Args:
            results: List of design system dicts
            
        Returns:
            Merged design system dict
        """
        if not results:
            return {}
        
        if len(results) == 1:
            return results[0]
        
        # Use first result as base
        merged = results[0].copy()
        
        # Merge color values (take first non-empty)
        if 'colors' in merged:
            for r in results[1:]:
                if 'colors' in r:
                    for key, value in r['colors'].items():
                        if key not in merged['colors'] or not merged['colors'][key]:
                            merged['colors'][key] = value
        
        # Merge style rules
        if 'styleRules' in merged:
            all_rules = set(merged.get('styleRules', []))
            for r in results[1:]:
                all_rules.update(r.get('styleRules', []))
            merged['styleRules'] = list(all_rules)
        
        return merged


def generate_css_variables(design_system: dict) -> str:
    """
    Generate CSS custom properties from a design system.
    
    Args:
        design_system: Design system dict
        
    Returns:
        CSS string with custom properties
    """
    css_lines = [":root {"]
    
    # Colors
    colors = design_system.get('colors', {})
    color_mapping = {
        'primary': '--color-primary',
        'secondary': '--color-secondary',
        'background': '--bg-canvas',
        'surface': '--bg-surface',
        'textPrimary': '--text-primary',
        'textSecondary': '--text-secondary',
        'textTertiary': '--text-tertiary',
        'border': '--border-default',
        'success': '--color-success',
        'warning': '--color-warning',
        'error': '--color-error',
    }
    
    for key, var_name in color_mapping.items():
        if key in colors and colors[key]:
            css_lines.append(f"  {var_name}: {colors[key]};")
    
    # Typography
    typography = design_system.get('typography', {})
    if typography.get('fontFamily'):
        css_lines.append(f"  --font-sans: {typography['fontFamily']};")
    if typography.get('baseFontSize'):
        css_lines.append(f"  --text-body-size: {typography['baseFontSize']};")
    if typography.get('fontWeightBold'):
        css_lines.append(f"  --font-weight-heading: {typography['fontWeightBold']};")
    if typography.get('fontWeightRegular'):
        css_lines.append(f"  --font-weight-body: {typography['fontWeightRegular']};")
    
    # Border Radius
    border_radius = design_system.get('borderRadius', {})
    if border_radius.get('medium'):
        css_lines.append(f"  --radius-md: {border_radius['medium']};")
    
    # Shadows
    shadows = design_system.get('shadows', {})
    shadow_mapping = {
        'level1': '--shadow-sm',
        'level2': '--shadow-md',
        'level3': '--shadow-lg',
    }
    for key, var_name in shadow_mapping.items():
        if key in shadows and shadows[key]:
            css_lines.append(f"  {var_name}: {shadows[key]};")
    
    css_lines.append("}")
    
    return "\n".join(css_lines)


def generate_tailwind_config(design_system: dict) -> dict:
    """
    Generate Tailwind CSS configuration from a design system.
    
    Args:
        design_system: Design system dict
        
    Returns:
        Dict suitable for tailwind.config.js theme extension
    """
    config = {
        "colors": {},
        "fontFamily": {},
        "borderRadius": {},
        "boxShadow": {},
    }
    
    # Colors
    colors = design_system.get('colors', {})
    config["colors"] = {
        "primary": colors.get('primary'),
        "secondary": colors.get('secondary'),
        "background": colors.get('background'),
        "surface": colors.get('surface'),
        "foreground": colors.get('textPrimary'),
        "muted": colors.get('textSecondary'),
        "success": colors.get('success'),
        "warning": colors.get('warning'),
        "error": colors.get('error'),
    }
    # Remove None values
    config["colors"] = {k: v for k, v in config["colors"].items() if v}
    
    # Typography
    typography = design_system.get('typography', {})
    if typography.get('fontFamily'):
        config["fontFamily"]["sans"] = [typography['fontFamily']]
    
    # Border Radius
    border_radius = design_system.get('borderRadius', {})
    config["borderRadius"] = {k: v for k, v in border_radius.items() if v}
    
    # Shadows
    shadows = design_system.get('shadows', {})
    shadow_mapping = {'level1': 'sm', 'level2': 'md', 'level3': 'lg'}
    for src, dest in shadow_mapping.items():
        if src in shadows and shadows[src]:
            config["boxShadow"][dest] = shadows[src]
    
    return config
