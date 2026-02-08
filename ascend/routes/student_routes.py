"""
Student Routes for ASCEND Application

This module defines student-specific routes using Flask Blueprints:
- Create and manage questions
- View question details and responses
- Get recommended mentors
- Manage learning roadmaps

All routes use the '/student' prefix and require student authentication.
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from database import db
from models.question import Question
from models.roadmap import Roadmap
from services.recommendation_service import recommend_mentors, generate_roadmap


# Create Blueprint for student routes
# URL prefix: /student
student_bp = Blueprint('student', __name__, url_prefix='/student')


def student_required(f):
    """
    Decorator to require student role.
    
    Usage:
        @student_bp.route('/endpoint')
        @login_required
        @student_required
        def endpoint():
            ...
    """
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_student():
            return jsonify({'error': 'Student access required'}), 403
        return f(*args, **kwargs)
    
    return decorated_function


@student_bp.route('/questions', methods=['GET'])
@login_required
@student_required
def get_questions():
    """
    Get all questions asked by the current student.
    
    Query Parameters:
        status: Filter by status ('open', 'answered', 'resolved', 'closed')
        page: Page number (default: 1)
        per_page: Items per page (default: 20)
    
    Returns:
        JSON: List of questions with pagination info
    """
    # Get query parameters
    status = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Build query
    query = Question.query.filter_by(student_id=current_user.id)
    
    if status:
        query = query.filter_by(status=status)
    
    # Paginate results
    pagination = query.order_by(Question.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'questions': [q.to_dict(include_responses=False) for q in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200


@student_bp.route('/questions', methods=['POST'])
@login_required
@student_required
def create_question():
    """
    Create a new question.
    
    Request JSON:
        {
            "title": "How do I learn Python?",
            "description": "I'm a beginner...",
            "category": "Python",
            "tags": ["beginner", "learning"],  # Optional
            "priority": 3  # Optional (1-5)
        }
    
    Returns:
        JSON: Created question data
    """
    data = request.get_json()
    
    # Validate required fields
    if not data or not data.get('title') or not data.get('description') or not data.get('category'):
        return jsonify({'error': 'Title, description, and category are required'}), 400
    
    # Create question
    question = Question(
        student_id=current_user.id,
        title=data['title'],
        description=data['description'],
        category=data['category'],
        priority=data.get('priority', 3)
    )
    
    # Set tags if provided
    if 'tags' in data and isinstance(data['tags'], list):
        question.set_tags_list(data['tags'])
    
    # Save to database
    db.session.add(question)
    db.session.commit()
    
    return jsonify({
        'message': 'Question created successfully',
        'question': question.to_dict()
    }), 201


@student_bp.route('/questions/<int:question_id>', methods=['GET'])
@login_required
@student_required
def get_question(question_id):
    """
    Get details of a specific question with all responses.
    
    Returns:
        JSON: Question data with responses
    """
    question = Question.query.get_or_404(question_id)
    
    # Verify ownership
    if question.student_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify({
        'question': question.to_dict(include_responses=True)
    }), 200


@student_bp.route('/questions/<int:question_id>', methods=['PUT'])
@login_required
@student_required
def update_question(question_id):
    """
    Update a question (only if not yet answered).
    
    Request JSON:
        {
            "title": "Updated title",  # Optional
            "description": "Updated description",  # Optional
            "status": "resolved"  # Optional
        }
    
    Returns:
        JSON: Updated question data
    """
    question = Question.query.get_or_404(question_id)
    
    # Verify ownership
    if question.student_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    # Update allowed fields
    if 'title' in data and question.is_open():
        question.title = data['title']
    
    if 'description' in data and question.is_open():
        question.description = data['description']
    
    if 'status' in data:
        if data['status'] == 'resolved':
            question.mark_as_resolved()
        elif data['status'] == 'closed':
            question.close()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Question updated successfully',
        'question': question.to_dict()
    }), 200


@student_bp.route('/questions/<int:question_id>', methods=['DELETE'])
@login_required
@student_required
def delete_question(question_id):
    """
    Delete a question (only if no responses yet).
    
    Returns:
        JSON: Success message
    """
    question = Question.query.get_or_404(question_id)
    
    # Verify ownership
    if question.student_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Only allow deletion if no responses
    if question.get_response_count() > 0:
        return jsonify({'error': 'Cannot delete question with responses'}), 400
    
    db.session.delete(question)
    db.session.commit()
    
    return jsonify({'message': 'Question deleted successfully'}), 200


@student_bp.route('/mentors', methods=['GET'])
@login_required
@student_required
def get_recommended_mentors():
    """
    Get recommended mentors based on category.
    
    Query Parameters:
        category: Category to filter mentors by
        limit: Maximum number of mentors to return (default: 10)
    
    Returns:
        JSON: List of recommended mentors
    """
    category = request.args.get('category')
    limit = request.args.get('limit', 10, type=int)
    
    mentors = recommend_mentors(current_user.id, category, limit)
    
    return jsonify({
        'mentors': [m.to_dict() for m in mentors]
    }), 200


@student_bp.route('/roadmap', methods=['GET'])
@login_required
@student_required
def get_roadmaps():
    """
    Get all roadmaps for the current student.
    
    Query Parameters:
        active_only: Only return active roadmaps (default: false)
    
    Returns:
        JSON: List of roadmaps
    """
    active_only = request.args.get('active_only', 'false').lower() == 'true'
    
    query = Roadmap.query.filter_by(student_id=current_user.id)
    
    if active_only:
        query = query.filter_by(is_active=True)
    
    roadmaps = query.order_by(Roadmap.created_at.desc()).all()
    
    return jsonify({
        'roadmaps': [r.to_dict() for r in roadmaps]
    }), 200


@student_bp.route('/roadmap', methods=['POST'])
@login_required
@student_required
def create_roadmap():
    """
    Create a new learning roadmap.
    
    Request JSON:
        {
            "title": "Python Mastery Path",
            "description": "Learn Python from basics to advanced",
            "goals": ["Learn basics", "Build projects", "Master advanced topics"]
        }
    
    Returns:
        JSON: Created roadmap data
    """
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    # Generate roadmap using AI service
    roadmap = generate_roadmap(
        student_id=current_user.id,
        title=data['title'],
        description=data.get('description'),
        goals=data.get('goals', [])
    )
    
    return jsonify({
        'message': 'Roadmap created successfully',
        'roadmap': roadmap.to_dict()
    }), 201


@student_bp.route('/roadmap/<int:roadmap_id>/milestone/<int:milestone_id>/complete', methods=['POST'])
@login_required
@student_required
def complete_milestone(roadmap_id, milestone_id):
    """
    Mark a milestone as completed.
    
    Returns:
        JSON: Updated roadmap data
    """
    roadmap = Roadmap.query.get_or_404(roadmap_id)
    
    # Verify ownership
    if roadmap.student_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    if roadmap.complete_milestone(milestone_id):
        db.session.commit()
        return jsonify({
            'message': 'Milestone completed',
            'roadmap': roadmap.to_dict()
        }), 200
    else:
        return jsonify({'error': 'Milestone not found'}), 404
