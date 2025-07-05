from utils.exceptions import CribbException

class FactoryException(CribbException):
    """Base exception for factory operations"""
    pass

class UnknownPropertyTypeException(FactoryException):
    """Raised when an unknown property type is requested"""
    pass

class TemplateValidationException(FactoryException):
    """Raised when template validation fails"""
    pass