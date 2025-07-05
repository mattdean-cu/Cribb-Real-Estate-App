from typing import Dict, Any, List
from .base_template import BasePropertyTemplate


class CommercialPropertyTemplate(BasePropertyTemplate):
    """Template for commercial properties"""

    def get_property_type(self) -> str:
        return "commercial"

    def get_required_fields(self) -> List[str]:
        return [
            'purchase_price',
            'annual_rent',  # Commercial often quoted annually
            'address',
            'lease_term'  # Lease term in years
        ]

    def get_default_values(self) -> Dict[str, Any]:
        return {
            'down_payment_percent': 30.0,  # Higher down payment for commercial
            'interest_rate': 5.0,  # Higher commercial rates
            'loan_term': 20,  # Shorter loan terms
            'property_tax_rate': 2.0,  # Higher commercial property taxes
            'insurance_annual': 3000,  # Higher commercial insurance
            'maintenance_rate': 2.0,  # Higher maintenance costs
            'vacancy_rate': 10.0,  # Higher commercial vacancy
            'property_mgmt_rate': 5.0,  # Professional management
            'closing_costs': 8000,  # Higher closing costs
            'cap_ex_reserve': 0.5,  # Capital expenditure reserve
            'tenant_improvements': 5000,  # Tenant improvement costs
        }

    def get_calculation_rules(self) -> Dict[str, Any]:
        return {
            'appreciation_rate': 2.5,  # More conservative appreciation
            'rent_increase_rate': 3.0,  # Built into lease escalations
            'expense_increase_rate': 3.0,
            'depreciation_years': 39,  # Commercial depreciation
            'tax_benefits': True,
            'cash_flow_frequency': 'monthly',
            'lease_based_income': True,  # Income tied to lease terms
            'triple_net_lease': False  # Whether tenant pays expenses
        }

    def apply_defaults(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Override to handle annual rent conversion"""
        result = super().apply_defaults(data)

        # Convert annual rent to monthly for consistency
        if 'annual_rent' in result and 'monthly_rent' not in result:
            result['monthly_rent'] = result['annual_rent'] / 12

        return result

    def get_description(self) -> str:
        return "Commercial property with longer lease terms and professional management"