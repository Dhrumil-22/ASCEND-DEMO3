"""
Main Application File for ASCEND

This module implements the Flask application factory pattern.
It creates and configures the Flask app, initializes extensions,
and registers all blueprints.

Usage:
    # Development
    python app.py
    
    # Production (with gunicorn)
    gunicorn -w 4 -b 0.0.0.0:5000 app:app
"""

import os
from flask import Flask, jsonify
from flask_login import LoginManager
from flask_cors import CORS
from config import config
from database import db, init_db


# Initialize Flask-Login
login_manager = LoginManager()


def create_app(config_name=None):
    """
    Application factory function.
    
    Creates and configures a Flask application instance.
    
    Args:
        config_name (str): Configuration name ('development', 'production', 'testing')
                          If None, uses FLASK_ENV environment variable
    
    Returns:
        Flask: Configured Flask application instance
        
    Usage:
        app = create_app('development')
        app.run()
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    initialize_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Create database tables
    init_db(app)
    
    return app


def initialize_extensions(app):
    """
    Initialize Flask extensions.
    
    This function initializes:
    - Flask-Login (authentication)
    - Flask-CORS (cross-origin requests)
    
    Note: SQLAlchemy is initialized in init_db() function
    
    Args:
        app (Flask): Flask application instance
    """
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Redirect to login if not authenticated
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Initialize CORS (allow cross-origin requests)
    CORS(app, supports_credentials=True)
    
    # Set up user loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        """
        Load user by ID for Flask-Login.
        
        This callback is used to reload the user object from the user ID
        stored in the session.
        
        Args:
            user_id (str): User ID from session
        
        Returns:
            User: User object or None if not found
        """
        from models.user import User
        return User.query.get(int(user_id))


def register_blueprints(app):
    """
    Register all application blueprints.
    
    Blueprints organize routes into modular components:
    - auth_bp: Authentication routes (/auth)
    - student_bp: Student routes (/student)
    - mentor_bp: Mentor routes (/mentor)
    - admin_bp: Admin routes (/admin)
    
    Args:
        app (Flask): Flask application instance
    """
    from routes.auth_routes import auth_bp
    from routes.student_routes import student_bp
    from routes.mentor_routes import mentor_bp
    from routes.admin_routes import admin_bp
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(mentor_bp)
    app.register_blueprint(admin_bp)
    
    # Register root route
    @app.route('/')
    def index():
        """
        Root endpoint - API information.
        
        Returns:
            JSON: API welcome message and available endpoints
        """
        return jsonify({
            'message': 'Welcome to ASCEND API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/auth',
                'student': '/student',
                'mentor': '/mentor',
                'admin': '/admin'
            },
            'documentation': '/docs'  # Future: Add API documentation
        }), 200
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """
        Health check endpoint for monitoring.
        
        Returns:
            JSON: Application health status
        """
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        }), 200


def register_error_handlers(app):
    """
    Register error handlers for common HTTP errors.
    
    Provides consistent JSON error responses.
    
    Args:
        app (Flask): Flask application instance
    """
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors."""
        return jsonify({
            'error': 'Resource not found',
            'message': str(error)
        }), 404
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors."""
        return jsonify({
            'error': 'Bad request',
            'message': str(error)
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized errors."""
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden errors."""
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource'
        }), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors."""
        # Rollback database session on error
        db.session.rollback()
        
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500


# Create application instance
app = create_app()


if __name__ == '__main__':
    """
    Run the application in development mode.
    
    This should only be used for development.
    For production, use a WSGI server like gunicorn.
    """
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run app in debug mode for development
    app.run(
        host='0.0.0.0',  # Listen on all interfaces
        port=port,
        debug=True  # Enable debug mode (auto-reload, detailed errors)
    )
