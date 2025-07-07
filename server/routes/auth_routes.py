# server/routes/auth_routes.py - Fixed Application Context Issues
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
import logging

# Import models individually to avoid circular imports
from models.user import User
from models.property import Property
from models.simulation import Simulation
from models import db

from server.services.auth_service import auth_rate_limit, get_rate_limiter

# Import auth service with error handling
try:
    from services.auth_service import ProductionAuthService
except ImportError:
    # Fallback if auth service not available
    print("⚠️  ProductionAuthService not available, using basic auth")
    ProductionAuthService = None

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Initialize logger
logger = logging.getLogger('auth_routes')


def get_client_info():
    """Extract client information from request"""
    try:
        from flask_limiter.util import get_remote_address
        ip_address = get_remote_address()
    except:
        ip_address = request.environ.get('REMOTE_ADDR', 'unknown')

    return {
        'ip_address': ip_address,
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'timestamp': datetime.utcnow()
    }


def apply_rate_limit(limit="5 per minute"):
    """Apply rate limiting if available"""
    try:
        limiter = current_app.extensions.get('limiter')
        if limiter:
            from flask_limiter.util import get_remote_address
            # Test the rate limit
            limiter.limit(limit).test()
    except Exception as e:
        # Log but don't fail
        logger.debug(f"Rate limiting not applied: {e}")


