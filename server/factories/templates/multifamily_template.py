from typing import Dict, Any, List
from .base_template import BasePropertyTemplate


class MultifamilyPropertyTemplate(BasePropertyTemplate):
    """Template for multifamily properties (2-4 units)"""

    def get_property_type(self) -> str:
        return "multifamily"

    def get_required_fields(self) -> List[str]:
        return [
            'purchase_price',
            'monthly_rent',  # Total rent from all units
            'address',
            'num_units'
        ]

    def get_default_values(self) -> Dict[str, Any]:
        return {
            'down_payment_percent': 25.0,  # Higher down payment for multifamily
            'interest_rate': 4.5,  # Slightly higher rate
            'loan_term': 30,
            'property_tax_rate': 1.5,  # Higher property taxes
            'insurance_annual': 2000,  # Higher insurance
            'maintenance_rate': 1.5,  # Higher maintenance (1.5% of purchase price)
            'vacancy_rate': 7.0,  # Higher vacancy rate
            'property_mgmt_rate': 8.0,  # Property management more common
            'closing_costs': 5000,  # Higher closing costs
            'rehab_costs': 0,
            'utilities_monthly': 200  # Owner may pay some utilities
        }

    def get_calculation_rules(self) -> Dict[str, Any]:
        return {
            'appreciation_rate': 3.5,  # Slightly higher appreciation
            'rent_increase_rate': 2.5,  # Higher rent increase potential
            'expense_increase_rate': 3.0,  # Higher expense increases
            'depreciation_years': 27.5,  # Residential depreciation
            'tax_benefits': True,
            'cash_flow_frequency': 'monthly',
            'scale_expenses_by_units': True  # Some expenses scale with unit count
        }

    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Override to add multifamily-specific validation"""
        super().validate_input(data)

        # Validate number of units
        if 'num_units' in data:
            if not isinstance(data['num_units'], int) or data['num_units'] < 2:
                raise ValueError("Multifamily properties must have at least 2 units")
            if data['num_units'] > 4:
                raise ValueError("This template is for 2-4 unit properties")

        return True

    def get_description(self) -> str:
        return "Multifamily property (2-4 units) with higher down payment and management requirements"