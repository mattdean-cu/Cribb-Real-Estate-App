# server/app.py - Complete Production Flask Application with Authentication
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_migrate import Migrate
from flask_mail import Mail
from models import db
from models.user import User
from models.property import Property
from models.simulation import Simulation
from datetime import datetime
import os
import logging
from logging.handlers import RotatingFileHandler

# Import services with error handling
try:
    from services.database_service import check_database_connection
except ImportError:
    def check_database_connection():
        try:
            db.session.execute('SELECT 1')
            return True
        except:
            return False

try:
    from config.production import config
except ImportError:
    print("⚠️  Production config not found, using basic config")


    # Fallback basic configuration
    class BasicConfig:
        DEBUG = True
        SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/cribb.db'
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SECRET_KEY = 'dev-secret-key-change-in-production'
        CORS_ORIGINS = ['http://localhost:3000']
        CORS_SUPPORTS_CREDENTIALS = True
        API_VERSION = '2.0.0'
        API_PREFIX = '/api/v1'
        ENABLE_REGISTRATION = True
        REQUIRE_EMAIL_VERIFICATION = False
        ENABLE_PASSWORD_RESET = True

        @staticmethod
        def init_app(app):
            pass


    config = {
        'development': BasicConfig,
        'production': BasicConfig,
        'default': BasicConfig
    }

try:
    from decouple import config as env_config
except ImportError:
    def env_config(key, default=None):
        return os.getenv(key, default)


