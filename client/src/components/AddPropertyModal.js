import React, { useState } from 'react';
import apiService from '../services/api';
import './AddPropertyModal.css';

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
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    { title: 'Basic Info', icon: '🏠' },
    { title: 'Financial', icon: '💰' },
    { title: 'Details', icon: '📐' },
    { title: 'Rental & Expenses', icon: '🏘️' },
    { title: 'Growth', icon: '📈' }
  ];

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

  const validateStep = (step) => {
    const newErrors = {};

    switch (step) {
      case 0: // Basic Info
        if (!formData.name.trim()) newErrors.name = 'Property name is required';
        if (!formData.address.trim()) newErrors.address = 'Address is required';
        if (!formData.city.trim()) newErrors.city = 'City is required';
        if (!formData.state.trim()) newErrors.state = 'State is required';
        if (!formData.zip_code.trim()) newErrors.zip_code = 'ZIP code is required';
        break;
      case 1: // Financial
        if (!formData.purchase_price || formData.purchase_price <= 0) {
          newErrors.purchase_price = 'Purchase price must be greater than 0';
        }
        if (!formData.down_payment || formData.down_payment < 0) {
          newErrors.down_payment = 'Down payment must be 0 or greater';
        }
        if (!formData.interest_rate || formData.interest_rate <= 0) {
          newErrors.interest_rate = 'Interest rate must be greater than 0';
        }
        if (formData.purchase_price && formData.down_payment &&
            parseFloat(formData.down_payment) > parseFloat(formData.purchase_price)) {
          newErrors.down_payment = 'Down payment cannot exceed purchase price';
        }
        break;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const nextStep = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, steps.length - 1));
    }
  };

  const prevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 0));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateStep(currentStep)) {
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
        interest_rate: parseFloat(formData.interest_rate) / 100,
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

  const renderStepContent = () => {
    switch (currentStep) {
      case 0: // Basic Information
        return (
          <div className="step-content">
            <div className="form-group-row">
              <div className="form-group">
                <label className="form-label">Property Name *</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  className={`form-input ${errors.name ? 'error' : ''}`}
                  placeholder="e.g., Main Street Rental"
                />
                {errors.name && <span className="error-text">{errors.name}</span>}
              </div>
              <div className="form-group">
                <label className="form-label">Property Type</label>
                <select
                  name="property_type"
                  value={formData.property_type}
                  onChange={handleInputChange}
                  className="form-input"
                >
                  <option value="single_family">🏠 Single Family</option>
                  <option value="multi_family">🏘️ Multi Family</option>
                  <option value="condo">🏢 Condo</option>
                  <option value="townhouse">🏡 Townhouse</option>
                  <option value="commercial">🏬 Commercial</option>
                  <option value="land">🌱 Land</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Address *</label>
              <input
                type="text"
                name="address"
                value={formData.address}
                onChange={handleInputChange}
                className={`form-input ${errors.address ? 'error' : ''}`}
                placeholder="123 Main Street"
              />
              {errors.address && <span className="error-text">{errors.address}</span>}
            </div>

            <div className="form-group-row">
              <div className="form-group">
                <label className="form-label">City *</label>
                <input
                  type="text"
                  name="city"
                  value={formData.city}
                  onChange={handleInputChange}
                  className={`form-input ${errors.city ? 'error' : ''}`}
                  placeholder="New York"
                />
                {errors.city && <span className="error-text">{errors.city}</span>}
              </div>
              <div className="form-group">
                <label className="form-label">State *</label>
                <input
                  type="text"
                  name="state"
                  value={formData.state}
                  onChange={handleInputChange}
                  className={`form-input ${errors.state ? 'error' : ''}`}
                  placeholder="NY"
                />
                {errors.state && <span className="error-text">{errors.state}</span>}
              </div>
              <div className="form-group">
                <label className="form-label">ZIP Code *</label>
                <input
                  type="text"
                  name="zip_code"
                  value={formData.zip_code}
                  onChange={handleInputChange}
                  className={`form-input ${errors.zip_code ? 'error' : ''}`}
                  placeholder="10001"
                />
                {errors.zip_code && <span className="error-text">{errors.zip_code}</span>}
              </div>
            </div>
          </div>
        );

      case 1: // Financial Details
        return (
          <div className="step-content">
            <div className="form-group-row">
              <div className="form-group">
                <label className="form-label">Purchase Price * 💰</label>
                <div className="input-with-icon">
                  <span className="input-icon">$</span>
                  <input
                    type="number"
                    name="purchase_price"
                    value={formData.purchase_price}
                    onChange={handleInputChange}
                    className={`form-input with-icon ${errors.purchase_price ? 'error' : ''}`}
                    placeholder="400,000"
                  />
                </div>
                {errors.purchase_price && <span className="error-text">{errors.purchase_price}</span>}
              </div>
              <div className="form-group">
                <label className="form-label">Down Payment * 💳</label>
                <div className="input-with-icon">
                  <span className="input-icon">$</span>
                  <input
                    type="number"
                    name="down_payment"
                    value={formData.down_payment}
                    onChange={handleInputChange}
                    className={`form-input with-icon ${errors.down_payment ? 'error' : ''}`}
                    placeholder="80,000"
                  />
                </div>
                {errors.down_payment && <span className="error-text">{errors.down_payment}</span>}
              </div>
            </div>

            <div className="form-group-row">
              <div className="form-group">
                <label className="form-label">Interest Rate * 📊</label>
                <div className="input-with-icon">
                  <input
                    type="number"
                    step="0.1"
                    name="interest_rate"
                    value={formData.interest_rate}
                    onChange={handleInputChange}
                    className={`form-input with-icon ${errors.interest_rate ? 'error' : ''}`}
                    placeholder="4.5"
                  />
                  <span className="input-icon-right">%</span>
                </div>
                {errors.interest_rate && <span className="error-text">{errors.interest_rate}</span>}
              </div>
              <div className="form-group">
                <label className="form-label">Loan Term 📅</label>
                <select
                  name="loan_term_years"
                  value={formData.loan_term_years}
                  onChange={handleInputChange}
                  className="form-input"
                >
                  <option value="15">15 years</option>
                  <option value="30">30 years</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Closing Costs 📋</label>
              <div className="input-with-icon">
                <span className="input-icon">$</span>
                <input
                  type="number"
                  name="closing_costs"
                  value={formData.closing_costs}
                  onChange={handleInputChange}
                  className="form-input with-icon"
                  placeholder="8,000"
                />
              </div>
            </div>

            {formData.purchase_price && formData.down_payment && (
              <div className="calculation-preview">
                <h4>💡 Loan Calculation</h4>
                <p>Loan Amount: <strong>${(parseFloat(formData.purchase_price || 0) - parseFloat(formData.down_payment || 0)).toLocaleString()}</strong></p>
                <p>Down Payment: <strong>{((parseFloat(formData.down_payment || 0) / parseFloat(formData.purchase_price || 1)) * 100).toFixed(1)}%</strong></p>
              </div>
            )}
          </div>
        );

      case 2: // Property Details
        return (
          <div className="step-content">
            <div className="form-group-row">
              <div className="form-group">
                <label className="form-label">Bedrooms 🛏️</label>
                <input
                  type="number"
                  name="bedrooms"
                  value={formData.bedrooms}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="3"
                />
              </div>
              <div className="form-group">
                <label className="form-label">Bathrooms 🚿</label>
                <input
                  type="number"
                  step="0.5"
                  name="bathrooms"
                  value={formData.bathrooms}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="2.5"
                />
              </div>
            </div>

            <div className="form-group-row">
              <div className="form-group">
                <label className="form-label">Square Feet 📐</label>
                <div className="input-with-icon">
                  <input
                    type="number"
                    name="square_feet"
                    value={formData.square_feet}
                    onChange={handleInputChange}
                    className="form-input with-icon"
                    placeholder="1,800"
                  />
                  <span className="input-icon-right">ft²</span>
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Year Built 🏗️</label>
                <input
                  type="number"
                  name="year_built"
                  value={formData.year_built}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="2010"
                />
              </div>
            </div>
          </div>
        );

      case 3: // Rental & Expenses
        return (
          <div className="step-content">
            <div className="section-header">
              <h4>💰 Rental Information</h4>
            </div>
            <div className="form-group-row">
              <div className="form-group">
                <label className="form-label">Monthly Rent 🏠</label>
                <div className="input-with-icon">
                  <span className="input-icon">$</span>
                  <input
                    type="number"
                    name="monthly_rent"
                    value={formData.monthly_rent}
                    onChange={handleInputChange}
                    className="form-input with-icon"
                    placeholder="3,200"
                  />
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Security Deposit 🛡️</label>
                <div className="input-with-icon">
                  <span className="input-icon">$</span>
                  <input
                    type="number"
                    name="security_deposit"
                    value={formData.security_deposit}
                    onChange={handleInputChange}
                    className="form-input with-icon"
                    placeholder="3,200"
                  />
                </div>
              </div>
            </div>

            <div className="section-header">
              <h4>📊 Monthly Operating Expenses</h4>
            </div>
            <div className="form-group-row">
              <div className="form-group">
                <label className="form-label">Property Taxes 🏛️</label>
                <div className="input-with-icon">
                  <span className="input-icon">$</span>
                  <input
                    type="number"
                    name="property_taxes"
                    value={formData.property_taxes}
                    onChange={handleInputChange}
                    className="form-input with-icon"
                    placeholder="500"
                  />
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Insurance 🛡️</label>
                <div className="input-with-icon">
                  <span className="input-icon">$</span>
                  <input
                    type="number"
                    name="insurance"
                    value={formData.insurance}
                    onChange={handleInputChange}
                    className="form-input with-icon"
                    placeholder="150"
                  />
                </div>
              </div>
            </div>

            <div className="form-group-row">
              <div className="form-group">
                <label className="form-label">Property Management 👔</label>
                <div className="input-with-icon">
                  <span className="input-icon">$</span>
                  <input
                    type="number"
                    name="property_management"
                    value={formData.property_management}
                    onChange={handleInputChange}
                    className="form-input with-icon"
                    placeholder="256"
                  />
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Maintenance Reserve 🔧</label>
                <div className="input-with-icon">
                  <span className="input-icon">$</span>
                  <input
                    type="number"
                    name="maintenance_reserve"
                    value={formData.maintenance_reserve}
                    onChange={handleInputChange}
                    className="form-input with-icon"
                    placeholder="160"
                  />
                </div>
              </div>
            </div>
          </div>
        );

      case 4: // Growth Assumptions
        return (
          <div className="step-content">
            <div className="form-group-row">
              <div className="form-group">
                <label className="form-label">Vacancy Rate 🏚️</label>
                <div className="input-with-icon">
                  <input
                    type="number"
                    step="0.1"
                    name="vacancy_rate"
                    value={formData.vacancy_rate}
                    onChange={handleInputChange}
                    className="form-input with-icon"
                    placeholder="5"
                  />
                  <span className="input-icon-right">%</span>
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Annual Rent Increase 📈</label>
                <div className="input-with-icon">
                  <input
                    type="number"
                    step="0.1"
                    name="annual_rent_increase"
                    value={formData.annual_rent_increase}
                    onChange={handleInputChange}
                    className="form-input with-icon"
                    placeholder="3"
                  />
                  <span className="input-icon-right">%</span>
                </div>
              </div>
            </div>

            <div className="form-group-row">
              <div className="form-group">
                <label className="form-label">Annual Expense Increase 📊</label>
                <div className="input-with-icon">
                  <input
                    type="number"
                    step="0.1"
                    name="annual_expense_increase"
                    value={formData.annual_expense_increase}
                    onChange={handleInputChange}
                    className="form-input with-icon"
                    placeholder="2.5"
                  />
                  <span className="input-icon-right">%</span>
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Property Appreciation 🏡</label>
                <div className="input-with-icon">
                  <input
                    type="number"
                    step="0.1"
                    name="property_appreciation"
                    value={formData.property_appreciation}
                    onChange={handleInputChange}
                    className="form-input with-icon"
                    placeholder="4"
                  />
                  <span className="input-icon-right">%</span>
                </div>
              </div>
            </div>

            <div className="growth-preview">
              <h4>📋 Summary of Assumptions</h4>
              <div className="preview-grid">
                <div className="preview-item">
                  <span>Vacancy Rate:</span>
                  <strong>{formData.vacancy_rate}%</strong>
                </div>
                <div className="preview-item">
                  <span>Rent Growth:</span>
                  <strong>{formData.annual_rent_increase}% annually</strong>
                </div>
                <div className="preview-item">
                  <span>Expense Growth:</span>
                  <strong>{formData.annual_expense_increase}% annually</strong>
                </div>
                <div className="preview-item">
                  <span>Appreciation:</span>
                  <strong>{formData.property_appreciation}% annually</strong>
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <h2>✨ Add New Property</h2>
          <button onClick={onClose} className="close-button">×</button>
        </div>

        {/* Progress Stepper */}
        <div className="stepper">
          {steps.map((step, index) => (
            <div 
              key={index} 
              className={`step ${index === currentStep ? 'active' : ''} ${index < currentStep ? 'completed' : ''}`}
            >
              <div className="step-icon">
                {index < currentStep ? '✓' : step.icon}
              </div>
              <span className="step-title">{step.title}</span>
            </div>
          ))}
        </div>

        {/* Form Content */}
        <form onSubmit={handleSubmit} className="modal-form">
          <div className="form-content">
            <h3 className="step-header">
              {steps[currentStep].icon} {steps[currentStep].title}
            </h3>
            {renderStepContent()}
          </div>

          {/* Navigation */}
          <div className="modal-footer">
            <div className="button-group">
              <button
                type="button"
                onClick={onClose}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              {currentStep > 0 && (
                <button
                  type="button"
                  onClick={prevStep}
                  className="btn btn-outline"
                >
                  Previous
                </button>
              )}
              {currentStep < steps.length - 1 ? (
                <button
                  type="button"
                  onClick={nextStep}
                  className="btn btn-primary"
                >
                  Next Step
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={loading}
                  className="btn btn-success"
                >
                  {loading ? 'Adding Property...' : '🎉 Add Property'}
                </button>
              )}
            </div>
          </div>

          {errors.submit && (
            <div className="error-banner">
              {errors.submit}
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default AddPropertyModal;