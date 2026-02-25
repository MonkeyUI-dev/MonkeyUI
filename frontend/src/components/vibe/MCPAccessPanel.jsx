import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Disclosure, DisclosureButton, DisclosurePanel } from '@headlessui/react'
import { 
  XMarkIcon, 
  ServerIcon,
  ClipboardDocumentIcon,
  CheckIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline'
import { Button } from '@/components/ui/button'

/**
 * MCP Access Panel - Displays MCP connection information for AI coding tools
 * Shows Streamable HTTP protocol configurations for VS Code Copilot and Cursor
 */
export default function MCPAccessPanel({ 
  isOpen, 
  onClose, 
  designSystemId, 
  designSystemName,
  apiKey 
}) {
  const { t } = useTranslation()
  const [copiedField, setCopiedField] = useState(null)

  if (!isOpen) return null

  // Get base URL for API endpoints
  const baseUrl = window.location.origin
  const serverName = `monkeyui-${(designSystemName || 'design-system').toLowerCase().replace(/\s+/g, '-')}`
  const mcpEndpoint = `${baseUrl}/api/v1/design-systems/mcp/${designSystemId}/`

  const handleCopy = async (text, field) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedField(field)
      setTimeout(() => setCopiedField(null), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  // VS Code Copilot configuration (Streamable HTTP)
  const vscodeConfig = `{
  "servers": {
    "${serverName}": {
      "type": "http",
      "url": "${mcpEndpoint}",
      "headers": {
        "Authorization": "Bearer ${apiKey || 'YOUR_API_KEY'}"
      }
    }
  }
}`

  // Cursor configuration (Streamable HTTP)
  const cursorConfig = `{
  "mcpServers": {
    "${serverName}": {
      "url": "${mcpEndpoint}",
      "headers": {
        "Authorization": "Bearer ${apiKey || 'YOUR_API_KEY'}"
      }
    }
  }
}`

  const sections = [
    {
      id: 'cursor',
      title: t('vibeStudio.mcp.cursorConfig'),
      description: t('vibeStudio.mcp.cursorDesc'),
      icon: <GlobeAltIcon className="size-5" style={{ color: 'var(--accent-mint)' }} />,
      subsections: [
        {
          id: 'cursor-config',
          title: t('vibeStudio.mcp.cursorConfigFile'),
          content: cursorConfig
        }
      ]
    },
    {
      id: 'copilot',
      title: t('vibeStudio.mcp.copilotConfig'),
      description: t('vibeStudio.mcp.copilotDesc'),
      icon: <GlobeAltIcon className="size-5" style={{ color: 'var(--accent-mint)' }} />,
      subsections: [
        {
          id: 'copilot-config',
          title: t('vibeStudio.mcp.copilotConfigFile'),
          content: vscodeConfig
        }
      ]
    }
  ]

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
      onClick={onClose}
    >
      <div 
        className="w-full max-w-2xl rounded-xl overflow-hidden max-h-[90vh] flex flex-col"
        style={{ backgroundColor: 'var(--bg-canvas)', border: '1px solid var(--border-subtle)' }}
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div 
          className="flex items-center justify-between px-6 py-4 flex-shrink-0"
          style={{ borderBottom: '1px solid var(--border-subtle)' }}
        >
          <div className="flex items-center gap-3">
            <div 
              className="size-10 rounded-lg flex items-center justify-center"
              style={{ backgroundColor: 'var(--accent-mint)' }}
            >
              <ServerIcon className="size-5 text-white" />
            </div>
            <div>
              <h2 
                className="text-lg font-bold"
                style={{ color: 'var(--text-primary)', fontWeight: 'var(--font-weight-heading)' }}
              >
                {t('vibeStudio.mcp.title')}
              </h2>
              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                {t('vibeStudio.mcp.subtitle')}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-full hover:bg-white/5 transition-colors"
          >
            <XMarkIcon className="size-5" style={{ color: 'var(--text-secondary)' }} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4 overflow-y-auto flex-1">
          {/* Protocol Notice */}
          <div 
            className="p-4 rounded-lg flex items-start gap-3"
            style={{ backgroundColor: 'rgba(168, 192, 175, 0.1)', border: '1px solid var(--accent-mint)' }}
          >
            <span className="text-xl">🔌</span>
            <div>
              <p 
                className="text-sm font-medium"
                style={{ color: 'var(--text-primary)' }}
              >
                {t('vibeStudio.mcp.standardProtocols')}
              </p>
              <p 
                className="text-sm mt-1"
                style={{ color: 'var(--text-secondary)' }}
              >
                {t('vibeStudio.mcp.standardProtocolsDesc')}
              </p>
            </div>
          </div>

          {/* Configuration Sections */}
          <div className="space-y-3">
            {sections.map((section) => (
              <Disclosure key={section.id} defaultOpen={section.id === 'cursor'}>
                {({ open }) => (
                  <div 
                    className="rounded-lg overflow-hidden"
                    style={{ border: '1px solid var(--border-subtle)' }}
                  >
                    <DisclosureButton
                      className="w-full flex items-center justify-between p-4 hover:bg-white/5 transition-colors"
                      style={{ backgroundColor: 'var(--bg-canvas)' }}
                    >
                      <div className="flex items-center gap-3">
                        <div 
                          className="size-9 rounded-lg flex items-center justify-center"
                          style={{ backgroundColor: 'var(--bg-surface)' }}
                        >
                          {section.icon}
                        </div>
                        <div className="text-left">
                          <span 
                            className="font-medium"
                            style={{ color: 'var(--text-primary)' }}
                          >
                            {section.title}
                          </span>
                          <p 
                            className="text-sm"
                            style={{ color: 'var(--text-secondary)' }}
                          >
                            {section.description}
                          </p>
                        </div>
                      </div>
                      {open ? (
                        <ChevronUpIcon className="size-5" style={{ color: 'var(--text-secondary)' }} />
                      ) : (
                        <ChevronDownIcon className="size-5" style={{ color: 'var(--text-secondary)' }} />
                      )}
                    </DisclosureButton>
                    
                    <DisclosurePanel
                      className="p-4 pt-0 space-y-4"
                      style={{ backgroundColor: 'var(--bg-surface)' }}
                    >
                      {section.subsections.map((subsection) => (
                        <div key={subsection.id} className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span 
                              className="text-sm font-medium"
                              style={{ color: 'var(--text-primary)' }}
                            >
                              {subsection.title}
                            </span>
                            <button
                              onClick={() => handleCopy(subsection.content, subsection.id)}
                              className="flex items-center gap-1.5 text-xs px-2 py-1 rounded-full hover:bg-white/5 transition-colors"
                              style={{ color: 'var(--accent-mint)' }}
                            >
                              {copiedField === subsection.id ? (
                                <>
                                  <CheckIcon className="size-3.5" />
                                  {t('common.copied')}
                                </>
                              ) : (
                                <>
                                  <ClipboardDocumentIcon className="size-3.5" />
                                  {t('common.copy')}
                                </>
                              )}
                            </button>
                          </div>
                          <pre 
                            className="rounded-lg p-4 text-xs overflow-x-auto font-mono"
                            style={{ 
                              backgroundColor: '#1e1e1e', 
                              color: '#d4d4d4',
                              border: '1px solid var(--border-subtle)'
                            }}
                          >
                            {subsection.content}
                          </pre>
                        </div>
                      ))}
                    </DisclosurePanel>
                  </div>
                )}
              </Disclosure>
            ))}
          </div>

          {/* Available Tools */}
          <div className="space-y-2">
            <h3 
              className="text-sm font-medium"
              style={{ color: 'var(--text-primary)' }}
            >
              {t('vibeStudio.mcp.availableTools')}
            </h3>
            <div className="grid grid-cols-2 gap-2">
              {[
                { name: 'get_design_system', desc: t('vibeStudio.mcp.tools.getDesignSystem') },
                { name: 'get_aesthetic_guidance', desc: t('vibeStudio.mcp.tools.getAestheticGuidance') },
              ].map((tool) => (
                <div 
                  key={tool.name}
                  className="p-3 rounded-lg"
                  style={{ backgroundColor: 'var(--bg-surface)', border: '1px solid var(--border-subtle)' }}
                >
                  <code 
                    className="text-xs font-mono"
                    style={{ color: 'var(--accent-mint)' }}
                  >
                    {tool.name}
                  </code>
                  <p 
                    className="text-xs mt-1"
                    style={{ color: 'var(--text-secondary)' }}
                  >
                    {tool.desc}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div 
          className="flex items-center justify-end gap-3 px-6 py-4 flex-shrink-0"
          style={{ borderTop: '1px solid var(--border-subtle)', backgroundColor: 'var(--bg-surface)' }}
        >
          <Button variant="outline" onClick={onClose}>
            {t('common.close')}
          </Button>
        </div>
      </div>
    </div>
  )
}
