"""
Mentor Response Model for ASCEND Application

This module defines the MentorResponse model which represents mentor answers to student questions.
Responses are used to:
- Provide guidance to students
- Calculate mentor trust scores
- Track mentor activity and expertise
"""

from database import db
from datetime import datetime


class MentorResponse(db.Model):
    """
    MentorResponse model representing mentor answers to questions.
    
    Attributes:
        id (int): Primary key, unique response identifier
        question_id (int): Foreign key to Question
        mentor_id (int): Foreign key to User (mentor)
        response_text (str): The mentor's answer/guidance
        is_helpful (bool): Whether student marked this as helpful
        upvotes (int): Number of upvotes from students
        created_at (datetime): Response creation timestamp
        updated_at (datetime): Last edit timestamp
    
    Relationships:
        question: Question this response answers
        mentor: Mentor who provided this response
    """
    
    __tablename__ = 'mentor_responses'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), 
                           nullable=False, index=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('users.id'), 
                         nullable=False, index=True)
    
    # Response content
    response_text = db.Column(db.Text, nullable=False)
    
    # Feedback metrics
    is_helpful = db.Column(db.Boolean, default=None)  # None = not rated yet
    upvotes = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow)
    
    # Relationships
    # Question this response answers
    question = db.relationship('Question', back_populates='responses')
    
    # Mentor who provided this response
    mentor = db.relationship('User', back_populates='mentor_responses')
    
    def mark_helpful(self):
        """
        Mark this response as helpful.
        
        This is typically called when a student finds the response useful.
        Updates the mentor's trust score.
        
        Usage:
            response.mark_helpful()
            db.session.commit()
        """
        self.is_helpful = True
        self.updated_at = datetime.utcnow()
        
        # Update mentor's trust score
        if self.mentor.trust_score:
            from services.trust_service import update_trust_score
            update_trust_score(self.mentor_id, helpful=True)
    
    def mark_not_helpful(self):
        """
        Mark this response as not helpful.
        
        This may negatively impact the mentor's trust score.
        
        Usage:
            response.mark_not_helpful()
            db.session.commit()
        """
        self.is_helpful = False
        self.updated_at = datetime.utcnow()
        
        # Update mentor's trust score
        if self.mentor.trust_score:
            from services.trust_service import update_trust_score
            update_trust_score(self.mentor_id, helpful=False)
    
    def add_upvote(self):
        """
        Add an upvote to this response.
        
        Upvotes indicate quality and can influence mentor rankings.
        
        Usage:
            response.add_upvote()
            db.session.commit()
        """
        self.upvotes += 1
        self.updated_at = datetime.utcnow()
    
    def edit_response(self, new_text):
        """
        Edit the response text.
        
        Args:
            new_text (str): Updated response text
            
        Usage:
            response.edit_response("Updated answer with more details...")
            db.session.commit()
        """
        self.response_text = new_text
        self.updated_at = datetime.utcnow()
    
    def to_dict(self, include_question=False, include_mentor=True):
        """
        Convert response object to dictionary for JSON serialization.
        
        Args:
            include_question (bool): Whether to include question details
            include_mentor (bool): Whether to include mentor info
            
        Returns:
            dict: Response data as dictionary
            
        Usage:
            response_data = response.to_dict()
            return jsonify(response_data)
        """
        data = {
            'id': self.id,
            'question_id': self.question_id,
            'response_text': self.response_text,
            'is_helpful': self.is_helpful,
            'upvotes': self.upvotes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_mentor and self.mentor:
            data['mentor'] = {
                'id': self.mentor.id,
                'username': self.mentor.username,
                'full_name': self.mentor.full_name,
                'expertise': self.mentor.get_expertise_list(),
                'trust_score': self.mentor.trust_score.score if self.mentor.trust_score else None
            }
        
        if include_question and self.question:
            data['question'] = {
                'id': self.question.id,
                'title': self.question.title,
                'category': self.question.category
            }
        
        return data
    
    def __repr__(self):
        """String representation of MentorResponse object."""
        return f'<MentorResponse {self.id} by Mentor {self.mentor_id} for Question {self.question_id}>'
