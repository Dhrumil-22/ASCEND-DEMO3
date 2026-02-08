"""
Question Model for ASCEND Application

This module defines the Question model which represents student questions
for career guidance and mentorship.

Question lifecycle:
1. Student submits structured question (status: 'open')
2. Question enters mentor queue based on skills/target_role
3. Mentor responds (status: 'answered')
4. Student can mark as resolved (status: 'resolved')
"""

from database import db
from datetime import datetime


class Question(db.Model):
    """
    Question model representing structured student queries.
    
    This model captures detailed information about a student's career question,
    including their skills, target role, and preparation level. This structured
    approach helps mentors provide more targeted and relevant guidance.
    
    Attributes:
        id (int): Primary key, unique question identifier
        student_id (int): Foreign key to User (student who asked)
        skills (str): Comma-separated list of student's current skills
        target_role (str): The role/position student is preparing for
        preparation_attempts (int): Number of times student has attempted preparation
        description (str): Detailed question description
        status (str): Question status - 'open', 'answered', 'resolved', 'closed'
        created_at (datetime): Question creation timestamp
        updated_at (datetime): Last update timestamp
    
    Relationships:
        student: User who asked this question (belongs to User)
        responses: Mentor responses to this question (has many MentorResponse)
    
    Status Flow:
        'open' → 'answered' → 'resolved' → 'closed'
    """
    
    __tablename__ = 'questions'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key to User (student)
    # This creates a "belongs to" relationship with User model
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), 
                          nullable=False, index=True)
    
    # Structured question fields
    skills = db.Column(db.String(500), nullable=False)
    """
    Student's current skills (comma-separated).
    Example: "Python, Django, REST APIs, PostgreSQL"
    This helps mentors understand the student's technical background.
    """
    
    target_role = db.Column(db.String(100), nullable=False, index=True)
    """
    The role/position student is preparing for.
    Example: "Backend Developer", "Data Scientist", "DevOps Engineer"
    Indexed for efficient filtering by role.
    """
    
    preparation_attempts = db.Column(db.Integer, default=0, nullable=False)
    """
    Number of times student has attempted preparation for this role.
    0 = First time, 1+ = Retrying after previous attempts
    Helps mentors gauge experience level and provide appropriate advice.
    """
    
    description = db.Column(db.Text, nullable=False)
    """
    Detailed question description.
    Should include:
    - Specific challenges faced
    - What has been tried so far
    - Expected outcome or guidance needed
    """
    
    # Status: 'open', 'answered', 'resolved', 'closed'
    status = db.Column(db.String(20), default='open', nullable=False, index=True)
    """
    Question status:
    - 'open': Waiting for mentor response
    - 'answered': Mentor has responded
    - 'resolved': Student marked as resolved
    - 'closed': Question closed (no more responses)
    """
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          nullable=False, index=True)
    """
    Question creation timestamp.
    Indexed for sorting by date and calculating question age.
    """
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow)
    """
    Last update timestamp.
    Automatically updated when question is modified.
    """
    
    # Relationships
    # Student who asked this question (belongs to User)
    student = db.relationship('User', back_populates='questions', 
                             foreign_keys=[student_id])
    """
    Belongs to relationship with User model.
    Allows accessing: question.student.username, question.student.email, etc.
    """
    
    # Mentor responses to this question (has many MentorResponse)
    responses = db.relationship('MentorResponse', back_populates='question',
                               lazy='dynamic', cascade='all, delete-orphan',
                               order_by='MentorResponse.created_at')
    """
    Has many relationship with MentorResponse model.
    Allows accessing: question.responses.all(), question.responses.count(), etc.
    Cascade delete ensures responses are deleted when question is deleted.
    """
    
    # Helper Methods
    
    def get_skills_list(self):
        """
        Get student's skills as a list.
        
        Returns:
            list: List of skills, or empty list if none
            
        Usage:
            skills = question.get_skills_list()
            # ['Python', 'Django', 'REST APIs', 'PostgreSQL']
        """
        if self.skills:
            return [skill.strip() for skill in self.skills.split(',')]
        return []
    
    def set_skills_list(self, skills_list):
        """
        Set student's skills from a list.
        
        Args:
            skills_list (list): List of skills
            
        Usage:
            question.set_skills_list(['Python', 'Django', 'REST APIs'])
        """
        self.skills = ', '.join(skills_list)
    
    def is_open(self):
        """
        Check if question is still open (waiting for response).
        
        Returns:
            bool: True if status is 'open', False otherwise
        """
        return self.status == 'open'
    
    def is_answered(self):
        """
        Check if question has been answered by a mentor.
        
        Returns:
            bool: True if status is 'answered' or 'resolved', False otherwise
        """
        return self.status in ['answered', 'resolved']
    
    def is_resolved(self):
        """
        Check if question has been marked as resolved by student.
        
        Returns:
            bool: True if status is 'resolved', False otherwise
        """
        return self.status == 'resolved'
    
    def mark_as_answered(self):
        """
        Mark question as answered (called when mentor responds).
        
        This is automatically called when a mentor submits a response.
        Updates status and timestamp.
        """
        self.status = 'answered'
        self.updated_at = datetime.utcnow()
    
    def mark_as_resolved(self):
        """
        Mark question as resolved (called by student).
        
        Student marks question as resolved when they're satisfied
        with the mentor's response.
        """
        self.status = 'resolved'
        self.updated_at = datetime.utcnow()
    
    def close(self):
        """
        Close question (no more responses accepted).
        
        Can be called by student or admin to prevent further responses.
        Useful for outdated or duplicate questions.
        """
        self.status = 'closed'
        self.updated_at = datetime.utcnow()
    
    def get_response_count(self):
        """
        Get the number of mentor responses to this question.
        
        Returns:
            int: Number of mentor responses
            
        Usage:
            count = question.get_response_count()
            print(f"This question has {count} responses")
        """
        return self.responses.count()
    
    def get_age_in_days(self):
        """
        Get the age of the question in days.
        
        Returns:
            int: Number of days since question was created
            
        Usage:
            age = question.get_age_in_days()
            if age > 7:
                print("Question is over a week old")
        """
        if self.created_at:
            delta = datetime.utcnow() - self.created_at
            return delta.days
        return 0
    
    def to_dict(self, include_student=True, include_responses=False):
        """
        Convert question object to dictionary for JSON serialization.
        
        Args:
            include_student (bool): Whether to include student info
            include_responses (bool): Whether to include all responses
            
        Returns:
            dict: Question data as dictionary
            
        Usage:
            question_data = question.to_dict(include_responses=True)
            return jsonify(question_data)
        """
        data = {
            'id': self.id,
            'student_id': self.student_id,
            'skills': self.get_skills_list(),
            'target_role': self.target_role,
            'preparation_attempts': self.preparation_attempts,
            'description': self.description,
            'status': self.status,
            'response_count': self.get_response_count(),
            'age_days': self.get_age_in_days(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Include student information if requested
        if include_student and self.student:
            data['student'] = {
                'id': self.student.id,
                'username': self.student.username,
                'full_name': self.student.full_name
            }
        
        # Include all responses if requested
        if include_responses:
            data['responses'] = [response.to_dict() for response in self.responses]
        
        return data
    
    def __repr__(self):
        """String representation of Question object."""
        return f'<Question {self.id}: {self.target_role} - {self.status}>'
