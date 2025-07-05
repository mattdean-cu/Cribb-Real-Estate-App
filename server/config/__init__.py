# Only import base config by default
from .base import BaseConfig

# Import other configs only when needed
def get_config(config_name):
    """Get configuration class by name"""
    if config_name == 'development':
        from .development import DevelopmentConfig
        return DevelopmentConfig
    elif config_name == 'production':
        from .production import ProductionConfig
        return ProductionConfig
    elif config_name == 'testing':
        from .testing import TestingConfig
        return TestingConfig
    else:
        from .development import DevelopmentConfig
        return DevelopmentConfig