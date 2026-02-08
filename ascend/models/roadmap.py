"""
Roadmap Model for ASCEND Application

This module defines the Roadmap model which represents personalized learning paths for students.
Roadmaps help students:
- Track their learning progress
- Set and achieve milestones
- Stay motivated with structured goals
"""

from database import db
from datetime import datetime
import json


class Roadmap(db.Model):
    """
    Roadmap model representing a student's learning path.
    
    Attributes:
        id (int): Primary key, unique roadmap identifier
        student_id (int): Foreign key to User (student)
        title (str): Roadmap title (e.g., "Python Mastery Path")
        description (str): Roadmap description/goals
        milestones (str): JSON string of milestones with progress
        progress (int): Overall progress percentage (0-100)
        target_date (datetime): Target completion date
        is_active (bool): Whether this roadmap is currently active
        created_at (datetime): Roadmap creation timestamp
        updated_at (datetime): Last update timestamp
    
    Relationships:
        student: Student who owns this roadmap
    
    Milestone Structure (JSON):
        [
            {
                "id": 1,
                "title": "Learn Python Basics",
                "description": "Variables, loops, functions",
                "completed": true,
                "completed_at": "2024-01-15T10:30:00"
            },
            {
                "id": 2,
                "title": "Build First Project",
                "description": "Create a simple calculator",
                "completed": false,
                "completed_at": null
            }
        ]
    """
    
    __tablename__ = 'roadmaps'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key to User (student)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), 
                          nullable=False, index=True)
    
    # Roadmap details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Milestones stored as JSON string
    milestones = db.Column(db.Text, nullable=False, default='[]')
    
    # Progress tracking
    progress = db.Column(db.Integer, default=0)  # 0-100 percentage
    target_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow)
    
    # Relationships
    # Student who owns this roadmap
    student = db.relationship('User', back_populates='roadmaps')
    
    def get_milestones(self):
        """
        Get milestones as a Python list.
        
        Returns:
            list: List of milestone dictionaries
            
        Usage:
            milestones = roadmap.get_milestones()
            for milestone in milestones:
                print(milestone['title'])
        """
        try:
            return json.loads(self.milestones)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_milestones(self, milestones_list):
        """
        Set milestones from a Python list.
        
        Args:
            milestones_list (list): List of milestone dictionaries
            
        Usage:
            roadmap.set_milestones([
                {"id": 1, "title": "Learn Basics", "completed": False}
            ])
        """
        self.milestones = json.dumps(milestones_list)
        self.calculate_progress()
    
    def add_milestone(self, title, description=""):
        """
        Add a new milestone to the roadmap.
        
        Args:
            title (str): Milestone title
            description (str): Milestone description
            
        Usage:
            roadmap.add_milestone("Complete Python Course", "Finish all modules")
            db.session.commit()
        """
        milestones = self.get_milestones()
        new_id = max([m.get('id', 0) for m in milestones], default=0) + 1
        
        new_milestone = {
            'id': new_id,
            'title': title,
            'description': description,
            'completed': False,
            'completed_at': None
        }
        
        milestones.append(new_milestone)
        self.set_milestones(milestones)
        self.updated_at = datetime.utcnow()
    
    def complete_milestone(self, milestone_id):
        """
        Mark a milestone as completed.
        
        Args:
            milestone_id (int): ID of the milestone to complete
            
        Returns:
            bool: True if milestone was found and completed, False otherwise
            
        Usage:
            if roadmap.complete_milestone(1):
                db.session.commit()
        """
        milestones = self.get_milestones()
        
        for milestone in milestones:
            if milestone.get('id') == milestone_id:
                milestone['completed'] = True
                milestone['completed_at'] = datetime.utcnow().isoformat()
                self.set_milestones(milestones)
                self.updated_at = datetime.utcnow()
                return True
        
        return False
    
    def uncomplete_milestone(self, milestone_id):
        """
        Mark a milestone as not completed.
        
        Args:
            milestone_id (int): ID of the milestone to uncomplete
            
        Returns:
            bool: True if milestone was found and uncompleted, False otherwise
        """
        milestones = self.get_milestones()
        
        for milestone in milestones:
            if milestone.get('id') == milestone_id:
                milestone['completed'] = False
                milestone['completed_at'] = None
                self.set_milestones(milestones)
                self.updated_at = datetime.utcnow()
                return True
        
        return False
    
    def calculate_progress(self):
        """
        Calculate overall progress based on completed milestones.
        
        Updates the progress field (0-100 percentage).
        
        Usage:
            roadmap.calculate_progress()
            print(f"Progress: {roadmap.progress}%")
        """
        milestones = self.get_milestones()
        
        if not milestones:
            self.progress = 0
            return
        
        completed = sum(1 for m in milestones if m.get('completed', False))
        self.progress = int((completed / len(milestones)) * 100)
    
    def is_completed(self):
        """Check if all milestones are completed."""
        return self.progress == 100
    
    def deactivate(self):
        """Deactivate this roadmap."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self):
        """Activate this roadmap."""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def to_dict(self, include_student=False):
        """
        Convert roadmap object to dictionary for JSON serialization.
        
        Args:
            include_student (bool): Whether to include student info
            
        Returns:
            dict: Roadmap data as dictionary
            
        Usage:
            roadmap_data = roadmap.to_dict()
            return jsonify(roadmap_data)
        """
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'milestones': self.get_milestones(),
            'progress': self.progress,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'is_active': self.is_active,
            'is_completed': self.is_completed(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_student and self.student:
            data['student'] = {
                'id': self.student.id,
                'username': self.student.username,
                'full_name': self.student.full_name
            }
        
        return data
    
    def __repr__(self):
        """String representation of Roadmap object."""
        return f'<Roadmap {self.id}: {self.title} ({self.progress}% complete)>'
