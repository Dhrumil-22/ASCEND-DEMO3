"""
User Model for ASCEND Application

This module defines the User model which represents all users in the system:
- Students: Ask questions and receive mentorship
- Mentors: Answer questions and provide guidance
- Admins: Manage the platform and verify mentors

The User model integrates with Flask-Login for authentication and session management.
"""

from database import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(UserMixin, db.Model):
    """
    User model for authentication and user management.
    
    Inherits from UserMixin to provide Flask-Login integration:
    - is_authenticated: Returns True if user is logged in
    - is_active: Returns True if user account is active
    - is_anonymous: Returns False for regular users
    - get_id(): Returns unique user identifier
    
    Attributes:
        id (int): Primary key, unique user identifier
        username (str): Unique username for login
        email (str): Unique email address
        password_hash (str): Hashed password (never store plain passwords!)
        role (str): User role - 'student', 'mentor', or 'admin'
        full_name (str): User's full name (optional)
        bio (str): User biography/description (optional)
        expertise (str): Mentor's areas of expertise (comma-separated)
        is_verified (bool): Whether mentor is verified by admin
        created_at (datetime): Account creation timestamp
        updated_at (datetime): Last profile update timestamp
    
    Relationships:
        questions: Questions asked by this user (if student)
        mentor_responses: Responses given by this user (if mentor)
        roadmaps: Learning roadmaps for this user (if student)
        trust_score: Trust score for this user (if mentor)
    """
    
    __tablename__ = 'users'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Authentication fields
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # User role: 'student', 'mentor', or 'admin'
    role = db.Column(db.String(20), nullable=False, default='student', index=True)
    
    # Profile fields
    full_name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    expertise = db.Column(db.String(255))  # Comma-separated areas of expertise
    
    # Verification status (for mentors)
    is_verified = db.Column(db.Boolean, default=False, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # Questions asked by this user (for students)
    questions = db.relationship('Question', back_populates='student', 
                               foreign_keys='Question.student_id',
                               lazy='dynamic', cascade='all, delete-orphan')
    
    # Responses given by this user (for mentors)
    mentor_responses = db.relationship('MentorResponse', back_populates='mentor',
                                      lazy='dynamic', cascade='all, delete-orphan')
    
    # Roadmaps for this user (for students)
    roadmaps = db.relationship('Roadmap', back_populates='student',
                              lazy='dynamic', cascade='all, delete-orphan')
    
    # Trust score for this user (for mentors) - one-to-one relationship
    trust_score = db.relationship('TrustScore', back_populates='mentor',
                                 uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """
        Hash and store the user's password.
        
        Uses Werkzeug's security functions to generate a secure password hash.
        The hash includes a salt to prevent rainbow table attacks.
        
        Args:
            password (str): Plain text password to hash
            
        Usage:
            user = User(username='john', email='john@example.com')
            user.set_password('secure_password_123')
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Verify a password against the stored hash.
        
        Args:
            password (str): Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
            
        Usage:
            if user.check_password('entered_password'):
                # Password is correct
                login_user(user)
        """
        return check_password_hash(self.password_hash, password)
    
    def is_student(self):
        """Check if user is a student."""
        return self.role == 'student'
    
    def is_mentor(self):
        """Check if user is a mentor."""
        return self.role == 'mentor'
    
    def is_admin(self):
        """Check if user is an admin."""
        return self.role == 'admin'
    
    def get_expertise_list(self):
        """
        Get mentor's expertise as a list.
        
        Returns:
            list: List of expertise areas, or empty list if none
            
        Usage:
            expertise = mentor.get_expertise_list()
            # ['Python', 'Machine Learning', 'Data Science']
        """
        if self.expertise:
            return [e.strip() for e in self.expertise.split(',')]
        return []
    
    def set_expertise_list(self, expertise_list):
        """
        Set mentor's expertise from a list.
        
        Args:
            expertise_list (list): List of expertise areas
            
        Usage:
            mentor.set_expertise_list(['Python', 'Machine Learning'])
        """
        self.expertise = ', '.join(expertise_list)
    
    def to_dict(self, include_email=False):
        """
        Convert user object to dictionary for JSON serialization.
        
        Args:
            include_email (bool): Whether to include email (for privacy)
            
        Returns:
            dict: User data as dictionary
            
        Usage:
            user_data = user.to_dict()
            return jsonify(user_data)
        """
        data = {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'full_name': self.full_name,
            'bio': self.bio,
            'expertise': self.get_expertise_list(),
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_email:
            data['email'] = self.email
        
        # Include trust score for mentors
        if self.is_mentor() and self.trust_score:
            data['trust_score'] = self.trust_score.score
        
        return data
    
    def __repr__(self):
        """String representation of User object."""
        return f'<User {self.username} ({self.role})>'