# Remove all @auth_rate_limit decorators and apply rate limiting inside functions instead

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user with comprehensive validation"""
    # Apply rate limiting inside the function
    apply_rate_limit("3 per minute")

    try:
        # Check if registration is enabled
        if not current_app.config.get('ENABLE_REGISTRATION', True):
            return jsonify({
                'error': 'Registration is currently disabled'
            }), 403

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Extract and validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field) or not str(data[field]).strip():
                return jsonify({'error': f'{field} is required'}), 400

        # Extract optional fields
        optional_data = {
            'phone': data.get('phone', '').strip(),
            'timezone': data.get('timezone', 'UTC')
        }

        # Basic email validation
        email = data['email'].lower().strip()
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Invalid email format'}), 400

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409

        # Create user (using basic method if ProductionAuthService not available)
        if ProductionAuthService:
            auth_service = ProductionAuthService()
            user = auth_service.create_user(
                email=email,
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                **optional_data
            )
        else:
            # Fallback user creation
            user = User.create_user(
                email=email,
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                **optional_data
            )

        db.session.add(user)
        db.session.commit()

        # Log registration
        client_info = get_client_info()
        logger.info(f"New user registered: {user.email} from {client_info['ip_address']}")

        # Handle email verification requirement
        if current_app.config.get('REQUIRE_EMAIL_VERIFICATION', False):
            return jsonify({
                'message': 'Registration successful. Please check your email to verify your account.',
                'user_id': user.uuid if hasattr(user, 'uuid') else user.id,
                'email_verification_required': True
            }), 201
        else:
            # Auto-verify and login user
            user.is_verified = True
            db.session.commit()

            login_user(user, remember=False)
            if hasattr(user, 'update_last_login'):
                user.update_last_login(client_info['ip_address'])

            return jsonify({
                'message': 'Registration successful',
                'user': user.to_dict(),
                'session_expires': user.last_login.isoformat() if user.last_login else None
            }), 201

    except ValueError as e:
        logger.warning(f"Registration validation error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration system error: {str(e)}")
        return jsonify({'error': 'Registration failed due to system error'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login with enhanced security"""
    # Apply rate limiting inside the function
    apply_rate_limit("10 per minute")

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        remember = data.get('remember', False)

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Get client information
        client_info = get_client_info()

        # Find user
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            logger.warning(f"Failed login attempt: {email} from {client_info['ip_address']}")
            return jsonify({'error': 'Invalid email or password'}), 401

        # Check if account is active
        if hasattr(user, 'can_login') and not user.can_login():
            logger.warning(f"Login attempt for inactive account: {email}")
            return jsonify({'error': 'Account is inactive'}), 403

        # Check email verification requirement
        if (current_app.config.get('REQUIRE_EMAIL_VERIFICATION', False) and
                hasattr(user, 'is_verified') and not user.is_verified):
            return jsonify({
                'error': 'Email verification required',
                'email_verification_required': True,
                'user_id': user.uuid if hasattr(user, 'uuid') else user.id
            }), 403

        # Log user in
        login_user(user, remember=remember)

        # Update last login if method exists
        if hasattr(user, 'update_last_login'):
            user.update_last_login(client_info['ip_address'])

        logger.info(f"Successful login: {email} from {client_info['ip_address']}")

        # Calculate session expiration
        session_duration = current_app.config.get('PERMANENT_SESSION_LIFETIME')
        session_expires = None
        if session_duration and user.last_login:
            session_expires = (user.last_login + session_duration).isoformat()

        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'session_expires': session_expires
        }), 200

    except Exception as e:
        logger.error(f"Login system error: {str(e)}")
        return jsonify({'error': 'Login failed due to system error'}), 500


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Secure logout"""
    try:
        user_email = current_user.email
        client_info = get_client_info()

        logout_user()

        logger.info(f"User logged out: {user_email} from {client_info['ip_address']}")
        return jsonify({'message': 'Logout successful'}), 200

    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current user information"""
    try:
        return jsonify({
            'user': current_user.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        return jsonify({'error': 'Failed to get user information'}), 500


@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update user profile"""
    # Apply rate limiting inside the function
    apply_rate_limit("5 per minute")

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'phone', 'timezone']
        updated_fields = []

        for field in allowed_fields:
            if field in data:
                value = data[field]
                setattr(current_user, field, value.strip() if value else None)
                updated_fields.append(field)

        if hasattr(current_user, 'updated_at'):
            current_user.updated_at = datetime.utcnow()

        db.session.commit()

        logger.info(f"Profile updated for {current_user.email}: {', '.join(updated_fields)}")

        return jsonify({
            'message': 'Profile updated successfully',
            'user': current_user.to_dict(),
            'updated_fields': updated_fields
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Profile update error for {current_user.email}: {str(e)}")
        return jsonify({'error': 'Profile update failed'}), 500


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    # Apply rate limiting inside the function
    apply_rate_limit("3 per minute")

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')

        if not current_password or not new_password:
            return jsonify({
                'error': 'Current password and new password are required'
            }), 400

        # Verify current password
        if not current_user.check_password(current_password):
            logger.warning(f"Failed password change attempt for {current_user.email}")
            return jsonify({'error': 'Current password is incorrect'}), 400

        # Basic password validation
        if len(new_password) < 8:
            return jsonify({'error': 'New password must be at least 8 characters long'}), 400

        # Update password
        current_user.set_password(new_password)
        if hasattr(current_user, 'updated_at'):
            current_user.updated_at = datetime.utcnow()

        db.session.commit()

        logger.info(f"Password changed for {current_user.email}")
        return jsonify({'message': 'Password changed successfully'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Password change error for {current_user.email}: {str(e)}")
        return jsonify({'error': 'Password change failed'}), 500


@auth_bp.route('/dashboard', methods=['GET'])
@login_required
def get_dashboard():
    """Get user dashboard data"""
    try:
        # Get user's properties
        properties = Property.query.filter_by(owner_id=current_user.id).all()

        # Calculate portfolio stats
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
        portfolio_stats['monthly_cash_flow'] = portfolio_stats['monthly_income'] - portfolio_stats['monthly_expenses']
        portfolio_stats['annual_cash_flow'] = portfolio_stats['monthly_cash_flow'] * 12

        # Calculate averages
        if properties:
            cap_rates = []
            cash_on_cash_returns = []

            for prop in properties:
                if hasattr(prop, 'cap_rate'):
                    cap_rates.append(float(prop.cap_rate))
                if hasattr(prop, 'cash_on_cash_return'):
                    cash_on_cash_returns.append(float(prop.cash_on_cash_return))

            portfolio_stats['average_cap_rate'] = sum(cap_rates) / len(cap_rates) if cap_rates else 0
            portfolio_stats['average_cash_on_cash'] = sum(cash_on_cash_returns) / len(
                cash_on_cash_returns) if cash_on_cash_returns else 0
        else:
            portfolio_stats['average_cap_rate'] = 0
            portfolio_stats['average_cash_on_cash'] = 0

        # Get recent properties (last 5)
        recent_properties = Property.query.filter_by(owner_id=current_user.id) \
            .order_by(Property.created_at.desc()) \
            .limit(5) \
            .all()

        # Get recent simulations (last 5) - with error handling
        recent_simulations = []
        try:
            recent_simulations = Simulation.query.filter_by(owner_id=current_user.id) \
                .order_by(Simulation.created_at.desc()) \
                .limit(5) \
                .all()
        except Exception:
            # Handle case where simulation table might not exist or have different structure
            pass

        return jsonify({
            'user': current_user.to_dict(),
            'portfolio_stats': portfolio_stats,
            'recent_properties': [prop.to_dict() for prop in recent_properties],
            'recent_simulations': [sim.to_dict() for sim in recent_simulations],
            'dashboard_generated_at': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Dashboard error for {current_user.email}: {str(e)}")
        return jsonify({'error': 'Failed to get dashboard data'}), 500


# Health check for auth system
@auth_bp.route('/health', methods=['GET'])
def auth_health():
    """Authentication system health check"""
    try:
        # Basic checks
        checks = {
            'database': False,
            'rate_limiter': False,
            'user_model': False
        }

        # Test database connection
        try:
            db.session.execute('SELECT 1')
            checks['database'] = True
        except:
            pass

        # Test rate limiter
        try:
            limiter = current_app.extensions.get('limiter')
            if limiter:
                checks['rate_limiter'] = True
        except:
            pass

        # Test user model
        try:
            User.query.first()
            checks['user_model'] = True
        except:
            pass

        overall_health = all(checks.values())

        return jsonify({
            'status': 'healthy' if overall_health else 'degraded',
            'checks': checks,
            'timestamp': datetime.utcnow().isoformat()
        }), 200 if overall_health else 503

    except Exception as e:
        logger.error(f"Auth health check error: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503


def register():
    """Register new user with comprehensive validation"""
    try:
        # Check if registration is enabled
        if not current_app.config.get('ENABLE_REGISTRATION', True):
            return jsonify({
                'error': 'Registration is currently disabled'
            }), 403

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Extract and validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field) or not str(data[field]).strip():
                return jsonify({'error': f'{field} is required'}), 400

        # Extract optional fields
        optional_data = {
            'phone': data.get('phone', '').strip(),
            'timezone': data.get('timezone', 'UTC')
        }

        # Basic email validation
        email = data['email'].lower().strip()
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Invalid email format'}), 400

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409

        # Create user (using basic method if ProductionAuthService not available)
        if ProductionAuthService:
            auth_service = ProductionAuthService()
            user = auth_service.create_user(
                email=email,
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                **optional_data
            )
        else:
            # Fallback user creation
            user = User.create_user(
                email=email,
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                **optional_data
            )

        db.session.add(user)
        db.session.commit()

        # Log registration
        client_info = get_client_info()
        logger.info(f"New user registered: {user.email} from {client_info['ip_address']}")

        # Handle email verification requirement
        if current_app.config.get('REQUIRE_EMAIL_VERIFICATION', False):
            return jsonify({
                'message': 'Registration successful. Please check your email to verify your account.',
                'user_id': user.uuid if hasattr(user, 'uuid') else user.id,
                'email_verification_required': True
            }), 201
        else:
            # Auto-verify and login user
            user.is_verified = True
            db.session.commit()

            login_user(user, remember=False)
            if hasattr(user, 'update_last_login'):
                user.update_last_login(client_info['ip_address'])

            return jsonify({
                'message': 'Registration successful',
                'user': user.to_dict(),
                'session_expires': user.last_login.isoformat() if user.last_login else None
            }), 201

    except ValueError as e:
        logger.warning(f"Registration validation error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration system error: {str(e)}")
        return jsonify({'error': 'Registration failed due to system error'}), 500


@auth_bp.route('/login', methods=['POST'])
@auth_rate_limit("10 per minute")
def login():
    """Login with enhanced security"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        remember = data.get('remember', False)

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Get client information
        client_info = get_client_info()

        # Find user
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            logger.warning(f"Failed login attempt: {email} from {client_info['ip_address']}")
            return jsonify({'error': 'Invalid email or password'}), 401

        # Check if account is active
        if hasattr(user, 'can_login') and not user.can_login():
            logger.warning(f"Login attempt for inactive account: {email}")
            return jsonify({'error': 'Account is inactive'}), 403

        # Check email verification requirement
        if (current_app.config.get('REQUIRE_EMAIL_VERIFICATION', False) and
                hasattr(user, 'is_verified') and not user.is_verified):
            return jsonify({
                'error': 'Email verification required',
                'email_verification_required': True,
                'user_id': user.uuid if hasattr(user, 'uuid') else user.id
            }), 403

        # Log user in
        login_user(user, remember=remember)

        # Update last login if method exists
        if hasattr(user, 'update_last_login'):
            user.update_last_login(client_info['ip_address'])

        logger.info(f"Successful login: {email} from {client_info['ip_address']}")

        # Calculate session expiration
        session_duration = current_app.config.get('PERMANENT_SESSION_LIFETIME')
        session_expires = None
        if session_duration and user.last_login:
            session_expires = (user.last_login + session_duration).isoformat()

        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'session_expires': session_expires
        }), 200

    except Exception as e:
        logger.error(f"Login system error: {str(e)}")
        return jsonify({'error': 'Login failed due to system error'}), 500


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Secure logout"""
    try:
        user_email = current_user.email
        client_info = get_client_info()

        logout_user()

        logger.info(f"User logged out: {user_email} from {client_info['ip_address']}")
        return jsonify({'message': 'Logout successful'}), 200

    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current user information"""
    try:
        return jsonify({
            'user': current_user.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        return jsonify({'error': 'Failed to get user information'}), 500


@auth_bp.route('/profile', methods=['PUT'])
@login_required
@auth_rate_limit("5 per minute")
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'phone', 'timezone']
        updated_fields = []

        for field in allowed_fields:
            if field in data:
                value = data[field]
                setattr(current_user, field, value.strip() if value else None)
                updated_fields.append(field)

        if hasattr(current_user, 'updated_at'):
            current_user.updated_at = datetime.utcnow()

        db.session.commit()

        logger.info(f"Profile updated for {current_user.email}: {', '.join(updated_fields)}")

        return jsonify({
            'message': 'Profile updated successfully',
            'user': current_user.to_dict(),
            'updated_fields': updated_fields
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Profile update error for {current_user.email}: {str(e)}")
        return jsonify({'error': 'Profile update failed'}), 500


@auth_bp.route('/change-password', methods=['POST'])
@login_required
@auth_rate_limit("3 per minute")
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')

        if not current_password or not new_password:
            return jsonify({
                'error': 'Current password and new password are required'
            }), 400

        # Verify current password
        if not current_user.check_password(current_password):
            logger.warning(f"Failed password change attempt for {current_user.email}")
            return jsonify({'error': 'Current password is incorrect'}), 400

        # Basic password validation
        if len(new_password) < 8:
            return jsonify({'error': 'New password must be at least 8 characters long'}), 400

        # Update password
        current_user.set_password(new_password)
        if hasattr(current_user, 'updated_at'):
            current_user.updated_at = datetime.utcnow()

        db.session.commit()

        logger.info(f"Password changed for {current_user.email}")
        return jsonify({'message': 'Password changed successfully'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Password change error for {current_user.email}: {str(e)}")
        return jsonify({'error': 'Password change failed'}), 500


@auth_bp.route('/dashboard', methods=['GET'])
@login_required
def get_dashboard():
    """Get user dashboard data"""
    try:
        # Get user's properties
        properties = Property.query.filter_by(owner_id=current_user.id).all()

        # Calculate portfolio stats
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
        portfolio_stats['monthly_cash_flow'] = portfolio_stats['monthly_income'] - portfolio_stats['monthly_expenses']
        portfolio_stats['annual_cash_flow'] = portfolio_stats['monthly_cash_flow'] * 12

        # Calculate averages
        if properties:
            cap_rates = []
            cash_on_cash_returns = []

            for prop in properties:
                if hasattr(prop, 'cap_rate'):
                    cap_rates.append(float(prop.cap_rate))
                if hasattr(prop, 'cash_on_cash_return'):
                    cash_on_cash_returns.append(float(prop.cash_on_cash_return))

            portfolio_stats['average_cap_rate'] = sum(cap_rates) / len(cap_rates) if cap_rates else 0
            portfolio_stats['average_cash_on_cash'] = sum(cash_on_cash_returns) / len(
                cash_on_cash_returns) if cash_on_cash_returns else 0
        else:
            portfolio_stats['average_cap_rate'] = 0
            portfolio_stats['average_cash_on_cash'] = 0

        # Get recent properties (last 5)
        recent_properties = Property.query.filter_by(owner_id=current_user.id) \
            .order_by(Property.created_at.desc()) \
            .limit(5) \
            .all()

        # Get recent simulations (last 5) - with error handling
        recent_simulations = []
        try:
            recent_simulations = Simulation.query.filter_by(owner_id=current_user.id) \
                .order_by(Simulation.created_at.desc()) \
                .limit(5) \
                .all()
        except Exception:
            # Handle case where simulation table might not exist or have different structure
            pass

        return jsonify({
            'user': current_user.to_dict(),
            'portfolio_stats': portfolio_stats,
            'recent_properties': [prop.to_dict() for prop in recent_properties],
            'recent_simulations': [sim.to_dict() for sim in recent_simulations],
            'dashboard_generated_at': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Dashboard error for {current_user.email}: {str(e)}")
        return jsonify({'error': 'Failed to get dashboard data'}), 500


# Health check for auth system
@auth_bp.route('/health', methods=['GET'])
def auth_health():
    """Authentication system health check"""
    try:
        # Basic checks
        checks = {
            'database': False,
            'rate_limiter': False,
            'user_model': False
        }

        # Test database connection
        try:
            db.session.execute('SELECT 1')
            checks['database'] = True
        except:
            pass

        # Test rate limiter
        limiter = get_rate_limiter()
        if limiter:
            checks['rate_limiter'] = True

        # Test user model
        try:
            User.query.first()
            checks['user_model'] = True
        except:
            pass

        overall_health = all(checks.values())

        return jsonify({
            'status': 'healthy' if overall_health else 'degraded',
            'checks': checks,
            'timestamp': datetime.utcnow().isoformat()
        }), 200 if overall_health else 503

    except Exception as e:
        logger.error(f"Auth health check error: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503


def register():
    """Register new user with comprehensive validation"""
    try:
        # Check if registration is enabled
        if not current_app.config.get('ENABLE_REGISTRATION', True):
            return jsonify({
                'error': 'Registration is currently disabled'
            }), 403

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Extract and validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field) or not str(data[field]).strip():
                return jsonify({'error': f'{field} is required'}), 400

        # Extract optional fields
        optional_data = {
            'phone': data.get('phone', '').strip(),
            'timezone': data.get('timezone', 'UTC')
        }

        # Basic email validation
        email = data['email'].lower().strip()
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Invalid email format'}), 400

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409

        # Create user (using basic method if ProductionAuthService not available)
        if ProductionAuthService:
            auth_service = ProductionAuthService()
            user = auth_service.create_user(
                email=email,
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                **optional_data
            )
        else:
            # Fallback user creation
            user = User.create_user(
                email=email,
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                **optional_data
            )

        db.session.add(user)
        db.session.commit()

        # Log registration
        client_info = get_client_info()
        logger.info(f"New user registered: {user.email} from {client_info['ip_address']}")

        # Handle email verification requirement
        if current_app.config.get('REQUIRE_EMAIL_VERIFICATION', False):
            return jsonify({
                'message': 'Registration successful. Please check your email to verify your account.',
                'user_id': user.uuid if hasattr(user, 'uuid') else user.id,
                'email_verification_required': True
            }), 201
        else:
            # Auto-verify and login user
            user.is_verified = True
            db.session.commit()

            login_user(user, remember=False)
            if hasattr(user, 'update_last_login'):
                user.update_last_login(client_info['ip_address'])

            return jsonify({
                'message': 'Registration successful',
                'user': user.to_dict(),
                'session_expires': user.last_login.isoformat() if user.last_login else None
            }), 201

    except ValueError as e:
        logger.warning(f"Registration validation error: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration system error: {str(e)}")
        return jsonify({'error': 'Registration failed due to system error'}), 500


@auth_bp.route('/login', methods=['POST'])
@auth_rate_limit("10 per minute")
def login():
    """Login with enhanced security"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        remember = data.get('remember', False)

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Get client information
        client_info = get_client_info()

        # Find user
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            logger.warning(f"Failed login attempt: {email} from {client_info['ip_address']}")
            return jsonify({'error': 'Invalid email or password'}), 401

        # Check if account is active
        if hasattr(user, 'can_login') and not user.can_login():
            logger.warning(f"Login attempt for inactive account: {email}")
            return jsonify({'error': 'Account is inactive'}), 403

        # Check email verification requirement
        if (current_app.config.get('REQUIRE_EMAIL_VERIFICATION', False) and
                hasattr(user, 'is_verified') and not user.is_verified):
            return jsonify({
                'error': 'Email verification required',
                'email_verification_required': True,
                'user_id': user.uuid if hasattr(user, 'uuid') else user.id
            }), 403

        # Log user in
        login_user(user, remember=remember)

        # Update last login if method exists
        if hasattr(user, 'update_last_login'):
            user.update_last_login(client_info['ip_address'])

        logger.info(f"Successful login: {email} from {client_info['ip_address']}")

        # Calculate session expiration
        session_duration = current_app.config.get('PERMANENT_SESSION_LIFETIME')
        session_expires = None
        if session_duration and user.last_login:
            session_expires = (user.last_login + session_duration).isoformat()

        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'session_expires': session_expires
        }), 200

    except Exception as e:
        logger.error(f"Login system error: {str(e)}")
        return jsonify({'error': 'Login failed due to system error'}), 500


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Secure logout"""
    try:
        user_email = current_user.email
        client_info = get_client_info()

        logout_user()

        logger.info(f"User logged out: {user_email} from {client_info['ip_address']}")
        return jsonify({'message': 'Logout successful'}), 200

    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current user information"""
    try:
        return jsonify({
            'user': current_user.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        return jsonify({'error': 'Failed to get user information'}), 500


@auth_bp.route('/profile', methods=['PUT'])
@login_required
@auth_rate_limit("5 per minute")
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'phone', 'timezone']
        updated_fields = []

        for field in allowed_fields:
            if field in data:
                value = data[field]
                setattr(current_user, field, value.strip() if value else None)
                updated_fields.append(field)

        if hasattr(current_user, 'updated_at'):
            current_user.updated_at = datetime.utcnow()

        db.session.commit()

        logger.info(f"Profile updated for {current_user.email}: {', '.join(updated_fields)}")

        return jsonify({
            'message': 'Profile updated successfully',
            'user': current_user.to_dict(),
            'updated_fields': updated_fields
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Profile update error for {current_user.email}: {str(e)}")
        return jsonify({'error': 'Profile update failed'}), 500


@auth_bp.route('/change-password', methods=['POST'])
@login_required
@auth_rate_limit("3 per minute")
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')

        if not current_password or not new_password:
            return jsonify({
                'error': 'Current password and new password are required'
            }), 400

        # Verify current password
        if not current_user.check_password(current_password):
            logger.warning(f"Failed password change attempt for {current_user.email}")
            return jsonify({'error': 'Current password is incorrect'}), 400

        # Basic password validation
        if len(new_password) < 8:
            return jsonify({'error': 'New password must be at least 8 characters long'}), 400

        # Update password
        current_user.set_password(new_password)
        if hasattr(current_user, 'updated_at'):
            current_user.updated_at = datetime.utcnow()

        db.session.commit()

        logger.info(f"Password changed for {current_user.email}")
        return jsonify({'message': 'Password changed successfully'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Password change error for {current_user.email}: {str(e)}")
        return jsonify({'error': 'Password change failed'}), 500


@auth_bp.route('/dashboard', methods=['GET'])
@login_required
def get_dashboard():
    """Get user dashboard data"""
    try:
        # Get user's properties
        properties = Property.query.filter_by(owner_id=current_user.id).all()

        # Calculate portfolio stats
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
        portfolio_stats['monthly_cash_flow'] = portfolio_stats['monthly_income'] - portfolio_stats['monthly_expenses']
        portfolio_stats['annual_cash_flow'] = portfolio_stats['monthly_cash_flow'] * 12

        # Calculate averages
        if properties:
            cap_rates = []
            cash_on_cash_returns = []

            for prop in properties:
                if hasattr(prop, 'cap_rate'):
                    cap_rates.append(float(prop.cap_rate))
                if hasattr(prop, 'cash_on_cash_return'):
                    cash_on_cash_returns.append(float(prop.cash_on_cash_return))

            portfolio_stats['average_cap_rate'] = sum(cap_rates) / len(cap_rates) if cap_rates else 0
            portfolio_stats['average_cash_on_cash'] = sum(cash_on_cash_returns) / len(
                cash_on_cash_returns) if cash_on_cash_returns else 0
        else:
            portfolio_stats['average_cap_rate'] = 0
            portfolio_stats['average_cash_on_cash'] = 0

        # Get recent properties (last 5)
        recent_properties = Property.query.filter_by(owner_id=current_user.id) \
            .order_by(Property.created_at.desc()) \
            .limit(5) \
            .all()

        # Get recent simulations (last 5) - with error handling
        recent_simulations = []
        try:
            recent_simulations = Simulation.query.filter_by(owner_id=current_user.id) \
                .order_by(Simulation.created_at.desc()) \
                .limit(5) \
                .all()
        except Exception:
            # Handle case where simulation table might not exist or have different structure
            pass

        return jsonify({
            'user': current_user.to_dict(),
            'portfolio_stats': portfolio_stats,
            'recent_properties': [prop.to_dict() for prop in recent_properties],
            'recent_simulations': [sim.to_dict() for sim in recent_simulations],
            'dashboard_generated_at': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Dashboard error for {current_user.email}: {str(e)}")
        return jsonify({'error': 'Failed to get dashboard data'}), 500


# Health check for auth system
@auth_bp.route('/health', methods=['GET'])
def auth_health():
    """Authentication system health check"""
    try:
        # Basic checks
        checks = {
            'database': False,
            'rate_limiter': False,
            'user_model': False
        }

        # Test database connection
        try:
            db.session.execute('SELECT 1')
            checks['database'] = True
        except:
            pass

        # Test rate limiter
        limiter = get_rate_limiter()
        if limiter:
            checks['rate_limiter'] = True

        # Test user model
        try:
            User.query.first()
            checks['user_model'] = True
        except:
            pass

        overall_health = all(checks.values())

        return jsonify({
            'status': 'healthy' if overall_health else 'degraded',
            'checks': checks,
            'timestamp': datetime.utcnow().isoformat()
        }), 200 if overall_health else 503

    except Exception as e:
        logger.error(f"Auth health check error: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503