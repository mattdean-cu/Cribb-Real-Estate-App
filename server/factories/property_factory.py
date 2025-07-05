from typing import Dict, Any, Type
from .templates.base_template import BasePropertyTemplate
from .templates.rental_template import RentalPropertyTemplate
from .templates.multifamily_template import MultifamilyPropertyTemplate
from .templates.commercial_template import CommercialPropertyTemplate
from .exceptions import UnknownPropertyTypeException


class PropertyTemplateFactory:
    """Factory for creating property simulation templates"""

    # Registry of available templates
    _templates: Dict[str, Type[BasePropertyTemplate]] = {
        'single_family_rental': RentalPropertyTemplate,
        'multifamily': MultifamilyPropertyTemplate,
        'commercial': CommercialPropertyTemplate,
    }

    @classmethod
    def create_template(cls, property_type: str) -> BasePropertyTemplate:
        """Create a property template based on type"""
        if property_type not in cls._templates:
            available_types = list(cls._templates.keys())
            raise UnknownPropertyTypeException(
                f"Unknown property type '{property_type}'. "
                f"Available types: {available_types}"
            )

        template_class = cls._templates[property_type]
        return template_class()

    @classmethod
    def get_available_types(cls) -> list[str]:
        """Get list of available property types"""
        return list(cls._templates.keys())

    @classmethod
    def register_template(cls, property_type: str, template_class: Type[BasePropertyTemplate]):
        """Register a new template type (for extensibility)"""
        cls._templates[property_type] = template_class

    @classmethod
    def get_template_info(cls, property_type: str = None) -> Dict[str, Any]:
        """Get information about templates"""
        if property_type:
            template = cls.create_template(property_type)
            return template.get_template_info()
        else:
            # Return info for all templates
            info = {}
            for ptype in cls._templates:
                template = cls.create_template(ptype)
                info[ptype] = template.get_template_info()
            return info

    @classmethod
    def prepare_property_data(cls, property_type: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare property data using the appropriate template"""
        template = cls.create_template(property_type)
        return template.prepare_simulation_data(raw_data)


# Convenience function for easy importing
def create_property_template(property_type: str) -> BasePropertyTemplate:
    """Convenience function to create a property template"""
    return PropertyTemplateFactory.create_template(property_type)