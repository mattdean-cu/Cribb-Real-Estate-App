import os
from pathlib import Path


class BaseConfig:
    """Base configuration class with common settings"""

    # Application
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    # File paths
    BASE_DIR = Path(__file__).parent.parent
    STATIC_FOLDER = BASE_DIR / 'static'
    UPLOAD_FOLDER = STATIC_FOLDER / 'uploads'
    EXPORT_FOLDER = STATIC_FOLDER / 'exports'

    # API settings
    API_VERSION = 'v1'
    API_PREFIX = f'/api/{API_VERSION}'

    # Report settings
    MAX_EXPORT_SIZE = 1000  # Maximum number of records in export

    # Financial calculation defaults
    DEFAULT_LOAN_TERM = 30
    DEFAULT_INTEREST_RATE = 4.0
    DEFAULT_DOWN_PAYMENT_PERCENT = 20

    # Alert thresholds
    MIN_ROI_THRESHOLD = 8.0  # Minimum ROI before alert
    MIN_CAP_RATE_THRESHOLD = 6.0  # Minimum cap rate before alert

    @staticmethod
    def init_app(app):
        """Initialize application with this config"""
        # Create necessary directories
        BaseConfig.STATIC_FOLDER.mkdir(exist_ok=True)
        BaseConfig.UPLOAD_FOLDER.mkdir(exist_ok=True)
        BaseConfig.EXPORT_FOLDER.mkdir(exist_ok=True)