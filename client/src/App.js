import React, { useState, useEffect } from 'react';
import PropertyDashboard from './components/PropertyDashboard';
import apiService from './services/api';
import './App.css';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [connectionError, setConnectionError] = useState(null);

  // Check backend connection on app load
  useEffect(() => {
    checkBackendConnection();
  }, []);

  const checkBackendConnection = async () => {
    try {
      setIsLoading(true);
      setConnectionError(null);

      const health = await apiService.checkHealth();

      if (health.status === 'healthy') {
        setIsConnected(true);
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

  // Main application
  return (
    <div className="App">
      <PropertyDashboard />
    </div>
  );
}

export default App;