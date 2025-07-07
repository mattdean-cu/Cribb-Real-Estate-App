import React, { useState, useEffect } from 'react';
import PropertyDashboard from './components/PropertyDashboard';
import LoginForm from './components/LoginForm';
import RegistrationForm from './components/RegistrationForm';
import apiService from './services/api';
import './App.css';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [connectionError, setConnectionError] = useState(null);
  const [user, setUser] = useState(null);
  const [showRegistration, setShowRegistration] = useState(false);

  // Check backend connection and authentication on app load
  useEffect(() => {
    checkBackendConnection();
  }, []);

  const checkBackendConnection = async () => {
    try {
      setIsLoading(true);
      setConnectionError(null);

      // First check if backend is healthy
      const health = await apiService.checkHealth();

      if (health.status === 'healthy') {
        setIsConnected(true);

        // Then check if user is already authenticated
        await checkAuthentication();
      } else {
        setConnectionError('Backend is not healthy');
      }
    } catch (error) {
      setConnectionError(`Cannot connect to backend: ${error.message}`);
      setIsConnected(false);
    } finally {
      setIsLoading(false);
    }
  };

  const checkAuthentication = async () => {
    try {
      // Try to get properties to check if authenticated
      await apiService.getProperties();
      setIsAuthenticated(true);

      // Optionally get current user info
      // const currentUser = await apiService.getCurrentUser();
      // setUser(currentUser);
    } catch (error) {
      // Not authenticated or session expired
      setIsAuthenticated(false);
      setUser(null);
    }
  };

  const handleLogin = async (email, password) => {
    try {
      const response = await apiService.login(email, password);
      setIsAuthenticated(true);
      setUser(response.user);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const handleRegister = async (userData) => {
    try {
      const response = await apiService.register(userData);
      // Auto-login after successful registration
      setIsAuthenticated(true);
      setUser(response.user);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const handleLogout = async () => {
    try {
      await apiService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setIsAuthenticated(false);
      setUser(null);
    }
  };

  // Loading screen
  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <h2>Connecting to Cribb Backend...</h2>
          <p>Please ensure your Flask server is running on port 5000</p>
        </div>
      </div>
    );
  }

  // Connection error screen
  if (!isConnected) {
    return (
      <div className="error-container">
        <div className="error-content">
          <div className="error-icon">⚠️</div>
          <h2>Backend Connection Failed</h2>
          <p>{connectionError}</p>

          <div className="error-instructions">
            <p><strong>To fix this:</strong></p>
            <ol>
              <li>Open terminal in your server directory</li>
              <li>Run: <code>python run_simple.py</code></li>
              <li>Ensure server is running on http://localhost:5000</li>
              <li>Click "Retry Connection" below</li>
            </ol>
          </div>

          <button onClick={checkBackendConnection} className="retry-button">
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  // Main application - show login, registration, or dashboard based on auth status
  return (
    <div className="App">
      {isAuthenticated ? (
        <PropertyDashboard
          user={user}
          onLogout={handleLogout}
        />
      ) : showRegistration ? (
        <RegistrationForm
          onRegister={handleRegister}
          onSwitchToLogin={() => setShowRegistration(false)}
        />
      ) : (
        <LoginForm
          onLogin={handleLogin}
          onSwitchToRegister={() => setShowRegistration(true)}
        />
      )}
    </div>
  );
}

export default App;