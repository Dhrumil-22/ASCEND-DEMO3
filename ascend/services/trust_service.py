"""
Trust Service for ASCEND Application

This module manages mentor trust scores:
- Calculate trust scores based on performance metrics
- Update scores based on student feedback
- Implement score decay for inactive mentors
- Provide trust score analytics

Trust score factors:
- Response helpfulness rate
- Total number of responses
- Response time
- Student satisfaction
- Activity level
"""

from database import db
from models.trust_score import TrustScore
from models.mentor_response import MentorResponse
from models.user import User
from datetime import datetime, timedelta


def calculate_trust_score(mentor_id):
    """
    Calculate and update a mentor's trust score.
    
    This recalculates the score from scratch based on all available data.
    
    Args:
        mentor_id (int): ID of the mentor
    
    Returns:
        TrustScore: Updated trust score object, or None if mentor not found
        
    Usage:
        trust_score = calculate_trust_score(mentor_id=5)
        print(f"New score: {trust_score.score}")
    """
    # Get mentor and trust score
    mentor = User.query.get(mentor_id)
    if not mentor or not mentor.is_mentor():
        return None
    
    trust_score = mentor.trust_score
    if not trust_score:
        # Create trust score if doesn't exist
        trust_score = TrustScore(mentor_id=mentor_id)
        db.session.add(trust_score)
    
    # Get all mentor responses
    responses = MentorResponse.query.filter_by(mentor_id=mentor_id).all()
    
    # Update response counts
    trust_score.total_responses = len(responses)
    trust_score.helpful_count = sum(1 for r in responses if r.is_helpful is True)
    trust_score.not_helpful_count = sum(1 for r in responses if r.is_helpful is False)
    
    # Calculate average response time (placeholder - requires timestamp tracking)
    # In production, track when question was asked vs when mentor responded
    trust_score.average_response_time = 24.0  # Default 24 hours
    
    # Recalculate score using TrustScore model's method
    trust_score.recalculate_score()
    
    # Commit changes
    db.session.commit()
    
    return trust_score


def update_trust_score(mentor_id, helpful=True):
    """
    Update trust score based on student feedback.
    
    This is called when a student marks a response as helpful/not helpful.
    
    Args:
        mentor_id (int): ID of the mentor
        helpful (bool): True if response was helpful, False otherwise
    
    Returns:
        TrustScore: Updated trust score object
        
    Usage:
        # Student marks response as helpful
        update_trust_score(mentor_id=5, helpful=True)
        
        # Student marks response as not helpful
        update_trust_score(mentor_id=5, helpful=False)
    """
    trust_score = TrustScore.query.filter_by(mentor_id=mentor_id).first()
    
    if not trust_score:
        # Create trust score if doesn't exist
        trust_score = TrustScore(mentor_id=mentor_id)
        db.session.add(trust_score)
    
    # Update feedback counts
    if helpful:
        trust_score.record_helpful_feedback()
    else:
        trust_score.record_not_helpful_feedback()
    
    # Commit changes
    db.session.commit()
    
    return trust_score


def apply_trust_score_decay():
    """
    Apply decay to trust scores of inactive mentors.
    
    Mentors who haven't responded in a while get a small score penalty.
    This encourages active participation.
    
    Decay rules:
    - No responses in 30 days: -5 points
    - No responses in 60 days: -10 points
    - No responses in 90 days: -15 points
    
    This should be run periodically (e.g., weekly cron job).
    
    Returns:
        int: Number of trust scores updated
        
    Usage:
        updated_count = apply_trust_score_decay()
        print(f"Applied decay to {updated_count} mentors")
    """
    now = datetime.utcnow()
    updated_count = 0
    
    # Get all trust scores
    trust_scores = TrustScore.query.all()
    
    for trust_score in trust_scores:
        # Get mentor's most recent response
        last_response = MentorResponse.query.filter_by(
            mentor_id=trust_score.mentor_id
        ).order_by(MentorResponse.created_at.desc()).first()
        
        if not last_response:
            continue
        
        # Calculate days since last response
        days_inactive = (now - last_response.created_at).days
        
        # Apply decay based on inactivity
        decay_amount = 0
        if days_inactive >= 90:
            decay_amount = 15
        elif days_inactive >= 60:
            decay_amount = 10
        elif days_inactive >= 30:
            decay_amount = 5
        
        if decay_amount > 0:
            # Apply decay (don't go below 0)
            trust_score.score = max(0, trust_score.score - decay_amount)
            trust_score.last_calculated = now
            updated_count += 1
    
    # Commit changes
    if updated_count > 0:
        db.session.commit()
    
    return updated_count


