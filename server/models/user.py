from . import db
from flask_login import UserMixin
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
import uuid


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    # Primary Key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Authentication
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # Profile Information
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))

    # Account Status
    is_active = db.Column(db.Boolean, default=True)
    is_premium = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)

    # Preferences
    default_currency = db.Column(db.String(3), default='USD')
    timezone = db.Column(db.String(50), default='UTC')

    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    verified_at = db.Column(db.DateTime)

    # Relationships
    properties = db.relationship('Property', back_populates='owner', lazy='dynamic',
                                 cascade='all, delete-orphan')
    simulations = db.relationship('Simulation', back_populates='user', lazy='dynamic',
                                  cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'

    @property
    def full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip()

    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)

    def mark_verified(self):
        """Mark user as verified"""
        self.is_verified = True
        self.verified_at = datetime.now(timezone.utc)

    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.now(timezone.utc)

    def to_dict(self, include_sensitive=False):
        """Convert to dictionary for JSON serialization"""
        data = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'phone': self.phone,
            'is_active': self.is_active,
            'is_premium': self.is_premium,
            'is_verified': self.is_verified,
            'default_currency': self.default_currency,
            'timezone': self.timezone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
        }

        # Include property and simulation counts
        data['properties_count'] = self.properties.count()
        data['simulations_count'] = self.simulations.count()

        return data

    @staticmethod
    def create_user(email, password, first_name, last_name, **kwargs):
        """Create a new user with validation"""
        # Check if user exists
        if User.query.filter_by(email=email).first():
            raise ValueError("User with this email already exists")

        user = User(
            email=email.lower().strip(),
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            phone=kwargs.get('phone'),
            is_premium=kwargs.get('is_premium', False),
            default_currency=kwargs.get('default_currency', 'USD'),
            timezone=kwargs.get('timezone', 'UTC')
        )

        user.set_password(password)
        return user