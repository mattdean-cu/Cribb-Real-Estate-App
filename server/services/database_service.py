from flask import current_app
from flask_migrate import Migrate
from models import db, User, Property, Simulation
from decimal import Decimal
import os

migrate = Migrate()


def init_database(app):
    """Initialize database with Flask app"""
    # Initialize SQLAlchemy
    db.init_app(app)

    # Initialize Flask-Migrate
    migrate.init_app(app, db)

    return db


def create_tables():
    """Create all database tables"""
    db.create_all()
    print("✅ Database tables created successfully!")


def drop_tables():
    """Drop all database tables"""
    db.drop_all()
    print("🗑️  Database tables dropped successfully!")


def reset_database():
    """Reset database - drop and recreate all tables"""
    db.drop_all()
    db.create_all()
    print("🔄 Database reset successfully!")


def check_database_connection():
    """Check database connection"""
    try:
        # Try to execute a simple query (SQLAlchemy 2.0+ requires text())
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def get_database_info():
    """Get database information and statistics"""
    try:
        info = {
            'database_url': current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured'),
            'users': User.query.count(),
            'properties': Property.query.count(),
            'simulations': Simulation.query.count(),
        }
        info['total_records'] = info['users'] + info['properties'] + info['simulations']
        return info
    except Exception as e:
        return {'error': str(e)}


def seed_database():
    """Seed database with sample data for development"""
    try:
        # Check if sample user already exists
        sample_user = User.query.filter_by(email='demo@cribb.app').first()

        if sample_user:
            print("📋 Sample data already exists!")
            return

        # Create sample user
        sample_user = User.create_user(
            email='demo@cribb.app',
            password='demo123',  # In production, this should be much stronger
            first_name='Demo',
            last_name='User',
            is_premium=True
        )

        db.session.add(sample_user)
        db.session.flush()  # Get the user ID

        # Create sample property
        sample_property = Property(
            name='Sample Investment Property',
            description='A sample rental property for demonstration purposes',
            address='123 Investment Street',
            city='Real Estate City',
            state='CA',
            zip_code='90210',
            property_type='single_family',
            bedrooms=3,
            bathrooms=Decimal('2.5'),
            square_feet=1800,
            year_built=2010,

            # Purchase details
            purchase_price=Decimal('400000'),
            down_payment=Decimal('80000'),  # 20%
            loan_amount=Decimal('320000'),
            interest_rate=Decimal('0.0450'),  # 4.5%
            loan_term_years=30,
            closing_costs=Decimal('8000'),

            # Rental details
            monthly_rent=Decimal('3200'),
            security_deposit=Decimal('3200'),

            # Operating expenses
            property_taxes=Decimal('500'),  # Monthly
            insurance=Decimal('150'),
            hoa_fees=Decimal('0'),
            property_management=Decimal('256'),  # 8% of rent
            maintenance_reserve=Decimal('160'),  # 5% of rent
            utilities=Decimal('0'),
            other_expenses=Decimal('50'),

            # Growth assumptions
            vacancy_rate=Decimal('0.05'),  # 5%
            annual_rent_increase=Decimal('0.03'),  # 3%
            annual_expense_increase=Decimal('0.025'),  # 2.5%
            property_appreciation=Decimal('0.04'),  # 4%

            owner_id=sample_user.id
        )

        db.session.add(sample_property)
        db.session.flush()  # Get the property ID

        # Create sample simulation
        sample_simulation = Simulation(
            name='10-Year Buy & Hold Analysis',
            description='Standard rental property investment analysis over 10 years',
            analysis_period_years=10,
            exit_strategy='hold',
            user_id=sample_user.id,
            property_id=sample_property.id
        )

        db.session.add(sample_simulation)
        db.session.commit()

        print("🌱 Database seeded with sample data successfully!")
        print(f"   - Sample user: {sample_user.email}")
        print(f"   - Sample property: {sample_property.name}")
        print(f"   - Sample simulation: {sample_simulation.name}")

    except Exception as e:
        db.session.rollback()
        print(f"❌ Failed to seed database: {e}")
        raise


def validate_database_setup():
    """Validate that database is properly set up"""
    errors = []

    try:
        # Check if tables exist
        if not db.engine.has_table('users'):
            errors.append("Users table does not exist")

        if not db.engine.has_table('properties'):
            errors.append("Properties table does not exist")

        if not db.engine.has_table('simulations'):
            errors.append("Simulations table does not exist")

        # Check if we can query tables
        User.query.first()
        Property.query.first()
        Simulation.query.first()

    except Exception as e:
        errors.append(f"Database query failed: {e}")

    return errors


def backup_database(backup_path=None):
    """Create a simple database backup (SQLite only)"""
    db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')

    if not db_url or not db_url.startswith('sqlite'):
        raise ValueError("Backup only supported for SQLite databases")

    import shutil
    from datetime import datetime

    # Extract database file path
    db_file = db_url.replace('sqlite:///', '')

    if not backup_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"{db_file}.backup_{timestamp}"

    shutil.copy2(db_file, backup_path)
    print(f"📁 Database backed up to: {backup_path}")
    return backup_path