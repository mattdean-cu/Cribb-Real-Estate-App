import React from 'react';

const SimulationResults = ({ results, property, years, onRunAgain }) => {
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

  const getReturnColor = (value) => {
    if (value > 15) return '#059669';
    if (value > 8) return '#3b82f6';
    if (value > 0) return '#d97706';
    return '#dc2626';
  };

  const { summary, yearly_results } = results;

  const containerStyle = {
    padding: '24px',
    maxHeight: 'calc(90vh - 160px)',
    overflowY: 'auto'
  };

  const gridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '16px',
    marginBottom: '24px'
  };

  const cardStyle = {
    padding: '24px',
    borderRadius: '8px',
    border: '1px solid'
  };

  const tableStyle = {
    width: '100%',
    borderCollapse: 'collapse',
    fontSize: '14px'
  };

  const thStyle = {
    textAlign: 'left',
    padding: '8px 12px',
    fontWeight: '500',
    color: '#374151',
    borderBottom: '1px solid #e5e7eb'
  };

  const tdStyle = {
    padding: '8px 12px',
    borderBottom: '1px solid #e5e7eb'
  };

  return (
    <div style={containerStyle}>
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: '24px' }}>
        <h3 style={{ fontSize: '24px', fontWeight: '700', color: '#1f2937', marginBottom: '8px' }}>
          {years}-Year Investment Analysis
        </h3>
        <p style={{ color: '#6b7280' }}>{property.name}</p>
      </div>

      {/* Key Metrics Cards */}
      <div style={gridStyle}>
        <div style={{
          ...cardStyle,
          background: 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)',
          borderColor: '#93c5fd'
        }}>
          <h4 style={{ fontSize: '14px', fontWeight: '500', color: '#1e40af', marginBottom: '4px' }}>
            Total Return
          </h4>
          <p style={{ fontSize: '24px', fontWeight: '700', color: '#1e3a8a' }}>
            {formatCurrency(summary.total_return)}
          </p>
          <p style={{ fontSize: '14px', color: '#3730a3', marginTop: '4px' }}>
            {formatPercentage(summary.total_return_percentage)} total
          </p>
        </div>

        <div style={{
          ...cardStyle,
          background: 'linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%)',
          borderColor: '#86efac'
        }}>
          <h4 style={{ fontSize: '14px', fontWeight: '500', color: '#166534', marginBottom: '4px' }}>
            Annual Return
          </h4>
          <p style={{
            fontSize: '24px',
            fontWeight: '700',
            color: getReturnColor(summary.average_annual_return)
          }}>
            {formatPercentage(summary.average_annual_return)}
          </p>
          <p style={{ fontSize: '14px', color: '#15803d', marginTop: '4px' }}>
            Annualized
          </p>
        </div>

        <div style={{
          ...cardStyle,
          background: 'linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 100%)',
          borderColor: '#c4b5fd'
        }}>
          <h4 style={{ fontSize: '14px', fontWeight: '500', color: '#7c3aed', marginBottom: '4px' }}>
            Cash Flow
          </h4>
          <p style={{ fontSize: '24px', fontWeight: '700', color: '#6d28d9' }}>
            {formatCurrency(summary.total_cash_flow)}
          </p>
          <p style={{ fontSize: '14px', color: '#7c3aed', marginTop: '4px' }}>
            Total over {years} years
          </p>
        </div>

        <div style={{
          ...cardStyle,
          background: 'linear-gradient(135deg, #fed7aa 0%, #fdba74 100%)',
          borderColor: '#fb923c'
        }}>
          <h4 style={{ fontSize: '14px', fontWeight: '500', color: '#ea580c', marginBottom: '4px' }}>
            Final Equity
          </h4>
          <p style={{ fontSize: '24px', fontWeight: '700', color: '#c2410c' }}>
            {formatCurrency(summary.final_equity)}
          </p>
          <p style={{ fontSize: '14px', color: '#ea580c', marginTop: '4px' }}>
            Property value minus debt
          </p>
        </div>
      </div>

      {/* Advanced Metrics */}
      <div style={{
        backgroundColor: '#f9fafb',
        padding: '24px',
        borderRadius: '8px',
        marginBottom: '24px'
      }}>
        <h4 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>
          Advanced Metrics
        </h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '24px' }}>
          <div>
            <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '4px' }}>
              Internal Rate of Return (IRR)
            </p>
            <p style={{
              fontSize: '20px',
              fontWeight: '700',
              color: getReturnColor(summary.internal_rate_of_return)
            }}>
              {formatPercentage(summary.internal_rate_of_return)}
            </p>
          </div>
          <div>
            <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '4px' }}>
              Net Present Value (NPV)
            </p>
            <p style={{
              fontSize: '20px',
              fontWeight: '700',
              color: summary.net_present_value >= 0 ? '#059669' : '#dc2626'
            }}>
              {formatCurrency(summary.net_present_value)}
            </p>
          </div>
          <div>
            <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '4px' }}>
              Cash-on-Cash Return
            </p>
            <p style={{
              fontSize: '20px',
              fontWeight: '700',
              color: getReturnColor(summary.cash_on_cash_return)
            }}>
              {formatPercentage(summary.cash_on_cash_return)}
            </p>
          </div>
        </div>
      </div>

      {/* Year by Year Breakdown */}
      <div style={{
        backgroundColor: 'white',
        border: '1px solid #e5e7eb',
        borderRadius: '8px',
        padding: '24px',
        marginBottom: '24px'
      }}>
        <h4 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>
          Year-by-Year Analysis
        </h4>
        <div style={{ overflowX: 'auto' }}>
          <table style={tableStyle}>
            <thead>
              <tr>
                <th style={thStyle}>Year</th>
                <th style={{ ...thStyle, textAlign: 'right' }}>Cash Flow</th>
                <th style={{ ...thStyle, textAlign: 'right' }}>Property Value</th>
                <th style={{ ...thStyle, textAlign: 'right' }}>Equity</th>
                <th style={{ ...thStyle, textAlign: 'right' }}>Debt Balance</th>
                <th style={{ ...thStyle, textAlign: 'right' }}>CoC Return</th>
              </tr>
            </thead>
            <tbody>
              {yearly_results.map((year, index) => (
                <tr key={index} style={{
                  backgroundColor: index % 2 === 0 ? '#f9fafb' : 'white'
                }}>
                  <td style={{ ...tdStyle, fontWeight: '500' }}>{year.year}</td>
                  <td style={{
                    ...tdStyle,
                    textAlign: 'right',
                    fontWeight: '500',
                    color: year.net_cash_flow >= 0 ? '#059669' : '#dc2626'
                  }}>
                    {formatCurrency(year.net_cash_flow)}
                  </td>
                  <td style={{ ...tdStyle, textAlign: 'right' }}>
                    {formatCurrency(year.property_value)}
                  </td>
                  <td style={{ ...tdStyle, textAlign: 'right', fontWeight: '500', color: '#3b82f6' }}>
                    {formatCurrency(year.equity)}
                  </td>
                  <td style={{ ...tdStyle, textAlign: 'right' }}>
                    {formatCurrency(year.debt_balance)}
                  </td>
                  <td style={{
                    ...tdStyle,
                    textAlign: 'right',
                    color: getReturnColor(year.cash_on_cash_return)
                  }}>
                    {formatPercentage(year.cash_on_cash_return)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Key Insights */}
      <div style={{
        backgroundColor: '#eff6ff',
        border: '1px solid #93c5fd',
        borderRadius: '8px',
        padding: '24px',
        marginBottom: '24px'
      }}>
        <h4 style={{ fontSize: '18px', fontWeight: '600', color: '#1e3a8a', marginBottom: '16px' }}>
          Key Insights
        </h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px', fontSize: '14px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ color: summary.total_return_percentage > 100 ? '#059669' : '#d97706' }}>
                {summary.total_return_percentage > 100 ? '✓' : '⚠'}
              </span>
              <span style={{ color: '#1e40af' }}>
                {summary.total_return_percentage > 100
                  ? 'Strong total return performance'
                  : 'Moderate total return performance'}
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ color: summary.internal_rate_of_return > 12 ? '#059669' : '#d97706' }}>
                {summary.internal_rate_of_return > 12 ? '✓' : '⚠'}
              </span>
              <span style={{ color: '#1e40af' }}>
                {summary.internal_rate_of_return > 12
                  ? 'IRR exceeds market expectations'
                  : 'IRR meets basic expectations'}
              </span>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ color: summary.net_present_value > 0 ? '#059669' : '#dc2626' }}>
                {summary.net_present_value > 0 ? '✓' : '✗'}
              </span>
              <span style={{ color: '#1e40af' }}>
                {summary.net_present_value > 0
                  ? 'Positive NPV - Good investment'
                  : 'Negative NPV - Risky investment'}
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ color: summary.cash_on_cash_return > 8 ? '#059669' : '#d97706' }}>
                {summary.cash_on_cash_return > 8 ? '✓' : '⚠'}
              </span>
              <span style={{ color: '#1e40af' }}>
                {summary.cash_on_cash_return > 8
                  ? 'Strong cash-on-cash returns'
                  : 'Moderate cash-on-cash returns'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: '16px' }}>
        <button
          onClick={onRunAgain}
          style={{
            backgroundColor: '#6b7280',
            color: 'white',
            padding: '8px 24px',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: '500'
          }}
        >
          Run New Analysis
        </button>
        <button style={{
          backgroundColor: '#059669',
          color: 'white',
          padding: '8px 24px',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          fontWeight: '500'
        }}>
          Save Results
        </button>
        <button style={{
          backgroundColor: '#3b82f6',
          color: 'white',
          padding: '8px 24px',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          fontWeight: '500'
        }}>
          Export Report
        </button>
      </div>
    </div>
  );
};

export default SimulationResults;