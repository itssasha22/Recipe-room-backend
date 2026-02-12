from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import Comment, Recipe

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/recipe/<int:recipe_id>', methods=['GET'])
def get_recipe_comments(recipe_id):
    """Get all comments for a specific recipe"""
    try:
        recipe = Recipe.query.get_or_404(recipe_id)
        comments = Comment.query.filter_by(recipe_id=recipe_id).order_by(Comment.created_at.desc()).all()
        return jsonify([comment.to_dict() for comment in comments]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@comments_bp.route('', methods=['POST'])
@jwt_required()
def create_comment():
    """Create a new comment on a recipe"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data.get('recipe_id') or not data.get('content'):
            return jsonify({'error': 'recipe_id and content are required'}), 400
        
        # Verify recipe exists
        recipe = Recipe.query.get_or_404(data['recipe_id'])
        
        comment = Comment(
            content=data['content'],
            recipe_id=data['recipe_id'],
            user_id=user_id
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return jsonify(comment.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@comments_bp.route('/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id):
    """Update a comment (only by the comment author)"""
    try:
        user_id = int(get_jwt_identity())
        comment = Comment.query.get_or_404(comment_id)
        
        if comment.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        if 'content' in data:
            comment.content = data['content']
        
        db.session.commit()
        return jsonify(comment.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@comments_bp.route('/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    """Delete a comment (only by the comment author)"""
    try:
        user_id = int(get_jwt_identity())
        comment = Comment.query.get_or_404(comment_id)
        
        if comment.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'message': 'Comment deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
