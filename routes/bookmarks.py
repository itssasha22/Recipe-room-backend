from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import Bookmark, Recipe

bookmarks_bp = Blueprint('bookmarks', __name__)

@bookmarks_bp.route('', methods=['GET'])
@jwt_required()
def get_user_bookmarks():
    """Get all bookmarks for the current user"""
    try:
        user_id = int(get_jwt_identity())
        bookmarks = Bookmark.query.filter_by(user_id=user_id).all()
        
        # Get the full recipe details for each bookmark
        recipes = []
        for bookmark in bookmarks:
            recipe = Recipe.query.get(bookmark.recipe_id)
            if recipe:
                recipe_data = recipe.to_dict(include_stats=True)
                recipe_data['bookmarked_at'] = bookmark.created_at.isoformat()
                recipes.append(recipe_data)
        
        return jsonify(recipes), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bookmarks_bp.route('', methods=['POST'])
@jwt_required()
def add_bookmark():
    """Add a recipe to bookmarks"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        if not data.get('recipe_id'):
            return jsonify({'error': 'recipe_id is required'}), 400
        
        # Verify recipe exists
        recipe = Recipe.query.get_or_404(data['recipe_id'])
        
        # Check if already bookmarked
        existing_bookmark = Bookmark.query.filter_by(
            user_id=user_id,
            recipe_id=data['recipe_id']
        ).first()
        
        if existing_bookmark:
            return jsonify({'message': 'Recipe already bookmarked', 'bookmark': existing_bookmark.to_dict()}), 200
        
        # Create new bookmark
        bookmark = Bookmark(
            recipe_id=data['recipe_id'],
            user_id=user_id
        )
        
        db.session.add(bookmark)
        db.session.commit()
        
        return jsonify(bookmark.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bookmarks_bp.route('/<int:recipe_id>', methods=['DELETE'])
@jwt_required()
def remove_bookmark(recipe_id):
    """Remove a recipe from bookmarks"""
    try:
        user_id = int(get_jwt_identity())
        
        bookmark = Bookmark.query.filter_by(
            user_id=user_id,
            recipe_id=recipe_id
        ).first()
        
        if not bookmark:
            return jsonify({'error': 'Bookmark not found'}), 404
        
        db.session.delete(bookmark)
        db.session.commit()
        return jsonify({'message': 'Bookmark removed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bookmarks_bp.route('/check/<int:recipe_id>', methods=['GET'])
@jwt_required()
def check_bookmark(recipe_id):
    """Check if a recipe is bookmarked by the current user"""
    try:
        user_id = int(get_jwt_identity())
        
        bookmark = Bookmark.query.filter_by(
            user_id=user_id,
            recipe_id=recipe_id
        ).first()
        
        return jsonify({'is_bookmarked': bookmark is not None}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