def create_app(config_name=None):
    """Production application factory with security best practices"""

    app = Flask(__name__)

    # Determine configuration
    if config_name is None:
        config_name = env_config('FLASK_ENV', default='development')

    # Load configuration
    try:
        config_class = config.get(config_name, config['default'])
        app.config.from_object(config_class)
        config_class.init_app(app)
    except Exception as e:
        print(f"⚠️  Configuration error: {e}")
        # Fallback to default config
        app.config.from_object(config['default'])

    # Security headers
    @app.after_request
    def set_security_headers(response):
        """Add security headers to all responses"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    # Initialize extensions
    init_extensions(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    # Initialize database
    with app.app_context():
        init_database()

    return app


def init_extensions(app):
    """Initialize Flask extensions with production settings"""

    # Initialize database
    db.init_app(app)

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    # Initialize CORS with security settings
    CORS(app,
         origins=app.config.get('CORS_ORIGINS', ['http://localhost:3000']),
         supports_credentials=app.config.get('CORS_SUPPORTS_CREDENTIALS', True),
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         max_age=86400)  # Cache preflight for 24 hours

    # Initialize Email
    mail = Mail(app)

    # Initialize Authentication Service with error handling
    try:
        from services.auth_service import ProductionAuthService
        auth_service = ProductionAuthService(app)
        app.extensions['auth_service'] = auth_service
        print("✅ Production auth service initialized")
    except ImportError:
        print("⚠️  Production auth service not available, using basic Flask-Login")
        # Initialize basic Flask-Login instead
        from flask_login import LoginManager

        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = 'auth.login'
        login_manager.login_message = 'Please log in to access this page.'

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        app.extensions['login_manager'] = login_manager
    except Exception as e:
        print(f"⚠️  Auth service initialization error: {e}")
        print("🔄 Continuing with basic setup...")

    # Store extensions in app for access
    app.extensions['mail'] = mail


def register_blueprints(app):
    """Register application blueprints with error handling"""

    # API prefix
    api_prefix = app.config.get('API_PREFIX', '/api/v1')

    # Health check routes (no auth required)
    @app.route('/health')
    def health_check():
        """Comprehensive health check endpoint"""
        try:
            with app.app_context():
                db_healthy = check_database_connection()

            # Check extensions
            auth_healthy = 'auth_service' in app.extensions
            mail_healthy = 'mail' in app.extensions
            limiter_healthy = 'limiter' in app.extensions

            checks = {
                'database': db_healthy,
                'authentication': auth_healthy,
                'email': mail_healthy,
                'rate_limiting': limiter_healthy
            }

            overall_health = all(checks.values())

            return jsonify({
                'status': 'healthy' if overall_health else 'degraded',
                'version': app.config.get('API_VERSION', '2.0.0'),
                'environment': app.config.get('ENV', 'unknown'),
                'checks': checks,
                'features': {
                    'registration_enabled': app.config.get('ENABLE_REGISTRATION', True),
                    'email_verification_required': app.config.get('REQUIRE_EMAIL_VERIFICATION', False),
                    'password_reset_enabled': app.config.get('ENABLE_PASSWORD_RESET', True)
                }
            }), 200 if overall_health else 503

        except Exception as e:
            app.logger.error(f"Health check error: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'error': 'Health check failed',
                'version': app.config.get('API_VERSION', '2.0.0')
            }), 503

    @app.route('/api/info')
    def api_info():
        """API information endpoint"""
        try:
            with app.app_context():
                try:
                    from services.database_service import get_database_info
                    db_info = get_database_info()
                except ImportError:
                    db_info = {'status': 'available'}

            return jsonify({
                'api_version': app.config.get('API_VERSION', '2.0.0'),
                'name': 'Cribb Real Estate API',
                'description': 'Production-ready real estate investment analysis platform',
                'database_info': db_info,
                'authentication': 'enabled',
                'rate_limiting': 'enabled',
                'endpoints': {
                    'authentication': '/api/auth',
                    'properties': f'{api_prefix}/properties',
                    'simulations': f'{api_prefix}/simulations',
                    'portfolio': f'{api_prefix}/portfolio'
                },
                'documentation': '/api/docs',  # TODO: Add API documentation
                'status': '/health'
            })
        except Exception as e:
            app.logger.error(f"API info error: {str(e)}")
            return jsonify({'error': 'Failed to get API information'}), 500

    # Register authentication routes
    try:
        from routes.auth_routes import auth_bp
        app.register_blueprint(auth_bp)
        app.logger.info("✅ Authentication routes registered")
    except ImportError as e:
        app.logger.error(f"⚠️  Authentication routes not found: {e}")

    # Register portfolio routes
    try:
        from routes.portfolio_routes import portfolio_bp
        app.register_blueprint(portfolio_bp)
        app.logger.info("✅ Portfolio routes registered")
    except ImportError as e:
        app.logger.error(f"⚠️  Portfolio routes not found: {e}")


    # Register property routes (with authentication)
    try:
        from routes.property_routes import property_bp
        app.register_blueprint(property_bp, url_prefix=api_prefix)
        app.logger.info("✅ Property routes registered")
    except ImportError as e:
        app.logger.error(f"⚠️  Property routes not found: {e}")

    # Register additional API routes
    register_api_routes(app, api_prefix)


def register_api_routes(app, api_prefix):
    """Register additional API routes with authentication"""

    # Protected simulations endpoints
    @app.route(f'{api_prefix}/simulations', methods=['GET'])
    def get_simulations():
        """Get all simulations for current user"""
        from flask_login import login_required, current_user

        @login_required
        def _get_simulations():
            try:
                simulations = Simulation.query.filter_by(owner_id=current_user.id) \
                    .order_by(Simulation.created_at.desc()).all()
                return jsonify([sim.to_dict() for sim in simulations]), 200
            except Exception as e:
                app.logger.error(f"Get simulations error: {str(e)}")
                return jsonify({'error': 'Failed to fetch simulations'}), 500

        return _get_simulations()

    @app.route(f'{api_prefix}/simulations/<simulation_id>', methods=['GET'])
    def get_simulation(simulation_id):
        """Get specific simulation with results"""
        from flask_login import login_required, current_user

        @login_required
        def _get_simulation():
            try:
                simulation = Simulation.query.filter_by(
                    id=simulation_id,
                    owner_id=current_user.id
                ).first_or_404()
                return jsonify(simulation.to_dict(include_results=True)), 200
            except Exception as e:
                app.logger.error(f"Get simulation error: {str(e)}")
                return jsonify({'error': 'Simulation not found'}), 404

        return _get_simulation()

    # Portfolio endpoints
    @app.route(f'{api_prefix}/portfolio/stats', methods=['GET'])
    def get_portfolio_stats():
        """Get portfolio statistics"""
        from flask_login import login_required, current_user

        @login_required
        def _get_portfolio_stats():
            try:
                properties = Property.query.filter_by(owner_id=current_user.id).all()

                if not properties:
                    return jsonify({
                        'total_properties': 0,
                        'total_investment': 0,
                        'total_equity': 0,
                        'monthly_income': 0,
                        'monthly_expenses': 0,
                        'monthly_cash_flow': 0,
                        'annual_cash_flow': 0,
                        'average_cap_rate': 0,
                        'average_cash_on_cash': 0
                    }), 200

                # Calculate comprehensive statistics
                stats = {
                    'total_properties': len(properties),
                    'total_investment': sum(float(prop.purchase_price) for prop in properties),
                    'total_equity': sum(float(prop.purchase_price - prop.loan_amount) for prop in properties),
                    'monthly_income': sum(float(prop.monthly_rent or 0) for prop in properties),
                    'monthly_expenses': sum(float(prop.total_monthly_expenses) for prop in properties),
                }

                stats['monthly_cash_flow'] = stats['monthly_income'] - stats['monthly_expenses']
                stats['annual_cash_flow'] = stats['monthly_cash_flow'] * 12

                # Calculate averages
                if properties:
                    stats['average_cap_rate'] = sum(float(prop.cap_rate) for prop in properties) / len(properties)
                    stats['average_cash_on_cash'] = sum(float(prop.cash_on_cash_return) for prop in properties) / len(
                        properties)
                else:
                    stats['average_cap_rate'] = 0
                    stats['average_cash_on_cash'] = 0

                # Property type breakdown
                property_types = {}
                for prop in properties:
                    prop_type = prop.property_type.value if hasattr(prop.property_type, 'value') else str(
                        prop.property_type)
                    if prop_type not in property_types:
                        property_types[prop_type] = 0
                    property_types[prop_type] += 1

                stats['property_types'] = property_types
                stats['calculated_at'] = datetime.utcnow().isoformat()

                return jsonify(stats), 200

            except Exception as e:
                app.logger.error(f"Portfolio stats error: {str(e)}")
                return jsonify({'error': 'Failed to get portfolio stats'}), 500

        return _get_portfolio_stats()

    # Admin endpoints (if user is admin)
    @app.route(f'{api_prefix}/admin/users', methods=['GET'])
    def admin_get_users():
        """Admin endpoint to get all users"""
        from flask_login import login_required, current_user

        @login_required
        def _admin_get_users():
            if not current_user.is_admin:
                return jsonify({'error': 'Admin access required'}), 403

            try:
                users = User.query.filter_by(deleted_at=None).all()
                return jsonify([user.to_dict(include_sensitive=True) for user in users]), 200
            except Exception as e:
                app.logger.error(f"Admin get users error: {str(e)}")
                return jsonify({'error': 'Failed to fetch users'}), 500

        return _admin_get_users()


def register_error_handlers(app):
    """Register comprehensive error handlers"""

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad request',
            'message': 'The request could not be understood or was missing required parameters',
            'status_code': 400
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'Authentication required',
            'message': 'Please log in to access this resource',
            'status_code': 401
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Access denied',
            'message': 'You do not have permission to access this resource',
            'status_code': 403
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Resource not found',
            'message': 'The requested resource could not be found',
            'status_code': 404
        }), 404

    @app.errorhandler(429)
    def ratelimit_handler(error):
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please try again later.',
            'status_code': 429
        }), 429

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f"Internal server error: {str(error)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }), 500

    @app.errorhandler(Exception)
    def unhandled_exception(error):
        db.session.rollback()
        app.logger.error(f"Unhandled exception: {str(error)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }), 500


def init_database():
    """Initialize database with tables and sample data"""
    try:
        # Create all tables
        db.create_all()
        print("✅ Database tables created/verified")

        # Create sample users if no users exist
        if User.query.count() == 0:
            print("🌱 Creating sample users...")

            # Create admin user
            admin_user = User.create_user(
                email=env_config('ADMIN_EMAIL', default='admin@cribb.com'),
                password='Admin123!@#',
                first_name='Admin',
                last_name='User',
                is_premium=True,
                is_admin=True,
                is_verified=True,
                timezone='America/Denver'
            )
            db.session.add(admin_user)

            # Create demo user
            demo_user = User.create_user(
                email='demo@cribb.com',
                password='Demo123!',
                first_name='Demo',
                last_name='User',
                is_premium=True,
                is_verified=True,
                timezone='America/Denver'
            )
            db.session.add(demo_user)
            db.session.flush()  # Get user IDs

            # Create sample properties for demo user
            from models.property import PropertyType
            from decimal import Decimal

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
                    'bedrooms': 3,
                    'bathrooms': Decimal('2'),
                    'square_feet': 1500,
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
                    'bedrooms': 2,
                    'bathrooms': Decimal('1'),
                    'square_feet': 1200,
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
            print("✅ Sample data created")
            print(f"   Admin user: {admin_user.email} / Admin123!@#")
            print(f"   Demo user: demo@cribb.com / Demo123!")
            print(f"   Created {len(sample_properties)} sample properties")
        else:
            print("📋 Database already has users")

    except Exception as e:
        db.session.rollback()
        print(f"⚠️  Database initialization error: {e}")
        print("🔄 Continuing anyway...")


def migrate_existing_properties_to_demo_user():
    """
    Run this if you have existing properties that need to be assigned to the demo user
    """
    try:
        # Find or create demo user
        demo_user = User.query.filter_by(email='demo@cribb.com').first()
        if not demo_user:
            demo_user = User.create_user(
                email='demo@cribb.com',
                password='Demo123!',
                first_name='Demo',
                last_name='User',
                is_premium=True,
                is_verified=True
            )
            db.session.add(demo_user)
            db.session.flush()

        # Update properties without owner_id
        orphaned_properties = Property.query.filter_by(owner_id=None).all()
        for prop in orphaned_properties:
            prop.owner_id = demo_user.id

        # Update properties with old sample_user references
        # This handles properties that might have been created with old user IDs
        invalid_properties = Property.query.filter(
            Property.owner_id.notin_(
                db.session.query(User.id).subquery()
            )
        ).all()

        for prop in invalid_properties:
            prop.owner_id = demo_user.id

        db.session.commit()
        print(f"✅ Migrated {len(orphaned_properties + invalid_properties)} properties to demo user")

    except Exception as e:
        db.session.rollback()
        print(f"❌ Migration error: {e}")


def reset_database():
    """
    CAUTION: This will delete all data and recreate tables
    Only use in development!
    """
    import os

    print("⚠️  WARNING: This will delete ALL data!")
    confirm = input("Type 'CONFIRM' to proceed: ")

    if confirm == 'CONFIRM':
        # Drop all tables
        db.drop_all()

        # Remove SQLite file if it exists
        db_path = 'instance/cribb.db'
        if os.path.exists(db_path):
            os.remove(db_path)

        # Recreate everything
        init_database()
        print("✅ Database reset complete")
    else:
        print("❌ Database reset cancelled")


# For development and production
if __name__ == '__main__':
    # Create .env file if it doesn't exist
    env_file = '.env'
    if not os.path.exists(env_file):
        print("⚠️  .env file not found. Please create one using .env.template")
        print("🔧 Using default development settings")

    app = create_app('development')

    print("\n🚀 Starting Cribb Real Estate (Production-Ready)")
    print("=" * 70)
    print("🔐 Security Features:")
    print("   ✅ Password strength validation (12+ chars, mixed case, numbers, symbols)")
    print("   ✅ Account lockout protection (5 attempts → 30min lock)")
    print("   ✅ Rate limiting (5/min auth, 100/hour general)")
    print("   ✅ Secure session management")
    print("   ✅ Security headers (XSS, CSRF, etc.)")
    print("   ✅ Input validation & sanitization")
    print("   ✅ Comprehensive audit logging")
    print("   ✅ Email verification (configurable)")
    print("   ✅ Password reset functionality")
    print("\n🔗 Authentication endpoints:")
    print("   POST /api/auth/register - Register new user")
    print("   POST /api/auth/login - Login user")
    print("   POST /api/auth/logout - Logout user")
    print("   GET  /api/auth/me - Get current user")
    print("   PUT  /api/auth/profile - Update profile")
    print("   POST /api/auth/change-password - Change password")
    print("   POST /api/auth/forgot-password - Request password reset")
    print("   POST /api/auth/reset-password - Reset password with token")
    print("   POST /api/auth/verify-email - Verify email")
    print("   GET  /api/auth/dashboard - Get user dashboard")
    print("\n🏠 Property endpoints (authenticated):")
    print("   GET    /api/v1/properties - Get user's properties")
    print("   POST   /api/v1/properties - Create property")
    print("   PUT    /api/v1/properties/<id> - Update property")
    print("   DELETE /api/v1/properties/<id> - Delete property")
    print("   POST   /api/v1/properties/<id>/simulate - Run simulation")
    print("   GET    /api/v1/portfolio/stats - Get portfolio statistics")
    print("\n📊 Additional endpoints:")
    print("   GET /api/v1/simulations - Get user's simulations")
    print("   GET /api/v1/admin/users - Admin: Get all users")
    print("\n🏥 System endpoints:")
    print("   GET /health - System health check")
    print("   GET /api/info - API information")
    print("   GET /api/auth/health - Auth system health")
    print("\n💡 Demo accounts:")
    print("   Admin: admin@cribb.com / Admin123!@#")
    print("   Demo:  demo@cribb.com / Demo123!")
    print("\n🔧 Development utilities:")
    print(
        "   python -c \"from app import migrate_existing_properties_to_demo_user; migrate_existing_properties_to_demo_user()\"")
    print("   python -c \"from app import reset_database; reset_database()\"")
    print("=" * 70)

    # Windows-compatible server selection
    if os.name == 'nt':  # Windows
        try:
            from waitress import serve

            print("🪟 Starting with Waitress server (Windows compatible)")
            serve(app, host='127.0.0.1', port=5000, threads=6)
        except ImportError:
            print("🪟 Waitress not installed, using Flask dev server")
            print("   Install Waitress for better performance: pip install waitress")
            app.run(debug=app.config.get('DEBUG', False), port=5000, host='127.0.0.1')
    else:  # Linux/Mac
        print("🐧 Starting with Flask development server")
        app.run(debug=app.config.get('DEBUG', False), port=5000, host='127.0.0.1')