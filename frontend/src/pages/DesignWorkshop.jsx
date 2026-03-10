import { useState, useEffect, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { PlusIcon, SwatchIcon, TrashIcon, EllipsisVerticalIcon, LinkIcon } from '@heroicons/react/24/outline'
import ConsoleLayout from '@/components/layout/ConsoleLayout'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import Pagination from '@/components/ui/Pagination'
import CreateVibeModal from '@/components/vibe/CreateVibeModal'
import designSystemService, { DesignSystemStatus } from '@/services/designSystem'
import { checkLLMReadiness } from '@/services/llmConfig'

const PAGE_SIZE = 10

export default function DesignWorkshop() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [designSystems, setDesignSystems] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const [totalPages, setTotalPages] = useState(1)
  const [pollingProgress, setPollingProgress] = useState({}) // { [systemId]: { progress, message } }
  const pollingRefs = useRef({}) // Store polling timers
  const [openSettingsTab, setOpenSettingsTab] = useState(null)
  const [showReadinessWarning, setShowReadinessWarning] = useState(false)

  // Fetch design systems on mount
  const fetchDesignSystems = useCallback(async (page = 1) => {
    try {
      setIsLoading(true)
      setError(null)
      console.log('[DesignWorkshop] Fetching page:', page)
      const response = await designSystemService.getDesignSystems({ 
        page, 
        pageSize: PAGE_SIZE 
      })
      console.log('[DesignWorkshop] Response:', response)
      setDesignSystems(response.results || [])
      setTotalCount(response.count || 0)
      setTotalPages(Math.ceil((response.count || 0) / PAGE_SIZE))
      setCurrentPage(page)
      
      // Start polling for processing/pending systems
      response.results?.forEach(system => {
        if (system.status === DesignSystemStatus.PROCESSING || system.status === DesignSystemStatus.PENDING) {
          startPollingSystem(system.id)
        }
      })
    } catch (err) {
      console.error('[DesignWorkshop] Failed to fetch design systems:', err)
      setError(err.message || t('common.error'))
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Start polling for a specific system
  const startPollingSystem = useCallback(async (systemId) => {
    // Avoid duplicate polling
    if (pollingRefs.current[systemId]) {
      return
    }

    const poll = async () => {
      try {
        const status = await designSystemService.getAnalysisStatus(systemId)
        
        setPollingProgress(prev => ({
          ...prev,
          [systemId]: {
            progress: status.progress || 0,
            message: status.message || ''
          }
        }))

        // Update design systems list with new status
        setDesignSystems(prev => 
          prev.map(sys => 
            sys.id === systemId 
              ? { ...sys, status: status.status, design_tokens: status.result || sys.design_tokens }
              : sys
          )
        )

        if (status.status === DesignSystemStatus.COMPLETED || status.status === DesignSystemStatus.FAILED) {
          // Stop polling
          stopPollingSystem(systemId)
        } else {
          // Continue polling every 10 seconds
          pollingRefs.current[systemId] = setTimeout(poll, 10000)
        }
      } catch (err) {
        console.error(`Polling failed for system ${systemId}:`, err)
        stopPollingSystem(systemId)
      }
    }

    poll()
  }, [])

  const stopPollingSystem = useCallback((systemId) => {
    if (pollingRefs.current[systemId]) {
      clearTimeout(pollingRefs.current[systemId])
      delete pollingRefs.current[systemId]
    }
    setPollingProgress(prev => {
      const next = { ...prev }
      delete next[systemId]
      return next
    })
  }, [])

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      Object.values(pollingRefs.current).forEach(timer => clearTimeout(timer))
    }
  }, [])

  useEffect(() => {
    fetchDesignSystems(currentPage)
  }, [])

  // Refresh list when page becomes visible (e.g., after navigating back)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        fetchDesignSystems(1) // Reset to page 1 when returning
      }
    }

    const handleFocus = () => {
      fetchDesignSystems(1) // Reset to page 1 when returning
    }
    
    document.addEventListener('visibilitychange', handleVisibilityChange)
    window.addEventListener('focus', handleFocus)
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
      window.removeEventListener('focus', handleFocus)
    }
  }, [fetchDesignSystems])

  const handleCreateNew = async () => {
    try {
      const { ready } = await checkLLMReadiness()
      if (!ready) {
        setShowReadinessWarning(true)
        setOpenSettingsTab('models')
        return
      }
    } catch {
      // If readiness check fails (e.g. network error), allow creation anyway
    }
    setIsCreateModalOpen(true)
  }

  const handleGoToStudio = (vibeData) => {
    // Navigate to new studio with state
    navigate('/vibe-studio/new', { 
      state: { 
        name: vibeData.name, 
        description: vibeData.description 
      } 
    })
  }

  const handleOpenStudio = (system) => {
    navigate(`/vibe-studio/${system.id}`)
  }

  const handleDeleteSystem = async (id, e) => {
    e.stopPropagation()
    if (!window.confirm(t('designWorkshop.confirmDelete'))) {
      return
    }
    try {
      await designSystemService.deleteDesignSystem(id)
      // Refresh current page
      fetchDesignSystems(currentPage)
    } catch (err) {
      console.error('Failed to delete design system:', err)
    }
  }

  const handlePageChange = (page) => {
    setCurrentPage(page)
    fetchDesignSystems(page)
    // Scroll to top of list
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <>
      <ConsoleLayout 
        onCreateNew={handleCreateNew}
        openSettingsTab={openSettingsTab}
        onSettingsClosed={() => { setOpenSettingsTab(null); setShowReadinessWarning(false) }}
      >
        <div className="space-y-8">
          {/* Readiness Warning */}
          {showReadinessWarning && (
            <div 
              className="flex items-center gap-3 p-4 rounded-xl text-sm"
              style={{ 
                backgroundColor: 'rgba(252, 211, 77, 0.1)',
                border: '1px solid rgba(252, 211, 77, 0.3)',
                color: 'var(--color-warning)'
              }}
            >
              <span className="flex-1">{t('settings.modelConfig.readinessWarning')}</span>
              <button
                onClick={() => setOpenSettingsTab('models')}
                className="px-3 py-1.5 rounded-lg text-xs font-medium flex-shrink-0"
                style={{
                  backgroundColor: 'var(--btn-primary-bg)',
                  color: 'var(--btn-primary-fg)'
                }}
              >
                {t('settings.modelConfig.readinessAction')}
              </button>
            </div>
          )}

          {/* Page Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 
                className="text-2xl font-bold tracking-tight"
                style={{ color: 'var(--text-primary)', fontWeight: 'var(--font-weight-heading)' }}
              >
                {t('designWorkshop.title')}
              </h1>
              <p 
                className="mt-1 text-sm"
                style={{ color: 'var(--text-secondary)' }}
              >
                {t('designWorkshop.description')}
              </p>
            </div>
            <Button onClick={handleCreateNew} className="gap-x-2">
              <PlusIcon className="size-4" />
              {t('designWorkshop.createNew')}
            </Button>
          </div>

          {/* Loading State */}
          {isLoading && (
            <div className="flex items-center justify-center py-16">
              <div className="animate-spin size-8 border-2 border-[#6B52E1] border-t-transparent rounded-full" />
            </div>
          )}

          {/* Error State */}
          {error && !isLoading && (
            <div 
              className="rounded-lg p-4 text-center"
              style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', color: 'var(--color-error)' }}
            >
              {error}
              <Button 
                variant="outline" 
                size="sm" 
                onClick={fetchDesignSystems}
                className="ml-4"
              >
                {t('common.retry')}
              </Button>
            </div>
          )}

          {/* Design Systems Grid */}
          {!isLoading && !error && designSystems.length === 0 && (
            <EmptyState />
          )}
          
          {!isLoading && !error && designSystems.length > 0 && (
            <>
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {designSystems.map((system) => (
                  <DesignSystemCard 
                    key={system.id} 
                    system={system} 
                    onSelect={() => handleOpenStudio(system)}
                    onDelete={(e) => handleDeleteSystem(system.id, e)}
                    progress={pollingProgress[system.id]}
                  />
                ))}
              </div>

              {/* Pagination */}
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                totalCount={totalCount}
                pageSize={PAGE_SIZE}
                onPageChange={handlePageChange}
              />
            </>
          )}
        </div>
      </ConsoleLayout>

      {/* Create Vibe Modal */}
      <CreateVibeModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onGoToStudio={handleGoToStudio}
      />
    </>
  )
}

