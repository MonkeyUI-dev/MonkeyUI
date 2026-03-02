import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import api from '../lib/api';

export default function SheBuildsRegister() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { login } = useAuth();

  const [credentials, setCredentials] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  const handleQuickRegister = async () => {
    setError('');
    setLoading(true);
    setCopied(false);
    setCredentials(null);

    try {
      const response = await api.post('/accounts/event-register/');
      const data = response.data;

      // Store tokens so the user can enter console directly
      if (data.tokens) {
        localStorage.setItem('access_token', data.tokens.access);
        localStorage.setItem('refresh_token', data.tokens.refresh);
        localStorage.setItem('user', JSON.stringify(data.user));
      }

      setCredentials(data.credentials);
    } catch (err) {
      setError(err.response?.data?.detail || t('sheBuilds.error'));
    } finally {
      setLoading(false);
    }
  };

  const handleCopyAll = async () => {
    if (!credentials) return;
    const text = [
      `Email: ${credentials.email}`,
      `Password: ${credentials.password}`,
      `API Key: ${credentials.api_key}`,
      '',
      t('sheBuilds.copyTagline'),
    ].join('\n');

    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleEnterConsole = () => {
    // Reload auth context by navigating — tokens are already in localStorage
    window.location.href = '/';
  };

  const handleRegisterAnother = () => {
    setCredentials(null);
    setCopied(false);
    setError('');
    // Clear stored tokens from previous quick-register
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  };

  return (
    <div
      className="flex min-h-screen flex-col items-center justify-center px-6 py-12"
      style={{ backgroundColor: 'var(--bg-canvas)' }}
    >
      {/* Event header */}
      <div className="w-full max-w-md text-center">
        <div
          className="mx-auto mb-4 inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-sm"
          style={{
            backgroundColor: 'rgba(168, 192, 175, 0.1)',
            border: '1px solid rgba(168, 192, 175, 0.2)',
            color: 'var(--accent-mint)',
          }}
        >
          <span>✦</span>
          <span>{t('sheBuilds.date')}</span>
        </div>

        <h1
          className="mt-4 text-5xl font-bold tracking-tight"
          style={{
            color: 'var(--text-primary)',
            fontWeight: 'var(--font-weight-heading)',
          }}
        >
          {t('sheBuilds.title')}
        </h1>

        <p
          className="mt-3 text-lg"
          style={{ color: 'var(--text-secondary)' }}
        >
          {t('sheBuilds.subtitle')}
        </p>

        <p
          className="mt-2 text-sm"
          style={{ color: 'var(--text-tertiary)' }}
        >
          {t('sheBuilds.description')}
        </p>
      </div>

      {/* Main card */}
      <div
        className="mt-10 w-full max-w-md rounded-xl p-8"
        style={{
          backgroundColor: 'var(--bg-surface)',
          border: '1px solid var(--border-subtle)',
        }}
      >
        {error && (
          <div
            className="mb-6 rounded-xl px-4 py-3 text-sm"
            style={{
              backgroundColor: 'rgba(252, 165, 165, 0.15)',
              color: 'var(--color-error)',
              borderRadius: 'var(--radius-md)',
            }}
          >
            {error}
          </div>
        )}

        {!credentials ? (
          /* Register button */
          <div className="text-center">
            <Button
              onClick={handleQuickRegister}
              disabled={loading}
              className="w-full rounded-full px-8 py-4 text-lg font-semibold transition-all"
              style={{
                backgroundColor: 'var(--btn-primary-bg)',
                color: 'var(--btn-primary-fg)',
                borderRadius: 'var(--radius-pill)',
              }}
            >
              {loading ? t('sheBuilds.registering') : t('sheBuilds.quickRegister')}
            </Button>
          </div>
        ) : (
          /* Credentials display */
          <div className="space-y-6">
            <div className="flex items-center gap-2 text-center">
              <div
                className="mx-auto flex items-center gap-2 rounded-full px-3 py-1 text-sm"
                style={{
                  backgroundColor: 'rgba(168, 192, 175, 0.15)',
                  color: 'var(--color-success)',
                }}
              >
                <span>✓</span>
                <span>{t('sheBuilds.success')}</span>
              </div>
            </div>

            <h3
              className="text-lg font-medium"
              style={{ color: 'var(--text-primary)' }}
            >
              {t('sheBuilds.credentials')}
            </h3>

            {/* Credential rows */}
            <div className="space-y-3">
              <CredentialRow label={t('sheBuilds.email')} value={credentials.email} />
              <CredentialRow label={t('sheBuilds.password')} value={credentials.password} />
              <CredentialRow label={t('sheBuilds.apiKey')} value={credentials.api_key} />
            </div>

            {/* Action buttons */}
            <div className="space-y-3 pt-2">
              <Button
                onClick={handleCopyAll}
                className="w-full rounded-full px-6 py-3 text-base font-semibold transition-all"
                style={{
                  backgroundColor: copied ? 'rgba(168, 192, 175, 0.2)' : 'transparent',
                  color: copied ? 'var(--color-success)' : 'var(--text-primary)',
                  border: '1px solid var(--border-default)',
                  borderRadius: 'var(--radius-pill)',
                }}
              >
                {copied ? t('sheBuilds.credentialsCopied') : t('sheBuilds.copyAll')}
              </Button>

              <Button
                onClick={handleEnterConsole}
                className="w-full rounded-full px-6 py-3 text-base font-semibold transition-all"
                style={{
                  backgroundColor: 'var(--btn-primary-bg)',
                  color: 'var(--btn-primary-fg)',
                  borderRadius: 'var(--radius-pill)',
                }}
              >
                {t('sheBuilds.enterConsole')}
              </Button>

              <button
                onClick={handleRegisterAnother}
                className="w-full text-center text-sm transition-colors hover:underline"
                style={{ color: 'var(--text-tertiary)' }}
              >
                {t('sheBuilds.registerAnother')}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function CredentialRow({ label, value }) {
  return (
    <div
      className="rounded-xl px-4 py-3"
      style={{
        backgroundColor: 'var(--bg-canvas)',
        border: '1px solid var(--border-subtle)',
      }}
    >
      <div
        className="mb-1 text-xs font-medium uppercase tracking-wider"
        style={{ color: 'var(--text-tertiary)' }}
      >
        {label}
      </div>
      <div
        className="break-all font-mono text-sm"
        style={{ color: 'var(--text-primary)' }}
      >
        {value}
      </div>
    </div>
  );
}
