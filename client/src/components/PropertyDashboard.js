import React, { useState, useEffect } from 'react';
import apiService from '../services/api';
import PropertyCard from './PropertyCard';
import SimulationModal from './SimulationModal';
import AddPropertyModal from './AddPropertyModal';
import EditPropertyModal from './EditPropertyModal';
import DeleteConfirmationModal from './DeleteConfirmationModal';

const PropertyDashboard = ({ user, onLogout }) => {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedProperty, setSelectedProperty] = useState(null);
  const [showSimulationModal, setShowSimulationModal] = useState(false);
  const [showAddPropertyModal, setShowAddPropertyModal] = useState(false);
  const [showEditPropertyModal, setShowEditPropertyModal] = useState(false);
  const [showDeleteConfirmationModal, setShowDeleteConfirmationModal] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

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

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await onLogout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setIsLoggingOut(false);
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

  const handleAddProperty = () => {
    setShowAddPropertyModal(true);
  };

  const handleCloseAddModal = () => {
    setShowAddPropertyModal(false);
  };

  const handlePropertyAdded = () => {
    // Refresh the properties list
    loadProperties();
  };

  const handleEditProperty = (property) => {
    setSelectedProperty(property);
    setShowEditPropertyModal(true);
  };

  const handleCloseEditModal = () => {
    setShowEditPropertyModal(false);
    setSelectedProperty(null);
  };

  const handlePropertyUpdated = () => {
    // Refresh the properties list
    loadProperties();
  };

  const handleDeleteProperty = (property) => {
    setSelectedProperty(property);
    setShowDeleteConfirmationModal(true);
  };

  const handleCloseDeleteModal = () => {
    setShowDeleteConfirmationModal(false);
    setSelectedProperty(null);
  };

  const handlePropertyDeleted = () => {
    // Refresh the properties list
    loadProperties();
  };

  // Get user initials
  const getUserInitials = () => {
    if (user?.initials) return user.initials;
    if (user?.first_name && user?.last_name) {
      return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
    }
    if (user?.first_name) return user.first_name[0].toUpperCase();
    return 'U';
  };

  // Get user display name
  const getUserDisplayName = () => {
    if (user?.full_name) return user.full_name;
    if (user?.first_name && user?.last_name) {
      return `${user.first_name} ${user.last_name}`;
    }
    if (user?.first_name) return user.first_name;
    return 'User';
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

  const userMenuStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '16px'
  };

  const userInfoStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '12px'
  };

  const userInitialsStyle = {
    width: '40px',
    height: '40px',
    borderRadius: '50%',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: '600',
    fontSize: '16px'
  };

  const userNameStyle = {
    fontWeight: '500',
    color: '#2d3748',
    fontSize: '16px'
  };

  const actionButtonsStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '12px'
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
    borderRadius: '6px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    fontSize: '14px'
  };

  const logoutButtonStyle = {
    ...buttonStyle,
    background: '#e2e8f0',
    border: '1px solid #cbd5e0',
    color: '#4a5568'
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

            {/* User Menu with Logout */}
            <div style={userMenuStyle}>
              <div style={userInfoStyle}>
                <div style={userInitialsStyle}>
                  {getUserInitials()}
                </div>
                <span style={userNameStyle}>
                  {getUserDisplayName()}
                </span>
              </div>

              <div style={actionButtonsStyle}>
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
                  onClick={handleAddProperty}
                >
                  Add Property
                </button>
                <button
                  onClick={handleLogout}
                  disabled={isLoggingOut}
                  style={{
                    ...logoutButtonStyle,
                    opacity: isLoggingOut ? 0.6 : 1,
                    cursor: isLoggingOut ? 'not-allowed' : 'pointer'
                  }}
                  onMouseEnter={(e) => {
                    if (!isLoggingOut) {
                      e.target.style.background = '#cbd5e0';
                      e.target.style.color = '#2d3748';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isLoggingOut) {
                      e.target.style.background = '#e2e8f0';
                      e.target.style.color = '#4a5568';
                    }
                  }}
                >
                  {isLoggingOut ? 'Signing out...' : 'Sign Out'}
                </button>
              </div>
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
                  onEditProperty={() => handleEditProperty(property)}
                  onDeleteProperty={() => handleDeleteProperty(property)}
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

      {/* Add Property Modal */}
      {showAddPropertyModal && (
        <AddPropertyModal
          onClose={handleCloseAddModal}
          onPropertyAdded={handlePropertyAdded}
        />
      )}

      {/* Edit Property Modal */}
      {showEditPropertyModal && selectedProperty && (
        <EditPropertyModal
          property={selectedProperty}
          onClose={handleCloseEditModal}
          onPropertyUpdated={handlePropertyUpdated}
        />
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirmationModal && selectedProperty && (
        <DeleteConfirmationModal
          property={selectedProperty}
          onClose={handleCloseDeleteModal}
          onPropertyDeleted={handlePropertyDeleted}
        />
      )}
    </div>
  );
};

export default PropertyDashboard;