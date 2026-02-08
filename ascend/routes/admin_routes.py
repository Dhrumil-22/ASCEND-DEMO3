"""
Admin Routes for ASCEND Application

This module defines admin-specific routes using Flask Blueprints:
- User management (list, verify, delete users)
- Mentor verification
- Platform analytics
- Content moderation

All routes use the '/admin' prefix and require admin authentication.
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from database import db
from models.user import User
from models.question import Question
from models.mentor_response import MentorResponse
from models.trust_score import TrustScore


# Create Blueprint for admin routes
# URL prefix: /admin
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """
    Decorator to require admin role.
    
    Usage:
        @admin_bp.route('/endpoint')
        @login_required
        @admin_required
        def endpoint():
            ...
    """
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    
    return decorated_function


@admin_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def get_users():
    """
    Get all users with filtering and pagination.
    
    Query Parameters:
        role: Filter by role ('student', 'mentor', 'admin')
        verified: Filter mentors by verification status (true/false)
        page: Page number (default: 1)
        per_page: Items per page (default: 50)
    
    Returns:
        JSON: List of users with pagination
    """
    role = request.args.get('role')
    verified = request.args.get('verified')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    # Build query
    query = User.query
    
    if role:
        query = query.filter_by(role=role)
    
    if verified is not None:
        is_verified = verified.lower() == 'true'
        query = query.filter_by(is_verified=is_verified)
    
    # Paginate results
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'users': [u.to_dict(include_email=True) for u in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@login_required
@admin_required
def get_user(user_id):
    """
    Get detailed information about a specific user.
    
    Returns:
        JSON: User data with additional details
    """
    user = User.query.get_or_404(user_id)
    
    user_data = user.to_dict(include_email=True)
    
    # Add role-specific data
    if user.is_student():
        user_data['question_count'] = user.questions.count()
        user_data['roadmap_count'] = user.roadmaps.count()
    
    if user.is_mentor():
        user_data['response_count'] = user.mentor_responses.count()
        if user.trust_score:
            user_data['trust_score_details'] = user.trust_score.to_dict()
    
    return jsonify({'user': user_data}), 200


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    """
    Delete a user account.
    
    WARNING: This will cascade delete all related data!
    
    Returns:
        JSON: Success message
    """
    user = User.query.get_or_404(user_id)
    
    # Prevent self-deletion
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({
        'message': f'User {username} deleted successfully'
    }), 200


@admin_bp.route('/verify-mentor/<int:mentor_id>', methods=['POST'])
@login_required
@admin_required
def verify_mentor(mentor_id):
    """
    Verify a mentor account.
    
    Verified mentors get priority in recommendations and queue.
    
    Returns:
        JSON: Updated mentor data
    """
    mentor = User.query.get_or_404(mentor_id)
    
    # Check if user is a mentor
    if not mentor.is_mentor():
        return jsonify({'error': 'User is not a mentor'}), 400
    
    # Verify mentor
    mentor.is_verified = True
    
    # Create trust score if doesn't exist
    if not mentor.trust_score:
        trust_score = TrustScore(mentor_id=mentor.id)
        db.session.add(trust_score)
    
    db.session.commit()
    
    return jsonify({
        'message': f'Mentor {mentor.username} verified successfully',
        'mentor': mentor.to_dict()
    }), 200


@admin_bp.route('/unverify-mentor/<int:mentor_id>', methods=['POST'])
@login_required
@admin_required
def unverify_mentor(mentor_id):
    """
    Unverify a mentor account.
    
    Returns:
        JSON: Updated mentor data
    """
    mentor = User.query.get_or_404(mentor_id)
    
    if not mentor.is_mentor():
        return jsonify({'error': 'User is not a mentor'}), 400
    
    mentor.is_verified = False
    db.session.commit()
    
    return jsonify({
        'message': f'Mentor {mentor.username} unverified',
        'mentor': mentor.to_dict()
    }), 200


@admin_bp.route('/analytics', methods=['GET'])
@login_required
@admin_required
def get_analytics():
    """
    Get platform analytics and statistics.
    
    Returns:
        JSON: Comprehensive platform statistics
    """
    # User statistics
    total_users = User.query.count()
    total_students = User.query.filter_by(role='student').count()
    total_mentors = User.query.filter_by(role='mentor').count()
    verified_mentors = User.query.filter_by(role='mentor', is_verified=True).count()
    
    # Question statistics
    total_questions = Question.query.count()
    open_questions = Question.query.filter_by(status='open').count()
    answered_questions = Question.query.filter_by(status='answered').count()
    resolved_questions = Question.query.filter_by(status='resolved').count()
    
    # Response statistics
    total_responses = MentorResponse.query.count()
    helpful_responses = MentorResponse.query.filter_by(is_helpful=True).count()
    
    # Top mentors by trust score
    top_mentors = db.session.query(User, TrustScore)\
        .join(TrustScore, User.id == TrustScore.mentor_id)\
        .order_by(TrustScore.score.desc())\
        .limit(10)\
        .all()
    
    analytics = {
        'users': {
            'total': total_users,
            'students': total_students,
            'mentors': total_mentors,
            'verified_mentors': verified_mentors
        },
        'questions': {
            'total': total_questions,
            'open': open_questions,
            'answered': answered_questions,
            'resolved': resolved_questions
        },
        'responses': {
            'total': total_responses,
            'helpful': helpful_responses,
            'helpfulness_rate': round((helpful_responses / total_responses * 100), 2) if total_responses > 0 else 0
        },
        'top_mentors': [
            {
                'mentor': mentor.to_dict(),
                'trust_score': trust_score.to_dict()
            }
            for mentor, trust_score in top_mentors
        ]
    }
    
    return jsonify(analytics), 200


@admin_bp.route('/moderate/<int:question_id>', methods=['POST'])
@login_required
@admin_required
def moderate_question(question_id):
    """
    Moderate a question (close or delete).
    
    Request JSON:
        {
            "action": "close"  # or "delete"
        }
    
    Returns:
        JSON: Success message
    """
    question = Question.query.get_or_404(question_id)
    
    data = request.get_json()
    action = data.get('action')
    
    if action == 'close':
        question.close()
        db.session.commit()
        return jsonify({'message': 'Question closed'}), 200
    
    elif action == 'delete':
        db.session.delete(question)
        db.session.commit()
        return jsonify({'message': 'Question deleted'}), 200
    
    else:
        return jsonify({'error': 'Invalid action. Use "close" or "delete"'}), 400


@admin_bp.route('/moderate/response/<int:response_id>', methods=['DELETE'])
@login_required
@admin_required
def moderate_response(response_id):
    """
    Delete an inappropriate mentor response.
    
    Returns:
        JSON: Success message
    """
    response = MentorResponse.query.get_or_404(response_id)
    
    db.session.delete(response)
    db.session.commit()
    
    return jsonify({'message': 'Response deleted'}), 200


@admin_bp.route('/change-role/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def change_user_role(user_id):
    """
    Change a user's role.
    
    Request JSON:
        {
            "role": "mentor"  # 'student', 'mentor', or 'admin'
        }
    
    Returns:
        JSON: Updated user data
    """
    user = User.query.get_or_404(user_id)
    
    data = request.get_json()
    new_role = data.get('role')
    
    if new_role not in ['student', 'mentor', 'admin']:
        return jsonify({'error': 'Invalid role'}), 400
    
    # Prevent changing own role
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot change your own role'}), 400
    
    old_role = user.role
    user.role = new_role
    
    # Create trust score if changing to mentor
    if new_role == 'mentor' and not user.trust_score:
        trust_score = TrustScore(mentor_id=user.id)
        db.session.add(trust_score)
    
    db.session.commit()
    
    return jsonify({
        'message': f'User role changed from {old_role} to {new_role}',
        'user': user.to_dict()
    }), 200
