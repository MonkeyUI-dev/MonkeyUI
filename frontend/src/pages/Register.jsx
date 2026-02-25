import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';

export default function Register() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { register } = useAuth();
  
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (password !== passwordConfirm) {
      setError(t('auth.register.passwordMismatch'));
      return;
    }

    setLoading(true);

    try {
      await register(name, email, password, passwordConfirm);
      navigate('/');
    } catch (err) {
      const errorData = err.response?.data;
      if (errorData) {
        // Handle field-specific errors
        const errors = [];
        Object.keys(errorData).forEach(key => {
          if (Array.isArray(errorData[key])) {
            errors.push(...errorData[key]);
          } else if (typeof errorData[key] === 'string') {
            errors.push(errorData[key]);
          }
        });
        setError(errors.join(' ') || t('auth.register.error'));
      } else {
        setError(t('auth.register.error'));
      }
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
          {t('auth.register.title')}
        </h2>
        <p 
          className="mt-2 text-center text-base"
          style={{ color: 'var(--text-secondary)' }}
        >
          {t('auth.register.subtitle')}
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
          <div className="space-y-2">
            <Label htmlFor="name">{t('auth.fields.name')}</Label>
            <Input
              id="name"
              name="name"
              type="text"
              required
              autoComplete="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={t('auth.fields.namePlaceholder')}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">{t('auth.fields.email')}</Label>
            <Input
              id="email"
              name="email"
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={t('auth.fields.emailPlaceholder')}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">{t('auth.fields.password')}</Label>
            <Input
              id="password"
              name="password"
              type="password"
              required
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={t('auth.fields.passwordPlaceholder')}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="passwordConfirm">{t('auth.fields.passwordConfirm')}</Label>
            <Input
              id="passwordConfirm"
              name="passwordConfirm"
              type="password"
              required
              autoComplete="new-password"
              value={passwordConfirm}
              onChange={(e) => setPasswordConfirm(e.target.value)}
              placeholder={t('auth.fields.passwordConfirmPlaceholder')}
            />
          </div>

          <div>
            <Button
              type="submit"
              disabled={loading}
              className="w-full rounded-full px-6 py-3 text-base font-semibold transition-all"
              style={{ 
                backgroundColor: 'var(--btn-primary-bg)',
                color: 'var(--btn-primary-fg)',
                borderRadius: 'var(--radius-pill)'
              }}
            >
              {loading ? t('common.loading') : t('auth.register.submit')}
            </Button>
          </div>
        </form>

        <p className="mt-10 text-center text-sm" style={{ color: 'var(--text-secondary)' }}>
          {t('auth.register.hasAccount')}{' '}
          <Link 
            to="/login" 
            className="font-semibold"
            style={{ color: 'var(--link-default)' }}
          >
            {t('auth.register.loginLink')}
          </Link>
        </p>
      </div>
    </div>
  );
}
