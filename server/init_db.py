
"""
Database initialization script for Cribb application
Run this to set up your database for the first time
"""

import os
import sys
from flask import Flask
from config import get_config
from database import init_db, create_tables, DatabaseManager


def initialize_database(config_name=None):
    """Initialize database with sample data"""

    # Create Flask app
    app = Flask(__name__)

    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Initialize database
    init_db(app)

    with app.app_context():
        print("🚀 Initializing Cribb database...")

        # Validate connection
        if not DatabaseManager.validate_connection():
            print("❌ Database connection failed. Check your configuration.")
            return False

        # Create tables
        create_tables()

        # You can add sample data here later
        print("✅ Database initialization complete!")
        return True


if __name__ == "__main__":
    # Allow specifying config via command line
    config_name = sys.argv[1] if len(sys.argv) > 1 else None

    if initialize_database(config_name):
        print("\n🎉 Database is ready for use!")
    else:
        print("\n❌ Database initialization failed!")
        sys.exit(1)