import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'

function App() {
  const { t, i18n } = useTranslation()
  const [count, setCount] = useState(0)

  const toggleLanguage = () => {
    const newLang = i18n.language === 'en' ? 'zh' : 'en'
    i18n.changeLanguage(newLang)
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto text-center space-y-8">
          <h1 className="text-4xl font-extrabold tracking-tight" style={{ fontWeight: 800 }}>
            {t('welcome.title')}
          </h1>
          
          <p className="text-xl" style={{ color: 'var(--text-secondary)' }}>
            {t('welcome.description')}
          </p>

          <div className="flex items-center justify-center gap-4">
            <Button onClick={() => setCount((count) => count + 1)}>
              {t('welcome.counter')}: {count}
            </Button>
            
            <Button variant="outline" onClick={toggleLanguage}>
              {i18n.language === 'en' ? '中文' : 'English'}
            </Button>
          </div>

          <div className="pt-8" style={{ borderTop: '1px solid var(--border-subtle)' }}>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
              {t('welcome.techStack')}
            </p>
            <div className="flex flex-wrap justify-center gap-2 mt-4">
              <span className="px-3 py-1 text-sm" style={{ backgroundColor: 'var(--bg-surface)', color: 'var(--text-primary)', borderRadius: 'var(--radius-md)' }}>
                React
              </span>
              <span className="px-3 py-1 text-sm" style={{ backgroundColor: 'var(--bg-surface)', color: 'var(--text-primary)', borderRadius: 'var(--radius-md)' }}>
                Vite
              </span>
              <span className="px-3 py-1 text-sm" style={{ backgroundColor: 'var(--bg-surface)', color: 'var(--text-primary)', borderRadius: 'var(--radius-md)' }}>
                TailwindCSS
              </span>
              <span className="px-3 py-1 text-sm" style={{ backgroundColor: 'var(--bg-surface)', color: 'var(--text-primary)', borderRadius: 'var(--radius-md)' }}>
                Shadcn/ui
              </span>
              <span className="px-3 py-1 text-sm" style={{ backgroundColor: 'var(--bg-surface)', color: 'var(--text-primary)', borderRadius: 'var(--radius-md)' }}>
                Django
              </span>
              <span className="px-3 py-1 text-sm" style={{ backgroundColor: 'var(--bg-surface)', color: 'var(--text-primary)', borderRadius: 'var(--radius-md)' }}>
                PostgreSQL
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
