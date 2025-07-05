from typing import Dict, Any, List
from .base_template import BasePropertyTemplate


class RentalPropertyTemplate(BasePropertyTemplate):
    """Template for single-family rental properties"""

    def get_property_type(self) -> str:
        return "single_family_rental"

    def get_required_fields(self) -> List[str]:
        return [
            'purchase_price',
            'monthly_rent',
            'address'
        ]

    def get_default_values(self) -> Dict[str, Any]:
        return {
            'down_payment_percent': 20.0,
            'interest_rate': 4.0,
            'loan_term': 30,
            'property_tax_rate': 1.2,
            'insurance_annual': 1200,
            'maintenance_rate': 1.0,  # 1% of purchase price annually
            'vacancy_rate': 5.0,  # 5% vacancy
            'property_mgmt_rate': 0.0,  # No property management by default
            'closing_costs': 3000,
            'rehab_costs': 0
        }

    def get_calculation_rules(self) -> Dict[str, Any]:
        return {
            'appreciation_rate': 3.0,  # 3% annual appreciation
            'rent_increase_rate': 2.0,  # 2% annual rent increase
            'expense_increase_rate': 2.5,  # 2.5% annual expense increase
            'depreciation_years': 27.5,  # Residential depreciation
            'tax_benefits': True,
            'cash_flow_frequency': 'monthly'
        }

    def get_description(self) -> str:
        return "Single-family rental property with standard residential investment assumptions"