def get_top_mentors(limit=10):
    """
    Get the top mentors by trust score.
    
    Args:
        limit (int): Maximum number of mentors to return
    
    Returns:
        list: List of tuples (User, TrustScore) sorted by score
        
    Usage:
        top_mentors = get_top_mentors(limit=5)
        for mentor, score in top_mentors:
            print(f"{mentor.username}: {score.score} ({score.get_rank()})")
    """
    top_mentors = db.session.query(User, TrustScore)\
        .join(TrustScore, User.id == TrustScore.mentor_id)\
        .filter(User.role == 'mentor')\
        .order_by(TrustScore.score.desc())\
        .limit(limit)\
        .all()
    
    return top_mentors


def get_trust_score_analytics():
    """
    Get analytics about trust scores across the platform.
    
    Returns:
        dict: Trust score analytics and statistics
        
    Usage:
        analytics = get_trust_score_analytics()
        print(f"Average trust score: {analytics['average_score']}")
    """
    from sqlalchemy import func
    
    # Get all trust scores
    trust_scores = TrustScore.query.all()
    
    if not trust_scores:
        return {
            'total_mentors': 0,
            'average_score': 0,
            'median_score': 0,
            'score_distribution': {}
        }
    
    # Calculate statistics
    scores = [ts.score for ts in trust_scores]
    average_score = sum(scores) / len(scores)
    median_score = sorted(scores)[len(scores) // 2]
    
    # Score distribution by rank
    ranks = {}
    for ts in trust_scores:
        rank = ts.get_rank()
        ranks[rank] = ranks.get(rank, 0) + 1
    
    # Get mentor with highest/lowest scores
    highest_score_mentor = max(trust_scores, key=lambda ts: ts.score)
    lowest_score_mentor = min(trust_scores, key=lambda ts: ts.score)
    
    analytics = {
        'total_mentors': len(trust_scores),
        'average_score': round(average_score, 2),
        'median_score': median_score,
        'highest_score': highest_score_mentor.score,
        'lowest_score': lowest_score_mentor.score,
        'score_distribution': ranks,
        'total_responses': sum(ts.total_responses for ts in trust_scores),
        'total_helpful_responses': sum(ts.helpful_count for ts in trust_scores)
    }
    
    return analytics


def recalculate_all_trust_scores():
    """
    Recalculate trust scores for all mentors.
    
    This should be run periodically to ensure scores are accurate.
    Useful after changing the scoring algorithm.
    
    Returns:
        int: Number of trust scores recalculated
        
    Usage:
        count = recalculate_all_trust_scores()
        print(f"Recalculated {count} trust scores")
    """
    # Get all mentors
    mentors = User.query.filter_by(role='mentor').all()
    
    count = 0
    for mentor in mentors:
        calculate_trust_score(mentor.id)
        count += 1
    
    return count


def get_mentor_performance_report(mentor_id):
    """
    Generate a detailed performance report for a mentor.
    
    Args:
        mentor_id (int): ID of the mentor
    
    Returns:
        dict: Comprehensive performance report
        
    Usage:
        report = get_mentor_performance_report(mentor_id=5)
        print(f"Helpfulness rate: {report['helpfulness_rate']}%")
    """
    mentor = User.query.get(mentor_id)
    if not mentor or not mentor.is_mentor():
        return {}
    
    trust_score = mentor.trust_score
    if not trust_score:
        return {'error': 'Trust score not found'}
    
    # Get response statistics
    responses = MentorResponse.query.filter_by(mentor_id=mentor_id).all()
    
    # Calculate time-based statistics
    now = datetime.utcnow()
    last_30_days = now - timedelta(days=30)
    recent_responses = [r for r in responses if r.created_at >= last_30_days]
    
    report = {
        'mentor': mentor.to_dict(),
        'trust_score': trust_score.to_dict(),
        'all_time_stats': {
            'total_responses': len(responses),
            'helpful_responses': trust_score.helpful_count,
            'not_helpful_responses': trust_score.not_helpful_count,
            'helpfulness_rate': round(trust_score.get_helpfulness_rate() * 100, 2)
        },
        'last_30_days': {
            'responses': len(recent_responses),
            'helpful': sum(1 for r in recent_responses if r.is_helpful is True),
            'not_helpful': sum(1 for r in recent_responses if r.is_helpful is False)
        },
        'rank': trust_score.get_rank(),
        'score_history': {
            'current_score': trust_score.score,
            'last_calculated': trust_score.last_calculated.isoformat() if trust_score.last_calculated else None
        }
    }
    
    return report
