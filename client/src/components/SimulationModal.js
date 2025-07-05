import React, { useState } from 'react';
import apiService from '../services/api';
import SimulationResults from './SimulationResults';

const SimulationModal = ({ property, onClose }) => {
  const [years, setYears] = useState(10);
  const [strategy, setStrategy] = useState('hold');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleRunSimulation = async () => {
    try {
      setLoading(true);
      setError(null);

      const simulationResults = await apiService.runSimulation(property.id, {
        years,
        strategy
      });

      setResults(simulationResults);
    } catch (err) {
      setError(err.message);
      console.error('Simulation failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setResults(null);
    setError(null);
    onClose();
  };

  const backdropStyle = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 50,
    padding: '16px'
  };

  const modalStyle = {
    backgroundColor: 'white',
    borderRadius: '8px',
    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    maxWidth: '1200px',
    width: '100%',
    maxHeight: '90vh',
    overflow: 'hidden'
  };

  const headerStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '24px',
    borderBottom: '1px solid #e5e7eb'
  };

  const gridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '16px'
  };

  const inputStyle = {
    width: '100%',
    padding: '12px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '16px'
  };

  const buttonStyle = {
    padding: '12px 32px',
    border: 'none',
    borderRadius: '6px',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.2s ease'
  };

  return (
    <div style={backdropStyle} onClick={handleClose}>
      <div style={modalStyle} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={headerStyle}>
          <div>
            <h2 style={{ fontSize: '24px', fontWeight: '700', color: '#1f2937', margin: 0 }}>
              ROI Simulation
            </h2>
            <p style={{ color: '#6b7280', margin: '4px 0 0 0' }}>{property.name}</p>
          </div>
          <button
            onClick={handleClose}
            style={{
              backgroundColor: 'transparent',
              border: 'none',
              fontSize: '24px',
              cursor: 'pointer',
              color: '#6b7280',
              padding: '4px'
            }}
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div style={{ padding: '24px', maxHeight: 'calc(90vh - 120px)', overflowY: 'auto' }}>
          {!results ? (
            /* Simulation Setup */
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              {/* Property Summary */}
              <div style={{ backgroundColor: '#f9fafb', padding: '16px', borderRadius: '8px' }}>
                <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '12px' }}>
                  Property Summary
                </h3>
                <div style={gridStyle}>
                  <div>
                    <p style={{ fontSize: '14px', color: '#6b7280' }}>Purchase Price</p>
                    <p style={{ fontWeight: '600' }}>${property.purchase_price.toLocaleString()}</p>
                  </div>
                  <div>
                    <p style={{ fontSize: '14px', color: '#6b7280' }}>Down Payment</p>
                    <p style={{ fontWeight: '600' }}>${property.down_payment.toLocaleString()}</p>
                  </div>
                  <div>
                    <p style={{ fontSize: '14px', color: '#6b7280' }}>Monthly Rent</p>
                    <p style={{ fontWeight: '600' }}>${property.monthly_rent?.toLocaleString() || 'N/A'}</p>
                  </div>
                  <div>
                    <p style={{ fontSize: '14px', color: '#6b7280' }}>Monthly Cash Flow</p>
                    <p style={{
                      fontWeight: '600',
                      color: property.monthly_cash_flow >= 0 ? '#059669' : '#dc2626'
                    }}>
                      ${property.monthly_cash_flow.toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>

              {/* Simulation Parameters */}
              <div>
                <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>
                  Simulation Parameters
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '24px' }}>
                  <div>
                    <label style={{
                      display: 'block',
                      fontSize: '14px',
                      fontWeight: '500',
                      color: '#374151',
                      marginBottom: '8px'
                    }}>
                      Analysis Period
                    </label>
                    <select
                      value={years}
                      onChange={(e) => setYears(parseInt(e.target.value))}
                      style={inputStyle}
                    >
                      <option value={5}>5 Years</option>
                      <option value={10}>10 Years</option>
                      <option value={15}>15 Years</option>
                      <option value={20}>20 Years</option>
                      <option value={30}>30 Years</option>
                    </select>
                  </div>
                  <div>
                    <label style={{
                      display: 'block',
                      fontSize: '14px',
                      fontWeight: '500',
                      color: '#374151',
                      marginBottom: '8px'
                    }}>
                      Investment Strategy
                    </label>
                    <select
                      value={strategy}
                      onChange={(e) => setStrategy(e.target.value)}
                      style={inputStyle}
                    >
                      <option value="hold">Buy & Hold</option>
                      <option value="refinance">Refinance Strategy</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Growth Assumptions */}
              <div style={{ backgroundColor: '#eff6ff', padding: '16px', borderRadius: '8px' }}>
                <h4 style={{ fontWeight: '600', color: '#1e3a8a', marginBottom: '8px' }}>
                  Growth Assumptions
                </h4>
                <div style={gridStyle}>
                  <div>
                    <p style={{ fontSize: '14px', color: '#1e40af' }}>Annual Rent Increase</p>
                    <p style={{ fontWeight: '600', color: '#1e3a8a' }}>
                      {(property.annual_rent_increase * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div>
                    <p style={{ fontSize: '14px', color: '#1e40af' }}>Expense Increase</p>
                    <p style={{ fontWeight: '600', color: '#1e3a8a' }}>
                      {(property.annual_expense_increase * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div>
                    <p style={{ fontSize: '14px', color: '#1e40af' }}>Property Appreciation</p>
                    <p style={{ fontWeight: '600', color: '#1e3a8a' }}>
                      {(property.property_appreciation * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div>
                    <p style={{ fontSize: '14px', color: '#1e40af' }}>Vacancy Rate</p>
                    <p style={{ fontWeight: '600', color: '#1e3a8a' }}>
                      {(property.vacancy_rate * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
              </div>

              {/* Error Display */}
              {error && (
                <div style={{
                  backgroundColor: '#fef2f2',
                  border: '1px solid #fecaca',
                  borderRadius: '6px',
                  padding: '16px'
                }}>
                  <div style={{ color: '#b91c1c' }}>
                    <strong>Simulation Error:</strong> {error}
                  </div>
                </div>
              )}

              {/* Run Simulation Button */}
              <div style={{ display: 'flex', justifyContent: 'center' }}>
                <button
                  onClick={handleRunSimulation}
                  disabled={loading}
                  style={{
                    ...buttonStyle,
                    backgroundColor: loading ? '#9ca3af' : '#3b82f6',
                    color: 'white',
                    opacity: loading ? 0.5 : 1,
                    cursor: loading ? 'not-allowed' : 'pointer'
                  }}
                >
                  {loading ? (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{
                        width: '16px',
                        height: '16px',
                        border: '2px solid #ffffff',
                        borderTop: '2px solid transparent',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite'
                      }}></div>
                      <span>Running Simulation...</span>
                    </div>
                  ) : (
                    `Run ${years}-Year Analysis`
                  )}
                </button>
              </div>
            </div>
          ) : (
            /* Simulation Results */
            <SimulationResults
              results={results}
              property={property}
              years={years}
              onRunAgain={() => setResults(null)}
            />
          )}
        </div>
      </div>

      {/* CSS Animation */}
      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default SimulationModal;