"""
Portfolio Simulation Service - Fixed Calculations
Handles portfolio-wide analysis and simulation across multiple properties
"""

import numpy as np
from typing import List, Dict, Any
from dataclasses import dataclass
from decimal import Decimal

# Import your existing simulation components
from .simulation_service import HoldStrategy, SimulationEngine


@dataclass
class PortfolioMetrics:
    total_investment: float
    total_value: float
    total_equity: float
    portfolio_irr: float
    portfolio_npv: float
    annual_cash_flow: float  # Changed: This is now truly ANNUAL
    total_cash_flow: float   # Added: This is total over all years
    diversification_score: float
    risk_adjusted_return: float


class PortfolioSimulationService:
    def __init__(self):
        self.strategy = HoldStrategy()
        self.engine = SimulationEngine(self.strategy)

    def simulate_portfolio(self, properties: List[Dict], simulation_params: Dict) -> Dict[str, Any]:
        """
        Run comprehensive portfolio simulation across all properties
        """
        if not properties:
            return {"error": "No properties provided for simulation"}

        # Individual property simulations
        property_results = {}
        for prop in properties:
            try:
                # Convert to format expected by your simulation engine
                property_data = self._convert_property_for_simulation(prop, simulation_params)

                # Run simulation using your existing engine
                years = simulation_params.get('analysis_period', 10)
                yearly_results, summary = self.engine.run_simulation(property_data, years)

                # Convert results to our expected format
                simulation_result = {
                    'irr': float(summary.internal_rate_of_return) / 100,  # Convert percentage to decimal
                    'npv': float(summary.net_present_value),
                    'annual_cash_flow': float(summary.total_cash_flow) / years,  # Average annual
                    'total_cash_flow': float(summary.total_cash_flow),  # Total over all years
                    'cash_on_cash_return': float(summary.cash_on_cash_return) / 100,
                    'cash_flow_projections': []
                }

                # Create cash flow projections from yearly results
                for result in yearly_results:
                    simulation_result['cash_flow_projections'].append({
                        'year': result.year,
                        'annual_cash_flow': float(result.net_cash_flow),
                        'monthly_cash_flow': float(result.net_cash_flow) / 12
                    })

                property_results[prop['id']] = {
                    'property': prop,
                    'simulation': simulation_result
                }

            except Exception as e:
                print(f"Error simulating property {prop.get('id', 'unknown')}: {str(e)}")
                continue

        if not property_results:
            return {"error": "No valid property simulations completed"}

        # Portfolio-wide calculations
        portfolio_analysis = self._calculate_portfolio_metrics(property_results, simulation_params)

        # Generate charts data
        charts_data = self._generate_portfolio_charts_data(property_results, portfolio_analysis)

        return {
            "portfolio_summary": portfolio_analysis,
            "property_results": property_results,
            "charts_data": charts_data,
            "simulation_params": simulation_params
        }

    def _convert_property_for_simulation(self, prop: Dict, params: Dict) -> Dict:
        """Convert frontend property data to format expected by simulation engine"""

        # Handle different property field names and convert to your simulation format
        purchase_price = float(prop.get('purchase_price', 0))
        current_value = float(prop.get('current_value', purchase_price))  # Use current_value if available

        # Calculate derived values if not provided
        down_payment = float(prop.get('down_payment', current_value * 0.2))
        loan_amount = float(prop.get('loan_amount', current_value - down_payment))
        monthly_rent = float(prop.get('monthly_rent', 0))
        monthly_expenses = float(prop.get('monthly_expenses', 0))

        return {
            'purchase_price': current_value,  # Use current value for simulation
            'down_payment': down_payment,
            'loan_amount': loan_amount,
            'interest_rate': float(prop.get('interest_rate', 0.045)),
            'loan_term_years': prop.get('loan_term_years', 30),
            'monthly_rent': monthly_rent,
            'total_monthly_expenses': monthly_expenses,
            'closing_costs': float(prop.get('closing_costs', 0)),

            # Growth rates from simulation parameters
            'annual_rent_increase': params.get('rent_growth_rate', 0.03),
            'annual_expense_increase': params.get('expense_growth_rate', 0.025),
            'property_appreciation': params.get('appreciation_rate', 0.04),
            'vacancy_rate': params.get('vacancy_rate', 0.05)
        }

    def _calculate_portfolio_metrics(self, property_results: Dict, params: Dict) -> PortfolioMetrics:
        """Calculate portfolio-wide performance metrics - FIXED VERSION"""

        years = params.get('analysis_period', 10)
        discount_rate = params.get('discount_rate', 0.08)

        # Aggregate initial investments and current values
        total_investment = sum(
            result['property']['purchase_price'] + result['property'].get('closing_costs', 0)
            for result in property_results.values()
        )

        total_current_value = sum(
            result['property'].get('current_value', result['property']['purchase_price'])
            for result in property_results.values()
        )

        # FIXED: Calculate portfolio cash flows correctly
        # Annual cash flow is the sum of individual property annual cash flows
        annual_cash_flow = sum(
            result['simulation']['annual_cash_flow']
            for result in property_results.values()
        )

        # Total cash flow over all years
        total_cash_flow = sum(
            result['simulation']['total_cash_flow']
            for result in property_results.values()
        )

        # Calculate portfolio cash flows year by year for IRR calculation
        portfolio_cash_flows = []
        for year in range(1, years + 1):
            year_cash_flow = 0

            for result in property_results.values():
                sim_data = result['simulation']
                if year <= len(sim_data.get('cash_flow_projections', [])):
                    year_data = sim_data['cash_flow_projections'][year - 1]
                    year_cash_flow += year_data.get('annual_cash_flow', 0)

            portfolio_cash_flows.append(year_cash_flow)

        # Calculate portfolio IRR
        cash_flows = [-total_investment] + portfolio_cash_flows
        portfolio_irr = self._calculate_irr(cash_flows)

        # Calculate portfolio NPV
        portfolio_npv = self._calculate_npv(cash_flows, discount_rate)

        # Calculate total equity (simplified)
        total_equity = 0
        for result in property_results.values():
            prop = result['property']
            current_value = prop.get('current_value', prop['purchase_price'])
            down_payment = prop.get('down_payment', current_value * 0.2)
            loan_amount = prop.get('loan_amount', current_value - down_payment)

            # Simplified equity calculation (assumes some principal paydown)
            estimated_remaining_debt = loan_amount * 0.85  # Rough estimate
            equity = max(0, current_value - estimated_remaining_debt)
            total_equity += equity

        # Diversification score (simplified)
        property_count = len(property_results)
        if property_count > 1:
            values = [prop['property'].get('current_value', prop['property']['purchase_price'])
                     for prop in property_results.values()]
            value_variance = np.var(values)
            diversification_score = min(1.0, property_count / 10) * (1 - min(1.0, value_variance / total_current_value))
        else:
            diversification_score = 0.0  # Single property = no diversification

        # Risk-adjusted return (Sharpe ratio approximation)
        avg_return = portfolio_irr if portfolio_irr else 0
        risk_free_rate = 0.03  # Assumption
        return_volatility = 0.15  # Simplified assumption
        risk_adjusted_return = (avg_return - risk_free_rate) / return_volatility if return_volatility > 0 else 0

        return PortfolioMetrics(
            total_investment=total_investment,
            total_value=total_current_value,
            total_equity=total_equity,
            portfolio_irr=portfolio_irr or 0,
            portfolio_npv=portfolio_npv,
            annual_cash_flow=annual_cash_flow,  # FIXED: Now shows correct annual amount
            total_cash_flow=total_cash_flow,    # NEW: Total over all years
            diversification_score=diversification_score,
            risk_adjusted_return=risk_adjusted_return
        )

    def _generate_portfolio_charts_data(self, property_results: Dict, portfolio_metrics: PortfolioMetrics) -> Dict:
        """Generate data structures for portfolio charts"""

        # Property comparison data
        property_comparison = []
        for prop_id, result in property_results.items():
            prop = result['property']
            sim = result['simulation']
            current_value = prop.get('current_value', prop['purchase_price'])
            annual_cash_flow = sim.get('annual_cash_flow', 0)

            # Calculate cap rate the same way as your Property model
            cap_rate = (annual_cash_flow / current_value) * 100 if current_value > 0 else 0

            property_comparison.append({
                'propertyName': prop.get('name', f'Property {prop_id}'),
                'irr': sim.get('irr', 0) * 100,
                'npv': sim.get('npv', 0),
                'currentValue': current_value,
                'cashFlow': annual_cash_flow,
                'capRate': cap_rate  # Added consistent cap rate calculation
            })

        # Portfolio cash flow over time
        years = 10  # Default analysis period
        portfolio_cash_flow = []

        for year in range(1, years + 1):
            year_data = {'year': year, 'total': 0}

            for prop_id, result in property_results.items():
                prop_name = result['property'].get('name', f'Property {prop_id}')
                sim_data = result['simulation']

                if year <= len(sim_data.get('cash_flow_projections', [])):
                    cash_flow = sim_data['cash_flow_projections'][year - 1].get('annual_cash_flow', 0)
                    year_data[prop_name] = cash_flow
                    year_data['total'] += cash_flow
                else:
                    year_data[prop_name] = 0

            portfolio_cash_flow.append(year_data)

        # Diversification data for pie chart
        diversification_data = []
        total_value = portfolio_metrics.total_value

        for prop_id, result in property_results.items():
            prop = result['property']
            prop_value = prop.get('current_value', prop['purchase_price'])
            diversification_data.append({
                'name': prop.get('name', f'Property {prop_id}'),
                'value': prop_value,
                'percentage': (prop_value / total_value) * 100 if total_value > 0 else 0
            })

        # Risk metrics over time
        risk_metrics = []
        for year in range(1, years + 1):
            portfolio_return = portfolio_metrics.portfolio_irr * 100
            sharpe_ratio = portfolio_metrics.risk_adjusted_return

            risk_metrics.append({
                'year': year,
                'portfolioReturn': portfolio_return,
                'sharpeRatio': sharpe_ratio,
                'volatility': 15.0  # Simplified assumption
            })

        # Portfolio summary for dashboard
        portfolio_summary = {
            'totalProperties': len(property_results),
            'totalInvestment': portfolio_metrics.total_investment,
            'totalValue': portfolio_metrics.total_value,
            'totalEquity': portfolio_metrics.total_equity,
            'portfolioIRR': portfolio_metrics.portfolio_irr * 100,
            'portfolioNPV': portfolio_metrics.portfolio_npv,
            'annualCashFlow': portfolio_metrics.annual_cash_flow,  # FIXED: Now correct annual amount
            'totalCashFlow': portfolio_metrics.total_cash_flow,    # NEW: Total over all years
            'diversificationScore': portfolio_metrics.diversification_score * 100,
            'riskAdjustedReturn': portfolio_metrics.risk_adjusted_return
        }

        return {
            'portfolioSummary': portfolio_summary,
            'propertyComparison': property_comparison,
            'portfolioCashFlow': portfolio_cash_flow,
            'diversificationData': diversification_data,
            'riskMetrics': risk_metrics
        }

    def _calculate_irr(self, cash_flows: List[float], max_iterations: int = 1000) -> float:
        """Calculate Internal Rate of Return using Newton-Raphson method"""
        try:
            if not cash_flows or len(cash_flows) < 2:
                return 0.0

            # Initial guess
            rate = 0.1

            for _ in range(max_iterations):
                npv = sum(cf / ((1 + rate) ** i) for i, cf in enumerate(cash_flows))
                npv_derivative = sum(-i * cf / ((1 + rate) ** (i + 1)) for i, cf in enumerate(cash_flows) if i > 0)

                if abs(npv_derivative) < 1e-10:
                    break

                new_rate = rate - npv / npv_derivative

                if abs(new_rate - rate) < 1e-10:
                    return new_rate

                rate = new_rate

                # Prevent negative rates or unrealistic high rates
                if rate < -0.99:
                    rate = -0.99
                elif rate > 10:
                    rate = 10

            return rate

        except (ZeroDivisionError, ValueError, OverflowError):
            return 0.0

    def _calculate_npv(self, cash_flows: List[float], discount_rate: float) -> float:
        """Calculate Net Present Value"""
        try:
            return sum(cf / ((1 + discount_rate) ** i) for i, cf in enumerate(cash_flows))
        except (ZeroDivisionError, ValueError, OverflowError):
            return 0.0