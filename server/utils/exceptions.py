class CribbException(Exception):
    """Base exception for Cribb application"""
    pass

class ValidationError(CribbException):
    """Raised when input validation fails"""
    pass

class SimulationError(CribbException):
    """Raised when ROI simulation encounters an error"""
    pass

class DatabaseError(CribbException):
    """Raised when database operations fail"""
    pass