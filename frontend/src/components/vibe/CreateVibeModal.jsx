import { Fragment, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Dialog, DialogPanel, DialogTitle, Transition, TransitionChild } from '@headlessui/react'
import { XMarkIcon, ArrowRightIcon } from '@heroicons/react/24/outline'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'

export default function CreateVibeModal({ isOpen, onClose, onGoToStudio }) {
  const { t } = useTranslation()
  const [vibeName, setVibeName] = useState('')
  const [styleDescription, setStyleDescription] = useState('')

  const handleSubmit = () => {
    if (vibeName.trim()) {
      onGoToStudio({
        name: vibeName.trim(),
        description: styleDescription.trim()
      })
      // Reset form
      setVibeName('')
      setStyleDescription('')
    }
  }

  const handleClose = () => {
    setVibeName('')
    setStyleDescription('')
    onClose()
  }

  return (
    <Transition show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={handleClose}>
        <TransitionChild
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/60 transition-opacity" />
        </TransitionChild>

        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <TransitionChild
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <DialogPanel 
                className="relative w-full max-w-lg transform overflow-hidden rounded-2xl p-6 shadow-xl transition-all"
                style={{ backgroundColor: 'var(--bg-canvas)', border: '1px solid var(--border-subtle)' }}
              >
                {/* Close button */}
                <button
                  onClick={handleClose}
                  className="absolute top-4 right-4 p-2 rounded-full hover:bg-white/5 transition-colors"
                >
                  <XMarkIcon className="size-5" style={{ color: 'var(--text-secondary)' }} />
                </button>

                {/* Header */}
                <DialogTitle
                  className="text-xl font-bold mb-6"
                  style={{ color: 'var(--text-primary)', fontWeight: 'var(--font-weight-heading)' }}
                >
                  {t('vibeStudio.createNew')}
                </DialogTitle>

                {/* Form */}
                <div className="space-y-5">
                  {/* Vibe Name */}
                  <div className="space-y-2">
                    <Label htmlFor="vibe-name">{t('vibeStudio.vibeName')}</Label>
                    <Input
                      type="text"
                      id="vibe-name"
                      value={vibeName}
                      onChange={(e) => setVibeName(e.target.value)}
                      placeholder={t('vibeStudio.vibeNamePlaceholder')}
                    />
                  </div>

                  {/* Style Description */}
                  <div className="space-y-2">
                    <Label htmlFor="style-description">{t('vibeStudio.styleDescription')}</Label>
                    <Textarea
                      id="style-description"
                      value={styleDescription}
                      onChange={(e) => setStyleDescription(e.target.value)}
                      placeholder={t('vibeStudio.styleDescriptionPlaceholder')}
                      rows={5}
                    />
                  </div>
                </div>

                {/* Footer */}
                <div className="mt-6 flex justify-end">
                  <Button 
                    onClick={handleSubmit}
                    disabled={!vibeName.trim()}
                    className="gap-x-2"
                    style={{ 
                      backgroundColor: vibeName.trim() ? 'var(--accent-mint)' : 'var(--bg-surface)',
                      color: vibeName.trim() ? 'var(--text-on-dark)' : 'var(--text-tertiary)'
                    }}
                  >
                    {t('vibeStudio.goToStudio')}
                    <ArrowRightIcon className="size-4" />
                  </Button>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </Transition>
  )
}
