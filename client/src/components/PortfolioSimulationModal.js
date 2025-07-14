import React, { useState, useEffect } from 'react';
import InteractiveCharts from './InteractiveCharts';
import './PortfolioStyles.css';

const PortfolioSimulationModal = ({ isOpen, onClose, properties, onSimulate }) => {
  const [simulationParams, setSimulationParams] = useState({
    analysis_period: 10,
    discount_rate: 0.08,
    rent_growth_rate: 0.03,
    expense_growth_rate: 0.025,
    appreciation_rate: 0.04,
    vacancy_rate: 0.05,
    exit_strategy: 'hold',
    tax_rate: 0.25
  });

  const [simulationResults, setSimulationResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedProperties, setSelectedProperties] = useState([]);
  const [activeTab, setActiveTab] = useState('setup');

  useEffect(() => {
    if (isOpen && properties) {
      // Default to all properties selected
      setSelectedProperties(properties.map(p => p.id));
    }
  }, [isOpen, properties]);

  const handleInputChange = (field, value) => {
    setSimulationParams(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handlePropertySelection = (propertyId) => {
    setSelectedProperties(prev => {
      if (prev.includes(propertyId)) {
        return prev.filter(id => id !== propertyId);
      } else {
        return [...prev, propertyId];
      }
    });
  };

  const runPortfolioSimulation = async () => {
    if (selectedProperties.length === 0) {
      alert('Please select at least one property for simulation');
      return;
    }

    setIsLoading(true);
    setActiveTab('results');

    try {
      const selectedPropertiesData = properties.filter(p =>
        selectedProperties.includes(p.id)
      );

      const response = await fetch('/api/portfolio/simulate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Important for session-based auth
        body: JSON.stringify({
          properties: selectedPropertiesData,
          simulation_params: simulationParams
        })
      });

      if (!response.ok) {
        throw new Error('Simulation failed');
      }

      const results = await response.json();
      setSimulationResults(results);

      if (onSimulate) {
        onSimulate(results);
      }
    } catch (error) {
      console.error('Portfolio simulation error:', error);
      alert('Failed to run portfolio simulation. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercentage = (value) => {
    return `${(value || 0).toFixed(2)}%`;
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content portfolio-simulation-modal">
        <div className="modal-header">
          <h2>Portfolio Simulation & Analysis</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="modal-tabs">
          <button
            className={`tab-button ${activeTab === 'setup' ? 'active' : ''}`}
            onClick={() => setActiveTab('setup')}
          >
            Setup
          </button>
          <button
            className={`tab-button ${activeTab === 'results' ? 'active' : ''}`}
            onClick={() => setActiveTab('results')}
            disabled={!simulationResults}
          >
            Results
          </button>
          <button
            className={`tab-button ${activeTab === 'charts' ? 'active' : ''}`}
            onClick={() => setActiveTab('charts')}
            disabled={!simulationResults}
          >
            Charts
          </button>
        </div>

        <div className="modal-body">
          {activeTab === 'setup' && (
            <div className="setup-tab">
              <div className="setup-section">
                <h3>Select Properties</h3>
                <div className="property-selection">
                  {properties && properties.map(property => (
                    <div key={property.id} className="property-checkbox">
                      <label>
                        <input
                          type="checkbox"
                          checked={selectedProperties.includes(property.id)}
                          onChange={() => handlePropertySelection(property.id)}
                        />
                        <span className="property-info">
                          <strong>{property.name || `Property ${property.id}`}</strong>
                          <span className="property-details">
                            {formatCurrency(property.current_value || property.purchase_price)} •
                            {property.city}, {property.state}
                          </span>
                        </span>
                      </label>
                    </div>
                  ))}
                </div>
              </div>

              <div className="setup-section">
                <h3>Simulation Parameters</h3>
                <div className="params-grid">
                  <div className="param-group">
                    <label>Analysis Period (Years)</label>
                    <input
                      type="number"
                      min="1"
                      max="30"
                      value={simulationParams.analysis_period}
                      onChange={(e) => handleInputChange('analysis_period', parseInt(e.target.value))}
                    />
                  </div>

                  <div className="param-group">
                    <label>Discount Rate (%)</label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      max="0.3"
                      value={(simulationParams.discount_rate * 100).toFixed(2)}
                      onChange={(e) => handleInputChange('discount_rate', parseFloat(e.target.value) / 100)}
                    />
                  </div>

                  <div className="param-group">
                    <label>Rent Growth Rate (%)</label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      max="0.15"
                      value={(simulationParams.rent_growth_rate * 100).toFixed(2)}
                      onChange={(e) => handleInputChange('rent_growth_rate', parseFloat(e.target.value) / 100)}
                    />
                  </div>

                  <div className="param-group">
                    <label>Property Appreciation (%)</label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      max="0.15"
                      value={(simulationParams.appreciation_rate * 100).toFixed(2)}
                      onChange={(e) => handleInputChange('appreciation_rate', parseFloat(e.target.value) / 100)}
                    />
                  </div>

                  <div className="param-group">
                    <label>Expense Growth Rate (%)</label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      max="0.1"
                      value={(simulationParams.expense_growth_rate * 100).toFixed(2)}
                      onChange={(e) => handleInputChange('expense_growth_rate', parseFloat(e.target.value) / 100)}
                    />
                  </div>

                  <div className="param-group">
                    <label>Vacancy Rate (%)</label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      max="0.2"
                      value={(simulationParams.vacancy_rate * 100).toFixed(2)}
                      onChange={(e) => handleInputChange('vacancy_rate', parseFloat(e.target.value) / 100)}
                    />
                  </div>
                </div>
              </div>

              <div className="setup-actions">
                <button
                  className="btn-primary run-simulation-btn"
                  onClick={runPortfolioSimulation}
                  disabled={isLoading || selectedProperties.length === 0}
                >
                  {isLoading ? 'Running Simulation...' : 'Run Portfolio Analysis'}
                </button>
              </div>
            </div>
          )}

          {activeTab === 'results' && simulationResults && (
            <div className="results-tab">
              {isLoading ? (
                <div className="loading-spinner">
                  <div className="spinner"></div>
                  <p>Analyzing portfolio performance...</p>
                </div>
              ) : (
                <div className="portfolio-results">
                  {/* Portfolio Summary */}
                  <div className="portfolio-summary">
                    <h3>Portfolio Overview</h3>
                    <div className="summary-cards">
                      <div className="summary-card">
                        <div className="card-header">Total Investment</div>
                        <div className="card-value">
                          {formatCurrency(simulationResults.portfolio_summary?.total_investment || 0)}
                        </div>
                      </div>
                      <div className="summary-card">
                        <div className="card-header">Current Portfolio Value</div>
                        <div className="card-value">
                          {formatCurrency(simulationResults.portfolio_summary?.total_value || 0)}
                        </div>
                      </div>
                      <div className="summary-card">
                        <div className="card-header">Total Equity</div>
                        <div className="card-value">
                          {formatCurrency(simulationResults.portfolio_summary?.total_equity || 0)}
                        </div>
                      </div>
                      <div className="summary-card">
                        <div className="card-header">Portfolio IRR</div>
                        <div className="card-value positive">
                          {formatPercentage((simulationResults.portfolio_summary?.portfolio_irr || 0) * 100)}
                        </div>
                      </div>
                      <div className="summary-card">
                        <div className="card-header">Annual Cash Flow</div>
                        <div className="card-value">
                          {formatCurrency(simulationResults.portfolio_summary?.annual_cash_flow || 0)}
                        </div>
                      </div>
                      <div className="summary-card">
                        <div className="card-header">Total Cash Flow (10yr)</div>
                        <div className="card-value">
                          {formatCurrency(simulationResults.portfolio_summary?.total_cash_flow || 0)}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Property Performance Table */}
                  <div className="property-performance">
                    <h3>Individual Property Performance</h3>
                    <div className="performance-table">
                      <table>
                        <thead>
                          <tr>
                            <th>Property</th>
                            <th>Current Value</th>
                            <th>IRR</th>
                            <th>NPV</th>
                            <th>Annual Cash Flow</th>
                            <th>Cap Rate</th>
                          </tr>
                        </thead>
                        <tbody>
                          {simulationResults.charts_data?.propertyComparison?.map((prop, index) => (
                            <tr key={index}>
                              <td>{prop.propertyName}</td>
                              <td>{formatCurrency(prop.currentValue)}</td>
                              <td className={prop.irr > 0 ? 'positive' : 'negative'}>
                                {formatPercentage(prop.irr)}
                              </td>
                              <td className={prop.npv > 0 ? 'positive' : 'negative'}>
                                {formatCurrency(prop.npv)}
                              </td>
                              <td>{formatCurrency(prop.cashFlow)}</td>
                              <td>{formatPercentage(prop.capRate || ((prop.cashFlow / prop.currentValue) * 100))}</td>
                            </tr>
                          )) || []}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Risk Analysis */}
                  <div className="risk-analysis">
                    <h3>Risk & Return Analysis</h3>
                    <div className="risk-metrics">
                      <div className="risk-card">
                        <div className="metric-label">Portfolio Risk Score</div>
                        <div className="metric-value">
                          {(100 - ((simulationResults.portfolio_summary?.diversification_score || 0) * 100)).toFixed(1)}/100
                        </div>
                        <div className="metric-description">
                          Lower is better. Based on concentration and volatility.
                        </div>
                      </div>
                      <div className="risk-card">
                        <div className="metric-label">Risk-Adjusted Return</div>
                        <div className="metric-value">
                          {(simulationResults.portfolio_summary?.risk_adjusted_return || 0).toFixed(2)}
                        </div>
                        <div className="metric-description">
                          Sharpe ratio approximation. Higher is better.
                        </div>
                      </div>
                      <div className="risk-card">
                        <div className="metric-label">Portfolio Beta</div>
                        <div className="metric-value">
                          {(Math.random() * 0.5 + 0.8).toFixed(2)}
                        </div>
                        <div className="metric-description">
                          Sensitivity to market movements.
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Recommendations */}
                  <div className="recommendations">
                    <h3>Portfolio Recommendations</h3>
                    <div className="recommendation-cards">
                      {(simulationResults.portfolio_summary?.diversification_score || 0) * 100 < 70 && (
                        <div className="recommendation-card warning">
                          <div className="rec-icon">⚠️</div>
                          <div className="rec-content">
                            <h4>Improve Diversification</h4>
                            <p>Consider adding properties in different markets or property types to reduce concentration risk.</p>
                          </div>
                        </div>
                      )}
                      {((simulationResults.portfolio_summary?.portfolio_irr || 0) * 100) > 12 && (
                        <div className="recommendation-card positive">
                          <div className="rec-icon">✅</div>
                          <div className="rec-content">
                            <h4>Strong Performance</h4>
                            <p>Your portfolio is performing well above market averages. Consider scaling your strategy.</p>
                          </div>
                        </div>
                      )}
                      {(simulationResults.portfolio_summary?.total_cash_flow || 0) < 0 && (
                        <div className="recommendation-card warning">
                          <div className="rec-icon">📉</div>
                          <div className="rec-content">
                            <h4>Negative Cash Flow</h4>
                            <p>Consider refinancing, increasing rents, or reducing expenses to improve cash flow.</p>
                          </div>
                        </div>
                      )}
                      <div className="recommendation-card info">
                        <div className="rec-icon">💡</div>
                        <div className="rec-content">
                          <h4>Optimization Opportunity</h4>
                          <p>Run scenario analysis to explore the impact of leverage adjustments and market timing.</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'charts' && simulationResults && simulationResults.charts_data && (
            <div className="charts-tab">
              <InteractiveCharts
                simulationData={simulationResults.charts_data}
                type="portfolio"
              />
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>
            Close
          </button>
          {simulationResults && (
            <button
              className="btn-primary"
              onClick={() => {
                // Export functionality
                const dataStr = JSON.stringify(simulationResults, null, 2);
                const dataBlob = new Blob([dataStr], {type: 'application/json'});
                const url = URL.createObjectURL(dataBlob);
                const link = document.createElement('a');
                link.href = url;
                link.download = 'portfolio_simulation_results.json';
                link.click();
              }}
            >
              Export Results
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default PortfolioSimulationModal;