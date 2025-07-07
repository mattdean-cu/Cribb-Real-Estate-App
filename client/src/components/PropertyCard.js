import React from 'react';

const PropertyCard = ({ property, onRunSimulation, onEditProperty, onDeleteProperty }) => {
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercentage = (value) => {
    return `${value.toFixed(2)}%`;
  };

  const getCashFlowColor = (cashFlow) => {
    if (cashFlow > 0) return '#059669';
    if (cashFlow < 0) return '#dc2626';
    return '#6b7280';
  };

  const getPropertyTypeLabel = (type) => {
    const typeMap = {
      'single_family': 'Single Family',
      'multi_family': 'Multi Family',
      'condo': 'Condo',
      'townhouse': 'Townhouse',
      'commercial': 'Commercial',
      'land': 'Land'
    };
    return typeMap[type] || type;
  };

  const cardStyle = {
    backgroundColor: 'white',
    borderRadius: '8px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    transition: 'all 0.2s ease',
    overflow: 'hidden'
  };

  const headerStyle = {
    padding: '24px',
    borderBottom: '1px solid #e5e7eb'
  };

  const contentStyle = {
    padding: '24px'
  };

  const gridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '16px',
    marginBottom: '16px'
  };

  const buttonStyle = {
    width: '100%',
    padding: '8px 16px',
    border: 'none',
    borderRadius: '4px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s ease'
  };

  const primaryButtonStyle = {
    ...buttonStyle,
    backgroundColor: '#3b82f6',
    color: 'white'
  };

  const secondaryButtonStyle = {
    ...buttonStyle,
    backgroundColor: '#e5e7eb',
    color: '#374151'
  };

  return (
    <div style={cardStyle}>
      {/* Header */}
      <div style={headerStyle}>
        <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1f2937', marginBottom: '4px' }}>
          {property.name}
        </h3>
        <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>
          {property.full_address}
        </p>
        <span style={{
          display: 'inline-block',
          padding: '2px 8px',
          fontSize: '12px',
          fontWeight: '500',
          backgroundColor: '#dbeafe',
          color: '#1d4ed8',
          borderRadius: '4px'
        }}>
          {getPropertyTypeLabel(property.property_type)}
        </span>
      </div>

      {/* Content */}
      <div style={contentStyle}>
        {/* Main Financial Info */}
        <div style={gridStyle}>
          <div>
            <p style={{ fontSize: '14px', color: '#6b7280' }}>Purchase Price</p>
            <p style={{ fontSize: '18px', fontWeight: '600', color: '#1f2937' }}>
              {formatCurrency(property.purchase_price)}
            </p>
          </div>
          <div>
            <p style={{ fontSize: '14px', color: '#6b7280' }}>Monthly Rent</p>
            <p style={{ fontSize: '18px', fontWeight: '600', color: '#1f2937' }}>
              {property.monthly_rent ? formatCurrency(property.monthly_rent) : 'N/A'}
            </p>
          </div>
        </div>

        <div style={gridStyle}>
          <div>
            <p style={{ fontSize: '14px', color: '#6b7280' }}>Down Payment</p>
            <p style={{ fontSize: '16px', fontWeight: '500', color: '#374151' }}>
              {formatCurrency(property.down_payment)}
            </p>
          </div>
          <div>
            <p style={{ fontSize: '14px', color: '#6b7280' }}>Monthly Expenses</p>
            <p style={{ fontSize: '16px', fontWeight: '500', color: '#374151' }}>
              {formatCurrency(property.total_monthly_expenses)}
            </p>
          </div>
        </div>

        {/* Property Stats */}
        {(property.bedrooms || property.bathrooms || property.square_feet) && (
          <div style={{ display: 'flex', gap: '16px', marginBottom: '16px', fontSize: '14px', color: '#6b7280' }}>
            {property.bedrooms && (
              <span>{property.bedrooms} bed{property.bedrooms !== 1 ? 's' : ''}</span>
            )}
            {property.bathrooms && (
              <span>{property.bathrooms} bath{property.bathrooms !== 1 ? 's' : ''}</span>
            )}
            {property.square_feet && (
              <span>{property.square_feet.toLocaleString()} sq ft</span>
            )}
          </div>
        )}

        {/* Financial Metrics */}
        <div style={{ borderTop: '1px solid #e5e7eb', paddingTop: '16px' }}>
          <div style={gridStyle}>
            <div>
              <p style={{ fontSize: '14px', color: '#6b7280' }}>Monthly Cash Flow</p>
              <p style={{
                fontSize: '18px',
                fontWeight: '700',
                color: getCashFlowColor(property.monthly_cash_flow)
              }}>
                {formatCurrency(property.monthly_cash_flow)}
              </p>
            </div>
            <div>
              <p style={{ fontSize: '14px', color: '#6b7280' }}>Cash-on-Cash Return</p>
              <p style={{
                fontSize: '18px',
                fontWeight: '700',
                color: getCashFlowColor(property.cash_on_cash_return)
              }}>
                {formatPercentage(property.cash_on_cash_return)}
              </p>
            </div>
          </div>

          <div style={{ ...gridStyle, marginBottom: '24px' }}>
            <div>
              <p style={{ fontSize: '14px', color: '#6b7280' }}>Cap Rate</p>
              <p style={{ fontSize: '16px', fontWeight: '500', color: '#374151' }}>
                {formatPercentage(property.cap_rate)}
              </p>
            </div>
            <div>
              <p style={{ fontSize: '14px', color: '#6b7280' }}>1% Rule</p>
              <p style={{
                fontSize: '16px',
                fontWeight: '500',
                color: property.one_percent_rule ? '#059669' : '#dc2626'
              }}>
                {property.one_percent_rule ? '✓ Passes' : '✗ Fails'}
              </p>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => onRunSimulation(property)}
            style={primaryButtonStyle}
            onMouseOver={(e) => e.target.style.backgroundColor = '#2563eb'}
            onMouseOut={(e) => e.target.style.backgroundColor = '#3b82f6'}
          >
            Run Simulation
          </button>
          <button
            onClick={() => onEditProperty(property)}
            style={{
              ...buttonStyle,
              backgroundColor: '#10b981',
              color: 'white',
              flex: '0 0 auto',
              padding: '8px 12px'
            }}
            onMouseOver={(e) => e.target.style.backgroundColor = '#059669'}
            onMouseOut={(e) => e.target.style.backgroundColor = '#10b981'}
          >
            Edit
          </button>
          <button
            onClick={() => onDeleteProperty(property)}
            style={{
              ...buttonStyle,
              backgroundColor: '#dc2626',
              color: 'white',
              flex: '0 0 auto',
              padding: '8px 12px'
            }}
            onMouseOver={(e) => e.target.style.backgroundColor = '#b91c1c'}
            onMouseOut={(e) => e.target.style.backgroundColor = '#dc2626'}
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
};

export default PropertyCard;