"""
Configuration Module for ASCEND Application

This module contains configuration classes for different environments:
- DevelopmentConfig: Settings for local development
- ProductionConfig: Settings for production deployment
- TestingConfig: Settings for running tests

Each configuration class inherits from the base Config class and can be
selected using the FLASK_ENV environment variable.
"""

import os
from datetime import timedelta


class Config:
    """
    Base configuration class with common settings.
    
    All environment-specific configurations inherit from this class.
    Contains default values that can be overridden in child classes.
    """
    
    # Secret key for session management and CSRF protection
    # In production, this should be set via environment variable
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking to save resources
    SQLALCHEMY_ECHO = False  # Set to True to log all SQL queries (useful for debugging)
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # Session expires after 7 days
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    
    # Flask-Login settings
    REMEMBER_COOKIE_DURATION = timedelta(days=30)  # "Remember me" cookie duration
    REMEMBER_COOKIE_SECURE = False  # Set to True in production with HTTPS
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Pagination settings
    QUESTIONS_PER_PAGE = 20
    USERS_PER_PAGE = 50
    
    # Trust score settings
    INITIAL_TRUST_SCORE = 50  # Starting trust score for new mentors
    MAX_TRUST_SCORE = 100
    MIN_TRUST_SCORE = 0


class DevelopmentConfig(Config):
    """
    Development environment configuration.
    
    Uses SQLite database for easy local development.
    Enables debug mode and detailed error messages.
    """
    
    DEBUG = True
    TESTING = False
    
    # SQLite database for development (stored in current directory)
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'ascend_dev.db')
    
    SQLALCHEMY_ECHO = True  # Log SQL queries in development


class ProductionConfig(Config):
    """
    Production environment configuration.
    
    Uses PostgreSQL/MySQL database (configured via environment variable).
    Disables debug mode and enforces secure cookie settings.
    """
    
    DEBUG = False
    TESTING = False
    
    # Database URI must be set via environment variable in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///ascend_prod.db'  # Fallback (not recommended for production)
    
    # Enforce secure cookies in production
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    
    def __init__(self):
        """Validate production configuration on initialization."""
        super().__init__()
        # Require SECRET_KEY to be set in production
        if not os.environ.get('SECRET_KEY'):
            import warnings
            warnings.warn(
                "SECRET_KEY environment variable is not set! Using default key. "
                "This is insecure for production!",
                UserWarning
            )


class TestingConfig(Config):
    """
    Testing environment configuration.
    
    Uses in-memory SQLite database for fast test execution.
    Disables CSRF protection for easier testing.
    """
    
    DEBUG = False
    TESTING = True
    
    # In-memory SQLite database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF protection in tests
    WTF_CSRF_ENABLED = False
    
    # Faster password hashing for tests
    BCRYPT_LOG_ROUNDS = 4


# Configuration dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
