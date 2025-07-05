from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import numpy as np
from datetime import datetime, timezone
import json


@dataclass
class YearlyResults:
    """Data class for yearly simulation results"""
    year: int
    beginning_balance: Decimal
    monthly_rent: Decimal
    total_rental_income: Decimal
    total_expenses: Decimal
    mortgage_payment: Decimal
    principal_payment: Decimal
    interest_payment: Decimal
    net_cash_flow: Decimal
    cumulative_cash_flow: Decimal
    property_value: Decimal
    equity: Decimal
    debt_balance: Decimal
    cash_on_cash_return: Decimal

    def to_dict(self):
        """Convert to dictionary with float values for JSON serialization"""
        return {k: float(v) if isinstance(v, Decimal) else v for k, v in asdict(self).items()}


@dataclass
class SimulationSummary:
    """Summary results of the simulation"""
    total_investment: Decimal
    total_cash_flow: Decimal
    final_property_value: Decimal
    final_equity: Decimal
    total_return: Decimal
    total_return_percentage: Decimal
    average_annual_return: Decimal
    internal_rate_of_return: Decimal
    net_present_value: Decimal
    cash_on_cash_return: Decimal

    def to_dict(self):
        """Convert to dictionary with float values for JSON serialization"""
        return {k: float(v) if isinstance(v, Decimal) else v for k, v in asdict(self).items()}


