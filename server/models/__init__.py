from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Import all models to register them with SQLAlchemy
from .user import User
from .property import Property
from .simulation import Simulation

# Make models available at package level
__all__ = ['db', 'User', 'Property', 'Simulation']
def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    return db