"""
Database Module for ASCEND Application

This module handles SQLAlchemy initialization and database operations.
It provides:
- SQLAlchemy instance (db) for use across the application
- Database initialization function
- Helper functions for database operations

Usage:
    from database import db
    
    # In models:
    class User(db.Model):
        ...
    
    # In app.py:
    db.init_app(app)
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    
    This provides a declarative base that all models will inherit from.
    It enables type hints and better IDE support for SQLAlchemy models.
    """
    pass


# Initialize SQLAlchemy with the custom base class
# This db instance will be imported and used throughout the application
db = SQLAlchemy(model_class=Base)


def init_db(app):
    """
    Initialize the database with the Flask application.
    
    This function:
    1. Binds the SQLAlchemy instance to the Flask app
    2. Creates all database tables if they don't exist
    3. Sets up the application context for database operations
    
    Args:
        app: Flask application instance
        
    Usage:
        app = create_app()
        init_db(app)
    """
    # Bind SQLAlchemy to the Flask app
    db.init_app(app)
    
    # Create all tables within application context
    with app.app_context():
        # Import all models here to ensure they're registered with SQLAlchemy
        # This must be done before create_all() is called
        from models.user import User
        from models.question import Question
        from models.mentor_response import MentorResponse
        from models.roadmap import Roadmap
        from models.trust_score import TrustScore
        
        # Create all tables defined in models
        db.create_all()
        
        print("✓ Database tables created successfully")


def drop_all_tables(app):
    """
    Drop all database tables.
    
    WARNING: This will delete all data in the database!
    Use only for development/testing purposes.
    
    Args:
        app: Flask application instance
        
    Usage:
        drop_all_tables(app)  # Use with caution!
    """
    with app.app_context():
        db.drop_all()
        print("✓ All database tables dropped")


def reset_database(app):
    """
    Reset the database by dropping and recreating all tables.
    
    WARNING: This will delete all data in the database!
    Use only for development/testing purposes.
    
    Args:
        app: Flask application instance
        
    Usage:
        reset_database(app)  # Use with caution!
    """
    with app.app_context():
        db.drop_all()
        print("✓ Dropped all tables")
        
        # Import models
        from models.user import User
        from models.question import Question
        from models.mentor_response import MentorResponse
        from models.roadmap import Roadmap
        from models.trust_score import TrustScore
        
        db.create_all()
        print("✓ Database reset complete")


def seed_database(app):
    """
    Seed the database with sample data for development/testing.
    
    This function creates:
    - Sample users (students, mentors, admin)
    - Sample questions
    - Sample mentor responses
    - Sample trust scores
    
    Args:
        app: Flask application instance
        
    Usage:
        seed_database(app)
    """
    with app.app_context():
        from models.user import User
        from models.question import Question
        from models.mentor_response import MentorResponse
        from models.trust_score import TrustScore
        
        # Check if database is already seeded
        if User.query.first() is not None:
            print("⚠ Database already contains data. Skipping seed.")
            return
        
        # Create sample users
        admin = User(
            username='admin',
            email='admin@ascend.com',
            role='admin'
        )
        admin.set_password('admin123')
        
        student = User(
            username='john_student',
            email='john@example.com',
            role='student'
        )
        student.set_password('student123')
        
        mentor = User(
            username='jane_mentor',
            email='jane@example.com',
            role='mentor'
        )
        mentor.set_password('mentor123')
        
        # Add users to session
        db.session.add_all([admin, student, mentor])
        db.session.commit()
        
        print("✓ Database seeded with sample data")
