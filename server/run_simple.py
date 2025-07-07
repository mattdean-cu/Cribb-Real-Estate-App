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

    # CREATE Property POST endpoint
    @app.route('/api/properties', methods=['POST'])
    def create_property():
        """Create new property"""
        from flask import request
        from models import Property, User
        from models.property import PropertyType
        from decimal import Decimal

        try:
            data = request.get_json()

            if not data:
                return {'error': 'No data provided'}, 400

            # Validate required fields
            required_fields = ['name', 'address', 'city', 'state', 'zip_code',
                               'property_type', 'purchase_price', 'down_payment',
                               'loan_amount', 'interest_rate', 'owner_id']

            for field in required_fields:
                if field not in data:
                    return {'error': f'Missing required field: {field}'}, 400

            # Verify owner exists
            owner = User.query.get(data['owner_id'])
            if not owner:
                return {'error': 'Owner not found'}, 404

            # Convert property_type string to enum
            try:
                property_type_enum = PropertyType(data['property_type'])
            except ValueError:
                return {'error': f'Invalid property type: {data["property_type"]}'}, 400

            # Create property
            property_obj = Property(
                name=data['name'],
                address=data['address'],
                city=data['city'],
                state=data['state'],
                zip_code=data['zip_code'],
                property_type=property_type_enum,

                # Financial Details
                purchase_price=Decimal(str(data['purchase_price'])),
                down_payment=Decimal(str(data['down_payment'])),
                loan_amount=Decimal(str(data['loan_amount'])),
                interest_rate=Decimal(str(data['interest_rate'])),
                loan_term_years=data.get('loan_term_years', 30),
                closing_costs=Decimal(str(data.get('closing_costs', 0))),

                # Property Details
                bedrooms=data.get('bedrooms'),
                bathrooms=Decimal(str(data['bathrooms'])) if data.get('bathrooms') else None,
                square_feet=data.get('square_feet'),
                year_built=data.get('year_built'),

                # Rental Information
                monthly_rent=Decimal(str(data['monthly_rent'])) if data.get('monthly_rent') else None,
                security_deposit=Decimal(str(data['security_deposit'])) if data.get('security_deposit') else None,

                # Operating Expenses
                property_taxes=Decimal(str(data.get('property_taxes', 0))),
                insurance=Decimal(str(data.get('insurance', 0))),
                hoa_fees=Decimal(str(data.get('hoa_fees', 0))),
                property_management=Decimal(str(data.get('property_management', 0))),
                maintenance_reserve=Decimal(str(data.get('maintenance_reserve', 0))),
                utilities=Decimal(str(data.get('utilities', 0))),
                other_expenses=Decimal(str(data.get('other_expenses', 0))),

                # Growth Assumptions
                vacancy_rate=Decimal(str(data.get('vacancy_rate', 0.05))),
                annual_rent_increase=Decimal(str(data.get('annual_rent_increase', 0.03))),
                annual_expense_increase=Decimal(str(data.get('annual_expense_increase', 0.02))),
                property_appreciation=Decimal(str(data.get('property_appreciation', 0.03))),

                owner_id=data['owner_id']
            )

            db.session.add(property_obj)
            db.session.commit()

            print(f"✅ Created new property: {property_obj.name}")
            return property_obj.to_dict(), 201

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating property: {e}")  # For debugging
            return {'error': str(e)}, 500

    # UPDATE Property PUT endpoint
    @app.route('/api/properties/<property_id>', methods=['PUT'])
    def update_property(property_id):
        """Update existing property"""
        from flask import request
        from models import Property, User
        from models.property import PropertyType
        from decimal import Decimal

        try:
            # Get the property
            property_obj = Property.query.get(property_id)
            if not property_obj:
                return {'error': 'Property not found'}, 404

            data = request.get_json()
            if not data:
                return {'error': 'No data provided'}, 400

            # Convert property_type string to enum if provided
            if 'property_type' in data:
                try:
                    property_type_enum = PropertyType(data['property_type'])
                    property_obj.property_type = property_type_enum
                except ValueError:
                    return {'error': f'Invalid property type: {data["property_type"]}'}, 400

            # Update basic information
            if 'name' in data:
                property_obj.name = data['name']
            if 'address' in data:
                property_obj.address = data['address']
            if 'city' in data:
                property_obj.city = data['city']
            if 'state' in data:
                property_obj.state = data['state']
            if 'zip_code' in data:
                property_obj.zip_code = data['zip_code']

            # Update financial details
            if 'purchase_price' in data:
                property_obj.purchase_price = Decimal(str(data['purchase_price']))
            if 'down_payment' in data:
                property_obj.down_payment = Decimal(str(data['down_payment']))
            if 'loan_amount' in data:
                property_obj.loan_amount = Decimal(str(data['loan_amount']))
            if 'interest_rate' in data:
                property_obj.interest_rate = Decimal(str(data['interest_rate']))
            if 'loan_term_years' in data:
                property_obj.loan_term_years = data['loan_term_years']
            if 'closing_costs' in data:
                property_obj.closing_costs = Decimal(str(data.get('closing_costs', 0)))

            # Update property details
            if 'bedrooms' in data:
                property_obj.bedrooms = data['bedrooms']
            if 'bathrooms' in data:
                property_obj.bathrooms = Decimal(str(data['bathrooms'])) if data['bathrooms'] else None
            if 'square_feet' in data:
                property_obj.square_feet = data['square_feet']
            if 'year_built' in data:
                property_obj.year_built = data['year_built']

            # Update rental information
            if 'monthly_rent' in data:
                property_obj.monthly_rent = Decimal(str(data['monthly_rent'])) if data['monthly_rent'] else None
            if 'security_deposit' in data:
                property_obj.security_deposit = Decimal(str(data['security_deposit'])) if data['security_deposit'] else None

            # Update operating expenses
            if 'property_taxes' in data:
                property_obj.property_taxes = Decimal(str(data.get('property_taxes', 0)))
            if 'insurance' in data:
                property_obj.insurance = Decimal(str(data.get('insurance', 0)))
            if 'hoa_fees' in data:
                property_obj.hoa_fees = Decimal(str(data.get('hoa_fees', 0)))
            if 'property_management' in data:
                property_obj.property_management = Decimal(str(data.get('property_management', 0)))
            if 'maintenance_reserve' in data:
                property_obj.maintenance_reserve = Decimal(str(data.get('maintenance_reserve', 0)))
            if 'utilities' in data:
                property_obj.utilities = Decimal(str(data.get('utilities', 0)))
            if 'other_expenses' in data:
                property_obj.other_expenses = Decimal(str(data.get('other_expenses', 0)))

            # Update growth assumptions
            if 'vacancy_rate' in data:
                property_obj.vacancy_rate = Decimal(str(data.get('vacancy_rate', 0.05)))
            if 'annual_rent_increase' in data:
                property_obj.annual_rent_increase = Decimal(str(data.get('annual_rent_increase', 0.03)))
            if 'annual_expense_increase' in data:
                property_obj.annual_expense_increase = Decimal(str(data.get('annual_expense_increase', 0.02)))
            if 'property_appreciation' in data:
                property_obj.property_appreciation = Decimal(str(data.get('property_appreciation', 0.03)))

            db.session.commit()

            print(f"✅ Updated property: {property_obj.name}")
            return property_obj.to_dict(), 200

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating property: {e}")
            return {'error': str(e)}, 500

    # DELETE Property endpoint
    @app.route('/api/properties/<property_id>', methods=['DELETE'])
    def delete_property(property_id):
        """Delete property"""
        from models import Property

        try:
            # Get the property
            property_obj = Property.query.get(property_id)
            if not property_obj:
                return {'error': 'Property not found'}, 404

            property_name = property_obj.name

            # Delete the property (cascading will handle simulations)
            db.session.delete(property_obj)
            db.session.commit()

            print(f"✅ Deleted property: {property_name}")
            return {'message': f'Property "{property_name}" deleted successfully'}, 200

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error deleting property: {e}")
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
    print("   http://localhost:5000/api/properties (GET/POST/PUT/DELETE)")
    print("   http://localhost:5000/api/properties/<id>/simulate")
    print("=" * 50)

    # Run the application
    app.run(debug=True, port=5000, host='127.0.0.1')


if __name__ == '__main__':
    main()