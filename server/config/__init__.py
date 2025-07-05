import os
from .base import BaseConfig
from .development import DevelopmentConfig
from .production import ProductionConfig
from .testing import TestingConfig

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Get configuration based on environment"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    return config.get(config_name, config['default'])


# Export for easy importing
__all__ = ['BaseConfig', 'DevelopmentConfig', 'ProductionConfig', 'TestingConfig', 'get_config']