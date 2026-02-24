import { useTranslation } from 'react-i18next'
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/20/solid'

/**
 * Pagination Component
 * A minimalist pagination component following MonkeyUI design system
 * 
 * @param {Object} props
 * @param {number} props.currentPage - Current page number (1-indexed)
 * @param {number} props.totalPages - Total number of pages
 * @param {number} props.totalCount - Total number of items
 * @param {number} props.pageSize - Items per page
 * @param {Function} props.onPageChange - Callback when page changes
 */
export default function Pagination({ 
  currentPage = 1, 
  totalPages = 1, 
  totalCount = 0,
  pageSize = 10,
  onPageChange 
}) {
  const { t } = useTranslation()

  console.log('[Pagination] Props:', { currentPage, totalPages, totalCount, pageSize })

  // Hide pagination if there are no items
  if (totalCount === 0) {
    console.log('[Pagination] Hidden: totalCount === 0')
    return null
  }

  if (totalPages <= 1) {
    console.log('[Pagination] Hidden: totalPages <= 1')
    return null
  }

  const startItem = (currentPage - 1) * pageSize + 1
  const endItem = Math.min(currentPage * pageSize, totalCount)

  const handlePrevious = () => {
    if (currentPage > 1) {
      onPageChange(currentPage - 1)
    }
  }

  const handleNext = () => {
    if (currentPage < totalPages) {
      onPageChange(currentPage + 1)
    }
  }

  const handlePageClick = (page) => {
    if (page !== currentPage) {
      onPageChange(page)
    }
  }

  // Generate page numbers to display
  const getPageNumbers = () => {
    const pages = []
    const showEllipsis = totalPages > 7

    if (!showEllipsis) {
      // Show all pages if 7 or fewer
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i)
      }
    } else {
      // Show first page, last page, current page and neighbors
      pages.push(1)
      
      if (currentPage > 3) {
        pages.push('ellipsis-start')
      }

      // Show current page and neighbors
      for (let i = Math.max(2, currentPage - 1); i <= Math.min(totalPages - 1, currentPage + 1); i++) {
        pages.push(i)
      }

      if (currentPage < totalPages - 2) {
        pages.push('ellipsis-end')
      }

      if (totalPages > 1) {
        pages.push(totalPages)
      }
    }

    return pages
  }

  const pageNumbers = getPageNumbers()

  return (
    <div 
      className="flex items-center justify-between px-4 py-6"
      style={{ borderTop: '1px solid var(--border-subtle)' }}
    >
      {/* Mobile View */}
      <div className="flex flex-1 justify-between sm:hidden">
        <button
          onClick={handlePrevious}
          disabled={currentPage === 1}
          className="relative inline-flex items-center rounded-md px-4 py-2 text-sm font-medium transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          style={{
            border: '1px solid var(--border-default)',
            backgroundColor: 'var(--bg-canvas)',
            color: 'var(--text-primary)'
          }}
        >
          {t('pagination.previous')}
        </button>
        <button
          onClick={handleNext}
          disabled={currentPage === totalPages}
          className="relative ml-3 inline-flex items-center rounded-md px-4 py-2 text-sm font-medium transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          style={{
            border: '1px solid var(--border-default)',
            backgroundColor: 'var(--bg-canvas)',
            color: 'var(--text-primary)'
          }}
        >
          {t('pagination.next')}
        </button>
      </div>

      {/* Desktop View */}
      <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
        <div>
          <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
            {t('pagination.showing')} <span className="font-medium" style={{ color: 'var(--text-primary)' }}>{startItem}</span> {t('pagination.to')}{' '}
            <span className="font-medium" style={{ color: 'var(--text-primary)' }}>{endItem}</span> {t('pagination.of')}{' '}
            <span className="font-medium" style={{ color: 'var(--text-primary)' }}>{totalCount}</span> {t('pagination.results')}
          </p>
        </div>
        <div>
          <nav
            aria-label={t('pagination.label')}
            className="isolate inline-flex -space-x-px rounded-md"
            style={{ boxShadow: 'var(--shadow-sm)' }}
          >
            {/* Previous Button */}
            <button
              onClick={handlePrevious}
              disabled={currentPage === 1}
              className="relative inline-flex items-center rounded-l-md px-2 py-2 transition-colors focus:z-20 disabled:opacity-40 disabled:cursor-not-allowed"
              style={{
                border: '1px solid var(--border-default)',
                backgroundColor: 'var(--bg-canvas)',
                color: 'var(--text-secondary)'
              }}
              onMouseEnter={(e) => {
                if (currentPage > 1) {
                  e.currentTarget.style.backgroundColor = 'var(--bg-surface)'
                }
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--bg-canvas)'
              }}
            >
              <span className="sr-only">{t('pagination.previous')}</span>
              <ChevronLeftIcon aria-hidden="true" className="size-5" />
            </button>

            {/* Page Numbers */}
            {pageNumbers.map((page, index) => {
              if (typeof page === 'string' && page.startsWith('ellipsis')) {
                return (
                  <span
                    key={page}
                    className="relative inline-flex items-center px-4 py-2 text-sm font-semibold"
                    style={{
                      border: '1px solid var(--border-default)',
                      backgroundColor: 'var(--bg-canvas)',
                      color: 'var(--text-tertiary)'
                    }}
                  >
                    ...
                  </span>
                )
              }

              const isActive = page === currentPage

              return (
                <button
                  key={page}
                  onClick={() => handlePageClick(page)}
                  aria-current={isActive ? 'page' : undefined}
                  className={`relative inline-flex items-center px-4 py-2 text-sm font-semibold transition-colors focus:z-20 ${
                    index > 0 ? 'hidden md:inline-flex' : ''
                  }`}
                  style={{
                    border: '1px solid var(--border-default)',
                    backgroundColor: isActive ? 'var(--btn-primary-bg)' : 'var(--bg-canvas)',
                    color: isActive ? 'var(--btn-primary-fg)' : 'var(--text-primary)'
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.backgroundColor = 'var(--bg-surface)'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.backgroundColor = 'var(--bg-canvas)'
                    }
                  }}
                >
                  {page}
                </button>
              )
            })}

            {/* Next Button */}
            <button
              onClick={handleNext}
              disabled={currentPage === totalPages}
              className="relative inline-flex items-center rounded-r-md px-2 py-2 transition-colors focus:z-20 disabled:opacity-40 disabled:cursor-not-allowed"
              style={{
                border: '1px solid var(--border-default)',
                backgroundColor: 'var(--bg-canvas)',
                color: 'var(--text-secondary)'
              }}
              onMouseEnter={(e) => {
                if (currentPage < totalPages) {
                  e.currentTarget.style.backgroundColor = 'var(--bg-surface)'
                }
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--bg-canvas)'
              }}
            >
              <span className="sr-only">{t('pagination.next')}</span>
              <ChevronRightIcon aria-hidden="true" className="size-5" />
            </button>
          </nav>
        </div>
      </div>
    </div>
  )
}
