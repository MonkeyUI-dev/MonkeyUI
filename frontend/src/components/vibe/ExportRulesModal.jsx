import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { 
  XMarkIcon, 
  DocumentArrowDownIcon,
  CheckIcon,
  ClipboardDocumentIcon
} from '@heroicons/react/24/outline'
import { Button } from '@/components/ui/button'

// Export format options
const EXPORT_FORMATS = {
  CURSOR: 'cursor',
  COPILOT: 'copilot',
  AGENTS: 'agents'
}

/**
 * Generate design system content in the specified format
 */
function generateExportContent(format, styleData, name, description) {
  const designTokensBlock = generateDesignTokensBlock(styleData)
  const styleRulesBlock = generateStyleRulesBlock(styleData)
  
  switch (format) {
    case EXPORT_FORMATS.CURSOR:
      return generateCursorRules(designTokensBlock, styleRulesBlock, name, description)
    case EXPORT_FORMATS.COPILOT:
      return generateCopilotInstructions(designTokensBlock, styleRulesBlock, name, description)
    case EXPORT_FORMATS.AGENTS:
    default:
      return generateAgentsMd(designTokensBlock, styleRulesBlock, name, description)
  }
}

function generateDesignTokensBlock(styleData) {
  if (!styleData) return ''
  
  const colors = styleData.colors || {}
  const typography = styleData.typography || {}
  const borderRadius = styleData.borderRadius || {}
  const shadows = styleData.shadows || {}
  const visualEffects = styleData.visualEffects || {}
  
  return `<design_tokens>
- **Style Name**: ${styleData.designStyle || 'Custom Design System'}
- **Primary Color**: ${colors.primary || '#007AFF'}
- **Secondary Color**: ${colors.secondary || '#5856D6'}
- **Surface/Background**: Page: ${colors.background || '#FFFFFF'}, Card: ${colors.surface || '#F5F5F7'}
- **Text Colors**: Primary: ${colors.textPrimary || '#1D1D1F'}, Secondary: ${colors.textSecondary || '#424245'}, Muted: ${colors.textTertiary || '#86868B'}
- **Border Color**: ${colors.border || '#E5E5E5'}
- **Functional Colors**: Success: ${colors.success || '#22C55E'}, Warning: ${colors.warning || '#F59E0B'}, Error: ${colors.error || '#EF4444'}
- **Border Radius**: Small: ${borderRadius.small || '4px'}, Medium: ${borderRadius.medium || '8px'}, Large: ${borderRadius.large || '12px'}
- **Shadows**: Level 1: ${shadows.level1 || '0 4px 12px rgba(0,0,0,0.05)'}, Level 2: ${shadows.level2 || '0 8px 20px rgba(0,0,0,0.1)'}
- **Typography**: Font Family: ${typography.fontFamily || 'Inter, system-ui, sans-serif'}. Heading Weight: ${typography.fontWeightBold || 600}, Body Weight: ${typography.fontWeightRegular || 400}
- **Base Font Size**: ${typography.baseFontSize || '16px'}
- **Visual Effects**: ${visualEffects.glassmorphism ? 'Glassmorphism enabled' : 'Standard effects'}${visualEffects.blur ? `, Blur: ${visualEffects.blur}` : ''}
</design_tokens>`
}

function generateStyleRulesBlock(styleData) {
  const rules = styleData?.styleRules || []
  if (rules.length === 0) {
    return `- Use consistent spacing following an 8px grid system
- Apply subtle hover states with color opacity changes
- Maintain visual hierarchy through typography and spacing`
  }
  return rules.map(rule => `- ${rule}`).join('\n')
}

