# server/middleware/auth_middleware.py
from functools import wraps
from flask import jsonify, request
from flask_login import current_user


def require_auth(f):
    """Decorator to require authentication"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)

    return decorated_function


def require_property_owner(f):
    """Decorator to require property ownership"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401

        # Get property_id from URL parameters
        property_id = kwargs.get('property_id') or request.view_args.get('property_id')
        if property_id:
            from models.property import Property
            property_obj = Property.query.get(property_id)
            if not property_obj or property_obj.owner_id != current_user.id:
                return jsonify({'error': 'Access denied'}), 403

        return f(*args, **kwargs)

    return decorated_function


def optional_auth(f):
    """Decorator for optional authentication (public endpoints that can show different content for authenticated users)"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # This decorator doesn't block access, just passes through
        # current_user will be available in the route
        return f(*args, **kwargs)

    return decorated_function