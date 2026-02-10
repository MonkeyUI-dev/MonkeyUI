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
function generateExportContent(format, styleData, aestheticAnalysis, name, description) {
  const designTokensBlock = generateDesignTokensBlock(styleData)
  
  switch (format) {
    case EXPORT_FORMATS.CURSOR:
      return generateCursorRules(designTokensBlock, aestheticAnalysis, name, description)
    case EXPORT_FORMATS.COPILOT:
      return generateCopilotInstructions(designTokensBlock, aestheticAnalysis, name, description)
    case EXPORT_FORMATS.AGENTS:
    default:
      return generateAgentsMd(designTokensBlock, aestheticAnalysis, name, description)
  }
}

function generateDesignTokensBlock(styleData) {
  if (!styleData) return ''
  
  const colors = styleData.colors || {}
  const typography = styleData.typography || {}
  const shadowDepth = styleData.shadowDepth ?? 0
  
  return `<design_tokens>
- **Primary Color**: ${colors.primary || 'N/A'}
- **Secondary Color**: ${colors.secondary || 'N/A'}
- **Background Color**: ${colors.background || 'N/A'}
- **Surface Color**: ${colors.surface || 'N/A'}
- **Typography**: Font Family: ${typography.fontFamily || typography.font_family || 'system-ui, sans-serif'}, Font Weight: ${typography.fontWeight || typography.font_weight || '400, 600, 700'}, Base Font Size: ${typography.baseFontSize || typography.base_font_size || '16px'}
- **Shadow Depth**: ${shadowDepth}/5 (${['Flat, no shadows', 'Very subtle shadows', 'Light shadows', 'Medium shadows', 'Pronounced shadows', 'Heavy/dramatic shadows'][shadowDepth] || 'Unknown'})
</design_tokens>`
}

function generateCursorRules(designTokens, aestheticAnalysis, name, description) {
  return `# ${name || 'Design System'} - Cursor Rules
# ${description || 'AI-generated design system for consistent UI development'}

# Role & Context
You are an expert Frontend Engineer and UI/UX Designer. You must strictly follow the defined Design System for every component, page, and style you generate.

# Design System Tokens (The "Source of Truth")
${designTokens}
${aestheticAnalysis ? `
# Aesthetic Guide (The "Design Soul")
The following aesthetic analysis captures the design's soul, mood, and stylistic DNA. Use this as creative context — pages should FEEL like they belong to the same design family without cloning the reference pixel-for-pixel.

${aestheticAnalysis}
` : ''}
# UI Implementation Rules
1. **No Hardcoding**: Never use hardcoded hex codes or pixel values in components.
   - Use CSS Variables (e.g., \`var(--primary)\`) or Tailwind classes (e.g., \`text-primary\`).
   - If a style is missing in the project config, refer to the <design_tokens> above.

2. **Component Consistency**:
   - Spacing must follow an 8px grid system (e.g., padding: 8px, 16px, 24px).
   - Apply the Shadow Depth level consistently across cards and elevated elements.
   - All buttons must have a hover state that is 10% darker/lighter than the Primary Color.

3. **Aesthetic Coherence**:
   - When generating new UI, always refer to the Aesthetic Guide for mood, material, and layout decisions.
   - Maintain the design's soul: follow the color grammar, typography rhythm, and layout patterns described above.
   - Respect the Anti-Patterns — avoid anything that would break the design's visual identity.

4. **Refusal Policy**:
   - If I ask you to create a UI that contradicts the <design_tokens> or the Aesthetic Guide, you must warn me first and ask if I want to deviate from the design system.

# CSS Variables Template
\`\`\`css
:root {
  /* Colors */
  --color-primary: [Primary Color];
  --color-secondary: [Secondary Color];
  --color-background: [Background Color];
  --color-surface: [Surface Color];
  
  /* Typography */
  --font-family: [Font Family];
  --font-size-base: [Base Font Size];
}
\`\`\`

# Implementation Guide
- For React/Next.js: Use Tailwind CSS with custom theme configuration.
- For CSS: Use the variables defined in \`globals.css\` or a dedicated \`design-tokens.css\`.
- For Vue/Svelte: Adapt Tailwind or use scoped CSS variables.
`
}

