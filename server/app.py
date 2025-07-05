from flask import Flask, jsonify
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate
from models import db, User, Property, Simulation
from services.database_service import check_database_connection
from config.development import DevelopmentConfig
import os


def create_app(config_name=None):
    """Application factory pattern"""

    app = Flask(__name__)

    # Determine configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    # Load configuration - use simple approach for now
    if config_name == 'development':
        from config.development import DevelopmentConfig
        config_class = DevelopmentConfig
    else:
        # Fallback basic config
        app.config.update({
            'DEBUG': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///instance/cribb.db',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SECRET_KEY': 'dev-secret-key'
        })
        config_class = None

    if config_class:
        app.config.from_object(config_class)
        config_class.init_app(app)

    # Initialize extensions
    init_extensions(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    return app


def init_extensions(app):
    """Initialize Flask extensions"""

    # Import models here to avoid circular imports
    from models import db, User

    # Initialize database
    db.init_app(app)

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    # Initialize CORS
    CORS(app, origins=['http://localhost:3000', 'http://localhost:3001'])

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)


def register_blueprints(app):
    """Register application blueprints"""

    # Health check routes
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        from services.database_service import check_database_connection

        with app.app_context():
            db_healthy = check_database_connection()

        return jsonify({
            'status': 'healthy' if db_healthy else 'unhealthy',
            'database': 'connected' if db_healthy else 'disconnected',
            'version': '1.0.0',
            'environment': app.config.get('ENV', 'unknown')
        }), 200 if db_healthy else 503

    @app.route('/api/info')
    def api_info():
        """API information endpoint"""
        from services.database_service import get_database_info

        with app.app_context():
            db_info = get_database_info()

        return jsonify({
            'api_version': app.config.get('API_VERSION', 'v1'),
            'database_info': db_info,
            'endpoints': {
                'users': f"{app.config.get('API_PREFIX', '/api/v1')}/users",
                'properties': f"{app.config.get('API_PREFIX', '/api/v1')}/properties",
                'simulations': f"{app.config.get('API_PREFIX', '/api/v1')}/simulations"
            }
        })

    # Import and register your existing routes
    try:
        from routes.property_routes import property_bp
        app.register_blueprint(property_bp, url_prefix=app.config.get('API_PREFIX', '/api/v1'))
    except ImportError:
        print("⚠️  Property routes not found, skipping...")

    # Register additional API routes
    register_api_routes(app)


def register_api_routes(app):
    """Register additional API routes"""

    api_prefix = app.config.get('API_PREFIX', '/api/v1')

    # Users API
    @app.route(f'{api_prefix}/users', methods=['GET'])
    def get_users():
        """Get all users"""
        users = User.query.all()
        return jsonify([user.to_dict() for user in users])

    @app.route(f'{api_prefix}/users/<user_id>', methods=['GET'])
    def get_user(user_id):
        """Get specific user"""
        user = User.query.get_or_404(user_id)
        return jsonify(user.to_dict())

    @app.route(f'{api_prefix}/users', methods=['POST'])
    def create_user():
        """Create new user"""
        from flask import request

        data = request.get_json()
        if not data or 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400

        try:
            user = User.create_user(
                email=data['email'],
                password=data.get('password', 'temp_password'),
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                **{k: v for k, v in data.items() if k in ['phone', 'is_premium', 'timezone']}
            )

            db.session.add(user)
            db.session.commit()

            return jsonify(user.to_dict()), 201

        except ValueError as e:
            return jsonify({'error': str(e)}), 409
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to create user'}), 500

    # Simulations API
    @app.route(f'{api_prefix}/simulations', methods=['GET'])
    def get_simulations():
        """Get all simulations"""
        from models.simulation import Simulation
        simulations = Simulation.query.all()
        return jsonify([sim.to_dict() for sim in simulations])

    @app.route(f'{api_prefix}/simulations/<simulation_id>', methods=['GET'])
    def get_simulation(simulation_id):
        """Get specific simulation with results"""
        from models.simulation import Simulation
        simulation = Simulation.query.get_or_404(simulation_id)
        return jsonify(simulation.to_dict(include_results=True))

    @app.route(f'{api_prefix}/properties/<property_id>/simulate', methods=['POST'])
    def simulate_property(property_id):
        """Run simulation on property"""
        from flask import request
        from models.property import Property
        from services.simulation_service import run_property_simulation

        property_obj = Property.query.get_or_404(property_id)
        data = request.get_json() or {}

        years = data.get('years', 10)
        strategy_type = data.get('strategy', 'hold')

        try:
            results = run_property_simulation(property_obj, years, strategy_type)
            return jsonify(results)
        except Exception as e:
            return jsonify({'error': str(e)}), 500


def register_error_handlers(app):
    """Register error handlers"""

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400


# For development
if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, port=5000)