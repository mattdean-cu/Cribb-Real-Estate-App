from abc import ABC, abstractmethod
from typing import Dict, Any, List
from utils.validators import validate_positive_number, validate_percentage


class BasePropertyTemplate(ABC):
    """Abstract base class for all property templates"""

    def __init__(self):
        self.property_type = self.get_property_type()
        self.required_fields = self.get_required_fields()
        self.default_values = self.get_default_values()
        self.calculation_rules = self.get_calculation_rules()

    @abstractmethod
    def get_property_type(self) -> str:
        """Return the property type identifier"""
        pass

    @abstractmethod
    def get_required_fields(self) -> List[str]:
        """Return list of required input fields"""
        pass

    @abstractmethod
    def get_default_values(self) -> Dict[str, Any]:
        """Return default values for optional fields"""
        pass

    @abstractmethod
    def get_calculation_rules(self) -> Dict[str, Any]:
        """Return property-specific calculation rules"""
        pass

    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data against template requirements"""
        # Check required fields
        for field in self.required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Validate positive numbers
        numeric_fields = ['purchase_price', 'monthly_rent', 'down_payment']
        for field in numeric_fields:
            if field in data:
                validate_positive_number(data[field], field)

        # Validate percentages
        percentage_fields = ['interest_rate', 'vacancy_rate', 'maintenance_rate']
        for field in percentage_fields:
            if field in data:
                validate_percentage(data[field], field)

        return True

    def apply_defaults(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default values to missing optional fields"""
        result = data.copy()

        for field, default_value in self.default_values.items():
            if field not in result:
                result[field] = default_value

        return result

    def prepare_simulation_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare and validate data for simulation"""
        # Validate input
        self.validate_input(raw_data)

        # Apply defaults
        simulation_data = self.apply_defaults(raw_data)

        # Add property type
        simulation_data['property_type'] = self.property_type

        # Add calculation rules
        simulation_data['calculation_rules'] = self.calculation_rules

        return simulation_data

    def get_template_info(self) -> Dict[str, Any]:
        """Get information about this template"""
        return {
            'property_type': self.property_type,
            'required_fields': self.required_fields,
            'default_values': self.default_values,
            'description': self.get_description()
        }

    @abstractmethod
    def get_description(self) -> str:
        """Return a description of this property template"""
        pass