class SimulationStrategy(ABC):
    """Abstract base class for simulation strategies"""

    @abstractmethod
    def calculate_year(self, year: int, property_data: Dict,
                       previous_results: Optional[YearlyResults] = None) -> YearlyResults:
        """Calculate results for a specific year"""
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the name of this strategy"""
        pass


class HoldStrategy(SimulationStrategy):
    """Strategy for buy-and-hold real estate investment"""

    def get_strategy_name(self) -> str:
        return "Buy and Hold"

    def calculate_year(self, year: int, property_data: Dict,
                       previous_results: Optional[YearlyResults] = None) -> YearlyResults:
        """Calculate yearly results for hold strategy"""

        # Extract property data with safe conversions
        purchase_price = Decimal(str(property_data.get('purchase_price', 0)))
        down_payment = Decimal(str(property_data.get('down_payment', 0)))
        loan_amount = Decimal(str(property_data.get('loan_amount', 0)))
        interest_rate = Decimal(str(property_data.get('interest_rate', 0)))
        loan_term_years = property_data.get('loan_term_years', 30)

        # Base financial data
        base_rent = Decimal(str(property_data.get('monthly_rent', 0)))
        base_expenses = Decimal(str(property_data.get('total_monthly_expenses', 0)))

        # Growth rates
        rent_growth = Decimal(str(property_data.get('annual_rent_increase', 0.03)))
        expense_growth = Decimal(str(property_data.get('annual_expense_increase', 0.02)))
        appreciation_rate = Decimal(str(property_data.get('property_appreciation', 0.03)))
        vacancy_rate = Decimal(str(property_data.get('vacancy_rate', 0.05)))

        # Calculate year-specific values
        years_elapsed = year - 1  # Year 1 = 0 years of growth

        # Monthly rent with growth
        monthly_rent = base_rent * (1 + rent_growth) ** years_elapsed

        # Monthly expenses with growth
        monthly_expenses = base_expenses * (1 + expense_growth) ** years_elapsed

        # Property value with appreciation
        property_value = purchase_price * (1 + appreciation_rate) ** years_elapsed

        # Calculate mortgage details
        monthly_payment = self._calculate_mortgage_payment(loan_amount, interest_rate, loan_term_years)

        # Calculate remaining balance
        if previous_results:
            beginning_balance = previous_results.debt_balance
        else:
            beginning_balance = loan_amount

        # Annual debt service calculations
        annual_principal = Decimal('0')
        annual_interest = Decimal('0')
        ending_balance = beginning_balance

        for month in range(12):
            if ending_balance <= 0:
                break

            monthly_interest = ending_balance * (interest_rate / 12)
            monthly_principal = monthly_payment - monthly_interest

            # Don't pay more principal than remaining balance
            if monthly_principal > ending_balance:
                monthly_principal = ending_balance

            annual_interest += monthly_interest
            annual_principal += monthly_principal
            ending_balance -= monthly_principal

        # Annual calculations
        effective_rent = monthly_rent * (1 - vacancy_rate)
        total_rental_income = effective_rent * 12
        total_expenses = monthly_expenses * 12
        mortgage_payment = monthly_payment * 12

        # Net cash flow
        net_cash_flow = total_rental_income - total_expenses - mortgage_payment

        # Cumulative cash flow
        if previous_results:
            cumulative_cash_flow = previous_results.cumulative_cash_flow + net_cash_flow
        else:
            cumulative_cash_flow = net_cash_flow

        # Equity calculation
        equity = property_value - ending_balance

        # Cash on cash return
        if down_payment > 0:
            cash_on_cash_return = (net_cash_flow / down_payment) * 100
        else:
            cash_on_cash_return = Decimal('0')

        return YearlyResults(
            year=year,
            beginning_balance=beginning_balance,
            monthly_rent=monthly_rent,
            total_rental_income=total_rental_income,
            total_expenses=total_expenses,
            mortgage_payment=mortgage_payment,
            principal_payment=annual_principal,
            interest_payment=annual_interest,
            net_cash_flow=net_cash_flow,
            cumulative_cash_flow=cumulative_cash_flow,
            property_value=property_value,
            equity=equity,
            debt_balance=ending_balance,
            cash_on_cash_return=cash_on_cash_return
        )

    def _calculate_mortgage_payment(self, loan_amount: Decimal, interest_rate: Decimal, term_years: int) -> Decimal:
        """Calculate monthly mortgage payment"""
        if loan_amount == 0 or interest_rate == 0:
            return Decimal('0')

        monthly_rate = interest_rate / 12
        num_payments = term_years * 12

        # Convert to float for calculation, then back to Decimal
        monthly_rate_float = float(monthly_rate)
        loan_amount_float = float(loan_amount)

        if monthly_rate_float == 0:
            payment = loan_amount_float / num_payments
        else:
            payment = loan_amount_float * (
                    monthly_rate_float * (1 + monthly_rate_float) ** num_payments
            ) / ((1 + monthly_rate_float) ** num_payments - 1)

        return Decimal(str(round(payment, 2)))


class SimulationEngine:
    """Main simulation engine using Strategy pattern"""

    def __init__(self, strategy: SimulationStrategy, discount_rate: Decimal = Decimal('0.08')):
        self.strategy = strategy
        self.discount_rate = discount_rate  # For NPV calculations

    def run_simulation(self, property_data: Dict, years: int) -> Tuple[List[YearlyResults], SimulationSummary]:
        """Run the complete simulation"""

        yearly_results = []
        previous_result = None

        # Calculate year by year
        for year in range(1, years + 1):
            year_result = self.strategy.calculate_year(year, property_data, previous_result)
            yearly_results.append(year_result)
            previous_result = year_result

        # Calculate summary
        summary = self._calculate_summary(property_data, yearly_results)

        return yearly_results, summary

    def _calculate_summary(self, property_data: Dict, yearly_results: List[YearlyResults]) -> SimulationSummary:
        """Calculate summary statistics from yearly results"""

        if not yearly_results:
            raise ValueError("No yearly results to summarize")

        down_payment = Decimal(str(property_data.get('down_payment', 0)))
        closing_costs = Decimal(str(property_data.get('closing_costs', 0)))
        total_investment = down_payment + closing_costs

        # Basic totals
        total_cash_flow = sum(result.net_cash_flow for result in yearly_results)
        final_result = yearly_results[-1]
        final_property_value = final_result.property_value
        final_equity = final_result.equity

        # Total return calculation (cash flow + equity - initial investment)
        total_return = total_cash_flow + final_equity - total_investment

        # Total return percentage
        if total_investment > 0:
            total_return_percentage = (total_return / total_investment) * 100
        else:
            total_return_percentage = Decimal('0')

        # Average annual return
        years = len(yearly_results)
        average_annual_return = total_return_percentage / years if years > 0 else Decimal('0')

        # Internal Rate of Return (IRR)
        irr = self._calculate_irr(total_investment, yearly_results, final_equity)

        # Net Present Value (NPV)
        npv = self._calculate_npv(total_investment, yearly_results, final_equity)

        # Average Cash on Cash Return
        if years > 0:
            cash_on_cash_return = sum(result.cash_on_cash_return for result in yearly_results) / years
        else:
            cash_on_cash_return = Decimal('0')

        return SimulationSummary(
            total_investment=total_investment,
            total_cash_flow=total_cash_flow,
            final_property_value=final_property_value,
            final_equity=final_equity,
            total_return=total_return,
            total_return_percentage=total_return_percentage,
            average_annual_return=average_annual_return,
            internal_rate_of_return=irr,
            net_present_value=npv,
            cash_on_cash_return=cash_on_cash_return
        )

    def _calculate_irr(self, initial_investment: Decimal, yearly_results: List[YearlyResults],
                       final_equity: Decimal) -> Decimal:
        """Calculate Internal Rate of Return using approximation"""

        # Create cash flow array
        cash_flows = [-float(initial_investment)]  # Initial investment as negative

        for i, result in enumerate(yearly_results):
            if i == len(yearly_results) - 1:
                # Last year includes property liquidation
                cash_flow = float(result.net_cash_flow + final_equity)
            else:
                cash_flow = float(result.net_cash_flow)
            cash_flows.append(cash_flow)

        # Simple IRR approximation using bisection method
        return self._approximate_irr(cash_flows)

    def _approximate_irr(self, cash_flows: List[float]) -> Decimal:
        """Approximate IRR using bisection method"""

        def npv_at_rate(rate: float) -> float:
            """Calculate NPV at given rate"""
            npv = 0
            for i, cf in enumerate(cash_flows):
                npv += cf / ((1 + rate) ** i)
            return npv

        # Bisection method
        low_rate = -0.99
        high_rate = 5.0
        tolerance = 1e-6
        max_iterations = 100

        for _ in range(max_iterations):
            mid_rate = (low_rate + high_rate) / 2
            npv = npv_at_rate(mid_rate)

            if abs(npv) < tolerance:
                return Decimal(str(round(mid_rate * 100, 4)))

            if npv > 0:
                low_rate = mid_rate
            else:
                high_rate = mid_rate

        return Decimal('0')  # Return 0 if no convergence

    def _calculate_npv(self, initial_investment: Decimal, yearly_results: List[YearlyResults],
                       final_equity: Decimal) -> Decimal:
        """Calculate Net Present Value"""

        npv = -initial_investment  # Initial investment

        for i, result in enumerate(yearly_results):
            year = i + 1
            discount_factor = (1 + self.discount_rate) ** year

            if i == len(yearly_results) - 1:
                # Last year includes property liquidation
                cash_flow = result.net_cash_flow + final_equity
            else:
                cash_flow = result.net_cash_flow

            npv += cash_flow / discount_factor

        return npv

    def export_results(self, yearly_results: List[YearlyResults], summary: SimulationSummary) -> Dict:
        """Export results to dictionary format"""

        return {
            'strategy': self.strategy.get_strategy_name(),
            'summary': summary.to_dict(),
            'yearly_results': [result.to_dict() for result in yearly_results],
            'generated_at': datetime.now(timezone.utc).isoformat()
        }


# Utility functions
def validate_property_data(property_data: Dict) -> List[str]:
    """Validate property data for simulation"""

    errors = []
    required_fields = [
        'purchase_price', 'down_payment', 'loan_amount', 'interest_rate',
        'loan_term_years', 'monthly_rent', 'total_monthly_expenses'
    ]

    for field in required_fields:
        if field not in property_data:
            errors.append(f"Missing required field: {field}")
            continue

        # Check for valid numeric values
        try:
            value = float(property_data[field])
            if value < 0:
                errors.append(f"{field} cannot be negative")
        except (ValueError, TypeError):
            errors.append(f"{field} must be a valid number")

    # Additional validation
    if 'purchase_price' in property_data and 'down_payment' in property_data:
        try:
            if float(property_data['down_payment']) > float(property_data['purchase_price']):
                errors.append("Down payment cannot exceed purchase price")
        except (ValueError, TypeError):
            pass

    return errors


def run_property_simulation(property_obj, years: int = 10, strategy_type: str = 'hold', **strategy_kwargs) -> Dict:
    """Convenience function to run simulation on a Property model object"""

    # Convert property object to dictionary
    property_data = property_obj.to_dict()

    # Validate data
    validation_errors = validate_property_data(property_data)
    if validation_errors:
        raise ValueError(f"Invalid property data: {', '.join(validation_errors)}")

    # Create strategy and engine
    strategy = HoldStrategy()  # For now, only hold strategy
    engine = SimulationEngine(strategy)

    # Run simulation
    yearly_results, summary = engine.run_simulation(property_data, years)

    # Export results
    return engine.export_results(yearly_results, summary)