import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { Dialog, DialogBackdrop, DialogPanel, TransitionChild, Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/react'
import {
  Bars3Icon,
  XMarkIcon,
  SwatchIcon,
  Cog6ToothIcon,
  KeyIcon,
  GlobeAltIcon,
  CheckIcon,
  ClipboardDocumentIcon,
} from '@heroicons/react/24/outline'
import { ChevronDownIcon } from '@heroicons/react/20/solid'
import { fetchAPIKeys, createAPIKey, deleteAPIKey } from '../../services/apiKeys'
import { Input } from '../ui/input'
import { Label } from '../ui/label'
import { Badge } from '../ui/badge'
import { Separator } from '../ui/separator'

function classNames(...classes) {
  return classes.filter(Boolean).join(' ')
}

export default function ConsoleLayout({ children, designSystems = [], onCreateNew }) {
  const { t, i18n } = useTranslation()
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [activeSettingTab, setActiveSettingTab] = useState('general')
  
  // API Keys state
  const [apiKeys, setApiKeys] = useState([])
  const [loadingKeys, setLoadingKeys] = useState(false)
  const [creatingKey, setCreatingKey] = useState(false)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [newKeyName, setNewKeyName] = useState('')
  const [newlyCreatedKey, setNewlyCreatedKey] = useState(null)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [keyToDelete, setKeyToDelete] = useState(null)
  const [copiedKeyId, setCopiedKeyId] = useState(null)

  // Load API keys when settings dialog opens and API Keys tab is active
  useEffect(() => {
    if (settingsOpen && activeSettingTab === 'apiKeys') {
      loadAPIKeys()
    }
  }, [settingsOpen, activeSettingTab])

  const loadAPIKeys = async () => {
    setLoadingKeys(true)
    try {
      const data = await fetchAPIKeys()
      // Handle both paginated response and direct array response
      const keys = data?.results ? data.results : (Array.isArray(data) ? data : [])
      setApiKeys(keys)
    } catch (error) {
      console.error('Failed to load API keys:', error)
      setApiKeys([])
    } finally {
      setLoadingKeys(false)
    }
  }

  const handleCreateKey = async () => {
    if (!newKeyName.trim()) return
    
    setCreatingKey(true)
    try {
      const response = await createAPIKey({ name: newKeyName })
      setNewlyCreatedKey(response.api_key)
      setShowCreateDialog(false)
      setNewKeyName('')
      // Reload the API keys list to show the newly created key
      await loadAPIKeys()
    } catch (error) {
      console.error('Failed to create API key:', error)
      alert(t('settings.apiKeyManagement.createError'))
    } finally {
      setCreatingKey(false)
    }
  }

  const handleCloseNewKeyDialog = () => {
    setNewlyCreatedKey(null)
    // Ensure the list is refreshed when closing the dialog
    if (activeSettingTab === 'apiKeys') {
      loadAPIKeys()
    }
  }

  const handleDeleteKey = async () => {
    if (!keyToDelete) return
    
    try {
      await deleteAPIKey(keyToDelete.id)
      setShowDeleteDialog(false)
      setKeyToDelete(null)
      await loadAPIKeys()
    } catch (error) {
      console.error('Failed to delete API key:', error)
      alert(t('settings.apiKeyManagement.deleteError'))
    }
  }

  const copyToClipboard = async (text, keyId = null) => {
    try {
      await navigator.clipboard.writeText(text)
      if (keyId) {
        setCopiedKeyId(keyId)
        setTimeout(() => setCopiedKeyId(null), 2000)
      }
    } catch (error) {
      console.error('Failed to copy:', error)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return t('settings.apiKeyManagement.never')
    // Map i18n language codes to locale codes for toLocaleDateString
    const localeMap = {
      'en': 'en-US',
      'zh-CN': 'zh-CN'
    }
    const locale = localeMap[i18n.language] || 'en-US'
    return new Date(dateString).toLocaleDateString(locale, {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const settingsTabs = [
    { id: 'general', name: t('settings.general'), icon: GlobeAltIcon },
    { id: 'apiKeys', name: t('settings.apiKeys'), icon: KeyIcon },
  ]

  const toggleLanguage = () => {
    const newLang = i18n.language === 'en' ? 'zh-CN' : 'en'
    i18n.changeLanguage(newLang)
  }

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <div className="h-full" style={{ backgroundColor: 'var(--bg-canvas)' }}>
      {/* Mobile sidebar */}
      <Dialog open={sidebarOpen} onClose={setSidebarOpen} className="relative z-50 lg:hidden">
        <DialogBackdrop
          transition
          className="fixed inset-0 bg-gray-900/80 transition-opacity duration-300 ease-linear data-closed:opacity-0"
        />

        <div className="fixed inset-0 flex">
          <DialogPanel
            transition
            className="relative mr-16 flex w-full max-w-xs flex-1 transform transition duration-300 ease-in-out data-closed:-translate-x-full"
          >
            <TransitionChild>
              <div className="absolute top-0 left-full flex w-16 justify-center pt-5 duration-300 ease-in-out data-closed:opacity-0">
                <button type="button" onClick={() => setSidebarOpen(false)} className="-m-2.5 p-2.5">
                  <span className="sr-only">{t('console.closeSidebar')}</span>
                  <XMarkIcon aria-hidden="true" className="size-6 text-white" />
                </button>
              </div>
            </TransitionChild>

            {/* Mobile Sidebar content */}
            <div 
              className="relative flex grow flex-col gap-y-5 overflow-y-auto px-6 pb-2"
              style={{ backgroundColor: 'var(--bg-canvas)', borderRight: '1px solid var(--border-subtle)' }}
            >
              <div className="relative flex h-16 shrink-0 items-center">
                <span 
                  className="text-xl font-bold"
                  style={{ color: 'var(--text-primary)', fontWeight: 'var(--font-weight-heading)' }}
                >
                  MonkeyUI
                </span>
              </div>
              <nav className="relative flex flex-1 flex-col">
                <ul role="list" className="flex flex-1 flex-col gap-y-7">
                  <li>
                    <div 
                      className="flex items-center justify-between"
                    >
                      <div className="flex items-center gap-x-2">
                        <SwatchIcon className="size-5" style={{ color: 'var(--text-secondary)' }} />
                        <span 
                          className="text-xs/6 font-semibold"
                          style={{ color: 'var(--text-secondary)' }}
                        >
                          {t('console.designWorkshop')}
                        </span>
                      </div>
                    </div>
                  </li>
                </ul>
              </nav>
            </div>
          </DialogPanel>
        </div>
      </Dialog>

      {/* Static sidebar for desktop */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-72 lg:flex-col">
        <div 
          className="flex grow flex-col gap-y-5 overflow-y-auto px-6"
          style={{ backgroundColor: 'var(--bg-canvas)', borderRight: '1px solid var(--border-subtle)' }}
        >
          <div className="flex h-16 shrink-0 items-center">
            <span 
              className="text-xl font-bold"
              style={{ color: 'var(--text-primary)', fontWeight: 'var(--font-weight-heading)' }}
            >
              MonkeyUI
            </span>
          </div>
          <nav className="flex flex-1 flex-col">
            <ul role="list" className="flex flex-1 flex-col gap-y-7">
              <li>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-x-2">
                    <SwatchIcon className="size-5" style={{ color: 'var(--text-secondary)' }} />
                    <span 
                      className="text-xs/6 font-semibold"
                      style={{ color: 'var(--text-secondary)' }}
                    >
                      {t('console.designWorkshop')}
                    </span>
                  </div>
                </div>
              </li>
              {/* Settings button */}
              <li className="mt-auto">
                <button
                  onClick={() => setSettingsOpen(true)}
                  className="group -mx-2 flex gap-x-3 rounded-2xl p-2 text-sm/6 font-semibold transition-colors hover:bg-white/5 w-full"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  <Cog6ToothIcon className="size-6 shrink-0" />
                  {t('console.settings')}
                </button>
              </li>
            </ul>
          </nav>
        </div>
      </div>

      {/* Mobile header */}
      <div 
        className="sticky top-0 z-40 flex items-center gap-x-6 px-4 py-4 sm:px-6 lg:hidden"
        style={{ backgroundColor: 'var(--bg-canvas)', borderBottom: '1px solid var(--border-subtle)' }}
      >
        <button
          type="button"
          onClick={() => setSidebarOpen(true)}
          className="-m-2.5 p-2.5"
          style={{ color: 'var(--text-secondary)' }}
        >
          <span className="sr-only">{t('console.openSidebar')}</span>
          <Bars3Icon aria-hidden="true" className="size-6" />
        </button>
        <div className="flex-1 text-sm/6 font-semibold" style={{ color: 'var(--text-primary)' }}>
          {t('console.designWorkshop')}
        </div>
        <button
          onClick={toggleLanguage}
          className="text-sm/6 font-medium"
          style={{ color: 'var(--text-secondary)' }}
        >
          {i18n.language === 'en' ? '中文' : 'EN'}
        </button>
      </div>

      {/* Main content */}
      <main className="lg:pl-72">
        {/* Top header bar */}
        <div 
          className="sticky top-0 z-40 flex h-16 shrink-0 items-center gap-x-4 border-b px-4 sm:gap-x-6 sm:px-6 lg:px-8"
          style={{ 
            backgroundColor: 'var(--bg-canvas)', 
            borderColor: 'var(--border-subtle)' 
          }}
        >
          {/* Mobile menu button */}
          <button
            type="button"
            onClick={() => setSidebarOpen(true)}
            className="-m-2.5 p-2.5 lg:hidden"
            style={{ color: 'var(--text-secondary)' }}
          >
            <span className="sr-only">{t('console.openSidebar')}</span>
            <Bars3Icon aria-hidden="true" className="size-6" />
          </button>

          {/* Separator */}
          <Separator orientation="vertical" className="h-6 lg:hidden" />

          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="flex flex-1"></div>
            
            <div className="flex items-center gap-x-4 lg:gap-x-6">
              {/* Separator */}
              <Separator orientation="vertical" className="hidden lg:block lg:h-6" />

              {/* Profile dropdown */}
              <Menu as="div" className="relative">
                <MenuButton className="flex items-center gap-x-3">
                  <span className="sr-only">Open user menu</span>
                  <span 
                    className="flex size-8 shrink-0 items-center justify-center rounded-full font-semibold"
                    style={{ 
                      backgroundColor: 'var(--accent-mint)', 
                      color: 'var(--text-on-dark)' 
                    }}
                  >
                    {user?.name?.charAt(0).toUpperCase() || user?.email?.charAt(0).toUpperCase()}
                  </span>
                  <span className="hidden lg:flex lg:items-center">
                    <span 
                      aria-hidden="true" 
                      className="text-sm/6 font-semibold"
                      style={{ color: 'var(--text-primary)' }}
                    >
                      {user?.name || user?.email?.split('@')[0]}
                    </span>
                    <ChevronDownIcon 
                      aria-hidden="true" 
                      className="ml-2 size-5" 
                      style={{ color: 'var(--text-tertiary)' }}
                    />
                  </span>
                </MenuButton>
                <MenuItems
                  transition
                  className="absolute right-0 z-10 mt-2.5 w-64 origin-top-right rounded-xl py-2 shadow-lg transition data-closed:scale-95 data-closed:transform data-closed:opacity-0 data-enter:duration-100 data-enter:ease-out data-leave:duration-75 data-leave:ease-in"
                  style={{ 
                    backgroundColor: 'var(--bg-canvas)', 
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-md)'
                  }}
                >
                  {/* User info section */}
                  <div className="px-4 py-3 border-b" style={{ borderColor: 'var(--border-subtle)' }}>
                    <p className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
                      {user?.name || t('auth.fields.name')}
                    </p>
                    <p className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>
                      {user?.email}
                    </p>
                  </div>
                  
                  <MenuItem>
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 text-sm data-focus:bg-white/5"
                      style={{ color: 'var(--text-primary)' }}
                    >
                      {t('common.logout')}
                    </button>
                  </MenuItem>
                </MenuItems>
              </Menu>
            </div>
          </div>
        </div>

        {/* Page content */}
        <div className="px-4 py-10 sm:px-6 lg:px-8">
          {children}
        </div>
      </main>

      {/* Settings Dialog */}
      <Dialog open={settingsOpen} onClose={setSettingsOpen} className="relative z-50">
        <DialogBackdrop className="fixed inset-0 bg-black/30" />
        <div className="fixed inset-0 flex items-center justify-center p-4">
          <DialogPanel 
            className="mx-auto max-w-4xl rounded-xl w-full flex overflow-hidden"
            style={{ 
              backgroundColor: 'var(--bg-canvas)',
              border: '1px solid var(--border-subtle)',
              height: '600px'
            }}
          >
            {/* Vertical Navigation */}
            <div 
              className="w-56 flex-shrink-0 py-6"
              style={{ 
                borderRight: '1px solid var(--border-subtle)',
                backgroundColor: 'var(--bg-surface)'
              }}
            >
              <div className="px-4 mb-6">
                <h2 
                  className="text-lg font-bold"
                  style={{ color: 'var(--text-primary)', fontWeight: 'var(--font-weight-heading)' }}
                >
                  {t('console.settings')}
                </h2>
              </div>
              
              <nav className="space-y-1 px-2">
                {settingsTabs.map((tab) => {
                  const Icon = tab.icon
                  const isActive = activeSettingTab === tab.id
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveSettingTab(tab.id)}
                      className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors"
                      style={{
                        backgroundColor: isActive ? 'var(--bg-canvas)' : 'transparent',
                        color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                        border: isActive ? '1px solid var(--border-subtle)' : '1px solid transparent'
                      }}
                    >
                      <Icon className="size-5" />
                      {tab.name}
                    </button>
                  )
                })}
              </nav>
            </div>

            {/* Content Area */}
            <div className="flex-1 flex flex-col overflow-hidden">
              {/* Header */}
              <div 
                className="flex items-center justify-between px-6 py-4"
                style={{ borderBottom: '1px solid var(--border-subtle)' }}
              >
                <h3 
                  className="text-base font-semibold"
                  style={{ color: 'var(--text-primary)' }}
                >
                  {settingsTabs.find(tab => tab.id === activeSettingTab)?.name}
                </h3>
                <button
                  onClick={() => {
                    setSettingsOpen(false)
                    setActiveSettingTab('general')
                  }}
                  className="p-1 rounded-full hover:bg-[#F5F0FF]"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  <XMarkIcon className="size-5" />
                </button>
              </div>

              {/* Scrollable Content */}
              <div className="flex-1 overflow-y-auto px-6 py-6">
                {activeSettingTab === 'general' && (
                  <div className="space-y-6">
                    {/* Language Setting */}
                    <div>
                      <Label className="mb-3">{t('settings.language')}</Label>
                      <div className="flex gap-3">
                        <button
                          onClick={() => i18n.changeLanguage('en')}
                          className="flex-1 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors"
                          style={{
                            backgroundColor: i18n.language === 'en' ? 'var(--btn-primary-bg)' : 'var(--bg-surface)',
                            color: i18n.language === 'en' ? 'var(--btn-primary-fg)' : 'var(--text-primary)',
                            border: i18n.language === 'en' ? 'none' : '1px solid var(--border-default)'
                          }}
                        >
                          English
                        </button>
                        <button
                          onClick={() => i18n.changeLanguage('zh-CN')}
                          className="flex-1 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors"
                          style={{
                            backgroundColor: i18n.language === 'zh-CN' ? 'var(--btn-primary-bg)' : 'var(--bg-surface)',
                            color: i18n.language === 'zh-CN' ? 'var(--btn-primary-fg)' : 'var(--text-primary)',
                            border: i18n.language === 'zh-CN' ? 'none' : '1px solid var(--border-default)'
                          }}
                        >
                          中文
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                {activeSettingTab === 'apiKeys' && (
                  <div className="space-y-6">
                    {/* Header with description and count */}
                    <div>
                      <p className="text-sm mb-2" style={{ color: 'var(--text-secondary)' }}>
                        {t('settings.apiKeyManagement.description')}
                      </p>
                      {!loadingKeys && (
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-medium" style={{ color: 'var(--text-tertiary)' }}>
                            {t('settings.apiKeyManagement.keyCount', { count: apiKeys.length })}
                          </span>
                          {apiKeys.length >= 10 && (
                            <span 
                              className="text-xs px-2 py-0.5 rounded"
                              style={{ backgroundColor: 'var(--accent-yellow)', color: 'var(--text-primary)' }}
                            >
                              {t('settings.apiKeyManagement.limitReached')}
                            </span>
                          )}
                        </div>
                      )}
                    </div>

                    {/* Create New Key Button */}
                    <div>
                      <button
                        onClick={() => setShowCreateDialog(true)}
                        disabled={apiKeys.length >= 10}
                        className="px-4 py-2.5 rounded-lg text-sm font-medium transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
                        style={{
                          backgroundColor: 'var(--btn-primary-bg)',
                          color: 'var(--btn-primary-fg)'
                        }}
                      >
                        {t('settings.apiKeyManagement.createNew')}
                      </button>
                    </div>

                    {/* API Keys List */}
                    {loadingKeys ? (
                      <div className="text-center py-12" style={{ color: 'var(--text-secondary)' }}>
                        {t('common.loading')}
                      </div>
                    ) : apiKeys.length === 0 ? (
                      <div 
                        className="text-center py-16 rounded-lg"
                        style={{ 
                          backgroundColor: 'var(--bg-surface)',
                          border: '1px solid var(--border-subtle)'
                        }}
                      >
                        <KeyIcon className="mx-auto size-12 mb-4" style={{ color: 'var(--text-tertiary)' }} />
                        <h3 className="text-sm font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
                          {t('settings.apiKeyManagement.noKeys')}
                        </h3>
                        <p className="text-sm px-8" style={{ color: 'var(--text-secondary)' }}>
                          {t('settings.apiKeyManagement.noKeysDescription')}
                        </p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {apiKeys.map((key) => (
                          <div
                            key={key.id}
                            className="p-5 rounded-lg transition-shadow hover:shadow-sm"
                            style={{
                              backgroundColor: 'var(--bg-surface)',
                              border: '1px solid var(--border-subtle)'
                            }}
                          >
                            <div className="flex items-start justify-between gap-4">
                              <div className="flex-1 min-w-0">
                                {/* Name and Status */}
                                <div className="flex items-center gap-2.5 mb-3">
                                  <h4 className="text-sm font-semibold truncate" style={{ color: 'var(--text-primary)' }}>
                                    {key.name}
                                  </h4>
                                  <Badge
                                    variant={key.is_active ? 'success' : 'muted'}
                                    className="flex-shrink-0"
                                  >
                                    {key.is_active ? t('settings.apiKeyManagement.active') : t('settings.apiKeyManagement.inactive')}
                                  </Badge>
                                </div>
                                
                                {/* Key Display */}
                                <div className="mb-3">
                                  <code 
                                    className="text-xs px-3 py-1.5 rounded inline-block font-mono"
                                    style={{ 
                                      backgroundColor: 'var(--bg-canvas)',
                                      color: 'var(--text-secondary)',
                                      border: '1px solid var(--border-subtle)'
                                    }}
                                  >
                                    {key.key_display}
                                  </code>
                                </div>
                                
                                {/* Metadata */}
                                <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs" style={{ color: 'var(--text-tertiary)' }}>
                                  <div className="flex items-center gap-1.5">
                                    <span className="font-medium">{t('settings.apiKeyManagement.created')}:</span>
                                    <span>{formatDate(key.created_at)}</span>
                                  </div>
                                  <div className="flex items-center gap-1.5">
                                    <span className="font-medium">{t('settings.apiKeyManagement.lastUsed')}:</span>
                                    <span>{formatDate(key.last_used_at)}</span>
                                  </div>
                                </div>
                              </div>
                              
                              {/* Delete Button */}
                              <button
                                onClick={() => {
                                  setKeyToDelete(key)
                                  setShowDeleteDialog(true)
                                }}
                                className="px-3 py-2 text-xs font-medium rounded-lg transition-colors flex-shrink-0"
                                style={{ 
                                  color: 'var(--color-error)',
                                  border: '1px solid var(--border-default)'
                                }}
                                onMouseEnter={(e) => {
                                  e.currentTarget.style.backgroundColor = 'rgba(239, 68, 68, 0.1)'
                                  e.currentTarget.style.borderColor = 'var(--color-error)'
                                }}
                                onMouseLeave={(e) => {
                                  e.currentTarget.style.backgroundColor = 'transparent'
                                  e.currentTarget.style.borderColor = 'var(--border-default)'
                                }}
                              >
                                {t('settings.apiKeyManagement.delete')}
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </DialogPanel>
        </div>
      </Dialog>

      {/* Create API Key Dialog */}
      <Dialog open={showCreateDialog} onClose={() => setShowCreateDialog(false)} className="relative z-50">
        <DialogBackdrop className="fixed inset-0 bg-black/30" />
        <div className="fixed inset-0 flex items-center justify-center p-4">
          <DialogPanel 
            className="mx-auto max-w-md rounded-xl p-6 w-full"
            style={{ 
              backgroundColor: 'var(--bg-canvas)',
              border: '1px solid var(--border-subtle)'
            }}
          >
            <h3 
              className="text-lg font-bold mb-4"
              style={{ color: 'var(--text-primary)', fontWeight: 'var(--font-weight-heading)' }}
            >
              {t('settings.apiKeyManagement.createNew')}
            </h3>
            
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>{t('settings.apiKeyManagement.keyName')}</Label>
                <Input
                  type="text"
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                  placeholder={t('settings.apiKeyManagement.keyNamePlaceholder')}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !creatingKey) {
                      handleCreateKey()
                    }
                  }}
                />
              </div>
            </div>

            <div className="mt-6 flex gap-3 justify-end">
              <button
                onClick={() => setShowCreateDialog(false)}
                className="px-4 py-2 rounded-lg text-sm font-medium"
                style={{
                  backgroundColor: 'var(--bg-surface)',
                  color: 'var(--text-primary)',
                  border: '1px solid var(--border-default)'
                }}
              >
                {t('common.cancel')}
              </button>
              <button
                onClick={handleCreateKey}
                disabled={creatingKey || !newKeyName.trim()}
                className="px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50"
                style={{
                  backgroundColor: 'var(--btn-primary-bg)',
                  color: 'var(--btn-primary-fg)'
                }}
              >
                {creatingKey ? t('common.saving') : t('common.save')}
              </button>
            </div>
          </DialogPanel>
        </div>
      </Dialog>

      {/* Show Newly Created Key Dialog */}
      <Dialog open={!!newlyCreatedKey} onClose={handleCloseNewKeyDialog} className="relative z-50">
        <DialogBackdrop className="fixed inset-0 bg-black/30" />
        <div className="fixed inset-0 flex items-center justify-center p-4">
          <DialogPanel 
            className="mx-auto max-w-md rounded-xl p-6 w-full"
            style={{ 
              backgroundColor: 'var(--bg-canvas)',
              border: '1px solid var(--border-subtle)'
            }}
          >
            <div className="flex items-center gap-3 mb-4">
              <div 
                className="size-10 rounded-full flex items-center justify-center"
                style={{ backgroundColor: 'var(--color-success)' }}
              >
                <CheckIcon className="size-6 text-white" />
              </div>
              <h3 
                className="text-lg font-bold"
                style={{ color: 'var(--text-primary)', fontWeight: 'var(--font-weight-heading)' }}
              >
                {t('settings.apiKeyManagement.createSuccess')}
              </h3>
            </div>
            
            <div 
              className="p-3 rounded-lg mb-4"
              style={{ backgroundColor: 'var(--accent-yellow)', color: 'var(--text-primary)' }}
            >
              <p className="text-sm font-medium">
                {t('settings.apiKeyManagement.createWarning')}
              </p>
            </div>

            <div className="space-y-3">
              <div>
                <Label className="text-xs mb-1">{t('settings.apiKeyManagement.keyName')}</Label>
                <div className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                  {newlyCreatedKey?.name}
                </div>
              </div>
              
              <div>
                <Label className="text-xs mb-1">API Key</Label>
                <div 
                  className="flex items-center gap-2 p-2 rounded-lg"
                  style={{ backgroundColor: 'var(--bg-surface)', border: '1px solid var(--border-subtle)' }}
                >
                  <code className="flex-1 text-xs break-all" style={{ color: 'var(--text-primary)' }}>
                    {newlyCreatedKey?.key}
                  </code>
                  <button
                    onClick={() => copyToClipboard(newlyCreatedKey?.key)}
                    className="p-1.5 rounded-full hover:bg-[#F5F0FF]"
                    style={{ color: 'var(--text-secondary)' }}
                  >
                    <ClipboardDocumentIcon className="size-4" />
                  </button>
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={handleCloseNewKeyDialog}
                className="px-4 py-2 rounded-lg text-sm font-medium"
                style={{
                  backgroundColor: 'var(--btn-primary-bg)',
                  color: 'var(--btn-primary-fg)'
                }}
              >
                {t('common.close')}
              </button>
            </div>
          </DialogPanel>
        </div>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onClose={() => setShowDeleteDialog(false)} className="relative z-50">
        <DialogBackdrop className="fixed inset-0 bg-black/30" />
        <div className="fixed inset-0 flex items-center justify-center p-4">
          <DialogPanel 
            className="mx-auto max-w-md rounded-xl p-6 w-full"
            style={{ 
              backgroundColor: 'var(--bg-canvas)',
              border: '1px solid var(--border-subtle)'
            }}
          >
            <h3 
              className="text-lg font-bold mb-4"
              style={{ color: 'var(--text-primary)', fontWeight: 'var(--font-weight-heading)' }}
            >
              {t('settings.apiKeyManagement.confirmDelete')}
            </h3>
            
            <p className="text-sm mb-2" style={{ color: 'var(--text-secondary)' }}>
              {t('settings.apiKeyManagement.deleteWarning')}
            </p>

            {keyToDelete && (
              <div 
                className="p-3 rounded-lg mb-4 mt-4"
                style={{ backgroundColor: 'var(--bg-surface)', border: '1px solid var(--border-subtle)' }}
              >
                <div className="text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  {keyToDelete.name}
                </div>
                <code className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                  {keyToDelete.key_display}
                </code>
              </div>
            )}

            <div className="mt-6 flex gap-3 justify-end">
              <button
                onClick={() => setShowDeleteDialog(false)}
                className="px-4 py-2 rounded-lg text-sm font-medium"
                style={{
                  backgroundColor: 'var(--bg-surface)',
                  color: 'var(--text-primary)',
                  border: '1px solid var(--border-default)'
                }}
              >
                {t('common.cancel')}
              </button>
              <button
                onClick={handleDeleteKey}
                className="px-4 py-2 rounded-lg text-sm font-medium"
                style={{
                  backgroundColor: 'var(--color-error)',
                  color: 'white'
                }}
              >
                {t('common.delete')}
              </button>
            </div>
          </DialogPanel>
        </div>
      </Dialog>
    </div>
  )
}