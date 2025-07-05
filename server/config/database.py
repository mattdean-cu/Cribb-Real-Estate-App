import os
from urllib.parse import quote_plus


class DatabaseConfig:
    """Database configuration for different environments"""

    # Database connection parameters
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'cribb_db')
    DB_USER = os.getenv('DB_USER', 'cribb_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'cribb_pass')

    # Connection pool settings (for production PostgreSQL)
    POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '10'))
    MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', '20'))
    POOL_TIMEOUT = int(os.getenv('DB_POOL_TIMEOUT', '30'))
    POOL_RECYCLE = int(os.getenv('DB_POOL_RECYCLE', '1800'))

    # Override DATABASE_URL if provided (useful for Heroku/production)
    DATABASE_URL = os.getenv('DATABASE_URL')

    @classmethod
    def get_database_url(cls, environment='development'):
        """Get database URL based on environment"""

        # If explicit DATABASE_URL is provided, use it
        if cls.DATABASE_URL:
            return cls.DATABASE_URL

        # Environment-specific database URLs
        if environment == 'testing':
            return 'sqlite:///:memory:'

        if environment == 'development':
            # Use SQLite for development
            sqlite_path = os.getenv('SQLITE_PATH', 'instance/cribb.db')
            return f'sqlite:///{sqlite_path}'

        if environment == 'production':
            # Use PostgreSQL for production
            password = quote_plus(cls.DB_PASSWORD)
            return f'postgresql://{cls.DB_USER}:{password}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}'

        raise ValueError(f"Unknown environment: {environment}")

    @classmethod
    def get_engine_options(cls, environment='development'):
        """Get SQLAlchemy engine options for environment"""

        if environment == 'production':
            return {
                'pool_size': cls.POOL_SIZE,
                'max_overflow': cls.MAX_OVERFLOW,
                'pool_timeout': cls.POOL_TIMEOUT,
                'pool_recycle': cls.POOL_RECYCLE,
                'pool_pre_ping': True,
            }

        return {}