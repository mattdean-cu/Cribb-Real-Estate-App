from .base import BaseConfig
import os


class DevelopmentConfig(BaseConfig):
    """Development configuration"""

    # Debug settings
    DEBUG = True
    TESTING = False

    # Database - Force SQLite for development (ignore DATABASE_URL for now)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/cribb.db'
    SQLALCHEMY_ECHO = False  # Set to True to see SQL queries
    SQLALCHEMY_ENGINE_OPTIONS = {}
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security (relaxed for development)
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False

    # CORS settings for React frontend
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:3001']

    @staticmethod
    def init_app(app):
        """Initialize development-specific settings"""
        BaseConfig.init_app(app)

        # Create instance directory for SQLite
        import os
        instance_dir = app.instance_path
        os.makedirs(instance_dir, exist_ok=True)

        print("🔧 Development configuration loaded")
        print(f"   Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"   Debug: {app.config['DEBUG']}")