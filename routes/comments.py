from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Comment, Recipe, User

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/<int:recipe_id>', methods=['GET'])
def get_comments(recipe_id):
    comments = Comment.query.filter_by(recipe_id=recipe_id).order_by(Comment.created_at.desc()).all()
    return jsonify([comment.to_dict() for comment in comments])

@comments_bp.route('/<int:recipe_id>', methods=['POST'])
@jwt_required()
def create_comment(recipe_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('content'):
        return jsonify({'error': 'Content is required'}), 400
    
    recipe = Recipe.query.get_or_404(recipe_id)
    
    comment = Comment(
        content=data['content'],
        user_id=user_id,
        recipe_id=recipe_id
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify(comment.to_dict()), 201

@comments_bp.route('/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id):
    user_id = get_jwt_identity()
    comment = Comment.query.get_or_404(comment_id)
    
    if comment.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    if 'content' in data:
        comment.content = data['content']
    
    db.session.commit()
    return jsonify(comment.to_dict())

@comments_bp.route('/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    user_id = get_jwt_identity()
    comment = Comment.query.get_or_404(comment_id)
    
    if comment.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({'message': 'Comment deleted'}), 200