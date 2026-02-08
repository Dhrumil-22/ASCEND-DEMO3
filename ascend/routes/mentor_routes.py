"""
Mentor Routes for ASCEND Application

This module defines mentor-specific routes using Flask Blueprints:
- View questions from the queue
- Respond to student questions
- View response history
- Check trust score and performance metrics

All routes use the '/mentor' prefix and require mentor authentication.
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from database import db
from models.question import Question
from models.mentor_response import MentorResponse
from services.queue_service import get_questions_for_mentor


# Create Blueprint for mentor routes
# URL prefix: /mentor
mentor_bp = Blueprint('mentor', __name__, url_prefix='/mentor')


def mentor_required(f):
    """
    Decorator to require mentor role.
    
    Usage:
        @mentor_bp.route('/endpoint')
        @login_required
        @mentor_required
        def endpoint():
            ...
    """
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_mentor():
            return jsonify({'error': 'Mentor access required'}), 403
        return f(*args, **kwargs)
    
    return decorated_function


@mentor_bp.route('/queue', methods=['GET'])
@login_required
@mentor_required
def get_queue():
    """
    Get questions from the mentor queue.
    
    Questions are filtered and prioritized based on:
    - Mentor's expertise
    - Question priority
    - Question age
    - Mentor's trust score
    
    Query Parameters:
        category: Filter by specific category
        limit: Maximum number of questions (default: 20)
    
    Returns:
        JSON: List of questions from queue
    """
    category = request.args.get('category')
    limit = request.args.get('limit', 20, type=int)
    
    # Get questions from queue service
    questions = get_questions_for_mentor(
        mentor_id=current_user.id,
        category=category,
        limit=limit
    )
    
    return jsonify({
        'questions': [q.to_dict(include_student=True) for q in questions],
        'count': len(questions)
    }), 200


@mentor_bp.route('/respond/<int:question_id>', methods=['POST'])
@login_required
@mentor_required
def respond_to_question(question_id):
    """
    Respond to a student question.
    
    Request JSON:
        {
            "response_text": "Here's my answer..."
        }
    
    Returns:
        JSON: Created response data
    """
    question = Question.query.get_or_404(question_id)
    
    # Check if question is still open
    if not question.is_open():
        return jsonify({'error': 'Question is no longer open'}), 400
    
    data = request.get_json()
    
    # Validate response text
    if not data or not data.get('response_text'):
        return jsonify({'error': 'Response text is required'}), 400
    
    # Create mentor response
    response = MentorResponse(
        question_id=question_id,
        mentor_id=current_user.id,
        response_text=data['response_text']
    )
    
    # Mark question as answered
    question.mark_as_answered()
    
    # Increment mentor's response count
    if current_user.trust_score:
        current_user.trust_score.increment_response_count()
    
    # Save to database
    db.session.add(response)
    db.session.commit()
    
    return jsonify({
        'message': 'Response submitted successfully',
        'response': response.to_dict(include_question=True)
    }), 201


@mentor_bp.route('/responses', methods=['GET'])
@login_required
@mentor_required
def get_responses():
    """
    Get all responses given by the current mentor.
    
    Query Parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 20)
    
    Returns:
        JSON: List of responses with pagination
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Paginate responses
    pagination = MentorResponse.query.filter_by(mentor_id=current_user.id)\
        .order_by(MentorResponse.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'responses': [r.to_dict(include_question=True) for r in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200


@mentor_bp.route('/responses/<int:response_id>', methods=['PUT'])
@login_required
@mentor_required
def edit_response(response_id):
    """
    Edit a mentor response.
    
    Request JSON:
        {
            "response_text": "Updated answer..."
        }
    
    Returns:
        JSON: Updated response data
    """
    response = MentorResponse.query.get_or_404(response_id)
    
    # Verify ownership
    if response.mentor_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    if not data or not data.get('response_text'):
        return jsonify({'error': 'Response text is required'}), 400
    
    # Update response
    response.edit_response(data['response_text'])
    db.session.commit()
    
    return jsonify({
        'message': 'Response updated successfully',
        'response': response.to_dict()
    }), 200


@mentor_bp.route('/responses/<int:response_id>', methods=['DELETE'])
@login_required
@mentor_required
def delete_response(response_id):
    """
    Delete a mentor response.
    
    Returns:
        JSON: Success message
    """
    response = MentorResponse.query.get_or_404(response_id)
    
    # Verify ownership
    if response.mentor_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Don't allow deletion if marked as helpful
    if response.is_helpful:
        return jsonify({'error': 'Cannot delete helpful responses'}), 400
    
    db.session.delete(response)
    db.session.commit()
    
    return jsonify({'message': 'Response deleted successfully'}), 200


@mentor_bp.route('/trust-score', methods=['GET'])
@login_required
@mentor_required
def get_trust_score():
    """
    Get the current mentor's trust score and performance metrics.
    
    Returns:
        JSON: Trust score data with detailed metrics
    """
    if not current_user.trust_score:
        return jsonify({'error': 'Trust score not found'}), 404
    
    return jsonify({
        'trust_score': current_user.trust_score.to_dict()
    }), 200


@mentor_bp.route('/stats', methods=['GET'])
@login_required
@mentor_required
def get_stats():
    """
    Get mentor statistics and performance overview.
    
    Returns:
        JSON: Comprehensive mentor statistics
    """
    # Get response statistics
    total_responses = MentorResponse.query.filter_by(mentor_id=current_user.id).count()
    helpful_responses = MentorResponse.query.filter_by(
        mentor_id=current_user.id, 
        is_helpful=True
    ).count()
    
    # Get recent activity
    recent_responses = MentorResponse.query.filter_by(mentor_id=current_user.id)\
        .order_by(MentorResponse.created_at.desc())\
        .limit(5)\
        .all()
    
    stats = {
        'total_responses': total_responses,
        'helpful_responses': helpful_responses,
        'trust_score': current_user.trust_score.to_dict() if current_user.trust_score else None,
        'recent_activity': [r.to_dict(include_question=True) for r in recent_responses]
    }
    
    return jsonify(stats), 200


@mentor_bp.route('/expertise', methods=['PUT'])
@login_required
@mentor_required
def update_expertise():
    """
    Update mentor's areas of expertise.
    
    Request JSON:
        {
            "expertise": ["Python", "Machine Learning", "Data Science"]
        }
    
    Returns:
        JSON: Updated mentor data
    """
    data = request.get_json()
    
    if not data or 'expertise' not in data:
        return jsonify({'error': 'Expertise list is required'}), 400
    
    if not isinstance(data['expertise'], list):
        return jsonify({'error': 'Expertise must be a list'}), 400
    
    # Update expertise
    current_user.set_expertise_list(data['expertise'])
    db.session.commit()
    
    return jsonify({
        'message': 'Expertise updated successfully',
        'mentor': current_user.to_dict()
    }), 200
