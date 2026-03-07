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
    window.location.href = '/';
  };

  const handleRegisterAnother = () => {
    setCredentials(null);
    setCopied(false);
    setError('');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  };

  return (
    <div
      className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden px-6 py-12"
      style={{
        fontFamily: 'Inter, SF Pro Display, system-ui, sans-serif',
        color: '#FFFFFF'
      }}
    >
      {/* Background Spectral Mesh Animation */}
      <div 
        className="absolute inset-0 z-0 pointer-events-none"
        style={{
          background: 'linear-gradient(-45deg, #6B8AF1, #F45099, #FF7C4D)',
          backgroundSize: '200% 200%',
          animation: 'sheb-drift 15s ease infinite',
        }}
      />
      <style>
        {`
          @keyframes sheb-drift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
          }
        `}
      </style>

      {/* Main Content Area (No Containers) */}
      <div className="relative z-10 w-full max-w-lg text-center flex flex-col items-center">
        {/* Event Context Eyebrow */}
        <div
          className="mb-8 text-sm uppercase tracking-[0.2em] font-medium"
          style={{ opacity: 0.9 }}
        >
          {t('sheBuilds.date')}
        </div>

        {/* Hero Typography */}
        <h1
          className="text-6xl sm:text-7xl font-bold tracking-tight leading-none mb-4"
          style={{ letterSpacing: '-0.02em', textShadow: 'none' }}
        >
          {t('sheBuilds.title')}
        </h1>

        <p
          className="text-xl sm:text-2xl font-medium mb-2"
          style={{ opacity: 0.9 }}
        >
          {t('sheBuilds.subtitle')}
        </p>

        <p
          className="text-base sm:text-lg max-w-md mx-auto mb-16"
          style={{ opacity: 0.8, fontWeight: 400 }}
        >
          {t('sheBuilds.description')}
        </p>

        {/* Dynamic Content area */}
        <div className="w-full flex flex-col items-center">
          {error && (
            <div
              className="mb-8 rounded-full px-6 py-3 text-sm"
              style={{
                backgroundColor: 'rgba(255, 255, 255, 0.2)',
                color: '#FFFFFF',
              }}
            >
              {error}
            </div>
          )}

          {!credentials ? (
            /* Register button */
            <div className="w-full max-w-sm">
              <Button
                onClick={handleQuickRegister}
                disabled={loading}
                className="w-full rounded-full px-8 py-5 text-xl font-bold transition-transform hover:scale-105"
                style={{
                  backgroundColor: '#FFFFFF',
                  color: '#F45099', /* Vibrant Magenta for pure contrast */
                  border: 'none',
                }}
              >
                {loading ? t('sheBuilds.registering') : t('sheBuilds.quickRegister')}
              </Button>
            </div>
          ) : (
            /* Credentials display (No Container cards) */
            <div className="w-full max-w-sm space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
              <div
                className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-widest px-4 py-1.5 rounded-full"
                style={{ backgroundColor: 'rgba(255, 255, 255, 0.2)' }}
              >
                <span>✓</span>
                <span>{t('sheBuilds.success')}</span>
              </div>

              <h3 className="text-2xl font-bold tracking-tight">
                {t('sheBuilds.credentials')}
              </h3>

              {/* Credential rows */}
              <div className="space-y-4 text-left">
                <CredentialRow label={t('sheBuilds.email')} value={credentials.email} />
                <CredentialRow label={t('sheBuilds.password')} value={credentials.password} />
                <CredentialRow label={t('sheBuilds.apiKey')} value={credentials.api_key} />
              </div>

              {/* Action buttons */}
              <div className="space-y-4 pt-4 flex flex-col items-center">
                <Button
                  onClick={handleEnterConsole}
                  className="w-full rounded-full px-6 py-4 text-lg font-bold transition-transform hover:scale-105"
                  style={{
                    backgroundColor: '#FFFFFF',
                    color: '#6B8AF1', /* Electric Blue */
                    border: 'none',
                  }}
                >
                  {t('sheBuilds.enterConsole')}
                </Button>

                <button
                  onClick={handleCopyAll}
                  className="text-sm font-semibold tracking-wide uppercase transition-opacity hover:opacity-100 mt-2"
                  style={{ opacity: copied ? 1 : 0.8, textDecoration: 'underline', textUnderlineOffset: '4px' }}
                >
                  {copied ? t('sheBuilds.credentialsCopied') : t('sheBuilds.copyAll')}
                </button>

                <button
                  onClick={handleRegisterAnother}
                  className="text-xs font-medium tracking-wider uppercase transition-opacity hover:opacity-100"
                  style={{ opacity: 0.6, textDecoration: 'underline', textUnderlineOffset: '4px' }}
                >
                  {t('sheBuilds.registerAnother')}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function CredentialRow({ label, value }) {
  return (
    <div className="py-2 border-b border-white/20">
      <div
        className="mb-1 text-xs font-bold uppercase tracking-widest"
        style={{ opacity: 0.7 }}
      >
        {label}
      </div>
      <div className="break-all font-mono text-lg font-medium text-white">
        {value}
      </div>
    </div>
  );
}

