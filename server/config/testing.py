import os
from .base import BaseConfig


class TestingConfig(BaseConfig):
    """Testing configuration"""

    DEBUG = True
    TESTING = True

    # Database - Use in-memory SQLite for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False

    # Logging
    LOG_LEVEL = 'ERROR'  # Only log errors during testing

    # Testing-specific settings
    SQLALCHEMY_ECHO = False  # Don't log SQL during tests

    # Override thresholds for testing
    MIN_ROI_THRESHOLD = 5.0
    MIN_CAP_RATE_THRESHOLD = 4.0

    @staticmethod
    def init_app(app):
        BaseConfig.init_app(app)
        print("🧪 Running in TESTING mode")