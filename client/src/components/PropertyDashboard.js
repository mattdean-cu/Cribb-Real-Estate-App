import React, { useState, useEffect } from 'react';
import apiService from '../services/api';
import PropertyCard from './PropertyCard';
import SimulationModal from './SimulationModal';

const PropertyDashboard = () => {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedProperty, setSelectedProperty] = useState(null);
  const [showSimulationModal, setShowSimulationModal] = useState(false);

  // Load properties on component mount
  useEffect(() => {
    loadProperties();
  }, []);

  const loadProperties = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getProperties();
      setProperties(data.properties || []);
    } catch (err) {
      setError(err.message);
      console.error('Failed to load properties:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunSimulation = (property) => {
    setSelectedProperty(property);
    setShowSimulationModal(true);
  };

  const handleCloseModal = () => {
    setShowSimulationModal(false);
    setSelectedProperty(null);
  };

  const containerStyle = {
    minHeight: '100vh',
    backgroundColor: '#f3f4f6'
  };

  const headerStyle = {
    backgroundColor: 'white',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
  };

  const headerContentStyle = {
    maxWidth: '1400px',
    margin: '0 auto',
    padding: '0 16px'
  };

  const headerInnerStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '24px 0'
  };

  const mainContentStyle = {
    maxWidth: '1400px',
    margin: '0 auto',
    padding: '32px 16px'
  };

  const statsGridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '24px',
    marginBottom: '32px'
  };

  const propertiesGridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
    gap: '24px'
  };

  const buttonStyle = {
    padding: '8px 16px',
    border: 'none',
    borderRadius: '4px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s ease'
  };

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh'
      }}>
        <div style={{
          width: '128px',
          height: '128px',
          border: '8px solid #e5e7eb',
          borderTop: '8px solid #3b82f6',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }}></div>
        <style jsx>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  if (error) {
    return (
      <div style={containerStyle}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh'
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '32px',
            borderRadius: '8px',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
            maxWidth: '400px',
            width: '100%'
          }}>
            <div style={{ textAlign: 'center', color: '#dc2626' }}>
              <h2 style={{ fontSize: '24px', fontWeight: '700', marginBottom: '16px' }}>
                Connection Error
              </h2>
              <p style={{ marginBottom: '16px' }}>{error}</p>
              <button
                onClick={loadProperties}
                style={{
                  ...buttonStyle,
                  backgroundColor: '#3b82f6',
                  color: 'white'
                }}
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={containerStyle}>
      {/* Header */}
      <div style={headerStyle}>
        <div style={headerContentStyle}>
          <div style={headerInnerStyle}>
            <div>
              <h1 style={{
                fontSize: '30px',
                fontWeight: '700',
                color: '#1f2937',
                margin: 0
              }}>
                Cribb Real Estate Portfolio
              </h1>
              <p style={{
                color: '#6b7280',
                margin: '4px 0 0 0'
              }}>
                Analyze and manage your real estate investments
              </p>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <button
                onClick={loadProperties}
                style={{
                  ...buttonStyle,
                  backgroundColor: '#6b7280',
                  color: 'white'
                }}
              >
                Refresh
              </button>
              <button
                style={{
                  ...buttonStyle,
                  backgroundColor: '#3b82f6',
                  color: 'white'
                }}
              >
                Add Property
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div style={mainContentStyle}>
        {properties.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '48px 0' }}>
            <div style={{ color: '#6b7280' }}>
              <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '8px' }}>
                No Properties Found
              </h3>
              <p>Start by adding your first investment property.</p>
            </div>
          </div>
        ) : (
          <>
            {/* Statistics */}
            <div style={statsGridStyle}>
              <div style={{
                backgroundColor: 'white',
                padding: '24px',
                borderRadius: '8px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
              }}>
                <h3 style={{ fontSize: '14px', fontWeight: '500', color: '#6b7280' }}>
                  Total Properties
                </h3>
                <p style={{ fontSize: '24px', fontWeight: '700', color: '#1f2937' }}>
                  {properties.length}
                </p>
              </div>
              <div style={{
                backgroundColor: 'white',
                padding: '24px',
                borderRadius: '8px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
              }}>
                <h3 style={{ fontSize: '14px', fontWeight: '500', color: '#6b7280' }}>
                  Total Value
                </h3>
                <p style={{ fontSize: '24px', fontWeight: '700', color: '#1f2937' }}>
                  ${properties.reduce((sum, p) => sum + p.purchase_price, 0).toLocaleString()}
                </p>
              </div>
              <div style={{
                backgroundColor: 'white',
                padding: '24px',
                borderRadius: '8px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
              }}>
                <h3 style={{ fontSize: '14px', fontWeight: '500', color: '#6b7280' }}>
                  Monthly Rent
                </h3>
                <p style={{ fontSize: '24px', fontWeight: '700', color: '#1f2937' }}>
                  ${properties.reduce((sum, p) => sum + (p.monthly_rent || 0), 0).toLocaleString()}
                </p>
              </div>
              <div style={{
                backgroundColor: 'white',
                padding: '24px',
                borderRadius: '8px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
              }}>
                <h3 style={{ fontSize: '14px', fontWeight: '500', color: '#6b7280' }}>
                  Monthly Cash Flow
                </h3>
                <p style={{
                  fontSize: '24px',
                  fontWeight: '700',
                  color: '#059669'
                }}>
                  ${properties.reduce((sum, p) => sum + p.monthly_cash_flow, 0).toLocaleString()}
                </p>
              </div>
            </div>

            {/* Properties Grid */}
            <div style={propertiesGridStyle}>
              {properties.map((property) => (
                <PropertyCard
                  key={property.id}
                  property={property}
                  onRunSimulation={() => handleRunSimulation(property)}
                />
              ))}
            </div>
          </>
        )}
      </div>

      {/* Simulation Modal */}
      {showSimulationModal && selectedProperty && (
        <SimulationModal
          property={selectedProperty}
          onClose={handleCloseModal}
        />
      )}
    </div>
  );
};

export default PropertyDashboard;