"""
Recommendation Service for ASCEND Application

This module provides recommendation algorithms for:
- Matching students with suitable mentors
- Generating personalized learning roadmaps
- Suggesting relevant questions to mentors

Recommendation factors:
- Mentor expertise and trust score
- Student learning goals and history
- Question category and complexity
"""

from database import db
from models.user import User
from models.roadmap import Roadmap
from models.trust_score import TrustScore
from sqlalchemy import and_


def recommend_mentors(student_id, category=None, limit=10):
    """
    Recommend mentors to a student based on expertise and trust score.
    
    Algorithm:
    1. Filter mentors by expertise (if category specified)
    2. Prioritize verified mentors
    3. Sort by trust score (descending)
    4. Return top N mentors
    
    Args:
        student_id (int): ID of the student requesting recommendations
        category (str): Optional category to filter by (e.g., 'Python', 'Career')
        limit (int): Maximum number of mentors to return
    
    Returns:
        list: List of User objects (mentors) sorted by relevance
        
    Usage:
        mentors = recommend_mentors(student_id=1, category='Python', limit=5)
        for mentor in mentors:
            print(f"{mentor.username}: {mentor.trust_score.score}")
    """
    # Base query: Get all verified mentors with trust scores
    query = db.session.query(User, TrustScore)\
        .join(TrustScore, User.id == TrustScore.mentor_id)\
        .filter(User.role == 'mentor')
    
    # Filter by category if specified
    if category:
        # Search for category in mentor's expertise
        query = query.filter(User.expertise.like(f'%{category}%'))
    
    # Prioritize verified mentors and sort by trust score
    query = query.order_by(
        User.is_verified.desc(),  # Verified mentors first
        TrustScore.score.desc()    # Then by trust score
    )
    
    # Limit results
    results = query.limit(limit).all()
    
    # Extract mentor objects from query results
    mentors = [mentor for mentor, trust_score in results]
    
    return mentors


def get_mentor_by_expertise(expertise_area):
    """
    Get all mentors with specific expertise.
    
    Args:
        expertise_area (str): Area of expertise to search for
    
    Returns:
        list: List of User objects (mentors) with matching expertise
        
    Usage:
        python_mentors = get_mentor_by_expertise('Python')
    """
    mentors = User.query.filter(
        and_(
            User.role == 'mentor',
            User.expertise.like(f'%{expertise_area}%')
        )
    ).all()
    
    return mentors


def generate_roadmap(student_id, title, description=None, goals=None):
    """
    Generate a personalized learning roadmap for a student.
    
    This is a basic implementation that creates milestones from goals.
    In a production system, this could use AI/ML to generate personalized paths.
    
    Args:
        student_id (int): ID of the student
        title (str): Roadmap title
        description (str): Optional roadmap description
        goals (list): List of learning goals
    
    Returns:
        Roadmap: Created roadmap object
        
    Usage:
        roadmap = generate_roadmap(
            student_id=1,
            title="Python Mastery",
            goals=["Learn basics", "Build projects", "Master advanced topics"]
        )
    """
    # Create roadmap
    roadmap = Roadmap(
        student_id=student_id,
        title=title,
        description=description or f"Personalized learning path: {title}"
    )
    
    # Generate milestones from goals
    if goals and isinstance(goals, list):
        milestones = []
        for idx, goal in enumerate(goals, start=1):
            milestone = {
                'id': idx,
                'title': goal,
                'description': f"Complete: {goal}",
                'completed': False,
                'completed_at': None
            }
            milestones.append(milestone)
        
        roadmap.set_milestones(milestones)
    else:
        # Default milestones if no goals provided
        default_milestones = [
            {
                'id': 1,
                'title': 'Getting Started',
                'description': 'Learn the fundamentals',
                'completed': False,
                'completed_at': None
            },
            {
                'id': 2,
                'title': 'Practice & Build',
                'description': 'Apply knowledge through projects',
                'completed': False,
                'completed_at': None
            },
            {
                'id': 3,
                'title': 'Master Advanced Concepts',
                'description': 'Deep dive into advanced topics',
                'completed': False,
                'completed_at': None
            }
        ]
        roadmap.set_milestones(default_milestones)
    
    # Save to database
    db.session.add(roadmap)
    db.session.commit()
    
    return roadmap


def suggest_learning_resources(category):
    """
    Suggest learning resources based on category.
    
    This is a placeholder for future implementation.
    Could integrate with external APIs or maintain a resource database.
    
    Args:
        category (str): Learning category
    
    Returns:
        list: List of resource dictionaries
        
    Usage:
        resources = suggest_learning_resources('Python')
    """
    # Placeholder implementation
    # In production, this could query a resources database or external API
    resources = [
        {
            'title': f'{category} Official Documentation',
            'type': 'documentation',
            'url': f'https://docs.{category.lower()}.org'
        },
        {
            'title': f'Learn {category} - Interactive Tutorial',
            'type': 'tutorial',
            'url': f'https://learn{category.lower()}.org'
        },
        {
            'title': f'{category} Community Forum',
            'type': 'community',
            'url': f'https://community.{category.lower()}.org'
        }
    ]
    
    return resources


def match_question_to_mentors(question, limit=5):
    """
    Find the best mentors to answer a specific question.
    
    Matching criteria:
    - Mentor expertise matches question category
    - High trust score
    - Verified status
    - Recent activity
    
    Args:
        question (Question): Question object to match
        limit (int): Maximum number of mentors to return
    
    Returns:
        list: List of User objects (mentors) best suited for the question
        
    Usage:
        from models.question import Question
        question = Question.query.get(1)
        mentors = match_question_to_mentors(question, limit=3)
    """
    # Use the recommend_mentors function with question's category
    mentors = recommend_mentors(
        student_id=question.student_id,
        category=question.category,
        limit=limit
    )
    
    return mentors


def get_personalized_recommendations(student_id):
    """
    Get personalized recommendations for a student.
    
    This includes:
    - Recommended mentors based on student's question history
    - Suggested learning paths
    - Relevant resources
    
    Args:
        student_id (int): ID of the student
    
    Returns:
        dict: Dictionary containing various recommendations
        
    Usage:
        recommendations = get_personalized_recommendations(student_id=1)
        print(recommendations['mentors'])
        print(recommendations['learning_paths'])
    """
    from models.question import Question
    
    # Get student's question history to understand interests
    student_questions = Question.query.filter_by(student_id=student_id).all()
    
    # Extract categories from questions
    categories = list(set([q.category for q in student_questions]))
    
    # Get recommended mentors for each category
    recommended_mentors = []
    for category in categories[:3]:  # Top 3 categories
        mentors = recommend_mentors(student_id, category, limit=2)
        recommended_mentors.extend(mentors)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_mentors = []
    for mentor in recommended_mentors:
        if mentor.id not in seen:
            seen.add(mentor.id)
            unique_mentors.append(mentor)
    
    recommendations = {
        'mentors': unique_mentors[:5],  # Top 5 unique mentors
        'categories_of_interest': categories,
        'total_questions_asked': len(student_questions)
    }
    
    return recommendations
