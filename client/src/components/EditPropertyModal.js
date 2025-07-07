import React, { useState } from 'react';
import apiService from '../services/api';

const EditPropertyModal = ({ property, onClose, onPropertyUpdated }) => {
  const [formData, setFormData] = useState({
    name: property.name || '',
    address: property.address || '',
    city: property.city || '',
    state: property.state || '',
    zip_code: property.zip_code || '',
    property_type: property.property_type || 'single_family',

    // Financial Details
    purchase_price: property.purchase_price || '',
    down_payment: property.down_payment || '',
    interest_rate: (property.interest_rate * 100) || '4.5', // Convert back to percentage
    loan_term_years: property.loan_term_years || '30',
    closing_costs: property.closing_costs || '',

    // Property Details
    bedrooms: property.bedrooms || '',
    bathrooms: property.bathrooms || '',
    square_feet: property.square_feet || '',
    year_built: property.year_built || '',

    // Rental Information
    monthly_rent: property.monthly_rent || '',
    security_deposit: property.security_deposit || '',

    // Operating Expenses (Monthly)
    property_taxes: property.property_taxes || '',
    insurance: property.insurance || '',
    hoa_fees: property.hoa_fees || '0',
    property_management: property.property_management || '',
    maintenance_reserve: property.maintenance_reserve || '',
    utilities: property.utilities || '0',
    other_expenses: property.other_expenses || '0',

    // Growth Assumptions (convert back to percentages)
    vacancy_rate: (property.vacancy_rate * 100) || '5',
    annual_rent_increase: (property.annual_rent_increase * 100) || '3',
    annual_expense_increase: (property.annual_expense_increase * 100) || '2.5',
    property_appreciation: (property.property_appreciation * 100) || '4'
  });

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Required fields
    if (!formData.name.trim()) newErrors.name = 'Property name is required';
    if (!formData.address.trim()) newErrors.address = 'Address is required';
    if (!formData.city.trim()) newErrors.city = 'City is required';
    if (!formData.state.trim()) newErrors.state = 'State is required';
    if (!formData.zip_code.trim()) newErrors.zip_code = 'ZIP code is required';

    // Financial validations
    if (!formData.purchase_price || formData.purchase_price <= 0) {
      newErrors.purchase_price = 'Purchase price must be greater than 0';
    }
    if (!formData.down_payment || formData.down_payment < 0) {
      newErrors.down_payment = 'Down payment must be 0 or greater';
    }
    if (!formData.interest_rate || formData.interest_rate <= 0) {
      newErrors.interest_rate = 'Interest rate must be greater than 0';
    }

    // Logical validations
    if (formData.purchase_price && formData.down_payment &&
        parseFloat(formData.down_payment) > parseFloat(formData.purchase_price)) {
      newErrors.down_payment = 'Down payment cannot exceed purchase price';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      // Calculate loan amount
      const purchasePrice = parseFloat(formData.purchase_price);
      const downPayment = parseFloat(formData.down_payment);
      const loanAmount = purchasePrice - downPayment;

      // Prepare property data
      const propertyData = {
        name: formData.name.trim(),
        address: formData.address.trim(),
        city: formData.city.trim(),
        state: formData.state.trim(),
        zip_code: formData.zip_code.trim(),
        property_type: formData.property_type,

        // Financial Details
        purchase_price: purchasePrice,
        down_payment: downPayment,
        loan_amount: loanAmount,
        interest_rate: parseFloat(formData.interest_rate) / 100, // Convert percentage to decimal
        loan_term_years: parseInt(formData.loan_term_years),
        closing_costs: parseFloat(formData.closing_costs) || 0,

        // Property Details
        bedrooms: formData.bedrooms ? parseInt(formData.bedrooms) : null,
        bathrooms: formData.bathrooms ? parseFloat(formData.bathrooms) : null,
        square_feet: formData.square_feet ? parseInt(formData.square_feet) : null,
        year_built: formData.year_built ? parseInt(formData.year_built) : null,

        // Rental Information
        monthly_rent: formData.monthly_rent ? parseFloat(formData.monthly_rent) : null,
        security_deposit: formData.security_deposit ? parseFloat(formData.security_deposit) : null,

        // Operating Expenses (Monthly)
        property_taxes: parseFloat(formData.property_taxes) || 0,
        insurance: parseFloat(formData.insurance) || 0,
        hoa_fees: parseFloat(formData.hoa_fees) || 0,
        property_management: parseFloat(formData.property_management) || 0,
        maintenance_reserve: parseFloat(formData.maintenance_reserve) || 0,
        utilities: parseFloat(formData.utilities) || 0,
        other_expenses: parseFloat(formData.other_expenses) || 0,

        // Growth Assumptions (convert percentages to decimals)
        vacancy_rate: parseFloat(formData.vacancy_rate) / 100,
        annual_rent_increase: parseFloat(formData.annual_rent_increase) / 100,
        annual_expense_increase: parseFloat(formData.annual_expense_increase) / 100,
        property_appreciation: parseFloat(formData.property_appreciation) / 100,

        owner_id: property.owner_id // Keep existing owner
      };

      await apiService.updateProperty(property.id, propertyData);
      onPropertyUpdated();
      onClose();

    } catch (error) {
      console.error('Failed to update property:', error);
      setErrors({ submit: error.message });
    } finally {
      setLoading(false);
    }
  };

  // Use same styles as AddPropertyModal
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
    maxWidth: '800px',
    width: '100%',
    maxHeight: '90vh',
    overflow: 'hidden',
    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
  };

  const headerStyle = {
    padding: '24px',
    borderBottom: '1px solid #e5e7eb',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  };

  const formStyle = {
    padding: '24px',
    maxHeight: 'calc(90vh - 160px)',
    overflowY: 'auto'
  };

  const gridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '16px',
    marginBottom: '24px'
  };

  const inputStyle = {
    width: '100%',
    padding: '8px 12px',
    border: '1px solid #d1d5db',
    borderRadius: '4px',
    fontSize: '14px'
  };

  const errorInputStyle = {
    ...inputStyle,
    borderColor: '#ef4444'
  };

  const labelStyle = {
    display: 'block',
    fontSize: '14px',
    fontWeight: '500',
    color: '#374151',
    marginBottom: '4px'
  };

  const sectionStyle = {
    marginBottom: '32px'
  };

  const sectionHeaderStyle = {
    fontSize: '18px',
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: '16px',
    paddingBottom: '8px',
    borderBottom: '2px solid #e5e7eb'
  };

  return (
    <div style={modalStyle} onClick={onClose}>
      <div style={contentStyle} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={headerStyle}>
          <h2 style={{ fontSize: '24px', fontWeight: '700', color: '#1f2937', margin: 0 }}>
            Edit Property: {property.name}
          </h2>
          <button
            onClick={onClose}
            style={{
              backgroundColor: 'transparent',
              border: 'none',
              fontSize: '24px',
              cursor: 'pointer',
              color: '#6b7280'
            }}
          >
            ×
          </button>
        </div>

        {/* Form - Same structure as AddPropertyModal but condensed */}
        <form onSubmit={handleSubmit} style={formStyle}>
          {/* Basic Information */}
          <div style={sectionStyle}>
            <h3 style={sectionHeaderStyle}>Basic Information</h3>
            <div style={gridStyle}>
              <div>
                <label style={labelStyle}>Property Name *</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  style={errors.name ? errorInputStyle : inputStyle}
                />
                {errors.name && <p style={{ color: '#ef4444', fontSize: '12px', margin: '4px 0 0 0' }}>{errors.name}</p>}
              </div>
              <div>
                <label style={labelStyle}>Property Type</label>
                <select
                  name="property_type"
                  value={formData.property_type}
                  onChange={handleInputChange}
                  style={inputStyle}
                >
                  <option value="single_family">Single Family</option>
                  <option value="multi_family">Multi Family</option>
                  <option value="condo">Condo</option>
                  <option value="townhouse">Townhouse</option>
                  <option value="commercial">Commercial</option>
                  <option value="land">Land</option>
                </select>
              </div>
            </div>

            <div style={gridStyle}>
              <div style={{ gridColumn: 'span 2' }}>
                <label style={labelStyle}>Address *</label>
                <input
                  type="text"
                  name="address"
                  value={formData.address}
                  onChange={handleInputChange}
                  style={errors.address ? errorInputStyle : inputStyle}
                />
                {errors.address && <p style={{ color: '#ef4444', fontSize: '12px', margin: '4px 0 0 0' }}>{errors.address}</p>}
              </div>
            </div>

            <div style={gridStyle}>
              <div>
                <label style={labelStyle}>City *</label>
                <input
                  type="text"
                  name="city"
                  value={formData.city}
                  onChange={handleInputChange}
                  style={errors.city ? errorInputStyle : inputStyle}
                />
                {errors.city && <p style={{ color: '#ef4444', fontSize: '12px', margin: '4px 0 0 0' }}>{errors.city}</p>}
              </div>
              <div>
                <label style={labelStyle}>State *</label>
                <input
                  type="text"
                  name="state"
                  value={formData.state}
                  onChange={handleInputChange}
                  style={errors.state ? errorInputStyle : inputStyle}
                />
                {errors.state && <p style={{ color: '#ef4444', fontSize: '12px', margin: '4px 0 0 0' }}>{errors.state}</p>}
              </div>
              <div>
                <label style={labelStyle}>ZIP Code *</label>
                <input
                  type="text"
                  name="zip_code"
                  value={formData.zip_code}
                  onChange={handleInputChange}
                  style={errors.zip_code ? errorInputStyle : inputStyle}
                />
                {errors.zip_code && <p style={{ color: '#ef4444', fontSize: '12px', margin: '4px 0 0 0' }}>{errors.zip_code}</p>}
              </div>
            </div>
          </div>

          {/* Financial Details */}
          <div style={sectionStyle}>
            <h3 style={sectionHeaderStyle}>Financial Details</h3>
            <div style={gridStyle}>
              <div>
                <label style={labelStyle}>Purchase Price * ($)</label>
                <input
                  type="number"
                  name="purchase_price"
                  value={formData.purchase_price}
                  onChange={handleInputChange}
                  style={errors.purchase_price ? errorInputStyle : inputStyle}
                />
                {errors.purchase_price && <p style={{ color: '#ef4444', fontSize: '12px', margin: '4px 0 0 0' }}>{errors.purchase_price}</p>}
              </div>
              <div>
                <label style={labelStyle}>Down Payment * ($)</label>
                <input
                  type="number"
                  name="down_payment"
                  value={formData.down_payment}
                  onChange={handleInputChange}
                  style={errors.down_payment ? errorInputStyle : inputStyle}
                />
                {errors.down_payment && <p style={{ color: '#ef4444', fontSize: '12px', margin: '4px 0 0 0' }}>{errors.down_payment}</p>}
              </div>
              <div>
                <label style={labelStyle}>Interest Rate * (%)</label>
                <input
                  type="number"
                  step="0.1"
                  name="interest_rate"
                  value={formData.interest_rate}
                  onChange={handleInputChange}
                  style={errors.interest_rate ? errorInputStyle : inputStyle}
                />
                {errors.interest_rate && <p style={{ color: '#ef4444', fontSize: '12px', margin: '4px 0 0 0' }}>{errors.interest_rate}</p>}
              </div>
              <div>
                <label style={labelStyle}>Monthly Rent ($)</label>
                <input
                  type="number"
                  name="monthly_rent"
                  value={formData.monthly_rent}
                  onChange={handleInputChange}
                  style={inputStyle}
                />
              </div>
            </div>
          </div>

          {/* Submit Buttons */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '32px', paddingTop: '16px', borderTop: '1px solid #e5e7eb' }}>
            <button
              type="button"
              onClick={onClose}
              style={{
                padding: '8px 16px',
                border: '1px solid #d1d5db',
                borderRadius: '4px',
                backgroundColor: 'white',
                color: '#374151',
                cursor: 'pointer'
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              style={{
                padding: '8px 24px',
                border: 'none',
                borderRadius: '4px',
                backgroundColor: loading ? '#9ca3af' : '#10b981',
                color: 'white',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontWeight: '500'
              }}
            >
              {loading ? 'Updating Property...' : 'Update Property'}
            </button>
          </div>

          {errors.submit && (
            <p style={{ color: '#ef4444', fontSize: '14px', marginTop: '8px', textAlign: 'center' }}>
              {errors.submit}
            </p>
          )}
        </form>
      </div>
    </div>
  );
};

export default EditPropertyModal;