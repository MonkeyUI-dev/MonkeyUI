import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { ClipboardDocumentIcon, CheckIcon, PencilIcon, EyeIcon } from '@heroicons/react/24/outline'
import { Layers } from 'lucide-react'
import { Textarea } from '@/components/ui/textarea'

const AestheticIcon = Layers

export default function AestheticAnalysisPanel({ aestheticData, isEmpty, isAnalyzing, onAestheticDataChange }) {
  const { t } = useTranslation()
  const [copied, setCopied] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [editValue, setEditValue] = useState('')

  const handleCopy = async () => {
    if (!aestheticData) return
    try {
      await navigator.clipboard.writeText(aestheticData)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const handleEdit = () => {
    setEditValue(aestheticData || '')
    setIsEditing(true)
  }

  const handleSaveEdit = () => {
    if (onAestheticDataChange) {
      onAestheticDataChange(editValue)
    }
    setIsEditing(false)
  }

  const handleCancelEdit = () => {
    setIsEditing(false)
    setEditValue('')
  }

  // Show empty state when no data and not analyzing
  if (isEmpty) {
    return (
      <div className="space-y-4">
        <div 
          className="rounded-xl p-12 flex flex-col items-center justify-center min-h-[400px]"
          style={{ backgroundColor: 'var(--bg-canvas)', border: '1px solid var(--border-subtle)' }}
        >
          <AestheticIcon className="size-16 mb-4" style={{ color: 'var(--text-tertiary)' }} />
          <p 
            className="text-sm font-medium mb-1 text-center"
            style={{ color: 'var(--text-secondary)' }}
          >
            {t('vibeStudio.aesthetic.noAnalysisYet')}
          </p>
          <p 
            className="text-xs text-center max-w-xs"
            style={{ color: 'var(--text-tertiary)' }}
          >
            {t('vibeStudio.aesthetic.uploadAndAnalyze')}
          </p>
        </div>
      </div>
    )
  }

  // Show loading state if analyzing without data yet
  if (isAnalyzing && !aestheticData) {
    return (
      <div className="space-y-4">
        <div 
          className="rounded-xl p-12 flex flex-col items-center justify-center min-h-[400px]"
          style={{ backgroundColor: 'var(--bg-canvas)', border: '1px solid var(--border-subtle)' }}
        >
          <div className="animate-spin size-8 border-2 border-[var(--accent-mint)] border-t-transparent rounded-full mb-4" />
          <p 
            className="text-sm font-medium"
            style={{ color: 'var(--text-secondary)' }}
          >
            {t('vibeStudio.aesthetic.analyzing')}
          </p>
        </div>
      </div>
    )
  }

  // If no data still, show nothing
  if (!aestheticData) {
    return null
  }

  return (
    <div className="space-y-4">
      {/* Main content area */}
      <div 
        className="rounded-xl overflow-hidden"
        style={{ border: '1px solid var(--border-subtle)' }}
      >
        {/* Header with actions */}
        <div 
          className="flex items-center justify-between px-4 py-2.5"
          style={{ 
            backgroundColor: 'var(--bg-surface)', 
            borderBottom: '1px solid var(--border-subtle)' 
          }}
        >
          <div className="flex items-center gap-2">
            <AestheticIcon className="size-4" style={{ color: 'var(--accent-blue)' }} />
            <span 
              className="text-xs font-medium"
              style={{ color: 'var(--text-tertiary)' }}
            >
              {t('vibeStudio.aesthetic.contextPack')}
            </span>
          </div>
          <div className="flex items-center gap-1">
            {/* Toggle edit/preview */}
            <button
              onClick={isEditing ? handleCancelEdit : handleEdit}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium hover:bg-[#F5F0FF] transition-colors"
              style={{ color: 'var(--text-secondary)' }}
            >
              {isEditing ? (
                <>
                  <EyeIcon className="size-3.5" />
                  <span>{t('vibeStudio.aesthetic.preview')}</span>
                </>
              ) : (
                <>
                  <PencilIcon className="size-3.5" />
                  <span>{t('common.edit')}</span>
                </>
              )}
            </button>
            {/* Copy button */}
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium hover:bg-[#F5F0FF] transition-colors"
              style={{ color: 'var(--text-secondary)' }}
            >
              {copied ? (
                <>
                  <CheckIcon className="size-3.5" style={{ color: 'var(--color-success)' }} />
                  <span style={{ color: 'var(--color-success)' }}>{t('common.copied')}</span>
                </>
              ) : (
                <>
                  <ClipboardDocumentIcon className="size-3.5" />
                  <span>{t('common.copy')}</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Content: Edit mode or Markdown preview */}
        {isEditing ? (
          <div className="p-4" style={{ backgroundColor: 'var(--bg-canvas)' }}>
            <Textarea
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              className="min-h-[500px] font-mono leading-relaxed resize-y"
            />
            <div className="flex justify-end gap-2 mt-3">
              <button
                onClick={handleCancelEdit}
                className="px-3 py-1.5 rounded-md text-xs font-medium transition-colors"
                style={{ color: 'var(--text-secondary)', border: '1px solid var(--border-default)' }}
              >
                {t('common.cancel')}
              </button>
              <button
                onClick={handleSaveEdit}
                className="px-3 py-1.5 rounded-md text-xs font-medium transition-colors"
                style={{ 
                  backgroundColor: 'var(--btn-primary-bg)', 
                  color: 'var(--btn-primary-fg)' 
                }}
              >
                {t('common.save')}
              </button>
            </div>
          </div>
        ) : (
          <div 
            className="p-6 overflow-y-auto aesthetic-markdown"
            style={{ backgroundColor: 'var(--bg-canvas)', maxHeight: '600px' }}
          >
            <ReactMarkdown 
              remarkPlugins={[remarkGfm]}
              components={{
                h1: ({children}) => (
                  <h1 className="text-2xl font-extrabold mb-3 mt-0" style={{ color: 'var(--accent-blue)' }}>{children}</h1>
                ),
                h2: ({children}) => (
                  <h2 className="text-lg font-bold mb-2 mt-6 pb-1" style={{ color: 'var(--text-primary)', borderBottom: '1px solid var(--border-subtle)' }}>{children}</h2>
                ),
                h3: ({children}) => (
                  <h3 className="text-sm font-semibold mb-1 mt-4" style={{ color: 'var(--text-primary)' }}>{children}</h3>
                ),
                p: ({children}) => (
                  <p className="text-sm leading-relaxed mb-3" style={{ color: 'var(--text-secondary)' }}>{children}</p>
                ),
                strong: ({children}) => (
                  <strong className="font-semibold" style={{ color: 'var(--text-primary)' }}>{children}</strong>
                ),
                ul: ({children}) => (
                  <ul className="text-sm mb-3 ml-4 space-y-1 list-disc" style={{ color: 'var(--text-secondary)' }}>{children}</ul>
                ),
                ol: ({children}) => (
                  <ol className="text-sm mb-3 ml-4 space-y-1 list-decimal" style={{ color: 'var(--text-secondary)' }}>{children}</ol>
                ),
                li: ({children}) => (
                  <li className="text-sm leading-relaxed">{children}</li>
                ),
                blockquote: ({children}) => (
                  <blockquote className="pl-4 my-3 text-sm italic" style={{ borderLeft: '3px solid var(--accent-blue)', color: 'var(--text-tertiary)' }}>{children}</blockquote>
                ),
                code: ({inline, children}) => 
                  inline ? (
                    <code className="px-1.5 py-0.5 rounded text-xs font-mono" style={{ backgroundColor: 'var(--bg-surface)', color: 'var(--accent-blue)' }}>{children}</code>
                  ) : (
                    <code className="block p-3 rounded-lg text-xs font-mono leading-relaxed overflow-x-auto my-2" style={{ backgroundColor: 'var(--bg-surface)', color: 'var(--text-primary)' }}>{children}</code>
                  ),
                hr: () => (
                  <hr className="my-4" style={{ borderColor: 'var(--border-subtle)' }} />
                ),
              }}
            >
              {aestheticData}
            </ReactMarkdown>
          </div>
        )}
      </div>

      {/* Helpful note */}
      <p 
        className="text-xs"
        style={{ color: 'var(--text-tertiary)' }}
      >
        {t('vibeStudio.aesthetic.description')}
      </p>
    </div>
  )
}