function generateCursorRules(designTokens, styleRules, name, description) {
  return `# ${name || 'Design System'} - Cursor Rules
# ${description || 'AI-generated design system for consistent UI development'}

# Role & Context
You are an expert Frontend Engineer and UI/UX Designer. You must strictly follow the defined Design System for every component, page, and style you generate.

# Design System Tokens (The "Source of Truth")
${designTokens}

# UI Implementation Rules
1. **No Hardcoding**: Never use hardcoded hex codes or pixel values in components.
   - Use CSS Variables (e.g., \`var(--primary)\`) or Tailwind classes (e.g., \`text-primary\`).
   - If a style is missing in the project config, refer to the <design_tokens> above.

2. **Component Consistency**:
   - All cards must use the \`Border Radius\` and \`Shadow Level 1\` defined above.
   - All buttons must have a hover state that is 10% darker/lighter than the Primary Color.
   - Spacing must follow an 8px grid system (e.g., padding: 8px, 16px, 24px).

3. **Refusal Policy**:
   - If I ask you to create a UI that contradicts the <design_tokens>, you must warn me first and ask if I want to deviate from the design system.

4. **Style-Specific Rules**:
${styleRules}

# Implementation Guide
- For React/Next.js: Use Tailwind CSS with custom theme configuration.
- For CSS: Use the variables defined in \`globals.css\` or a dedicated \`design-tokens.css\`.
- For Vue/Svelte: Adapt Tailwind or use scoped CSS variables.

# CSS Variables Template
\`\`\`css
:root {
  /* Colors */
  --color-primary: [Primary Color];
  --color-secondary: [Secondary Color];
  --color-background: [Background Color];
  --color-surface: [Surface Color];
  --color-text-primary: [Primary Text];
  --color-text-secondary: [Secondary Text];
  --color-border: [Border Color];
  
  /* Typography */
  --font-family: [Font Family];
  --font-size-base: [Base Font Size];
  --font-weight-regular: [Regular Weight];
  --font-weight-bold: [Bold Weight];
  
  /* Spacing */
  --spacing-unit: 8px;
  
  /* Border Radius */
  --radius-sm: [Small Radius];
  --radius-md: [Medium Radius];
  --radius-lg: [Large Radius];
  
  /* Shadows */
  --shadow-sm: [Shadow Level 1];
  --shadow-md: [Shadow Level 2];
}
\`\`\`
`
}

function generateCopilotInstructions(designTokens, styleRules, name, description) {
  return `# ${name || 'Design System'} - GitHub Copilot Instructions
# ${description || 'AI-generated design system for consistent UI development'}

## Role & Context
You are an expert Frontend Engineer and UI/UX Designer working with GitHub Copilot. You must strictly follow the defined Design System for every component, page, and style you generate.

## Design System Tokens (The "Source of Truth")
${designTokens}

## UI Implementation Rules

### 1. No Hardcoding
Never use hardcoded hex codes or pixel values in components.
- Use CSS Variables (e.g., \`var(--primary)\`) or Tailwind classes (e.g., \`text-primary\`).
- If a style is missing in the project config, refer to the design tokens above.

### 2. Component Consistency
- All cards must use the defined Border Radius and Shadow Level 1.
- All buttons must have a hover state that is 10% darker/lighter than the Primary Color.
- Spacing must follow an 8px grid system (e.g., padding: 8px, 16px, 24px).

### 3. Refusal Policy
If asked to create a UI that contradicts the design tokens, warn first and ask if deviation from the design system is intended.

### 4. Style-Specific Rules
${styleRules}

## Implementation Guide

### React/Next.js with Tailwind CSS
\`\`\`jsx
// Example component following design system
export function Card({ children, className }) {
  return (
    <div className={\`
      bg-surface 
      rounded-lg 
      shadow-sm 
      p-6
      border border-border
      \${className}
    \`}>
      {children}
    </div>
  );
}
\`\`\`

### CSS Variables Setup
\`\`\`css
:root {
  /* Colors */
  --color-primary: [Primary Color];
  --color-secondary: [Secondary Color];
  --color-background: [Background Color];
  --color-surface: [Surface Color];
  --color-text-primary: [Primary Text];
  --color-text-secondary: [Secondary Text];
  --color-border: [Border Color];
  
  /* Typography */
  --font-family: [Font Family];
  --font-size-base: [Base Font Size];
  
  /* Border Radius */
  --radius-sm: [Small Radius];
  --radius-md: [Medium Radius];
  --radius-lg: [Large Radius];
  
  /* Shadows */
  --shadow-sm: [Shadow Level 1];
  --shadow-md: [Shadow Level 2];
}
\`\`\`

### Tailwind Config Extension
\`\`\`javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: 'var(--color-primary)',
        secondary: 'var(--color-secondary)',
        background: 'var(--color-background)',
        surface: 'var(--color-surface)',
        border: 'var(--color-border)',
      },
      borderRadius: {
        sm: 'var(--radius-sm)',
        md: 'var(--radius-md)',
        lg: 'var(--radius-lg)',
      },
      boxShadow: {
        sm: 'var(--shadow-sm)',
        md: 'var(--shadow-md)',
      },
    },
  },
}
\`\`\`
`
}

