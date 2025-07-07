#!/usr/bin/env python3
"""
Simple development server runner for Cribb backend - Now with Authentication
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Main function to run the development server with authentication"""

    print("🚀 Starting Cribb Backend with Authentication")
    print("=" * 60)

    # Create instance directory for SQLite
    instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    print(f"📁 Created instance directory: {instance_dir}")

    # Import here to avoid config issues
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    from flask_login import LoginManager, login_user, logout_user, login_required, current_user

    # Create a Flask app with authentication support
    app = Flask(__name__)
    app.config.update({
        'DEBUG': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{os.path.join(instance_dir, "cribb.db")}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'dev-secret-key-for-authentication'
    })

    # Initialize CORS with credentials support
    CORS(app,
         origins=['http://localhost:3000', 'http://localhost:3001'],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

    # Initialize database
    from models import db
    db.init_app(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = None  # Disable automatic redirects
    login_manager.login_message = 'Please log in to access this page.'

    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return User.query.get(int(user_id))

    # Handle unauthorized access properly for API
    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({'error': 'Authentication required'}), 401

    print("🔧 Configuration loaded with authentication")
    print(f"   Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"   Debug: {app.config['DEBUG']}")
    print(f"   Authentication: Enabled")

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
                from models.user import User
                from models.property import Property
                from models.simulation import Simulation

                # Create all tables
                db.create_all()
                print("✅ Database tables created!")

                # Check if we already have data
                if User.query.count() == 0:
                    print("🌱 Seeding database...")

                    # Create demo user
                    demo_user = User.create_user(
                        email='demo@cribb.com',
                        password='Demo123!',
                        first_name='Demo',
                        last_name='User',
                        is_premium=True
                    )
                    db.session.add(demo_user)

                    # Create admin user
                    admin_user = User.create_user(
                        email='admin@cribb.com',
                        password='Admin123!',
                        first_name='Admin',
                        last_name='User',
                        is_premium=True
                    )
                    db.session.add(admin_user)
                    db.session.flush()

                    # Create sample properties for demo user
                    from decimal import Decimal
                    from models.property import PropertyType

                    sample_properties = [
                        {
                            'name': 'Sample Property',
                            'address': '123 Main St',
                            'city': 'Demo City',
                            'state': 'CA',
                            'zip_code': '12345',
                            'property_type': PropertyType.SINGLE_FAMILY,
                            'purchase_price': Decimal('400000'),
                            'down_payment': Decimal('80000'),
                            'loan_amount': Decimal('320000'),
                            'interest_rate': Decimal('0.045'),
                            'monthly_rent': Decimal('3200'),
                            'property_taxes': Decimal('400'),
                            'insurance': Decimal('150'),
                            'maintenance_reserve': Decimal('100'),
                            'owner_id': demo_user.id
                        },
                        {
                            'name': 'Elm Street Investment',
                            'address': '456 Elm Street',
                            'city': 'Denver',
                            'state': 'CO',
                            'zip_code': '80202',
                            'property_type': PropertyType.SINGLE_FAMILY,
                            'purchase_price': Decimal('450000'),
                            'down_payment': Decimal('90000'),
                            'loan_amount': Decimal('360000'),
                            'interest_rate': Decimal('0.05'),
                            'monthly_rent': Decimal('2200'),
                            'property_taxes': Decimal('375'),
                            'insurance': Decimal('125'),
                            'owner_id': demo_user.id
                        },
                        {
                            'name': 'Elm Multi Test',
                            'address': '460 Elm Street',
                            'city': 'Denver',
                            'state': 'CO',
                            'zip_code': '80202',
                            'property_type': PropertyType.MULTI_FAMILY,
                            'purchase_price': Decimal('1150000'),
                            'down_payment': Decimal('380000'),
                            'loan_amount': Decimal('770000'),
                            'interest_rate': Decimal('0.055'),
                            'monthly_rent': Decimal('9500'),
                            'bedrooms': 6,
                            'bathrooms': Decimal('6'),
                            'square_feet': 3600,
                            'property_taxes': Decimal('958'),
                            'insurance': Decimal('400'),
                            'maintenance_reserve': Decimal('950'),
                            'property_management': Decimal('475'),
                            'owner_id': demo_user.id
                        }
                    ]

                    for prop_data in sample_properties:
                        property_obj = Property(**prop_data)
                        db.session.add(property_obj)

                    db.session.commit()
                    print("✅ Sample data created!")
                    print(f"   Demo user: demo@cribb.com / Demo123!")
                    print(f"   Admin user: admin@cribb.com / Admin123!")
                    print(f"   Created {len(sample_properties)} sample properties")
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

    # ===================
    # AUTHENTICATION ROUTES
    # ===================

    @app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
    def login():
        """Login endpoint - supports both POST and OPTIONS for CORS"""
        if request.method == 'OPTIONS':
            return '', 200

        try:
            data = request.get_json()
            if not data:
                return {'error': 'No data provided'}, 400

            email = data.get('email', '').lower().strip()
            password = data.get('password', '')

            if not email or not password:
                return {'error': 'Email and password required'}, 400

            from models.user import User
            user = User.query.filter_by(email=email).first()

            if not user or not user.check_password(password):
                return {'error': 'Invalid credentials'}, 401

            login_user(user, remember=data.get('remember', False))

            return {
                'message': 'Login successful',
                'user': user.to_dict()
            }, 200

        except Exception as e:
            return {'error': f'Login failed: {str(e)}'}, 500

    @app.route('/api/auth/logout', methods=['POST', 'OPTIONS'])
    @login_required
    def logout():
        """Logout endpoint"""
        if request.method == 'OPTIONS':
            return '', 200

        try:
            logout_user()
            return {'message': 'Logout successful'}, 200
        except Exception as e:
            return {'error': f'Logout failed: {str(e)}'}, 500

    @app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
    def register():
        """Register endpoint"""
        if request.method == 'OPTIONS':
            return '', 200

        try:
            data = request.get_json()
            if not data:
                return {'error': 'No data provided'}, 400

            required_fields = ['email', 'password', 'first_name', 'last_name']
            for field in required_fields:
                if not data.get(field):
                    return {'error': f'{field} is required'}, 400

            email = data['email'].lower().strip()

            # Check if user exists
            from models.user import User
            if User.query.filter_by(email=email).first():
                return {'error': 'Email already registered'}, 409

            # Create user
            user = User.create_user(
                email=email,
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone=data.get('phone', ''),
                is_premium=data.get('is_premium', False)
            )

            db.session.add(user)
            db.session.commit()

            # Auto-login
            login_user(user)

            return {
                'message': 'Registration successful',
                'user': user.to_dict()
            }, 201

        except Exception as e:
            db.session.rollback()
            return {'error': f'Registration failed: {str(e)}'}, 500

    @app.route('/api/auth/me', methods=['GET', 'OPTIONS'])
    @login_required
    def get_current_user():
        """Get current user"""
        if request.method == 'OPTIONS':
            return '', 200

        try:
            return {'user': current_user.to_dict()}, 200
        except Exception as e:
            return {'error': f'Failed to get user: {str(e)}'}, 500

    @app.route('/api/auth/dashboard', methods=['GET', 'OPTIONS'])
    @login_required
    def get_dashboard():
        """Get user dashboard"""
        if request.method == 'OPTIONS':
            return '', 200

        try:
            from models.property import Property
            properties = Property.query.filter_by(owner_id=current_user.id).all()

            portfolio_stats = {
                'total_properties': len(properties),
                'total_investment': sum(float(prop.purchase_price) for prop in properties),
                'monthly_income': sum(float(prop.monthly_rent or 0) for prop in properties),
            }

            # Calculate monthly expenses
            total_expenses = 0
            for prop in properties:
                if hasattr(prop, 'total_monthly_expenses'):
                    total_expenses += float(prop.total_monthly_expenses)

            portfolio_stats['monthly_expenses'] = total_expenses
            portfolio_stats['monthly_cash_flow'] = portfolio_stats['monthly_income'] - portfolio_stats[
                'monthly_expenses']

            return {
                'user': current_user.to_dict(),
                'portfolio_stats': portfolio_stats,
                'recent_properties': [prop.to_dict() for prop in properties[:5]]
            }, 200

        except Exception as e:
            return {'error': f'Dashboard failed: {str(e)}'}, 500

    # ===================
    # SYSTEM ROUTES
    # ===================

    @app.route('/health')
    def health():
        try:
            from models.user import User
            from models.property import Property
            user_count = User.query.count()
            property_count = Property.query.count()
            return {
                'status': 'healthy',
                'message': 'Cribb backend is running with authentication!',
                'database': 'connected',
                'users': user_count,
                'properties': property_count,
                'authentication': 'enabled'
            }
        except:
            return {'status': 'healthy', 'message': 'Cribb backend is running!', 'database': 'disconnected'}

    @app.route('/')
    def home():
        return {'message': 'Cribb Real Estate ROI API', 'version': '2.0.0', 'authentication': 'enabled'}

    @app.route('/api/users')
    @login_required
    def get_users():
        """Get all users (admin only in production)"""
        try:
            from models.user import User
            users = User.query.all()
            return {'users': [user.to_dict() for user in users]}
        except Exception as e:
            return {'error': str(e)}, 500

    # ===================
    # PROPERTY ROUTES (Protected)
    # ===================

    @app.route('/api/properties')
    @login_required
    def get_properties():
        """Get current user's properties only"""
        try:
            from models.property import Property
            properties = Property.query.filter_by(owner_id=current_user.id).all()
            return {'properties': [prop.to_dict() for prop in properties]}
        except Exception as e:
            return {'error': str(e)}, 500

    @app.route('/api/properties', methods=['POST'])
    @login_required
    def create_property():
        """Create new property for current user"""
        try:
            data = request.get_json()

            if not data:
                return {'error': 'No data provided'}, 400

            # Validate required fields (removed owner_id since it's set automatically)
            required_fields = ['name', 'address', 'city', 'state', 'zip_code',
                               'property_type', 'purchase_price', 'down_payment',
                               'loan_amount', 'interest_rate']

            for field in required_fields:
                if field not in data:
                    return {'error': f'Missing required field: {field}'}, 400

            # Convert property_type string to enum
            from models.property import PropertyType
            from decimal import Decimal

            try:
                property_type_enum = PropertyType(data['property_type'])
            except ValueError:
                return {'error': f'Invalid property type: {data["property_type"]}'}, 400

            # Create property for current user
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

                owner_id=current_user.id  # Automatically set to current user
            )

            db.session.add(property_obj)
            db.session.commit()

            print(f"✅ Created new property: {property_obj.name} for user {current_user.email}")
            return property_obj.to_dict(), 201

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating property: {e}")
            return {'error': str(e)}, 500

    @app.route('/api/properties/<property_id>', methods=['PUT'])
    @login_required
    def update_property(property_id):
        """Update existing property (only if user owns it)"""
        try:
            from models.property import Property, PropertyType
            from decimal import Decimal

            # Get the property and verify ownership
            property_obj = Property.query.filter_by(id=property_id, owner_id=current_user.id).first()
            if not property_obj:
                return {'error': 'Property not found or access denied'}, 404

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
                property_obj.security_deposit = Decimal(str(data['security_deposit'])) if data[
                    'security_deposit'] else None

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

            print(f"✅ Updated property: {property_obj.name} for user {current_user.email}")
            return property_obj.to_dict(), 200

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error updating property: {e}")
            return {'error': str(e)}, 500

    @app.route('/api/properties/<property_id>', methods=['DELETE'])
    @login_required
    def delete_property(property_id):
        """Delete property (only if user owns it)"""
        try:
            from models.property import Property

            # Get the property and verify ownership
            property_obj = Property.query.filter_by(id=property_id, owner_id=current_user.id).first()
            if not property_obj:
                return {'error': 'Property not found or access denied'}, 404

            property_name = property_obj.name

            # Delete the property (cascading will handle simulations)
            db.session.delete(property_obj)
            db.session.commit()

            print(f"✅ Deleted property: {property_name} for user {current_user.email}")
            return {'message': f'Property "{property_name}" deleted successfully'}, 200

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error deleting property: {e}")
            return {'error': str(e)}, 500

    @app.route('/api/properties/<property_id>/simulate', methods=['POST'])
    @login_required
    def simulate_property(property_id):
        """Run simulation (only if user owns the property)"""
        try:
            from models.property import Property

            # Get the property and verify ownership
            property_obj = Property.query.filter_by(id=property_id, owner_id=current_user.id).first()
            if not property_obj:
                return {'error': 'Property not found or access denied'}, 404

            # Get simulation parameters
            data = request.get_json() or {}
            years = data.get('years', 10)
            strategy_type = data.get('strategy', 'hold')

            # Run simulation
            from services.simulation_service import run_property_simulation
            results = run_property_simulation(property_obj, years, strategy_type)

            return results

        except Exception as e:
            return {'error': str(e)}, 500

    print("\n🌐 Server starting at http://localhost:5000")
    print("🔐 Authentication endpoints:")
    print("   POST /api/auth/login")
    print("   POST /api/auth/logout")
    print("   POST /api/auth/register")
    print("   GET  /api/auth/me")
    print("   GET  /api/auth/dashboard")
    print("🏠 Property endpoints (protected):")
    print("   GET/POST/PUT/DELETE /api/properties")
    print("   POST /api/properties/<id>/simulate")
    print("💡 Demo accounts:")
    print("   demo@cribb.com / Demo123!")
    print("   admin@cribb.com / Admin123!")
    print("=" * 60)

    # Run the application
    app.run(debug=True, port=5000, host='127.0.0.1')


if __name__ == '__main__':
    main()