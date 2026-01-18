import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { Dialog, DialogBackdrop, DialogPanel, TransitionChild, Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/react'
import {
  Bars3Icon,
  XMarkIcon,
  SwatchIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline'
import { ChevronDownIcon } from '@heroicons/react/20/solid'

function classNames(...classes) {
  return classes.filter(Boolean).join(' ')
}

export default function ConsoleLayout({ children, designSystems = [], onCreateNew }) {
  const { t, i18n } = useTranslation()
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [settingsOpen, setSettingsOpen] = useState(false)

  const toggleLanguage = () => {
    const newLang = i18n.language === 'en' ? 'zh' : 'en'
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
                  className="group -mx-2 flex gap-x-3 rounded-md p-2 text-sm/6 font-semibold transition-colors hover:bg-gray-50 w-full"
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
          <div 
            aria-hidden="true" 
            className="h-6 w-px lg:hidden" 
            style={{ backgroundColor: 'var(--border-subtle)' }}
          />

          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="flex flex-1"></div>
            
            <div className="flex items-center gap-x-4 lg:gap-x-6">
              {/* Separator */}
              <div 
                aria-hidden="true" 
                className="hidden lg:block lg:h-6 lg:w-px" 
                style={{ backgroundColor: 'var(--border-subtle)' }}
              />

              {/* Profile dropdown */}
              <Menu as="div" className="relative">
                <MenuButton className="flex items-center gap-x-3">
                  <span className="sr-only">Open user menu</span>
                  <span 
                    className="flex size-8 shrink-0 items-center justify-center rounded-full font-semibold"
                    style={{ 
                      backgroundColor: 'var(--accent-blue)', 
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
                      className="block w-full text-left px-4 py-2 text-sm data-focus:bg-gray-50"
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
            className="mx-auto max-w-md rounded-xl p-6 w-full"
            style={{ 
              backgroundColor: 'var(--bg-canvas)',
              border: '1px solid var(--border-subtle)'
            }}
          >
            <div className="flex items-center justify-between mb-6">
              <h2 
                className="text-lg font-bold"
                style={{ color: 'var(--text-primary)', fontWeight: 'var(--font-weight-heading)' }}
              >
                {t('console.settings')}
              </h2>
              <button
                onClick={() => setSettingsOpen(false)}
                className="p-1 rounded-md hover:bg-gray-100"
                style={{ color: 'var(--text-secondary)' }}
              >
                <XMarkIcon className="size-5" />
              </button>
            </div>

            {/* Language Setting */}
            <div className="space-y-4">
              <div>
                <label 
                  className="block text-sm font-semibold mb-3"
                  style={{ color: 'var(--text-primary)' }}
                >
                  {t('settings.language')}
                </label>
                <div className="flex gap-3">
                  <button
                    onClick={() => {
                      i18n.changeLanguage('en')
                    }}
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
                    onClick={() => {
                      i18n.changeLanguage('zh')
                    }}
                    className="flex-1 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors"
                    style={{
                      backgroundColor: i18n.language === 'zh' ? 'var(--btn-primary-bg)' : 'var(--bg-surface)',
                      color: i18n.language === 'zh' ? 'var(--btn-primary-fg)' : 'var(--text-primary)',
                      border: i18n.language === 'zh' ? 'none' : '1px solid var(--border-default)'
                    }}
                  >
                    中文
                  </button>
                </div>
              </div>
            </div>

            {/* Close button */}
            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setSettingsOpen(false)}
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
    </div>
  )
}