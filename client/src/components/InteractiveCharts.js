import React from 'react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

const InteractiveCharts = ({ simulationData, type = 'single' }) => {
  if (!simulationData) return null;

  // Format currency for tooltips
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  // Format percentage for tooltips
  const formatPercentage = (value) => `${(value * 100).toFixed(1)}%`;

  // Custom tooltip component
  const CustomTooltip = ({ active, payload, label, formatter = formatCurrency }) => {
    if (active && payload && payload.length) {
      return (
        <div className="chart-tooltip">
          <p className="tooltip-label">{`Year ${label}`}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }}>
              {`${entry.dataKey}: ${formatter(entry.value)}`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  // Single Property Charts
  if (type === 'single') {
    const { cashFlowProjections, propertyValue, totalReturn } = simulationData;

    return (
      <div className="charts-container">
        {/* Cash Flow Over Time */}
        <div className="chart-section">
          <h3>Cash Flow Projections</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={cashFlowProjections}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Area
                type="monotone"
                dataKey="monthlyCashFlow"
                stackId="1"
                stroke="#4CAF50"
                fill="#4CAF50"
                fillOpacity={0.3}
                name="Monthly Cash Flow"
              />
              <Area
                type="monotone"
                dataKey="annualCashFlow"
                stackId="2"
                stroke="#2196F3"
                fill="#2196F3"
                fillOpacity={0.3}
                name="Annual Cash Flow"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Property Value Growth */}
        <div className="chart-section">
          <h3>Property Value Growth</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={propertyValue}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line
                type="monotone"
                dataKey="currentValue"
                stroke="#FF9800"
                strokeWidth={3}
                dot={{ r: 4 }}
                name="Property Value"
              />
              <Line
                type="monotone"
                dataKey="equity"
                stroke="#9C27B0"
                strokeWidth={2}
                strokeDasharray="5 5"
                name="Owner Equity"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* ROI Breakdown */}
        <div className="chart-section">
          <h3>Return Components</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={totalReturn}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis tickFormatter={(value) => `${value.toFixed(1)}%`} />
              <Tooltip content={<CustomTooltip formatter={formatPercentage} />} />
              <Legend />
              <Bar dataKey="cashOnCashReturn" fill="#4CAF50" name="Cash-on-Cash Return" />
              <Bar dataKey="appreciationReturn" fill="#2196F3" name="Appreciation Return" />
              <Bar dataKey="totalReturn" fill="#FF9800" name="Total Return" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  }

  // Portfolio Charts
  if (type === 'portfolio') {
    const {
      portfolioSummary,
      propertyComparison,
      portfolioCashFlow,
      diversificationData,
      riskMetrics
    } = simulationData;

    const pieColors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336', '#00BCD4'];

    return (
      <div className="charts-container portfolio-charts">
        {/* Portfolio Overview */}
        <div className="chart-row">
          <div className="chart-section half-width">
            <h3>Portfolio Value Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={diversificationData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {diversificationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={pieColors[index % pieColors.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => formatCurrency(value)} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-section half-width">
            <h3>Property Performance Comparison</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={propertyComparison} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" tickFormatter={(value) => `${value.toFixed(1)}%`} />
                <YAxis dataKey="propertyName" type="category" width={100} />
                <Tooltip formatter={(value) => `${value.toFixed(2)}%`} />
                <Bar dataKey="irr" fill="#4CAF50" name="IRR" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Portfolio Cash Flow */}
        <div className="chart-section">
          <h3>Portfolio Cash Flow Projections</h3>
          <ResponsiveContainer width="100%" height={350}>
            <AreaChart data={portfolioCashFlow}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`} />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              {portfolioCashFlow[0] && Object.keys(portfolioCashFlow[0])
                .filter(key => key !== 'year' && key !== 'total')
                .map((propertyKey, index) => (
                <Area
                  key={propertyKey}
                  type="monotone"
                  dataKey={propertyKey}
                  stackId="1"
                  stroke={pieColors[index % pieColors.length]}
                  fill={pieColors[index % pieColors.length]}
                  fillOpacity={0.6}
                  name={propertyKey}
                />
              ))}
              <Line
                type="monotone"
                dataKey="total"
                stroke="#000"
                strokeWidth={3}
                name="Total Portfolio"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Risk Metrics */}
        <div className="chart-section">
          <h3>Risk & Return Analysis</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={riskMetrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis yAxisId="left" tickFormatter={(value) => `${value.toFixed(1)}%`} />
              <YAxis yAxisId="right" orientation="right" tickFormatter={(value) => `${value.toFixed(2)}`} />
              <Tooltip />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="portfolioReturn"
                stroke="#4CAF50"
                strokeWidth={2}
                name="Portfolio Return %"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="sharpeRatio"
                stroke="#FF9800"
                strokeWidth={2}
                strokeDasharray="5 5"
                name="Sharpe Ratio"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  }

  return null;
};

export default InteractiveCharts;