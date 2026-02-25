import { useState, useCallback, useEffect } from 'react'
import { useNavigate, useParams, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { TabGroup, TabList, Tab, TabPanels, TabPanel } from '@headlessui/react'
import { 
  ArrowLeftIcon, 
  ArrowDownTrayIcon, 
  BookmarkIcon, 
  PhotoIcon, 
  XMarkIcon,
  ServerIcon
} from '@heroicons/react/24/outline'
import { Layers, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import Alert from '@/components/ui/Alert'
import StyleAnalysisPanel from '@/components/vibe/StyleAnalysisPanel'
import AestheticAnalysisPanel from '@/components/vibe/AestheticAnalysisPanel'
import ExportRulesModal from '@/components/vibe/ExportRulesModal'
import MCPAccessPanel from '@/components/vibe/MCPAccessPanel'
import designSystemService, { DesignSystemStatus } from '@/services/designSystem'

export default function VibeStudio({ isNew }) {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { id } = useParams()
  const location = useLocation()
  const [uploadedImages, setUploadedImages] = useState([])
  const [styleData, setStyleData] = useState(null) // null for new, will be set when loaded
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(null)
  const [displayProgress, setDisplayProgress] = useState(0) // Frontend display progress for smooth animation
  const [error, setError] = useState(null)
  const [name, setName] = useState(location.state?.name || 'Untitled Design')
  const [description, setDescription] = useState(location.state?.description || '')
  const [isSaving, setIsSaving] = useState(false)
  const [currentDesignSystem, setCurrentDesignSystem] = useState(null)
  const [isLoading, setIsLoading] = useState(!isNew)
  const [isImageExpanded, setIsImageExpanded] = useState(false)
  const [isExportModalOpen, setIsExportModalOpen] = useState(false)
  const [isMCPPanelOpen, setIsMCPPanelOpen] = useState(false)
  const [alert, setAlert] = useState({ show: false, type: 'success', message: '' })
  const [aestheticData, setAestheticData] = useState(null)

  // Convert backend style data format to frontend format
  // Backend now returns structured JSON directly from AI analysis
  // MVP fields only: colors, typography, shadowDepth
  const convertStyleData = (data) => {
    // If data has the new structured format (from schema.py convert_to_frontend_format)
    if (data.colors !== undefined) {
      return {
        colors: data.colors,
        typography: data.typography,
        shadowDepth: data.shadowDepth,
      }
    }
    
    // Legacy format fallback (for existing data in database)
    return {
      colors: data.colors,
      typography: data.typography,
      shadowDepth: data.shadows?.level2 ? 2 : (data.shadowDepth || 0),
    }
  }

  // Convert frontend style data format to backend format
  const convertToBackendFormat = (data) => {
    return {
      colors: data.colors,
      typography: data.typography,
      shadowDepth: data.shadowDepth,
    }
  }

  // Load existing design system if editing
  useEffect(() => {
    if (!isNew && id) {
      loadDesignSystem()
    }
  }, [isNew, id])

  // Simulate smooth progress growth on frontend
  useEffect(() => {
    if (!isAnalyzing) {
      setDisplayProgress(0)
      return
    }

    const backendProgress = analysisProgress?.progress || 0
    
    // If backend progress is higher, jump to it immediately
    if (backendProgress > displayProgress) {
      setDisplayProgress(backendProgress)
    }

    // Slowly increment display progress even if backend hasn't updated
    const interval = setInterval(() => {
      setDisplayProgress(prev => {
        const backend = analysisProgress?.progress || 0
        
        // Don't exceed 98% without backend confirmation (leave room for completion)
        if (prev >= 98) return prev
        
        // Don't go more than 10% ahead of backend progress
        if (prev >= backend + 10 && backend > 0) return prev
        
        // Increment slowly (0.5% every 500ms = 1% per second)
        return Math.min(prev + 0.5, 98)
      })
    }, 500)

    return () => clearInterval(interval)
  }, [isAnalyzing, analysisProgress])

  const loadDesignSystem = async () => {
    try {
      setIsLoading(true)
      const designSystem = await designSystemService.getDesignSystem(id)
      
      setName(designSystem.name || 'Untitled Design')
      setDescription(designSystem.description || '')
      setCurrentDesignSystem(designSystem)
      
      if (designSystem.design_tokens && Object.keys(designSystem.design_tokens).length > 0) {
        setStyleData(convertStyleData(designSystem.design_tokens))
      }
      
      // Load aesthetic analysis if available
      if (designSystem.aesthetic_analysis) {
        setAestheticData(designSystem.aesthetic_analysis)
      }
      
      // Load existing image (one-to-one relationship)
      if (designSystem.image) {
        setUploadedImages([{
          id: designSystem.image.id,
          url: designSystem.image.url,
          name: designSystem.image.name,
          fromServer: true
        }])
      }
      
      // Only poll if there's an image and status is processing/pending
      if (designSystem.image && 
          (designSystem.status === DesignSystemStatus.PROCESSING || 
           designSystem.status === DesignSystemStatus.PENDING)) {
        setIsAnalyzing(true)
        pollAnalysisStatus(designSystem.id)
      }
    } catch (err) {
      console.error('Failed to load design system:', err)
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  // Poll for analysis status
  const pollAnalysisStatus = async (systemId) => {
    const pollId = systemId || currentDesignSystem?.id
    if (!pollId) return
    
    try {
      setIsAnalyzing(true)
      await designSystemService.pollAnalysisStatus(
        pollId,
        (status) => {
          setAnalysisProgress(status)
          if (status.status === 'completed' && status.result) {
            setStyleData(convertStyleData(status.result))
            // Update current design system status
            setCurrentDesignSystem(prev => prev ? { ...prev, status: DesignSystemStatus.COMPLETED } : prev)
            // Fetch full design system to get aesthetic_analysis
            designSystemService.getDesignSystem(pollId).then(ds => {
              if (ds.aesthetic_analysis) {
                setAestheticData(ds.aesthetic_analysis)
              }
            }).catch(err => console.error('Failed to load aesthetic analysis:', err))
          }
        }
      )
      setIsAnalyzing(false)
      setAnalysisProgress(null)
    } catch (err) {
      setError(err.message)
      setIsAnalyzing(false)
    }
  }

  // Handle file drop
  const handleDrop = useCallback((e) => {
    e.preventDefault()
    const files = Array.from(e.dataTransfer.files).filter(file => 
      file.type.startsWith('image/')
    )
    handleFiles(files)
  }, [])

  const handleDragOver = (e) => {
    e.preventDefault()
  }

  const handleFileInput = (e) => {
    const files = Array.from(e.target.files).filter(file => 
      file.type.startsWith('image/')
    )
    handleFiles(files)
  }

  const handleFiles = (files) => {
    // Only allow one image (one-to-one relationship)
    if (files.length > 0) {
      const file = files[0]
      const newImage = {
        id: Date.now(),
        file,
        url: URL.createObjectURL(file),
        name: file.name,
        fromServer: false
      }
      setUploadedImages([newImage])
    }
  }

  const removeImage = async (image) => {
    if (image.fromServer && currentDesignSystem?.id) {
      try {
        await designSystemService.deleteImage(currentDesignSystem.id, image.id)
      } catch (err) {
        console.error('Failed to delete image:', err)
      }
    }
    setUploadedImages(prev => prev.filter(img => img.id !== image.id))
  }

  // Start AI analysis
  const handleStartAnalysis = async () => {
    // Prevent duplicate clicks
    if (isAnalyzing) {
      return
    }
    
    // Set analyzing state immediately to disable button
    setIsAnalyzing(true)
    setError(null)
    
    try {
      // If this is a new design system, create it first
      if (isNew || !currentDesignSystem?.id) {
        setAnalysisProgress({ progress: 0, message: t('vibeStudio.creatingDesignSystem') })
        const created = await designSystemService.createDesignSystem({
          name,
          description
        })
        setCurrentDesignSystem(created)
        // Navigate to the edit URL
        navigate(`/vibe-studio/${created.id}`, { replace: true })
        // Continue with analysis
        await performAnalysis(created.id)
      } else {
        await performAnalysis(currentDesignSystem.id)
      }
    } catch (err) {
      console.error('Failed to create design system:', err)
      setError(err.message)
      setIsAnalyzing(false)
      setAnalysisProgress(null)
    }
  }

  const performAnalysis = async (systemId) => {
    if (uploadedImages.length === 0) {
      setError(t('vibeStudio.noImages'))
      setIsAnalyzing(false)
      setAnalysisProgress(null)
      return
    }
    
    // Note: isAnalyzing should already be true from handleStartAnalysis
    setAnalysisProgress({ progress: 0, message: t('vibeStudio.preparingImages') })
    
    try {
      // Convert new local images to base64 and upload
      const localImages = uploadedImages.filter(img => !img.fromServer && img.file)
      
      if (localImages.length > 0) {
        const imageData = await designSystemService.filesToImageData(
          localImages.map(img => img.file)
        )
        
        setAnalysisProgress({ progress: 5, message: t('vibeStudio.uploadingImages') })
        await designSystemService.uploadImages(systemId, imageData)
        
        // Mark images as uploaded
        setUploadedImages(prev => prev.map(img => ({
          ...img,
          fromServer: true
        })))
      }
      
      // Start analysis
      setAnalysisProgress({ progress: 8, message: t('vibeStudio.startingAnalysis') })
      await designSystemService.startAnalysis(systemId)
      
      // Poll for completion
      await designSystemService.pollAnalysisStatus(
        systemId,
        (status) => {
          // Only update progress if it's moving forward (prevent visual regression)
          setAnalysisProgress(prev => {
            const newProgress = status.progress || 0
            const prevProgress = prev?.progress || 0
            // Keep the higher progress value to prevent visual regression
            if (newProgress >= prevProgress) {
              return status
            }
            return { ...status, progress: prevProgress }
          })
          if (status.status === 'completed' && status.result) {
            setStyleData(convertStyleData(status.result))
            // Fetch full design system to get aesthetic_analysis
            designSystemService.getDesignSystem(systemId).then(ds => {
              if (ds.aesthetic_analysis) {
                setAestheticData(ds.aesthetic_analysis)
              }
            }).catch(err => console.error('Failed to load aesthetic analysis:', err))
          }
        }
      )
      
      setIsAnalyzing(false)
      setAnalysisProgress(null)
    } catch (err) {
      console.error('Analysis failed:', err)
      setError(err.message || t('vibeStudio.analysisFailed'))
      setIsAnalyzing(false)
      setAnalysisProgress(null)
    }
  }

  const handleExportRules = () => {
    setIsExportModalOpen(true)
  }

  const handleSaveVibe = async () => {
    setIsSaving(true)
    try {
      let systemId
      if (isNew || !currentDesignSystem?.id) {
        // Create new design system
        const created = await designSystemService.createDesignSystem({
          name,
          description,
          design_tokens: styleData ? convertToBackendFormat(styleData) : null,
        })
        systemId = created.id
        // Navigate to the edit URL (so URL reflects the new ID)
        navigate(`/vibe-studio/${systemId}`, { replace: true })
      } else {
        // Update existing design system
        systemId = currentDesignSystem.id
        await designSystemService.updateDesignSystem(systemId, {
          name,
          description,
          design_tokens: styleData ? convertToBackendFormat(styleData) : null,
        })
      }
      
      // Reload the design system to get the latest status (especially after analysis completes)
      const updated = await designSystemService.getDesignSystem(systemId)
      setCurrentDesignSystem(updated)
      
      // Show success alert
      setAlert({ show: true, type: 'success', message: t('vibeStudio.saveSuccess') })
    } catch (err) {
      console.error('Save failed:', err)
      setError(err.message)
      setAlert({ show: true, type: 'error', message: err.message || t('vibeStudio.saveFailed') })
    } finally {
      setIsSaving(false)
    }
  }

  // Check if color is light (needs border)
  const isLightColor = (color) => {
    if (!color) return false
    
    // Handle CSS variables
    if (color.startsWith('var(')) {
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

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--bg-surface)' }}>
      {/* Alert notification */}
      {alert.show && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 max-w-md w-full px-4">
          <Alert 
            type={alert.type}
            message={alert.message}
            show={alert.show}
            onClose={() => setAlert({ ...alert, show: false })}
            autoClose={5000}
          />
        </div>
      )}

      {/* Header */}
      <header 
        className="sticky top-0 z-40 px-6 py-4"
        style={{ backgroundColor: 'var(--bg-canvas)', borderBottom: '1px solid var(--border-subtle)' }}
      >
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-x-4">
            <button
              onClick={() => navigate('/')}
              className="p-2 rounded-full hover:bg-white/5 transition-colors"
            >
              <ArrowLeftIcon className="size-5" style={{ color: 'var(--text-secondary)' }} />
            </button>
            <div className="flex items-center gap-x-3">
              <div 
                className="size-10 rounded-lg flex items-center justify-center"
                style={{ 
                  backgroundColor: styleData?.colors?.primary || 'var(--accent-mint)',
                  border: isLightColor(styleData?.colors?.primary || 'var(--accent-mint)') ? '1px solid var(--border-default)' : 'none'
                }}
              >
                <Layers 
                  className="size-6" 
                  style={{ color: isLightColor(styleData?.colors?.primary || 'var(--accent-mint)') ? 'var(--bg-canvas)' : 'var(--text-on-dark)' }}
                />
              </div>
              <div>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="text-lg font-bold bg-transparent border-none outline-none"
                  style={{ color: 'var(--text-primary)', fontWeight: 'var(--font-weight-heading)' }}
                  placeholder={t('vibeStudio.untitled')}
                />
                <p 
                  className="text-sm"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  {t('vibeStudio.subtitle')}
                </p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-x-3">
            {/* MCP Access Button - only show when design system exists and is completed */}
            {currentDesignSystem?.id && (
              <Button 
                variant="outline" 
                onClick={() => setIsMCPPanelOpen(true)}
                disabled={currentDesignSystem.status !== DesignSystemStatus.COMPLETED || isAnalyzing}
                className="gap-x-2"
              >
                <ServerIcon className="size-4" />
                {t('vibeStudio.mcp.access')}
              </Button>
            )}
            <Button 
              variant="outline" 
              onClick={handleExportRules}
              disabled={!styleData || isAnalyzing}
              className="gap-x-2"
            >
              <ArrowDownTrayIcon className="size-4" />
              {t('vibeStudio.exportRules')}
            </Button>
            <Button 
              onClick={handleSaveVibe}
              className="gap-x-2"
              disabled={isSaving || !styleData || isAnalyzing}
              style={{ backgroundColor: 'var(--accent-mint)', color: 'var(--text-on-dark)' }}
            >
              <BookmarkIcon className="size-4" />
              {isSaving ? t('common.saving') : t('vibeStudio.saveVibe')}
            </Button>
          </div>
        </div>
      </header>

      {/* Error Banner */}
      {error && (
        <div 
          className="mx-6 mt-4 p-4 rounded-lg flex items-center justify-between max-w-7xl"
          style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid var(--color-error)' }}
        >
          <span style={{ color: 'var(--color-error)' }}>{error}</span>
          <button onClick={() => setError(null)}>
            <XMarkIcon className="size-5" style={{ color: 'var(--color-error)' }} />
          </button>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
          {/* Left: Source Material */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-x-2">
                <PhotoIcon className="size-5" style={{ color: 'var(--text-secondary)' }} />
                <span 
                  className="text-xs font-semibold"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  {t('vibeStudio.sourceMaterial')}
                </span>
              </div>
              
              {/* Analyze Button */}
              <Button
                onClick={handleStartAnalysis}
                disabled={isAnalyzing || uploadedImages.length === 0}
                size="sm"
                className="relative"
                style={{ 
                  backgroundColor: isAnalyzing || uploadedImages.length === 0 ? 'var(--bg-surface)' : 'var(--accent-mint)', 
                  color: isAnalyzing || uploadedImages.length === 0 ? 'var(--text-secondary)' : 'var(--text-on-dark)',
                  cursor: isAnalyzing || uploadedImages.length === 0 ? 'not-allowed' : 'pointer'
                }}
              >
                {isAnalyzing && (
                  <Loader2 className="animate-spin -ml-1 mr-2 h-4 w-4 inline-block" />
                )}
                {isAnalyzing ? t('vibeStudio.analyzing') : t('vibeStudio.analyzeImages')}
              </Button>
            </div>
            
            {/* Drop Zone */}
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              className="relative rounded-xl overflow-hidden"
              style={{ 
                backgroundColor: 'var(--bg-canvas)', 
                border: '2px dashed var(--border-subtle)',
                height: '600px'
              }}
            >
              {uploadedImages.length === 0 ? (
                <label className="flex flex-col items-center justify-center h-full min-h-[400px] cursor-pointer hover:bg-white/5 transition-colors">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileInput}
                    className="hidden"
                  />
                  <PhotoIcon className="size-16 mb-4" style={{ color: 'var(--text-tertiary)' }} />
                  <p 
                    className="text-sm font-medium mb-1"
                    style={{ color: 'var(--text-secondary)' }}
                  >
                    {t('vibeStudio.dropImages')}
                  </p>
                  <p 
                    className="text-xs"
                    style={{ color: 'var(--text-tertiary)' }}
                  >
                    {t('vibeStudio.orClickToUpload')}
                  </p>
                </label>
              ) : (
                <div className="h-full flex flex-col items-center justify-center p-4">
                  {uploadedImages.map((image) => (
                    <div key={image.id} className="relative group w-full h-full flex flex-col">
                      <div 
                        className="flex-1 flex items-center justify-center overflow-hidden rounded-lg cursor-pointer"
                        onClick={() => setIsImageExpanded(true)}
                      >
                        <img
                          src={image.url}
                          alt={image.name}
                          className="max-w-full max-h-full object-contain hover:opacity-90 transition-opacity"
                          style={{ maxHeight: 'calc(600px - 4rem)' }}
                        />
                      </div>
                      {!isAnalyzing && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            removeImage(image)
                          }}
                          className="absolute top-2 right-2 p-1.5 rounded-full bg-black/60 text-white opacity-0 group-hover:opacity-100 transition-opacity z-10"
                        >
                          <XMarkIcon className="size-4" />
                        </button>
                      )}
                      <p className="text-sm text-center mt-2" style={{ color: 'var(--text-secondary)' }}>
                        {image.name}
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {/* Loading overlay */}
              {isAnalyzing && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/80 backdrop-blur-sm">
                  <div className="text-center max-w-sm px-6">
                    {/* Circular progress indicator */}
                    <div className="relative inline-flex items-center justify-center mb-6">
                      {/* Background circle */}
                      <svg className="size-32 -rotate-90">
                        <circle
                          cx="64"
                          cy="64"
                          r="56"
                          stroke="rgba(255, 255, 255, 0.1)"
                          strokeWidth="8"
                          fill="none"
                        />
                        {/* Progress circle with Tailwind animate-pulse */}
                        <circle
                          cx="64"
                          cy="64"
                          r="56"
                          stroke="var(--accent-mint)"
                          strokeWidth="8"
                          fill="none"
                          strokeLinecap="round"
                          className="animate-pulse"
                          strokeDasharray={`${2 * Math.PI * 56}`}
                          strokeDashoffset={`${2 * Math.PI * 56 * (1 - displayProgress / 100)}`}
                          style={{ 
                            transition: 'stroke-dashoffset 0.5s ease'
                          }}
                        />
                      </svg>
                      {/* Percentage text */}
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span 
                          className="text-3xl font-bold"
                          style={{ color: 'var(--accent-mint)' }}
                        >
                          {Math.floor(displayProgress)}%
                        </span>
                      </div>
                    </div>
                    
                    <p 
                      className="text-base font-medium"
                      style={{ color: 'white' }}
                    >
                      {analysisProgress?.message || t('vibeStudio.analyzing')}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right: Tabbed Analysis Panel */}
          <div className="space-y-4">
            <TabGroup>
              {/* Tab Navigation */}
              <TabList
                className="flex rounded-lg p-1 gap-1"
                style={{ backgroundColor: 'var(--bg-canvas)', border: '1px solid var(--border-subtle)' }}
              >
                <Tab
                  className="flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors outline-none data-[selected]:bg-[var(--btn-primary-bg)] data-[selected]:text-[var(--btn-primary-fg)]"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  {t('vibeStudio.tabs.designSystem')}
                </Tab>
                <Tab
                  className="flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors outline-none data-[selected]:bg-[var(--btn-primary-bg)] data-[selected]:text-[var(--btn-primary-fg)]"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  {t('vibeStudio.tabs.aestheticAnalysis')}
                </Tab>
              </TabList>

              {/* Tab Content */}
              <TabPanels>
                <TabPanel>
                  <StyleAnalysisPanel 
                    styleData={styleData}
                    onStyleDataChange={setStyleData}
                    isEmpty={!styleData && !isAnalyzing && currentDesignSystem?.status !== DesignSystemStatus.PROCESSING && currentDesignSystem?.status !== DesignSystemStatus.PENDING}
                    isAnalyzing={isAnalyzing}
                  />
                </TabPanel>
                <TabPanel>
                  <AestheticAnalysisPanel
                    aestheticData={aestheticData}
                    isEmpty={!aestheticData && !isAnalyzing && currentDesignSystem?.status !== DesignSystemStatus.PROCESSING && currentDesignSystem?.status !== DesignSystemStatus.PENDING}
                    isAnalyzing={isAnalyzing}
                    onAestheticDataChange={setAestheticData}
                  />
                </TabPanel>
              </TabPanels>
            </TabGroup>
          </div>
        </div>
      </main>

      {/* Image Expanded Modal */}
      {isImageExpanded && uploadedImages.length > 0 && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/95 p-8"
          onClick={() => setIsImageExpanded(false)}
        >
          <button
            onClick={() => setIsImageExpanded(false)}
            className="absolute top-4 right-4 p-2 rounded-full bg-white/10 hover:bg-white/20 text-white transition-colors"
          >
            <XMarkIcon className="size-6" />
          </button>
          <div className="max-w-7xl max-h-full overflow-auto">
            <img
              src={uploadedImages[0].url}
              alt={uploadedImages[0].name}
              className="w-full h-auto"
              onClick={(e) => e.stopPropagation()}
            />
          </div>
        </div>
      )}

      {/* Export Rules Modal */}
      <ExportRulesModal
        isOpen={isExportModalOpen}
        onClose={() => setIsExportModalOpen(false)}
        styleData={styleData}
        aestheticAnalysis={aestheticData}
        name={name}
        description={description}
      />

      {/* MCP Access Panel */}
      <MCPAccessPanel
        isOpen={isMCPPanelOpen}
        onClose={() => setIsMCPPanelOpen(false)}
        designSystemId={currentDesignSystem?.id}
        designSystemName={name}
        apiKey={currentDesignSystem?.mcp_api_key}
      />
    </div>
  )
}
