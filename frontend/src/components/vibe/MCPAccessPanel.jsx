import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { 
  XMarkIcon, 
  ServerIcon,
  ClipboardDocumentIcon,
  CheckIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  CommandLineIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline'
import { Button } from '@/components/ui/button'

/**
 * MCP Access Panel - Displays MCP connection information for vibe coding tools
 * Shows both stdio and streamable-http protocol configurations
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
  const [expandedSection, setExpandedSection] = useState('stdio')

  if (!isOpen) return null

  // Get base URL for API endpoints
  const baseUrl = window.location.origin
  const serverName = `monkeyui-${(designSystemName || 'design-system').toLowerCase().replace(/\s+/g, '-')}`

  const handleCopy = async (text, field) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedField(field)
      setTimeout(() => setCopiedField(null), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  // stdio protocol - for Cursor, Claude Desktop
  const stdioCommand = `python -m apps.design_system.mcp.cli \\
  --design-system-id ${designSystemId} \\
  --api-key ${apiKey || 'YOUR_API_KEY'}`

  // Cursor MCP configuration (stdio)
  const cursorConfig = `{
  "mcpServers": {
    "${serverName}": {
      "command": "python",
      "args": [
        "-m", "apps.design_system.mcp.cli",
        "--design-system-id", "${designSystemId}",
        "--api-key", "${apiKey || 'YOUR_API_KEY'}"
      ],
      "cwd": "/path/to/monkeyui/backend"
    }
  }
}`

  // Claude Desktop configuration (stdio)
  const claudeDesktopConfig = `{
  "mcpServers": {
    "${serverName}": {
      "command": "python",
      "args": [
        "-m", "apps.design_system.mcp.cli",
        "--design-system-id", "${designSystemId}",
        "--api-key", "${apiKey || 'YOUR_API_KEY'}"
      ],
      "cwd": "/path/to/monkeyui/backend"
    }
  }
}`

  // Streamable HTTP configuration
  const streamableHttpUrl = `${baseUrl}/api/v1/design-systems/mcp/${designSystemId}/`
  
  const streamableHttpConfig = `# Streamable HTTP Endpoint
URL: ${streamableHttpUrl}

# Authentication
Header: Authorization: Bearer ${apiKey || 'YOUR_API_KEY'}

# HTTP Method
POST (application/json)`

  const sections = [
    {
      id: 'stdio',
      title: t('vibeStudio.mcp.stdioProtocol'),
      description: t('vibeStudio.mcp.stdioDesc'),
      icon: <CommandLineIcon className="size-5" style={{ color: 'var(--accent-blue)' }} />,
      subsections: [
        {
          id: 'stdio-command',
          title: t('vibeStudio.mcp.cliCommand'),
          content: stdioCommand
        },
        {
          id: 'cursor',
          title: t('vibeStudio.mcp.cursorConfig'),
          content: cursorConfig
        },
        {
          id: 'claude-desktop',
          title: t('vibeStudio.mcp.claudeDesktopConfig'),
          content: claudeDesktopConfig
        }
      ]
    },
    {
      id: 'streamable-http',
      title: t('vibeStudio.mcp.streamableHttpProtocol'),
      description: t('vibeStudio.mcp.streamableHttpDesc'),
      icon: <GlobeAltIcon className="size-5" style={{ color: 'var(--accent-blue)' }} />,
      subsections: [
        {
          id: 'http-config',
          title: t('vibeStudio.mcp.httpEndpoint'),
          content: streamableHttpConfig
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
              style={{ backgroundColor: 'var(--accent-blue)' }}
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
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <XMarkIcon className="size-5" style={{ color: 'var(--text-secondary)' }} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4 overflow-y-auto flex-1">
          {/* Protocol Notice */}
          <div 
            className="p-4 rounded-lg flex items-start gap-3"
            style={{ backgroundColor: 'rgba(42, 153, 211, 0.1)', border: '1px solid var(--accent-blue)' }}
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
              <div 
                key={section.id}
                className="rounded-lg overflow-hidden"
                style={{ border: '1px solid var(--border-subtle)' }}
              >
                <button
                  onClick={() => setExpandedSection(expandedSection === section.id ? null : section.id)}
                  className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
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
                  {expandedSection === section.id ? (
                    <ChevronUpIcon className="size-5" style={{ color: 'var(--text-secondary)' }} />
                  ) : (
                    <ChevronDownIcon className="size-5" style={{ color: 'var(--text-secondary)' }} />
                  )}
                </button>
                
                {expandedSection === section.id && (
                  <div 
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
                            className="flex items-center gap-1.5 text-xs px-2 py-1 rounded hover:bg-gray-200 transition-colors"
                            style={{ color: 'var(--accent-blue)' }}
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
                  </div>
                )}
              </div>
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
                { name: 'get_colors', desc: t('vibeStudio.mcp.tools.getColors') },
                { name: 'get_typography', desc: t('vibeStudio.mcp.tools.getTypography') },
                { name: 'get_spacing', desc: t('vibeStudio.mcp.tools.getSpacing') },
                { name: 'get_component_styles', desc: t('vibeStudio.mcp.tools.getComponentStyles') },
                { name: 'get_css_variables', desc: t('vibeStudio.mcp.tools.getCssVariables') },
                { name: 'get_tailwind_config', desc: t('vibeStudio.mcp.tools.getTailwindConfig') },
              ].map((tool) => (
                <div 
                  key={tool.name}
                  className="p-3 rounded-lg"
                  style={{ backgroundColor: 'var(--bg-surface)', border: '1px solid var(--border-subtle)' }}
                >
                  <code 
                    className="text-xs font-mono"
                    style={{ color: 'var(--accent-blue)' }}
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
