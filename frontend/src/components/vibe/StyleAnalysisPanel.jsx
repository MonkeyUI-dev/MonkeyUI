import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline'

// Icons for each section
function ColorPaletteIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="10" />
      <circle cx="12" cy="12" r="4" fill="currentColor" />
    </svg>
  )
}

function TypographyIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M4 7V4h16v3" />
      <path d="M12 4v16" />
      <path d="M8 20h8" />
    </svg>
  )
}

function ShadowIcon({ className }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="3" width="14" height="14" rx="2" />
      <rect x="7" y="7" width="14" height="14" rx="2" fill="currentColor" opacity="0.3" />
    </svg>
  )
}

function StyleIcon({ className, ...props }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...props}>
      <path d="M12 2L2 7l10 5 10-5-10-5z" />
      <path d="M2 17l10 5 10-5" />
      <path d="M2 12l10 5 10-5" />
    </svg>
  )
}


// Collapsible Section Component
function CollapsibleSection({ title, icon: Icon, children, defaultOpen = false }) {
  const [isOpen, setIsOpen] = useState(defaultOpen)

  return (
    <div 
      className="rounded-xl overflow-hidden"
      style={{ backgroundColor: 'var(--bg-canvas)', border: '1px solid var(--border-subtle)' }}
    >
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-4 hover:bg-[#F5F0FF] transition-colors"
      >
        <div className="flex items-center gap-x-3">
          <Icon className="size-5" style={{ color: 'var(--accent-blue)' }} />
          <span 
            className="font-semibold"
            style={{ color: 'var(--text-primary)' }}
          >
            {title}
          </span>
        </div>
        {isOpen ? (
          <ChevronUpIcon className="size-5" style={{ color: 'var(--text-tertiary)' }} />
        ) : (
          <ChevronDownIcon className="size-5" style={{ color: 'var(--text-tertiary)' }} />
        )}
      </button>
      {isOpen && (
        <div className="px-4 pb-4">
          {children}
        </div>
      )}
    </div>
  )
}

// Color Swatch Component
function ColorSwatch({ label, color, onChange }) {
  const { t } = useTranslation()
  
  return (
    <div className="space-y-2">
      <span 
        className="text-xs font-medium"
        style={{ color: 'var(--text-tertiary)' }}
      >
        {label}
      </span>
      <div 
        className="flex items-center gap-x-3 p-3 rounded-lg"
        style={{ backgroundColor: 'var(--bg-surface)' }}
      >
        <div 
          className="size-8 rounded-md shrink-0"
          style={{ backgroundColor: color, border: '1px solid var(--border-subtle)' }}
        />
        <input
          type="text"
          value={color}
          onChange={(e) => onChange(e.target.value)}
          className="flex-1 bg-transparent text-sm font-mono outline-none"
          style={{ color: 'var(--text-primary)' }}
        />
      </div>
    </div>
  )
}

export default function StyleAnalysisPanel({ styleData, onStyleDataChange, isEmpty, isAnalyzing }) {
  const { t } = useTranslation()

  // Show empty state when no data and not analyzing
  if (isEmpty) {
    return (
      <div className="space-y-4">
        {/* Section Header */}
        <div className="flex items-center gap-x-2 mb-2">
          <StyleIcon className="size-5" style={{ color: 'var(--text-secondary)' }} />
          <span 
            className="text-xs font-semibold"
            style={{ color: 'var(--text-secondary)' }}
          >
            {t('vibeStudio.styleAnalysis')}
          </span>
        </div>

        {/* Empty State */}
        <div 
          className="rounded-xl p-12 flex flex-col items-center justify-center min-h-[400px]"
          style={{ backgroundColor: 'var(--bg-canvas)', border: '1px solid var(--border-subtle)' }}
        >
          <StyleIcon className="size-16 mb-4" style={{ color: 'var(--text-tertiary)' }} />
          <p 
            className="text-sm font-medium mb-1 text-center"
            style={{ color: 'var(--text-secondary)' }}
          >
            {t('vibeStudio.noAnalysisYet')}
          </p>
          <p 
            className="text-xs text-center max-w-xs"
            style={{ color: 'var(--text-tertiary)' }}
          >
            {t('vibeStudio.uploadAndAnalyze')}
          </p>
        </div>
      </div>
    )
  }

  // Show loading state if analyzing without data yet
  if (isAnalyzing && !styleData) {
    return (
      <div className="space-y-4">
        {/* Section Header */}
        <div className="flex items-center gap-x-2 mb-2">
          <StyleIcon className="size-5" style={{ color: 'var(--text-secondary)' }} />
          <span 
            className="text-xs font-semibold"
            style={{ color: 'var(--text-secondary)' }}
          >
            {t('vibeStudio.styleAnalysis')}
          </span>
        </div>

        {/* Analyzing State */}
        <div 
          className="rounded-xl p-12 flex flex-col items-center justify-center min-h-[400px]"
          style={{ backgroundColor: 'var(--bg-canvas)', border: '1px solid var(--border-subtle)' }}
        >
          <div className="animate-spin size-8 border-2 border-[#6B52E1] border-t-transparent rounded-full mb-4" />
          <p 
            className="text-sm font-medium"
            style={{ color: 'var(--text-secondary)' }}
          >
            {t('vibeStudio.analyzing')}
          </p>
        </div>
      </div>
    )
  }

  // If no style data still, show empty
  if (!styleData) {
    return null
  }

  const updateColor = (key, value) => {
    onStyleDataChange({
      ...styleData,
      colors: {
        ...(styleData.colors || {}),
        [key]: value
      }
    })
  }

  const updateTypography = (key, value) => {
    onStyleDataChange({
      ...styleData,
      typography: {
        ...(styleData.typography || {}),
        [key]: value
      }
    })
  }

  const updateShadow = (value) => {
    onStyleDataChange({
      ...styleData,
      shadowDepth: value
    })
  }

  return (
    <div className="space-y-4">
      {/* Section Header */}
      <div className="flex items-center gap-x-2 mb-2">
        <StyleIcon className="size-5" style={{ color: 'var(--text-secondary)' }} />
        <span 
          className="text-xs font-semibold"
          style={{ color: 'var(--text-secondary)' }}
        >
          {t('vibeStudio.styleAnalysis')}
        </span>
      </div>

      {/* Color Palette Section */}
      <CollapsibleSection 
        title={t('vibeStudio.colorPalette')} 
        icon={ColorPaletteIcon}
        defaultOpen={true}
      >
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <ColorSwatch 
              label={t('vibeStudio.primaryColor')} 
              color={styleData.colors?.primary || '#000000'}
              onChange={(v) => updateColor('primary', v)}
            />
            <ColorSwatch 
              label={t('vibeStudio.secondaryColor')} 
              color={styleData.colors?.secondary || '#000000'}
              onChange={(v) => updateColor('secondary', v)}
            />
            <ColorSwatch 
              label={t('vibeStudio.backgroundColor')} 
              color={styleData.colors?.background || '#FFFFFF'}
              onChange={(v) => updateColor('background', v)}
            />
            <ColorSwatch 
              label={t('vibeStudio.surfaceColor')} 
              color={styleData.colors?.surface || '#FFFFFF'}
              onChange={(v) => updateColor('surface', v)}
            />
          </div>
        </div>
      </CollapsibleSection>

      {/* Typography Section */}
      <CollapsibleSection 
        title={t('vibeStudio.typography')} 
        icon={TypographyIcon}
      >
        <div className="space-y-4">
          <div 
            className="p-3 rounded-lg"
            style={{ backgroundColor: 'var(--bg-surface)' }}
          >
            <label 
              className="text-xs font-medium block mb-2"
              style={{ color: 'var(--text-tertiary)' }}
            >
              {t('vibeStudio.fontFamily')}
            </label>
            <input
              type="text"
              value={styleData.typography?.fontFamily || ''}
              onChange={(e) => updateTypography('fontFamily', e.target.value)}
              className="w-full bg-transparent text-sm outline-none"
              style={{ color: 'var(--text-primary)' }}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div 
              className="p-3 rounded-lg"
              style={{ backgroundColor: 'var(--bg-surface)' }}
            >
              <label 
                className="text-xs font-medium block mb-2"
                style={{ color: 'var(--text-tertiary)' }}
              >
                {t('vibeStudio.fontWeight')}
              </label>
              <input
                type="text"
                value={styleData.typography?.fontWeight || ''}
                onChange={(e) => updateTypography('fontWeight', e.target.value)}
                className="w-full bg-transparent text-sm outline-none"
                style={{ color: 'var(--text-primary)' }}
              />
            </div>
            <div 
              className="p-3 rounded-lg"
              style={{ backgroundColor: 'var(--bg-surface)' }}
            >
              <label 
                className="text-xs font-medium block mb-2"
                style={{ color: 'var(--text-tertiary)' }}
              >
                {t('vibeStudio.baseFontSize')}
              </label>
              <input
                type="text"
                value={styleData.typography?.baseFontSize || ''}
                onChange={(e) => updateTypography('baseFontSize', e.target.value)}
                className="w-full bg-transparent text-sm outline-none"
                style={{ color: 'var(--text-primary)' }}
              />
            </div>
          </div>
        </div>
      </CollapsibleSection>

      {/* Shadows & Depth Section */}
      <CollapsibleSection 
        title={t('vibeStudio.shadowsDepth')} 
        icon={ShadowIcon}
      >
        <div 
          className="p-3 rounded-lg"
          style={{ backgroundColor: 'var(--bg-surface)' }}
        >
          <label 
            className="text-xs font-medium block mb-2"
            style={{ color: 'var(--text-tertiary)' }}
          >
            {t('vibeStudio.shadowLevel')}
          </label>
          <div className="flex items-center gap-x-4">
            <input
              type="range"
              min="0"
              max="5"
              value={styleData.shadowDepth ?? 0}
              onChange={(e) => updateShadow(parseInt(e.target.value))}
              className="flex-1"
            />
            <span 
              className="text-sm font-mono w-8 text-center"
              style={{ color: 'var(--text-primary)' }}
            >
              {styleData.shadowDepth ?? 0}
            </span>
          </div>
        </div>
      </CollapsibleSection>
    </div>
  )
}
