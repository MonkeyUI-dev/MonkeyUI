import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import Login from './pages/Login';
import Register from './pages/Register';
import DesignWorkshop from './pages/DesignWorkshop';
import VibeStudio from './pages/VibeStudio';
import { initializeGoogleAnalytics, trackPageView } from './lib/analytics';

function GoogleAnalyticsTracker() {
  const location = useLocation();

  useEffect(() => {
    if (!initializeGoogleAnalytics()) {
      return;
    }

    trackPageView(location.pathname, location.search);
  }, [location.pathname, location.search]);

  return null;
}

function App() {
  return (
    <Router>
      <GoogleAnalyticsTracker />
      <AuthProvider>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Protected routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DesignWorkshop />
              </ProtectedRoute>
            }
          />
          <Route
            path="/vibe-studio/new"
            element={
              <ProtectedRoute>
                <VibeStudio isNew={true} />
              </ProtectedRoute>
            }
          />
          <Route
            path="/vibe-studio/:id"
            element={
              <ProtectedRoute>
                <VibeStudio isNew={false} />
              </ProtectedRoute>
            }
          />
          
          {/* Catch all - redirect to home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;

