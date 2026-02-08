"""
Trust Score Model for ASCEND Application

This module defines the TrustScore model which tracks mentor reliability and quality.
Trust scores are used to:
- Rank mentors in recommendations
- Prioritize high-quality mentors in the queue
- Provide feedback to mentors on their performance

Trust score calculation factors:
- Number of responses given
- Percentage of helpful responses
- Response time
- Student satisfaction ratings
"""

from database import db
from datetime import datetime


class TrustScore(db.Model):
    """
    TrustScore model representing a mentor's reliability score.
    
    This is a one-to-one relationship with User (mentor role).
    Each mentor has exactly one trust score that evolves over time.
    
    Attributes:
        id (int): Primary key, unique trust score identifier
        mentor_id (int): Foreign key to User (mentor) - unique
        score (int): Current trust score (0-100)
        total_responses (int): Total number of responses given
        helpful_count (int): Number of responses marked as helpful
        not_helpful_count (int): Number of responses marked as not helpful
        average_response_time (float): Average time to respond (in hours)
        last_calculated (datetime): When score was last recalculated
        created_at (datetime): Trust score creation timestamp
        updated_at (datetime): Last update timestamp
    
    Relationships:
        mentor: Mentor user this score belongs to
    
    Score Calculation:
    - Base score: 50 (starting point for new mentors)
    - Helpful response: +2 points
    - Not helpful response: -3 points
    - Fast response (< 24h): +1 point
    - Slow response (> 72h): -1 point
    - Minimum score: 0
    - Maximum score: 100
    """
    
    __tablename__ = 'trust_scores'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key to User (mentor) - unique constraint for one-to-one relationship
    mentor_id = db.Column(db.Integer, db.ForeignKey('users.id'), 
                         unique=True, nullable=False, index=True)
    
    # Score metrics
    score = db.Column(db.Integer, default=50, nullable=False)  # 0-100
    total_responses = db.Column(db.Integer, default=0)
    helpful_count = db.Column(db.Integer, default=0)
    not_helpful_count = db.Column(db.Integer, default=0)
    
    # Performance metrics
    average_response_time = db.Column(db.Float, default=0.0)  # in hours
    
    # Timestamps
    last_calculated = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow)
    
    # Relationships
    # Mentor user this score belongs to
    mentor = db.relationship('User', back_populates='trust_score')
    
    def get_helpfulness_rate(self):
        """
        Calculate the percentage of helpful responses.
        
        Returns:
            float: Helpfulness rate (0.0 to 1.0)
            
        Usage:
            rate = trust_score.get_helpfulness_rate()
            print(f"Helpfulness: {rate * 100:.1f}%")
        """
        if self.total_responses == 0:
            return 0.0
        
        rated_responses = self.helpful_count + self.not_helpful_count
        if rated_responses == 0:
            return 0.5  # Neutral if no ratings yet
        
        return self.helpful_count / rated_responses
    
    def increment_response_count(self):
        """
        Increment the total response count.
        
        Called when a mentor submits a new response.
        
        Usage:
            trust_score.increment_response_count()
            db.session.commit()
        """
        self.total_responses += 1
        self.updated_at = datetime.utcnow()
    
    def record_helpful_feedback(self):
        """
        Record a helpful feedback.
        
        Increases helpful_count and recalculates score.
        
        Usage:
            trust_score.record_helpful_feedback()
            db.session.commit()
        """
        self.helpful_count += 1
        self.recalculate_score()
        self.updated_at = datetime.utcnow()
    
    def record_not_helpful_feedback(self):
        """
        Record a not helpful feedback.
        
        Increases not_helpful_count and recalculates score.
        
        Usage:
            trust_score.record_not_helpful_feedback()
            db.session.commit()
        """
        self.not_helpful_count += 1
        self.recalculate_score()
        self.updated_at = datetime.utcnow()
    
    def recalculate_score(self):
        """
        Recalculate the trust score based on current metrics.
        
        Score calculation:
        - Start with base score (50)
        - Add points for helpful responses
        - Subtract points for not helpful responses
        - Adjust based on response time
        - Clamp between 0 and 100
        
        Usage:
            trust_score.recalculate_score()
            db.session.commit()
        """
        # Start with base score
        base_score = 50
        
        # Calculate score based on helpfulness
        helpful_points = self.helpful_count * 2
        not_helpful_points = self.not_helpful_count * 3
        
        # Calculate final score
        new_score = base_score + helpful_points - not_helpful_points
        
        # Bonus for high helpfulness rate (if enough responses)
        if self.total_responses >= 10:
            helpfulness_rate = self.get_helpfulness_rate()
            if helpfulness_rate > 0.8:
                new_score += 10  # Bonus for excellent mentors
            elif helpfulness_rate < 0.3:
                new_score -= 10  # Penalty for poor performance
        
        # Clamp score between 0 and 100
        self.score = max(0, min(100, new_score))
        self.last_calculated = datetime.utcnow()
    
    def get_rank(self):
        """
        Get mentor rank based on trust score.
        
        Returns:
            str: Rank name ('Novice', 'Intermediate', 'Advanced', 'Expert', 'Master')
            
        Usage:
            rank = trust_score.get_rank()
            print(f"Mentor Rank: {rank}")
        """
        if self.score >= 90:
            return 'Master'
        elif self.score >= 75:
            return 'Expert'
        elif self.score >= 60:
            return 'Advanced'
        elif self.score >= 40:
            return 'Intermediate'
        else:
            return 'Novice'
    
    def to_dict(self, include_mentor=False):
        """
        Convert trust score object to dictionary for JSON serialization.
        
        Args:
            include_mentor (bool): Whether to include mentor info
            
        Returns:
            dict: Trust score data as dictionary
            
        Usage:
            score_data = trust_score.to_dict()
            return jsonify(score_data)
        """
        data = {
            'id': self.id,
            'score': self.score,
            'rank': self.get_rank(),
            'total_responses': self.total_responses,
            'helpful_count': self.helpful_count,
            'not_helpful_count': self.not_helpful_count,
            'helpfulness_rate': round(self.get_helpfulness_rate() * 100, 1),
            'average_response_time': round(self.average_response_time, 2),
            'last_calculated': self.last_calculated.isoformat() if self.last_calculated else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_mentor and self.mentor:
            data['mentor'] = {
                'id': self.mentor.id,
                'username': self.mentor.username,
                'full_name': self.mentor.full_name,
                'expertise': self.mentor.get_expertise_list()
            }
        
        return data
    
    def __repr__(self):
        """String representation of TrustScore object."""
        return f'<TrustScore {self.score} ({self.get_rank()}) for Mentor {self.mentor_id}>'