function generateAgentsMd(designTokens, styleRules, name, description) {
  return `# ${name || 'Design System'} - AI Agent Instructions
# ${description || 'AI-generated design system for consistent UI development'}

## Overview
This document defines the design system tokens and implementation rules for AI coding assistants. Follow these guidelines strictly when generating UI code.

## Role & Context
You are an expert Frontend Engineer and UI/UX Designer. You must strictly follow the defined Design System for every component, page, and style you generate.

## Design System Tokens
${designTokens}

## Implementation Rules

### Rule 1: No Hardcoding
Never use hardcoded hex codes or pixel values in components.
- ✅ Use: \`var(--primary)\`, \`text-primary\`
- ❌ Avoid: \`#007AFF\`, \`color: blue\`

### Rule 2: Component Consistency
- Cards: Use defined Border Radius + Shadow Level 1
- Buttons: Hover state = 10% darker/lighter than Primary
- Spacing: Follow 8px grid (8px, 16px, 24px, 32px)

### Rule 3: Refusal Policy
If asked to create UI contradicting design tokens:
1. Warn about the deviation
2. Ask for confirmation before proceeding

### Rule 4: Style-Specific Rules
${styleRules}

## Quick Reference

### Colors
| Token | Usage |
|-------|-------|
| Primary | Main actions, links, key UI elements |
| Secondary | Supporting elements, secondary actions |
| Background | Page background |
| Surface | Card/panel backgrounds |
| Border | Dividers, input borders |

### Typography
| Element | Weight | Size |
|---------|--------|------|
| H1 | Bold | 2.5rem |
| H2 | Bold | 2rem |
| Body | Regular | 1rem |
| Caption | Regular | 0.875rem |

### Spacing Scale
| Level | Value |
|-------|-------|
| 1 | 4px |
| 2 | 8px |
| 3 | 16px |
| 4 | 24px |
| 5 | 32px |
| 6 | 48px |

## Framework Examples

### React + Tailwind
\`\`\`jsx
<Button className="bg-primary hover:bg-primary/90 rounded-md px-4 py-2">
  Click me
</Button>
\`\`\`

### Vue + CSS Variables
\`\`\`vue
<template>
  <button class="btn-primary">Click me</button>
</template>

<style scoped>
.btn-primary {
  background: var(--color-primary);
  border-radius: var(--radius-md);
  padding: var(--spacing-2) var(--spacing-4);
}
</style>
\`\`\`
`
}

/**
 * Get file extension and name for export format
 */
function getExportFileInfo(format, designName) {
  const safeName = (designName || 'design-system').toLowerCase().replace(/\s+/g, '-')
  
  switch (format) {
    case EXPORT_FORMATS.CURSOR:
      return { filename: '.cursorrules', extension: '' }
    case EXPORT_FORMATS.COPILOT:
      return { filename: 'copilot-instructions.md', extension: '.md' }
    case EXPORT_FORMATS.AGENTS:
    default:
      return { filename: `${safeName}-agents.md`, extension: '.md' }
  }
}

