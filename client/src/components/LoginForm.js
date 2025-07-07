import React, { useState } from 'react';
import './AuthForm.css';

const LoginForm = ({ onLogin, onSwitchToRegister }) => {
  const [email, setEmail] = useState('demo@cribb.com'); // Pre-filled for demo
  const [password, setPassword] = useState('Demo123!'); // Pre-filled for demo
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const result = await onLogin(email, password);

      if (!result.success) {
        setError(result.error || 'Login failed');
      }
    } catch (error) {
      setError('An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>🏠 Cribb Real Estate</h1>
          <h2>ROI Analysis Platform</h2>
          <p>Sign in to analyze your property investments</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
              disabled={isLoading}
            />
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <button
            type="submit"
            className="auth-button"
            disabled={isLoading}
          >
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="demo-info">
          <p><strong>Demo Credentials:</strong></p>
          <p>Email: demo@cribb.com</p>
          <p>Password: Demo123!</p>
        </div>

        <div className="auth-switch">
          <p>Don't have an account?</p>
          <button
            type="button"
            onClick={onSwitchToRegister}
            className="switch-button"
            disabled={isLoading}
          >
            Create Account
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;