#!/usr/bin/env python3
"""
Simple development server runner for Cribb backend
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Main function to run the development server"""

    print("🚀 Starting Cribb Backend (Simple Mode)")
    print("=" * 50)

    # Create instance directory for SQLite
    instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    print(f"📁 Created instance directory: {instance_dir}")

    # Import here to avoid config issues
    from flask import Flask
    from flask_cors import CORS

    # Create a simple Flask app with basic config
    app = Flask(__name__)
    app.config.update({
        'DEBUG': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{os.path.join(instance_dir, "cribb.db")}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'dev-secret-key-for-testing'
    })

    # Initialize CORS
    CORS(app, origins=['http://localhost:3000', 'http://localhost:3001'])

    # Initialize database
    from models import db
    db.init_app(app)

    print("🔧 Simple configuration loaded")
    print(f"   Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"   Debug: {app.config['DEBUG']}")

    with app.app_context():
        try:
            from sqlalchemy import text

            # Check if tables exist by trying to query them
            print("📊 Checking database...")

            try:
                # Try to check if users table exists
                result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'"))
                table_exists = result.fetchone() is not None

                if table_exists:
                    print("✅ Database tables exist!")
                else:
                    print("🔧 Tables don't exist, creating them...")
                    raise Exception("Tables need to be created")

            except Exception:
                print("🔧 Creating database tables...")

                # Import all models to ensure they're registered
                from models import User, Property, Simulation

                # Create all tables
                db.create_all()
                print("✅ Database tables created!")

                # Check if we already have data
                if User.query.count() == 0:
                    print("🌱 Seeding database...")

                    # Create a simple user
                    user = User(
                        email='demo@cribb.app',
                        first_name='Demo',
                        last_name='User',
                        is_premium=True
                    )
                    user.set_password('demo123')
                    db.session.add(user)
                    db.session.flush()

                    # Create a simple property
                    from decimal import Decimal
                    from models.property import PropertyType  # Import the enum

                    property_obj = Property(
                        name='Sample Property',
                        address='123 Main St',
                        city='Demo City',
                        state='CA',
                        zip_code='12345',
                        property_type=PropertyType.SINGLE_FAMILY,  # Use enum instead of string
                        purchase_price=Decimal('400000'),
                        down_payment=Decimal('80000'),
                        loan_amount=Decimal('320000'),
                        interest_rate=Decimal('0.045'),
                        monthly_rent=Decimal('3200'),
                        property_taxes=Decimal('500'),
                        insurance=Decimal('150'),
                        owner_id=user.id
                    )
                    db.session.add(property_obj)
                    db.session.commit()

                    print("✅ Sample data created!")
                else:
                    print("📋 Database already has data")

        except Exception as setup_error:
            print(f"⚠️  Database setup issue: {setup_error}")
            # Try to rollback and continue
            try:
                db.session.rollback()
            except:
                pass
            print("🔄 Continuing anyway...")

    # Add a simple health check route
    @app.route('/health')
    def health():
        try:
            from models import User, Property
            user_count = User.query.count()
            property_count = Property.query.count()
            return {
                'status': 'healthy',
                'message': 'Cribb backend is running!',
                'database': 'connected',
                'users': user_count,
                'properties': property_count
            }
        except:
            return {'status': 'healthy', 'message': 'Cribb backend is running!', 'database': 'disconnected'}

    @app.route('/')
    def home():
        return {'message': 'Cribb Real Estate ROI API', 'version': '1.0.0'}

    @app.route('/api/users')
    def get_users():
        try:
            from models import User
            users = User.query.all()
            return {'users': [user.to_dict() for user in users]}
        except Exception as e:
            return {'error': str(e)}, 500

    @app.route('/api/properties')
    def get_properties():
        try:
            from models import Property
            properties = Property.query.all()
            return {'properties': [prop.to_dict() for prop in properties]}
        except Exception as e:
            return {'error': str(e)}, 500

    @app.route('/api/properties/<property_id>/simulate', methods=['POST'])
    def simulate_property(property_id):
        try:
            from flask import request
            from models import Property  # Import here
            from services.simulation_service import run_property_simulation

            # Get the property
            property_obj = Property.query.get(property_id)
            if not property_obj:
                return {'error': 'Property not found'}, 404

            # Get simulation parameters
            data = request.get_json() or {}
            years = data.get('years', 10)
            strategy_type = data.get('strategy', 'hold')

            # Run simulation
            results = run_property_simulation(property_obj, years, strategy_type)

            return results

        except Exception as e:
            return {'error': str(e)}, 500

    print("\n🌐 Server starting at http://localhost:5000")
    print("💡 Test endpoints:")
    print("   http://localhost:5000/")
    print("   http://localhost:5000/health")
    print("   http://localhost:5000/api/users")
    print("   http://localhost:5000/api/properties")
    print("=" * 50)

    # Run the application
    app.run(debug=True, port=5000, host='127.0.0.1')


if __name__ == '__main__':
    main()