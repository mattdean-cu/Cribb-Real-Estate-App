import os
from .base import BaseConfig


class DevelopmentConfig(BaseConfig):
    """Development configuration"""

    DEBUG = True
    TESTING = False

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              f'sqlite:///{BaseConfig.BASE_DIR}/cribb_dev.db'

    # Logging
    LOG_LEVEL = 'DEBUG'

    # CORS settings for development
    CORS_ORIGINS = ['http://localhost:3000']  # React dev server

    # Development-specific settings
    SQLALCHEMY_ECHO = True  # Log all SQL queries

    @staticmethod
    def init_app(app):
        BaseConfig.init_app(app)
        print("🏗️  Running in DEVELOPMENT mode")