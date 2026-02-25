import { useState, useEffect } from 'react'
import { CheckCircleIcon, ExclamationTriangleIcon, XCircleIcon, InformationCircleIcon, XMarkIcon } from '@heroicons/react/20/solid'

const alertStyles = {
  success: {
    container: 'bg-green-50 dark:bg-green-500/10 dark:outline dark:outline-green-500/20',
    icon: 'text-green-400',
    text: 'text-green-800 dark:text-green-300',
    button: 'bg-green-50 text-green-500 hover:bg-green-100 focus-visible:ring-green-600 focus-visible:ring-offset-green-50 dark:bg-transparent dark:text-green-400 dark:hover:bg-green-500/10 dark:focus-visible:ring-green-500 dark:focus-visible:ring-offset-green-900',
    Icon: CheckCircleIcon
  },
  error: {
    container: 'bg-red-50 dark:bg-red-500/10 dark:outline dark:outline-red-500/20',
    icon: 'text-red-400',
    text: 'text-red-800 dark:text-red-300',
    button: 'bg-red-50 text-red-500 hover:bg-red-100 focus-visible:ring-red-600 focus-visible:ring-offset-red-50 dark:bg-transparent dark:text-red-400 dark:hover:bg-red-500/10 dark:focus-visible:ring-red-500 dark:focus-visible:ring-offset-red-900',
    Icon: XCircleIcon
  },
  warning: {
    container: 'bg-yellow-50 dark:bg-yellow-500/10 dark:outline dark:outline-yellow-500/20',
    icon: 'text-yellow-400',
    text: 'text-yellow-800 dark:text-yellow-300',
    button: 'bg-yellow-50 text-yellow-500 hover:bg-yellow-100 focus-visible:ring-yellow-600 focus-visible:ring-offset-yellow-50 dark:bg-transparent dark:text-yellow-400 dark:hover:bg-yellow-500/10 dark:focus-visible:ring-yellow-500 dark:focus-visible:ring-offset-yellow-900',
    Icon: ExclamationTriangleIcon
  },
  info: {
    container: 'bg-blue-50 dark:bg-blue-500/10 dark:outline dark:outline-blue-500/20',
    icon: 'text-blue-400',
    text: 'text-blue-800 dark:text-blue-300',
    button: 'bg-blue-50 text-blue-500 hover:bg-blue-100 focus-visible:ring-blue-600 focus-visible:ring-offset-blue-50 dark:bg-transparent dark:text-blue-400 dark:hover:bg-blue-500/10 dark:focus-visible:ring-blue-500 dark:focus-visible:ring-offset-blue-900',
    Icon: InformationCircleIcon
  }
}

/**
 * Alert component for displaying notifications
 * 
 * @param {string} type - Type of alert: 'success', 'error', 'warning', 'info'
 * @param {string} message - Alert message to display
 * @param {boolean} show - Control visibility from parent
 * @param {function} onClose - Callback when alert is dismissed
 * @param {number} autoClose - Auto-close delay in milliseconds (0 = no auto-close)
 */
export default function Alert({ 
  type = 'info', 
  message, 
  show = true, 
  onClose,
  autoClose = 5000 
}) {
  const [visible, setVisible] = useState(show)
  const style = alertStyles[type] || alertStyles.info
  const Icon = style.Icon

  useEffect(() => {
    setVisible(show)
  }, [show])

  useEffect(() => {
    if (visible && autoClose > 0) {
      const timer = setTimeout(() => {
        handleClose()
      }, autoClose)
      return () => clearTimeout(timer)
    }
  }, [visible, autoClose])

  const handleClose = () => {
    setVisible(false)
    onClose?.()
  }

  if (!visible) return null

  return (
    <div className={`rounded-md p-4 ${style.container}`}>
      <div className="flex">
        <div className="shrink-0">
          <Icon aria-hidden="true" className={`size-5 ${style.icon}`} />
        </div>
        <div className="ml-3">
          <p className={`text-sm font-medium ${style.text}`}>{message}</p>
        </div>
        <div className="ml-auto pl-3">
          <div className="-mx-1.5 -my-1.5">
            <button
              type="button"
              onClick={handleClose}
              className={`inline-flex rounded-md p-1.5 focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-hidden ${style.button}`}
            >
              <span className="sr-only">Dismiss</span>
              <XMarkIcon aria-hidden="true" className="size-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