function DesignSystemCard({ system, onSelect, onDelete, progress }) {
  const { t } = useTranslation()
  const isProcessing = system.status === DesignSystemStatus.PROCESSING || system.status === DesignSystemStatus.PENDING
  
  // Check if color is light (needs border)
  const isLightColor = (color) => {
    if (!color) return false
    
    // Handle CSS variables
    if (color.startsWith('var(')) {
      // We can't easily compute CSS variables in JS without DOM access,
      // but we know our specific variables
      if (color.includes('--bg-canvas') || color.includes('--bg-surface')) return false
      if (color.includes('--brand-primary') || color.includes('--text-primary')) return true
      return false
    }

    let r, g, b

    // Handle rgb/rgba
    if (color.startsWith('rgb')) {
      const match = color.match(/\d+/g)
      if (match && match.length >= 3) {
        r = parseInt(match[0], 10)
        g = parseInt(match[1], 10)
        b = parseInt(match[2], 10)
      } else {
        return false
      }
    } 
    // Handle hex
    else if (color.startsWith('#') || /^[0-9A-Fa-f]{3,6}$/.test(color)) {
      let hex = color.replace('#', '')
      if (hex.length === 3) {
        hex = hex.split('').map(char => char + char).join('')
      }
      if (hex.length !== 6) return false
      
      r = parseInt(hex.substr(0, 2), 16)
      g = parseInt(hex.substr(2, 2), 16)
      b = parseInt(hex.substr(4, 2), 16)
    }
    // Handle named colors (basic ones)
    else {
      const namedColors = {
        white: [255, 255, 255],
        black: [0, 0, 0],
        transparent: [0, 0, 0] // Assume dark for transparent
      }
      const rgb = namedColors[color.toLowerCase()]
      if (rgb) {
        [r, g, b] = rgb
      } else {
        return false
      }
    }

    // Calculate luminance (perceived brightness)
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    // If luminance > 0.5, it's a light color
    return luminance > 0.5
  }
  
  // Get status badge variant
  const getStatusBadgeVariant = (status) => {
    switch (status) {
      case DesignSystemStatus.COMPLETED:
        return 'success'
      case DesignSystemStatus.PROCESSING:
      case DesignSystemStatus.PENDING:
        return 'info'
      case DesignSystemStatus.FAILED:
        return 'error'
      default:
        return 'muted'
    }
  }
  
  // Format date
  const formatDate = (dateStr) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    return date.toLocaleDateString()
  }
  
  return (
    <div
      onClick={onSelect}
      className="group relative rounded-xl p-6 cursor-pointer transition-all duration-200 hover:shadow-md"
      style={{ 
        backgroundColor: 'var(--bg-canvas)', 
        border: '1px solid var(--border-subtle)',
      }}
    >
      {/* Top row: Avatar and actions */}
      <div className="flex items-start justify-between mb-4">
        {/* Color indicator */}
        <div 
          className="flex size-12 items-center justify-center rounded-lg text-lg font-bold"
          style={{ 
            backgroundColor: system.primary_color || 'var(--bg-surface)',
            color: system.primary_color 
              ? (isLightColor(system.primary_color) ? 'var(--bg-canvas)' : 'var(--text-on-dark)')
              : 'var(--text-secondary)',
            border: isLightColor(system.primary_color) ? '1px solid var(--border-default)' : 'none'
          }}
        >
          {system.initial || system.name?.charAt(0).toUpperCase()}
        </div>
        
        {/* Actions */}
        <div className="flex items-center gap-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
          {system.mcp_enabled && system.status === DesignSystemStatus.COMPLETED && (
            <div 
              className="p-1.5 rounded-md"
              title={t('designWorkshop.mcpEnabled')}
            >
              <LinkIcon className="size-4" style={{ color: 'var(--accent-blue)' }} />
            </div>
          )}
          <button
            onClick={onDelete}
            className="p-1.5 rounded-md hover:bg-[#FFF0F0] transition-colors"
            title={t('common.delete')}
          >
            <TrashIcon className="size-4" style={{ color: 'var(--color-error)' }} />
          </button>
        </div>
      </div>

      {/* Content */}
      <h3 
        className="text-base font-semibold mb-1 group-hover:text-[#6B52E1] transition-colors"
        style={{ color: 'var(--text-primary)' }}
      >
        {system.name}
      </h3>
      <p 
        className="text-sm mb-4 line-clamp-2"
        style={{ color: 'var(--text-secondary)' }}
      >
        {system.description || t('designWorkshop.noDescription')}
      </p>

      {/* Progress bar for processing systems */}
      {isProcessing && progress && (
        <div className="mb-3">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
              {progress.message || t('designWorkshop.analyzing')}
            </span>
            <span className="text-xs font-medium" style={{ color: 'var(--color-info)' }}>
              {progress.progress || 0}%
            </span>
          </div>
          <Progress
            value={progress.progress || 0}
            className="bg-[var(--bg-surface)]"
            indicatorClassName="bg-[var(--color-info)]"
          />
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between">
        <div 
          className="text-xs"
          style={{ color: 'var(--text-tertiary)' }}
        >
          {t('designWorkshop.updatedAt')}: {formatDate(system.updated_at)}
        </div>
        
        {/* Status badge */}
        <Badge variant={getStatusBadgeVariant(system.status)}>
          {t(`designWorkshop.status.${system.status}`)}
        </Badge>
      </div>

      {/* Hover overlay */}
      <div 
        className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"
        style={{ boxShadow: 'var(--shadow-sm)' }}
      />
    </div>
  )
}

function EmptyState({ onCreateNew }) {
  const { t } = useTranslation()
  
  return (
    <div 
      className="flex flex-col items-center justify-center rounded-xl py-16 px-6 text-center"
      style={{ 
        backgroundColor: 'var(--bg-surface)', 
        border: '2px dashed var(--border-subtle)' 
      }}
    >
      <div 
        className="flex size-16 items-center justify-center rounded-full mb-4"
        style={{ backgroundColor: 'var(--bg-canvas)', border: '1px solid var(--border-subtle)' }}
      >
        <SwatchIcon className="size-8" style={{ color: 'var(--text-tertiary)' }} />
      </div>
      <h3 
        className="text-lg font-semibold mb-2"
        style={{ color: 'var(--text-primary)' }}
      >
        {t('designWorkshop.emptyTitle')}
      </h3>
      <p 
        className="text-sm max-w-sm"
        style={{ color: 'var(--text-secondary)' }}
      >
        {t('designWorkshop.emptyDescription')}
      </p>
    </div>
  )
}
