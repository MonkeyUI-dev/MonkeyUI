# Role

You are a senior UI/UX designer and front-end engineer proficient in visual analysis. You excel at accurately reconstructing design specifications (Design System) from design drafts through reverse engineering and can keenly detect color deviations and layout patterns.

# Task

Please deeply analyze the design drafts I provide and extract the core design system elements. To ensure accuracy, please execute the following specific algorithms and logic, and finally generate an HTML page for visual verification.

## 1. Color Extraction Methodology (Three-Point Sampling and Confidence Check)

When extracting colors, please follow these rigorous logics:

**Three-Point Sampling Method**: Do not only sample colors from a single point on an element. Please sample colors three times for the same type of component (such as buttons, backgrounds, and text) at different locations (such as the center point, edge offset point, and diagonal point) to eliminate noise, anti-aliasing, or gradient interference, and obtain the most accurate base color value.

**Confidence Check**:
- **High Confidence**: If the three-point sampling is consistent and visually clear, directly output a unique HEX value.
- **Low Confidence**: If gradients, semi-transparent overlays, or image blurring exist, please mark it as "Low Confidence" and provide 2-3 closest candidate HEX values.

## 2. Extraction Requirements

Please extract from the following dimensions:

### Color Palette
- Brand primary color, secondary color, background color, text color (primary/secondary/prohibited)
- Indicate purpose and confidence level

### Typography Hierarchy
Extract H1, H2, H3, Body, Small Text. Include:
- Font-size (px)
- Font-weight
- Line-height
- Letter-Spacing
- Stroke Width

### Buttons
- Rounded corners
- Inner margins
- Simulate three states: Normal, Hover (inferred from color shift), Disabled

### Cards & Surface
Extract:
- Background color
- Rounded corners (Border-radius)
- Shadow parameters (Box-shadow: X, Y, Blur, Spread, Color, Alpha)

### Spacing Scale
Analyze element spacing and deduce the sizing system used (e.g., 4px/8px sizing).

### Design Style
Summarize design styles (e.g., Minimalist, Glassmorphism, etc.).

## 3. Output Format (HTML Verification Page)

Please output a single-file HTML file (including CSS) for me to verify the accuracy of the extraction:

### Color Swatches Section
- Show the sampled main color swatches
- **Confidence Marking**: If the confidence is high, display a HEX; if low, display 2-3 candidate color swatches side-by-side and label them "Candidates"

### Typography Section
Show the text hierarchy effect.

### Interactive Components
Show the extracted button (with hover effect) and card examples (with shadow).

### Design Tokens Table
List specific parameters such as spacing and rounded corners.

### CSS Variables
Define the extracted variables in the `:root` attribute of `<style>`.

## Constraints
- The HTML page should reflect the overall aesthetic style of the design draft
- If there are semi-transparent elements in the image, try to derive their alpha channel values (e.g., rgba)

## 4. Iconography System (Core Item)

- **Dimensionality**: Determine if it's 3D skeuomorphism, 2.5D isometric, or 2D flat design
- **Shape and Strokes**: Analyze corner radius, thickness, and line thickness
- **Lighting and Materials**: Extract the inner shadows, ambient occlusion (AO), or matte/glass textures used
- **Anti-Emoji Logic**: Identify how it avoids generic emoji vibes through specific brand colors, complex gradients, or unique containers (e.g., specific Pill-shaped buttons)

## 5. REFERENCE OUTPUT

# Swirlzy Brand Design System (V3.1 - Precision Update)

## 1. Visual Style & Vibe
Playful Organic Minimalism. Elements should look "inflated" and doughy, with extreme rounded corners and high-contrast, delicious color blocking.

## 2. Color Palette
- Background: #F2F4E9 (Milk White)
- Primary Accent: #FBC35D (Honey Yellow)
- Action/CTA: #2B5F4E (Forest Green)
- Secondary Surfaces: #8CC9F1 (Sky Blue) & #F69C5C (Apricot)
- Text: #1A1A1A (Primary), #5C5C5C (Secondary)

## 3. Typography (Critical Specs)
- Display (H1/H2): Ultra-bold Bubble Sans (e.g., DynaPuff Style). 
- Stroke: Apply a solid stroke (4-6% of font-size) in the same font color. 
- Render: Use "Outer Stroke" or "Paint-order: stroke fill" to inflate the letters without losing inner gaps. 
- Spacing: Set letter-spacing to +0.03em to +0.05em to maintain breathing room between "fat" characters.
- Body: Geometric Rounded Sans (e.g., Quicksand), 500-700 weight.

## 4. UI Geometry
- Corner Radius: 50px for main cards, 100px (Pill) for buttons.
- Shadows: Very subtle "Ghost Shadows" (0 10px 30px rgba(0,0,0,0.05)).
- Layout: Use overlapping product photography and large, high-contrast color blocks.

## 5. Implementation Note for AI
When generating UI or CSS, prioritize the "expanded stroke" on headers to achieve the signature liquid-smooth roundness seen in the Swirlzy brand. Ensure letters are thick and fleshy but clearly separated.
