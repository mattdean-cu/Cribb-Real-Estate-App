# server/config/production.py
import os
from datetime import timedelta
from decouple import config


class Config:
    """Base configuration with security defaults"""

    # Security - Always use environment variables
    SECRET_KEY = config('SECRET_KEY', default=os.urandom(32))
    WTF_CSRF_ENABLED = True

    # Database
    SQLALCHEMY_DATABASE_URI = config('DATABASE_URL', default='sqlite:///instance/cribb.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_timeout': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }

    # Session Configuration
    SESSION_COOKIE_SECURE = config('FLASK_ENV', default='development') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=config('SESSION_TIMEOUT_HOURS', default=2, cast=int))

    # CORS Configuration
    CORS_ORIGINS = config('CORS_ORIGINS', default='http://localhost:3000').split(',')
    CORS_SUPPORTS_CREDENTIALS = True

    # Rate Limiting
    RATELIMIT_STORAGE_URL = config('REDIS_URL', default='memory://')
    RATELIMIT_STRATEGY = 'fixed-window'

    # Email Configuration
    MAIL_SERVER = config('MAIL_SERVER', default='localhost')
    MAIL_PORT = config('MAIL_PORT', default=587, cast=int)
    MAIL_USE_TLS = config('MAIL_USE_TLS', default=True, cast=bool)
    MAIL_USERNAME = config('MAIL_USERNAME', default=None)
    MAIL_PASSWORD = config('MAIL_PASSWORD', default=None)
    MAIL_DEFAULT_SENDER = config('MAIL_DEFAULT_SENDER', default='noreply@cribb.com')

    # Feature Flags
    ENABLE_REGISTRATION = config('ENABLE_REGISTRATION', default=True, cast=bool)
    REQUIRE_EMAIL_VERIFICATION = config('REQUIRE_EMAIL_VERIFICATION', default=False, cast=bool)
    ENABLE_PASSWORD_RESET = config('ENABLE_PASSWORD_RESET', default=True, cast=bool)

    # Logging
    LOG_LEVEL = config('LOG_LEVEL', default='INFO')
    LOG_FILE = config('LOG_FILE', default='logs/cribb.log')

    # Admin
    ADMIN_EMAIL = config('ADMIN_EMAIL', default='admin@cribb.com')

    # API Configuration
    API_VERSION = '2.0.0'
    API_PREFIX = '/api/v1'

    @staticmethod
    def init_app(app):
        """Initialize app-specific settings"""
        pass


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

    # More permissive for development
    SESSION_COOKIE_SECURE = False
    REQUIRE_EMAIL_VERIFICATION = False

    # Development-specific rate limits (more generous)
    RATELIMIT_DEFAULT = "1000 per hour"

    @staticmethod
    def init_app(app):
        Config.init_app(app)

        # Setup development logging
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )


class ProductionConfig(Config):
    """Production configuration with enhanced security"""
    DEBUG = False
    TESTING = False

    # Strict security for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    REQUIRE_EMAIL_VERIFICATION = True

    # Stricter rate limits for production
    RATELIMIT_DEFAULT = "100 per hour"

    @staticmethod
    def init_app(app):
        Config.init_app(app)

        # Setup production logging
        import logging
        from logging.handlers import RotatingFileHandler, SMTPHandler

        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(app.config['LOG_FILE'])
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # File logging
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        # Email critical errors to admin
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])

            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()

            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr=app.config['MAIL_DEFAULT_SENDER'],
                toaddrs=[app.config['ADMIN_EMAIL']],
                subject='Cribb Real Estate Application Error',
                credentials=auth,
                secure=secure
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Cribb Real Estate production startup')


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True

    # Use in-memory database for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # Disable security features for testing
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    REQUIRE_EMAIL_VERIFICATION = False

    # No rate limiting for tests
    RATELIMIT_ENABLED = False


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}