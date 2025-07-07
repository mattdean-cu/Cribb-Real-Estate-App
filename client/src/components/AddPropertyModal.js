import React, { useState } from 'react';
import apiService from '../services/api';

const AddPropertyModal = ({ onClose, onPropertyAdded }) => {
  const [formData, setFormData] = useState({
    name: '',
    address: '',
    city: '',
    state: '',
    zip_code: '',
    property_type: 'single_family',

    // Financial Details
    purchase_price: '',
    down_payment: '',
    interest_rate: '4.5',
    loan_term_years: '30',
    closing_costs: '',

    // Property Details
    bedrooms: '',
    bathrooms: '',
    square_feet: '',
    year_built: '',

    // Rental Information
    monthly_rent: '',
    security_deposit: '',

    // Operating Expenses (Monthly)
    property_taxes: '',
    insurance: '',
    hoa_fees: '0',
    property_management: '',
    maintenance_reserve: '',
    utilities: '0',
    other_expenses: '0',

    // Growth Assumptions
    vacancy_rate: '5',
    annual_rent_increase: '3',
    annual_expense_increase: '2.5',
    property_appreciation: '4'
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
      // Get the demo user ID (we'll use the existing demo user)
      const usersData = await apiService.getUsers();
      const demoUser = usersData.users[0]; // Use first user (demo user)

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

        owner_id: demoUser.id
      };

      await apiService.createProperty(propertyData);
      onPropertyAdded();
      onClose();

    } catch (error) {
      console.error('Failed to create property:', error);
      setErrors({ submit: error.message });
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
            Add New Property
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

        {/* Form */}
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
                  placeholder="e.g., Main Street Rental"
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
                  placeholder="123 Main Street"
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
                  placeholder="New York"
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
                  placeholder="NY"
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
                  placeholder="10001"
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
                  placeholder="400000"
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
                  placeholder="80000"
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
                  placeholder="4.5"
                />
                {errors.interest_rate && <p style={{ color: '#ef4444', fontSize: '12px', margin: '4px 0 0 0' }}>{errors.interest_rate}</p>}
              </div>
              <div>
                <label style={labelStyle}>Loan Term (years)</label>
                <select
                  name="loan_term_years"
                  value={formData.loan_term_years}
                  onChange={handleInputChange}
                  style={inputStyle}
                >
                  <option value="15">15 years</option>
                  <option value="30">30 years</option>
                </select>
              </div>
            </div>

            <div style={gridStyle}>
              <div>
                <label style={labelStyle}>Closing Costs ($)</label>
                <input
                  type="number"
                  name="closing_costs"
                  value={formData.closing_costs}
                  onChange={handleInputChange}
                  style={inputStyle}
                  placeholder="8000"
                />
              </div>
            </div>
          </div>

          {/* Property Details */}
          <div style={sectionStyle}>
            <h3 style={sectionHeaderStyle}>Property Details</h3>
            <div style={gridStyle}>
              <div>
                <label style={labelStyle}>Bedrooms</label>
                <input
                  type="number"
                  name="bedrooms"
                  value={formData.bedrooms}
                  onChange={handleInputChange}
                  style={inputStyle}
                  placeholder="3"
                />
              </div>
              <div>
                <label style={labelStyle}>Bathrooms</label>
                <input
                  type="number"
                  step="0.5"
                  name="bathrooms"
                  value={formData.bathrooms}
                  onChange={handleInputChange}
                  style={inputStyle}
                  placeholder="2.5"
                />
              </div>
              <div>
                <label style={labelStyle}>Square Feet</label>
                <input
                  type="number"
                  name="square_feet"
                  value={formData.square_feet}
                  onChange={handleInputChange}
                  style={inputStyle}
                  placeholder="1800"
                />
              </div>
              <div>
                <label style={labelStyle}>Year Built</label>
                <input
                  type="number"
                  name="year_built"
                  value={formData.year_built}
                  onChange={handleInputChange}
                  style={inputStyle}
                  placeholder="2010"
                />
              </div>
            </div>
          </div>

          {/* Rental Information */}
          <div style={sectionStyle}>
            <h3 style={sectionHeaderStyle}>Rental Information</h3>
            <div style={gridStyle}>
              <div>
                <label style={labelStyle}>Monthly Rent ($)</label>
                <input
                  type="number"
                  name="monthly_rent"
                  value={formData.monthly_rent}
                  onChange={handleInputChange}
                  style={inputStyle}
                  placeholder="3200"
                />
              </div>
              <div>
                <label style={labelStyle}>Security Deposit ($)</label>
                <input
                  type="number"
                  name="security_deposit"
                  value={formData.security_deposit}
                  onChange={handleInputChange}
                  style={inputStyle}
                  placeholder="3200"
                />
              </div>
            </div>
          </div>

          {/* Operating Expenses */}
          <div style={sectionStyle}>
            <h3 style={sectionHeaderStyle}>Monthly Operating Expenses</h3>
            <div style={gridStyle}>
              <div>
                <label style={labelStyle}>Property Taxes ($)</label>
                <input
                  type="number"
                  name="property_taxes"
                  value={formData.property_taxes}
                  onChange={handleInputChange}
                  style={inputStyle}
                  placeholder="500"
                />
              </div>
              <div>
                <label style={labelStyle}>Insurance ($)</label>
                <input
                  type="number"
                  name="insurance"
                  value={formData.insurance}
                  onChange={handleInputChange}
                  style={inputStyle}
                  placeholder="150"
                />
              </div>
              <div>
                <label style={labelStyle}>HOA Fees ($)</label>
                <input
                  type="number"
                  name="hoa_fees"
                  value={formData.hoa_fees}
                  onChange={handleInputChange}
                  style={inputStyle}
                  placeholder="0"
                />
              </div>
              <div>
                <label style={labelStyle}>Property Management ($)</label>
                <input
                  type="number"
                  name="property_management"
                  value={formData.property_management}
                  onChange={handleInputChange}
                  style={inputStyle}
                  placeholder="256"
                />
              </div>
              <div>
                <label style={labelStyle}>Maintenance Reserve ($)</label>
                <input
                  type="number"
                  name="maintenance_reserve"
                  value={formData.maintenance_reserve}
                  onChange={handleInputChange}
                  style={inputStyle}
                  placeholder="160"
                />
              </div>
              <div>
                <label style={labelStyle}>Utilities ($)</label>
                <input
                  type="number"
                  name="utilities"
                  value={formData.utilities}
                  onChange={handleInputChange}
                  style={inputStyle}
                  placeholder="0"
                />
              </div>
              <div>
                <label style={labelStyle}>Other Expenses ($)</label>
                <input
                  type="number"
                  name="other_expenses"
                  value={formData.other_expenses}
                  onChange={handleInputChange}
                  style={inputStyle}
                  placeholder="50"
                />
              </div>
            </div>
          </div>

          {/* Growth Assumptions */}
          <div style={sectionStyle}>
            <h3 style={sectionHeaderStyle}>Growth Assumptions</h3>
            <div style={gridStyle}>
              <div>
                <label style={labelStyle}>Vacancy Rate (%)</label>
                <input
                  type="number"
                  step="0.1"
                  name="vacancy_rate"
                  value={formData.vacancy_rate}
                  onChange={handleInputChange}
                  style={inputStyle}
                  placeholder="5"
                />
              </div>
              <div>
                <label style={labelStyle}>Annual Rent Increase (%)</label>
                <input
                  type="number"
                  step="0.1"
                  name="annual_rent_increase"
                  value={formData.annual_rent_increase}
                  onChange={handleInputChange}
                  style={inputStyle}
                  placeholder="3"
                />
              </div>
              <div>
                <label style={labelStyle}>Annual Expense Increase (%)</label>
                <input
                  type="number"
                  step="0.1"
                  name="annual_expense_increase"
                  value={formData.annual_expense_increase}
                  onChange={handleInputChange}
                  style={inputStyle}
                  placeholder="2.5"
                />
              </div>
              <div>
                <label style={labelStyle}>Property Appreciation (%)</label>
                <input
                  type="number"
                  step="0.1"
                  name="property_appreciation"
                  value={formData.property_appreciation}
                  onChange={handleInputChange}
                  style={inputStyle}
                  placeholder="4"
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
                backgroundColor: loading ? '#9ca3af' : '#3b82f6',
                color: 'white',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontWeight: '500'
              }}
            >
              {loading ? 'Adding Property...' : 'Add Property'}
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

export default AddPropertyModal;