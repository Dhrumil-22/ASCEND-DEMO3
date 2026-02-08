"""
Queue Service for ASCEND Application

This module manages the question queue system for mentors:
- Fetch questions from queue based on mentor expertise
- Prioritize questions by urgency and age
- Distribute questions fairly among mentors
- Track queue metrics

Queue prioritization factors:
- Question priority level (1-5)
- Question age (older questions get higher priority)
- Mentor expertise match
- Mentor trust score
"""

from database import db
from models.question import Question
from models.user import User
from datetime import datetime, timedelta
from sqlalchemy import and_, or_


def get_questions_for_mentor(mentor_id, category=None, limit=20):
    """
    Get questions from the queue for a specific mentor.
    
    Questions are filtered and prioritized based on:
    1. Mentor's expertise areas
    2. Question priority level
    3. Question age (older = higher priority)
    4. Questions not yet answered
    
    Args:
        mentor_id (int): ID of the mentor
        category (str): Optional category filter
        limit (int): Maximum number of questions to return
    
    Returns:
        list: List of Question objects sorted by priority
        
    Usage:
        questions = get_questions_for_mentor(mentor_id=5, limit=10)
        for question in questions:
            print(f"{question.title} (Priority: {question.priority})")
    """
    # Get mentor's expertise
    mentor = User.query.get(mentor_id)
    if not mentor or not mentor.is_mentor():
        return []
    
    expertise_areas = mentor.get_expertise_list()
    
    # Base query: Get open questions
    query = Question.query.filter_by(status='open')
    
    # Filter by category if specified
    if category:
        query = query.filter_by(category=category)
    # Otherwise, filter by mentor's expertise
    elif expertise_areas:
        # Create OR conditions for each expertise area
        expertise_filters = [
            Question.category.like(f'%{area}%') for area in expertise_areas
        ]
        query = query.filter(or_(*expertise_filters))
    
    # Sort by priority (descending) and age (older first)
    query = query.order_by(
        Question.priority.desc(),
        Question.created_at.asc()
    )
    
    # Limit results
    questions = query.limit(limit).all()
    
    return questions


def prioritize_questions():
    """
    Recalculate priority for all open questions based on age.
    
    Priority boost rules:
    - Questions older than 7 days: +1 priority
    - Questions older than 14 days: +2 priority
    - Maximum priority: 5
    
    This should be run periodically (e.g., daily cron job).
    
    Returns:
        int: Number of questions updated
        
    Usage:
        updated_count = prioritize_questions()
        print(f"Updated {updated_count} questions")
    """
    now = datetime.utcnow()
    updated_count = 0
    
    # Get all open questions
    open_questions = Question.query.filter_by(status='open').all()
    
    for question in open_questions:
        age_days = (now - question.created_at).days
        original_priority = question.priority
        
        # Calculate new priority based on age
        if age_days >= 14:
            question.priority = min(5, original_priority + 2)
        elif age_days >= 7:
            question.priority = min(5, original_priority + 1)
        
        # Track if priority changed
        if question.priority != original_priority:
            updated_count += 1
    
    # Commit changes
    if updated_count > 0:
        db.session.commit()
    
    return updated_count


