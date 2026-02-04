"""
Prompt templates for design system generation.

This module provides utilities to load prompt templates from markdown files,
including support for multi-step analysis workflow with style-specific prompts.
"""
import os
from pathlib import Path
from functools import lru_cache


PROMPTS_DIR = Path(__file__).parent


# =============================================================================
# Style-Specific Guidelines for Different Visual Patterns
# =============================================================================

STYLE_GUIDELINES = {
    "neumorphism": """
## Neumorphism-Specific Extraction Guidelines

### Shadow System (Critical for Neumorphism)
- **Light Shadow**: Extract the lighter shadow (usually white/cream with ~0.5-0.8 opacity)
  - Position: typically top-left (-X, -Y)
  - Color: usually rgba(255,255,255,0.5-0.8)
- **Dark Shadow**: Extract the darker shadow
  - Position: typically bottom-right (+X, +Y)
  - Color: usually 10-20% darker than background with 0.3-0.6 opacity
- **Shadow Distance**: Usually 8-20px offset
- **Blur Radius**: Usually 15-30px

### Surface Colors
- Surface colors are very close to background (within 2-5% lightness difference)
- Look for subtle color temperature shifts (slightly warmer or cooler)

### Pressed/Active States
- Check if shadows invert (become inset) for pressed states
- Inner shadow parameters are crucial for pressed state recreation

### Example CSS Pattern:
```css
box-shadow: 
  -8px -8px 20px rgba(255,255,255,0.7),
  8px 8px 20px rgba(163,177,198,0.6);
/* Pressed state: */
box-shadow: 
  inset 4px 4px 10px rgba(163,177,198,0.5),
  inset -4px -4px 10px rgba(255,255,255,0.5);
```
""",
    
    "glassmorphism": """
## Glassmorphism-Specific Extraction Guidelines

### Backdrop Effects (Critical)
- **Blur Amount**: Extract backdrop-filter blur value (typically 10-40px)
- **Background Opacity**: Usually 0.1-0.4 for the frosted effect
- **Saturation**: Sometimes backdrop-filter includes saturate() (100-180%)

### Border Highlights
- Look for subtle top/left border highlights (1px, white with 0.1-0.3 opacity)
- Sometimes includes gradient borders for the "light refraction" effect

### Background Colors
- Extract the rgba values with precise alpha channels
- Background is usually white or light color with very low opacity

### Layer Detection
- Identify what's visible through the glass (background gradients, images, etc.)
- Note the contrast between glass surface and underlying content

### Example CSS Pattern:
```css
background: rgba(255, 255, 255, 0.15);
backdrop-filter: blur(20px) saturate(180%);
border: 1px solid rgba(255, 255, 255, 0.2);
border-radius: 16px;
```
""",
    
    "gradient": """
## Gradient-Specific Extraction Guidelines

### Gradient Analysis (Critical)
- **Type**: Linear, radial, or conic gradient
- **Direction/Angle**: Precise angle in degrees (e.g., 135deg, 45deg)
- **Color Stops**: Extract each color with its position percentage
- **Transitions**: Note if transitions are smooth or have hard stops

### Color Sampling for Gradients
- Sample at least 3-5 points along the gradient path
- Note the transition smoothness between colors
- Identify if colors are vibrant/saturated or muted

### Common Gradient Patterns
- Diagonal gradients (135deg is very popular)
- Radial gradients from center or corner
- Multi-stop gradients with 3+ colors

### Example CSS Pattern:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f64f59 100%);
/* or */
background: radial-gradient(circle at 30% 30%, #ff9a9e 0%, #fecfef 100%);
```
""",
    
    "material": """
## Material Design-Specific Extraction Guidelines

### Elevation System (Critical)
- **Level 1** (Cards): 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)
- **Level 2** (Raised buttons): 0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23)
- **Level 3** (Dialogs): 0 10px 20px rgba(0,0,0,0.19), 0 6px 6px rgba(0,0,0,0.23)
- Note: Material often uses dual-shadow (key light + ambient)

### Color System
- Primary and secondary colors are usually from Material color palette
- Look for the 500 shade as primary, with 700 for hover states
- Surface colors follow the spec (background/surface/error)

### Corner Radius
- Material 2: Often 4px for small, 8px for medium
- Material 3: Larger radii (8px, 12px, 16px, 28px)

### State Layers
- Hover: +4% surface tint overlay
- Focus: +12% surface tint overlay
- Pressed: +12% surface tint overlay

### Example CSS Pattern:
```css
box-shadow: 0 2px 4px rgba(0,0,0,0.14), 
            0 3px 4px rgba(0,0,0,0.12), 
            0 1px 5px rgba(0,0,0,0.20);
border-radius: 8px;
```
""",
    
    "playful": """
## Playful/Organic Style-Specific Guidelines

### Extreme Rounded Corners (Signature Feature)
- Cards: Usually 24px-50px radius
- Buttons: Often "pill" shape (height/2 or 9999px)
- Elements appear "inflated" or "doughy"

### Typography (Critical)
- **Display Fonts**: Look for ultra-bold, bubble-like fonts
- **Stroke/Outline**: Headers may have solid stroke (4-6% of font-size)
- **Letter Spacing**: Increased (+0.03em to +0.05em) to prevent letters from touching
- Font weights: Usually 700-900 for headings

### Color Blocking
- High-contrast color combinations
- Bold, saturated colors
- "Delicious" color palette (food/candy-inspired)

### Shadows
- Usually very subtle "ghost shadows"
- Example: 0 10px 30px rgba(0,0,0,0.05)
- Sometimes no shadows at all (relying on color contrast)

### Example CSS Pattern:
```css
border-radius: 50px;
font-weight: 800;
letter-spacing: 0.05em;
-webkit-text-stroke: 2px currentColor;
paint-order: stroke fill;
box-shadow: 0 10px 30px rgba(0,0,0,0.05);
```
""",
    
    "flat": """
## Flat/Minimal Style-Specific Guidelines

### Shadows
- No shadows OR extremely subtle (0 1px 2px rgba(0,0,0,0.05))
- Relies on color and spacing for hierarchy

### Color System
- Clean, clear colors without gradients
- High contrast between elements
- Often monochromatic or limited palette

### Borders
- May use borders instead of shadows for separation
- Usually 1px solid with subtle color

### Typography
- Clean sans-serif fonts
- Regular weights (400-600)
- Clear hierarchy through size, not decoration

### Spacing
- Generous whitespace
- Consistent spacing rhythm (often 8px grid)

### Example CSS Pattern:
```css
background: #ffffff;
border: 1px solid #e5e7eb;
border-radius: 8px;
/* No shadows */
```
""",
    
    "general": """
## General Extraction Guidelines

Since no specific visual pattern was strongly detected, please:

1. **Analyze Shadows Carefully**: Note shadow type, color, blur, spread
2. **Check for Transparency**: Look for rgba values, backdrop effects
3. **Identify Dominant Pattern**: Even mixed designs lean toward one style
4. **Document Uncertainty**: Use styleRules to note ambiguous elements

Focus on extracting accurate values even if the overall style is eclectic.
"""
}


