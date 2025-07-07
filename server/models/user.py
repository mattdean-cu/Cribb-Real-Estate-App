# server/models/user.py - Production User Model with Security
from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from datetime import datetime, timedelta
import secrets
import uuid


class User(UserMixin, db.Model):
    """Production User model with enhanced security features"""
    __tablename__ = 'users'

    # Primary identification
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    email = Column(String(120), unique=True, nullable=False, index=True)

    # Authentication
    password_hash = Column(String(255), nullable=False)
    password_reset_token = Column(String(100), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)

    # Profile information
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=True)
    timezone = Column(String(50), default='UTC')

    # Account status and security
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

    # Email verification
    email_verification_token = Column(String(100), nullable=True)
    email_verification_expires = Column(DateTime, nullable=True)

    # Security tracking
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    last_login_ip = Column(String(45), nullable=True)  # IPv6 compatible
    force_password_change = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete

    # Relationships
    properties = db.relationship('Property', back_populates='owner', lazy=True,
                                 cascade='all, delete-orphan')
    simulations = db.relationship('Simulation', back_populates='user', lazy=True,
                                  cascade='all, delete-orphan')

    def __init__(self, email, first_name, last_name, **kwargs):
        self.email = email.lower().strip()
        self.first_name = first_name.strip()
        self.last_name = last_name.strip()
        self.uuid = str(uuid.uuid4())
        self.email_verification_token = secrets.token_urlsafe(32)
        self.email_verification_expires = datetime.utcnow() + timedelta(hours=24)

        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    # Password methods
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256:260000')
        self.password_reset_token = None
        self.password_reset_expires = None
        self.force_password_change = False

    def check_password(self, password):
        """Check if the provided password matches the stored hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def generate_password_reset_token(self):
        """Generate a secure password reset token"""
        self.password_reset_token = secrets.token_urlsafe(32)
        self.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        return self.password_reset_token

    def verify_password_reset_token(self, token):
        """Verify password reset token is valid and not expired"""
        if not self.password_reset_token or not self.password_reset_expires:
            return False
        if self.password_reset_expires < datetime.utcnow():
            return False
        return secrets.compare_digest(self.password_reset_token, token)

    # Email verification methods
    def generate_email_verification_token(self):
        """Generate a new email verification token"""
        self.email_verification_token = secrets.token_urlsafe(32)
        self.email_verification_expires = datetime.utcnow() + timedelta(hours=24)
        return self.email_verification_token

    def verify_email_token(self, token):
        """Verify email verification token"""
        if not self.email_verification_token or not self.email_verification_expires:
            return False
        if self.email_verification_expires < datetime.utcnow():
            return False
        if secrets.compare_digest(self.email_verification_token, token):
            self.is_verified = True
            self.email_verification_token = None
            self.email_verification_expires = None
            return True
        return False

    # Security methods
    def is_account_locked(self):
        """Check if account is currently locked"""
        if not self.account_locked_until:
            return False
        if self.account_locked_until > datetime.utcnow():
            return True
        else:
            # Auto-unlock expired locks
            self.account_locked_until = None
            self.failed_login_attempts = 0
            return False

    def lock_account(self, duration_minutes=30):
        """Lock account for specified duration"""
        self.account_locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        db.session.commit()

    def unlock_account(self):
        """Manually unlock account"""
        self.account_locked_until = None
        self.failed_login_attempts = 0
        db.session.commit()

    def increment_failed_login(self):
        """Increment failed login attempts and lock if threshold reached"""
        self.failed_login_attempts += 1

        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.lock_account(30)  # Lock for 30 minutes
        # Longer lock after 10 attempts
        elif self.failed_login_attempts >= 10:
            self.lock_account(120)  # Lock for 2 hours

        db.session.commit()

    def reset_failed_login(self):
        """Reset failed login attempts on successful login"""
        self.failed_login_attempts = 0
        self.account_locked_until = None

    def update_last_login(self, ip_address=None):
        """Update login tracking information"""
        self.last_login = datetime.utcnow()
        if ip_address:
            self.last_login_ip = ip_address
        self.reset_failed_login()
        db.session.commit()

    # Utility methods
    def get_full_name(self):
        """Return the user's full name"""
        return f"{self.first_name} {self.last_name}"

    def get_initials(self):
        """Return the user's initials"""
        return f"{self.first_name[0]}{self.last_name[0]}".upper()

    def soft_delete(self):
        """Soft delete the user (mark as deleted but keep data)"""
        self.deleted_at = datetime.utcnow()
        self.is_active = False
        self.email = f"deleted_{self.uuid}_{self.email}"  # Prevent email conflicts

    def can_login(self):
        """Check if user is allowed to log in"""
        return (self.is_active and
                not self.deleted_at and
                not self.is_account_locked())

    # Class methods
    @classmethod
    def create_user(cls, email, password, first_name, last_name, **kwargs):
        """Create a new user with validation"""
        # Check if email already exists
        if cls.query.filter_by(email=email.lower()).first():
            raise ValueError('Email already registered')

        user = cls(email=email, first_name=first_name, last_name=last_name, **kwargs)
        user.set_password(password)
        return user

    @classmethod
    def find_by_email(cls, email):
        """Find user by email (case-insensitive)"""
        return cls.query.filter_by(email=email.lower()).first()

    @classmethod
    def find_by_uuid(cls, user_uuid):
        """Find user by UUID"""
        return cls.query.filter_by(uuid=user_uuid).first()

    # Serialization
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary representation"""
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'initials': self.get_initials(),
            'phone': self.phone,
            'timezone': self.timezone,
            'is_active': self.is_active,
            'is_premium': self.is_premium,
            'is_verified': self.is_verified,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }

        if include_sensitive:
            data.update({
                'failed_login_attempts': self.failed_login_attempts,
                'account_locked_until': self.account_locked_until.isoformat() if self.account_locked_until else None,
                'last_login_ip': self.last_login_ip,
                'force_password_change': self.force_password_change,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None
            })

        return data

    def __repr__(self):
        return f'<User {self.email}>'