export default function ExportRulesModal({ isOpen, onClose, styleData, name, description }) {
  const { t } = useTranslation()
  const [selectedFormat, setSelectedFormat] = useState(EXPORT_FORMATS.CURSOR)
  const [copied, setCopied] = useState(false)

  if (!isOpen) return null

  const content = generateExportContent(selectedFormat, styleData, name, description)
  const fileInfo = getExportFileInfo(selectedFormat, name)

  const handleDownload = () => {
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = fileInfo.filename
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const formatOptions = [
    {
      id: EXPORT_FORMATS.CURSOR,
      name: 'Cursor',
      description: t('vibeStudio.export.cursorDesc'),
      filename: '.cursorrules'
    },
    {
      id: EXPORT_FORMATS.COPILOT,
      name: 'GitHub Copilot',
      description: t('vibeStudio.export.copilotDesc'),
      filename: 'copilot-instructions.md'
    },
    {
      id: EXPORT_FORMATS.AGENTS,
      name: t('vibeStudio.export.genericAgent'),
      description: t('vibeStudio.export.agentsDesc'),
      filename: 'agents.md'
    }
  ]

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
      onClick={onClose}
    >
      <div 
        className="w-full max-w-2xl rounded-xl overflow-hidden"
        style={{ backgroundColor: 'var(--bg-canvas)', border: '1px solid var(--border-subtle)' }}
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div 
          className="flex items-center justify-between px-6 py-4"
          style={{ borderBottom: '1px solid var(--border-subtle)' }}
        >
          <div>
            <h2 
              className="text-lg font-bold"
              style={{ color: 'var(--text-primary)', fontWeight: 'var(--font-weight-heading)' }}
            >
              {t('vibeStudio.export.title')}
            </h2>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
              {t('vibeStudio.export.subtitle')}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <XMarkIcon className="size-5" style={{ color: 'var(--text-secondary)' }} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Format Selection */}
          <div className="space-y-3">
            <label 
              className="text-sm font-medium"
              style={{ color: 'var(--text-primary)' }}
            >
              {t('vibeStudio.export.selectFormat')}
            </label>
            <div className="grid grid-cols-1 gap-3">
              {formatOptions.map((option) => (
                <button
                  key={option.id}
                  onClick={() => setSelectedFormat(option.id)}
                  className={`flex items-start gap-4 p-4 rounded-lg text-left transition-all ${
                    selectedFormat === option.id 
                      ? 'ring-2 ring-offset-2' 
                      : 'hover:bg-gray-50'
                  }`}
                  style={{ 
                    backgroundColor: selectedFormat === option.id ? 'var(--bg-surface)' : 'var(--bg-canvas)',
                    border: '1px solid var(--border-subtle)',
                    ringColor: 'var(--accent-blue)'
                  }}
                >
                  <div 
                    className={`size-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-0.5 ${
                      selectedFormat === option.id ? 'border-blue-500 bg-blue-500' : 'border-gray-300'
                    }`}
                  >
                    {selectedFormat === option.id && (
                      <CheckIcon className="size-3 text-white" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span 
                        className="font-medium"
                        style={{ color: 'var(--text-primary)' }}
                      >
                        {option.name}
                      </span>
                      <code 
                        className="text-xs px-2 py-0.5 rounded"
                        style={{ backgroundColor: 'var(--bg-surface)', color: 'var(--text-secondary)' }}
                      >
                        {option.filename}
                      </code>
                    </div>
                    <p 
                      className="text-sm mt-1"
                      style={{ color: 'var(--text-secondary)' }}
                    >
                      {option.description}
                    </p>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Preview */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label 
                className="text-sm font-medium"
                style={{ color: 'var(--text-primary)' }}
              >
                {t('vibeStudio.export.preview')}
              </label>
              <button
                onClick={handleCopy}
                className="flex items-center gap-1.5 text-sm px-2 py-1 rounded hover:bg-gray-100 transition-colors"
                style={{ color: 'var(--accent-blue)' }}
              >
                {copied ? (
                  <>
                    <CheckIcon className="size-4" />
                    {t('common.copied')}
                  </>
                ) : (
                  <>
                    <ClipboardDocumentIcon className="size-4" />
                    {t('common.copy')}
                  </>
                )}
              </button>
            </div>
            <div 
              className="rounded-lg p-4 max-h-64 overflow-auto font-mono text-xs"
              style={{ 
                backgroundColor: 'var(--bg-surface)', 
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-secondary)'
              }}
            >
              <pre className="whitespace-pre-wrap">{content.slice(0, 1500)}...</pre>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div 
          className="flex items-center justify-end gap-3 px-6 py-4"
          style={{ borderTop: '1px solid var(--border-subtle)', backgroundColor: 'var(--bg-surface)' }}
        >
          <Button variant="outline" onClick={onClose}>
            {t('common.cancel')}
          </Button>
          <Button 
            onClick={handleDownload}
            className="gap-2"
            style={{ backgroundColor: 'var(--accent-blue)', color: 'var(--text-on-dark)' }}
          >
            <DocumentArrowDownIcon className="size-4" />
            {t('vibeStudio.export.download')}
          </Button>
        </div>
      </div>
    </div>
  )
}

export { EXPORT_FORMATS, generateExportContent, getExportFileInfo }