def get_queue_stats():
    """
    Get statistics about the question queue.
    
    Returns:
        dict: Queue statistics including counts by status and category
        
    Usage:
        stats = get_queue_stats()
        print(f"Open questions: {stats['open_questions']}")
    """
    # Count questions by status
    open_count = Question.query.filter_by(status='open').count()
    answered_count = Question.query.filter_by(status='answered').count()
    resolved_count = Question.query.filter_by(status='resolved').count()
    closed_count = Question.query.filter_by(status='closed').count()
    
    # Get oldest unanswered question
    oldest_open = Question.query.filter_by(status='open')\
        .order_by(Question.created_at.asc())\
        .first()
    
    # Calculate average wait time for answered questions
    answered_questions = Question.query.filter_by(status='answered').all()
    if answered_questions:
        total_wait_time = sum([
            (q.updated_at - q.created_at).total_seconds() / 3600  # in hours
            for q in answered_questions
        ])
        avg_wait_time = total_wait_time / len(answered_questions)
    else:
        avg_wait_time = 0
    
    # Count by category
    from sqlalchemy import func
    category_counts = db.session.query(
        Question.category,
        func.count(Question.id)
    ).filter_by(status='open')\
     .group_by(Question.category)\
     .all()
    
    stats = {
        'open_questions': open_count,
        'answered_questions': answered_count,
        'resolved_questions': resolved_count,
        'closed_questions': closed_count,
        'total_questions': open_count + answered_count + resolved_count + closed_count,
        'oldest_open_question_age_days': (
            (datetime.utcnow() - oldest_open.created_at).days
            if oldest_open else 0
        ),
        'average_wait_time_hours': round(avg_wait_time, 2),
        'questions_by_category': {
            category: count for category, count in category_counts
        }
    }
    
    return stats


def get_urgent_questions(limit=10):
    """
    Get the most urgent questions that need immediate attention.
    
    Urgency criteria:
    - High priority (4-5)
    - Old age (>7 days)
    - No responses yet
    
    Args:
        limit (int): Maximum number of questions to return
    
    Returns:
        list: List of urgent Question objects
        
    Usage:
        urgent = get_urgent_questions(limit=5)
        # Send notifications to mentors
    """
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    # Get open questions with high priority or old age
    urgent_questions = Question.query.filter(
        and_(
            Question.status == 'open',
            or_(
                Question.priority >= 4,
                Question.created_at <= seven_days_ago
            )
        )
    ).order_by(
        Question.priority.desc(),
        Question.created_at.asc()
    ).limit(limit).all()
    
    return urgent_questions


def assign_question_to_mentor(question_id, mentor_id):
    """
    Assign a specific question to a mentor (future feature).
    
    This is a placeholder for implementing question assignment.
    Could be used for:
    - Manual assignment by admins
    - Automatic assignment based on expertise
    - Load balancing among mentors
    
    Args:
        question_id (int): ID of the question
        mentor_id (int): ID of the mentor
    
    Returns:
        bool: True if assignment successful, False otherwise
        
    Note:
        This requires adding an 'assigned_to' field to the Question model.
    """
    # Placeholder implementation
    # In production, you would:
    # 1. Add 'assigned_to' field to Question model
    # 2. Verify mentor expertise matches question
    # 3. Update question with assignment
    # 4. Send notification to mentor
    
    question = Question.query.get(question_id)
    mentor = User.query.get(mentor_id)
    
    if not question or not mentor or not mentor.is_mentor():
        return False
    
    # Future: question.assigned_to = mentor_id
    # db.session.commit()
    
    return True


def get_mentor_queue_load(mentor_id):
    """
    Get the current queue load for a mentor.
    
    This helps with load balancing and showing mentors their workload.
    
    Args:
        mentor_id (int): ID of the mentor
    
    Returns:
        dict: Queue load statistics for the mentor
        
    Usage:
        load = get_mentor_queue_load(mentor_id=5)
        print(f"Available questions: {load['available_questions']}")
    """
    mentor = User.query.get(mentor_id)
    if not mentor or not mentor.is_mentor():
        return {}
    
    # Get questions available to this mentor
    available_questions = get_questions_for_mentor(mentor_id, limit=100)
    
    # Get mentor's response statistics
    from models.mentor_response import MentorResponse
    total_responses = MentorResponse.query.filter_by(mentor_id=mentor_id).count()
    
    # Get responses in last 7 days
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_responses = MentorResponse.query.filter(
        and_(
            MentorResponse.mentor_id == mentor_id,
            MentorResponse.created_at >= seven_days_ago
        )
    ).count()
    
    load = {
        'available_questions': len(available_questions),
        'total_responses_given': total_responses,
        'responses_last_7_days': recent_responses,
        'expertise_areas': mentor.get_expertise_list()
    }
    
    return load
