"""
Authentication Routes for ASCEND Application

This module defines authentication-related routes using Flask Blueprints:
- User registration
- User login
- User logout
- Profile management

All routes use the '/auth' prefix when registered in the main app.
"""

from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from database import db
from models.user import User
from models.trust_score import TrustScore


# Create Blueprint for authentication routes
# URL prefix: /auth
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Students register normally with full access.
    Mentors register with is_verified=False (requires admin approval).
    Admin accounts cannot be created via this endpoint (manual creation only).
    
    Request JSON:
        {
            "username": "john_doe",
            "email": "john@example.com",
            "password": "secure_password",
            "role": "student",  # Optional: 'student' or 'mentor' (NOT 'admin')
            "full_name": "John Doe"  # Optional
        }
    
    Returns:
        JSON: User data and success message
        
    Status Codes:
        201: User created successfully
        400: Invalid input or user already exists
        403: Attempt to create admin account
    """
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Username, email, and password are required'}), 400
    
    # Prevent admin account creation via API
    role = data.get('role', 'student')
    if role == 'admin':
        return jsonify({
            'error': 'Admin accounts cannot be created via registration',
            'message': 'Admin accounts must be created manually by system administrators'
        }), 403
    
    # Validate role
    if role not in ['student', 'mentor']:
        return jsonify({'error': 'Invalid role. Must be "student" or "mentor"'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        role=role,
        full_name=data.get('full_name')
    )
    
    # Hash and set password (NEVER store plain text!)
    user.set_password(data['password'])
    
    # Mentors require admin approval before they can answer questions
    if user.is_mentor():
        user.is_verified = False  # Explicitly set to False for mentors
    
    # Add user to database
    db.session.add(user)
    db.session.commit()
    
    # If user is a mentor, create trust score with initial value
    if user.is_mentor():
        trust_score = TrustScore(mentor_id=user.id)
        db.session.add(trust_score)
        db.session.commit()
    
    # Prepare response message
    response_data = {
        'message': 'User registered successfully',
        'user': user.to_dict()
    }
    
    # Add note for mentors about verification
    if user.is_mentor():
        response_data['note'] = 'Your mentor account requires admin approval before you can answer questions'
    
    return jsonify(response_data), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Log in an existing user.
    
    Request JSON:
        {
            "username": "john_doe",  # Or email
            "password": "secure_password",
            "remember": true  # Optional: remember user session
        }
    
    Returns:
        JSON: User data and success message
        
    Status Codes:
        200: Login successful
        401: Invalid credentials
    """
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400
    
    # Find user by username or email
    user = User.query.filter(
        (User.username == data['username']) | (User.email == data['username'])
    ).first()
    
    # Verify user exists and password is correct
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # Log in user
    remember = data.get('remember', False)
    login_user(user, remember=remember)
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(include_email=True)
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    Log out the current user.
    
    Requires authentication.
    
    Returns:
        JSON: Success message
        
    Status Codes:
        200: Logout successful
        401: Not authenticated
    """
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """
    Get current user's profile.
    
    Requires authentication.
    
    Returns:
        JSON: User profile data
        
    Status Codes:
        200: Profile retrieved successfully
        401: Not authenticated
    """
    return jsonify({
        'user': current_user.to_dict(include_email=True)
    }), 200


@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """
    Update current user's profile.
    
    Requires authentication.
    
    Request JSON:
        {
            "full_name": "John Doe",  # Optional
            "bio": "Passionate learner",  # Optional
            "expertise": ["Python", "Machine Learning"]  # Optional (mentors only)
        }
    
    Returns:
        JSON: Updated user data
        
    Status Codes:
        200: Profile updated successfully
        400: Invalid input
        401: Not authenticated
    """
    data = request.get_json()
    
    # Update allowed fields
    if 'full_name' in data:
        current_user.full_name = data['full_name']
    
    if 'bio' in data:
        current_user.bio = data['bio']
    
    # Only mentors can update expertise
    if 'expertise' in data and current_user.is_mentor():
        if isinstance(data['expertise'], list):
            current_user.set_expertise_list(data['expertise'])
        else:
            return jsonify({'error': 'Expertise must be a list'}), 400
    
    # Save changes
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': current_user.to_dict(include_email=True)
    }), 200


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """
    Change current user's password.
    
    Requires authentication.
    
    Request JSON:
        {
            "current_password": "old_password",
            "new_password": "new_secure_password"
        }
    
    Returns:
        JSON: Success message
        
    Status Codes:
        200: Password changed successfully
        400: Invalid input
        401: Current password incorrect
    """
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Current and new password are required'}), 400
    
    # Verify current password
    if not current_user.check_password(data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    # Set new password
    current_user.set_password(data['new_password'])
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'}), 200
