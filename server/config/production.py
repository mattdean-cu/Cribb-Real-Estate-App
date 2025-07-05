import os
from .base import BaseConfig


class ProductionConfig(BaseConfig):
    """Production configuration"""

    DEBUG = False
    TESTING = False

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              f'sqlite:///{BaseConfig.BASE_DIR}/cribb_prod.db'

    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")

    # Logging
    LOG_LEVEL = 'WARNING'

    # CORS settings for production
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')

    # Production-specific settings
    SQLALCHEMY_ECHO = False

    @staticmethod
    def init_app(app):
        BaseConfig.init_app(app)

        # Production-specific initialization
        import logging
        from logging.handlers import RotatingFileHandler

        # Set up file logging
        if not app.debug:
            file_handler = RotatingFileHandler(
                BaseConfig.BASE_DIR / 'logs' / 'cribb.log',
                maxBytes=10240000,  # 10MB
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('Cribb startup')