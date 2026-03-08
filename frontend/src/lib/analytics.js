const GA_MEASUREMENT_ID = import.meta.env.VITE_GA_MEASUREMENT_ID?.trim();

const GA_SCRIPT_ID = 'ga-gtag-script';

export const isGoogleAnalyticsEnabled = Boolean(GA_MEASUREMENT_ID);

function isBrowserEnvironment() {
  return typeof window !== 'undefined' && typeof document !== 'undefined';
}

export function initializeGoogleAnalytics() {
  if (!isGoogleAnalyticsEnabled || !isBrowserEnvironment()) {
    return false;
  }

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function gtag(...args) {
    window.dataLayer.push(args);
  };

  if (!document.getElementById(GA_SCRIPT_ID)) {
    const script = document.createElement('script');
    script.id = GA_SCRIPT_ID;
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`;
    document.head.appendChild(script);
  }

  window.gtag('js', new Date());
  window.gtag('config', GA_MEASUREMENT_ID, { send_page_view: false });

  return true;
}

export function trackPageView(pathname, search = '') {
  if (!isGoogleAnalyticsEnabled || !isBrowserEnvironment() || typeof window.gtag !== 'function') {
    return;
  }

  const pagePath = `${pathname}${search}`;

  window.gtag('config', GA_MEASUREMENT_ID, {
    page_path: pagePath,
    page_title: document.title,
    page_location: window.location.href,
  });
}