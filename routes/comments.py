from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Comment, Recipe, User
from utils import sanitize_html, validate_comment_content, paginate_results, standardize_error, standardize_response

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/<int:recipe_id>', methods=['GET'])
def get_comments(recipe_id):
    """Get paginated comments for a recipe"""
    # Verify recipe exists
    recipe = Recipe.query.get_or_404(recipe_id)
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Query comments
    query = Comment.query.filter_by(recipe_id=recipe_id).order_by(Comment.created_at.desc())
    
    # Paginate
    result = paginate_results(query, page, per_page)
    
    if result is None:
        return standardize_error('Invalid pagination parameters', 400)
    
    # Convert to dict
    result['items'] = [comment.to_dict() for comment in result['items']]
    
    return standardize_response(result)

@comments_bp.route('/<int:recipe_id>', methods=['POST'])
@jwt_required()
def create_comment(recipe_id):
    """Create a new comment on a recipe"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return standardize_error('Request body is required', 400)
    
    # Validate content
    is_valid, result = validate_comment_content(data.get('content'))
    if not is_valid:
        return standardize_error(result, 400)
    
    # Verify recipe exists
    recipe = Recipe.query.get_or_404(recipe_id)
    
    # Sanitize content
    sanitized_content = sanitize_html(result)
    
    # Create comment
    comment = Comment(
        content=sanitized_content,
        user_id=user_id,
        recipe_id=recipe_id
    )
    
    try:
        db.session.add(comment)
        db.session.commit()
        return standardize_response(comment.to_dict(), 'Comment created successfully', 201)
    except Exception as e:
        db.session.rollback()
        return standardize_error('Failed to create comment', 500)

@comments_bp.route('/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id):
    """Update a comment (user can only update their own comments)"""
    user_id = get_jwt_identity()
    comment = Comment.query.get_or_404(comment_id)
    
    # Check authorization
    if comment.user_id != user_id:
        return standardize_error('Unauthorized: You can only edit your own comments', 403)
    
    data = request.get_json()
    if not data:
        return standardize_error('Request body is required', 400)
    
    # Validate and sanitize new content
    if 'content' in data:
        is_valid, result = validate_comment_content(data['content'])
        if not is_valid:
            return standardize_error(result, 400)
        
        comment.content = sanitize_html(result)
    
    try:
        db.session.commit()
        return standardize_response(comment.to_dict(), 'Comment updated successfully')
    except Exception as e:
        db.session.rollback()
        return standardize_error('Failed to update comment', 500)

@comments_bp.route('/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """Delete a comment (user can only delete their own comments)"""
    user_id = get_jwt_identity()
    comment = Comment.query.get_or_404(comment_id)
    
    # Check authorization
    if comment.user_id != user_id:
        return standardize_error('Unauthorized: You can only delete your own comments', 403)
    
    try:
        db.session.delete(comment)
        db.session.commit()
        return standardize_response(None, 'Comment deleted successfully', 200)
    except Exception as e:
        db.session.rollback()
        return standardize_error('Failed to delete comment', 500)