#!/usr/bin/env python3
"""
Database health check script
"""

from flask import Flask
from config import get_config
from database import init_db, DatabaseManager


def check_database_health():
    """Check database health and connection"""

    app = Flask(__name__)
    config_class = get_config()
    app.config.from_object(config_class)

    init_db(app)

    with app.app_context():
        print("🔍 Checking database health...")

        # Check connection
        if not DatabaseManager.validate_connection():
            return False

        # Get table information
        table_info = DatabaseManager.get_table_info()

        print(f"📊 Found {len(table_info)} tables:")
        for table, info in table_info.items():
            print(f"  ✓ {table} ({info['column_count']} columns)")

        print("✅ Database health check passed!")
        return True


if __name__ == "__main__":
    if check_database_health():
        print("\n🎉 Database is healthy!")
    else:
        print("\n❌ Database health check failed!")