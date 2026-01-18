import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';

export default function Login() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { login } = useAuth();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || t('auth.login.error'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col justify-center px-6 py-12 lg:px-8" style={{ backgroundColor: 'var(--bg-canvas)' }}>
      <div className="sm:mx-auto sm:w-full sm:max-w-sm">
        <h2 
          className="mt-10 text-center text-4xl font-extrabold tracking-tight"
          style={{ 
            color: 'var(--text-primary)',
            fontWeight: 'var(--font-weight-heading)'
          }}
        >
          {t('auth.login.title')}
        </h2>
        <p 
          className="mt-2 text-center text-base"
          style={{ color: 'var(--text-secondary)' }}
        >
          {t('auth.login.subtitle')}
        </p>
      </div>

      <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
        {error && (
          <div 
            className="mb-4 rounded-xl px-4 py-3 text-sm"
            style={{ 
              backgroundColor: 'var(--color-error)',
              color: 'var(--text-on-dark)',
              borderRadius: 'var(--radius-md)'
            }}
          >
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label 
              htmlFor="email" 
              className="block text-sm font-medium mb-2"
              style={{ color: 'var(--text-primary)' }}
            >
              {t('auth.fields.email')}
            </label>
            <input
              id="email"
              name="email"
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="block w-full rounded-xl px-4 py-3 text-base outline-none transition-all"
              style={{ 
                backgroundColor: 'var(--bg-surface)',
                color: 'var(--text-primary)',
                border: '1px solid var(--border-default)',
                borderRadius: 'var(--radius-md)'
              }}
              placeholder={t('auth.fields.emailPlaceholder')}
            />
          </div>

          <div>
            <label 
              htmlFor="password" 
              className="block text-sm font-medium mb-2"
              style={{ color: 'var(--text-primary)' }}
            >
              {t('auth.fields.password')}
            </label>
            <input
              id="password"
              name="password"
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="block w-full rounded-xl px-4 py-3 text-base outline-none transition-all"
              style={{ 
                backgroundColor: 'var(--bg-surface)',
                color: 'var(--text-primary)',
                border: '1px solid var(--border-default)',
                borderRadius: 'var(--radius-md)'
              }}
              placeholder={t('auth.fields.passwordPlaceholder')}
            />
          </div>

          <div>
            <Button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl px-6 py-3 text-base font-semibold transition-all"
              style={{ 
                backgroundColor: 'var(--btn-primary-bg)',
                color: 'var(--btn-primary-fg)',
                borderRadius: 'var(--radius-md)'
              }}
            >
              {loading ? t('common.loading') : t('auth.login.submit')}
            </Button>
          </div>
        </form>

        <p className="mt-10 text-center text-sm" style={{ color: 'var(--text-secondary)' }}>
          {t('auth.login.noAccount')}{' '}
          <Link 
            to="/register" 
            className="font-semibold"
            style={{ color: 'var(--link-default)' }}
          >
            {t('auth.login.registerLink')}
          </Link>
        </p>
      </div>
    </div>
  );
}