function generateCopilotInstructions(designTokens, aestheticAnalysis, name, description) {
  return `# ${name || 'Design System'} - GitHub Copilot Instructions
# ${description || 'AI-generated design system for consistent UI development'}

## Role & Context
You are an expert Frontend Engineer and UI/UX Designer working with GitHub Copilot. You must strictly follow the defined Design System for every component, page, and style you generate.

## Design System Tokens (The "Source of Truth")
${designTokens}
${aestheticAnalysis ? `
## Aesthetic Guide (The "Design Soul")
The following aesthetic analysis captures the design's soul, mood, and stylistic DNA. Use this as creative context — pages should FEEL like they belong to the same design family without cloning the reference pixel-for-pixel.

${aestheticAnalysis}
` : ''}
## UI Implementation Rules

### 1. No Hardcoding
Never use hardcoded hex codes or pixel values in components.
- Use CSS Variables (e.g., \`var(--primary)\`) or Tailwind classes (e.g., \`text-primary\`).
- If a style is missing in the project config, refer to the design tokens above.

### 2. Component Consistency
- Spacing must follow an 8px grid system (e.g., padding: 8px, 16px, 24px).
- Apply the Shadow Depth level consistently across cards and elevated elements.
- All buttons must have a hover state that is 10% darker/lighter than the Primary Color.

### 3. Aesthetic Coherence
- When generating new UI, always refer to the Aesthetic Guide for mood, material, and layout decisions.
- Maintain the design's soul: follow the color grammar, typography rhythm, and layout patterns described above.
- Respect the Anti-Patterns — avoid anything that would break the design's visual identity.

### 4. Refusal Policy
If asked to create a UI that contradicts the design tokens or the Aesthetic Guide, warn first and ask if deviation from the design system is intended.

## CSS Variables Setup
\`\`\`css
:root {
  /* Colors */
  --color-primary: [Primary Color];
  --color-secondary: [Secondary Color];
  --color-background: [Background Color];
  --color-surface: [Surface Color];
  
  /* Typography */
  --font-family: [Font Family];
  --font-size-base: [Base Font Size];
}
\`\`\`

## Implementation Guide
- For React/Next.js: Use Tailwind CSS with custom theme configuration.
- For CSS: Use the variables defined in \`globals.css\` or a dedicated \`design-tokens.css\`.
- For Vue/Svelte: Adapt Tailwind or use scoped CSS variables.
`
}

function generateAgentsMd(designTokens, aestheticAnalysis, name, description) {
  return `# ${name || 'Design System'} - AI Agent Instructions
# ${description || 'AI-generated design system for consistent UI development'}

## Overview
This document defines the design system tokens, aesthetic guide, and implementation rules for AI coding assistants. Follow these guidelines strictly when generating UI code.

## Role & Context
You are an expert Frontend Engineer and UI/UX Designer. You must strictly follow the defined Design System for every component, page, and style you generate.

## Design System Tokens
${designTokens}
${aestheticAnalysis ? `
## Aesthetic Guide (The "Design Soul")
The following aesthetic analysis captures the design's soul, mood, and stylistic DNA. Use this as creative context — pages should FEEL like they belong to the same design family without cloning the reference pixel-for-pixel.

${aestheticAnalysis}
` : ''}
## Implementation Rules

### Rule 1: No Hardcoding
Never use hardcoded hex codes or pixel values in components.
- ✅ Use: \`var(--primary)\`, \`text-primary\`
- ❌ Avoid: \`#007AFF\`, \`color: blue\`

### Rule 2: Component Consistency
- Spacing: Follow 8px grid (8px, 16px, 24px, 32px)
- Apply the Shadow Depth level consistently across cards and elevated elements
- Buttons: Hover state = 10% darker/lighter than Primary

### Rule 3: Aesthetic Coherence
- When generating new UI, always refer to the Aesthetic Guide for mood, material, and layout decisions
- Maintain the design's soul: follow the color grammar, typography rhythm, and layout patterns
- Respect the Anti-Patterns — avoid anything that would break the design's visual identity

### Rule 4: Refusal Policy
If asked to create UI contradicting design tokens or the Aesthetic Guide:
1. Warn about the deviation
2. Ask for confirmation before proceeding

## Quick Reference

### Colors
| Token | Usage |
|-------|-------|
| Primary | Main actions, links, key UI elements |
| Secondary | Supporting elements, secondary actions |
| Background | Page background |
| Surface | Card/panel backgrounds |

### Spacing Scale
| Level | Value |
|-------|-------|
| 1 | 4px |
| 2 | 8px |
| 3 | 16px |
| 4 | 24px |
| 5 | 32px |
| 6 | 48px |

## CSS Variables Template
\`\`\`css
:root {
  --color-primary: [Primary Color];
  --color-secondary: [Secondary Color];
  --color-background: [Background Color];
  --color-surface: [Surface Color];
  --font-family: [Font Family];
  --font-size-base: [Base Font Size];
}
\`\`\`

## Implementation Guide
- For React/Next.js: Use Tailwind CSS with custom theme configuration.
- For CSS: Use the variables defined in \`globals.css\` or a dedicated \`design-tokens.css\`.
- For Vue/Svelte: Adapt Tailwind or use scoped CSS variables.
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

export default function ExportRulesModal({ isOpen, onClose, styleData, aestheticAnalysis, name, description }) {
  const { t } = useTranslation()
  const [selectedFormat, setSelectedFormat] = useState(EXPORT_FORMATS.CURSOR)
  const [copied, setCopied] = useState(false)

  if (!isOpen) return null

  const content = generateExportContent(selectedFormat, styleData, aestheticAnalysis, name, description)
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
              <pre className="whitespace-pre-wrap">{content}</pre>
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
