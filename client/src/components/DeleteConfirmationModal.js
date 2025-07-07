import React, { useState } from 'react';
import apiService from '../services/api';

const DeleteConfirmationModal = ({ property, onClose, onPropertyDeleted }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleDelete = async () => {
    setLoading(true);
    setError(null);

    try {
      await apiService.deleteProperty(property.id);
      onPropertyDeleted();
      onClose();
    } catch (err) {
      setError(err.message);
      console.error('Failed to delete property:', err);
    } finally {
      setLoading(false);
    }
  };

  const modalStyle = {
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

  const contentStyle = {
    backgroundColor: 'white',
    borderRadius: '8px',
    maxWidth: '400px',
    width: '100%',
    padding: '24px',
    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
  };

  const iconStyle = {
    width: '48px',
    height: '48px',
    backgroundColor: '#fef2f2',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    margin: '0 auto 16px auto'
  };

  const buttonStyle = {
    padding: '8px 16px',
    border: 'none',
    borderRadius: '4px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s ease'
  };

  return (
    <div style={modalStyle} onClick={onClose}>
      <div style={contentStyle} onClick={(e) => e.stopPropagation()}>
        {/* Warning Icon */}
        <div style={iconStyle}>
          <span style={{ fontSize: '24px', color: '#dc2626' }}>⚠️</span>
        </div>

        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '16px' }}>
          <h2 style={{
            fontSize: '18px',
            fontWeight: '600',
            color: '#1f2937',
            margin: '0 0 8px 0'
          }}>
            Delete Property
          </h2>
          <p style={{ color: '#6b7280', margin: 0 }}>
            Are you sure you want to delete this property? This action cannot be undone.
          </p>
        </div>

        {/* Property Info */}
        <div style={{
          backgroundColor: '#f9fafb',
          border: '1px solid #e5e7eb',
          borderRadius: '6px',
          padding: '12px',
          marginBottom: '20px'
        }}>
          <h3 style={{
            fontSize: '16px',
            fontWeight: '600',
            color: '#1f2937',
            margin: '0 0 4px 0'
          }}>
            {property.name}
          </h3>
          <p style={{
            fontSize: '14px',
            color: '#6b7280',
            margin: '0 0 8px 0'
          }}>
            {property.full_address}
          </p>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
            <span style={{ color: '#6b7280' }}>Purchase Price:</span>
            <span style={{ fontWeight: '500', color: '#1f2937' }}>
              ${property.purchase_price.toLocaleString()}
            </span>
          </div>
        </div>

        {/* Warning Message */}
        <div style={{
          backgroundColor: '#fef2f2',
          border: '1px solid #fecaca',
          borderRadius: '6px',
          padding: '12px',
          marginBottom: '20px'
        }}>
          <p style={{
            fontSize: '14px',
            color: '#b91c1c',
            margin: 0,
            fontWeight: '500'
          }}>
            ⚠️ This will also delete all associated simulation data and cannot be undone.
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div style={{
            backgroundColor: '#fef2f2',
            border: '1px solid #fecaca',
            borderRadius: '6px',
            padding: '12px',
            marginBottom: '20px'
          }}>
            <p style={{ fontSize: '14px', color: '#b91c1c', margin: 0 }}>
              Error: {error}
            </p>
          </div>
        )}

        {/* Buttons */}
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={onClose}
            disabled={loading}
            style={{
              ...buttonStyle,
              flex: 1,
              backgroundColor: 'white',
              border: '1px solid #d1d5db',
              color: '#374151'
            }}
          >
            Cancel
          </button>
          <button
            onClick={handleDelete}
            disabled={loading}
            style={{
              ...buttonStyle,
              flex: 1,
              backgroundColor: loading ? '#fca5a5' : '#dc2626',
              color: 'white',
              opacity: loading ? 0.7 : 1,
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                <div style={{
                  width: '16px',
                  height: '16px',
                  border: '2px solid #ffffff',
                  borderTop: '2px solid transparent',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }}></div>
                <span>Deleting...</span>
              </div>
            ) : (
              'Delete Property'
            )}
          </button>
        </div>

        {/* CSS Animation */}
        <style jsx>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    </div>
  );
};

export default DeleteConfirmationModal;