@lru_cache(maxsize=32)
def load_prompt(name: str) -> str:
    """
    Load a prompt template from a markdown file.
    
    Args:
        name: The name of the prompt file (without .md extension)
        
    Returns:
        The content of the prompt file as a string
        
    Raises:
        FileNotFoundError: If the prompt file doesn't exist
    """
    prompt_path = PROMPTS_DIR / f"{name}.md"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt template '{name}' not found at {prompt_path}")
    
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def get_image_analysis_prompt() -> str:
    """Get the image analysis prompt for extracting design systems from images."""
    return load_prompt("image_analysis")


def get_single_step_analysis_prompt() -> str:
    """
    Get the single-step design system analysis prompt.
    
    This prompt instructs the LLM to:
    - Use three-point sampling for accurate color extraction
    - Extract typography, buttons, cards, spacing, and iconography
    - Generate an HTML verification page with CSS variables
    """
    return load_prompt("design_system_single_step")


def get_json_analysis_prompt() -> str:
    """
    Get the JSON-only design system analysis prompt.
    
    This prompt instructs the LLM to output structured JSON
    containing design tokens without any HTML. Used with
    structured output features of Gemini and OpenRouter.
    """
    return load_prompt("design_system_json")


def get_design_system_prompt() -> str:
    """Get the base design system prompt template."""
    return load_prompt("design_system_analysis")


def get_visual_style_detection_prompt() -> str:
    """
    Get the visual style detection prompt for Step 1 of the workflow.
    This prompt quickly identifies the dominant visual pattern.
    """
    return load_prompt("visual_style_detection")


def get_style_specific_prompt(visual_style: str) -> str:
    """
    Get a style-specific analysis prompt for Step 2 of the workflow.
    
    Args:
        visual_style: The detected visual style (neumorphism, glassmorphism, 
                     flat, gradient, material, playful, general)
    
    Returns:
        Customized prompt with style-specific guidelines embedded
    """
    # Load the template
    template = load_prompt("style_specific_analysis")
    
    # Get style-specific guidelines
    guidelines = STYLE_GUIDELINES.get(visual_style, STYLE_GUIDELINES["general"])
    
    # Replace placeholders
    prompt = template.replace("{visual_style}", visual_style)
    prompt = prompt.replace("{style_guidelines}", guidelines)
    
    return prompt


def get_style_guidelines(visual_style: str) -> str:
    """
    Get just the style-specific guidelines without the full prompt.
    Useful for appending to existing prompts.
    
    Args:
        visual_style: The detected visual style
        
    Returns:
        Style-specific extraction guidelines
    """
    return STYLE_GUIDELINES.get(visual_style, STYLE_GUIDELINES["general"])


def list_available_prompts() -> list[str]:
    """List all available prompt templates."""
    return [
        f.stem for f in PROMPTS_DIR.glob("*.md")
        if f.stem != "__init__"
    ]


def list_supported_styles() -> list[str]:
    """List all supported visual styles."""
    return list(STYLE_GUIDELINES.keys())

