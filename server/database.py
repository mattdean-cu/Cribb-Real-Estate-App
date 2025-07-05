from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()


def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # Import all models here to ensure they're registered with SQLAlchemy
        from models import User, Property  # Will create these models next

        # Create tables if they don't exist (for development)
        if app.config.get('FLASK_ENV') == 'development':
            db.create_all()
            print("📊 Database tables created/verified")


def get_db():
    """Get database instance for use in other modules"""
    return db


def create_tables():
    """Create all database tables"""
    db.create_all()
    print("✅ All database tables created")


def drop_tables():
    """Drop all database tables (use with caution!)"""
    db.drop_all()
    print("⚠️  All database tables dropped")


def reset_database():
    """Reset database - drop and recreate all tables"""
    drop_tables()
    create_tables()
    print("🔄 Database reset complete")


# Database utility functions
class DatabaseManager:
    """Database management utility class"""

    @staticmethod
    def backup_database(backup_path=None):
        """Create a backup of the database"""
        if backup_path is None:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_{timestamp}.db"

        # For SQLite databases
        if 'sqlite' in db.engine.url.drivername:
            import shutil
            db_path = db.engine.url.database
            shutil.copy2(db_path, backup_path)
            print(f"💾 Database backed up to: {backup_path}")
            return backup_path
        else:
            print("⚠️  Backup not implemented for this database type")
            return None

    @staticmethod
    def get_table_info():
        """Get information about all tables"""
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()

        table_info = {}
        for table in tables:
            columns = inspector.get_columns(table)
            table_info[table] = {
                'columns': [col['name'] for col in columns],
                'column_count': len(columns)
            }

        return table_info

    @staticmethod
    def validate_connection():
        """Validate database connection"""
        try:
            db.engine.execute('SELECT 1')
            print("✅ Database connection valid")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False


# Context managers for database operations
from contextlib import contextmanager


@contextmanager
def db_transaction():
    """Context manager for database transactions"""
    try:
        db.session.begin()
        yield db.session
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"❌ Transaction rolled back: {e}")
        raise
    finally:
        db.session.close()


# CLI commands for database management
def register_db_commands(app):
    """Register database CLI commands with Flask app"""

    @app.cli.command()
    def init_db_command():
        """Initialize the database"""
        create_tables()
        print("Database initialized!")

    @app.cli.command()
    def reset_db_command():
        """Reset the database"""
        reset_database()
        print("Database reset!")

    @app.cli.command()
    def backup_db_command():
        """Backup the database"""
        backup_path = DatabaseManager.backup_database()
        if backup_path:
            print(f"Database backed up to: {backup_path}")

    @app.cli.command()
    def db_info_command():
        """Show database information"""
        table_info = DatabaseManager.get_table_info()
        print("\n📊 Database Information:")
        for table, info in table_info.items():
            print(f"  Table: {table}")
            print(f"    Columns: {', '.join(info['columns'])}")
            print(f"    Column Count: {info['column_count']}")